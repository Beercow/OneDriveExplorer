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

import json
import pandas as pd
import logging

log = logging.getLogger(__name__)


class ParseResult:
    def __init__(self, df, rbin_df, df_scope, graphMetadata, scopeID, account, localHashAlgorithm, offline_db, comment):
        self.df = df
        self.rbin_df = rbin_df
        self.df_scope = df_scope
        self.graphMetadata = graphMetadata
        self.scopeID = scopeID
        self.account = account
        self.localHashAlgorithm = localHashAlgorithm
        self.offline_db = offline_db
        self.comment = comment

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(df={len(self.df)} rows, rbin_df={len(self.rbin_df)} rows, scopeID={len(self.scopeID)})"


def parse_csv(filename):
    file = open(filename, 'r', encoding='utf-8')
    columns_to_drop = ['parentResourceId', 'resourceId', 'inRecycleBin', 'volumeId', 'fileId',
                       'DeleteTimeStamp', 'notificationTime', 'hash', 'deletingProcess']
    columns_to_drop_2 = ['MountPoint']

    dtypes = {'Type': 'object', 'scopeID': 'object', 'siteID': 'object', 'webID': 'object',
              'listID': 'object', 'tenantID': 'object', 'webURL': 'object', 'remotePath': 'object',
              'libraryType': 'object', 'resourceID': 'object', 'parentResourceID': 'object',
              'eTag': 'object', 'volumeID': 'str', 'itemIndex': 'Int64', 'localHashDigest': 'object',
              'localHashAlgorithm': 'Int64', 'lastChange': 'object', 'size': 'object', 'Name': 'str',
              'fileStatus': 'Int64', 'spoPermissions': 'object', 'sharedItem': 'Int64', 'Media': 'object',
              'parentScopeID': 'object', 'folderStatus': 'Int64', 'Path': 'str',
              'shortcutVolumeID': 'str', 'shortcutItemIndex': 'Int64', 'hydrationCount': 'Int64',
              'folderColor': 'Int64', 'ListSync': 'str', 'Metadata': 'str'}

    try:
        csv_name = filename.name.replace('/', '\\')
    except AttributeError:
        csv_name = ''

    log.info(f'Started parsing {csv_name}')
    comment = file.readline()
    cleaned_str = comment.lstrip("#")
    data_dict = json.loads(cleaned_str)

    try:
        df = pd.read_csv(file, low_memory=False, quotechar='"', dtype=dtypes, comment="#")

        try:
            df_scope = df.loc[df['Type'] == 'Scope',
                                            ['Type', 'scopeID', 'siteID', 'webID', 'listID', 'tenantID',
                                             'webURL', 'remotePath', 'spoPermissions', 'shortcutVolumeID',
                                             'shortcutItemIndex', 'libraryType']]
            columns_to_fill = df_scope.columns.difference(['libraryType'])
            df_scope[columns_to_fill] = df_scope[columns_to_fill].fillna('')
            df_scope['remotePath'] = df_scope['remotePath'].fillna('')

            scopeID = df_scope['scopeID'].tolist()
        except Exception:
            df_scope = pd.DataFrame()
            scopeID = []

        if 'inRecycleBin' in df.columns:
            df = df.astype({'fileId': 'str', 'inRecycleBin': 'Int64'})
            rbin_df = df[df['Type'] == 'Deleted'][['Type', 'parentResourceId', 'resourceId', 'eTag',
                                                   'Path', 'Name', 'inRecycleBin', 'volumeId', 'fileId',
                                                   'DeleteTimeStamp', 'notificationTime', 'size', 'hash',
                                                   'deletingProcess']]
            rbin_df = rbin_df.astype(object).where(pd.notna(rbin_df), '')
            df = df.drop(df[df['Type'] == 'Deleted'].index)
            df.drop(columns=columns_to_drop, inplace=True)
        else:
            rbin_df = pd.DataFrame()

        try:
            df.drop(columns=columns_to_drop_2, inplace=True)
        except Exception:
            pass
        df['Path'] = df['Path'].astype(str).fillna('')
        df['Name'] = df['Name'].astype(str).fillna('')
        try:
            df.localHashDigest.fillna('', inplace=True)
        except Exception:
            pass

        for col in ['notificationTime', 'firstHydrationTime', 'lastHydrationTime',
                    'diskLastAccessTime', 'diskCreationTime']:
            if col in df:
                df[col].fillna('', inplace=True)

        if 'lastKnownPinState' in df:
            df.lastKnownPinState = df.lastKnownPinState.apply(lambda x: '' if pd.isna(x) else int(x))

        if 'remotePath' in df:
            df.remotePath.fillna('', inplace=True)

    except Exception as e:
        log.error(f'Not a valid csv: {csv_name} - Error: {e}')
        return ParseResult(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                           pd.DataFrame(), [], '', 0, pd.DataFrame(), data_dict)

    return ParseResult(df, rbin_df, df_scope, pd.DataFrame(columns=['resourceID', 'Metadata']),
                       scopeID, '', 0, pd.DataFrame(columns=['resourceID', 'ListSync']), data_dict)
