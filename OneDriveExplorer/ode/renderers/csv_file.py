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
import pandas as pd
import logging

log = logging.getLogger(__name__)


def print_csv(df, rbin_df, name, csv_path, csv_name=False):
    log.info('Started writing CSV file')

    if not os.path.exists(csv_path):
        os.makedirs(csv_path)

    convert = {'fileStatus': 'Int64',
               'volumeID': 'Int64',
               'itemIndex': 'Int64',
               'sharedItem': 'Int64',
               'folderStatus': 'Int64'
              }

    df = df.astype(convert)

    df = df.sort_values(by=['Level', 'parentResourceID', 'Type', 'FileSort', 'FolderSort', 'libraryType'],
            ascending=[False, False, False, True, False, False])

    df = df.drop(['Level', 'FileSort', 'FolderSort'], axis=1)

    if not rbin_df.empty:
        df = pd.concat([df, rbin_df], ignore_index=True, axis=0)

    csv_file = os.path.basename(name).split('.')[0]+"_OneDrive.csv"

    if csv_name:
        csv_file = csv_name

    file_extension = os.path.splitext(name)[1][1:]

    if file_extension == 'previous' and not csv_name:
        csv_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.csv"

    df.to_csv(csv_path + '/' + csv_file, index=False)
