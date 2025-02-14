# OneDriveExplorer
# Copyright (C) 2025
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

import logging
import codecs
import json
import sqlite3
from dissect import cstruct
import pandas as pd
from ode.utils import permissions, change_dtype


class ParseResult:
    def __init__(self, df, rbin_df, df_scope, graphMetadata, scopeID, account, localHashAlgorithm):
        self.df = df
        self.rbin_df = rbin_df
        self.df_scope = df_scope
        self.graphMetadata = graphMetadata
        self.scopeID = scopeID
        self.account = account
        self.localHashAlgorithm = localHashAlgorithm

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(df={len(self.df)} rows, rbin_df={len(self.rbin_df)} rows, scopeID={len(self.scopeID)})"


class SQLiteParser:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.datstruct = cstruct.cstruct()
        self.scope_header = False
        self.files_header = False
        self.folders_header = False
        self.df = pd.DataFrame()
        self.rbin_df = pd.DataFrame()
        self.df_scope = pd.DataFrame()
        self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])
        self.scopeID = []
        self.account = None
        self.localHashAlgorithm = 0
        self.dict_1 = {'lastChange': 0,
                       'sharedItem': 0,
                       'mediaDateTaken': 0,
                       'mediaWidth': 0,
                       'mediaHeight': 0,
                       'mediaDuration': 0
                       }
        self.dict_2 = {'mediaDateTaken': 0,
                       'mediaWidth': 0,
                       'mediaHeight': 0,
                       'mediaDuration': 0
                       }

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

    def compute_hash(self, row):
        self.localHashAlgorithm = row['localHashAlgorithm']  # Set the value to the global variable

        # Perform the logic based on the algorithm
        if self.localHashAlgorithm == 4 and row['localHashDigest'] not in (None, ''):
            return f'SHA1({row["localHashDigest"].hex()})'
        elif self.localHashAlgorithm == 5 and row['localHashDigest'] not in (None, ''):
            return f'quickXor({codecs.encode(row["localHashDigest"], "base64").decode("utf-8").rstrip()})'
        elif row['localHashDigest'] not in (None, ''):
            return f'{self.localHashAlgorithm}:{row["localHashDigest"]}'
        else:
            return ''

    def parse_sql(self, sql_dir):
        self.account = sql_dir.rsplit('\\', 1)[-1]

        self.log.info(f'Start parsing {self.account}.')

        try:
            SyncEngineDatabase = sqlite3.connect(f'file:/{sql_dir}/SyncEngineDatabase.db?mode=ro', uri=True)
            cursor = SyncEngineDatabase.execute("SELECT value FROM __oddbm_schema WHERE name = 'version'")
            schema_version = cursor.fetchall()[0][0]

            try:
                if schema_version == 8:
                    self.df_scope = pd.read_sql_query("SELECT scopeID, siteID, webID, listID, spoPermissions, shortcutVolumeID, shortcutItemIndex, libraryType FROM od_ScopeInfo_Records", SyncEngineDatabase)
                else:
                    self.df_scope = pd.read_sql_query("SELECT scopeID, siteID, webID, listID, tenantID, webURL, remotePath, spoPermissions, shortcutVolumeID, shortcutItemIndex, libraryType FROM od_ScopeInfo_Records", SyncEngineDatabase)
                self.df_scope.insert(0, 'Type', 'Scope')
                self.df_scope = change_dtype(self.df_scope, df_name='df_scope', schema_version=schema_version)
                self.df_scope['spoPermissions'] = self.df_scope['spoPermissions'].apply(lambda x: permissions(x))

                self.scopeID = self.df_scope['scopeID'].tolist()

                if schema_version >= 32:
                    df_files = pd.read_sql_query("SELECT parentResourceID, od_ClientFile_Records.resourceID, eTag, fileName, fileStatus, lastKnownPinState, spoPermissions, volumeID, itemIndex, diskLastAccessTime, diskCreationTime, lastChange, size, localHashDigest, localHashAlgorithm, sharedItem, mediaDateTaken, mediaWidth, mediaHeight, mediaDuration, od_HydrationData.* FROM od_ClientFile_Records LEFT OUTER JOIN od_HydrationData ON od_ClientFile_Records.resourceID = od_HydrationData.resourceID", SyncEngineDatabase)
                    df_files = df_files.loc[:, ~df_files.columns.duplicated(keep='first')]
                elif 29 < schema_version <= 31:
                    df_files = pd.read_sql_query("SELECT parentResourceID, od_ClientFile_Records.resourceID, eTag, fileName, fileStatus, spoPermissions, volumeID, itemIndex, diskLastAccessTime, lastChange, size, localHashDigest, localHashAlgorithm, sharedItem, mediaDateTaken, mediaWidth, mediaHeight, mediaDuration, od_HydrationData.* FROM od_ClientFile_Records LEFT OUTER JOIN od_HydrationData ON od_ClientFile_Records.resourceID = od_HydrationData.resourceID", SyncEngineDatabase)
                    df_files = df_files.loc[:, ~df_files.columns.duplicated(keep='first')]
                elif 20 < schema_version <= 29:
                    df_files = pd.read_sql_query("SELECT parentResourceID, od_ClientFile_Records.resourceID, eTag, fileName, fileStatus, spoPermissions, volumeID, itemIndex, lastChange, size, localHashDigest, localHashAlgorithm, sharedItem, mediaDateTaken, mediaWidth, mediaHeight, mediaDuration, od_HydrationData.* FROM od_ClientFile_Records LEFT OUTER JOIN od_HydrationData ON od_ClientFile_Records.resourceID = od_HydrationData.resourceID", SyncEngineDatabase)
                    df_files = df_files.loc[:, ~df_files.columns.duplicated(keep='first')]
                elif schema_version <= 20:
                    df_files = pd.read_sql_query("SELECT parentResourceID, resourceID, eTag, fileName, fileStatus, spoPermissions, volumeID, itemIndex, lastChange, size, localHashDigest, localHashAlgorithm, sharedItem, mediaDateTaken, mediaWidth, mediaHeight, mediaDuration FROM od_ClientFile_Records", SyncEngineDatabase)

                df_files.insert(0, 'Type', 'File')
                df_files.rename(columns={"fileName": "Name",
                                         "mediaDateTaken": "DateTaken",
                                         "mediaWidth": "Width",
                                         "mediaHeight": "Height",
                                         "mediaDuration": "Duration"
                                         }, inplace=True)

                # All need to be moved to utils.change_dtype
                if 'notificationTime' in df_files:
                    df_files.rename(columns={"notificationTime": "HydrationTime"}, inplace=True)
                    df_files['HydrationTime'] = pd.to_datetime(df_files['HydrationTime'], unit='s').astype(str)
                    df_files['HydrationTime'].replace('NaT', '', inplace=True)

                if 'firstHydrationTime' in df_files:
                    df_files['lastHydrationType'].fillna('', inplace=True)
                    df_files['firstHydrationTime'] = pd.to_datetime(df_files['firstHydrationTime'], unit='s').astype(str)
                    df_files['firstHydrationTime'].replace('NaT', '', inplace=True)
                    df_files['lastHydrationTime'] = pd.to_datetime(df_files['lastHydrationTime'], unit='s').astype(str)
                    df_files['lastHydrationTime'].replace('NaT', '', inplace=True)

                if 'diskLastAccessTime' in df_files:
                    df_files['diskLastAccessTime'] = pd.to_datetime(df_files['diskLastAccessTime'], unit='s').astype(str)
                    df_files['diskLastAccessTime'].replace('NaT', '', inplace=True)

                if 'diskCreationTime' in df_files:
                    df_files['diskCreationTime'] = pd.to_datetime(df_files['diskCreationTime'], unit='s').astype(str)
                    df_files['diskCreationTime'].replace('NaT', '', inplace=True)

                if 'lastKnownPinState' in df_files:
                    df_files.lastKnownPinState = df_files.lastKnownPinState.apply(lambda x: '' if pd.isna(x) else int(x))

                df_files['DateTaken'] = pd.to_datetime(df_files['DateTaken'], unit='s').fillna('1970-01-01 00:00:00').astype(str)
                df_files = change_dtype(df_files, df_name='df_files', schema_version=schema_version)
                columns = ['DateTaken', 'Width', 'Height', 'Duration']
                df_files['Media'] = df_files[columns].to_dict(orient='records')
                df_files = df_files.drop(columns=columns)
                df_files['localHashDigest'] = df_files.apply(self.compute_hash, axis=1)
                df_files['size'] = df_files['size'].apply(lambda x: '0 KB' if x == 0 else f'{x//1024 + 1:,} KB')
                df_files['spoPermissions'] = df_files['spoPermissions'].apply(lambda x: permissions(x))
                df_files['lastChange'] = pd.to_datetime(df_files['lastChange'], unit='s').astype(str)

                if 23 < schema_version:
                    df_folders = pd.read_sql_query("SELECT parentScopeID, parentResourceID, resourceID, eTag, folderName, folderStatus, spoPermissions, volumeID, itemIndex, folderColor, sharedItem FROM od_ClientFolder_Records", SyncEngineDatabase)
                else:
                    df_folders = pd.read_sql_query("SELECT parentScopeID, parentResourceID, resourceID, eTag, folderName, folderStatus, spoPermissions, volumeID, itemIndex, sharedItem FROM od_ClientFolder_Records", SyncEngineDatabase)
                df_folders.insert(0, 'Type', 'Folder')
                df_folders.rename(columns={"folderName": "Name"}, inplace=True)
                df_folders = change_dtype(df_folders, df_name='df_folders', schema_version=schema_version)
                df_folders['spoPermissions'] = df_folders['spoPermissions'].apply(lambda x: permissions(x))

                self.df = pd.concat([self.df_scope, df_files, df_folders], ignore_index=True, axis=0)
                self.df = self.df.where(pd.notnull(self.df), None)

                if self.df.empty:
                    self.log.warning(f'{sql_dir}\SyncEngineDatabase.db is empty.')

                if schema_version >= 10:
                    self.graphMetadata = pd.read_sql_query("SELECT od_GraphMetadata_Records.* FROM od_GraphMetadata_Records INNER JOIN od_ClientFile_Records ON od_ClientFile_Records.resourceID = od_GraphMetadata_Records.resourceID", SyncEngineDatabase)
                    self.graphMetadata = change_dtype(self.graphMetadata, df_name='df_GraphMetadata_Records', schema_version=schema_version)
                    if not self.graphMetadata.empty:
                        json_columns = ['graphMetadataJSON', 'filePolicies']
                        self.graphMetadata[json_columns] = self.graphMetadata[json_columns].map(lambda x: json.loads(x) if pd.notna(x) and x.strip() else '')
                        columns2 = ['graphMetadataJSON', 'spoCompositeID', 'createdBy', 'modifiedBy', 'filePolicies', 'fileExtension', 'lastWriteCount']
                        self.graphMetadata['Metadata'] = self.graphMetadata[columns2].to_dict(orient='records')
                        self.graphMetadata = self.graphMetadata.drop(columns=columns2)
                else:
                    self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])

            except Exception as e:
                self.log.warning(f'Unable to parse {sql_dir}\SyncEngineDatabase.db. {e}')
                self.df = pd.DataFrame()
                self.df_scope = pd.DataFrame()
                self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])
                self.scopeID = []

            SyncEngineDatabase.close()

        except sqlite3.OperationalError:
            self.log.info('SyncEngineDatabase.db does not exist')
            self.df = pd.DataFrame()
            self.df_scope = pd.DataFrame()
            self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])
            self.scopeID = []

        try:
            SafeDelete = sqlite3.connect(f'file:/{sql_dir}/SafeDelete.db?mode=ro', uri=True)

            try:
                self.rbin_df = pd.read_sql_query("SELECT parentResourceId, resourceId, itemName, volumeId, fileId, notificationTime FROM items_moved_to_recycle_bin", SafeDelete)
                filter_delete_info_df = pd.read_sql_query("SELECT path, volumeId, fileId, notificationTime, process FROM filter_delete_info", SafeDelete)

                self.rbin_df.rename(columns={"itemName": "Name"}, inplace=True)

                self.rbin_df.insert(0, 'Type', 'Deleted')
                self.rbin_df.insert(3, 'eTag', '')
                self.rbin_df.insert(4, 'Path', '')
                self.rbin_df.insert(6, 'inRecycleBin', '')
                self.rbin_df.insert(9, 'DeleteTimeStamp', '')
                self.rbin_df.insert(11, 'size', '')
                self.rbin_df.insert(12, 'hash', '')
                self.rbin_df.insert(13, 'deletingProcess', '')

                filter_delete_info_df.rename(columns={"path": "Path",
                                                      "process": "deletingProcess"
                                                      }, inplace=True)

                filter_delete_info_df.insert(0, 'Type', 'Deleted')
                filter_delete_info_df.insert(1, 'parentResourceId', '')
                filter_delete_info_df.insert(2, 'resourceId', '')
                filter_delete_info_df.insert(3, 'eTag', '')
                filter_delete_info_df.insert(5, 'Name', '')
                filter_delete_info_df.insert(6, 'inRecycleBin', '')
                filter_delete_info_df.insert(9, 'DeleteTimeStamp', '')
                filter_delete_info_df.insert(11, 'size', '')
                filter_delete_info_df.insert(12, 'hash', '')

                filter_delete_info_df['Name'] = filter_delete_info_df['Path'].str.rsplit('\\', n=1).str[-1]
                filter_delete_info_df['Path'] = filter_delete_info_df['Path'].str.rsplit('\\', n=1).str[0]

                self.rbin_df = pd.concat([self.rbin_df, filter_delete_info_df], ignore_index=True, axis=0)

                self.rbin_df['notificationTime'] = pd.to_datetime(self.rbin_df['notificationTime'], unit='s').astype(str)
                self.rbin_df['volumeId'] = self.rbin_df['volumeId'].apply(lambda x: '{}{}{}{}-{}{}{}{}'.format(*format(x, '08x')).upper())

            except Exception as e:
                self.log.warning(f'Unable to parse {sql_dir}\SafeDelete.db. {e}')
                self.rbin_df = pd.DataFrame()

            SafeDelete.close()

        except sqlite3.OperationalError:
            self.log.info('SafeDelete.db does not exist')
            self.rbin_df = pd.DataFrame()

        return ParseResult(
            self.df,
            self.rbin_df,
            self.df_scope,
            self.graphMetadata,
            self.scopeID,
            self.account,
            self.localHashAlgorithm
        )
