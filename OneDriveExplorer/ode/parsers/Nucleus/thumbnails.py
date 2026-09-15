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

import base64
import hashlib
import io
import sqlite3
import logging
import pandas as pd


class ParseResult:
    def __init__(self, df):
        self.df = df

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(df={len(self.df)} rows)"


class SQLiteTableExporter:
    def __init__(self, db_path=None):
        self.log = logging.getLogger(__name__)
        self.db_path = db_path
        self.df = pd.DataFrame()
        self.account = None
        self.filename = None
        self.directory = None
        self.hash = None

    def set_db_path(self, db_path):
        self.db_path = db_path

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

    def get_thumbnails(self):
        self.directory = self.db_path.rsplit('\\', 1)[0]
        self.filename = self.db_path.split('\\')[-1]
        self.hash = self.hash_file(self.db_path)
        self.account = self.db_path.replace('/', '\\').split('\\')[-3]

        query = """
        SELECT
            t.thumbnail,
            tm.accountCid,
            di.driveId,
            tm.driveItemId,
            tm.listItemUniqueId,
            tm.fileSystemId,
            tm.cTag,
            tm.localId,
            mt.mimeType,
            tm.boxSize,
            tm.isLargestSize,
            tm.isFullFidelity,
            tm.imageModTime,
            tm.insertTime,
            tm.RemovedTime,
            tm.isLocal

        FROM thumbnail_metadata AS tm

        JOIN drive_identities AS di
            ON tm.driveIdentityRef = di.id

        LEFT JOIN mime_types AS mt
            ON tm.mimeTypeRef = mt.id

        JOIN thumbnails AS t
            ON tm.id = t.thumbnailMetadataRef;
        """

        try:
            # Connect to the SQLite database
            self.conn = sqlite3.connect(f'file:/{self.db_path}/Microsoft.ListSync.Thumbnails.db?mode=ro', uri=True)

            self.df = pd.read_sql_query(query, self.conn)
            self.df.to_csv('test.csv', index=False, encoding='utf-8')

        except sqlite3.OperationalError:
            self.log.info('Microsoft.ListSync.Thumbnails.db does not exist')
            self.df = pd.DataFrame()

        return ParseResult(
            self.df
        )

    def load_csv(self, saved_data):
        if isinstance(saved_data, str):
            self.df = pd.read_csv(saved_data, dtype=str)
        else:
            self.df = pd.read_csv(
                io.BytesIO(saved_data),
                dtype=str
            )

        self.df["thumbnail"] = self.df["thumbnail"].apply(
            lambda x: base64.b64decode(x)
            if pd.notna(x)
            else None
        )

        return ParseResult(
            self.df
        )
