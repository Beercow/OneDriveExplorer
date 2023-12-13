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
import struct
import hashlib
import quickxorhash
import base64
from datetime import datetime
import logging
from ode.utils import progress, progress_gui

log = logging.getLogger(__name__)


class DeleteProcessor:
    def __init__(self):
        pass

    @staticmethod
    def from_unix_sec(_):
        try:
            return datetime.utcfromtimestamp(int(_)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            log.error(e)
            return datetime.utcfromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def hash_file(file_path):
        buf_size = 65536
        sha1 = hashlib.sha1()
        quick_xor_hash = quickxorhash.quickxorhash()

        try:
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(buf_size)
                    if not data:
                        break
                    sha1.update(data)
                    quick_xor_hash.update(data)

            sha1_digest = sha1.hexdigest()
            quick_xor_digest = base64.b64encode(quick_xor_hash.digest()).decode("utf-8")

            return [f'SHA1({sha1_digest})', f'quickXor({quick_xor_digest})']
        except Exception:
            return ['', '']

    def get_file_metadata(self, i_name, files, od_keys, account):
        with open(i_name, "rb") as file:
            file_record = file.read()

        file_header = int(str(struct.unpack_from('<q', file_record[:])[0]))
        file_size = f"{int(str(struct.unpack_from('<q', file_record[8:])[0])) // 1024 + 1:,} KB"
        delete_time_stamp = int(str(struct.unpack_from('<q', file_record[16:])[0])[0:11]) - 11644473600

        if file_header == 2:
            file_name_length = int(str(struct.unpack_from('<l', file_record[24:])[0]))
            name_length = "<" + str(file_name_length * 2) + "s"
            file_name = struct.unpack_from(name_length, file_record[28:])[0].decode('utf-16').rstrip('\u0000')
        else:
            file_name = str(struct.unpack_from('<520s', file_record[24:])[0]).decode('utf-16').rstrip('\u0000')

        name = file_name.split('\\')[-1]
        path = file_name.rsplit('\\', 1)[0]

        for acc in od_keys.subkeys():
            if any(f'{x.name()}\\' in file_name for x in list(acc.values())):
                if len(files) != 0:
                    for file in files:
                        hash_func = self.hash_file(f'{i_name.replace("$I", "$R")}{file}')[0] if account == 'Personal' else \
                            self.hash_file(f'{i_name.replace("$I", "$R")}{file}')[1]
                        file_size = os.stat(f'{i_name.replace("$I", "$R")}{file}')
                        name = file.split('\\')[-1]
                        path = file.rsplit('\\', 1)[0]
                        input_data = {
                            'Type': 'Deleted',
                            'parentResourceId': '',
                            'resourceId': '',
                            'eTag': '',
                            'Path': f'{file_name}{path}',
                            'Name': name,
                            'inRecycleBin': '2',
                            'volumeId': '',
                            'fileId': '',
                            'DeleteTimeStamp': self.from_unix_sec(delete_time_stamp),
                            'size': f'{file_size.st_size // 1024 + 1} KB',
                            'hash': hash_func
                        }
                        yield input_data
                else:
                    hash_func = self.hash_file(f'{i_name.replace("$I", "$R")}')[0] if account == 'Personal' else \
                        self.hash_file(f'{i_name.replace("$I", "$R")}')[1]
                    input_data = {
                        'Type': 'Deleted',
                        'parentResourceId': '',
                        'resourceId': '',
                        'eTag': '',
                        'Path': f'{path}',
                        'Name': name,
                        'inRecycleBin': '2',
                        'volumeId': '',
                        'fileId': '',
                        'DeleteTimeStamp': self.from_unix_sec(delete_time_stamp),
                        'size': file_size,
                        'hash': hash_func
                    }
                    yield input_data

    def find_deleted(self, recbin, od_keys, account, gui=False, pb=False, value_label=False):
        recbin = recbin.replace('/', '\\')
        log.info(f'Started parsing {recbin}')

        file_info = {}

        for path, subdirs, files in os.walk(recbin):
            for name in files:
                if "$I" in name:
                    index = name[2:]
                    file_info.setdefault(name, {'iname': os.path.join(path, name), 'files': []})

            for x in file_info.keys():
                if x[2:] in path:
                    for name in files:
                        file_info[x]['files'].append(os.path.join(path, name).split(x[2:])[-1])

        total = len(file_info)
        count = 0

        if gui:
            pb['value'] = 0

        deleted_items = []

        for key, value in file_info.items():
            iname = value.get('iname', '')
            filenames = value.get('files', [])

            match = self.get_file_metadata(iname, filenames, od_keys, account)
            if match:
                deleted_items.extend(match)

            if gui:
                progress_gui(total, count, pb, value_label, status='Adding deleted items. Please wait....')
            else:
                progress(count, total, status='Adding deleted items. Please wait....')
            count += 1

        log.info(f'Parsing complete {recbin}')
        return deleted_items
