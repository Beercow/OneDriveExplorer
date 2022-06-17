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
import logging
import codecs
import pandas as pd
from Registry import Registry
from ode.utils import unicode_strings, progress, progress_gui

log = logging.getLogger(__name__)


def parse_dat(usercid, reghive, recbin, start, gui=False, pb=False, value_label=False):
    usercid = (usercid).replace('/', '\\')

    if reghive:
        try:
            reghive = (reghive).replace('/', '\\')
        except AttributeError:
            pass

    log.info(f'Start parsing {usercid}. Registry hive: {reghive}')
    ff = re.compile(b'([\x01|\x02|\x09]\xab\xab\xab\xab\xab\xab\xab)')  # \x01 = file, \x02 = folder, \x09 = share

    with open(usercid, 'rb') as f:
        total = len(f.read())
        f.seek(0)
        version = int(f.read(1).hex(), 16)
        if version <= 0x29:
            ff = re.compile(b'([\x01|\x02|\x09]\xab\xab\xab)')
#        if version >= 0x35:
#            ff = re.compile(b'([\x01|\x02]\x00\x27\xec\xb1\x01\x00\x00|\x09\xab\xab\xab\xab\xab\xab\xab)')  # \x01 = file, \x02 = folder, \x09 = share
        uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
        personal = uuid4hex.search(f.read())
        f.seek(0)
        dir_index = []
        entries = re.finditer(ff, f.read())
        current = next(entries, total)
        while isinstance(current, re.Match):
            s = current.start()
            count = s
            n_current = next(entries, total)
            hash = ''
            size = ''
            f.seek(s)
            if b'\x09' in current[0]:
                f.seek(s + 16)
                check = f.read(8)
                if check == b'\x01\x00\x00\x00\x00\x00\x00\x00':
                    duuid = f.read(39).decode("utf-8")
                    ouuid = ''
                    eTag = ''
                else:
                    current = n_current
                    continue
            else:
                if current[0].startswith(b'\x01'):
                    type = 'File'
                else:
                    type = 'Folder'
                if version <= 0x29:
                    f.seek(s + 8)
                else:
                    f.seek(s + 16)
                check = f.read(8)
                if check == b'\x01\x00\x00\x00\x00\x00\x00\x00':
                    ouuid = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    duuid = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    eTag = f.read(56).decode("utf-8").split('\u0000\u0000', 1)[0]
                    f.seek(26, 1)
                    if type == 'File':
                        if personal:
                            hash = f'SHA1({f.read(20).hex()})'
                        else:
                            hash = f'quickXor({codecs.encode(f.read(20), "base64").decode("utf-8").rstrip()})'
                        if version <= 0x29:
                            f.seek(4, 1)
                        else:
                            f.seek(12, 1)
                        size = int.from_bytes(f.read(8), "little")
                    try:
                        buffer = n_current.start() - f.tell()
                    except AttributeError:
                        buffer = n_current - f.tell()
                    name = unicode_strings(f.read(buffer), ouuid)
                else:
                    current = n_current
                    continue
            if not dir_index:
                if reghive and personal:
                    try:
                        reg_handle = Registry.Registry(reghive)
                        int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive\Personal')
                        for providers in int_keys.values():
                            if providers.name() == 'MountPoint':
                                mountpoint = providers.value()
                    except Exception as e:
                        log.warning(f'Unable to read registry hive! {e}')
                        mountpoint = 'User Folder'
                else:
                    mountpoint = 'User Folder'
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'eTag': '',
                         'Type': 'Root Default',
                         'Name': mountpoint,
                         'Size': '',
                         'Hash': '',
                         'Children': []
                         }
                dir_index.append(input)
            input = {'ParentId': duuid,
                     'DriveItemId': ouuid,
                     'eTag': eTag,
                     'Type': type,
                     'Name': name.split('\u0000', 1)[0],
                     'Size': size,
                     'Hash': hash,
                     'Children': []
                     }

            dir_index.append(input)

            if gui:
                progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
            else:
                progress(count, total, status='Building folder list. Please wait....')

            current = n_current

    print('\n')

    return pd.DataFrame.from_records(dir_index), f.name, personal
