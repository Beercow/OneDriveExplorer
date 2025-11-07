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
import re
import hashlib
import logging
import pandas as pd
import numpy as np
from Registry import Registry
import ode.parsers.recbin

log = logging.getLogger(__name__)

find_deleted = ode.parsers.recbin.DeleteProcessor()


class OneDriveParser:
    def __init__(self):
        pass

    def hash_file(self, file):
        BUF_SIZE = 65536
        sha1 = hashlib.sha1()

        try:
            with open(file, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)

            return sha1.hexdigest()
        except Exception:
            return ''

    def parse_reg(self, reghive, account, df):
        reg_handle = Registry.Registry(reghive)
        int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive')
        od_keys = reg_handle.open(f'SOFTWARE\\Microsoft\\OneDrive\\Accounts\\{account}\\Tenants')
        ac_keys = reg_handle.open('SOFTWARE\\Microsoft\\OneDrive\\Accounts')

        df['MountPoint'] = ''
        for providers in int_keys.subkeys():
            df.loc[(df.resourceID == providers.name()), ['MountPoint']] = [x.value() for x in list(providers.values()) if x.name() == 'MountPoint'][0]
            df.loc[(df.scopeID == providers.name()), ['MountPoint']] = [x.value() for x in list(providers.values()) if x.name() == 'MountPoint'][0]

        for x in [value for subkey in [acc2.values() for acc in ac_keys.subkeys() for acc2 in acc.subkeys() if acc2.name() == 'ScopeIdToMountPointPathCache'] for value in subkey]:
            if x.value() is not None:
                df.loc[df['resourceID'] == x.name(), 'MountPoint'] = x.value()
                df.loc[df['scopeID'] == x.name(), 'MountPoint'] = x.value()

        try:
            reghive.seek(0)
        except Exception:
            pass

        return df, od_keys

    def find_parent(self, x, id_name_dict, parent_dict):
        value = parent_dict.get(x, None)
        if value is None:
            return ''
        else:
            # In case there is a id without name.
            if id_name_dict.get(value, None) is None:
                return self.find_parent(value, id_name_dict, parent_dict) + x

        return self.find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))

    def create_cache(self, df_data, gui, directory, filename, hash, account, scopeID=[], od_settings=False):
        cache = {}
        final = []
        is_del = []
        df_scope = pd.DataFrame()
        rbin_df = pd.DataFrame()
        comment = None
        account = account
        allowed_keys = ['mountId', 'scopeID', 'siteID', 'webID', 'listID', 'tenantID', 'webURL', 'remotePath', 'MountPoint', 'spoPermissions', 'shortcutVolumeID', 'shortcutItemIndex']

        if od_settings:
            scopeID = od_settings.scopeID
            df_scope = od_settings.df_scope
            rbin_df = od_settings.rbin_df
            account = od_settings.account
            if hasattr(od_settings, "comment"):
                comment = od_settings.comment

        parent_col = 'parentResourceID' if 'parentResourceID' in df_data.columns else 'ParentFileSystemId'
        child_col = 'resourceID' if 'resourceID' in df_data.columns else 'FileSystemId'
        scope_col = 'scopeID' if 'scopeID' in df_data.columns else 'mountId'

        for row in df_data.sort_values(
            by=['Level', parent_col, 'Type', 'FileSort', 'FolderSort', 'libraryType'],
                ascending=[False, False, False, True, False, False]).to_dict('records'):
            if row['Type'] == 'File':
                try:
                    if 'ParentFileSystemId' in row:
                        file = {key: row[key] for key in ('ParentFileSystemId', 'FileSystemId', 'UniqueId', 'Path', 'Name', 'lastChange', 'size', 'PinState', 'fileStatus')}
                    elif 'diskCreationTime' in row:
                        file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'lastHydrationType', 'lastKnownPinState','spoPermissions', 'volumeID', 'itemIndex', 'diskLastAccessTime', 'diskCreationTime', 'lastChange', 'firstHydrationTime', 'lastHydrationTime', 'hydrationCount', 'size', 'localHashDigest', 'sharedItem', 'Media', 'Metadata', 'ListSync')}

                    elif 'diskLastAccessTime' in row:
                        file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'lastHydrationType', 'spoPermissions', 'volumeID', 'itemIndex', 'diskLastAccessTime', 'lastChange', 'firstHydrationTime', 'lastHydrationTime', 'hydrationCount', 'size', 'localHashDigest', 'sharedItem', 'Media', 'Metadata', 'ListSync')}

                    elif 'hydrationCount' in row:
                        file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'lastHydrationType', 'spoPermissions', 'volumeID', 'itemIndex', 'lastChange', 'firstHydrationTime', 'lastHydrationTime', 'hydrationCount', 'size', 'localHashDigest', 'sharedItem', 'Media', 'Metadata', 'ListSync')}

                    elif 'HydrationTime' in row:
                        file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'spoPermissions', 'volumeID', 'itemIndex', 'lastChange', 'HydrationTime', 'size', 'localHashDigest', 'sharedItem', 'Media', 'Metadata', 'ListSync')}

                    else:
                        file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'spoPermissions', 'volumeID', 'itemIndex', 'lastChange', 'size', 'localHashDigest', 'sharedItem', 'Media', 'Metadata', 'ListSync')}

                except Exception as e:
                    if gui:
                        log.error(f'Unable to read dataframe. Something went wrong. {e}')
                    else:
                        print(f'Unable to read dataframe. Something went wrong. {e}')
                    return {}

                folder = cache.setdefault(row[parent_col], {})
                folder.setdefault('Files', []).append(file)

            elif row['Type'] == 'Document' and row['resourceID'] not in scopeID:
                file = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'fileStatus', 'PermMask', 'Created', 'lastChange', 'SharedItem', 'size', 'localHashDigest', 'ListSync')}
                folder = cache.setdefault(row['parentResourceID'], {})
                folder.setdefault('Files', []).append(file)

            else:
                if 'Scope' in row['Type']:
                    if row[scope_col] not in scopeID:
                        continue
                    scope = {key: row[key] for key in row if key in allowed_keys}
                    folder = cache.get(row[scope_col], {})
                    temp = {**scope, **folder}
                    final.insert(0, temp)
                else:
                    if 'folderColor' in row:
                        try:
                            sub_folder = {key: row[key] for key in (
                                        'parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'folderStatus', 'spoPermissions', 'volumeID',
                                        'itemIndex', 'sharedItem', 'folderColor', 'ListSync')}
                        except Exception:
                            sub_folder = {key: row[key] for key in ('parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'folderStatus', 'Created', 'lastChange', 'SharedItem', 'folderColor', 'PermMask', 'ListSync')}

                    elif 'ParentFileSystemId' in row:
                        sub_folder = {key: row[key] for key in (
                                     'ParentFileSystemId', 'FileSystemId', 'UniqueId', 'Path', 'Name', 'lastChange', 'size', 'PinState', 'folderStatus')}
                    else:
                        sub_folder = {key: row[key] for key in (
                                    'parentResourceID', 'resourceID', 'eTag', 'Path', 'Name', 'folderStatus', 'spoPermissions', 'volumeID',
                                    'itemIndex', 'sharedItem', 'ListSync')}
                    if row[child_col] in scopeID:
                        scopeID.remove(row['resourceID'])
                        for s in df_scope.loc[df_scope[scope_col] == row['resourceID']].to_dict('records'):
                            scope = {key: s[key] for key in s if key in allowed_keys}
                            scope['MountPoint'] = row['MountPoint']
                            scope['spoPermissions'] = s['spoPermissions']
                            scope['shortcutVolumeID'] = s['shortcutVolumeID']
                            scope['shortcutItemIndex'] = s['shortcutItemIndex']
                        folder = cache.get(row['resourceID'], {})
                        temp = {**sub_folder, **folder}
                        scope.setdefault('Links', []).append(temp)
                        folder_merge = cache.setdefault(row['parentResourceID'], {})
                        folder_merge.setdefault('Scope', []).append(scope)
                    else:
                        folder = cache.get(row[child_col], {})
                        temp = {**sub_folder, **folder}
                        folder_merge = cache.setdefault(row[parent_col], {})
                        folder_merge.setdefault('Folders', []).append(temp)

        if not rbin_df.empty:
            for row in rbin_df.to_dict('records'):
                file = {key: row[key] for key in ('parentResourceId', 'resourceId', 'eTag', 'Path', 'Name', 'inRecycleBin', 'volumeId', 'fileId', 'DeleteTimeStamp', 'notificationTime', 'size', 'hash', 'deletingProcess')}

                # Nesting of deleted items
                # dfolder = dcache.setdefault(row['parentResourceId'], {})
                # dfolder.setdefault('Files', []).append(file)

                is_del.append(file)

            deleted = {'Type': 'Root Deleted',
                       'Children': ''
                       }

            deleted['Children'] = is_del
            final.append(deleted)

        if comment:
            cache = {"Path": comment['Path'],
                     "Name": comment['Name'],
                     "Hash": comment['Hash'],
                     "Account": comment['Account'],
                     "Data": '',
                     "FileUsageSync": ''
                     }
        else:
            cache = {"Path": directory,
                     "Name": filename,
                     "Hash": hash,
                     "Account": account,
                     "Data": '',
                     "FileUsageSync": ''
                     }

        cache['Data'] = final

        return cache

    # Generate scopeID list instead of passing
    def parse_onedrive(self, od_settings, file_path, reghive=False, recbin=False, od_list_sync=False, od_fod=False, gui=False, pb=False, value_label=False):
        online_cache = {}

        if isinstance(file_path, list):
            directory, f1 = os.path.split(file_path[0])
            directory, f2 = os.path.split(file_path[1])
            filename = [f1, f2]
            h = []
            for f in file_path:
                h.append(self.hash_file(f))
            hash = h
        elif os.path.isdir(file_path):
            directory = file_path
            filename = ['SyncEngineDatabase.db', 'SafeDelete.db']
            h = []
            for f in filename:
                h.append(self.hash_file(f'{file_path}\{f}'))
            hash = h
        else:
            directory, filename = os.path.split(file_path)
            hash = self.hash_file(file_path)

        if od_settings and not od_settings.df.empty:
            rbin_df = od_settings.rbin_df
            pd.set_option('display.max_columns', None)

            if od_list_sync:
                ocr_db = od_list_sync.ocr_db
            else:
                ocr_db = pd.DataFrame(columns=['resourceID', 'ListSync'])

            try:
                od_settings.df_scope['shortcutVolumeID'] = od_settings.df_scope['shortcutVolumeID'].apply(lambda x: '{:08x}'.format(x) if pd.notna(x) else '')
                od_settings.df_scope['shortcutVolumeID'] = od_settings.df_scope['shortcutVolumeID'].apply(lambda x: '{}{}{}{}-{}{}{}{}'.format(*x.upper()) if x else '')
            except Exception:
                pass

            if reghive:
                try:
                    od_settings.df, od_keys = self.parse_reg(reghive, od_settings.account, od_settings.df)

                    if gui:
                        pb.stop()
                        pb.configure(mode='indeterminate')
                        value_label['text'] = 'Building folder list. Please wait....'
                        pb.start()

                except Exception as e:
                    reghive = False
                    log.warning(f'Unable to read registry hive! {e}')
                    pass

            try:
                od_settings.df['MountPoint'] = od_settings.df['MountPoint'].where(pd.notna(od_settings.df['MountPoint']), '')
            except KeyError:
                od_settings.df['MountPoint'] = ''

            id_name_dict = {
                resource_id if resource_id is not None else od_settings.df.at[index, 'scopeID']:
                    od_settings.df.at[index, 'MountPoint'] if name is None else name if name is not None else ''
                for resource_id, name, index in zip(od_settings.df['resourceID'], od_settings.df['Name'], od_settings.df.index)
            }

            parent_dict = {resource_id if resource_id is not None else od_settings.df.at[index, 'scopeID']: '' if parent_id is None else parent_id
                           for resource_id, parent_id, index in zip(od_settings.df['resourceID'], od_settings.df['parentResourceID'], od_settings.df.index)}

            if 'Path' in od_settings.df.columns:
                od_settings.df['Level'] = od_settings.df['Path'].str.split('\\\\').str.len()

            else:
                od_settings.df['Path'] = od_settings.df.resourceID.apply(lambda x: self.find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
                od_settings.df['Level'] = od_settings.df['Path'].str.len()
                od_settings.df['Path'] = od_settings.df['Path'].str.join('\\')

            parent_resource_dict = od_settings.df[(od_settings.df['resourceID'].notnull()) & (od_settings.df['Type'] == 'Folder')].set_index('resourceID').apply(lambda x: x['Path'] + '\\' + x['Name'], axis=1).to_dict()

            for index, row in od_settings.rbin_df.iterrows():
                parent_resource_id = row['parentResourceId']
                if parent_resource_id in parent_resource_dict:
                    od_settings.rbin_df.at[index, 'Path'] = parent_resource_dict[parent_resource_id]

            if reghive and recbin:
                rbin = find_deleted.find_deleted(recbin, od_keys, od_settings.localHashAlgorithm, od_settings.rbin_df, gui=gui, pb=pb, value_label=value_label)
                lrbin_df = pd.DataFrame.from_records(rbin)
                od_settings.rbin_df = pd.concat([od_settings.rbin_df, lrbin_df], ignore_index=True, axis=0)

            od_settings.df['FileSort'] = ''
            od_settings.df['FolderSort'] = ''

            od_settings.df.loc[od_settings.df.Type == 'File', ['FileSort']] = od_settings.df['Name'].str.lower()
            od_settings.df.loc[od_settings.df.Type == 'Folder', ['FolderSort']] = od_settings.df['Name'].str.lower()

            od_settings.df['volumeID'].fillna(0, inplace=True)
            od_settings.df['itemIndex'].fillna(0, inplace=True)
            od_settings.df['shortcutVolumeID'].fillna(0, inplace=True)
            od_settings.df['shortcutItemIndex'].fillna(0, inplace=True)

            try:
                od_settings.df['volumeID'] = od_settings.df['volumeID'].apply(lambda x: '{:08x}'.format(x) if pd.notna(x) else '')
                od_settings.df['volumeID'] = od_settings.df['volumeID'].apply(lambda x: '{}{}{}{}-{}{}{}{}'.format(*x.upper()) if x else '')
                od_settings.df['shortcutVolumeID'] = od_settings.df['shortcutVolumeID'].apply(lambda x: '{:08x}'.format(x) if pd.notna(x) else '')
                od_settings.df['shortcutVolumeID'] = od_settings.df['shortcutVolumeID'].apply(lambda x: '{}{}{}{}-{}{}{}{}'.format(*x.upper()) if x else '')
            except Exception:
                pass

            if 'Metadata' in od_settings.df.columns:
                df = od_settings.df
            else:
                for df in [od_settings.df, ocr_db, od_settings.graphMetadata]:
                    df['resourceID_base'] = df['resourceID'].str.split('+').str[0]

                df = (
                    pd.merge(
                        od_settings.df,
                        ocr_db.drop(columns=['resourceID']),
                        on='resourceID_base',
                        how='outer'
                    )
                    .merge(
                        od_settings.graphMetadata.drop(columns=['resourceID']),
                        on='resourceID_base',
                        how='outer'
                    )
                )

                df.drop(columns=['resourceID_base'], inplace=True)

            df[['Type', 'Metadata', 'ListSync']] = df[['Type', 'Metadata', 'ListSync']].fillna('')

            online_cache = self.create_cache(df, gui, directory, filename, hash, None, [], od_settings)

        elif od_list_sync and not od_list_sync.df_list_sync.empty:
            od_list_sync.df_list_sync['Level'] = od_list_sync.df_list_sync['Path'].str.split('/').str.len()

            od_list_sync.df_list_sync['FileSort'] = ''
            od_list_sync.df_list_sync['FolderSort'] = ''
            od_list_sync.df_list_sync['MountPoint'] = ''

            od_list_sync.df_list_sync.loc[od_list_sync.df_list_sync.Type == 'Document', ['FileSort']] = od_list_sync.df_list_sync['Name'].str.lower()
            od_list_sync.df_list_sync.loc[od_list_sync.df_list_sync.Type == 'Folder', ['FolderSort']] = od_list_sync.df_list_sync['Name'].str.lower()

            od_list_sync.df_list_sync['scopeID'] = od_list_sync.df_list_sync['scopeID'].astype('str').fillna('')

            online_cache = self.create_cache(od_list_sync.df_list_sync, gui, directory, filename, hash, od_list_sync.account, od_list_sync.scopeID, od_settings)

            df = od_list_sync.df_list_sync
            rbin_df = pd.DataFrame()

        elif od_fod and not od_fod.df.empty:
            id_name_dict = {
                FileSystemId if FileSystemId is not None else od_fod.df.at[index, 'mountId']:
                    od_fod.df.at[index, 'MountPoint'] if name is None else name if name is not None else ''
                for FileSystemId, name, index in zip(od_fod.df['FileSystemId'], od_fod.df['Name'], od_fod.df.index)
            }

            parent_dict = {FileSystemId if FileSystemId is not None else od_fod.df.at[index, 'mountId']: '' if ParentFileSystemId is None else ParentFileSystemId
                           for FileSystemId, ParentFileSystemId, index in zip(od_fod.df['FileSystemId'], od_fod.df['ParentFileSystemId'], od_fod.df.index)}

            if 'Path' in od_fod.df.columns:
                od_fod.df['Level'] = od_fod.df['Path'].str.split('\\\\').str.len()

            else:
                od_fod.df['Path'] = od_fod.df.FileSystemId.apply(lambda x: self.find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
                od_fod.df['Level'] = od_fod.df['Path'].str.len()
                od_fod.df['Path'] = od_fod.df['Path'].str.join('\\')

            od_fod.df['FileSort'] = ''
            od_fod.df['FolderSort'] = ''

            od_fod.df.loc[od_fod.df.Type == 'File', ['FileSort']] = od_fod.df['Name'].str.lower()
            od_fod.df.loc[od_fod.df.Type == 'Folder', ['FolderSort']] = od_fod.df['Name'].str.lower()

            online_cache = self.create_cache(od_fod.df, gui, directory, filename, hash, od_fod.account, od_fod.scopeID, od_settings)

            df = od_fod.df
            rbin_df = pd.DataFrame()

        else:
            df = pd.DataFrame()
            rbin_df = pd.DataFrame()

        return online_cache, df, rbin_df
