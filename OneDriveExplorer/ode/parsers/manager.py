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

import ctypes
import logging
import os
import time
import re
from Registry import Registry
from ode.helpers.mft import live_hive
import ode.parsers.dat as dat_parser
import ode.parsers.onedrive as onedrive_parser
import ode.parsers.sqlite_db as sqlite_parser
import ode.parsers.offline as SQLiteTableExporter
import ode.parsers.fileusagesync as fileusagesync
from ode.parsers.odl import parse_odl, load_cparser
from ode.renderers.json import print_json
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
import pandas as pd
import json

log = logging.getLogger(__name__)
fus = fileusagesync.SQLiteTableExporter()


def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class ParsingManager:
    def __init__(self, args, q):
        self.args = args
        self.q = q
        self.profile = {}
        self.fields_to_check = ['SETTINGS_DAT', 'SYNC_ENGINE', 'SAFE_DEL', 'LIST_SYNC', 'FILE_USAGE_SYNC', 'LOGS']
        self.DATParser = dat_parser.DATParser()
        self.OneDriveParser = onedrive_parser.OneDriveParser()
        self.SQLiteParser = sqlite_parser.SQLiteParser()
        self.start = time.time()

    def start_parsing(self):
        if self.args.REG_HIVE:
            try:
                Registry.Registry(self.args.REG_HIVE)
            except Exception:
                try:
                    parts = os.path.splitdrive(self.args.REG_HIVE)[1].replace('\\', '/').rsplit('/', 2)
                    alt_path = f'{parts[0]}/{parts[1]}'
                    key = parts[-2]
                    self.q.put(f'Searching for {key} NTUSER.DAT. Please wait....')
                    self.args.REG_HIVE = live_hive(key, alt_path)
                except Exception:
                    pass
                self.q.put('')
                print('\r\n')

        if any(getattr(self.args, field) for field in self.fields_to_check):
            offline_db = pd.DataFrame(columns=['resourceID', 'ListSync'])

            if self.args.LIST_SYNC != '':
                log.info("Stared parsing Microsoft.ListSync.db")
                self.q.put('Stared parsing Microsoft.ListSync.db. Please wait....')
                exporter = SQLiteTableExporter.SQLiteTableExporter(self.args.LIST_SYNC)
                offline_db = exporter.get_offline_data()
                self.q.put('')
                print('\r\n')

            if self.args.FILE_USAGE_SYNC != '':
                cache = {"Path": '', "Name": '', "Hash": '', "Account": ''}
                directory, file = os.path.split(self.args.FILE_USAGE_SYNC)
                fus.set_db_path(directory)
                log.info("Stared parsing Microsoft.FileUsageSync.db")
                self.q.put('Stared parsing Microsoft.FileUsageSync.db. Pleas wait....')
                fus.get_recent_files_formatted_spo()
                if not any([self.args.SETTINGS_DAT, self.args.SYNC_ENGINE, self.args.SAFE_DEL]):
                    self.save_output(cache, pd.DataFrame(), pd.DataFrame(), '')
                self.q.put('')
                print('\r\n')

            if self.args.SETTINGS_DAT != '':
                account = os.path.dirname(self.args.SETTINGS_DAT.replace('/', '\\')).rsplit('\\', 1)[-1]
                name = f'{account}_{os.path.split(self.args.SETTINGS_DAT)[1]}'

                od_settings = self.DATParser.parse_dat(self.args.SETTINGS_DAT, account)

                if od_settings and not od_settings.df.empty:
                    self.parse_results(od_settings, self.args.SETTINGS_DAT, name, self.start, False, self.args.REG_HIVE, self.args.RECYCLE_BIN, offline_db)

            if self.args.SYNC_ENGINE != '' or self.args.SAFE_DEL != '':
                self.q.put('Parsing settings SQLite. Please wait....')
                sedb = self.args.SYNC_ENGINE
                sddb = self.args.SAFE_DEL
                filename = False

                od_settings = self.SQLiteParser.parse_sql(filename, sedb, sddb)

                if not filename:
                    filename = [sedb, sddb]

                if od_settings:
                    self.parse_results(od_settings, filename, od_settings.account, self.start, False, self.args.REG_HIVE, self.args.RECYCLE_BIN, offline_db)
                self.q.put('')
                print('\r\n')

            if self.args.LOGS and (not self.args.LIVE or not self.args.PROFILE):
                load_cparser(self.args.cstructs)
                if self.args.LOGS is not True:
                    key_find = re.compile(r'Users/(?P<user>[^/]+)/AppData')
                    pname = self.args.LOGS.replace('/', '\\').split(os.sep)[-2]
                    key = re.findall(key_find, self.args.LOGS)
                    if len(key) == 0:
                        key = 'ODL'
                    else:
                        key = key[-1]

                    odl = parse_odl(self.args.LOGS, pname)
                    print()
                    log_output = f'{self.args.output_dir}/{pname}_logs.csv'
                    odl.to_csv(log_output, index=False)

        if self.args.LIVE or self.args.PROFILE:
            if self.args.LIVE:
                self.q.put(f'Searching for OneDrive data in {self.args.LIVE}')
                users_folder = os.path.expandvars("%SystemDrive%\\Users\\")
                rec_folder = os.path.expandvars("%SystemDrive%\\$Recycle.Bin\\")
                user_names = [folder for folder in os.listdir(users_folder) if os.path.isdir(os.path.join(users_folder, folder))]

                if os.path.exists(rec_folder):
                    self.args.RECYCLE_BIN = rec_folder

                for user in user_names:
                    self.profile.setdefault(user, {})
                    od_profile = os.path.join(users_folder, user, "AppData\\Local\\Microsoft\\OneDrive")
                    self.build_profile(od_profile, user)

                for key, value in self.profile.items():
                    if self.has_settings(value) and is_user_admin():
                        self.args.REG_HIVE = live_hive(key, os.path.splitdrive(os.path.join(users_folder, key))[1].replace('\\', '/'))
                    else:
                        self.args.REG_HIVE = ''

                    self.parse_profile(value, key)

            else:
                profile_path = self.args.PROFILE.replace('/', '\\')
                self.build_profile(profile_path)
                self.parse_profile(self.profile)

    def parse_profile(self, profile, user=False):
        for key, value in profile.items():
            offline_db = pd.DataFrame(columns=['resourceID', 'ListSync'])
            if key == 'logs':
                load_cparser(self.args.cstructs)
                if self.args.LOGS:
                    log.info(f'Parsing OneDrive logs for {key}')
                    print(f'\n\nParsing {key} OneDrive logs\n')
                    for folder_name in value:
                        if user:
                            pname = f'{user}_{folder_name.split(os.sep)[-2]}'
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
                self.q.put('Gathering offline data. Please wait....')
                exporter = SQLiteTableExporter.SQLiteTableExporter(f'{v}\\Microsoft.ListSync.db')
                offline_db = exporter.get_offline_data()
                self.q.put('')
                print('\r\n')
                log.info('Gathering file usage data. Please wait....')
                self.q.put('Gathering file usage data. Please wait....')
                fus.set_db_path(f'{v}')
                fus.get_recent_files_formatted_spo()
                self.q.put('')
                print('\r\n')

            # Then process "settings" if it exists
            if "settings" in value:
                v = value["settings"].replace('/', '\\')
                log.info('Building folder list. Please wait....')
                for path, subdirs, files in os.walk(v):
                    for name in files:
                        if name.endswith('.dat') and not (name.endswith('import.dat') or name.endswith('screenshot.dat')):
                            od_settings = self.DATParser.parse_dat(f'{v}\\{name}', key)
                            if od_settings and not od_settings.df.empty:
                                if user:
                                    pname = f'{user}_{od_settings.account}_{name}'
                                else:
                                    pname = f'{od_settings.account}_{name}'
                                self.parse_results(od_settings, f'{v}\\{name}', pname, self.start, False, self.args.REG_HIVE, self.args.RECYCLE_BIN, pd.DataFrame(columns=['resourceID', 'ListSync']))
                self.q.put('Parsing SyncEngine/SafeDelete db. Please wait....')
                od_settings = self.SQLiteParser.parse_sql(v)

                if od_settings:
                    if not od_settings.df.empty:
                        if user:
                            pname = f'{user}_{key}'
                        else:
                            pname = key
                        self.parse_results(od_settings, v, pname, self.start, False, self.args.REG_HIVE, self.args.RECYCLE_BIN, offline_db)
                self.q.put('')
                print('\r\n')

    def has_settings(self, data):
        if isinstance(data, dict):
            if 'settings' in data:
                return True
            return any(self.has_settings(v) for v in data.values())
        return False

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

    def build_profile(self, profile_path, user=False):
        profile_path = profile_path.replace('/', '\\')

        patterns = {
            'settings': re.compile(r'\\settings\\(?P<account>Personal|Business[0-9])$'),
            'listsync': re.compile(r'\\ListSync\\(?P<account>Business[0-9])\\settings$'),
            'logs': re.compile(r'\\(?P<logs>logs)$')
        }

        for path, subdirs, files in os.walk(profile_path):
            for key, pattern in patterns.items():
                match = pattern.search(path)
                if not match:
                    continue

                identifier = match.group('account' if key != 'logs' else 'logs')

                target = self.profile[user] if user else self.profile
                if key == 'logs':
                    target.setdefault(identifier, []).append(path)
                else:
                    target.setdefault(identifier, {}).setdefault(key, '')
                    target[identifier][key] = path

    def save_output(self, cache, df, rbin_df, name):
        comment_json = json.dumps({
            "Path": cache["Path"],
            "Name": cache["Name"],
            "Hash": cache["Hash"],
            "Account": cache["Account"]
        })

        # Save outputs based on args
        if self.args.csv or not (self.args.html or self.args.json):
            print('\r\n')
            self.q.put('Saving csv. Please wait....')
            try:
                print_csv(df, rbin_df, name, self.args.output_dir, comment_json, fus.df_data)
            except Exception as e:
                log.warning(f'Unable to save CSV: {e}')
            self.q.put('')

        if self.args.html:
            print('\r\n')
            self.q.put('Saving html. Please wait....')
            try:
                print_html(df, rbin_df, name, self.args.output_dir, fus.df_data)
            except Exception as e:
                log.warning(f'Unable to save HTML: {e}')

        if self.args.json:
            print('\r\n')
            self.q.put('Saving json. Please wait....')
            try:
                print_json(cache, name, fus.json_data, self.args.pretty, self.args.output_dir)
            except Exception as e:
                log.warning(f'Unable to save JSON: {e}')

        try:
            file_count = df.Type.value_counts().get('File', 0)
            folder_count = df.Type.value_counts().get('Folder', 0)
            del_count = len(rbin_df) if rbin_df is not None else 0
        except Exception:
            file_count = 0
            folder_count = 0
            del_count = 0

        elapsed = format((time.time() - self.start), ".4f")
        print(f'\n\n{file_count} file(s) - {del_count} deleted, {folder_count} folder(s) in {elapsed} seconds\n')
