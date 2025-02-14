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
# Based off of Yogesh Khatri, @SwiftForensics https://github.com/ydkhatri/OneDrive/blob/main/odl.py
#

import json
import logging
import sqlite3
import pandas as pd
from ode.utils import change_dtype


class SQLiteTableExporter:
    def __init__(self, db_path):
        self.log = logging.getLogger(__name__)
        self.db_path = db_path
        self.conn = None
        self.cursor = None

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

    def get_offline_data(self):
        try:
            # Connect to the SQLite database
            self.conn = sqlite3.connect(f'file:/{self.db_path}?mode=ro', uri=True)
            self.conn.create_function("strtoll", 2, self.strtoll, deterministic=True)
            self.cursor = self.conn.cursor()

            try:
                # Find tables matching a pattern
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%rows'")
                tables = self.cursor.fetchall()

                # Perform a query on each matching table
                merged_data = []
                for table in tables:
                    table_name = table[0]
#                    if self.column_exists(table_name, "MediaServiceOCR"):
                    df = pd.read_sql_query(
                        f'SELECT UniqueID, SharedWithDetails, MediaServiceMetadata FROM "{table_name}"', 
                        self.conn
                    )
                    df.rename(columns={"UniqueId": "resourceID"}, inplace=True)
                    merged_data.append(df)

                    # Merge all collected data into a single DataFrame
                if merged_data:
                    df_offline = pd.concat(merged_data, ignore_index=True)
                    df_offline['resourceID'] = df_offline['resourceID'].str.replace('-', '', regex=False)
                    df_offline = change_dtype(df_offline, df_name='offline')
                    json_columns = ['SharedWithDetails', 'MediaServiceMetadata']
                    df_offline[json_columns] = df_offline[json_columns].map(lambda x: json.loads(x) if pd.notna(x) and x.strip() else '')
                    df_offline['MediaServiceMetadata'] = df_offline.apply(self.populate_media_service_metadata, axis=1)
                    df_offline = df_offline.loc[~((df_offline["SharedWithDetails"] == '') & (df_offline["MediaServiceMetadata"] == ''))]
                    df_offline['ListSync'] = df_offline[['SharedWithDetails', 'MediaServiceMetadata']].apply(lambda x: {'SharedWithDetails': x[0], 'MediaServiceMetadata': x[1]}, axis=1)
                    df_offline.drop(columns=['SharedWithDetails', 'MediaServiceMetadata'], inplace=True)
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

        return df_offline
