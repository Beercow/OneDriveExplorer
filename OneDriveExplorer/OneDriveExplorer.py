import sys
import re
import io
from collections import namedtuple
import json
import argparse

__author__ = "Brian Maloney"
__version__ = "2022.02.08"
__email__ = "bmmaloney97@gmail.com"

dir_list = []
folder_structure = {}
ASCII_BYTE = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
String = namedtuple("String", ["s", "offset"])


def unicode_strings(buf, n=2):
    reg = rb"((?:[%s]\x00){%d,})" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    return match.group().decode("utf-16")


def folder_search(dict_list, input, duuid, added):
    for k, v in dict_list.items():
        if(isinstance(v, list)):
            for dic in v:
                if duuid == dic['Object_UUID']:
                    dic['Children'].append(input)
                    added = True
                else:
                    r = folder_search(dic, input, duuid, added)
                    added = r
    return added


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def parse_onedrive(usercid, outfile, pretty):
    misfits = []
    with open(usercid, 'rb') as f:
        b = f.read()
    data = io.BytesIO(b)
    if data.read(11)[10] != 1:
        print('Not a valid OneDrive file')
        sys.exit()
    data.seek(-7, 1)
    if data.read(1) == b'\x01':
        uuid4hex = re.compile(b'[A-F0-9]{16}![0-9]*\.')
    else:
        uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
    total = len(b)
    for match in re.finditer(uuid4hex, b):
        s = match.start()
        count = s
        diroffset = s - 40
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8").strip('\u0000')
        if duuid not in dir_list:
            dir_list.append(duuid)
        progress(count, total, status='Building folder list. Please wait....')

    print('\n')

    folder_structure = {'Folder_UUID': '',
                        'Object_UUID': dir_list[0],
                        'Type': 'Folder',
                        'Name': 'Root',
                        'Children': []
                        }

    for match in re.finditer(uuid4hex, b):
        added = False
        s = match.start()
        count = s
        diroffset = s - 40
        objoffset = s - 79
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8").strip('\u0000')
        data.seek(objoffset)
        ouuid = data.read(32).decode("utf-8").strip('\u0000')
        name = unicode_strings(data.read())
        if ouuid in dir_list:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'Folder',
                     'Name': name,
                     'Children': []
                     }
            if duuid == folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                added = folder_search(folder_structure, input, duuid, added)
                if not added:
                    misfits.append(input)
        else:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'File',
                     'Name': name
                     }
            if duuid == folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                added = folder_search(folder_structure, input, duuid, added)
                if not added:
                    misfits.append(input)
        progress(count, total, status='Recreating OneDrive folder. Please wait....')

    print('\n')

    total = len(misfits)
    count = 0
    for i in misfits:
        added = folder_search(folder_structure, i, i['Folder_UUID'], added)
        count += 1
        progress(count, total, status='Adding missing files/folders. Please wait....')

    print('\n')

    if pretty:
        json_object = json.dumps(folder_structure,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(folder_structure)

    output = open(outfile, 'w')
    output.write(json_object)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="<UserCid>.dat file to be parsed")
    parser.add_argument("-o", "--outfile", help="File name to save json representation to. When pressent, overrides default name", default="OneDrive.json")
    parser.add_argument("--pretty", help="When exporting to json, use a more human readable layout. Default is FALSE", action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.file:
        parse_onedrive(args.file, args.outfile, args.pretty)


if __name__ == '__main__':
    main()
