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

import ast
import csv
import zipfile
from io import StringIO
import pandas as pd
import logging

log = logging.getLogger(__name__)


def load_project(zip_name, q, stop_event, tv, file_items):
    with zipfile.ZipFile(zip_name, 'r') as archive:
        filenames = archive.namelist()

        for filename in filenames:
            with archive.open(filename) as data:
                arc_name = archive.filename.replace('/', '\\')
                log.info(f'Importing {filename} from {arc_name} project.')
                detach_items = ['fileStatus', 'inRecycleBin']
                if '_OneDrive.csv' in filename:
                    send_data = []
                    csv_reader = csv.reader(StringIO(data.read().decode('utf8')))
                    header = next(csv_reader)
                    for row in csv_reader:
                        parent_id = row[0]
                        index = row[1]
                        iid = row[2]
                        text = row[3]
                        image = ast.literal_eval(row[4])[0]
                        values = tuple(ast.literal_eval(row[5]))
                        is_open = row[6]
                        try:
                            tags = ast.literal_eval(row[7])
                        except:
                            tags = row[7]
                        
                        try:
                            tv.insert(parent_id, index, iid=iid, text=text, image=image, values=values, open=is_open, tags=tags)
                        except Exception as e:
                            log.error(f'Unable to load {zip_name}. The following error has occured: {e}')
                            q.put(['done'])
                            
                        if any(any(detach_item in sub for sub in tv.item(iid)["values"]) for detach_item in detach_items):
                            file_items[parent_id].append(iid)
                            tv.detach(iid)

                if '_logs.csv' in filename:
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
            row = [tv.parent(child), 'end', child]
            row.extend(list(tv.item(child).values()))
            csvwriter.writerow(row)
            if child in file_items:
                for i in file_items[child]:
                    row = [child, 'end', i]
                    row.extend(list(tv.item(i).values()))
                    csvwriter.writerow(row)
            find_children(item=child)

    pb.configure(mode='indeterminate')
    pb.start()

    with zipfile.ZipFile(zip_name, 'w') as archive:
        count = 1
        string_buffer = StringIO()
        d = tv.get_children()
        for i in d:
            filename = f"{tv.item(i)['text'].split('.')[0][1:]}_OneDrive.csv"

            if filename in archive.namelist():
                filename = f"{tv.item(i)['text'].split('.')[0][1:]}({count})_OneDrive.csv"
                count += 1

            value_label['text'] = f"Saving {filename} to {zip_name}. Please wait...."
            log.info(f'Saving {filename} to {zip_name}.')
            csvwriter = csv.writer(string_buffer)
            csvwriter.writerow(['parent', 'index', 'iid', 'text', 'image', 'values', 'open', 'tags'])
            row = [tv.parent(i), 'end', i]
            row.extend(list(tv.item(i).values()))
            csvwriter.writerow(row)
            find_children(item=i)
            archive.writestr(filename, string_buffer.getvalue())
            string_buffer.truncate(0)
            string_buffer.seek(0)

        for key, value in user_logs.items():
            value_label['text'] = f"Saving {key} to {zip_name}. Please wait...."
            log.info(f'Saving {key} to {zip_name}.')
            df = value.model.df
            df.to_csv(string_buffer, index=False)

            if key in archive.namelist():
                new_key = key.rsplit('_', 1)
                key = f'{new_key[0]}({count})_{new_key[1]}'
                count += 1

            archive.writestr(key, string_buffer.getvalue())
            string_buffer.truncate(0)
            string_buffer.seek(0)

    pb.stop()
    value_label['text'] = "Project saved successfuly."
    pb.configure(mode='determinate')

