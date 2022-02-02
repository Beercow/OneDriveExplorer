import sys
import re
import io
from collections import namedtuple, OrderedDict
import json
import time

ASCII_BYTE = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
String = namedtuple("String", ["s", "offset"])
uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)


def unicode_strings(buf, n=4):
    reg = rb"((?:[%s]\x00){%d,})" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    return match.group().decode("utf-16")


def folder_search(dict_list, input, duuid):
    for k, v in dict_list.items():
        if(isinstance(v, list)):
            for dic in v:
                if duuid in dic['Object_UUID']:
                    dic['Children'].append(input)
                else:
                    folder_search(dic, input, duuid)


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


dir_list = []
folder_structure = OrderedDict()


def main():
    start = time.time()
    with open(sys.argv[1], 'rb') as f:
        b = f.read()
    data = io.BytesIO(b)
    total = len(b)
    for match in re.finditer(uuid4hex, b):
        s = match.start()
        count = s
        diroffset = s - 40
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8")
        if duuid not in dir_list:
            dir_list.append(duuid)
        progress(count, total, status='Building folder list. Pleas wait....')

    folder_structure = {'Folder_UUID': '',
                        'Object_UUID': dir_list[0],
                        'Type': 'Folder',
                        'Name': 'Root',
                        'Children': []
                        }

    for match in re.finditer(uuid4hex, b):
        s = match.start()
        count = s
        diroffset = s - 40
        objoffset = s - 79
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8")
        data.seek(objoffset)
        ouuid = data.read(32).decode("utf-8")
        name = unicode_strings(data.read())
        if ouuid in dir_list:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'Folder',
                     'Name': name,
                     'Children': []
                     }
            if duuid in folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                folder_search(folder_structure, input, duuid)
        else:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'File',
                     'Name': name
                     }
            if duuid in folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                folder_search(folder_structure, input, duuid)
        progress(count, total, status='Recreating OneDrive folder. Pleas wait....')

    json_object = json.dumps(folder_structure,
                             sort_keys=False,
                             indent=4,
                             separators=(',', ': ')
                             )
    print(json_object)
    print(f'\033[1;37mProcessed file in {format((time.time() - start), ".4f")} seconds \033[1;0m')
    sys.exit()

if __name__ == '__main__':
    main()
