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

import os
import io
import gzip
import re
import string
import datetime
import pandas as pd
import ode.helpers.structures as cdef
from ode.utils import progress_gui, progress
from dissect import cstruct
import logging

log = logging.getLogger(__name__)

printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')

cparser = cstruct.cstruct()
cparser.load(cdef.ODL_DEF)


def ReadUnixMsTime(unix_time_ms):  # Unix millisecond timestamp
    '''Returns datetime object, or empty string upon error'''
    if unix_time_ms not in (0, None, ''):
        try:
            if isinstance(unix_time_ms, str):
                unix_time_ms = float(unix_time_ms)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time_ms/1000)
        except (ValueError, OverflowError, TypeError) as ex:
            # print("ReadUnixMsTime() Failed to convert timestamp from value " + str(unix_time_ms) + " Error was: " + str(ex))
            pass
    return ''


def extract_strings(data):
    extracted = []
    #for match in not_control_char_re.finditer(data): # This gets all unicode chars, can include lot of garbage if you only care about English, will miss out other languages
    for match in ascii_chars_re.finditer(data): # Matches ONLY Ascii (old behavior) , good if you only care about English
        x = match.group().rstrip('\n').rstrip('\r')
        x.replace('\r', '').replace('\n', ' ')
#        x = tokenized_replace(x, map)
        extracted.append(x)

    if len(extracted) == 0:
        extracted = ''
    elif len(extracted) == 1:
        extracted = extracted[0]
    return extracted


def process_odl(filename):
    odl_rows = []
    basename = os.path.basename(filename)
    try:
        f = open(filename, 'rb')
    except Exception as e:
        log.error(e)
        return pd.DataFrame()
    with f:
        i = 1
        header = f.read(8)
        if header[0:8] == b'EBFGONED':  # Odl header
            f.seek(0x100)
            header = f.read(8)
            file_pos = 0x108
        else:
            file_pos = 8
        # Now either we have the gzip header here or the CDEF header (compressed or uncompressed handles both)
        if header[0:4] == b'\x1F\x8B\x08\x00':  # gzip
            try:
                f.seek(file_pos - 8)
                file_data = gzip.decompress(f.read())
            except (gzip.BadGzipFile, OSError) as ex:
                log.error(f'..decompression error for file {basename}. {ex}')
                return pd.DataFrame()
            f.close()
            f = io.BytesIO(file_data)
            header = f.read(8)
        if header != b'\xCC\xDD\xEE\xFF\0\0\0\0':  # CDEF header
            log.warning(f'{basename} wrong header! Did not find 0xCCDDEEFF')
            return pd.DataFrame()
        else:
            f.seek(-8, io.SEEK_CUR)
            header = f.read(56)  # odl complete header is 56 bytes
        while header:
            odl = {
                'Filename': basename,
                'File_Index': i,
                'Timestamp': None,
                'Code_File': '',
                'Flags': '',
                'Function': '',
                'Params': ''
            }
            header = cparser.Data_block(header)
            if header.data_len == 0 or header.signature != 0xffeeddcc:
                return pd.DataFrame()
            timestamp = ReadUnixMsTime(header.timestamp)
            odl['Timestamp'] = timestamp
            data = cparser.Data(f.read(header.data_len))
            params_len = (header.data_len - data.code_file_name_len - data.code_function_name_len - 12)
            f.seek(- params_len, io.SEEK_CUR)

            if params_len:
                try:
                    structure = getattr(cparser, f"{data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                    try:
                        params = structure(f.read(params_len))
                        if len(params) == 0:
                            f.seek(- params_len, 1)
                            params = extract_strings(f.read(params_len).decode('utf8', 'ignore'))
                    except EOFError:
                        log.error(f"EOFError while parsing {data.code_file_name.decode('utf8').lower().split('.')[0]}_{data.code_function_name.decode('utf8').split('::')[-1].replace('~', '_').replace(' ()', '_').lower()}")
                        f.seek(- params_len, 1)
                        params = extract_strings(f.read(params_len).decode('utf8', 'ignore'))
                except AttributeError as e:
                    log.warning(e)
                    params = extract_strings(f.read(params_len).decode('utf8', 'ignore'))
            else:
                params = ''
            odl['Code_File'] = data.code_file_name.decode('utf8')
            odl['Flags'] = data.unknown
            odl['Function'] = data.code_function_name.decode('utf8')
            odl['Params'] = params
            odl_rows.append(odl)
            i += 1
            header = f.read(56)
    return pd.DataFrame.from_records(odl_rows)


def parse_odl(rootDir, key='', pb=False, value_label=False, gui=False):
    filenames = []

    df = pd.DataFrame(columns=['Filename',
                               'File_Index',
                               'Timestamp',
                               'Code_File',
                               'Flags',
                               'Function',
                               'Params'])

    for path, subdirs, files in os.walk(rootDir):
        filematch = ([os.path.join(path, file) for file in files if file.endswith(('.odl', '.odlgz', '.odlsent', '.aodl'))])
        if filematch:
            filenames += filematch

    total = len(filenames)
    count = 0
    if gui:
        pb.configure(mode='determinate')
    for filename in filenames:
        count += 1
        log_df = process_odl(filename)
        if gui:
            progress_gui(total, count, pb, value_label, status=f'Parsing log files for {key}. Please wait....')
        else:
            progress(count, total, status=f'Parsing log files for {key}. Please wait....')
        df = pd.concat([df, log_df], ignore_index=True, axis=0)

    return df
