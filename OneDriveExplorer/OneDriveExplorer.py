import os
import sys
import re
from collections import namedtuple
import json
import argparse
import pandas as pd
import time


__author__ = "Brian Maloney"
__version__ = "2022.02.16"
__email__ = "bmmaloney97@gmail.com"

ASCII_BYTE = rb" !#\$%&\'\(\)\+,-\.0123456789;=@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\}\~\t"
String = namedtuple("String", ["s", "offset"])


def unicode_strings(buf, n=1):
    reg = rb"((?:[%s]\x00){%d,}\x00\x00\xab)" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    if match:
        return match.group()[:-3].decode("utf-16")
    return 'null'


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def parse_onedrive(usercid, outfile, pretty, start):
    with open(usercid, 'rb') as f:
        total = len(f.read())
        f.seek(0)
        uuid4hex = re.compile(b'[A-F0-9]{16}![0-9]*\.')
        personal = uuid4hex.search(f.read())
        if not personal:
            uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
        f.seek(0)
        df = pd.DataFrame(columns=['ParentId',
                                   'DriveItemId',
                                   'Type',
                                   'Name',
                                   'Children'])
        dir_index = []
        for match in re.finditer(uuid4hex, f.read()):
            s = match.start()
            count = s
            diroffset = s - 40
            objoffset = s - 79
            f.seek(diroffset)
            duuid = f.read(32).decode("utf-8").strip('\u0000')
            f.seek(objoffset)
            ouuid = f.read(32).decode("utf-8").strip('\u0000')
            name = unicode_strings(f.read(400))
            if not dir_index:
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'Type': 'Root',
                         'Name': f.name,
                         'Children': []
                         }
            else:
                input = {'ParentId': duuid,
                         'DriveItemId': ouuid,
                         'Type': 'File',
                         'Name': name,
                         'Children': []
                         }

            dir_index.append(input)
            progress(count, total, status='Building folder list. Please wait....')

    print('\n')

    df = pd.DataFrame.from_records(dir_index)
    df.loc[df.DriveItemId.isin(df.ParentId), 'Type'] = 'Folder'
    df.at[0, 'Type'] = 'Root'
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    def find_parent(x):
        value = parent_dict.get(x, None)
        if value is None:
            return ""
        else:
            # Incase there is a id without name.
            if id_name_dict.get(value, None) is None:
                return "" + find_parent(value)

            return str(id_name_dict.get(value)) +", "+ find_parent(value)

    df['Level'] = df.DriveItemId.apply(lambda x: len(find_parent(x).rstrip(', ').split()))
    object_count = len(df.index)
    depth = df.Level.max()

    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}
    cache = {}

    for row in df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[False, False, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'Type', 'Name', 'Children'))
        if row['Type'] == 'File':
            folder = cache.setdefault(row['ParentId'], {})
            folder.setdefault('Children', []).append(file)
        else:
            folder = cache.get(row['DriveItemId'], {})
            temp = {**file, **folder}
            folder_merge = cache.setdefault(row['ParentId'], {})
            if row['Type'] == 'Root':
                cache = temp
            else:
                folder_merge.setdefault('Children', []).append(temp)

    if pretty:
        json_object = json.dumps(cache,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(cache)

    if not outfile:
        outfile = os.path.basename(f.name).split('.')[0]+"_OneDrive.json"
        file_extension = os.path.splitext(f.name)[1][1:]
        if file_extension == 'previous':
            outfile = os.path.basename(f.name).split('.')[0]+"_"+file_extension+"_OneDrive.json"
    output = open(outfile, 'w')
    output.write(json_object)
    print(f'{object_count} entries(s), {depth} folders in {format((time.time() - start), ".4f")} seconds')
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
    parser.add_argument("-o", "--outfile", help="File name to save json representation to. When pressent, overrides default name")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.file:
        parse_onedrive(args.file, args.outfile, args.pretty, start)


if __name__ == '__main__':
    main()
