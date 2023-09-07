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

import re
import io
import logging
import psutil
import pytsk3

log = logging.getLogger(__name__)
dirPath = '/'
partitionList = psutil.disk_partitions()
filedata = ''


def directoryRecurse(directoryObject, parentPath, user, filedata=False):
    for entryObject in directoryObject:
        if entryObject.info.name.name in [b".", b".."]:
            continue

        try:
            f_type = entryObject.info.name.type
            size = entryObject.info.meta.size
        except Exception:
            continue

        try:

            filepath = '/%s/%s' % ('/'.join(parentPath), entryObject.info.name.name.decode())

            if f_type == pytsk3.TSK_FS_NAME_TYPE_REG and entryObject.info.meta.size != 0:
                searchResult = re.match(b'NTUSER.DAT$', entryObject.info.name.name)

                if not searchResult:
                    continue

                filepath = filepath.replace('/', '\\')
                log.info(f'File: {parentPath}, {filepath}, {entryObject.info.name.name.decode()}, {entryObject.info.meta.size}')
                filedata = entryObject.read_random(0, entryObject.info.meta.size)
                filedata = io.BytesIO(filedata)
                return filedata
                break

            elif f_type == pytsk3.TSK_FS_NAME_TYPE_REG and entryObject.info.meta.size == 0:
                pass

            else:
                continue
#                log.warning(f'This went wrong, {entryObject.info.name.name} {f_type}')

        except IOError as e:
            log.error(e)
            continue


def live_hive(user, profile_path):
    for partition in partitionList:
        imagehandle = pytsk3.Img_Info('\\\\.\\'+partition.device.strip("\\"))

        if 'NTFS' in partition.fstype:
            log.info(partition)
            filesystemObject = pytsk3.FS_Info(imagehandle)
            directoryObject = filesystemObject.open_dir(path=profile_path)
            data = directoryRecurse(directoryObject, [], user, filedata=filedata)
            return data
