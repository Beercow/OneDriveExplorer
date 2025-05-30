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
import re
from io import StringIO, BytesIO
import csv
import urllib.parse
import logging
import codecs
import pandas as pd
from ode.utils import progress, progress_gui, permissions, change_dtype
import ode.helpers.structures as datstruct

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
        self.df = pd.DataFrame()
        self.df_scope = pd.DataFrame()
        self.scopeID = []
        self.account = None
        self.localHashAlgorithm = 0
        self.rbin_df = pd.DataFrame()
        self.graphMetadata = pd.DataFrame(columns=['resourceID', 'Metadata'])

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

    def parse_dat(self, usercid, account='Business', gui=False, pb=False, value_label=False):
        usercid = (usercid).replace('/', '\\')
        self.account = usercid.split(os.sep)[-2]
        self.scope_header = False
        self.files_header = False
        self.folders_header = False
        temp_scope = StringIO()
        temp_files = StringIO()
        temp_folders = StringIO()

        #if reghive:
        #    try:
        #        reghive = (reghive).replace('/', '\\')
        #    except AttributeError:
        #        pass

        log.info(f'Start parsing {usercid}')

        try:
            with open(usercid, 'rb') as f:
                total = f.seek(0, os.SEEK_END)
                f.seek(0, 0)
                header = datstruct.HEADER(BytesIO(f.read(536)))
                version = header['Version']
                if header['syncTokenData_size']:
                    account = 'Personal'
                    csvwriter = csv.writer(temp_scope, escapechar='\\')
                    csvwriter.writerow(['scopeID', 'siteID', 'webID', 'listID', 'libraryType', 'spoPermissions', 'shortcutVolumeID', 'shortcutItemIndex'])
                    self.scope_header = True
                    syncTokenData = urllib.parse.unquote(header['syncTokenData'][:header['syncTokenData_size']].decode('utf-8'))
                    syncDict = dict(item.split("=") for item in syncTokenData.split(";"))
                    csvwriter.writerow([syncDict['ID'], '', '', '', '', ''])

                if version == '29':
                    chunk = 1048
                    BLOCK_CONSTANT = 1048
                    FOLDER_CONSTANT = 299
                    DELETE_CONSTANT = 1032
                    LSCOPE_CONSTANT = 208
                    LFOLDER_CONSTANT = 825
                    VAULT_CONSTANT = 320
                    ASCOPE_CONSTANT = 176

                elif version == '2a':
                    chunk = 1080
                    BLOCK_CONSTANT = 1080
                    FOLDER_CONSTANT = 331
                    DELETE_CONSTANT = 1064
                    LSCOPE_CONSTANT = 240
                    LFOLDER_CONSTANT = 857
                    VAULT_CONSTANT = 352
                    ASCOPE_CONSTANT = 208

                elif version == '2b':
                    chunk = 1080
                    BLOCK_CONSTANT = 1080
                    FOLDER_CONSTANT = 331
                    DELETE_CONSTANT = 1064
                    LSCOPE_CONSTANT = 240
                    LFOLDER_CONSTANT = 857
                    VAULT_CONSTANT = 352
                    ASCOPE_CONSTANT = 208

                elif version == '2c':
                    chunk = 1096
                    BLOCK_CONSTANT = 1096
                    FOLDER_CONSTANT = 347
                    DELETE_CONSTANT = 1080
                    LSCOPE_CONSTANT = 256
                    LFOLDER_CONSTANT = 873
                    VAULT_CONSTANT = 368
                    ASCOPE_CONSTANT = 224

                elif version == '2d':
                    chunk = 1104
                    BLOCK_CONSTANT = 1098
                    FOLDER_CONSTANT = 347
                    DELETE_CONSTANT = 1082
                    LSCOPE_CONSTANT = 258
                    LFOLDER_CONSTANT = 875
                    VAULT_CONSTANT = 370
                    ASCOPE_CONSTANT = 226

                elif version == '2e':
                    chunk = 1128
                    BLOCK_CONSTANT = 1128
                    FOLDER_CONSTANT = 371
                    DELETE_CONSTANT = 1112
                    LSCOPE_CONSTANT = 288
                    LFOLDER_CONSTANT = 905
                    VAULT_CONSTANT = 400
                    ASCOPE_CONSTANT = 256

                elif version == '2f':
                    chunk = 1128
                    BLOCK_CONSTANT = 1128
                    FOLDER_CONSTANT = 371
                    DELETE_CONSTANT = 1112
                    LSCOPE_CONSTANT = 288
                    LFOLDER_CONSTANT = 905
                    VAULT_CONSTANT = 400
                    ASCOPE_CONSTANT = 256

                elif version == '30':
                    chunk = 1152
                    BLOCK_CONSTANT = 1152
                    FOLDER_CONSTANT = 395
                    DELETE_CONSTANT = 1136
                    LSCOPE_CONSTANT = 312
                    LFOLDER_CONSTANT = 929
                    VAULT_CONSTANT = 424
                    ASCOPE_CONSTANT = 280

                elif version == '31':
                    chunk = 1160
                    BLOCK_CONSTANT = 1160
                    FOLDER_CONSTANT = 403
                    DELETE_CONSTANT = 1144
                    LSCOPE_CONSTANT = 320
                    LFOLDER_CONSTANT = 937
                    VAULT_CONSTANT = 432
                    ASCOPE_CONSTANT = 288

                elif version == '32':
                    chunk = 1160
                    BLOCK_CONSTANT = 1160
                    FOLDER_CONSTANT = 403
                    DELETE_CONSTANT = 1144
                    LSCOPE_CONSTANT = 320
                    LFOLDER_CONSTANT = 937
                    VAULT_CONSTANT = 432
                    ASCOPE_CONSTANT = 288

                elif version == '33':
                    chunk = 1160
                    BLOCK_CONSTANT = 1160
                    FOLDER_CONSTANT = 403
                    DELETE_CONSTANT = 1144
                    LSCOPE_CONSTANT = 320
                    LFOLDER_CONSTANT = 937
                    VAULT_CONSTANT = 432
                    ASCOPE_CONSTANT = 288

                elif version == '34':
                    chunk = 1160
                    BLOCK_CONSTANT = 1160
                    FOLDER_CONSTANT = 403
                    DELETE_CONSTANT = 1144
                    LSCOPE_CONSTANT = 320
                    LFOLDER_CONSTANT = 937
                    VAULT_CONSTANT = 432
                    ASCOPE_CONSTANT = 288

                elif version == '35':
                    chunk = 1176
                    BLOCK_CONSTANT = 1176
                    FOLDER_CONSTANT = 419
                    DELETE_CONSTANT = 1160
                    LSCOPE_CONSTANT = 336
                    LFOLDER_CONSTANT = 953
                    VAULT_CONSTANT = 448
                    ASCOPE_CONSTANT = 304

                elif version == '36':
                    chunk = 1232
                    BLOCK_CONSTANT = 1232
                    FOLDER_CONSTANT = 475
                    DELETE_CONSTANT = 1216
                    LSCOPE_CONSTANT = 392
                    LFOLDER_CONSTANT = 1009
                    VAULT_CONSTANT = 504
                    ASCOPE_CONSTANT = 360

                else:
                    if not gui:
                        print(f'Unknown dat verison: {version} (Please report issue)')
                    log.error(f'Unknown dat verison: {version} (Please report issue)')
                    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []

                if account == 'Personal':
                    uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
                else:
                    uuid4hex = re.compile(b'"({[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}},[0-9]*)"', re.I)
                f.seek(0)
                dir_index = []
                entries = re.finditer(uuid4hex, f.read())
                current = next(entries, total)
                while isinstance(current, re.Match):
                    s = current.start()
                    count = s
                    n_current = next(entries, total)
                    hash = ''
                    size = ''
                    ffoffset = s - 102
                    if version <= '29':
                        ffoffset = s - 94
                    f.seek(ffoffset)
                    count = f.tell()
                    ff = f.read(1)

                    if f.tell() == total:
                        break

                    f. seek(-1, 1)
                    #if version <= '29':
                    #    f.seek(15, 1)
                    #else:
                    #    f.seek(23, 1)
                    #DriveItemId = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    #ParentId = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                    #eTag = f.read(56).decode("utf-8").split('\u0000\u0000', 1)[0]
                    #f.seek(26, 1)
                    print(ff)
                    if ff == b'\x01':
                        data_type = 'File'
                        if version == '29':
                            block = datstruct.DAT_FILE_v29(BytesIO(f.read(chunk)))
                        elif version == '2a':
                            block = datstruct.DAT_FILE_v2a(BytesIO(f.read(chunk)))
                        elif version == '2b':
                            block = datstruct.DAT_FILE_v2b(BytesIO(f.read(chunk)))
                        elif version == '2c':
                            block = datstruct.DAT_FILE_v2c(BytesIO(f.read(chunk)))
                        elif version == '2d':
                            block = datstruct.DAT_FILE_v2d(BytesIO(f.read(chunk)))
                        elif version == '2e':
                            block = datstruct.DAT_FILE_v2e(BytesIO(f.read(chunk)))
                        elif version == '2f':
                            block = datstruct.DAT_FILE_v2f(BytesIO(f.read(chunk)))
                        elif version == '30':
                            block = datstruct.DAT_FILE_v30(BytesIO(f.read(chunk)))
                        elif version == '31':
                            block = datstruct.DAT_FILE_v31(BytesIO(f.read(chunk)))
                        elif version == '32':
                            block = datstruct.DAT_FILE_v32(BytesIO(f.read(chunk)))
                        elif version == '33':
                            block = datstruct.DAT_FILE_v33(BytesIO(f.read(chunk)))
                        elif version == '34':
                            block = datstruct.DAT_FILE_v34(BytesIO(f.read(chunk)))
                        elif version == '35':
                            block = datstruct.DAT_FILE_v35(BytesIO(f.read(chunk)))
                        elif version == '36':
                            block = datstruct.DAT_FILE_v36(BytesIO(f.read(chunk)))
                        else:
                            block = datstruct.DAT_FILE(BytesIO(f.read(chunk)))

                    elif ff == b'\x02':
                        data_type = 'Folder'
                        if int(version, 16) <= 44:
                            block = datstruct.DAT_FOLDER_v29_v2c(BytesIO(f.read(chunk)), FOLDER_CONSTANT)
                        else:
                            block = datstruct.DAT_FOLDER_v2d_v36(BytesIO(f.read(chunk)), FOLDER_CONSTANT)

                    elif ff == b'\x09':
                        data_type = 'Scope'
                        block = datstruct.DAT_LIBRARY_SCOPE(BytesIO(f.read(chunk)), LSCOPE_CONSTANT)
                        for key in self.rem_list:
                            try:
                                del block[key]
                            except Exception:
                                continue
                        block.update([('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    elif ff == b'\x0a':
                        data_type = 'Scope'
                        block = datstruct.DAT_LIBRARY_FOLDER(BytesIO(f.read(chunk)), LFOLDER_CONSTANT)
                        for key in self.rem_list:
                            try:
                                del block[key]
                            except Exception:
                                continue
                        block.update([('siteID', b''), ('webID', b'')])
                        block.move_to_end('listID', last=True)
                        block.update([('libraryType', ''), ('spoPermissions', ''), ('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    elif ff == b'\x0b':
                        data_type = 'Scope'
                        block = datstruct.DAT_VAULT(BytesIO(f.read(chunk)), VAULT_CONSTANT)
                        for key in self.rem_list:
                            try:
                                del block[key]
                            except Exception:
                                continue
                        block.update([('siteID', b''), ('webID', b''), ('listID', b''), ('libraryType', ''), ('spoPermissions', '')])
                        block.move_to_end('shortcutVolumeID', last=True)
                        block.move_to_end('shortcutItemIndex', last=True)

                    elif ff == b'\x0c':
                        data_type = 'Scope'
                        block = datstruct.DAT_ADDED_SCOPE(BytesIO(f.read(chunk)), ASCOPE_CONSTANT)
                        for key in self.rem_list:
                            try:
                                del block[key]
                            except Exception:
                                continue
                        block.update([('shortcutVolumeID', ''), ('shortcutItemIndex', '')])

                    else:
                        block = datstruct.DAT_BLOCK(BytesIO(f.read(chunk)), BLOCK_CONSTANT)
                        continue

                    for k, v in block.items():
                        if k in self.split_str:
                            block[k] = (v.split(b'\x00\x00')[0] + b'\x00').decode('utf-16le')
                        if k in self.int_to_bin:
                            block[k] = f'{int.from_bytes(v, byteorder="big"):032b}'
                        if k in self.int_to_hex:
                            block[k] = int.from_bytes(v, byteorder='big')
                        if k in self.bytes_to_hex:
                            block[k] = v.hex()
                        if k in self.bytes_to_str:
                            block[k] = v.decode('utf-8')
                        if k in self.id_format:
                            block[k] = self.format_id(v)

                    if data_type == 'File':
                        csvwriter = csv.writer(temp_files, escapechar='\\')
                        if version <= '2b':
                            self.merge_dicts(block, self.dict_1)
                        elif version >= '2c' and version <= '34':
                            self.merge_dicts(block, self.dict_2)
                            block['sharedItem'] = [*block['bitMask']][29]
                        elif version >= '35':
                            self.merge_dicts(block, self.dict_3)
                            block['sharedItem'] = [*block['bitMask']][29]
                        if not self.files_header:
                            csvwriter.writerow(dict(block))
                            self.files_header = True

                    if data_type == 'Folder':
                        csvwriter = csv.writer(temp_folders, escapechar='\\')
                        block['sharedItem'] = [*block['bitMask']][29]
                        if not self.folders_header:
                            csvwriter.writerow(dict(block))
                            self.folders_header = True

                    if data_type == 'Scope':
                        csvwriter = csv.writer(temp_scope, escapechar='\\')
                        if not self.scope_header:
                            csvwriter.writerow(dict(block))
                            self.scope_header = True

                    csvwriter.writerow(block.values())

                    if count % 30 == 0:
                        if gui:
                            progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                        else:
                            progress(count, total, status='Building folder list. Please wait....')
                    #if type == 'File':
                    #    if account == 'Personal':
                    #        hash = f'SHA1({f.read(20).hex()})'
                    #    else:
                    #        hash = f'quickXor({codecs.encode(f.read(20), "base64").decode("utf-8").rstrip()})'
                    #    if version <= '29':
                    #        f.seek(4, 1)
                    #    else:
                    #        f.seek(12, 1)
                    #    size = int.from_bytes(f.read(8), "little")
                    try:
                        buffer = n_current.start() - f.tell()
                    except AttributeError:
                        buffer = n_current - f.tell()
                    #name = unicode_strings(f.read(buffer), DriveItemId)
                    #if not dir_index:
                    #    input = {'ParentId': '',
                    #            'DriveItemId': ParentId,
                    #            'eTag': '',
                    #            'Type': 'Root Default',
                    #            'Name': 'User Folder',
                    #            'Size': '',
                    #            'Hash': '',
                    #            'Children': []
                    #            }
                    #    dir_index.append(input)
                    #input = {'ParentId': ParentId,
                    #        'DriveItemId': DriveItemId,
                    #        'eTag': eTag,
                    #        'Type': type,
                    #        'Name': name.split('\u0000', 1)[0],
                    #        'Size': size,
                    #        'Hash': hash,
                    #        'Children': []
                    #        }
                    #
                    #dir_index.append(input)
                    #
                    #if gui:
                    #    progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                    #else:
                    #    progress(count, total, status='Building folder list. Please wait....')
    
                    current = n_current
    
        except Exception as e:
            log.error(f'Unable to parse {usercid}. {e}')
            print(f'Unable to parse {usercid}. {e}')
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
        