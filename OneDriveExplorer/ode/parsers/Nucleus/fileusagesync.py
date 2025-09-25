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

import ast
import logging
import sqlite3
import pandas as pd
import json


class SQLiteTableExporter:
    def __init__(self, db_path=None):
        self.log = logging.getLogger(__name__)
        self.db_path = db_path
        self.conn = None
        self.json_data = []
        self.df_data = pd.DataFrame()

    def set_db_path(self, db_path):
        self.db_path = db_path

    def parse_json(self, value):
        try:
            # First, decode the double-escaped string
            value = value.encode().decode('unicode_escape')

            # Now, parse the cleaned JSON
            return json.loads(value)
        except Exception as e:
            print("JSON Parse Error:", e)
            return None

    def nest_dict(self, flat_dict):
        nested = {}
        for flat_key, value in flat_dict.items():
            keys = flat_key.split('.')
            d = nested
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value
        return nested

    def load_data(self, saved_data):
        self.json_data = saved_data
        self.df_data = pd.json_normalize(saved_data)

    def load_csv(self, saved_data):
        self.df_data = pd.read_csv(saved_data)
        self.df_data['file.AllExtensions.SharingHistory.Instances'] = self.df_data['file.AllExtensions.SharingHistory.Instances'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else x)
        self.json_data = [self.nest_dict(row.dropna().to_dict()) for _, row in self.df_data.iterrows()]

    def get_recent_files_formatted_spo(self):
        if not self.db_path:
            self.log.error("Database path not set. Use set_db_path() first.")
            return

        try:
            self.conn = sqlite3.connect(f'file:/{self.db_path}/Microsoft.FileUsageSync.db?mode=ro', uri=True)
            query = "SELECT FormattedValue FROM recent_files_formatted_spo"
            try:
                df = pd.read_sql_query(query, self.conn)
                self.conn.close()
                parsed_jsons = df["FormattedValue"].apply(self.parse_json).dropna().tolist()
                self.json_data = parsed_jsons
                self.df_data = pd.json_normalize(parsed_jsons)
            except Exception as e:
                self.log.warning(f'Unable to parse {self.db_path}/Microsoft.FileUsageSync.db. {e}')
        except sqlite3.OperationalError:
            self.log.info('Microsoft.FileUsageSync.db does not exist')

