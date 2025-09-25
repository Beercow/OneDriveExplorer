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

import codecs
import hashlib
import json
import logging
import sqlite3
from urllib.parse import unquote
import pandas as pd
from ode.utils import change_dtype


class ParseResult:
    def __init__(self, ocr_db, df_offline, scopeID, account):
        self.ocr_db = ocr_db
        self.df_offline = df_offline
        self.scopeID = scopeID
        self.account = account

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(ocr_db={len(self.ocr_db)} rows, df_offline={len(self.df_offline)} rows, scopeID={len(self.scopeID)})"


class SQLiteTableExporter:
    def __init__(self, db_path):
        self.log = logging.getLogger(__name__)
        self.db_path = db_path
        self.df_scope = pd.DataFrame()
        self.scopeID = []
        self.conn = None
        self.cursor = None
        self.account = None
        self.filename = None
        self.directory = None
        self.hash = None

    def strtoll(self, ptr, base):
        try:
            stripped_ptr = ptr.strip()
            result = int(stripped_ptr, base)

            if result < -(2**63):
                raise OverflowError("Underflow: Value too small for long long")
            elif result >= 2**63:
                raise OverflowError("Overflow: Value too large for long long")

            return result

        except ValueError:
            return 0
        except OverflowError as e:
            if "Underflow" in str(e):
                return -(2**63)
            elif "Overflow" in str(e):
                return (2**63) - 1

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

    def column_exists(self, table_name, column_name):
        self.cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = self.cursor.fetchall()
        for col in columns:
            if col[1] == column_name:
                return True
        return False

    def populate_media_service_metadata(self, row):
        if 'wordDump' in row['MediaServiceMetadata']:
            return row['MediaServiceMetadata'].get('wordDump', '')
        return ''

    def compute_hash(self, row):
        if row['localHashDigest'] not in (None, ''):
            return f'quickXor({codecs.encode(bytes.fromhex(row["localHashDigest"][4:]), "base64").decode("utf-8").rstrip()})'
        else:
            return ''

    def get_offline_data(self):
        self.directory = self.db_path.rsplit('\\', 1)[0]
        self.filename = self.db_path.split('\\')[-1]
        self.hash = self.hash_file(self.db_path)
        self.account = self.db_path.replace('/', '\\').split('\\')[-3]

        replacements = {
            "-": "",
            "{": "",
            "}": ""
        }

        try:
            # Connect to the SQLite database
            self.conn = sqlite3.connect(f'file:/{self.db_path}?mode=ro', uri=True)
            self.conn.create_function("strtoll", 2, self.strtoll, deterministic=True)
            self.cursor = self.conn.cursor()

            self.df_scope = pd.read_sql_query("SELECT lci.siteID, l.webID, lci.listID, l.siteUrl, l.listUrl, lci.listCollectionID FROM list_collection_items lci JOIN lists l ON lci.siteID = l.siteID AND lci.listID = l.listID;", self.conn)
            self.df_scope['siteID'] = self.df_scope['siteID'].replace(replacements, regex=True).str.lower()
            self.df_scope['webID'] = self.df_scope['webID'].replace(replacements, regex=True).str.lower()
            self.df_scope['listID'] = self.df_scope['listID'].replace(replacements, regex=True).str.lower()
            self.df_scope['Type'] = 'Scope'
            self.df_scope.rename(columns={"listCollectionID": "libraryType"}, inplace=True)

            try:
                # Find tables matching a pattern
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%rows'")
                tables = self.cursor.fetchall()

                # Perform a query on each matching table
                merged_data = []
                smerged_data = []
                for table in tables:
                    table_name = table[0]

                    self.cursor.execute(f'SELECT name FROM PRAGMA_TABLE_INFO("{table_name}") WHERE name LIKE "A2OD%"')
                    columns = self.cursor.fetchall()
                    col_names = [r[0] for r in columns]

                    if 'A2ODRemoteItemUniqueId' in col_names:
                        cols = ", ".join(col_names)
                        cols += ", COALESCE(json_extract(A2ODExtendedMetadata, '$.riwu'), '') AS webURL"
                        cols += ", COALESCE(json_extract(A2ODExtendedMetadata, '$.riti'), '') AS tenantID"
                        cols += ", ProgID"
                        df_smerge = pd.read_sql_query(f'SELECT {cols} FROM "{table_name}" WHERE ProgID = "AddToOneDrive.MountPoint" AND A2ODRemoteItemUniqueId IS NOT NULL AND A2ODRemoteItemUniqueId <> ""', self.conn)
                        df_smerge.rename(columns={"A2ODRemoteItemSiteId": "siteID"}, inplace=True)
                        df_smerge.rename(columns={"A2ODRemoteItemWebId": "webID"}, inplace=True)
                        df_smerge.rename(columns={"A2ODRemoteItemListId": "listID"}, inplace=True)
                        df_smerge['siteID'] = df_smerge['siteID'].replace(replacements, regex=True).str.lower()
                        df_smerge['webID'] = df_smerge['webID'].replace(replacements, regex=True).str.lower()
                        df_smerge['listID'] = df_smerge['listID'].replace(replacements, regex=True).str.lower()
                        df_smerge.drop(columns=["A2ODMountCount", "A2ODIsMountPoint", "A2ODExtendedMetadata", "A2ODRemoteItemUniqueId"], inplace=True)
                        smerged_data.append(df_smerge)

                    df = pd.read_sql_query(
                        f'SELECT ContentType, ParentUniqueId, DocConcurrencyNumber, UniqueID, FileLeafRef, EncodedAbsUrl, Created, Modified, SMTotalFileStreamSize, StreamHash, SharedWithDetails, _ColorHex, MediaServiceMetadata FROM "{table_name}"',
                        self.conn
                    )
                    df.rename(columns={"ContentType": "Type"}, inplace=True)
                    df.rename(columns={"ParentUniqueId": "parentResourceID"}, inplace=True)
                    df.rename(columns={"UniqueId": "resourceID"}, inplace=True)
                    df.rename(columns={"FileLeafRef": "Name"}, inplace=True)
                    df.rename(columns={"EncodedAbsUrl": "Path"}, inplace=True)
                    df.rename(columns={"SMTotalFileStreamSize": "size"}, inplace=True)
                    df.rename(columns={"StreamHash": "localHashDigest"}, inplace=True)
                    df.rename(columns={"_ColorHex": "folderColor"}, inplace=True)
                    df.rename(columns={"Modified": "lastChange"}, inplace=True)
                    merged_data.append(df)

                # Merge all collected data into a single DataFrame
                if smerged_data:
                    smerged_df = pd.concat(smerged_data, ignore_index=True)

                    # Decide which keys to join on – likely siteID/webID/listID
                    self.df_scope = pd.merge(
                        self.df_scope,
                        smerged_df,
                        on=["siteID", "webID", "listID"],
                        how="outer"
                    )

                if merged_data:
                    df_offline = pd.concat(merged_data, ignore_index=True)
                    df_offline['fileStatus'] = ''
                    df_offline['folderStatus'] = ''
                    df_offline.loc[df_offline.Type == 'Document', ['FileSort']] = df_offline['Name'].str.lower()
                    df_offline.loc[df_offline.Type == 'Folder', ['FolderSort']] = df_offline['Name'].str.lower()
                    df_offline['folderColor'] = df_offline['folderColor'].astype("Int64").fillna(0)
                    df_offline['eTag'] = '"{' + df_offline['resourceID'].astype(str) + '},' + df_offline['DocConcurrencyNumber'].astype(str) + '"'
                    df_offline['resourceID'] = df_offline['resourceID'].replace(replacements, regex=True).str.lower()
                    df_offline['parentResourceID'] = df_offline['parentResourceID'].replace(replacements, regex=True).str.lower()
                    df_offline['size'] = pd.to_numeric(df_offline['size'], errors='coerce').fillna(0).astype(int)
                    df_offline['Path'] = df_offline['Path'].str.rsplit('/', n=1).str[0]
                    df_offline['size'] = df_offline['size'].apply(lambda x: '0 KB' if x == 0 else f'{x//1024 + 1:,} KB')
                    df_offline['localHashDigest'] = df_offline.apply(self.compute_hash, axis=1)
                    df_offline['SharedItem'] = df_offline['SharedWithDetails'].fillna("").str.strip().ne("").astype("Int64")
                    df_offline = change_dtype(df_offline, df_name='offline')
                    json_columns = ['SharedWithDetails', 'MediaServiceMetadata']
                    df_offline[json_columns] = df_offline[json_columns].map(lambda x: json.loads(x) if pd.notna(x) and x.strip() else '')
                    df_offline['MediaServiceMetadata'] = df_offline.apply(self.populate_media_service_metadata, axis=1)
                    df_offline['ListSync'] = df_offline[['SharedWithDetails', 'MediaServiceMetadata']].apply(
                        lambda x: (
                            {'SharedWithDetails': x['SharedWithDetails'], 'MediaServiceMetadata': x['MediaServiceMetadata']}
                            if pd.notna(x['SharedWithDetails']) and str(x['SharedWithDetails']).strip() != ""
                            or pd.notna(x['MediaServiceMetadata']) and str(x['MediaServiceMetadata']).strip() != ""
                            else ''
                        ),
                        axis=1
                    )
                    df_offline.drop(columns=['SharedWithDetails', 'MediaServiceMetadata'], inplace=True)

                    missing_ids = set(df_offline["parentResourceID"].dropna()) - set(df_offline["resourceID"].dropna())

                    missing_map = (
                        df_offline.loc[df_offline["parentResourceID"].isin(missing_ids), ["parentResourceID", "Path"]]
                        .set_index("parentResourceID")["Path"].apply(unquote)
                        .to_dict()
                    )

                    self.scopeID = list(missing_map.keys())
                    scopeid_lookup = pd.DataFrame([
                        {'siteUrl': webURL.rsplit('/', 1)[0], 'scopeID': scopeID}
                        for scopeID, webURL in missing_map.items()
                    ])

                    self.df_scope = self.df_scope.merge(
                        scopeid_lookup,
                        on='siteUrl',
                        how='left'
                    )
                    self.df_scope['MountPoint'] = ''
                    self.df_scope.fillna('', inplace=True)

                    df_offline = pd.concat([df_offline, self.df_scope], ignore_index=True)
                    df_offline['scopeID'] = df_offline['scopeID'].fillna('')

                else:
                    self.log.info(f'No _rows tables found in {self.db_path}.')
                    df_offline = pd.DataFrame(columns=['resourceID', 'ListSync'])

            except Exception as e:
                self.log.warning(f'Unable to parse {self.db_path}. {e}')
                df_offline = pd.DataFrame(columns=['resourceID', 'ListSync'])

            self.conn.close()

        except sqlite3.OperationalError:
            self.log.info('Microsoft.ListSync.db does not exist')
            df_offline = pd.DataFrame(columns=['resourceID', 'ListSync'])

        ocr_db = df_offline[['resourceID', 'ListSync']]
        ocr_db = ocr_db[
            ocr_db['ListSync'].notna() & (ocr_db['ListSync'] != '')
            ]

        return ParseResult(
            ocr_db,
            df_offline,
            self.scopeID,
            self.account
        )
