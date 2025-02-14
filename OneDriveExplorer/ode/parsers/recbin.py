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

import os
import struct
import hashlib
import quickxorhash
import base64
from datetime import datetime, timedelta
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

            return [f'SHA1({sha1_digest})', f'quickXor({quick_xor_digest})', '2']

        except PermissionError:
            return ['', '', '2']

        except Exception:
            return ['', '', '']

    def if_exists(self, path, name, delete_time_stamp, rbin_df):
        test_date = datetime.strptime(self.from_unix_sec(delete_time_stamp), '%Y-%m-%d %H:%M:%S')

        for index, row in rbin_df.iterrows():
            try:
                test_path = row.get('Path', '').split('\\', 1)[1]
            except IndexError:
                test_path = row.get('Name', '')

            if path.endswith(test_path) and row.get('Name') == name:
                delete_timestamp = datetime.strptime(row.get('notificationTime'), '%Y-%m-%d %H:%M:%S')
                if delete_timestamp - timedelta(seconds=1) <= test_date <= delete_timestamp + timedelta(seconds=1):
                    return index

            if test_path.endswith(name):
                delete_timestamp = datetime.strptime(row.get('notificationTime'), '%Y-%m-%d %H:%M:%S')
                if delete_timestamp - timedelta(seconds=1) <= test_date <= delete_timestamp + timedelta(seconds=1):
                    return index

        return -1

    def get_file_metadata(self, i_name, files, od_keys, localHashAlgorithm, rbin_df):
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
                full_file_path = f'{i_name.replace("$I", "$R")}'
                parentResourceId = ''
                get_hash = self.hash_file(full_file_path)
                hash_func = get_hash[1] if localHashAlgorithm == 5 else get_hash[0]
                index = self.if_exists(path, name, delete_time_stamp, rbin_df)

                if index >= 0:
                    rbin_df.at[index, 'inRecycleBin'] = get_hash[2]
                    rbin_df.at[index, 'DeleteTimeStamp'] = self.from_unix_sec(delete_time_stamp)
                    rbin_df.at[index, 'size'] = file_size
                    rbin_df.at[index, 'hash'] = hash_func
                    parentResourceId = rbin_df.at[index, 'resourceId']
                else:
                    input_data = {
                        'Type': 'Deleted',
                        'parentResourceId': '',
                        'resourceId': '',
                        'eTag': '',
                        'Path': f'{path}',
                        'Name': name,
                        'inRecycleBin': get_hash[2],
                        'volumeId': '',
                        'fileId': '',
                        'DeleteTimeStamp': self.from_unix_sec(delete_time_stamp),
                        'notificationTime': '',
                        'size': file_size,
                        'hash': hash_func,
                        'deletingProcess': ''
                    }
                    yield input_data

                if files:
                    for file in files:
                        full_file_path = f'{i_name.replace("$I", "$R")}{file}'
                        get_hash = self.hash_file(full_file_path)
                        hash_func = get_hash[1] if localHashAlgorithm == 5 else get_hash[0]
                        file_stat = os.stat(full_file_path)
                        name = file.split('\\')[-1]
                        path = file.rsplit('\\', 1)[0]
                        index = self.if_exists(f'{file_name}{path}', name, delete_time_stamp, rbin_df)

                        if index >= 0:
                            rbin_df.at[index, 'inRecycleBin'] = get_hash[2]
                            rbin_df.at[index, 'DeleteTimeStamp'] = self.from_unix_sec(delete_time_stamp)
                            rbin_df.at[index, 'size'] = f'{file_stat.st_size // 1024 + 1} KB'
                            rbin_df.at[index, 'hash'] = hash_func

                        else:
                            input_data = {
                                'Type': 'Deleted',
                                'parentResourceId': parentResourceId,
                                'resourceId': '',
                                'eTag': '',
                                'Path': f'{file_name}{path}',
                                'Name': name,
                                'inRecycleBin': get_hash[2],
                                'volumeId': '',
                                'fileId': '',
                                'DeleteTimeStamp': self.from_unix_sec(delete_time_stamp),
                                'notificationTime': '',
                                'size': f'{file_stat.st_size // 1024 + 1} KB',
                                'hash': hash_func,
                                'deletingProcess': ''
                            }
                            yield input_data

    def find_deleted(self, recbin, od_keys, localHashAlgorithm, rbin_df, gui=False, pb=False, value_label=False):
        recbin = recbin.replace('/', '\\')
        log.info(f'Started parsing {recbin}')

        file_info = {}

        for path, subdirs, files in os.walk(recbin):
            for name in files:
                if "$I" in name:
                    file_info.setdefault(name, {'iname': os.path.join(path, name), 'files': [], 'folders': []})

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

            match = self.get_file_metadata(iname, filenames, od_keys, localHashAlgorithm, rbin_df)
            if match:
                deleted_items.extend(match)

            if gui:
                progress_gui(total, count, pb, value_label, status='Adding deleted items. Please wait....')
            else:
                progress(count, total, status='Adding deleted items. Please wait....')
            count += 1

        log.info(f'Parsing complete {recbin}')
        return deleted_items
