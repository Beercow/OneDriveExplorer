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

import ast
import pandas as pd
import logging

log = logging.getLogger(__name__)


def parse_csv(filename):

    file = open(filename.name, 'r', encoding='utf-8')
    columns_to_drop = ['parentResourceId', 'resourceId', 'inRecycleBin', 'volumeId', 'fileId', 'DeleteTimeStamp', 'notificationTime', 'hash', 'deletingProcess']
    columns_to_drop_2 = ['MountPoint', 'fileName', 'graphMetadataJSON', 'spoCompositeID', 'createdBy', 'modifiedBy', 'filePolicies', 'fileExtension', 'lastWriteCount']

    dtypes = {'Type': 'object',
              'scopeID': 'object',
              'siteID': 'object',
              'webID': 'object',
              'listID': 'object',
              'tenantID': 'object',
              'webURL': 'object',
              'remotePath': 'object',
              'libraryType': 'object',
              'resourceID': 'object',
              'parentResourceID': 'object',
              'eTag': 'object',
              'volumeID': 'Int64',
              'itemIndex': 'Int64',
              'localHashDigest': 'object',
              'lastChange': 'object',
              'size': 'object',
              'Name': 'object',
              'fileStatus': 'Int64',
              'spoPermissions': 'object',
              'sharedItem': 'Int64',
              'Media': 'object',
              'parentScopeID': 'object',
              'folderStatus': 'Int64',
              'Path': 'object',
              'shortcutVolumeID': 'Int64',
              'shortcutItemIndex': 'Int64',
              'hydrationCount': 'Int64'
              }

    try:
        csv_name = filename.name.replace('/', '\\')
    except AttributeError:
        csv_name = ''

    log.info(f'Started parsing {csv_name}')

    try:
        df = pd.read_csv(file, low_memory=False, quotechar='"', dtype=dtypes)
        df_scope = df.loc[df['Type'] == 'Scope',
                          ['Type', 'scopeID', 'siteID', 'webID', 'listID',
                           'tenantID', 'webURL', 'remotePath', 'spoPermissions',
                           'shortcutVolumeID', 'shortcutItemIndex', 'libraryType']]
        columns_to_fill = df_scope.columns.difference(['libraryType'])
        df_scope[columns_to_fill] = df_scope[columns_to_fill].fillna('')

        if 'remotePath' in df_scope:
            df_scope.remotePath.fillna('', inplace=True)

        scopeID = df_scope['scopeID'].tolist()

        if 'inRecycleBin' in df.columns:
            convert = {'fileId': 'Int64',
                       'inRecycleBin': 'Int64'
                       }
            df = df.astype(convert)
            rbin_df = df.loc[df['Type'] == 'Deleted',
                             ['Type', 'parentResourceId', 'resourceId', 'eTag',
                              'Path', 'Name', 'inRecycleBin', 'volumeId',
                              'fileId', 'DeleteTimeStamp', 'notificationTime', 'size', 'hash',
                              'deletingProcess']]
            rbin_df = rbin_df.astype(object)
            rbin_df = rbin_df.where(pd.notna(rbin_df), '')
            df = df.drop(df[df['Type'] == 'Deleted'].index)
            df.drop(columns=columns_to_drop, inplace=True)
        else:
            rbin_df = pd.DataFrame()

        df_GraphMetadata_Records = df.loc[(df['Type'] == 'File') & df['fileName'].notna(),
                                          ['fileName', 'resourceID', 'graphMetadataJSON', 'spoCompositeID',
                                           'createdBy', 'modifiedBy', 'filePolicies', 'fileExtension', 'lastWriteCount']]

        if not df_GraphMetadata_Records.empty:
            json_columns = ['graphMetadataJSON', 'filePolicies']
            df_GraphMetadata_Records[json_columns] = df_GraphMetadata_Records[json_columns].map(lambda x: ast.literal_eval(x) if pd.notna(x) and x.strip() else '')
            df_GraphMetadata_Records['lastWriteCount'] = df_GraphMetadata_Records['lastWriteCount'].astype('Int64')

            if 'fileExtension' in df_GraphMetadata_Records:
                df_GraphMetadata_Records.fileExtension.fillna('', inplace=True)

        df.drop(columns=columns_to_drop_2, inplace=True)
        df.localHashDigest.fillna('', inplace=True)
        if 'notificationTime' in df:
            df.HydrationTime.fillna('', inplace=True)

        if 'firstHydrationTime' in df:
            df.lastHydrationType.fillna('', inplace=True)
            df.firstHydrationTime.fillna('', inplace=True)
            df.lastHydrationTime.fillna('', inplace=True)

        if 'diskLastAccessTime' in df:
            df.diskLastAccessTime.fillna('', inplace=True)

        if 'diskCreationTime' in df:
            df.diskCreationTime.fillna('', inplace=True)

        if 'lastKnownPinState' in df:
                    df.lastKnownPinState = df.lastKnownPinState.apply(lambda x: '' if pd.isna(x) else int(x))

        if 'remotePath' in df:
            df.remotePath.fillna('', inplace=True)

    except Exception as e:
        print(e)
        log.error(f'Not a valid csv. {csv_name}')
        df = pd.DataFrame()
        rbin_df = pd.DataFrame()
        df_scope = pd.DataFrame()
        df_GraphMetadata_Records = pd.DataFrame()
        scopeID = []

    return df, rbin_df, df_scope, df_GraphMetadata_Records, scopeID
