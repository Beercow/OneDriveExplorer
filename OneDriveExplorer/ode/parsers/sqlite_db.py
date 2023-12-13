import os
import sys
import logging
import codecs
import csv
from io import StringIO
import json
import urllib.parse
import sqlite3
from dissect import cstruct
import pandas as pd
from ode.utils import progress, progress_gui

class SQLiteParser:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.datstruct = cstruct.cstruct()
        self.scope_header = False
        self.files_header = False
        self.folders_header = False
        self.dict_1 = {'lastChange': 0, 'sharedItem': 0, 'mediaDateTaken': 0, 'mediaWidth': 0, 'mediaHeight': 0, 'mediaDuration': 0}
        self.dict_2 = {'mediaDateTaken': 0, 'mediaWidth': 0, 'mediaHeight': 0, 'mediaDuration': 0}
        self.dict_3 = {'mediaDuration': 0}
        self.int_to_bin = ['bitMask']
        self.int_to_hex = ['header', 'entry_offset']
        self.bytes_to_str = ['eTag', 'listID', 'scopeID', 'siteID', 'webID', 'syncTokenData']
        self.bytes_to_hex = ['localHashDigest', 'serverHashDigest', 'localWaterlineData', 'localWriteValidationToken', 'localSyncTokenData', 'localCobaltHashAlgorithm']
        self.int_to_date = ['lastChange', 'serverLastChange', 'mediaDateTaken']
        self.split_str = ['fileName', 'folderName']
        self.id_format = ['resourceID', 'parentResourceID', 'parentScopeID', 'scopeID', 'sourceResourceID']
        self.rem_list = ['header', 'entry_offset', 'unknown1', 'unknown2', 'unknown3', 'flags', 'unknown4', 'unknown5', 'unknown6', 'syncTokenData', 'syncTokenData_size', 'spoPermissions', 'unknown7', 'shortcutVolumeID', 'shortcutItemIndex', 'sourceResourceID']

    def format_id(self, _):
        f = _[:32].decode("utf-8")
        s = int.from_bytes(_[32:], "big")
        if s != 0:
            return f'{f}+{s}'
        return f

    def merge_dicts(self, dict_1, dict_2):
        for k, v in dict_2.items():
            dict_1[k] = v
        return dict_1

    def permissions(self, _):
        perstr = []
        # Lists and Documents
        if _ & 0x0:
            perstr.append("EmptyMask")
        if _ & 0x1:
            perstr.append("ViewListItems")
        if _ & 0x2:
            perstr.append("AddListItems")
        if _ & 0x4:
            perstr.append("EditListItems")
        if _ & 0x8:
            perstr.append("DeleteListItems")
        if _ & 0x10:
            perstr.append("ApproveItems")
        if _ & 0x20:
            perstr.append("OpenItems")
        if _ & 0x40:
            perstr.append("ViewVersions")
        if _ & 0x80:
            perstr.append("DeleteVersions")
        if _ & 0x100:
            perstr.append("OverrideListBehaviors")
        if _ & 0x200:
            perstr.append("ManagePersonalViews")
        if _ & 0x400:
            perstr.append("ManageLists")
        if _ & 0x800:
            perstr.append("ViewApplicationPages")
        # Web Level
        if _ & 0x1000:
            perstr.append("Open")
        if _ & 0x2000:
            perstr.append("ViewPages")
        if _ & 0x4000:
            perstr.append("AddAndCustomizePages")
        if _ & 0x8000:
            perstr.append("ApplyThemAndBorder")
        if _ & 0x10000:
            perstr.append("ApplyStyleSheets")
        if _ & 0x20000:
            perstr.append("ViewAnalyticsData")
        if _ & 0x40000:
            perstr.append("UseSSCSiteCreation")
        if _ & 0x80000:
            perstr.append("CreateSubsite")
        if _ & 0x100000:
            perstr.append("CreateGroups")
        if _ & 0x200000:
            perstr.append("ManagePermissions")
        if _ & 0x400000:
            perstr.append("BrowseDirectories")
        if _ & 0x800000:
            perstr.append("BrowseUserInfo")
        if _ & 0x1000000:
            perstr.append("AddDelPersonalWebParts")
        if _ & 0x2000000:
            perstr.append("UpdatePersonalWebParts")
        if _ & 0x4000000:
            perstr.append("ManageWeb")
        return perstr

    def find_parent(self, x, id_name_dict, parent_dict):
        value = parent_dict.get(x, None)
        if x is None:
            return ''
        elif value is None:
            return x + "\\\\"
        else:
            # Incase there is a id without name.
            if id_name_dict.get(value, None) is None:
                return self.find_parent(value, id_name_dict, parent_dict) + x
        return self.find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))

    def parse_sql(self, sql_dir):
        account = sql_dir.rsplit('\\', 1)[-1]
    
        self.log.info(f'Start parsing {account}.')
    
        try:
            SyncEngineDatabase = sqlite3.connect(f'file:/{sql_dir}/SyncEngineDatabase.db?mode=ro', uri=True)

            try:
                df_scope = pd.read_sql_query("SELECT scopeID, siteID, webID, listID, tenantID, webURL, remotePath, libraryType FROM od_ScopeInfo_Records", SyncEngineDatabase)
                df_scope.insert(0, 'Type', 'Scope')
                columns_to_fill = df_scope.columns.difference(['libraryType'])
                df_scope[columns_to_fill] = df_scope[columns_to_fill].fillna('')
#                df_scope.fillna('')
                scopeID = df_scope['scopeID'].tolist()

                df_files = pd.read_sql_query("SELECT parentResourceID, resourceID, eTag, fileName, fileStatus, spoPermissions, volumeID, itemIndex, lastChange, size, localHashDigest, sharedItem, mediaDateTaken, mediaWidth, mediaHeight, mediaDuration FROM od_ClientFile_Records", SyncEngineDatabase)
                df_files.rename(columns={"fileName": "Name",
                                         "mediaDateTaken": "DateTaken",
                                         "mediaWidth": "Width",
                                         "mediaHeight": "Height",
                                         "mediaDuration": "Duration"
                                        }, inplace=True)
                df_files['DateTaken'] = pd.to_datetime(df_files['DateTaken'], unit='s').astype(str)
                columns = ['DateTaken', 'Width', 'Height', 'Duration']
                df_files['Media'] = df_files[columns].to_dict(orient='records') 
                df_files = df_files.drop(columns=columns)
                if account == 'Personal':
                    df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'SHA1({x.hex()})')
                else:
                    df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'quickXor({codecs.encode(x, "base64").decode("utf-8").rstrip()})')
                df_files['size'] = df_files['size'].apply(lambda x: f'{x//1024 + 1:,} KB')
                df_files['spoPermissions'] = df_files['spoPermissions'].apply(lambda x: self.permissions(x))
                df_files['lastChange'] = pd.to_datetime(df_files['lastChange'], unit='s').astype(str)
                df_files.insert(0, 'Type', 'File')

                df_folders = pd.read_sql_query("SELECT parentScopeID, parentResourceID, resourceID, eTag, folderName, folderStatus, spoPermissions, volumeID, itemIndex FROM od_ClientFolder_Records", SyncEngineDatabase)
                df_folders.rename(columns={"folderName": "Name"}, inplace=True)
                df_folders['spoPermissions'] = df_folders['spoPermissions'].apply(lambda x: self.permissions(x))
                df_folders.insert(0, 'Type', 'Folder')
            
                df = pd.concat([df_scope, df_files, df_folders], ignore_index=True, axis=0)
                df = df.where(pd.notnull(df), None)

            except Exception as e:
                self.log.warning(f'Unable to parse {sql_dir}\SyncEngineDatabase.db. {e}')
                df = pd.DataFrame()
                df_scope = pd.DataFrame()
                scopeID = []
                

            SyncEngineDatabase.close()

        except sqlite3.OperationalError:
            self.log.info('SyncEngineDatabase.db does not exist')
            df = pd.DataFrame()
            df_scope = pd.DataFrame()
            scopeID = []

        try:
            SafeDelete = sqlite3.connect(f'file:/{sql_dir}/SafeDelete.db?mode=ro', uri=True)

            try:
                rbin_df = pd.read_sql_query("SELECT parentResourceId, resourceId, itemName, volumeId, fileId, notificationTime FROM items_moved_to_recycle_bin", SafeDelete)

                rbin_df.rename(columns={"itemName": "Name",
                                        "notificationTime": "DeleteTimeStamp"
                                       }, inplace=True)

                rbin_df.insert(0, 'Type', 'Deleted')
                rbin_df.insert(3, 'eTag', '')
                rbin_df.insert(4, 'Path', '')
                rbin_df.insert(6, 'inRecycleBin', '')
                rbin_df.insert(10, 'size', '')
                rbin_df.insert(11, 'hash', '')
                rbin_df['DeleteTimeStamp'] = pd.to_datetime(rbin_df['DeleteTimeStamp'], unit='s').astype(str)
                rbin_df['volumeId'] = rbin_df['volumeId'].apply(lambda x: '{}{}{}{}-{}{}{}{}'.format(*format(x, '08x')).upper())

            except Exception as e:
                self.log.warning(f'Unable to parse {sql_dir}\SafeDelete.db. {e}')
                rbin_df = pd.DataFrame()

            SafeDelete.close()

        except sqlite3.OperationalError:
            self.log.info('SafeDelete.db does not exist')
            rbin_df = pd.DataFrame()

        return df, rbin_df, df_scope, scopeID, account
