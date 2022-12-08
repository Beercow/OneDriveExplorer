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

log = logging.getLogger(__name__)


def from_unix_sec(_):
    try:
        return datetime.utcfromtimestamp(int(_)).strftime('%Y-%m-%d %H:%M:%S')

    except:
        return datetime.utcfromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S')


def find_deleted(recbin, od_keys, account):
    recbin = (recbin).replace('/', '\\')
    log.info(f'Started parsing {recbin}')
    d = {}
    i = []
    rbin = []

    for path, subdirs, files in os.walk(recbin):
        for name in files:
            if "$I" in name:
                i.append(name[2:])
                d.setdefault(name, {})
                d[name].setdefault('iname', os.path.join(path, name))
                d[name].setdefault('files', [])

        for x in i:
            if x in path:
                for name in files:
                    d[f'$I{x}'].setdefault('files', []).append(os.path.join(path, name).split(x)[-1])

    for key, value in d.items():
        filenames = []
        for k, v in value.items():
            if k == 'iname':
                iname = v
            if k == 'files':
                filenames = v

        match = getFileMetadata(iname, filenames, od_keys, account)
        if match:
            for m in match:
                rbin.append(m)

    return rbin


def hash_file(file):
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    h = quickxorhash.quickxorhash()

    try:
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
                h.update(data)

        return [f'SHA1({sha1.hexdigest()})', f'quickXor({base64.b64encode(h.digest()).decode("utf-8")})']
    except Exception as e:
        return ['', '']


def getFileMetadata(iName, files, od_keys, account):
    fileRecord = 0

    with open(iName, "rb") as file:
        fileRecord = file.read()

    fileHeader = int(str(struct.unpack_from('<q', fileRecord[0:])[0]))

    if (fileHeader == 2):
        fileSize = int(str(struct.unpack_from('<q', fileRecord[8:])[0]))
        deleteTimeStamp = int(str(struct.unpack_from('<q', fileRecord[16:])[0])[0:11]) - 11644473600
        fileNameLength = int(str(struct.unpack_from('<l', fileRecord[24:])[0]))
        nameLength = "<" + str(fileNameLength * 2) + "s"
        fileName = struct.unpack_from(nameLength, fileRecord[28:])[0].decode('utf-16').rstrip('\u0000')
        name = fileName.split('\\')[-1]
        path = fileName.rsplit('\\', 1)[0]

    else:
        fileSize = int(str(struct.unpack_from('<q', fileRecord[8:])[0]))
        deleteTimeStamp = int(str(struct.unpack_from('<q', fileRecord[16:])[0])[0:11]) - 11644473600
        fileName = str(struct.unpack_from('<520s', fileRecord[24:])[0]).decode('utf-16').rstrip('\u0000')
        name = fileName.split('\\')[-1]
        path = fileName.rsplit('\\', 1)[0]

    for account in od_keys.subkeys():
        if [x.name() for x in list(account.values()) if f'{x.name()}\\' in fileName]:
            if len(files) != 0:
                for file in files:
                    if account == 'Personal':
                        hash = hash_file(f'{iName.replace("$I", "$R")}{file}')[0]
                    else:
                        hash = hash_file(f'{iName.replace("$I", "$R")}{file}')[1]
                    fileSize = os.stat(f'{iName.replace("$I", "$R")}{file}')
                    name = file.split('\\')[-1]
                    path = file.rsplit('\\', 1)[0]
                    input = {'ParentId': '',
                             'DriveItemId': '',
                             'eTag': '',
                             'Type': 'File - deleted',
                             'Name': name,
                             'Size': fileSize.st_size,
                             'Hash': hash,
                             'Path': f'{fileName}{path}',
                             'DeleteTimeStamp': from_unix_sec(deleteTimeStamp),
                             'Children': [],
                             'Level': ''
                             }

                    yield input

            else:
                if account == 'Personal':
                    hash = hash_file(f'{iName.replace("$I", "$R")}')[0]
                else:
                    hash = hash_file(f'{iName.replace("$I", "$R")}')[1]

                input = {'ParentId': '',
                         'DriveItemId': '',
                         'eTag': '',
                         'Type': 'File - deleted',
                         'Name': name,
                         'Size': fileSize,
                         'Hash': hash,
                         'Path': f'{path}',
                         'DeleteTimeStamp': from_unix_sec(deleteTimeStamp),
                         'Children': [],
                         'Level': ''
                         }

                yield input
