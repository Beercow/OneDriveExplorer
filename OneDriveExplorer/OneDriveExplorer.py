import os
import sys
import re
import argparse
import time
import logging
from ode.renderers.json import print_json
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
from ode.parsers.dat import parse_dat
from ode.parsers.onedrive import parse_onedrive
from ode.parsers.odl import parse_odl, load_cparser

logging.basicConfig(level=logging.INFO,
                    format='\n\n%(asctime)s, %(levelname)s, %(message)s\n',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )

__author__ = "Brian Maloney"
__version__ = "2023.03.06"
__email__ = "bmmaloney97@gmail.com"
rbin = []


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


def main():
    def output():
        if args.csv:
            print_csv(df, rbin_df, name, args.csv, args.csvf)

        if args.html:
            print_html(df, rbin_df, name, args.html)

        if ((args.csv or args.html) and args.json) or (not args.csv and not args.html):
            if not args.json:
                args.json = '.'
            print_json(df, rbin_df, name, args.pretty, args.json)

        try:
            file_count = df.Type.value_counts()['File']
        except KeyError:
            logging.warning("KeyError: 'File'")
            file_count = 0

        try:
            del_count = rbin_df.Type.value_counts()['File - deleted']
        except (KeyError, AttributeError):
            logging.warning("KeyError: 'File - deleted'")
            del_count = 0

        try:
            folder_count = df.Type.value_counts()['Folder']
        except KeyError:
            logging.warning("KeyError: 'Folder'")
            folder_count = 0

        print(f'{file_count} files(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds')

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

    print(banner)
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="<UserCid>.dat file to be parsed")
    parser.add_argument("-d", "--dir", help="Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and ODL logs. This mode is primarily used with KAPE.")
    parser.add_argument("-r", "--REG_HIVE", dest="reghive", help="If a registry hive is provided then the mount points of the SyncEngines will be resolved.")
    parser.add_argument("-rb", "--RECYCLE_BIN", help="$Recycle.Bin")
    parser.add_argument("--csv", help="Directory to save CSV formatted results to. Be sure to include the full path in double quotes.")
    parser.add_argument("--csvf", help="File name to save CSV formatted results to. When present, overrides default name.")
    parser.add_argument("--html", help="Directory to save html formatted results to. Be sure to include the full path in double quotes.")
    parser.add_argument("--json", help="Directory to save json representation to. Use --pretty for a more human readable layout.")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')
    parser.add_argument("--cstructs", help="The path where ODL cstructs are located. Defaults to 'cstructs' folder where program was executed.")
    parser.add_argument("--debug", help="Show debug information during processing.", action='store_true')
    parser.add_argument("-l", "--logs", help="Directory to recursively process for ODL logs.", nargs='?', const=True)

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        print('\nEither -f or -d is required. Exiting')
        parser.exit()

    if args.RECYCLE_BIN and not args.reghive:
        parser.print_help()
        print('\n-r is required to use -rb. Exiting')
        parser.exit()

    if not args.debug:
        logging.getLogger().setLevel(logging.CRITICAL)

    if args.json:
        if not os.path.exists(args.json):
            try:
                os.makedirs(args.json)
            except OSError:
                print('Error: Remove trailing \ from directory.\nExample: --json "c:\\temp" ')
                sys.exit()

    if args.csv:
        if not os.path.exists(args.csv):
            try:
                os.makedirs(args.csv)
            except OSError:
                print('Error: Remove trailing \ from directory.\nExample: --csv "c:\\temp" ')
                sys.exit()

    if args.html:
        if not os.path.exists(args.html):
            try:
                os.makedirs(args.html)
            except OSError:
                print('Error: Remove trailing \ from directory.\nExample: --html "c:\\temp" ')
                sys.exit()

    if args.file:
        account = os.path.dirname(args.file.replace('/', '\\')).rsplit('\\', 1)[-1]
        df, name = parse_dat(args.file, args.reghive, args.RECYCLE_BIN, start, account)
        df, rbin_df = parse_onedrive(df, account, args.reghive, args.RECYCLE_BIN)
        if df.empty:
            filename = args.file.replace('/', '\\')
            print(f'Unable to parse {filename}.')
            logging.warning(f'Unable to parse {filename}.')
        else:
            output()
        rootDir = args.logs
        if rootDir is None:
            sys.exit()
        if rootDir is not True:
            load_cparser(args.cstructs)
            odl = parse_odl(rootDir)
            if not args.csv:
                args.csv = '.'
            log_output = f'{args.csv}/ODL_logs.csv'
            odl.to_csv(log_output, index=False)

    if args.dir:
        logging.info(f'Searching for OneDrive data in {args.dir}')
        d = {}
        hive = re.compile(r'\\Users\\(?P<user>.*)?')
        dat = re.compile(r'\\Users\\(?P<user>.*)?\\AppData\\Local\\Microsoft\\OneDrive\\settings')
        log_dir = re.compile(r'\\Users\\(?P<user>.*)?\\AppData\\Local\\Microsoft\\OneDrive\\logs$')
        rootDir = args.dir
        spinner = spinning_cursor()
        delay = time.time()
        for path, subdirs, files in os.walk(rootDir):
            if (time.time() - delay) > 0.1:
                sys.stdout.write(f'Searching for OneDrive data {next(spinner)}\r')
                sys.stdout.flush()
                delay = time.time()
            hive_find = re.findall(hive, path)
            dat_find = re.findall(dat, path)
            log_find = re.findall(log_dir, path)
            if path.endswith('$Recycle.Bin'):
                args.RECYCLE_BIN = path

            if hive_find:
                for name in files:
                    if name == 'NTUSER.DAT':
                        logging.info(f'Found {name} for {hive_find[0]}')
                        d.setdefault(hive_find[0], {})
                        d[hive_find[0]].setdefault('hive', os.path.join(path, name))
                        args.reghive = os.path.join(path, name)

            if dat_find:
                for name in files:
                    if '.dat' in name:
                        logging.info(f'Found {name} for {dat_find[0]}')
                        d.setdefault(dat_find[0], {})
                        d[dat_find[0]].setdefault('files', []).append(os.path.join(path, name))

            if log_find:
                d.setdefault(log_find[0], {})
                d[log_find[0]].setdefault('logs', []).append(path)

        for key, value in d.items():
            filenames = []
            for k, v in value.items():
                if k == 'hive':
                    args.reghive = v
                if k == 'files':
                    filenames = v

                if len(filenames) != 0:
                    logging.info(f'Parsing OneDrive data for {key}')
                    print(f'\n\nParsing {key} OneDrive\n')
                    for filename in filenames:
                        account = os.path.dirname(filename.replace('/', '\\')).rsplit('\\', 1)[-1]
                        df, name = parse_dat(filename, args.reghive, args.RECYCLE_BIN, start, account)
                        df, rbin_df = parse_onedrive(df, account, args.reghive, args.RECYCLE_BIN)
                        if df.empty:
                            filename = filename.replace('/', '\\')
                            print(f'Unable to parse {filename}.')
                            logging.warning(f'Unable to parse {filename}.')
                        else:
                            output()

        if args.logs:
            load_cparser(args.cstructs)
            for key, value in d.items():
                for k, v in value.items():
                    if k == 'logs':
                        logging.info(f'Parsing OneDrive logs for {key}')
                        print(f'\n\nParsing {key} OneDrive logs\n')
                        logs = v
                        odl = parse_odl(logs[0], key)
                        log_output = f'{key}_logs.csv'
                        odl.to_csv(log_output, index=False)

    sys.exit()


if __name__ == '__main__':
    main()
