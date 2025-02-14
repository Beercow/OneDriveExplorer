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
import os
import time
import re
import ode.parsers.dat as dat_parser
import ode.parsers.onedrive as onedrive_parser
import ode.parsers.sqlite_db as sqlite_parser
import ode.parsers.offline as SQLiteTableExporter
from ode.parsers.odl import parse_odl
from ode.renderers.json import print_json
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
import pandas as pd

log = logging.getLogger(__name__)


class ParsingManager:
    def __init__(self, args, profile=False, user=False):
        self.args = args
        self.profile = profile
        self.user = user
        self.DATParser = dat_parser.DATParser()
        self.OneDriveParser = onedrive_parser.OneDriveParser()
        self.SQLiteParser = sqlite_parser.SQLiteParser()
        self.start = time.time()

    def start_parsing(self):
        if self.args.file:
            account = os.path.dirname(self.args.file.replace('/', '\\')).rsplit('\\', 1)[-1]
            name = f'{account}_{os.path.split(self.args.file)[1]}'

            od_settings = self.DATParser.parse_dat(self.args.file, account)

            if od_settings and not od_settings.df.empty:
                self.parse_results(od_settings, self.args.file, name, self.start, False, self.args.reghive, self.args.RECYCLE_BIN, pd.DataFrame(columns=['resourceID', 'ListSync']))
            else:
                filename = self.args.file.replace('/', '\\')
                print(f'Unable to parse {filename}.')
                log.warning(f'Unable to parse {filename}.')
                return

        if self.args.sql:
            self.args.sql = self.args.sql.replace('/', '\\')
            sql_dir = re.compile(r'\\Users\\(?P<user>.*?)\\AppData\\Local\\Microsoft\\OneDrive\\settings\\(?P<account>.*?)$')
            sql_find = re.findall(sql_dir, self.args.sql)
            try:
                name = f'{sql_find[0][0]}_{sql_find[0][1]}'
            except Exception:
                name = 'SQLite_DB'

            od_settings = self.SQLiteParser.parse_sql(self.args.sql)

            if od_settings and not od_settings.df.empty:
                self.parse_results(od_settings, self.args.sql, od_settings.account, self.start, False, self.args.reghive, self.args.RECYCLE_BIN, pd.DataFrame(columns=['resourceID', 'ListSync']))

        if self.args.dir:
            for key, value in self.profile.items():
                offline_db = pd.DataFrame(columns=['resourceID', 'ListSync'])
                if key == 'logs':
                    if self.args.logs:
                        log.info(f'Parsing OneDrive logs for {key}')
                        print(f'\n\nParsing {key} OneDrive logs\n')
                        for folder_name in value:
                            if self.user:
                                pname = f'{self.user}_{folder_name.split(os.sep)[-2]}'
                            else:
                                pname = folder_name.split(os.sep)[-2]

                            odl = parse_odl(folder_name, pname)
                            print()
                            log_output = f'{self.args.output_dir}/{pname}_logs.csv'
                            odl.to_csv(log_output, index=False)

                    continue

                # First, process "listsync" if it exists
                if "listsync" in value:
                    v = value["listsync"].replace('/', '\\')
                    log.info('Gathering offline data. Please wait....')
                    print('Gathering offline data. Please wait....')
                    exporter = SQLiteTableExporter.SQLiteTableExporter(f'{v}\\Microsoft.ListSync.db')
                    offline_db = exporter.get_offline_data()

                # Then process "settings" if it exists
                if "settings" in value:
                    v = value["settings"].replace('/', '\\')
                    log.info('Building folder list. Please wait....')
                    print('Building folder list. Please wait....')
                    for path, subdirs, files in os.walk(v):
                        for name in files:
                            if name.endswith('.dat'):
                                od_settings = self.DATParser.parse_dat(f'{v}\\{name}', key)
                                if od_settings and not od_settings.df.empty:
                                    if self.user:
                                        pname = f'{self.user}_{od_settings.account}_{name}'
                                    else:
                                        pname = f'{od_settings.account}_{name}'
                                    self.parse_results(od_settings, f'{v}\\{name}', pname, self.start, False, self.args.reghive, self.args.RECYCLE_BIN, pd.DataFrame(columns=['resourceID', 'ListSync']))
                    od_settings = self.SQLiteParser.parse_sql(v)
                    if od_settings:
                        if not od_settings.df.empty:
                            if self.user:
                                pname = f'{self.user}_{key}'
                            else:
                                pname = key
                            self.parse_results(od_settings, v, pname, self.start, False, self.args.reghive, self.args.RECYCLE_BIN, offline_db)

    def parse_results(self, od_settings, filename, key, start, x=False, reghive=False, recbin=False, offline_db=False, gui=False, pb=False, value_label=False, save=True):
        cache, df, rbin_df = self.OneDriveParser.parse_onedrive(od_settings,
                                                                filename,
                                                                reghive,
                                                                recbin,
                                                                offline_db)

        if not cache:
            filename = self.args.file.replace('/', '\\')
            print(f'Unable to parse {filename}.')
            log.warning(f'Unable to parse {filename}.')
            return

        self.save_output(cache, df, rbin_df, key)

    def save_output(self, cache, df, rbin_df, name):
        if self.args.csv:
            print_csv(df, rbin_df, name, self.args.output_dir)

        if self.args.html:
            print_html(df, rbin_df, name, self.args.output_dir)

        if self.args.json:
            print_json(cache, name, self.args.pretty, self.args.output_dir)
        else:
            print_csv(df, rbin_df, name, self.args.output_dir)

        try:
            file_count = df.Type.value_counts()['File']
        except KeyError:
            logging.warning("KeyError: 'File'")
            file_count = 0

        try:
            del_count = len(rbin_df)
        except (KeyError, AttributeError):
            logging.warning("KeyError: 'File - deleted'")
            del_count = 0

        try:
            folder_count = df.Type.value_counts()['Folder']
        except KeyError:
            logging.warning("KeyError: 'Folder'")
            folder_count = 0

        print(f'\n\n{file_count} files(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - self.start), ".4f")} seconds\n')
