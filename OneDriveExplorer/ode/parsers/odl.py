# OneDriveExplorer
# Copyright (C) 2022
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
import gzip
import re
import string
import datetime
import base64
import json
import pandas as pd
from ode.utils import progress_gui, progress
from dissect import cstruct
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging

log = logging.getLogger(__name__)

printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')
cparser = ''

# UnObfuscation code
dkey_dict = {}
utf_type = 'utf16'

headers = '''

typedef struct _Odl_header{
    char    signature[8];  // EBFGONED
    uint32    unk_version;
    uint32    unk1;
    uint64    unk2;
    uint32    unk3;
    char      one_drive_version[0x40];
    char      windows_version[0x40];
    char      reserved[0x64];
} Odl_header;

typedef struct _Data_block{
    uint64    signature;  // CCDDEEFF00000000
    uint64    timestamp;
    uint32    unk1;
    uint32    unk2;
    char      unk3_guid[16];
    uint32    unk4;
    uint32    unk5;
    uint32    data_len;
    uint32    unk6;
} Data_block;

typedef struct _Data{
    uint32    code_file_name_len;
    char      code_file_name[code_file_name_len];
    uint32    unknown;
    uint32    code_function_name_len;
    char      code_function_name[code_function_name_len];
} Data;

'''


def load_cparser():
    global cparser
    cparser = cstruct.cstruct()
    cparser.load(headers)

    try:
        for file in os.listdir(f'{os.getcwd()}/cstructs'):
            if file.startswith('!'):
                continue
            try:
                cparser.loadfile(os.path.join(f'{os.getcwd()}/cstructs', file))
            except Exception as ex:
                log.warning(f'Something went wrong loading {file}: {ex}')
                continue
    except Exception as ex:
        log.warning(ex)


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


def decrypt(cipher_text, dkey):
    '''cipher_text is expected to be base64 encoded'''
    global dkey_dict
    global utf_type

    if not dkey_dict:
        return ""
    if len(cipher_text) < 22:
        return ""  # invalid
    # add proper base64 padding
    remainder = len(cipher_text) % 4
    if remainder == 1:
        return ""  # invalid b64
    elif remainder in (2, 3):
        cipher_text += "=" * (4 - remainder)
    try:
        cipher_text = cipher_text.replace('_', '/').replace('-', '+')
        cipher_text = base64.b64decode(cipher_text)
    except Exception:
        return ""

    if len(cipher_text) % 16 != 0:
        return ""
    else:
        pass

    try:
        cipher = AES.new(dkey, AES.MODE_CBC, iv=b'\0'*16)
        raw = cipher.decrypt(cipher_text)
    except ValueError:
        return ""
    try:
        plain_text = unpad(raw, 16)
    except Exception:
        return ""
    try:
        plain_text = plain_text.decode(utf_type)  # , 'ignore')
    except ValueError:
        return ""
    return plain_text


def read_keystore(keystore_path):
    global dkey_dict
    global utf_type
    encoding = guess_encoding(keystore_path)
    with open(keystore_path, 'r', encoding=encoding) as f:
        try:
            j = json.load(f)
            dkey = j[0]['Key']
            version = j[0]['Version']
            utf_type = 'utf32' if dkey.endswith('\\u0000\\u0000') else 'utf16'
            log.info(f"Recovered Unobfuscation key {dkey}, version={version}, utf_type={utf_type}")
            dkey_dict[os.path.dirname(keystore_path)] = base64.b64decode(dkey)
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


def tokenized_replace(string, map, dkey):
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
            decrypted_word = decrypt(word, dkey)
            if decrypted_word:
                output += decrypted_word
            elif word in map:
                output += map[word]
            else:
                output += word
    return output


def extract_strings(data, map, dkey):
    extracted = []
    # for match in not_control_char_re.finditer(data): # This gets all unicode chars, can include lot of garbage if you only care about English, will miss out other languages
    for match in ascii_chars_re.finditer(data):  # Matches ONLY Ascii (old behavior) , good if you only care about English
        x = match.group().rstrip('\n').rstrip('\r')
        x.replace('\r', '').replace('\n', ' ')
        x = tokenized_replace(x, map, dkey)
        extracted.append(x)

    if len(extracted) == 0:
        extracted = ''
    elif len(extracted) == 1:
        extracted = extracted[0]
    return extracted


def unobfucate_strings(data, map, dkey):
    params = []
    exclude = ['_len', 'unk']

    for key, value in data._values.items():
        if any(x in key for x in exclude):
            continue
        if isinstance(value, bytes):
            value = value.decode('utf8', 'ignore')
            value = tokenized_replace(value, map, dkey)
        params.append(f'{key}={str(value)}')

    return params


def process_odl(filename, map):
    odl_rows = []
    basename = os.path.basename(filename)
#    dirname = os.path.dirname(filename)
    try:
        dkey = [dkey_dict[key] for key in dkey_dict if key in os.path.dirname(filename)][0]
    except Exception:
        dkey = ''
    try:
        f = open(filename, 'rb')
    except Exception as e:
        log.error(e)
        return pd.DataFrame()
    with f:
        i = 1
        header = cparser.Odl_header(f.read(0x100))
        if header.signature == b'EBFGONED':  # Odl header
            pass
        else:
            log.warning(f'{basename} wrong header! Did not find EBFGONED')
            return pd.DataFrame()
        signature = f.read(8)

        # Now either we have the gzip header here or the CDEF header (compressed or uncompressed handles both)
        if signature[0:4] == b'\x1F\x8B\x08\x00':  # gzip
            try:
                f.seek(-8, 1)
                file_data = gzip.decompress(f.read())
            except (gzip.BadGzipFile, OSError) as ex:
                log.error(f'..decompression error for file {basename}. {ex}')
                return pd.DataFrame()
            f.close()
            f = io.BytesIO(file_data)
            signature = f.read(8)
        if signature != b'\xCC\xDD\xEE\xFF\0\0\0\0':  # CDEF header
            log.warning(f'{basename} wrong header! Did not find 0xCCDDEEFF')
            return pd.DataFrame()
        else:
            f.seek(-8, 1)
            data_block = f.read(56)  # odl complete header is 56 bytes
        while data_block:
            description = ''
            odl = {
                'Filename': basename,
                'File_Index': i,
                'Timestamp': None,
                'One_Drive_Version': header.one_drive_version.decode('utf8').split('\x00', 1)[0],
                'OS_Version': header.windows_version.decode('utf8').split('\x00', 1)[0],
                'Code_File': '',
                'Flags': '',
                'Function': '',
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
            data_block = cparser.Data_block(data_block)
            if data_block.data_len == 0 or data_block.signature != 0xffeeddcc:
                return pd.DataFrame()
            timestamp = ReadUnixMsTime(data_block.timestamp)
            odl['Timestamp'] = timestamp
            data = cparser.Data(f.read(data_block.data_len))
            params_len = (data_block.data_len - data.code_file_name_len - data.code_function_name_len - 12)
            f.seek(- params_len, io.SEEK_CUR)

            if params_len:
                try:
                    structure = getattr(cparser, f"{data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.unknown}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                    try:
                        params = structure(f.read(params_len))
                        if len(params) == 0:
                            f.seek(- params_len, 1)
                            params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map, dkey)
                        else:
                            params = unobfucate_strings(params, map, dkey)
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
                            except:
                                pass
                            params = ', '.join(params)
                        description = ''.join([v for (k, v) in cparser.consts.items() if k == f"{data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.unknown}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}_des"])
                    except EOFError:
                        log.error(f"EOFError while parsing {data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.unknown}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                        f.seek(- params_len, 1)
                        params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map, dkey)
                except AttributeError:
                    params = extract_strings(f.read(params_len).decode('utf8', 'ignore'), map, dkey)

            else:
                params = ''
            odl['Code_File'] = data.code_file_name.decode('utf8')
            odl['Flags'] = data.unknown
            odl['Function'] = data.code_function_name.decode('utf8')
            odl['Description'] = description
            odl['Params'] = params
            odl_rows.append(odl)
            i += 1
            data_block = f.read(56)
    return pd.DataFrame.from_records(odl_rows)


def parse_odl(rootDir, key='', pb=False, value_label=False, gui=False):
    filenames = []
    obfuscation_maps = []

    map = {}

    df = pd.DataFrame(columns=['Filename',
                               'File_Index',
                               'Timestamp',
                               'One_Drive_Version',
                               'OS_Version',
                               'Code_File',
                               'Flags',
                               'Function',
                               'Description',
                               'Params',
                               'Param1',
                               'Param2',
                               'Param3',
                               'Param4',
                               'Param5',
                               'Param6',
                               'Param7',
                               'Param8',
                               'Param9',
                               'Param10',
                               'Param11',
                               'Param12',
                               'Param13'])

    for path, subdirs, files in os.walk(rootDir):
        filematch = ([os.path.join(path, file) for file in files if file.endswith(('.odl', '.odlgz', '.odlsent', '.aodl'))])
        obfuscation_map = ([os.path.join(path, file) for file in files if file == "ObfuscationStringMap.txt"])
        keystore_file = (os.path.join(path, file) for file in files if file == "general.keystore")
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
    count = 0
    if gui:
        pb.configure(mode='determinate')
    for filename in filenames:
        count += 1
        log_df = process_odl(filename, map)
        if gui:
            progress_gui(total, count, pb, value_label, status=f'Parsing log files for {key}. Please wait....')
        else:
            progress(count, total, status=f'Parsing log files for {key}. Please wait....')
        df = pd.concat([df, log_df], ignore_index=True, axis=0)

    return df
