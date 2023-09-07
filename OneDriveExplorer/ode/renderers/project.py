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

import csv
import zipfile
from io import StringIO
import pandas as pd
from ode.parsers.csv_file import parse_csv
from ode.parsers.onedrive import parse_onedrive
import logging

log = logging.getLogger(__name__)


def load_project(zip_name, q, stop_event):
    with zipfile.ZipFile(zip_name, 'r') as archive:
        filenames = archive.namelist()

        for filename in filenames:
            with archive.open(filename) as data:
                arc_name = archive.filename.replace('/', '\\')
                log.info(f'Importing {filename} from {arc_name} project.')
                if '_OneDrive.csv' in filename:
                    send_data = []
                    string_buffer = StringIO(data.read().decode('utf8'))
                    df, name = parse_csv(string_buffer)
                    df, rbin_df = parse_onedrive(df)
                    string_buffer.truncate(0)
                    string_buffer.seek(0)
                    send_data.append(filename)
                    send_data.append(df)
                    q.put(send_data)

                if '_logs.csv' in filename:
                    q.put(['wait', filename])
                    send_data = []
                    df = pd.read_csv(data, dtype=str)
                    send_data.append(filename)
                    send_data.append(df)
                    q.put(send_data)

    q.put(['done'])


def save_project(tv, file_items, zip_name, user_logs, pb, value_label):
    def find_children(item=''):
        children = tv.get_children(item)
        for child in children:
            row = tv.item(child)['values']
            if row[6] == 'File - deleted':
                row.pop(0)
                row.pop(0)
                row.pop(7)
                row.insert(7, '')
                row.insert(7, '')
                row.insert(7, '')
                csvwriter.writerow(row)
            elif row[6] != 'Root Deleted':
                row.pop(0)
                row.pop(0)
                row.pop(10)
                csvwriter.writerow(row)
            if child in file_items:
                for i in file_items[child]:
                    row = tv.item(i)['values']
                    row.pop(0)
                    row.pop(0)
                    row.pop(10)
                    csvwriter.writerow(row)
            find_children(item=child)

    pb.configure(mode='indeterminate')
    pb.start()

    with zipfile.ZipFile(zip_name, 'w') as archive:
        string_buffer = StringIO()
        d = tv.get_children()
        for i in d:
            row = tv.item(i)['values']
            row.pop(0)
            row.pop(0)
            row.pop(10)
            filename = row[3].split('\\')[-1].split('.')[0] + '_OneDrive.csv'
            value_label['text'] = f"Saving {filename} to {zip_name}. Please wait...."
            log.info(f'Saving {filename} to {zip_name}.')
            csvwriter = csv.writer(string_buffer, delimiter=',')
            csvwriter.writerow(["ParentId", "DriveItemId", "eTag", "Name", "Type", "Size", "Hash", "Status", "Date_modified", "Shared", "Path", 'DeleteTimeStamp'])
            find_children(item=i)
            archive.writestr(filename, string_buffer.getvalue())
            string_buffer.truncate(0)
            string_buffer.seek(0)

        for key, value in user_logs.items():
            value_label['text'] = f"Saving {key} to {zip_name}. Please wait...."
            log.info(f'Saving {key} to {zip_name}.')
            df = value.model.df
            df.to_csv(string_buffer, index=False)
            archive.writestr(key, string_buffer.getvalue())
            string_buffer.truncate(0)
            string_buffer.seek(0)

    pb.stop()
    value_label['text'] = "Project saved successfuly."
    pb.configure(mode='determinate')

