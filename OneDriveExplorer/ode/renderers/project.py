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
import re
from io import StringIO
import pandas as pd
import logging
from ode.utils import progress_gui

log = logging.getLogger(__name__)


def load_project(zip_name, df_GraphMetadata_Records, q, stop_event, tv, file_items, pb, value_label):
    try:
        with zipfile.ZipFile(zip_name, 'r') as archive:
            filenames = archive.namelist()
            pb.configure(mode='determinate')
            pb.start()

            for filename in filenames:
                with archive.open(filename) as data:
                    arc_name = archive.filename.split('/')[-1]
                    log.info(f'Importing {filename} from {arc_name} project.')
                    detach_items = ['fileStatus', 'inRecycleBin']

                    if '_OneDrive.csv' in filename:
                        value_label['text'] = "Gathering metadata. Pleas wait..."
                        count = 0
                        send_data = []
                        df = pd.read_csv(data, low_memory=False, quotechar='"')
                        df.fillna('', inplace=True)
                        df_column = df['meta'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) and x.strip() != "" else None).apply(pd.Series)
                        df_Temp = pd.DataFrame(df_column)
                        df_GraphMetadata_Records = pd.concat([df_GraphMetadata_Records.astype(df_Temp.dtypes), df_Temp.astype(df_GraphMetadata_Records.dtypes)], ignore_index=True, axis=0).drop_duplicates(subset='resourceID')
                        df_GraphMetadata_Records.dropna(inplace=True)
                        total = len(df)

                        for row in df.to_dict('records'):
                            count += 1
                            try:
                                tags = ast.literal_eval(row['tags'])
                            except Exception:
                                tags = row['tags']
                            try:
                                tv.insert(row['parent'], row['index'], iid=row['iid'], text=row['text'], image=ast.literal_eval(row['image'])[0], values=tuple(ast.literal_eval(row['values'])), open=row['open'], tags=tags)
                            except Exception as e:
                                log.error(f'Unable to load {zip_name}. The following error has occured: {e}')
                                q.put(['done'])
                                return
                            if any(any(detach_item in sub for sub in tv.item(row['iid'])["values"]) for detach_item in detach_items):
                                file_items[row['parent']].append(row['iid'])
                                tv.detach(row['iid'])
                            if count % 20 == 0:
                                progress_gui(total, count, pb, value_label, status=f'Importing {filename} from {arc_name} project.')

                    if '_logs.csv' in filename:
                        value_label['text'] = f'Importing {filename} from {arc_name} project.'
                        pb.configure(mode='indeterminate')
                        pb.start()
                        send_data = []
                        df = pd.read_csv(data, dtype=str)
                        send_data.append(filename)
                        send_data.append(df)
                        q.put(send_data)

            if not df_GraphMetadata_Records.empty:
                df_GraphMetadata_Records['lastWriteCount'] = df_GraphMetadata_Records['lastWriteCount'].astype('Int64')
            q.put([df_GraphMetadata_Records])
    except Exception as e:
        log.error(f'Error importing {zip_name.split("/")[-1]}. {e}')

    q.put(['done'])


def save_project(tv, file_items, df_GraphMetadata_Records, zip_name, user_logs, pb, value_label):
    def find_children(count, item=''):
        children = tv.get_children(item)
        pattern = r'resourceID: |resourceId: '

        for child in children:
            count += 1
            row = [tv.parent(child), 'end', child]
            row.extend(list(tv.item(child).values()))
            csvwriter.writerow(row)

            if child in file_items:
                for i in file_items[child]:
                    count += 1
                    line_value = re.split(pattern, tv.item(i, 'values')[3])[1]
                    df_result = df_GraphMetadata_Records[df_GraphMetadata_Records['resourceID'] == line_value]
                    row = [child, 'end', i]
                    row.extend(list(tv.item(i).values()))
                    row.extend(df_result.to_dict(orient='records'))
                    csvwriter.writerow(row)
                    progress_gui(total, count, pb, value_label, status=f'Saving {filename} to {zip_name.split("/")[-1]}.')

            progress_gui(total, count, pb, value_label, status=f'Saving {filename} to {zip_name.split("/")[-1]}.')
            count = find_children(count, item=child)

        return count

    def get_total_items(tree, item):
        # Get the direct children of the current item
        children = tree.get_children(item)

        # Initialize the count with the direct children count
        count = len(children)

        # Recursively count items for each child
        for child in children:
            count += get_total_items(tree, child)

        return count

    total = get_total_items(tv, "")
    total += sum(len(value) for value in file_items.values())
    count = 0

    pb.configure(mode='determinate')
    pb.start()

    try:
        with zipfile.ZipFile(zip_name, 'w') as archive:
            file_count = 1
            string_buffer = StringIO()
            d = tv.get_children()

            for i in d:
                filename = f"{tv.item(i)['text'].split('.')[0][1:]}_OneDrive.csv"

                if filename in archive.namelist():
                    filename = f"{tv.item(i)['text'].split('.')[0][1:]}({file_count})_OneDrive.csv"
                    file_count += 1

                log.info(f'Saving {filename} to {zip_name}.')
                csvwriter = csv.writer(string_buffer)
                csvwriter.writerow(['parent', 'index', 'iid', 'text', 'image', 'values', 'open', 'tags', 'meta'])
                row = [tv.parent(i), 'end', i]
                row.extend(list(tv.item(i).values()))
                csvwriter.writerow(row)
                count = find_children(count, item=i)
                archive.writestr(filename, string_buffer.getvalue())
                string_buffer.truncate(0)
                string_buffer.seek(0)

            pb.configure(mode='indeterminate')
            pb.start()

            for key, value in user_logs.items():
                value_label['text'] = f"Saving {key} to {zip_name}. Please wait...."
                log.info(f'Saving {key} to {zip_name}.')
                df = value.model.df
                df.to_csv(string_buffer, index=False)

                if key in archive.namelist():
                    new_key = key.rsplit('_', 1)
                    key = f'{new_key[0]}({file_count})_{new_key[1]}'
                    file_count += 1

                archive.writestr(key, string_buffer.getvalue())
                string_buffer.truncate(0)
                string_buffer.seek(0)

    except Exception as e:
        log.error(f'Error saving {zip_name}: {e}')
        pb.stop()
        value_label['text'] = 'Error saving project.'
        pb.configure(mode='determinate')
        return

    pb.stop()
    value_label['text'] = "Project saved successfuly."
    pb.configure(mode='determinate')

