# OneDriveExplorer
# Copyright (C) 2022
#
# This file is part of OneDriveExplorer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import logging
import codecs
import csv
from io import StringIO
import binascii
import json
import urllib.parse
import sqlite3
from dissect import cstruct
import pandas as pd
import numpy as np
from ode.utils import progress, progress_gui

class DATParser:
    def __init__(self):
        self.application_path = f'{os.path.dirname(os.path.abspath(__file__))}/../..'
        self.log = logging.getLogger(__name__)
        self.datstruct = cstruct.cstruct()
        self.DAT_DEF = f'{self.application_path}/ode/helpers/structures'
        self.datstruct.loadfile(self.DAT_DEF)
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
        self.rem_list = ['header', 'entry_offset', 'unknown1', 'unknown2', 'unknown3', 'flags', 'unknown4', 'unknown5', 'unknown6', 'syncTokenData', 'syncTokenData_size', 'unknown7', 'shortcutVolumeID', 'shortcutItemIndex', 'sourceResourceID']

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


    def parse_dat(self, usercid, account='Business', gui=False, pb=False, value_label=False):
        usercid = (usercid).replace('/', '\\')
        self.scope_header = False
        self.files_header = False
        self.folders_header = False
        temp_scope = StringIO()
        temp_files = StringIO()
        temp_folders = StringIO()
        
        self.log.info(f'Start parsing {usercid}.')

        try:
            with open(usercid, 'rb') as f:
                total = f.seek(0, os.SEEK_END)
                f.seek(0, 0)
                header = self.datstruct.HEADER(f.read(536))
                version = hex(header.Version)[2:]
                if header.syncTokenData_size != 0:
                    account = 'Personal'
                    csvwriter = csv.writer(temp_scope, escapechar='\\')
                    csvwriter.writerow(['scopeID', 'siteID', 'webID', 'listID', 'libraryType', 'spoPermissions'])
                    self.scope_header = True
                    syncTokenData = urllib.parse.unquote(header.syncTokenData[:int(header.syncTokenData_size)].decode('utf-8'))
                    syncDict = dict(item.split("=") for item in syncTokenData.split(";"))
                    csvwriter.writerow([syncDict['ID'], '', '', '', '', ''])

                if version == '29':
                    chunk = 1048
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1048
                    #define FOLDER_CONSTANT  299
                    #define DELETE_CONSTANT  1032
                    #define LSCOPE_CONSTANT  208
                    #define LFOLDER_CONSTANT 825
                    #define VAULT_CONSTANT   320
                    #define ASCOPE_CONSTANT  176
                    """)

                elif version == '2a':
                    chunk = 1080
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1080
                    #define FOLDER_CONSTANT  331
                    #define DELETE_CONSTANT  1064
                    #define LSCOPE_CONSTANT  240
                    #define LFOLDER_CONSTANT 857
                    #define VAULT_CONSTANT   352
                    #define ASCOPE_CONSTANT  208
                    """)
    
                elif version == '2b':
                    chunk = 1080
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1080
                    #define FOLDER_CONSTANT  331
                    #define DELETE_CONSTANT  1064
                    #define LSCOPE_CONSTANT  240
                    #define LFOLDER_CONSTANT 857
                    #define VAULT_CONSTANT   352
                    #define ASCOPE_CONSTANT  208
                    """)

                elif version == '2c':
                    chunk = 1096
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1096
                    #define FOLDER_CONSTANT  347
                    #define DELETE_CONSTANT  1080
                    #define LSCOPE_CONSTANT  256
                    #define LFOLDER_CONSTANT 873
                    #define VAULT_CONSTANT   368
                    #define ASCOPE_CONSTANT  224
                    """)

                elif version == '2d':
                    chunk = 1104
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1098
                    #define FOLDER_CONSTANT  347
                    #define DELETE_CONSTANT  1082
                    #define LSCOPE_CONSTANT  258
                    #define LFOLDER_CONSTANT 875
                    #define VAULT_CONSTANT   370
                    #define ASCOPE_CONSTANT  226
                    """)

                elif version == '2e':
                    chunk = 1128
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1128
                    #define FOLDER_CONSTANT  371
                    #define DELETE_CONSTANT  1112
                    #define LSCOPE_CONSTANT  288
                    #define LFOLDER_CONSTANT 905
                    #define VAULT_CONSTANT   400
                    #define ASCOPE_CONSTANT  256
                    """)

                elif version == '2f':
                    chunk = 1128
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1128
                    #define FOLDER_CONSTANT  371
                    #define DELETE_CONSTANT  1112
                    #define LSCOPE_CONSTANT  288
                    #define LFOLDER_CONSTANT 905
                    #define VAULT_CONSTANT   400
                    #define ASCOPE_CONSTANT  256
                    """)

                elif version == '30':
                    chunk = 1152
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1152
                    #define FOLDER_CONSTANT  395
                    #define DELETE_CONSTANT  1136
                    #define LSCOPE_CONSTANT  312
                    #define LFOLDER_CONSTANT 929
                    #define VAULT_CONSTANT   424
                    #define ASCOPE_CONSTANT  280
                    """)

                elif version == '31':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '32':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '33':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '34':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '35':
                    chunk = 1176
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1176
                    #define FOLDER_CONSTANT  419
                    #define DELETE_CONSTANT  1160
                    #define LSCOPE_CONSTANT  336
                    #define LFOLDER_CONSTANT 953
                    #define VAULT_CONSTANT   448
                    #define ASCOPE_CONSTANT  304
                    """)

                elif version == '36':
                    chunk = 1232
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1232
                    #define FOLDER_CONSTANT  475
                    #define DELETE_CONSTANT  1216
                    #define LSCOPE_CONSTANT  392
                    #define LFOLDER_CONSTANT 1009
                    #define VAULT_CONSTANT   504
                    #define ASCOPE_CONSTANT  360
                    """)

                else:
                    if not gui:
                        print(f'Unknown dat verison: {version} (Please report issue)')
                    log.error(f'Unknown dat verison: {version} (Please report issue)')
                    return pd.DataFrame(), f.name

                while True:
                    count = f.tell()
                    ff = f.read(1).hex()

                    if f.tell() == total:
                        break

                    f. seek(-1, 1)

                    if ff == '01':
                        data_type = 'File'
                        if version == '29':
                            block = self.datstruct.DAT_FILE_v29(f.read(chunk))
                        elif version == '2a':
                            block = self.datstruct.DAT_FILE_v2a(f.read(chunk))
                        elif version == '2b':
                            block = self.datstruct.DAT_FILE_v2b(f.read(chunk))
                        elif version == '2c':
                            block = self.datstruct.DAT_FILE_v2c(f.read(chunk))
                        elif version == '2d':
                            block = self.datstruct.DAT_FILE_v2d(f.read(chunk))
                        elif version == '2e':
                            block = self.datstruct.DAT_FILE_v2e(f.read(chunk))
                        elif version == '2f':
                            block = self.datstruct.DAT_FILE_v2f(f.read(chunk))
                        elif version == '30':
                            block = self.datstruct.DAT_FILE_v30(f.read(chunk))
                        elif version == '31':
                            block = self.datstruct.DAT_FILE_v31(f.read(chunk))
                        elif version == '32':
                            block = self.datstruct.DAT_FILE_v32(f.read(chunk))
                        elif version == '33':
                            block = self.datstruct.DAT_FILE_v33(f.read(chunk))
                        elif version == '34':
                            block = self.datstruct.DAT_FILE_v34(f.read(chunk))
                        elif version == '35':
                            block = self.datstruct.DAT_FILE_v35(f.read(chunk))
                        elif version == '36':
                            block = self.datstruct.DAT_FILE_v36(f.read(chunk))
                        else:
                            block = self.datstruct.DAT_FILE(f.read(chunk))

                    elif ff == '02':
                        data_type = 'Folder'
                        if int(version, 16) <= 44:
                            block = self.datstruct.DAT_FOLDER_v29_v2c(f.read(chunk))
                        else:
                            block = self.datstruct.DAT_FOLDER_v2d_v36(f.read(chunk))

                    elif ff == '09':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_LIBRARY_SCOPE(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except:
                                continue

                    elif ff == '0a':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_LIBRARY_FOLDER(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except:
                                continue
                        block._values.update([('siteID', b''), ('webID', b'')])
                        block._values.move_to_end('listID', last=True)
                        block._values.update([('libraryType', b''), ('spoPermissions', '')])

                    elif ff == '0b':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_VAULT(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except:
                                continue
                        block._values.update([('siteID', b''), ('webID', b''), ('listID', b''), ('libraryType', b''), ('spoPermissions', '')])

                    elif ff == '0c':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_ADDED_SCOPE(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except:
                                continue

                    else:
                        block = self.datstruct.DAT_BLOCK(f.read(chunk))
                        continue

                    for k, v in block._values.items():
                        if k in self.split_str:
                            block._values[k] = v.split('\x00', 1)[0]
                        if k in self.int_to_bin:
                            block._values[k] = f'{v:032b}'
                        if k in self.int_to_hex:
                            block._values[k] = hex(v)
                        if k in self.bytes_to_hex:
                            block._values[k] = v.hex()
                        if k in self.bytes_to_str:
                            block._values[k] = v.decode('utf-8')
                        if k in self.id_format:
                            block._values[k] = self.format_id(v)

                    if data_type == 'File':
                        csvwriter = csv.writer(temp_files, escapechar='\\')
                        if version <= '2b':
                            self.merge_dicts(block._values, self.dict_1)
                        if version >= '2c' and version <= '34':
                            self.merge_dicts(block._values, self.dict_2)
                            block._values['sharedItem'] = [*block.bitMask][29]
                        if version >= '35':
                            self.merge_dicts(block._values, self.dict_3)
                            block._values['sharedItem'] = [*block.bitMask][29]
                        if not self.files_header:
                            csvwriter.writerow(dict(block._values))
                            self.files_header = True

                    if data_type == 'Folder':
                        csvwriter = csv.writer(temp_folders, escapechar='\\')
                        if not self.folders_header:
                            csvwriter.writerow(dict(block._values))
                            self.folders_header = True

                    if data_type == 'Scope':
                        csvwriter = csv.writer(temp_scope, escapechar='\\')
                        if not self.scope_header:
                            csvwriter.writerow(dict(block._values))
                            self.scope_header = True

                    csvwriter.writerow(block._values.values())
                
                    if count % 30 == 0:
                        if gui:
                            progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                        else:
                            progress(count, total, status='Building folder list. Please wait....')

        except Exception as e:
            #log.error(e)
            print(e)
            return pd.DataFrame, usercid

        if not gui:
            print('\n')
                    
        temp_scope.seek(0)
        temp_files.seek(0)
        temp_folders.seek(0)

        df_scope = pd.read_csv(temp_scope)
        temp_scope.close()
        df_scope.insert(0, 'Type', 'Scope')
        df_scope.insert(5, 'tenantID', '')
        df_scope.insert(6, 'webURL', '')
        df_scope.insert(7, 'remotePath', '')
        df_scope = df_scope.astype(object)
        df_scope['spoPermissions'].replace('', np.nan, inplace=True)
        df_scope['spoPermissions']= df_scope['spoPermissions'].fillna(0).astype('int')
        df_scope['spoPermissions'] = df_scope['spoPermissions'].apply(lambda x: self.permissions(x))
        df_scope.fillna('', inplace=True)
        scopeID = df_scope['scopeID'].tolist()

        df_files = pd.read_csv(temp_files, usecols=['parentResourceID', 'resourceID', 'eTag', 'fileName', 'fileStatus', 'spoPermissions', 'volumeID', 'itemIndex', 'lastChange', 'size', 'localHashDigest', 'sharedItem', 'mediaDateTaken', 'mediaWidth', 'mediaHeight', 'mediaDuration'])
        temp_files.close()
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
            df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'SHA1({x})')
        else:
            df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'quickXor({codecs.encode(binascii.unhexlify(x), "base64").decode("utf-8").rstrip()})')
        df_files['size'] = df_files['size'].apply(lambda x: f'{x//1024 + 1:,} KB')
        df_files['spoPermissions'] = df_files['spoPermissions'].apply(lambda x: self.permissions(x))
        df_files['lastChange'] = pd.to_datetime(df_files['lastChange'], unit='s').astype(str)
        df_files.insert(0, 'Type', 'File')

        df_folders = pd.read_csv(temp_folders, usecols=['parentScopeID', 'parentResourceID', 'resourceID', 'eTag', 'folderName', 'folderStatus', 'spoPermissions', 'volumeID', 'itemIndex'])
        temp_folders.close()
        df_folders.rename(columns={"folderName": "Name"}, inplace=True)
        df_folders['spoPermissions'] = df_folders['spoPermissions'].apply(lambda x: self.permissions(x))
        df_folders.insert(0, 'Type', 'Folder')
        df = pd.concat([df_scope, df_files, df_folders], ignore_index=True, axis=0)
        df = df.where(pd.notnull(df), None)
    
        return df, pd.DataFrame(), df_scope, scopeID
