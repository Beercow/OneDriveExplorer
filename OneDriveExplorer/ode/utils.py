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
import re
import sys
import shutil
import urllib.request
from zipfile import ZipFile
import hashlib
import logging
from Registry import Registry
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = f'{os.path.dirname(os.path.abspath(__file__))}/..'

spec = spec_from_loader("schema", SourceFileLoader("schema", f"{application_path}/ode/helpers/schema"))
schema = module_from_spec(spec)
spec.loader.exec_module(schema)

log = logging.getLogger(__name__)

BASE_DIR = os.getcwd()
NEW_MAPS_URL = "https://github.com/Beercow/ODEFiles/archive/master.zip"
NEW_MAPS_DIR = os.path.join(BASE_DIR, "ODEFiles-master", "cstructs")
OLD_MAPS_DIR = os.path.join(BASE_DIR, "cstructs")


def update_from_repo(gui=False):
    print(f'\033[1;37mChecking for updated Cstructs at {NEW_MAPS_URL}...\n\033[1;0m')
    archive_path = os.path.join(BASE_DIR, "____master.zip")

    if os.path.exists(archive_path):
        os.remove(archive_path)

    urllib.request.urlretrieve(NEW_MAPS_URL, archive_path)

    with ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(BASE_DIR)

    os.remove(archive_path)

    if not os.path.exists(OLD_MAPS_DIR):
        os.makedirs(OLD_MAPS_DIR)

    new_maps = os.listdir(NEW_MAPS_DIR)

    new_local_maps = []
    updated_local_maps = []

    for new_map in new_maps:
        dest = os.path.join(OLD_MAPS_DIR, new_map)

        if not os.path.exists(dest):
            # new target
            new_local_maps.append(new_map)
        else:
            # current destination file exists, so compare to new
            with open(os.path.join(NEW_MAPS_DIR, new_map), 'rb') as new_file:
                new_sha = hashlib.sha1(new_file.read()).hexdigest()

            with open(dest, 'rb') as dest_file:
                dest_sha = hashlib.sha1(dest_file.read()).hexdigest()

            if new_sha != dest_sha:
                # updated file
                updated_local_maps.append(new_map)
        shutil.copy2(os.path.join(NEW_MAPS_DIR, new_map), dest)

    if new_local_maps or updated_local_maps:
        print("\n\033[1;31mUpdates found!\033[1;0m")

        if new_local_maps:
            print("\n\033[1;33mNew cstructs\033[1;0m")
            for new_local_map in new_local_maps:
                print(f"\033[1;37m{os.path.splitext(new_local_map)[0]}\033[1;0m")

        if updated_local_maps:
            print("\n\033[1;33mUpdated cstructs\033[1;0m")
            for updated_local_map in updated_local_maps:
                print(f"\033[1;37m{os.path.splitext(updated_local_map)[0]}\033[1;0m")

    else:
        print("\033[1;37mNo new cstructs available\033[1;0m")

    shutil.rmtree(os.path.join(BASE_DIR, "ODEFiles-master"))

    if gui:
        input('\n\nPress any key to exit')


def parse_reg(reghive, account, df):
    reg_handle = Registry.Registry(reghive)
    int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive')

    od_keys = reg_handle.open(f'SOFTWARE\\Microsoft\\OneDrive\\Accounts\\{account}\\Tenants')

    for providers in int_keys.subkeys():
        df.loc[(df.DriveItemId == providers.name().split('+')[0]), ['Name']] = [x.value() for x in list(providers.values()) if x.name() == 'MountPoint'][0]

    try:
        reghive.seek(0)
    except Exception:
        pass

    return df, od_keys


def find_parent(x, id_name_dict, parent_dict):
    value = parent_dict.get(x, None)
    if value is None:
        return x  # may need to change to ''
    else:
        # In case there is a id without name.
        if id_name_dict.get(value, None) is None:
            return find_parent(value, id_name_dict, parent_dict) + x

    return find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))


def unicode_strings(buf, ouuid):
    uni_re = re.compile("(?:["
                        "\w"
                        "\s"
                        u"\u0020-\u007f"
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U00002500-\U00002BEF"  # chinese char
                        u"\U00002702-\U000027B0"
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        u"\U0001f926-\U0001f937"
                        u"\U00010000-\U0010ffff"
                        u"\u2640-\u2642"
                        u"\u2600-\u2B55"
                        u"\u200d"
                        u"\u23cf"
                        u"\u23e9"
                        u"\u231a"
                        u"\ufe0f"  # dingbats
                        u"\u3030"
                        "]{1,}\x00[\uabab|\x00\x00]?)", flags=re.UNICODE)
    match = uni_re.search(buf.decode("utf-16", errors='ignore'))

    if match:
        try:
            return match.group()
        except Exception as e:
            log.warning(e)

    log.error(f'An error occured trying to find the name of {ouuid}. Raw Data:{buf}')
    return '??????????'


def change_dtype(df, df_name=None, schema_version=0):
    # Define mappings for dtype changes and fill values
    dtype_fill_map = {
        'df_scope': {
            'dtype_changes': {'Type': 'str', 'scopeID': 'str', 'siteID': 'str', 'webID': 'str', 'listID': 'str', 'spoPermissions': 'Int64', 'shortcutVolumeID': 'Int64', 'shortcutItemIndex': 'Int64'},
            'fill_values': {'Type': 'Scope', 'scopeID': '', 'siteID': '', 'webID': '', 'listID': '', 'spoPermissions': 0, 'shortcutVolumeID': 0, 'shortcutItemIndex': 0}
        },
        'df_files': {
            'dtype_changes': {'Type': 'str', 'parentResourceID': 'str', 'resourceID': 'str', 'eTag': 'str', 'Name': 'str', 'fileStatus': 'Int64', 'spoPermissions': 'Int64', 'volumeID': 'Int64', 'itemIndex': 'Int64', 'size': 'Int64', 'sharedItem': 'Int64', 'Width': 'Int64', 'Height': 'Int64', 'Duration': 'Int64'},
            'fill_values': {'Type': 'File', 'parentResourceID': '', 'resourceID': '', 'eTag': '', 'Name': '', 'fileStatus': 0, 'spoPermissions': 0, 'volumeID': 0, 'itemIndex': 0, 'size': 0, 'sharedItem': 0, 'Width': 0, 'Height': 0, 'Duration': 0}
        },
        'df_folders': {
            'dtype_changes': {'Type': 'str', 'parentScopeID': 'str', 'parentResourceID': 'str', 'resourceID': 'str', 'eTag': 'str', 'Name': 'str', 'folderStatus': 'Int64', 'spoPermissions': 'Int64', 'volumeID': 'Int64', 'itemIndex': 'Int64', 'sharedItem': 'Int64'},
            'fill_values': {'Type': 'Folder', 'parentScopeID': '', 'parentResourceID': '', 'resourceID': '', 'eTag': '', 'Name': '', 'folderStatus': 0, 'spoPermissions': 0, 'volumeID': 0, 'itemIndex': 0, 'sharedItem': 0}
        },
        'df_GraphMetadata_Records': {
            'dtype_changes': {'fileName': 'str', 'resourceID': 'str', 'graphMetadataJSON': 'str', 'spoCompositeID': 'str', 'createdBy': 'str', 'modifiedBy': 'str', 'lastWriteCount': 'Int64'},
            'fill_values': {'fileName': '', 'resourceID': '', 'graphMetadataJSON': '', 'spoCompositeID': '', 'createdBy': '', 'modifiedBy': '', 'lastWriteCount': 0}
        },
        'rbin_df': {
            'dtype_changes': {'Type': 'str', 'parentResourceId': 'str', 'resourceId': 'str', 'eTag': 'str', 'Path': 'str', 'Name': 'str', 'inRecycleBin': 'Int64', 'volumeId': 'Int64', 'fileId': 'str', 'DeleteTimeStamp': 'Int64', 'notificationTime': 'Int64', 'size': 'Int64', 'hash': 'str', 'deletingProcess': 'str'},
            'fill_values': {'Type': '', 'parentResourceId': '', 'resourceId': '', 'eTag': '', 'Path': '', 'Name': '', 'inRecycleBin': 0, 'volumeId': 0, 'fileId': '', 'DeleteTimeStamp': 0, 'notificationTime': 0, 'size': 0, 'hash': '', 'deletingProcess': ''}
        }
    }

    # Handle special cases
    if df_name == 'df_files' and schema_version >= 27:
        dtype_fill_map['df_files']['dtype_changes']['hydrationCount'] = 'Int64'
        dtype_fill_map['df_files']['fill_values']['hydrationCount'] = 0

    if df_name == 'df_scope' and schema_version > 8:
        dtype_fill_map['df_files']['dtype_changes']['tenantID'] = 'str'
        dtype_fill_map['df_files']['fill_values']['tenantID'] = ''
        dtype_fill_map['df_files']['dtype_changes']['webURL'] = 'str'
        dtype_fill_map['df_files']['fill_values']['webURL'] = ''
        dtype_fill_map['df_files']['dtype_changes']['remotePath'] = 'str'
        dtype_fill_map['df_files']['fill_values']['remotePath'] = ''
    
    if df_name == 'df_GraphMetadata_Records' and schema_version > 13:
        dtype_fill_map['df_files']['dtype_changes']['filePolicies'] = 'str'
        dtype_fill_map['df_files']['fill_values']['filePolicies'] = ''
        dtype_fill_map['df_files']['dtype_changes']['fileExtension'] = 'str'
        dtype_fill_map['df_files']['fill_values']['fileExtension'] = ''
        dtype_fill_map['df_files']['dtype_changes']['lastWriteCount'] = 'Int64'
        dtype_fill_map['df_files']['fill_values']['lastWriteCount'] = 0
    
    # Apply changes if df_name is recognized
    if df_name in dtype_fill_map:
        df.fillna(dtype_fill_map[df_name]['fill_values'], inplace=True)
        df = df.astype(dtype_fill_map[df_name]['dtype_changes'])

    return df


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def progress_gui(total, count, pb, value_label, status=False):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total), 1)
        value_label['text'] = f"{status} {pb['value']}%"


def permissions(_):
    perstr = []
    # Lists and Documents
    if _ & 0x0:
        perstr.append("EmptyMask")
    if _ & 0x1:
        perstr.append("ViewListItems")
    if _ & 0x2:
        perstr.append("AddListItems")
    if _ & 0x4:
        perstr.append("EditListItems")
    if _ & 0x8:
        perstr.append("DeleteListItems")
    if _ & 0x10:
        perstr.append("ApproveItems")
    if _ & 0x20:
        perstr.append("OpenItems")
    if _ & 0x40:
        perstr.append("ViewVersions")
    if _ & 0x80:
        perstr.append("DeleteVersions")
    if _ & 0x100:
        perstr.append("OverrideListBehaviors")
    if _ & 0x200:
        perstr.append("ManagePersonalViews")
    if _ & 0x800:
        perstr.append("ManageLists")
    if _ & 0x1000:
        perstr.append("ViewApplicationPages")
    # Web Level
    if _ & 0x10000:
        perstr.append("Open")
    if _ & 0x20000:
        perstr.append("ViewPages")
    if _ & 0x40000:
        perstr.append("AddAndCustomizePages")
    if _ & 0x80000:
        perstr.append("ApplyThemAndBorder")
    if _ & 0x100000:
        perstr.append("ApplyStyleSheets")
    if _ & 0x200000:
        perstr.append("ViewAnalyticsData")
    if _ & 0x400000:
        perstr.append("UseSSCSiteCreation")
    if _ & 0x800000:
        perstr.append("CreateSubsite")
    if _ & 0x1000000:
        perstr.append("CreateGroups")
    if _ & 0x2000000:
        perstr.append("ManagePermissions")
    if _ & 0x4000000:
        perstr.append("BrowseDirectories")
    if _ & 0x8000000:
        perstr.append("BrowseUserInfo")
    if _ & 0x10000000:
        perstr.append("AddDelPersonalWebParts")
    if _ & 0x20000000:
        perstr.append("UpdatePersonalWebParts")
    if _ & 0x40000000:
        perstr.append("ManageWeb")
    if _ & 0x1000000000:
        perstr.append("UseClientIntegration")
    if _ & 0x2000000000:
        perstr.append("UseRemoteInterfaces")
    if _ & 0x4000000000:
        perstr.append("ManageAlerts")
    if _ & 0x8000000000:
        perstr.append("CreateAlerts")
    if _ & 0x10000000000:
        perstr.append("EditPersonalUserInformation")
    # Special Permissions
    if _ & 0x4000000000000000:
        perstr.append("EnumeratePermissions")
    return perstr
