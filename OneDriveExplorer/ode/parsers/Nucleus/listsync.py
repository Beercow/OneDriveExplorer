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
import json
import sqlite3
import pandas as pd
import logging
from urllib.parse import unquote
from ode.utils import change_dtype


class ParseResult:
    def __init__(self, ocr_db, df_list_sync, scopeID, account):
        self.ocr_db = ocr_db
        self.df_list_sync = df_list_sync
        self.scopeID = scopeID
        self.account = account

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(ocr_db={len(self.ocr_db)} rows, df_list_sync={len(self.df_list_sync)} rows, scopeID={len(self.scopeID)})"


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

        self.replacements = {
            "-": "",
            "{": "",
            "}": ""
        }

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

    def populate_media_service_metadata(self, row):
        if 'wordDump' in row['MediaServiceMetadata']:
            return row['MediaServiceMetadata'].get('wordDump', '')
        return ''

    def compute_hash(self, row):
        if row['localHashDigest'] not in (None, ''):
            return f'quickXor({codecs.encode(bytes.fromhex(row["localHashDigest"][4:]), "base64").decode("utf-8").rstrip()})'
        else:
            return ''

    def get_permissions(self, perm_mask):
        if isinstance(perm_mask, str) and perm_mask.startswith("0x"):
            perm_mask = int(perm_mask, 16)

        permissions = [
            ("Full Control", 63),
            ("Design", 5),
            ("Edit", 12),
            ("Contribute", 3),
            ("Read", 40),
            ("Restricted View", None)
        ]

        for name, bit in permissions:
            if bit is None:
                return name
            if perm_mask & (1 << (bit - 1)):
                return name

    def get_df_scope(self):
        # Get all distinct keys
        self.cursor.execute("SELECT DISTINCT key FROM list_collection_item_attributes;")
        keys = [row[0] for row in self.cursor.fetchall()]

        if len(keys) == 0:
            self.df_scope = pd.DataFrame()
            return

        # Keys that must always exist in the pivot
        required_keys = ["siteTitle", "listTitle", "title"]

        # Add missing keys
        for key in required_keys:
            if key not in keys:
                keys.append(key)

        # Build dynamic pivot expressions
        pivot_expressions = [
            f"MAX(CASE WHEN key = '{k}' THEN value END) AS '{k}'" for k in keys
        ]
        pivot_sql = ",\n    ".join(pivot_expressions)

        # Build the list of pivot columns for the final SELECT.
        # Exclude "title" because we will create our own calculated title below.
        select_columns = [
            f'p."{k}"'
            for k in keys
            if k != "title"
        ]
        select_sql = ",\n    ".join(select_columns)

        # Build full query
        query = f"""
        WITH pivoted AS (
            SELECT
                listCollectionItemID,
                {pivot_sql}
            FROM list_collection_item_attributes
            GROUP BY listCollectionItemID
        )
        SELECT
            p.listCollectionItemID,
            {select_sql},

            COALESCE(
                NULLIF(
                    TRIM(
                        COALESCE(p.siteTitle, '') ||
                        CASE
                            WHEN p.siteTitle IS NOT NULL
                            AND p.listTitle IS NOT NULL
                            THEN '/'
                            ELSE ''
                        END ||
                        COALESCE(p.listTitle, '')
                    ),
                    ''
                ),
                p.title,
                l.title
            ) AS title,

            l.hidden,
            l.lastChangeToken,
            l.vroomSyncToken,
            l.permissionToken,
            l.effectivePermMask,
            l.lastLocalETag,
            l.localETagColumnName,
            l.flags,
            l.schemaVersion,
            l.lastViewChangeToken,
            l.timeOfLastSyncVerification,
            l.lastUnsyncTime,
            l.lastSyncTime,
            l.lastActiveTime,
            l.lastFullSyncTime,
            l.lastSettingsChangeToken,
            l.syncStartTime,
            l.swapSyncTokenTime,
            l.apiType,
            l.internalVersion,
            l.previousLastActiveTime,
            l.lastUnsyncReason,
            l.eligibilityDetails,
            l.lastRecordedListPermissions,
            l.hasResyncedFolders,
            l.ocdiVersion,
            l.teamID,
            l.templateType,
            l.lastForcedSyncSchema,
            l.lastResyncStartTime,
            l.lastResyncEndTime,
            l.lastResyncReason,
            s.conflictCount,
            s.changeCount,
            lc.name AS collectionName
        FROM pivoted AS p
        LEFT JOIN lists l
            ON l.listID = p.listId
            AND l.siteID = p.siteId
        LEFT JOIN list_sync_details s
            ON s.listID = p.listId
        LEFT JOIN list_collection_items AS lci
            ON p.listCollectionItemID = lci.listCollectionItemID
        LEFT JOIN list_collections AS lc
            ON lci.listCollectionID = lc.listCollectionID
        ORDER BY p.listCollectionItemID;
        """

        # Run query
        try:
            self.df_scope = pd.read_sql_query(query, self.conn)
            self.df_scope.rename(columns={"siteId": "siteID", "webId": "webID", "listId": "listID"}, inplace=True)
            self.df_scope['siteID'] = self.df_scope['siteID'].replace(self.replacements, regex=True).str.lower()
            self.df_scope['webID'] = self.df_scope['webID'].replace(self.replacements, regex=True).str.lower()
            self.df_scope['listID'] = self.df_scope['listID'].replace(self.replacements, regex=True).str.lower()
            self.df_scope['Type'] = 'Scope'
            self.df_scope.rename(columns={"listCollectionItemID": "libraryType"}, inplace=True)
        except Exception as e:
            self.log.error(f'Error running query:, {e}')
            self.df_scope = pd.DataFrame()

    def combine_duplicate_columns(self, df):
        if df.columns.is_unique:
            return df

        result = pd.DataFrame(index=df.index)

        # Keep track of columns we've already processed
        processed = set()

        for column in df.columns:
            if column in processed:
                continue

            # Get every occurrence of this column
            duplicate_columns = df.loc[:, df.columns == column]

            # If there's only one, just copy it
            if duplicate_columns.shape[1] > 1:
                self.log.warning(
                    f"Combining {duplicate_columns.shape[1]} "
                    f"duplicate columns: {column}"
                )

                result[column] = (
                    duplicate_columns
                    .bfill(axis=1)
                    .iloc[:, 0]
                )
            else:
                # Take the first non-null value from left to right
                result[column] = duplicate_columns.bfill(axis=1).iloc[:, 0]

            processed.add(column)

        return result

    def normalize_list_key(self, value):
        return str(value).replace("-", "").lower()

    def get_list_sync_data(self):
        self.directory = self.db_path.rsplit('\\', 1)[0]
        self.filename = self.db_path.split('\\')[-1]
        self.account = self.db_path.replace('/', '\\').split('\\')[-3]

        try:
            # Connect to the SQLite database
            self.conn = sqlite3.connect(f'file:/{self.db_path}?mode=ro', uri=True)
            self.conn.create_function("strtoll", 2, self.strtoll, deterministic=True)
            self.cursor = self.conn.cursor()

            self.get_df_scope()

            try:
                # Find tables matching a pattern
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%rows'")
                tables = self.cursor.fetchall()

                # Build lookup from listId + siteId -> templateType
                template_lookup = {}

                for _, row in self.df_scope.iterrows():
                    list_id = row.get("listID")
                    site_id = row.get("siteID")
                    template_type = row.get("templateType")

                    if pd.notna(list_id) and pd.notna(site_id):
                        key = f"list_{list_id}_{site_id}"
                        template_lookup[key] = template_type

                # Add templateType to each table tuple
                tables = [
                    (
                        table_name,
                        template_lookup.get(
                            self.normalize_list_key(
                                table_name.removesuffix("_rows")
                            )
                        )
                    )
                    for (table_name,) in tables
                ]

                # Perform a query on each matching table
                merged_data = []
                smerged_data = []

                for table in tables:
                    try:
                        table_name = table[0]

                        if table[1] not in ("101", "700"):
                            continue

                        self.cursor.execute(
                            f'PRAGMA table_info("{table_name}")'
                        )

                        table_info = self.cursor.fetchall()
                        all_col_names = [row[1] for row in table_info]

                        a2od_columns = [
                            column
                            for column in all_col_names
                            if column.startswith("A2OD") or column == "UniqueId"
                        ]

                        ocr_columns = [
                            column
                            for column in all_col_names
                            if column.startswith("MediaServiceOCR")
                        ]

                        if 'A2ODRemoteItemUniqueId' in all_col_names:
                            cols = ", ".join(
                                f'"{column}"'
                                for column in a2od_columns
                            )

                            cols += ", COALESCE(json_extract(A2ODExtendedMetadata, '$.riwu'), '') AS webURL"
                            cols += ", COALESCE(json_extract(A2ODExtendedMetadata, '$.riti'), '') AS tenantID"
                            cols += ", ProgID"
                            df_smerge = pd.read_sql_query(f'SELECT {cols} FROM "{table_name}" WHERE ProgID = "AddToOneDrive.MountPoint" AND A2ODRemoteItemUniqueId IS NOT NULL AND A2ODRemoteItemUniqueId <> ""', self.conn)
                            df_smerge.rename(columns={"A2ODRemoteItemSiteId": "siteID"}, inplace=True)
                            df_smerge.rename(columns={"A2ODRemoteItemWebId": "webID"}, inplace=True)
                            df_smerge.rename(columns={"A2ODRemoteItemListId": "listID"}, inplace=True)
                            df_smerge['siteID'] = df_smerge['siteID'].replace(self.replacements, regex=True).str.lower()
                            df_smerge['webID'] = df_smerge['webID'].replace(self.replacements, regex=True).str.lower()
                            df_smerge['listID'] = df_smerge['listID'].replace(self.replacements, regex=True).str.lower()
                            df_smerge.drop(columns=["A2ODMountCount", "A2ODIsMountPoint", "A2ODExtendedMetadata", "A2ODRemoteItemUniqueId"], inplace=True)
                            smerged_data.append(df_smerge)

                        if len(ocr_columns) == 1:
                            ocr_expression = f'"{ocr_columns[0]}" AS "MediaServiceOCR"'
                        elif len(ocr_columns) > 1:
                            quoted_ocr_columns = [
                                f'"{column}"'
                                for column in ocr_columns
                            ]
                            ocr_expression = (
                                f'COALESCE({", ".join(quoted_ocr_columns)}) '
                                f'AS "MediaServiceOCR"'
                            )
                        else:
                            ocr_expression = f'NULL AS "MediaServiceOCR"'

                        wanted_columns = [
                            "ContentType",
                            "ParentUniqueId",
                            "DocConcurrencyNumber",
                            "UniqueId",
                            "FileLeafRef",
                            "EncodedAbsUrl",
                            "Created",
                            "Modified",
                            "SMTotalFileStreamSize",
                            "StreamHash",
                            "SharedWithDetails",
                            "_ColorHex",
                            "MediaServiceMetadata",
                            "PermMask",
                            "ProgId",
                        ]

                        select_columns = [
                            f'"{column}"' if column in all_col_names
                            else f'NULL AS "{column}"'
                            for column in wanted_columns
                        ]

                        cols = ", ".join(select_columns)

                        df = pd.read_sql_query(
                            f'''
                            SELECT
                                {ocr_expression},
                                {cols}
                            FROM "{table_name}"
                            ''',
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
                        df.loc[df['ProgId'] == "AddToOneDrive.MountPoint", 'Type'] = "Folder"
                        df.drop(columns=["ProgId"], inplace=True)
                        merged_data.append(df)

                    except Exception as e:
                        self.log.warning(f'Unable to parse {table_name}. {e}')
                        continue

                # Merge all collected data into a single DataFrame
                if smerged_data:
                    smerged_df = pd.concat(smerged_data, ignore_index=True)

                    self.df_scope = self.combine_duplicate_columns(self.df_scope)

                    # Decide which keys to join on – likely siteID/webID/listID
                    self.df_scope = pd.merge(
                        self.df_scope,
                        smerged_df,
                        on=["siteID", "webID", "listID"],
                        how="outer"
                    )

                if merged_data:
                    df_list_sync = pd.concat(merged_data, ignore_index=True)
                    df_list_sync['fileStatus'] = ''
                    df_list_sync['folderStatus'] = ''
                    df_list_sync.loc[df_list_sync.Type == 'Document', ['FileSort']] = df_list_sync['Name'].str.lower()
                    df_list_sync.loc[df_list_sync.Type == 'Folder', ['FolderSort']] = df_list_sync['Name'].str.lower()
                    df_list_sync['folderColor'] = df_list_sync['folderColor'].astype("Int64").fillna(0)
                    df_list_sync['eTag'] = '"{' + df_list_sync['resourceID'].astype(str) + '},' + df_list_sync['DocConcurrencyNumber'].astype(str) + '"'
                    df_list_sync['resourceID'] = df_list_sync['resourceID'].replace(self.replacements, regex=True).str.lower()
                    df_list_sync['parentResourceID'] = df_list_sync['parentResourceID'].replace(self.replacements, regex=True).str.lower()
                    df_list_sync['size'] = pd.to_numeric(df_list_sync['size'], errors='coerce').fillna(0).astype(int)
                    df_list_sync['Path'] = df_list_sync['Path'].str.rsplit('/', n=1).str[0]
                    df_list_sync['size'] = df_list_sync['size'].apply(lambda x: '0 KB' if x == 0 else f'{x//1024 + 1:,} KB')
                    df_list_sync['localHashDigest'] = df_list_sync.apply(self.compute_hash, axis=1)
                    df_list_sync['SharedItem'] = df_list_sync['SharedWithDetails'].fillna("").str.strip().ne("").astype("Int64")
                    df_list_sync = change_dtype(df_list_sync, df_name='offline')
                    json_columns = ['SharedWithDetails']
                    df_list_sync[json_columns] = df_list_sync[json_columns].map(lambda x: json.loads(x) if pd.notna(x) and x.strip() else '')
                    #df_list_sync['MediaServiceMetadata'] = df_list_sync.apply(self.populate_media_service_metadata, axis=1)
                    df_list_sync['ListSync'] = df_list_sync[['SharedWithDetails', 'MediaServiceOCR']].apply(
                        lambda x: (
                            {'SharedWithDetails': x['SharedWithDetails'], 'MediaServiceOCR': x['MediaServiceOCR']}
                            if pd.notna(x['SharedWithDetails']) and str(x['SharedWithDetails']).strip() != ""
                            or pd.notna(x['MediaServiceOCR']) and str(x['MediaServiceOCR']).strip() != ""
                            else ''
                        ),
                        axis=1
                    )
                    df_list_sync['PermMask'] = df_list_sync['PermMask'].apply(lambda x: self.get_permissions(x))
                    df_list_sync.drop(columns=['SharedWithDetails', 'MediaServiceOCR'], inplace=True)

                    missing_ids = set(df_list_sync["parentResourceID"].dropna()) - set(df_list_sync["resourceID"].dropna())

                    missing_map = (
                        df_list_sync.loc[df_list_sync["parentResourceID"].isin(missing_ids), ["parentResourceID", "Path"]]
                        .set_index("parentResourceID")["Path"].apply(unquote)
                        .to_dict()
                    )

                    self.scopeID = list(missing_map.keys())
                    scopeid_lookup = pd.DataFrame([
                        {'listUrl': webURL, 'scopeID': scopeID}
                        for scopeID, webURL in missing_map.items()
                    ])

                    self.df_scope = self.df_scope.merge(
                        scopeid_lookup,
                        on='listUrl',
                        how='left'
                    )
                    self.df_scope['MountPoint'] = ''
                    self.df_scope.fillna('', inplace=True)

                    df_list_sync = pd.concat([df_list_sync, self.df_scope], ignore_index=True)
                    df_list_sync['scopeID'] = df_list_sync['scopeID'].fillna('')

                else:
                    self.log.info(f'No _rows tables found in {self.db_path}.')
                    df_list_sync = pd.DataFrame(columns=['resourceID', 'ListSync'])

            except Exception as e:
                self.log.warning(f'Unable to parse {self.db_path}. {e}')
                df_list_sync = pd.DataFrame(columns=['resourceID', 'ListSync'])

            self.conn.close()

        except sqlite3.OperationalError:
            self.log.info('Microsoft.ListSync.db does not exist')
            df_list_sync = pd.DataFrame(columns=['resourceID', 'ListSync'])

        ocr_db = df_list_sync[['resourceID', 'ListSync']]
        ocr_db = ocr_db[
            ocr_db['ListSync'].notna() & (ocr_db['ListSync'] != '')
            ]

        return ParseResult(
            ocr_db,
            df_list_sync,
            self.scopeID,
            self.account
        )
