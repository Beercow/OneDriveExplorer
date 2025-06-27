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
import argparse
import time
import logging
import uuid
import pandas as pd
import warnings
import threading
import traceback
import queue
from datetime import datetime
import ode.parsers.dat as dat_parser
import ode.parsers.onedrive as onedrive_parser
from ode.parsers.odl import load_cparser
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
__version__ = "2025.06.27"
__email__ = "bmmaloney97@gmail.com"
rbin = []
DATParser = dat_parser.DATParser()
OneDriveParser = onedrive_parser.OneDriveParser()
SQLiteParser = sqlite_parser.SQLiteParser()
parsing_complete = threading.Event()
q = queue.Queue()
stop = threading.Event()
running_threads = []

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


def log_error_and_exit(error_msg: str, title="Unhandled Exception"):
    log_date = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    log_file = os.path.join(application_path, f'ODE_error_{log_date}.log')

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write('The following error has occurred and ODE is shutting down.\n')
            f.write(f'For further assistance: {__email__}\n')
            f.write(f'OneDriveExplorer v{__version__}\n\n')
            f.write(error_msg)
    except Exception as file_err:
        print("Failed to write error to file:", file_err)

    print(f"\n\n[{title}] See {log_file} for details.\n")

    # Stop all tracked threads gracefully
    stop.set()
    for t in running_threads:
        if t.is_alive():
            t.join(timeout=5)

    sys.exit(1)


def report_callback_exception(exc, val, tb):
    error_msg = ''.join(traceback.format_exception(exc, val, tb))
    log_error_and_exit(error_msg, title="Tkinter Exception")


def thread_exception_handler(args):
    error_msg = ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    log_error_and_exit(error_msg, title="Thread Exception")


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_error_and_exit(error_msg, title="CLI Exception")


# Activate global exception hooks
threading.excepthook = thread_exception_handler
sys.excepthook = global_exception_handler


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


def thread_parser(Parser):
    Parser.start_parsing()
    parsing_complete.set()  # Signal that parsing is complete


def main():
    fields_to_check = ['SETTINGS_DAT', 'SYNC_ENGINE', 'SAFE_DEL', 'LIST_SYNC', 'FILE_USAGE_SYNC', 'LOGS']

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

    parser.add_argument("--LIVE", help="Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and ODL logs. This mode is primarily used with KAPE.")
    parser.add_argument("--PROFILE", help="Profile folder to process. Default location: %%APPDATALOCAL%%\Microsoft\OneDrive")
    parser.add_argument("--SETTINGS_DAT", help="<UserCid>.dat file to be parsed", default='')
    parser.add_argument("--SYNC_ENGINE", help="SyncEngineDatabase.db file to load.", default='')
    parser.add_argument("--SAFE_DEL", help="SafeDelete.db file to load.", default='')
    parser.add_argument("--LIST_SYNC", help="Microsoft.ListSync.db file to load.", default='')
    parser.add_argument("--FILE_USAGE_SYNC", help="Microsoft.FileUsageSync.db file to load.", default='')
    parser.add_argument("--REG_HIVE", help="If a registry hive is provided then the mount points of the SyncEngines will be resolved.")
    parser.add_argument("--RECYCLE_BIN", help="$Recycle.Bin folder to load.")
    parser.add_argument("--LOGS", help="Directory to recursively process for ODL logs.", nargs='?', const=True)
    parser.add_argument("--output-dir", help="Directory to save results to. Be sure to include the full path in double quotes.", default=".")
    parser.add_argument("--csv", action='store_true', help="Save CSV formatted results.")
    parser.add_argument("--html", action='store_true', help="Save html formatted results.")
    parser.add_argument("--json", action='store_true', help="Save json formatted results. Use --pretty for a more human readable layout.")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')
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

    # Ensure only one mode is used
    if sum(bool(mode) for mode in [args.LIVE, args.PROFILE] + [getattr(args, f) for f in fields_to_check[:5]]) > 1:
        parser.error("Only one of --LIVE, --PROFILE, or any of --SETTINGS_DAT, --SYNC_ENGINE, --SAFE_DEL, --LIST_SYNC, --FILE_USAGE_SYNC can be used.")

    # Enforce dependency: --RECYCLE_BIN requires --REG_HIVE
    if args.RECYCLE_BIN and not args.REG_HIVE:
        parser.error("--RECYCLE_BIN requires --REG_HIVE to be specified.")

    # Enforce dependency: --LIST_SYNC requires --SYNC_ENGINE or --SETTINGS_DAT
    if args.LIST_SYNC and not (args.SYNC_ENGINE or args.SETTINGS_DAT):
        parser.error("--LIST_SYNC requires either --SYNC_ENGINE or --SETTINGS_DAT to be provided.")

    # --PROFILE allows --REG_HIVE and --RECYCLE_BIN; --LIVE does not
    if args.LIVE and (args.REG_HIVE or args.RECYCLE_BIN):
        parser.error("--LIVE cannot be used with --REG_HIVE or --RECYCLE_BIN.")

    if not args.debug:
        logging.getLogger().setLevel(logging.CRITICAL)

    if args.output_dir:
        if not os.path.exists(args.output_dir):
            try:
                os.makedirs(args.output_dir)
            except OSError:
                print('Error: Remove trailing \ from directory.\nExample: --output-dir "c:\\temp" ')
                sys.exit()

    if sys.argv[-1] == '--LOGS':
        args.LOGS = True

    should_parse = args.LIVE or args.PROFILE or (
        any(getattr(args, field) for field in fields_to_check) and not args.LOGS
    )

    if should_parse:
        Parser = manager.ParsingManager(args, q)

        t = threading.Thread(target=thread_parser,
                             args=(Parser,),
                             daemon=True)
        running_threads.append(t)
        t.start()

        last_stat = ''

        while not parsing_complete.is_set():
            try:
                stat = q.get_nowait()
                last_stat = stat
            except queue.Empty:
                pass

            if last_stat:
                sys.stdout.write(f'{last_stat} {next(spinner)}\r')
                sys.stdout.flush()

            time.sleep(0.2)

    sys.exit()


if __name__ == '__main__':
    main()
