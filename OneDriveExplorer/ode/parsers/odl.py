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
# Based off of Yogesh Khatri, @SwiftForensics https://github.com/ydkhatri/OneDrive/blob/main/odl.py
#

import os
import io
import zlib
import re
import string
import datetime
import base64
import json
from ruamel.yaml import YAML
from cerberus import Validator
import pandas as pd
from ode.utils import progress_gui, progress, schema
from dissect import cstruct
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging
import ctypes
import concurrent.futures
import queue
import threading
import itertools

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

log = logging.getLogger(__name__)

printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')
cparser = ''

# UnObfuscation code
dkey_list = {}
key_type = ''
utf_type = 'utf16'

headers = '''

typedef struct _Odl_header{
    uint64    signature;  // 0x44454e4f47464245 EBFGONED
    uint32    odl_version;
} Odl_header;

typedef struct _Odl_header_V1{
    uint32    unk1;
    uint64    unk2;
    uint32    unk3;
    char      one_drive_version[0x44];
} Odl_header_V1;

typedef struct _Odl_header_V2_3{
    uint32    unk1;
    uint64    unk2;
    uint32    unk3;
    char      one_drive_version[0x40];
    char      windows_version[0x40];
    char      reserved[0x64];
} Odl_header_V2_3;

typedef struct _Data_block_V2{
    uint32     signature;  // CCDDEEFF
    uint16    context_data_len;
    uint16    unknown_flag;
    uint64     timestamp;
    uint32     unk1;
    uint32     unk2;
    uint128    unk3_guid;
    uint32     unk4;
    uint32     unk5;
    uint32     data_len;
    uint32     unk6;
    // followed by Data
} Data_block_V2;

typedef struct _Data_block_V3{
    uint32    signature;  // CCDDEEFF
    uint16    context_data_len;
    uint16    unknown_flag;
    uint64    timestamp;
    uint32    unk1;
    uint32    unk2;
    uint32    data_len;
    uint32    unk3;
    char      context_data[context_data_len];
    // followed by Data
} Data_block_V3;

typedef struct _Data_v2{
    uint32    code_file_name_len;
    char      code_file_name[code_file_name_len];
    uint32    flags;
    uint32    code_function_name_len;
    char      code_function_name[code_function_name_len];
} Data_v2;

typedef struct _Data_v3{
    uint128    unk1_guid;
    uint32     unk2;
    uint32     unk3;
    uint32     code_file_name_len;
    char       code_file_name[code_file_name_len];
    uint32     flags;
    uint32     code_function_name_len;
    char       code_function_name[code_function_name_len];
} Data_v3;

'''


def load_cparser(cstructs_dir=False, clist=False):
    global cparser
    cparser = cstruct.cstruct()
    cparser.load(headers)
    yaml = YAML()
    v = Validator()

    if not cstructs_dir:
        cstructs_dir = f'{os.getcwd()}\\cstructs'

    if not clist:
        log.info(f"Loading ODL cstructs from {cstructs_dir}")

    li = []
    id = []

    try:
        for file in os.listdir(cstructs_dir):
            if file.startswith('!'):
                continue
            try:
                if not file.endswith('cstruct'):
                    continue
                with open(os.path.join(cstructs_dir, file)) as f:
                    data = yaml.load(f.read())
                    if clist:
                        list_cstruct(file, data, v, id)
                    else:
                        if not v.validate(data, schema.cstruct):
                            log.error(f'{file} is not valid. {v.errors}')
                            continue
                        if data['Id'] in id:
                            log.error(f'Id is not unique. {file} will not load.')
                            continue
                        else:
                            id.append(data['Id'])

                        for x in data['Functions']:
                            for flag in x['Flags']:
                                name = f"{data['Code_File'].lower().split('.')[0]}_{flag}_{x['Function'].split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}"
                                cparser.load(x['Structure'] % (name, x['Description'], name))

                        df = pd.json_normalize(data)

                if not clist:
                    li.append(df)

            except Exception as ex:
                log.warning(f'Something went wrong loading {file}: {ex}')
                continue

    except Exception as e:
        log.warning(f'{e}. Not needed but, to map ODL events, sync with GitHub to get cstruct files.')

    if not clist:
        try:
            df = pd.concat(li, ignore_index=True, axis=0)
        except Exception:
            df = pd.DataFrame()
        log.info("Loading ODL cstructs complete.")
        return df


def list_cstruct(file, data, v, id):
    if not v.validate(data, schema.cstruct):
        print(f'\033[1;31m{file} is not valid. {v.errors}\033[1;0m\n')
        return
    if data['Id'] in id:
        print(f'\033[1;31mId is not unique. {file} will not load.\033[1;0m\n')
        return
    else:
        id.append(data['Id'])
    print(f"\033[1;33mODL cstruct: {data['Code_File']}\033[1;0m")
    print(f"\033[1;37m             Description: {data['Description']}\033[1;0m\n")


def ReadUnixMsTime(unix_time_ms):  # Unix millisecond timestamp
    '''Returns datetime object, or empty string upon error'''
    if unix_time_ms not in (0, None, ''):
        try:
            if isinstance(unix_time_ms, str):
                unix_time_ms = float(unix_time_ms)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time_ms/1000)
        except (ValueError, OverflowError, TypeError) as ex:
            log.error(f'ReadUnixMsTime() Failed to convert timestamp from value {unix_time_ms} Error was: {ex}')
            pass
    return ''


def guess_encoding(obfuscation_map_path):
    '''Returns either UTF8 or UTF16LE after checking the file'''
    encoding = 'utf-16le'  # on windows this is the default
    with open(obfuscation_map_path, 'rb') as f:
        data = f.read(4)
        if len(data) == 4:
            if data[1] == 0 and data[3] == 0 and data[0] != 0 and data[2] != 0:
                pass  # confirmed utf-16le
            else:
                encoding = 'utf8'
    return encoding


def decrypt(cipher_text):
    '''cipher_text is expected to be base64 encoded'''
    global dkey_list
    global utf_type

    if not dkey_list:
        return ''
    if len(cipher_text) < 22:
        return ''  # invalid or it was not encrypted!
    # add proper base64 padding
    remainder = len(cipher_text) % 4
    if remainder == 1:
        return ''  # invalid b64 or it was not encrypted!
    elif remainder in (2, 3):
        cipher_text += "=" * (4 - remainder)
    try:
        cipher_text = cipher_text.replace('_', '/').replace('-', '+')
        cipher_text = base64.b64decode(cipher_text)
    except Exception:
        return ''

    if len(cipher_text) % 16 != 0:
        return ''  # invalid b64 or it was not encrypted!

    for key, values in dkey_list.items():
        global key_type
        key_type = key
        for value in values:
            try:
                cipher = AES.new(value, AES.MODE_CBC, iv=b'\0'*16)
                raw = cipher.decrypt(cipher_text)
            except ValueError as ex:
                # log.error(f'Exception while decrypting data {str(ex)}')
                return ''
            try:
                plain_text = unpad(raw, 16)
            except Exception as ex:  # possible fix to change value
                # print("Error in unpad!", str(ex), raw)
                continue
            try:
                plain_text = plain_text.decode(utf_type)
            except ValueError as ex:
                # print(f"Error decoding {utf_type}", str(ex))
                return ''
            return plain_text


def read_keystore(keystore_path):
    global dkey_list
    global utf_type
    encoding = guess_encoding(keystore_path)
    with open(keystore_path, 'r', encoding=encoding) as f:
        try:
            j = json.load(f)
            dkey = j[0]['Key']
            version = j[0]['Version']
            utf_type = 'utf32' if dkey.endswith('\\u0000\\u0000') else 'utf16'
            log.info(f"Recovered Unobfuscation key from {f.name}, key:{dkey}, version:{version}, utf_type:{utf_type}")
            if not any(base64.b64decode(dkey) in values for values in dkey_list.values()):
                dkey_list.setdefault(os.path.basename(f.name).split('.')[0], []).append(base64.b64decode(dkey))
            if version != 1:
                log.warning(f'WARNING: Key version {version} is unsupported. This may not work. Contact the author if you see this to add support for this version.')
        except ValueError as ex:
            log.error("JSON error " + str(ex))


def read_obfuscation_map(obfuscation_map_path, map):
    if map is None:
        map = {}

    repeated_items_found = False
    encoding = guess_encoding(obfuscation_map_path)
    with open(obfuscation_map_path, 'r', encoding=encoding) as f:
        log.info(f"Building map from {f.name}")
        for line in f.readlines():
            line = line.rstrip('\n')
            terms = line.split('\t')
            if len(terms) == 2:
                if terms[0] in map:  # REPEATED item found!
                    pass
                else:
                    map[terms[0]] = terms[1]
                    last_key = terms[0]
                    last_val = terms[1]
            else:
                last_val += '\n' + line
                map[last_key] = last_val

    if repeated_items_found:
        log.warning('WARNING: Multiple instances of some keys were found in the ObfuscationMap.')
    return map


def tokenized_replace(string, map):
    output = ''
    tokens = ':\\.@%#&*|{}!?<>;:~()//"\''
    parts = []  # [ ('word', 1), (':', 0), ..] word=1, token=0
    last_word = ''
    last_token = ''
    for i, char in enumerate(string):
        if char in tokens:
            if last_word:
                parts.append((last_word, 1))
                last_word = ''
            if last_token:
                last_token += char
            else:
                last_token = char
        else:
            if last_token:
                parts.append((last_token, 0))
                last_token = ''
            if last_word:
                last_word += char
            else:
                last_word = char
    if last_token:
        parts.append((last_token, 0))
    if last_word:
        parts.append((last_word, 1))

    # now join all parts replacing the words
    for part in parts:
        if part[1] == 0:  # token
            output += part[0]
        else:  # word
            word = part[0]
            decrypted_word = decrypt(word)
            if decrypted_word:
                output += decrypted_word
            elif word in map:
                output += map[word]
            else:
                output += word
    return output


def extract_strings(data, map):
    extracted = []
    # for match in not_control_char_re.finditer(data): # This gets all unicode chars, can include lot of garbage if you only care about English, will miss out other languages
    for match in ascii_chars_re.finditer(data):  # Matches ONLY Ascii (old behavior) , good if you only care about English
        x = match.group().rstrip('\n').rstrip('\r')
        x.replace('\r', '').replace('\n', ' ')
        x = tokenized_replace(x, map)
        extracted.append(x)

    if len(extracted) == 0:
        extracted = ''
    elif len(extracted) == 1:
        extracted = extracted[0]
    return extracted


def extract_context_data(data):
    hex_str = data.hex()
    index = 0
    extracted_text = ''

    length_hex = hex_str[2:6]
    length_hex = length_hex[2:4] + length_hex[0:2]
    length = int(length_hex, 16)
    index += 6

    extracted_text += f"{bytes.fromhex(hex_str[index:index + length * 2]).decode('utf-8', errors='ignore')}"
    index += length * 2

    while index < len(hex_str):
        segment_length_hex = hex_str[index:index + 2]
        segment_length = int(segment_length_hex, 16)
        index += 4

        text_segment = bytes.fromhex(hex_str[index:index + segment_length * 2]).decode('utf-8', errors='ignore')
        extracted_text += f' {text_segment}'
        index += segment_length * 2

    return extracted_text


def unobfucate_strings(data, map):
    params = []
    exclude = ['_len', 'unk']

    for key, value in data._values.items():
        if any(x in key for x in exclude):
            continue
        if isinstance(value, bytes):
            value = value.decode('utf8', 'ignore')
            value = tokenized_replace(value, map)
        params.append(f'{key}={str(value)}')

    return params


def process_odl(filename, map):
    global key_type
    odl_rows = []
    basename = os.path.basename(filename)
    profile = os.path.dirname(filename).split('\\')[-1]

    try:
        f = open(filename, 'rb')
    except Exception as e:
        log.error(e)
        return pd.DataFrame()
    with f:
        i = 1
        try:
            header = cparser.Odl_header(f.read(12))
            if header.odl_version == 1:
                header_con = cparser.Odl_header_V1(f.read(84))
                header_con._values.update([('windows_version', b'')])
            else:
                header_con = cparser.Odl_header_V2_3(f.read(244))
        except Exception:
            log.warning(f'Unable to parse {basename}. Not a valid log file.')
            return pd.DataFrame()

        if header.signature == 0x44454e4f47464245:  # Odl header EBFGONED
            pass
        else:
            log.error(f'{basename} wrong header! Did not find EBFGONED')
            return pd.DataFrame()
        signature = f.read(8)
        # Now either we have the gzip header here or the CDEF header (compressed or uncompressed handles both)
        if signature[0:4] == b'\x1F\x8B\x08\x00':  # gzip
            try:
                f.seek(-8, 1)
                all_data = f.read()
                z = zlib.decompressobj(31)
                file_data = z.decompress(all_data)
            except (zlib.error, OSError) as ex:
                log.error(f'..decompression error for file {basename}. {ex}')
                return pd.DataFrame()
            f.close()
            f = io.BytesIO(file_data)
            signature = f.read(8)
        if signature[0:4] != b'\xCC\xDD\xEE\xFF':  # CDEF header
            log.error(f'{basename} wrong header! Did not find 0xCCDDEEFF')
            return pd.DataFrame()
        else:
            context_data_len = int.from_bytes(signature[4:6], byteorder='little')
            f.seek(-8, 1)
            if header.odl_version == 3:
                db_size = 32
                first_db_size = 32 + context_data_len
            else:
                db_size = 56
                first_db_size = 56
            data_block = f.read(first_db_size)  # odl complete header is 56 bytes
        while data_block:
            description = ''
            odl = {
                'Profile': profile,
                'Key_Type': key_type,
                'Log_Type': basename.split('-')[0],
                'Filename': basename,
                'File_Index': i,
                'Timestamp': None,
                'One_Drive_Version': header_con.one_drive_version.decode('utf8').split('\x00', 1)[0],
                'OS_Version': header_con.windows_version.decode('utf8').split('\x00', 1)[0],
                'Code_File': '',
                'Flags': '',
                'Function': '',
                'Context_Data': '',
                'Description': '',
                'Params': '',
                'Param1': '',
                'Param2': '',
                'Param3': '',
                'Param4': '',
                'Param5': '',
                'Param6': '',
                'Param7': '',
                'Param8': '',
                'Param9': '',
                'Param10': '',
                'Param11': '',
                'Param12': '',
                'Param13': ''
            }

            if header.odl_version in [1, 2]:
                data_block = cparser.Data_block_V2(data_block)
            elif header.odl_version == 3:
                data_block = cparser.Data_block_V3(data_block)
            else:
                log.error(f'Unknown odl_version = {header.odl_version}')

            if data_block.signature != 0xffeeddcc:
                log.warning(f'Unable to parse {basename} completely. Did not find 0xCCDDEEFF')
                return pd.DataFrame.from_records(odl_rows)

            timestamp = ReadUnixMsTime(data_block.timestamp)
            odl['Timestamp'] = timestamp

            try:
                if header.odl_version == 3:
                    if data_block.context_data_len > 0:
                        data = cparser.Data_v2(f.read(data_block.data_len - data_block.context_data_len))
                        params_len = (data_block.data_len - data_block.context_data_len - data.code_file_name_len - data.code_function_name_len - 12)
                    else:
                        data = cparser.Data_v3(f.read(data_block.data_len))
                        params_len = (data_block.data_len - data.code_file_name_len - data.code_function_name_len - 36)
                else:
                    data = cparser.Data_v2(f.read(data_block.data_len))
                    params_len = (data_block.data_len - data.code_file_name_len - data.code_function_name_len - 12)
                f.seek(- params_len, 1)
            except Exception as e:
                log.warning(f'Unable to parse {basename} completely. {type(e).__name__}')
                return pd.DataFrame.from_records(odl_rows)

            if params_len:
                try:
                    structure = getattr(cparser, f"{data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.flags}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                    try:
                        params = structure(f.read(params_len))
                        if len(params) == 0:
                            f.seek(- params_len, 1)
                            params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map)
                        else:
                            params = unobfucate_strings(params, map)
                            try:
                                odl['Param1'] = params[0]
                                odl['Param2'] = params[1]
                                odl['Param3'] = params[2]
                                odl['Param4'] = params[3]
                                odl['Param5'] = params[4]
                                odl['Param6'] = params[5]
                                odl['Param7'] = params[6]
                                odl['Param8'] = params[7]
                                odl['Param9'] = params[8]
                                odl['Param10'] = params[9]
                                odl['Param11'] = params[10]
                                odl['Param12'] = params[11]
                                odl['Param13'] = params[12]
                            except Exception:
                                pass

                            params = ', '.join(params)

                        description = ''.join([v for (k, v) in cparser.consts.items() if k == f"{data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.flags}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}_des"])
                    except EOFError:
                        log.warning(f"EOFError while parsing {data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.flags}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                        f.seek(- params_len, 1)
                        params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map)
                except AttributeError:
                    params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map)

            else:
                params = ''

            odl['Key_Type'] = key_type
            odl['Code_File'] = data.code_file_name.decode('utf8')
            odl['Flags'] = data.flags
            odl['Function'] = data.code_function_name.decode('utf8')
            if hasattr(data_block, 'context_data') and data_block.context_data:
                odl['Context_Data'] = extract_context_data(data_block.context_data)
            odl['Description'] = description
            odl['Params'] = params
            odl_rows.append(odl)

            key_type = ''
            i += 1
            eof = f.read(8)[4:6]

            if eof == b'':
                break

            context_data_len = int.from_bytes(eof, byteorder='little')
            f.seek(-8, 1)
            data_block = f.read(db_size + context_data_len)

    f.close()
    return pd.DataFrame.from_records(odl_rows)


def progress_bar(q, total, pb, value_label, key, gui=False):
    while True:
        count = q.get()
        if count is None:
            break
        if gui:
            progress_gui(total, count, pb, value_label, status=f'Parsing log files for {key}. Please wait....')
        else:
            progress(count, total, status=f'Parsing log files for {key}. Please wait....')
        q.task_done()


def parse_odl(rootDir, key='', pb=False, value_label=False, gui=False):
    filenames = []
    obfuscation_maps = []
    map = {}
    q = queue.Queue()

    df = pd.DataFrame()

    for path, subdirs, files in os.walk(rootDir):
        filematch = ([os.path.join(path, file) for file in files if file.endswith(('.odl', '.odlgz', '.odlsent', '.aodl'))])
        obfuscation_map = ([os.path.join(path, file) for file in files if file == "ObfuscationStringMap.txt"])
        keystore_file = (os.path.join(path, file) for file in files if "general.keystore" in file or "vault.keystore" in file)

        if filematch:
            filenames += filematch
        if obfuscation_map:
            obfuscation_maps += obfuscation_map
        if keystore_file:
            for keystore in keystore_file:
                read_keystore(keystore)

    if obfuscation_maps:
        for obfuscation_map_file in obfuscation_maps:
            map = read_obfuscation_map(obfuscation_map_file, map)

    total = len(filenames)
    if total == 0:
        return df

    results = []
    counter = itertools.count(1)

    def worker(filename):
        log_df = process_odl(filename, map)
        count = next(counter)
        q.put(count)
        return log_df

    if gui:
        pb.configure(mode='determinate')

    t = threading.Thread(target=progress_bar, args=(q, total, pb, value_label, key, gui,))
    t.start()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(worker, filenames))

    df = pd.concat(results, ignore_index=True, axis=0)
    q.put(None)
    t.join()
    return df
