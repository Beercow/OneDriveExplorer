import os
import sys
import logging
import codecs
import pandas as pd
from dissect import cstruct
from datetime import datetime
import urllib.parse
from ode.utils import progress, progress_gui

log = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = f'{os.path.dirname(os.path.abspath(__file__))}/../..'


def from_unix_sec(_):
    try:
        return datetime.utcfromtimestamp(int(_)).strftime('%Y-%m-%d %H:%M:%S')

    except Exception:
        return datetime.utcfromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S')


def parse_dat(usercid, reghive, recbin, start, account, gui=False, pb=False, value_label=False):
    usercid = (usercid).replace('/', '\\')

    datstruct = cstruct.cstruct()
    DAT_DEF = f'{application_path}/ode/helpers/structures'
    datstruct.loadfile(DAT_DEF)

    int_to_bin = ['bitMask']
    int_to_hex = ['header', 'entry_offset', 'volumeID']
    bytes_to_str = ['resourceID', 'parentResourceID', 'eTag', 'parentScopeID', 'driveItemID', 'listID', 'scopeID', 'siteID', 'webID', 'syncTokenData']
    bytes_to_hex = ['serverHashDigest', 'localWaterlineData', 'localWriteValidationToken', 'localSyncTokenData', 'localCobaltHashAlgorithm']
    int_to_date = ['lastChange', 'serverLastChange', 'mediaDateTaken']
    split_str = ['fileName', 'folderName']

    if reghive:
        try:
            reghive = (reghive).replace('/', '\\')
        except AttributeError:
            pass

    log.info(f'Start parsing {usercid}. Registry hive: {reghive}')

    try:
        with open(usercid, 'rb') as f:
            total = f.seek(0, os.SEEK_END)
            f.seek(0, 0)
            header = datstruct.HEADER(f.read(536))
            version = hex(header.Version)[2:]

            if version == '29':
                chunk = 1048
                datstruct.load("""
                #define BLOCK_CONSTANT   1048
                #define FILE_CONSTANT    317
                #define FOLDER_CONSTANT  299
                #define DELETE_CONSTANT  1032
                #define LSCOPE_CONSTANT  208
                #define LFOLDER_CONSTANT 825
                #define UNKNOWN_CONSTANT 320
                """)

            elif version == '2a':
                chunk = 1080
                datstruct.load("""
                #define BLOCK_CONSTANT   1080
                #define FILE_CONSTANT    349
                #define FOLDER_CONSTANT  331
                #define DELETE_CONSTANT  1064
                #define LSCOPE_CONSTANT  240
                #define LFOLDER_CONSTANT 857
                #define UNKNOWN_CONSTANT 352
                """)

            elif version == '2b':
                chunk = 1080
                datstruct.load("""
                #define BLOCK_CONSTANT   1080
                #define FILE_CONSTANT    349
                #define FOLDER_CONSTANT  331
                #define DELETE_CONSTANT  1064
                #define LSCOPE_CONSTANT  240
                #define LFOLDER_CONSTANT 857
                #define UNKNOWN_CONSTANT 352
                """)

            elif version == '2c':
                chunk = 1096
                datstruct.load("""
                #define BLOCK_CONSTANT   1096
                #define FILE_CONSTANT    357
                #define FOLDER_CONSTANT  347
                #define DELETE_CONSTANT  1080
                #define LSCOPE_CONSTANT  256
                #define LFOLDER_CONSTANT 873
                #define UNKNOWN_CONSTANT 368
                """)

            elif version == '2d':
                chunk = 1104
                datstruct.load("""
                #define BLOCK_CONSTANT   1098
                #define FILE_CONSTANT    357
                #define FOLDER_CONSTANT  347
                #define DELETE_CONSTANT  1082
                #define LSCOPE_CONSTANT  258
                #define LFOLDER_CONSTANT 875
                #define UNKNOWN_CONSTANT 370
                """)

            elif version == '2e':
                chunk = 1128
                datstruct.load("""
                #define BLOCK_CONSTANT   1128
                #define FILE_CONSTANT    381
                #define FOLDER_CONSTANT  371
                #define DELETE_CONSTANT  1112
                #define LSCOPE_CONSTANT  288
                #define LFOLDER_CONSTANT 905
                #define UNKNOWN_CONSTANT 400
                """)

            elif version == '2f':
                chunk = 1128
                datstruct.load("""
                #define BLOCK_CONSTANT   1128
                #define FILE_CONSTANT    381
                #define FOLDER_CONSTANT  371
                #define DELETE_CONSTANT  1112
                #define LSCOPE_CONSTANT  288
                #define LFOLDER_CONSTANT 905
                #define UNKNOWN_CONSTANT 400
                """)

            elif version == '30':
                chunk = 1152
                datstruct.load("""
                #define BLOCK_CONSTANT   1152
                #define FILE_CONSTANT    405
                #define FOLDER_CONSTANT  395
                #define DELETE_CONSTANT  1136
                #define LSCOPE_CONSTANT  312
                #define LFOLDER_CONSTANT 929
                #define UNKNOWN_CONSTANT 424
                """)

            elif version == '31':
                chunk = 1160
                datstruct.load("""
                #define BLOCK_CONSTANT   1160
                #define FILE_CONSTANT    413
                #define FOLDER_CONSTANT  403
                #define DELETE_CONSTANT  1144
                #define LSCOPE_CONSTANT  320
                #define LFOLDER_CONSTANT 937
                #define UNKNOWN_CONSTANT 432
                """)

            elif version == '32':
                chunk = 1160
                datstruct.load("""
                #define BLOCK_CONSTANT   1160
                #define FILE_CONSTANT    413
                #define FOLDER_CONSTANT  403
                #define DELETE_CONSTANT  1144
                #define LSCOPE_CONSTANT  320
                #define LFOLDER_CONSTANT 937
                #define UNKNOWN_CONSTANT 432
                """)

            elif version == '33':
                chunk = 1160
                datstruct.load("""
                #define BLOCK_CONSTANT   1160
                #define FILE_CONSTANT    413
                #define FOLDER_CONSTANT  403
                #define DELETE_CONSTANT  1144
                #define LSCOPE_CONSTANT  320
                #define LFOLDER_CONSTANT 937
                #define UNKNOWN_CONSTANT 432
                """)

            elif version == '34':
                chunk = 1160
                datstruct.load("""
                #define BLOCK_CONSTANT   1160
                #define FILE_CONSTANT    413
                #define FOLDER_CONSTANT  403
                #define DELETE_CONSTANT  1144
                #define LSCOPE_CONSTANT  320
                #define LFOLDER_CONSTANT 937
                #define UNKNOWN_CONSTANT 432
                """)

            elif version == '35':
                chunk = 1176
                datstruct.load("""
                #define BLOCK_CONSTANT   1176
                #define FILE_CONSTANT    212
                #define FOLDER_CONSTANT  419
                #define DELETE_CONSTANT  1160
                #define LSCOPE_CONSTANT  336
                #define LFOLDER_CONSTANT 953
                #define UNKNOWN_CONSTANT 448
                """)

            elif version == '36':
                chunk = 1232
                datstruct.load("""
                #define BLOCK_CONSTANT   1232
                #define FILE_CONSTANT    268
                #define FOLDER_CONSTANT  475
                #define DELETE_CONSTANT  1216
                #define LSCOPE_CONSTANT  392
                #define LFOLDER_CONSTANT 1009
                #define UNKNOWN_CONSTANT 504
                """)

            else:
                if not gui:
                    print(f'Unknown dat verison: {version} (Please report issue)')
                log.error(f'Unknown dat verison: {version} (Please report issue)')
                return pd.DataFrame(), f.name

            dir_index = []
            scope = []

            if int(header.syncTokenData_size) > 0:
                syncTokenData = urllib.parse.unquote(header.syncTokenData[:int(header.syncTokenData_size)].decode('utf-8'))
                syncDict = dict(item.split("=") for item in syncTokenData.split(";"))
                input_data = {'ParentId': '',
                              'DriveItemId': syncDict['ID'],
                              'eTag': '',
                              'Type': 'Root Default',
                              'Name': 'User Folder',
                              'Size': '',
                              'Hash': '',
                              'Children': []
                              }

                dir_index.append(input_data)

            while True:
                count = f.tell()
                hash = ''
                size = ''
                status = ''
                lastChange = ''
                shared = '0'
                ff = f.read(1).hex()

                if f.tell() == total:
                    break

                f. seek(-1, 1)

                if ff == '01':
                    data_type = 'File'
                    if version == '29':
                        block = datstruct.DAT_FILE_v29(f.read(chunk))
                    elif version == '2a':
                        block = datstruct.DAT_FILE_v2a(f.read(chunk))
                    elif version == '2b':
                        block = datstruct.DAT_FILE_v2b(f.read(chunk))
                    elif version == '2c':
                        block = datstruct.DAT_FILE_v2c(f.read(chunk))
                    elif version == '2d':
                        block = datstruct.DAT_FILE_v2d(f.read(chunk))
                    elif version == '2e':
                        block = datstruct.DAT_FILE_v2e(f.read(chunk))
                    elif version == '2f':
                        block = datstruct.DAT_FILE_v2f(f.read(chunk))
                    elif version == '30':
                        block = datstruct.DAT_FILE_v30(f.read(chunk))
                    elif version == '31':
                        block = datstruct.DAT_FILE_v31(f.read(chunk))
                    elif version == '32':
                        block = datstruct.DAT_FILE_v32(f.read(chunk))
                    elif version == '33':
                        block = datstruct.DAT_FILE_v33(f.read(chunk))
                    elif version == '34':
                        block = datstruct.DAT_FILE_v34(f.read(chunk))
                    elif version == '35':
                        block = datstruct.DAT_FILE_v35(f.read(chunk))
                    elif version == '36':
                        block = datstruct.DAT_FILE_v36(f.read(chunk))
                    else:
                        block = datstruct.DAT_FILE(f.read(chunk))

                elif ff == '02':
                    data_type = 'Folder'
                    if int(version, 16) <= 44:
                        block = datstruct.DAT_FOLDER_v29_v2c(f.read(chunk))
                    else:
                        block = datstruct.DAT_FOLDER_v2d_v36(f.read(chunk))

                elif ff == '09':
                    if not dir_index:
                        data_type = 'Root Default'
                        name = 'User Folder'
                    else:
                        data_type = 'Root Shared'
                        name = 'Shared with user'
                    block = datstruct.DAT_LIBRARY_SCOPE(f.read(chunk))

                else:
                    block = datstruct.DAT_BLOCK(f.read(chunk))
                    continue

                for k, v in block._values.items():
                    if k in split_str:
                        block._values[k] = v.split('\x00', 1)[0]
                    if k in int_to_bin:
                        block._values[k] = f'{v:032b}'
                    if k in int_to_hex:
                        block._values[k] = hex(v)
                    if k in bytes_to_hex:
                        block._values[k] = v.hex()
                    if k in bytes_to_str:
                        block._values[k] = v.decode('utf-8').split('\x00', 1)[0]
                    if k in int_to_date:
                        block._values[k] = from_unix_sec(v)

                if data_type == 'File':
                    if account == 'Personal':
                        hash = f'SHA1({block.localHashDigest.hex()})'
                    else:
                        hash = f'quickXor({codecs.encode(block.localHashDigest, "base64").decode("utf-8").rstrip()})'
                    size = f'{block.size//1024 + 1:,} KB'
                    name = block.fileName
                    status = str(block.fileStatus)
                    if int(version, 16) >= 44:
                        lastChange = block.lastChange
                        shared = [*block.bitMask][29]

                if data_type == 'Folder':
                    name = block.folderName
                    status = str(block.folderStatus)

                if ff == '09':
                    if block.scopeID in scope:
                        continue
                    else:
                        scope.append(block.scopeID)

                    input_data = {'ParentId': '',
                                  'DriveItemId': block.scopeID,
                                  'eTag': '',
                                  'Type': data_type,
                                  'Name': name,
                                  'Size': '',
                                  'Hash': '',
                                  'Status': '',
                                  'Date_modified': '',
                                  'Shared': '',
                                  'Children': []
                                  }

                    dir_index.append(input_data)
                    continue

                input_data = {'ParentId': block.parentResourceID,
                              'DriveItemId': block.resourceID,
                              'eTag': block.eTag,
                              'Type': data_type,
                              'Name': name,
                              'Size': size,
                              'Hash': hash,
                              'Status': status,
                              'Date_modified': lastChange,
                              'Shared': shared,
                              'Children': []
                              }

                dir_index.append(input_data)

                if gui:
                    progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                else:
                    progress(count, total, status='Building folder list. Please wait....')

    except Exception as e:
#        log.error(e)
        return pd.DataFrame, usercid

    if not gui:
        print('\n')

    df = pd.DataFrame.from_records(dir_index)
    df['Date_modified'] = pd.to_datetime(df['Date_modified']).apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if not pd.isnull(x) else '')
    df = df.fillna('')

    return df, f.name
