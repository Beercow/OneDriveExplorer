import os
import sys
import re
import codecs
import json
import argparse
import pandas as pd
import time
import logging
from Registry import Registry

logging.basicConfig(level=logging.INFO,
                    format='\n\n%(asctime)s, %(levelname)s, %(message)s\n',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )

__author__ = "Brian Maloney"
__version__ = "2022.04.06"
__email__ = "bmmaloney97@gmail.com"


def unicode_strings(buf, ouuid):
    uni_re = re.compile("(?:["
                        "\w"
                        "\s"
                        u"\u0020-\u007f"
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U00002500-\U00002BEF"  # chinese char
                        u"\U00002702-\U000027B0"
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        u"\U0001f926-\U0001f937"
                        u"\U00010000-\U0010ffff"
                        u"\u2640-\u2642"
                        u"\u2600-\u2B55"
                        u"\u200d"
                        u"\u23cf"
                        u"\u23e9"
                        u"\u231a"
                        u"\ufe0f"  # dingbats
                        u"\u3030"
                        "]{1,}\x00\uabab)", flags=re.UNICODE)
    match = uni_re.search(buf.decode("utf-16", errors='ignore'))
    if match:
        try:
            return match.group()[:-2]
        except Exception as e:
            logging.warning(e)
    logging.error(f'An error occured trying to find the name of {ouuid}. Raw Data:{buf}')
    return '??????????'


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


def print_json(df, name, pretty, json_path):
    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}
    cache = {}
    final = []

    df.loc[df.Type == 'File', ['FileSort']] = df['Name'].str.lower()
    df.loc[df.Type == 'Folder', ['FolderSort']] = df['Name'].str.lower()

    for row in df.sort_values(by=['Level', 'ParentId', 'Type', 'FileSort', 'FolderSort'], ascending=[False, False, False, True, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'Children'))
        if row['Type'] == 'File':
            folder = cache.setdefault(row['ParentId'], {})
            folder.setdefault('Children', []).append(file)
        else:
            folder = cache.get(row['DriveItemId'], {})
            temp = {**file, **folder}
            folder_merge = cache.setdefault(row['ParentId'], {})
            if 'Root' in row['Type']:
                final.insert(0, temp)
            else:
                folder_merge.setdefault('Children', []).append(temp)

    cache = {'ParentId': '',
             'DriveItemId': '',
             'eTag': '',
             'Type': 'Root Drive',
             'Path': '',
             'Name': name,
             'Size': '',
             'Hash': '',
             'Children': ''
             }

    cache['Children'] = final

    if pretty:
        json_object = json.dumps(cache,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(cache)

    json_file = os.path.basename(name).split('.')[0]+"_OneDrive.json"
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        json_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.json"
    if json_path:
        json_file = json_path + '/' + json_file

    output = open(json_file, 'w')
    output.write(json_object)
    output.close()


def print_csv(df, name, csv_path, csv_name):
    df = df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[True, False, False])
    df = df.drop(['Children', 'Level'], axis=1)

    csv_file = os.path.basename(name).split('.')[0]+"_OneDrive.csv"
    if csv_name:
        csv_file = csv_name
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous' and not csv_name:
        csv_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.csv"
    df.to_csv(csv_path + '/' + csv_file, index=False)


def print_html(df, name, html_path):
    df = df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[True, False, False])
    df = df.drop(['Children', 'Level'], axis=1)

    html_file = os.path.basename(name).split('.')[0]+"_OneDrive.html"
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        html_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.html"

    output = open(html_path + '/' + html_file, 'w', encoding='utf-8')
    output.write(df.to_html(index=False))
    output.close()


def find_parent(x, id_name_dict, parent_dict):
    value = parent_dict.get(x, None)
    if value is None:
        return x
    else:
        # Incase there is a id without name.
        if id_name_dict.get(value, None) is None:
            return find_parent(value, id_name_dict, parent_dict) + x

    return find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))


def parse_onedrive(usercid, reghive, json_path, csv_path, csv_name, pretty, html_path, start):
    logging.info(f'Start parsing {usercid}. Registry hive: {reghive}')
    ff = re.compile(b'([\x01|\x02|\x09]\xab\xab\xab\xab\xab\xab\xab)') # \x01 = file, \x02 = folder, \x09 = share

    with open(usercid, 'rb') as f:
        total = len(f.read())
        f.seek(0)
        uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
        personal = uuid4hex.search(f.read())
        f.seek(0)
        df = pd.DataFrame(columns=['ParentId',
                                   'DriveItemId',
                                   'eTag',
                                   'Type',
                                   'Name',
                                   'Size',
                                   'Hash',
                                   'Children'])
        dir_index = []
        entries = re.finditer(ff, f.read())
        current = next(entries, total)
        while isinstance(current, re.Match):
            s = current.start()
            count = s
            n_current = next(entries, total)
            hash = ''
            size = ''
            f.seek(s)
            if b'\x09' in current[0]:
                f.seek(s + 16)
                check = f.read(8)
                if check == b'\x01\x00\x00\x00\x00\x00\x00\x00':
                    duuid = f.read(39).decode("utf-8")
                    ouuid = ''
                    eTag = ''
                else:
                    current = n_current
                    continue
            else:
                if b'\x01' in current[0]:
                    type = 'File'
                else:
                    type = 'Folder'
                f.seek(s + 16)
                check = f.read(8)
                if check == b'\x01\x00\x00\x00\x00\x00\x00\x00':
                    ouuid = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    duuid = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    eTag = f.read(56).decode("utf-8").split('\u0000\u0000', 1)[0]
                    f.seek(26, 1)
                    if type == 'File':
                        if personal:
                            hash = f'SHA1({f.read(20).hex()})'
                        else:
                            hash = f'quickXor({codecs.encode(f.read(20), "base64").decode("utf-8").rstrip()})'
                        f.seek(12, 1)
                        size = int.from_bytes(f.read(8), "little")
                    try:
                        buffer = n_current.start() - f.tell()
                    except AttributeError:
                        buffer = n_current - f.tell()
                    name = unicode_strings(f.read(buffer), ouuid)
                else:
                    current = n_current
                    continue
            if not dir_index:
                if reghive and personal:
                    try:
                        reg_handle = Registry.Registry(reghive)
                        int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive\Personal')
                        for providers in int_keys.values():
                            if providers.name() == 'MountPoint':
                                mountpoint = providers.value()
                    except Exception as e:
                        logging.warning(f'Unable to read registry hive! {e}')
                        mountpoint = 'User Folder'
                else:
                    mountpoint = 'User Folder'
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'eTag': eTag,
                         'Type': 'Root Default',
                         'Name': mountpoint,
                         'Size': '',
                         'Hash': '',
                         'Children': []
                         }
                dir_index.append(input)
            input = {'ParentId': duuid,
                     'DriveItemId': ouuid,
                     'eTag': eTag,
                     'Type': type,
                     'Name': name,
                     'Size': size,
                     'Hash': hash,
                     'Children': []
                     }

            dir_index.append(input)
            progress(count, total, status='Building folder list. Please wait....')
            current = n_current

    print('\n')

    df = pd.DataFrame.from_records(dir_index)

    share_df = df.loc[(~df.ParentId.isin(df.DriveItemId)) & (df.Type != 'Root Default')]
    share_list = list(set(share_df.ParentId))
    share_root = []

    for x in share_list:
        input = {'ParentId': '',
                 'DriveItemId': x,
                 'eTag': '',
                 'Type': 'Root Shared',
                 'Name': 'Shared with user',
                 'Size': '',
                 'Hash': '',
                 'Children': [],
                 'Level': 1
                 }
        share_root.append(input)
    share_df = pd.DataFrame.from_records(share_root)
    df = pd.concat([df, share_df], ignore_index=True, axis=0)

    if reghive:
        try:
            reg_handle = Registry.Registry(reghive)
            int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive')
            for providers in int_keys.subkeys():
                df.loc[(df.DriveItemId == providers.name().split('+')[0]), ['Name']] = [x.value() for x in list(providers.values()) if x.name() =='MountPoint'][0]
        except Exception as e:
            logging.warning(f'Unable to read registry hive! {e}')
            pass

    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))
    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
    df['Level'] = df['Path'].str.len()
    df['Path'] = df['Path'].str.join('\\')

    if csv_path:
        print_csv(df, f.name, csv_path, csv_name)
    if html_path:
        print_html(df, f.name, html_path)
    if ((csv_path or html_path) and json_path) or (not csv_path and not html_path):
        print_json(df, f.name, pretty, json_path)
    try:
        file_count = df.Type.value_counts()['File']
    except KeyError:
        logging.warning("KeyError: 'File'")
        file_count = 0
    try:
        folder_count = df.Type.value_counts()['Folder']
    except KeyError:
        logging.warning("KeyError: 'Folder'")
        folder_count = 0

    print(f'{file_count} files(s), {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds')


def main():
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
    parser.add_argument("-d", "--dir", help="Directory to recursively process, looking for <UserCid>.dat and NTUSER hive. This mode is primarily used with KAPE so both <UserCid>.dat and NTUSER hive can be located")
    parser.add_argument("-r", "--REG_HIVE", dest="reghive", help="If a registry hive is provided then the mount points of the SyncEngines will be resolved.")
    parser.add_argument("--csv", help="Directory to save CSV formatted results to. Be sure to include the full path in double quotes")
    parser.add_argument("--csvf", help="File name to save CSV formatted results to. When present, overrides default name")
    parser.add_argument("--html", help="Directory to save xhtml formatted results to. Be sure to include the full path in double quotes")
    parser.add_argument("--json", help="Directory to save json representation to. Use --pretty for a more human readable layout")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')
    parser.add_argument("--debug", help="Show debug information during processing", action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        print('\nEither -f or -d is required. Exiting')
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
        parse_onedrive(args.file, args.reghive, args.json, args.csv, args.csvf, args.pretty, args.html, start)
        sys.exit()

    if args.dir:
        logging.info(f'Searching for OneDrive data in {args.dir}')
        d = {}
        hive = re.compile(r'\\Users\\(?P<user>.*)?')
        dat = re.compile(r'\\Users\\(?P<user>.*)?\\AppData\\Local\\Microsoft\\OneDrive\\settings')
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
                        parse_onedrive(filename, args.reghive, args.json, args.csv, args.csvf, args.pretty, args.html, start)
        sys.exit()


if __name__ == '__main__':
    main()
