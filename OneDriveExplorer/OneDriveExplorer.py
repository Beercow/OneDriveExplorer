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

import os
import sys
import re
import argparse
import time
import logging
import uuid
import pandas as pd
import warnings
import threading
import ode.parsers.dat as dat_parser
import ode.parsers.onedrive as onedrive_parser
from ode.parsers.odl import parse_odl, load_cparser
import ode.parsers.sqlite_db as sqlite_parser
from ode.utils import update_from_repo
import ode.parsers.manager as manager

warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

logging.basicConfig(level=logging.INFO,
                    format='\n\n%(asctime)s, %(levelname)s, %(message)s\n',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )

__author__ = "Brian Maloney"
__version__ = "2025.02.14"
__email__ = "bmmaloney97@gmail.com"
rbin = []
DATParser = dat_parser.DATParser()
OneDriveParser = onedrive_parser.OneDriveParser()
SQLiteParser = sqlite_parser.SQLiteParser()
result = None
parsing_complete = threading.Event()
onedrive_complete = threading.Event()
output_complete = threading.Event()


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


def guid():
    print('\033[1;35mGenerating 10 random GUIDs\033[1;0m\n')
    count = 0
    while True:
        print(f'\033[1;37m{uuid.uuid4()}\033[1;0m')
        count += 1
        if count == 10:
            print()
            break


def parse_sql_thread(sqlFolder, Parser):
    global result
    result = None
    result = Parser.start_parsing()
    parsing_complete.set()  # Signal that parsing is complete


def main():

    def has_settings(data):
        if isinstance(data, dict):
            if 'settings' in data:
                return True
            return any(has_settings(v) for v in data.values())
        return False

    banner = r'''
     _____                ___                           ___                 _
    (  _  )              (  _`\        _               (  _`\              (_ )
    | ( ) |  ___     __  | | ) | _ __ (_) _   _    __  | (_(_)       _ _    | |    _    _ __   __   _ __
    | | | |/' _ `\ /'__`\| | | )( '__)| |( ) ( ) /'__`\|  _)_ (`\/')( '_`\  | |  /'_`\ ( '__)/'__`\( '__)
    | (_) || ( ) |(  ___/| |_) || |   | || \_/ |(  ___/| (_( ) >  < | (_) ) | | ( (_) )| |  (  ___/| |
    (_____)(_) (_)`\____)(____/'(_)   (_)`\___/'`\____)(____/'(_/\_)| ,__/'(___)`\___/'(_)  `\____)(_) v{}
                                                                    | |        by @bmmaloney97
                                                                    (_)
    '''.format(__version__)

    print(f'\033[1;37m{banner}\033[1;0m')
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="<UserCid>.dat file to be parsed")
    parser.add_argument("-s", "--sql", help="OneDrive folder containing SQLite databases")
    parser.add_argument("-d", "--dir", help="Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and ODL logs. This mode is primarily used with KAPE.")
    parser.add_argument("-l", "--logs", help="Directory to recursively process for ODL logs.", nargs='?', const=True)
    parser.add_argument("-r", "--REG_HIVE", dest="reghive", help="If a registry hive is provided then the mount points of the SyncEngines will be resolved.")
    parser.add_argument("-rb", "--RECYCLE_BIN", help="$Recycle.Bin")
    parser.add_argument("--csv", action='store_true', help="Save CSV formatted results.")
    parser.add_argument("--html", action='store_true', help="Save html formatted results.")
    parser.add_argument("--json", action='store_true', help="Save json formatted results. Use --pretty for a more human readable layout.")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')
    parser.add_argument("--output-dir", help="Directory to save results to. Be sure to include the full path in double quotes.", default=".")
    parser.add_argument("--clist", help="List available cstructs. Defaults to 'cstructs' folder where program was executed. Use --cstructs for different cstruct folder.", action='store_true')
    parser.add_argument("--cstructs", help="The path where ODL cstructs are located. Defaults to 'cstructs' folder where program was executed.")
    parser.add_argument("--sync", help="If true, OneDriveExplorer will download the latest Cstrucs from https://github.com/Beercow/ODEFiles prior to running. Default is FALSE", action='store_true')
    parser.add_argument("--debug", help="Show debug information during processing.", action='store_true')
    parser.add_argument("--guids", help="OneDriveExplorer will generate 10 GUIDs and exit. Useful when creating new Cstructs. Default is FALSE", action='store_true')
    parser.add_argument("--gui", help=argparse.SUPPRESS, action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()
    spinner = spinning_cursor()

    if args.sync:
        update_from_repo(args.gui)
        sys.exit()

    if args.guids:
        guid()
        sys.exit()

    if args.clist:
        load_cparser(args.cstructs, args.clist)
        sys.exit()

    if not any([args.file, args.dir, args.sql, args.logs]):
        parser.print_help()
        print('\nEither -f, -d, -s or -l is required. Exiting')
        parser.exit()

    if args.RECYCLE_BIN and not args.reghive:
        parser.print_help()
        print('\n-r is required to use -rb. Exiting')
        parser.exit()

    if not args.debug:
        logging.getLogger().setLevel(logging.CRITICAL)

    if args.output_dir:
        if not os.path.exists(args.output_dir):
            try:
                os.makedirs(args.output_dir)
            except OSError:
                print('Error: Remove trailing \ from directory.\nExample: --output-dir "c:\\temp" ')
                sys.exit()

    if args.dir:
        logging.info(f'Searching for OneDrive data in {args.dir}')
        profile = {}
        users_folder = f'{args.dir}\\Users\\'
        rec_folder = f'{args.dir}\\$Recycle.Bin\\'
        user_names = [folder for folder in os.listdir(users_folder) if os.path.isdir(os.path.join(users_folder, folder))]
        settings_dir = re.compile(r'\\settings\\(?P<account>Personal|Business[0-9])$')
        listsync_settings_dir = re.compile(r'\\ListSync\\(?P<account>Business[0-9])\\settings$')
        logs_dir = re.compile(r'\\(?P<logs>logs)$')

        if os.path.exists(rec_folder):
            args.RECYCLE_BIN = rec_folder

        delay = time.time()
        for user in user_names:
            profile.setdefault(user, {})
            od_profile = os.path.join(users_folder, user, "AppData\\Local\\Microsoft\\OneDrive")

            for path, subdirs, files in os.walk(od_profile):
                settings_find = re.findall(settings_dir, path)
                listsync_find = re.findall(listsync_settings_dir, path)
                logs_find = re.findall(logs_dir, path)

                if (time.time() - delay) > 0.1:
                    sys.stdout.write(f'Searching for OneDrive data {next(spinner)}\r')
                    sys.stdout.flush()
                    delay = time.time()

                if settings_find:
                    profile[user].setdefault(settings_find[0], {})
                    profile[user][settings_find[0]].setdefault('settings', '')
                    profile[user][settings_find[0]]['settings'] = path

                if listsync_find:
                    profile[user].setdefault(listsync_find[0], {})
                    profile[user][listsync_find[0]].setdefault('listsync', '')
                    profile[user][listsync_find[0]]['listsync'] = path

                if logs_find:
                    profile[user].setdefault(logs_find[0], [])
                    profile[user][logs_find[0]].append(path)

        for key, value in profile.items():
            if has_settings(value):
                args.reghive = f'{users_folder}{key}\\NTUSER.DAT'
            else:
                args.reghive = None

            Parser = manager.ParsingManager(args, value, key)
            Parser.start_parsing()

    if args.sql:
        Parser = manager.ParsingManager(args)
        threading.Thread(target=parse_sql_thread,
                         args=(args.sql, Parser,),
                         daemon=True).start()

        delay = time.time()
        while not parsing_complete.is_set():
            if (time.time() - delay) > 0.1:
                sys.stdout.write(f'Parsing SQLite. Please wait.... {next(spinner)}\r')
                sys.stdout.flush()
                delay = time.time()
            time.sleep(0.2)

    if args.file:
        Parser = manager.ParsingManager(args)
        Parser.start_parsing()

    if args.logs:
        load_cparser(args.cstructs)
        if args.logs is not True:
            key_find = re.compile(r'Users/(?P<user>[^/]+)/AppData')
            pname = args.logs.replace('/', '\\').split(os.sep)[-2]
            key = re.findall(key_find, args.logs)
            if len(key) == 0:
                key = 'ODL'
            else:
                key = key[-1]
            odl = parse_odl(args.logs, pname)
            print()
            log_output = f'{args.output_dir}/{pname}_logs.csv'
            odl.to_csv(log_output, index=False)

    sys.exit()


if __name__ == '__main__':
    main()
