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

#import ctypes
import logging
import pandas as pd
import ode.parsers.recbin as find_deleted
from ode.utils import find_parent, parse_reg
#from ode.helpers.mft import live_hive

log = logging.getLogger(__name__)


def parse_onedrive(df, account=False, reghive=False, recbin=False, gui=False, pb=False, value_label=False):
    if df.empty:
        return df, pd.DataFrame()
    share_df = df.loc[(~df.ParentId.isin(df.DriveItemId)) & (~df.Type.str.contains('Root'))]
    share_list = list(set(share_df.ParentId))
    share_root = []

    for x in share_list:
        input = {'ParentId': '',
                 'DriveItemId': x,
                 'eTag': '',
                 'Type': 'Root Shared',
                 'Name': 'Shared with user',
                 'Size': '',
                 'Hash': '',
                 'Status': '',
                 'Date_modified': '',
                 'Shared': '',
                 'Children': [],
                 'Level': 1
                 }

        share_root.append(input)

    share_df = pd.DataFrame.from_records(share_root)
    df = pd.concat([df, share_df], ignore_index=True, axis=0)
    rbin_df = pd.DataFrame()

    if reghive:
        try:
            df, od_keys = parse_reg(reghive, account, df)

            if recbin:
                rbin = find_deleted.find_deleted(recbin, od_keys, account,
                                                 gui=gui, pb=pb,
                                                 value_label=value_label)
                rbin_df = pd.DataFrame.from_records(rbin)

        except Exception as e:
#            if PermissionError and ctypes.windll.shell32.IsUserAnAdmin():
#                value_label['text'] = f"Searching for {account}'s NTUSER.DAT. Please wait...."
#                pb.configure(mode='indeterminate')
#                pb.start()
#                reghive = live_hive(account)
#            else:
            log.warning(f'Unable to read registry hive! {e}')
            pass

    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    if 'Path' in df.columns:
        df['Level'] = df['Path'].str.split('\\\\').str.len()

    else:
        df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
        df['Level'] = df['Path'].str.len()
        df['Path'] = df['Path'].str.join('\\')

    return df, rbin_df
