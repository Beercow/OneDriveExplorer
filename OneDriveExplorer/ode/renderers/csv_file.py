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
import pandas as pd
import logging

log = logging.getLogger(__name__)


def print_csv(df, rbin_df, name, csv_path, comment, fus):
    log.info('Started writing CSV file')

    if not os.path.exists(csv_path):
        os.makedirs(csv_path)

    if not df.empty:
        df = df.sort_values(by=['Level', 'parentResourceID', 'Type', 'FileSort', 'FolderSort', 'libraryType'],
                            ascending=[False, False, False, True, False, False])

        df = df.drop(['Level', 'FileSort', 'FolderSort'], axis=1)

    if not rbin_df.empty:
        df = pd.concat([df, rbin_df], ignore_index=True, axis=0)

    csv_file = os.path.basename(name).split('.')[0]+"_OneDrive.csv"
    fus_file = os.path.basename(name).split('.')[0]+"_FileUsageSync.csv"

    file_extension = os.path.splitext(name)[1][1:]

    if file_extension == 'previous' and not csv_name:
        csv_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.csv"
        fus_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_FileUsageSync.csv"

    if not df.empty:
        with open(csv_path + '/' + csv_file, 'w', encoding='utf-8', newline='') as f:
            f.write(f'#{comment}\n')  # Add your comment here
            df.to_csv(f, index=False, encoding='utf-8')

    if not fus.empty:
        with open(csv_path + '/' + fus_file, 'w', encoding='utf-8', newline='') as f:
            fus.to_csv(f, index=False, encoding='utf-8')
