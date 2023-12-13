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
        return x # may need to change to ''
    else:
        # Incase there is a id without name.
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
