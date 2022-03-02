import os
import sys
import re
from collections import namedtuple
import json
import argparse
import pandas as pd
import time
from Registry import Registry


__author__ = "Brian Maloney"
__version__ = "2022.03.02"
__email__ = "bmmaloney97@gmail.com"

ASCII_BYTE = rb" !#\$%&\'\(\)\+,-\.0123456789;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\}\~\t"
String = namedtuple("String", ["s", "offset"])


def unicode_strings(buf, n=1):
    reg = rb"((?:[%s]\x00){%d,}\x00\x00\xab)" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    if match:
        return match.group()[:-3].decode("utf-16"), match.start()
    return 'null'


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def print_json(df, name, pretty, json_path):
    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}
    cache = {}
    final = []

    for row in df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[False, False, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Name', 'Size', 'Children'))
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
             'Name': name,
             'Size': '',
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
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\'))
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
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\'))
    html_file = os.path.basename(name).split('.')[0]+"_OneDrive.html"
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        html_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.html"

    output = open(html_path + '/' + html_file, 'w')
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

    return find_parent(value, id_name_dict, parent_dict) +"\\\\"+ str(id_name_dict.get(value))


def parse_onedrive(usercid, reghive, json_path, csv_path, csv_name, pretty, html_path, start):
    with open(usercid, 'rb') as f:
        total = len(f.read())
        f.seek(0)
        uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
        personal = uuid4hex.search(f.read())
        if not personal:
            uuid4hex = re.compile(b'"({[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}},[0-9]*)"', re.I)
        f.seek(0)
        df = pd.DataFrame(columns=['ParentId',
                                   'DriveItemId',
                                   'eTag',
                                   'Type',
                                   'Name',
                                   'Size',
                                   'Children'])
        dir_index = []
        for match in re.finditer(uuid4hex, f.read()):
            s = match.start()
            eTag = match.group(1).decode("utf-8")
            count = s
            diroffset = s - 39
            objoffset = s - 78
            f.seek(objoffset)
            ouuid = f.read(32).decode("utf-8").strip('\u0000')
            f.seek(diroffset)
            duuid = f.read(32).decode("utf-8").strip('\u0000')
            name, name_s = unicode_strings(f.read(400))
            sizeoffset = diroffset + 24 + name_s
            f.seek(sizeoffset)
            size = int.from_bytes(f.read(8), "little")
            if not dir_index:
                if reghive and personal:
                    try:
                        reg_handle = Registry.Registry(reghive)
                        int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive\Personal')
                        for providers in int_keys.values():
                            if providers.name() == 'MountPoint':
                                mountpoint = providers.value()
                    except:
                        mountpoint = 'User Folder'
                else:
                    mountpoint = 'User Folder'
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'eTag': eTag,
                         'Type': 'Root Default',
                         'Name': mountpoint,
                         'Size': '',
                         'Children': []
                         }
                dir_index.append(input)
            input = {'ParentId': duuid,
                     'DriveItemId': ouuid,
                     'eTag': eTag,
                     'Type': 'File',
                     'Name': name,
                     'Size': size,
                     'Children': []
                     }

            dir_index.append(input)
            progress(count, total, status='Building folder list. Please wait....')

    print('\n')

    df = pd.DataFrame.from_records(dir_index)
    df.loc[(df.DriveItemId.isin(df.ParentId)) | (df.Size == 2880154368), ['Type', 'Size']] = ['Folder', '']
    df.at[0, 'Type'] = 'Root Default'
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Level'] = df.DriveItemId.apply(lambda x: len(find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\')))

    share_df = df.loc[(df.Level == 1) & (~df.ParentId.isin(df.DriveItemId)) & (df.Type != 'Root Default')]
    share_list = list(set(share_df.ParentId))
    share_root = []

    for x in share_list:
        input = {'ParentId': '',
                 'DriveItemId': x,
                 'eTag': '',
                 'Type': 'Root Shared',
                 'Name': 'Shared with user',
                 'Size': '',
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
        except:
            pass

    if csv_path:
        print_csv(df, f.name, csv_path, csv_name)
    if html_path:
        print_html(df, f.name, html_path)
    if ((csv_path or html_path) and json_path) or (not csv_path and not html_path):
        print_json(df, f.name, pretty, json_path)
    try:
        file_count = df.Type.value_counts()['File']
    except KeyError:
        file_count = 0
    try:
        folder_count = df.Type.value_counts()['Folder']
    except KeyError:
        folder_count = 0

    print(f'{file_count} files(s), {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds')
    sys.exit()


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
    parser.add_argument("-r", "--REG_HIVE", dest="reghive", help="If a registry hive is provided then the mount points of the SyncEngines will be resolved.")
    parser.add_argument("--csv", help="Directory to save CSV formatted results to. Be sure to include the full path in double quotes")
    parser.add_argument("--csvf", help="File name to save CSV formatted results to. When present, overrides default name")
    parser.add_argument("--html", help="Directory to save xhtml formatted results to. Be sure to include the full path in double quotes")
    parser.add_argument("--json", help="Directory to save json representation to. Use --pretty for a more human readable layout")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

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


if __name__ == '__main__':
    main()
