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

import hashlib
import sqlite3
import logging
import pandas as pd


class ParseResult:
    def __init__(self, df, df_scope, scopeID, account):
        self.df = df
        self.df_scope = df_scope
        self.scopeID = scopeID
        self.account = account

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(df={len(self.df)} rows, scopeID={len(self.scopeID)})"


class SQLiteTableExporter:
    def __init__(self, db_path):
        self.log = logging.getLogger(__name__)
        self.db_path = db_path
        self.df_scope = pd.DataFrame()
        self.scopeID = []
        self.df = pd.DataFrame()
        self.account = None
        self.filename = None
        self.directory = None
        self.hash = None

    def hash_file(self, file):
        BUF_SIZE = 65536
        sha1 = hashlib.sha1()

        try:
            with open(file, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)

            return sha1.hexdigest()
        except Exception:
            return ''

    def get_files_on_denamd_rows(self):
        self.directory = self.db_path.rsplit('\\', 1)[0]
        self.filename = self.db_path.split('\\')[-1]
        self.hash = self.hash_file(self.db_path)
        self.account = self.db_path.replace('/', '\\').split('\\')[-3]

        try:
            # Connect to the SQLite database
            self.conn = sqlite3.connect(f'file:/{self.db_path}?mode=ro', uri=True)
            self.cursor = self.conn.cursor()

            try:
                self.df_scope = pd.read_sql_query("SELECT mountId, siteId, webId, listId, webUrl, mountPoint, libraryType from files_on_demand_mountpoints", self.conn)
                self.df_scope.insert(0, 'Type', 'Scope')
                self.df_scope.rename(columns={"siteId": "siteID"}, inplace=True)
                self.df_scope.rename(columns={"webId": "webID"}, inplace=True)
                self.df_scope.rename(columns={"listId": "listID"}, inplace=True)
                self.df_scope.rename(columns={"webUrl": "webURL"}, inplace=True)
                self.df_scope.rename(columns={"mountPoint": "MountPoint"}, inplace=True)

                self.scopeID = self.df_scope['mountId'].tolist()

                df_files = pd.read_sql_query("SELECT PinState, UniqueId, FileSystemId, CASE WHEN ParentFileSystemId = 'root' THEN mountId ELSE ParentFileSystemId END AS ParentFileSystemId, FonDLastModified, Name FROM files_on_demand_rows WHERE FileSystemId NOT IN (SELECT DISTINCT ParentFileSystemId FROM files_on_demand_rows WHERE ParentFileSystemId IS NOT NULL);", self.conn)
                df_files.insert(0, 'Type', 'File')

                df_folders = pd.read_sql_query("SELECT PinState, UniqueId, FileSystemId, CASE WHEN ParentFileSystemId = 'root' THEN mountId ELSE ParentFileSystemId END AS ParentFileSystemId, FonDLastModified, Name FROM files_on_demand_rows WHERE FileSystemId IN (SELECT DISTINCT ParentFileSystemId FROM files_on_demand_rows WHERE ParentFileSystemId IS NOT NULL);", self.conn)
                df_folders.insert(0, 'Type', 'Folder')

                self.df = pd.concat([self.df_scope, df_files, df_folders], ignore_index=True, axis=0)
                self.df = self.df.where(pd.notnull(self.df), None)
                self.df.rename(columns={"FonDLastModified": "lastChange"}, inplace=True)
                self.df['lastChange'] = pd.to_datetime(self.df['lastChange'], unit='ms').astype(str)
                self.df['PinState'] = self.df['PinState'].astype("Int64").fillna(0)
                self.df['size'] = ''
                self.df['fileStatus'] = ''
                self.df['folderStatus'] = ''

            except Exception as e:
                self.log.warning(f'Unable to parse {self.db_path}. {e}')
                self.df = pd.DataFrame()
                self.df_scope = pd.DataFrame()
                self.scopeID = []

            self.conn.close()

        except sqlite3.OperationalError:
            self.log.info('Microsoft.FilesOnDemand.db does not exist')
            self.df = pd.DataFrame()
            self.df_scope = pd.DataFrame()
            self.scopeID = []

        return ParseResult(
            self.df,
            self.df_scope,
            self.scopeID,
            self.account
        )
