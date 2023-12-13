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

import pandas as pd
import logging

log = logging.getLogger(__name__)


def parse_csv(filename):

    file = open(filename.name, 'r', encoding='utf-8')
    columns_to_drop = ['parentResourceId', 'resourceId', 'inRecycleBin', 'volumeId', 'fileId', 'DeleteTimeStamp', 'hash']
    
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
              'Path': 'object'
             }

    try:
        csv_name = (filename.name).replace('/', '\\')
    except AttributeError:
        csv_name = ''
    log.info(f'Started parsing {csv_name}')

    try:
        df = pd.read_csv(file, low_memory=False, quotechar='"', dtype=dtypes)
        df_scope = df.loc[df['Type'] == 'Scope', ['Type', 'scopeID', 'siteID', 'webID', 'listID', 'tenantID', 'webURL', 'remotePath', 'libraryType']]
        columns_to_fill = df_scope.columns.difference(['libraryType'])
        df_scope[columns_to_fill] = df_scope[columns_to_fill].fillna('')
        scopeID = df_scope['scopeID'].tolist()
        if 'inRecycleBin' in df.columns:
            convert = {'fileId': 'Int64',
                       'inRecycleBin': 'Int64'
                      }
            df = df.astype(convert)
            rbin_df = df.loc[df['Type'] == 'Deleted', ['Type', 'parentResourceId', 'resourceId', 'eTag', 'Path', 'Name', 'inRecycleBin', 'volumeId', 'fileId', 'DeleteTimeStamp', 'size', 'hash']]
            rbin_df = rbin_df.astype(object)
            rbin_df = rbin_df.where(pd.notna(rbin_df), '')
            df = df.drop(df[df['Type'] == 'Deleteed'].index)
            df.drop(columns=columns_to_drop, inplace=True)
        else:
            rbin_df = pd.DataFrame()
        df = df.astype(object)
        df = df.where(pd.notna(df), None)

    except Exception:
        log.error(f'Not a valid csv. {csv_name}')
        df = pd.DataFrame()
        rbin_df = pd.DataFrame()
        df_scope = pd.DataFrame()
        scopeID = []

    return df, rbin_df, df_scope, scopeID
