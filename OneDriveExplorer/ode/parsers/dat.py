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
import logging
import codecs
import csv
from io import StringIO
import binascii
import urllib.parse
from dissect import cstruct
import pandas as pd
from ode.utils import progress, progress_gui, permissions, change_dtype

log = logging.getLogger(__name__)


class ParseResult:
    def __init__(self, df, rbin_df, df_scope, graphMetadata, scopeID, account, localHashAlgorithm):
        self.df = df
        self.rbin_df = rbin_df
        self.df_scope = df_scope
        self.graphMetadata = graphMetadata
        self.scopeID = scopeID
        self.account = account
        self.localHashAlgorithm = localHashAlgorithm

    def __repr__(self):
        """Custom string representation for debugging."""
        return f"ParseResult(df={len(self.df)} rows, rbin_df={len(self.rbin_df)} rows, scopeID={len(self.scopeID)})"


class DATParser:
    def __init__(self):
        self.application_path = f'{os.path.dirname(os.path.abspath(__file__))}/../..'
        self.log = logging.getLogger(__name__)
        self.datstruct = cstruct.cstruct()
        self.DAT_DEF = f'{self.application_path}/ode/helpers/structures'
        self.df = pd.DataFrame()
        self.df_scope = pd.DataFrame()
        self.scopeID = []
        self.account = None
        self.localHashAlgorithm = 0
        self.rbin_df = pd.DataFrame()
        self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])
        self.datstruct.loadfile(self.DAT_DEF)
        self.dict_1 = {'lastChange': 0,
                       'sharedItem': 0,
                       'mediaDateTaken': 0,
                       'mediaWidth': 0,
                       'mediaHeight': 0,
                       'mediaDuration': 0
                       }
        self.dict_2 = {'mediaDateTaken': 0,
                       'mediaWidth': 0,
                       'mediaHeight': 0,
                       'mediaDuration': 0
                       }
        self.dict_3 = {'mediaDuration': 0}
        self.int_to_bin = ['bitMask']
        self.int_to_hex = ['header',
                           'entry_offset'
                           ]
        self.bytes_to_str = ['eTag',
                             'listID',
                             'scopeID',
                             'siteID',
                             'webID',
                             'syncTokenData'
                             ]
        self.bytes_to_hex = ['localHashDigest',
                             'serverHashDigest',
                             'localWaterlineData',
                             'localWriteValidationToken',
                             'localSyncTokenData',
                             'localCobaltHashAlgorithm'
                             ]
        self.split_str = ['fileName',
                          'folderName'
                          ]
        self.id_format = ['resourceID',
                          'parentResourceID',
                          'parentScopeID',
                          'scopeID',
                          'sourceResourceID'
                          ]
        self.rem_list = ['header',
                         'entry_offset',
                         'unknown1',
                         'unknown2',
                         'unknown3',
                         'flags',
                         'unknown4',
                         'unknown5',
                         'unknown6',
                         'syncTokenData',
                         'syncTokenData_size',
                         'unknown7',
                         'sourceResourceID'
                         ]

    def format_id(self, _):
        f = _[:32].decode("utf-8")
        s = int.from_bytes(_[32:], "big")
        if s != 0:
            return f'{f}+{s}'
        return f

    def merge_dicts(self, dict_1, dict_2):
        for k, v in dict_2.items():
            dict_1[k] = v
        return dict_1

    def find_parent(self, x, id_name_dict, parent_dict):
        value = parent_dict.get(x, None)
        if x is None:
            return ''
        elif value is None:
            return x + "\\\\"
        else:
            # Incase there is a id without name.
            if id_name_dict.get(value, None) is None:
                return self.find_parent(value, id_name_dict, parent_dict) + x
        return self.find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))

    def parse_dat(self, usercid, account='Business', gui=False, pb=False, value_label=False):
        usercid = (usercid).replace('/', '\\')
        self.account = usercid.split(os.sep)[-2]
        self.scope_header = False
        self.files_header = False
        self.folders_header = False
        temp_scope = StringIO()
        temp_files = StringIO()
        temp_folders = StringIO()

        self.log.info(f'Start parsing {usercid}.')

        try:
            with open(usercid, 'rb') as f:
                total = f.seek(0, os.SEEK_END)
                f.seek(0, 0)
                header = self.datstruct.HEADER(f.read(536))
                version = hex(header.Version)[2:]
                if header.syncTokenData_size != 0:
                    account = 'Personal'
                    csvwriter = csv.writer(temp_scope, escapechar='\\')
                    csvwriter.writerow(['scopeID', 'siteID', 'webID', 'listID', 'libraryType', 'spoPermissions', 'shortcutVolumeID', 'shortcutItemIndex'])
                    self.scope_header = True
                    syncTokenData = urllib.parse.unquote(header.syncTokenData[:int(header.syncTokenData_size)].decode('utf-8'))
                    syncDict = dict(item.split("=") for item in syncTokenData.split(";"))
                    csvwriter.writerow([syncDict['ID'], '', '', '', '', ''])

                if version == '29':
                    chunk = 1048
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1048
                    #define FOLDER_CONSTANT  299
                    #define DELETE_CONSTANT  1032
                    #define LSCOPE_CONSTANT  208
                    #define LFOLDER_CONSTANT 825
                    #define VAULT_CONSTANT   320
                    #define ASCOPE_CONSTANT  176
                    """)

                elif version == '2a':
                    chunk = 1080
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1080
                    #define FOLDER_CONSTANT  331
                    #define DELETE_CONSTANT  1064
                    #define LSCOPE_CONSTANT  240
                    #define LFOLDER_CONSTANT 857
                    #define VAULT_CONSTANT   352
                    #define ASCOPE_CONSTANT  208
                    """)

                elif version == '2b':
                    chunk = 1080
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1080
                    #define FOLDER_CONSTANT  331
                    #define DELETE_CONSTANT  1064
                    #define LSCOPE_CONSTANT  240
                    #define LFOLDER_CONSTANT 857
                    #define VAULT_CONSTANT   352
                    #define ASCOPE_CONSTANT  208
                    """)

                elif version == '2c':
                    chunk = 1096
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1096
                    #define FOLDER_CONSTANT  347
                    #define DELETE_CONSTANT  1080
                    #define LSCOPE_CONSTANT  256
                    #define LFOLDER_CONSTANT 873
                    #define VAULT_CONSTANT   368
                    #define ASCOPE_CONSTANT  224
                    """)

                elif version == '2d':
                    chunk = 1104
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1098
                    #define FOLDER_CONSTANT  347
                    #define DELETE_CONSTANT  1082
                    #define LSCOPE_CONSTANT  258
                    #define LFOLDER_CONSTANT 875
                    #define VAULT_CONSTANT   370
                    #define ASCOPE_CONSTANT  226
                    """)

                elif version == '2e':
                    chunk = 1128
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1128
                    #define FOLDER_CONSTANT  371
                    #define DELETE_CONSTANT  1112
                    #define LSCOPE_CONSTANT  288
                    #define LFOLDER_CONSTANT 905
                    #define VAULT_CONSTANT   400
                    #define ASCOPE_CONSTANT  256
                    """)

                elif version == '2f':
                    chunk = 1128
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1128
                    #define FOLDER_CONSTANT  371
                    #define DELETE_CONSTANT  1112
                    #define LSCOPE_CONSTANT  288
                    #define LFOLDER_CONSTANT 905
                    #define VAULT_CONSTANT   400
                    #define ASCOPE_CONSTANT  256
                    """)

                elif version == '30':
                    chunk = 1152
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1152
                    #define FOLDER_CONSTANT  395
                    #define DELETE_CONSTANT  1136
                    #define LSCOPE_CONSTANT  312
                    #define LFOLDER_CONSTANT 929
                    #define VAULT_CONSTANT   424
                    #define ASCOPE_CONSTANT  280
                    """)

                elif version == '31':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '32':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '33':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '34':
                    chunk = 1160
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1160
                    #define FOLDER_CONSTANT  403
                    #define DELETE_CONSTANT  1144
                    #define LSCOPE_CONSTANT  320
                    #define LFOLDER_CONSTANT 937
                    #define VAULT_CONSTANT   432
                    #define ASCOPE_CONSTANT  288
                    """)

                elif version == '35':
                    chunk = 1176
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1176
                    #define FOLDER_CONSTANT  419
                    #define DELETE_CONSTANT  1160
                    #define LSCOPE_CONSTANT  336
                    #define LFOLDER_CONSTANT 953
                    #define VAULT_CONSTANT   448
                    #define ASCOPE_CONSTANT  304
                    """)

                elif version == '36':
                    chunk = 1232
                    self.datstruct.load("""
                    #define BLOCK_CONSTANT   1232
                    #define FOLDER_CONSTANT  475
                    #define DELETE_CONSTANT  1216
                    #define LSCOPE_CONSTANT  392
                    #define LFOLDER_CONSTANT 1009
                    #define VAULT_CONSTANT   504
                    #define ASCOPE_CONSTANT  360
                    """)

                else:
                    if not gui:
                        print(f'Unknown dat verison: {version} (Please report issue)')
                    log.error(f'Unknown dat verison: {version} (Please report issue)')
                    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

                while True:
                    count = f.tell()
                    ff = f.read(1).hex()

                    if f.tell() == total:
                        break

                    f. seek(-1, 1)

                    if ff == '01':
                        data_type = 'File'
                        if version == '29':
                            block = self.datstruct.DAT_FILE_v29(f.read(chunk))
                        elif version == '2a':
                            block = self.datstruct.DAT_FILE_v2a(f.read(chunk))
                        elif version == '2b':
                            block = self.datstruct.DAT_FILE_v2b(f.read(chunk))
                        elif version == '2c':
                            block = self.datstruct.DAT_FILE_v2c(f.read(chunk))
                        elif version == '2d':
                            block = self.datstruct.DAT_FILE_v2d(f.read(chunk))
                        elif version == '2e':
                            block = self.datstruct.DAT_FILE_v2e(f.read(chunk))
                        elif version == '2f':
                            block = self.datstruct.DAT_FILE_v2f(f.read(chunk))
                        elif version == '30':
                            block = self.datstruct.DAT_FILE_v30(f.read(chunk))
                        elif version == '31':
                            block = self.datstruct.DAT_FILE_v31(f.read(chunk))
                        elif version == '32':
                            block = self.datstruct.DAT_FILE_v32(f.read(chunk))
                        elif version == '33':
                            block = self.datstruct.DAT_FILE_v33(f.read(chunk))
                        elif version == '34':
                            block = self.datstruct.DAT_FILE_v34(f.read(chunk))
                        elif version == '35':
                            block = self.datstruct.DAT_FILE_v35(f.read(chunk))
                        elif version == '36':
                            block = self.datstruct.DAT_FILE_v36(f.read(chunk))
                        else:
                            block = self.datstruct.DAT_FILE(f.read(chunk))

                    elif ff == '02':
                        data_type = 'Folder'
                        if int(version, 16) <= 44:
                            block = self.datstruct.DAT_FOLDER_v29_v2c(f.read(chunk))
                        else:
                            block = self.datstruct.DAT_FOLDER_v2d_v36(f.read(chunk))

                    elif ff == '09':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_LIBRARY_SCOPE(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except Exception:
                                continue
                        block._values.update([('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    elif ff == '0a':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_LIBRARY_FOLDER(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except Exception:
                                continue
                        block._values.update([('siteID', b''), ('webID', b'')])
                        block._values.move_to_end('listID', last=True)
                        block._values.update([('libraryType', ''), ('spoPermissions', ''), ('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    elif ff == '0b':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_VAULT(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except Exception:
                                continue
                        block._values.update([('siteID', b''), ('webID', b''), ('listID', b''), ('libraryType', ''), ('spoPermissions', '')])
                        block._values.move_to_end('shortcutVolumeID', last=True)
                        block._values.move_to_end('shortcutItemIndex', last=True)

                    elif ff == '0c':
                        data_type = 'Scope'
                        block = self.datstruct.DAT_ADDED_SCOPE(f.read(chunk))
                        for key in self.rem_list:
                            try:
                                del block._values[key]
                            except Exception:
                                continue
                        block._values.update([('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    else:
                        block = self.datstruct.DAT_BLOCK(f.read(chunk))
                        continue

                    for k, v in block._values.items():
                        if k in self.split_str:
                            block._values[k] = v.split('\x00', 1)[0]
                        if k in self.int_to_bin:
                            block._values[k] = f'{v:032b}'
                        if k in self.int_to_hex:
                            block._values[k] = hex(v)
                        if k in self.bytes_to_hex:
                            block._values[k] = v.hex()
                        if k in self.bytes_to_str:
                            block._values[k] = v.decode('utf-8')
                        if k in self.id_format:
                            block._values[k] = self.format_id(v)

                    if data_type == 'File':
                        csvwriter = csv.writer(temp_files, escapechar='\\')
                        if version <= '2b':
                            self.merge_dicts(block._values, self.dict_1)
                        elif version >= '2c' and version <= '34':
                            self.merge_dicts(block._values, self.dict_2)
                            block._values['sharedItem'] = [*block.bitMask][29]
                        elif version >= '35':
                            self.merge_dicts(block._values, self.dict_3)
                            block._values['sharedItem'] = [*block.bitMask][29]
                        if not self.files_header:
                            csvwriter.writerow(dict(block._values))
                            self.files_header = True

                    if data_type == 'Folder':
                        csvwriter = csv.writer(temp_folders, escapechar='\\')
                        block._values['sharedItem'] = [*block.bitMask][29]
                        if not self.folders_header:
                            csvwriter.writerow(dict(block._values))
                            self.folders_header = True

                    if data_type == 'Scope':
                        csvwriter = csv.writer(temp_scope, escapechar='\\')
                        if not self.scope_header:
                            csvwriter.writerow(dict(block._values))
                            self.scope_header = True

                    csvwriter.writerow(block._values.values())

                    if count % 30 == 0:
                        if gui:
                            progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                        else:
                            progress(count, total, status='Building folder list. Please wait....')

        except Exception as e:
            # log.error(e)
            return ParseResult(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                               self.graphMetadata, [], self.account,
                               self.localHashAlgorithm)

        if not gui:
            print()

        temp_scope.seek(0)
        temp_files.seek(0)
        temp_folders.seek(0)

        self.df_scope = pd.read_csv(temp_scope)
        temp_scope.close()
        self.df_scope.insert(0, 'Type', 'Scope')
        self.df_scope.insert(5, 'tenantID', '')
        self.df_scope.insert(6, 'webURL', '')
        self.df_scope.insert(7, 'remotePath', '')
        self.df_scope = change_dtype(self.df_scope, df_name='df_scope')
        self.df_scope['spoPermissions'] = self.df_scope['spoPermissions'].apply(lambda x: permissions(x))
        self.scopeID = self.df_scope['scopeID'].tolist()

        df_files = pd.read_csv(temp_files, usecols=['parentResourceID', 'resourceID', 'eTag', 'fileName', 'fileStatus', 'spoPermissions', 'volumeID', 'itemIndex', 'lastChange', 'size', 'localHashDigest', 'sharedItem', 'mediaDateTaken', 'mediaWidth', 'mediaHeight', 'mediaDuration'])
        temp_files.close()
        df_files['localHashAlgorithm'] = 0
        df_files.insert(0, 'Type', 'File')
        df_files.rename(columns={"fileName": "Name",
                                 "mediaDateTaken": "DateTaken",
                                 "mediaWidth": "Width",
                                 "mediaHeight": "Height",
                                 "mediaDuration": "Duration"
                                 }, inplace=True)
        df_files['DateTaken'] = pd.to_datetime(df_files['DateTaken'], unit='s').astype(str)
        df_files = change_dtype(df_files, df_name='df_files')
        columns = ['DateTaken', 'Width', 'Height', 'Duration']
        df_files['Media'] = df_files[columns].to_dict(orient='records')
        df_files = df_files.drop(columns=columns)
        if account == 'Personal':
            df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'SHA1({x})')
            self.localHashAlgorithm = 4
        else:
            df_files['localHashDigest'] = df_files['localHashDigest'].apply(lambda x: f'quickXor({codecs.encode(binascii.unhexlify(x), "base64").decode("utf-8").rstrip()})')
            self.localHashAlgorithm = 5
        df_files['size'] = df_files['size'].apply(lambda x: '0 KB' if x == 0 else f'{x//1024 + 1:,} KB')
        df_files['spoPermissions'] = df_files['spoPermissions'].apply(lambda x: permissions(x))
        df_files['lastChange'] = pd.to_datetime(df_files['lastChange'], unit='s').astype(str)
        df_folders = pd.read_csv(temp_folders, usecols=['parentScopeID', 'parentResourceID', 'resourceID', 'eTag', 'folderName', 'folderStatus', 'spoPermissions', 'volumeID', 'itemIndex', 'sharedItem'])
        temp_folders.close()
        df_folders.insert(0, 'Type', 'Folder')
        df_folders.rename(columns={"folderName": "Name"}, inplace=True)
        df_folders = change_dtype(df_folders, df_name='df_folders')
        df_folders['spoPermissions'] = df_folders['spoPermissions'].apply(lambda x: permissions(x))

        self.df = pd.concat([self.df_scope, df_files, df_folders], ignore_index=True, axis=0)
        self.df = self.df.where(pd.notnull(self.df), None)

        return ParseResult(self.df, self.rbin_df, self.df_scope,
                           self.graphMetadata, self.scopeID, self.account,
                           self.localHashAlgorithm)
