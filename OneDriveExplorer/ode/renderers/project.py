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

import ast
import base64
import csv
import os
import re
import tempfile
import zipfile
from io import StringIO
from PIL import ImageTk, Image
import pandas as pd
import logging
from ode.utils import progress_gui

log = logging.getLogger(__name__)


def load_images(zip_name):
    s_image = {}

    try:
        with zipfile.ZipFile(zip_name, "r") as archive:
            filenames = archive.namelist()

            filtered_list = [
                item
                for item in filenames
                if item.startswith("Images/")
                and not item.endswith("/")
                and os.path.basename(item).startswith("pyimage")
                and item.lower().endswith(".png")
            ]

            # Sort by the number in pyimage#
            sorted_list = sorted(
                filtered_list,
                key=lambda x: int(
                    os.path.splitext(
                        os.path.basename(x)
                    )[0][7:]
                )
            )

            for img in sorted_list:
                with archive.open(img) as data:
                    image = Image.open(data)
                    image.load()

                    photo = ImageTk.PhotoImage(image)

                    # pyimage68, pyimage69, etc.
                    image_name = os.path.splitext(
                        os.path.basename(img)
                    )[0]

                    s_image[image_name] = photo

            return s_image

    except Exception as e:
        log.error(
            f"Error loading images from "
            f"{zip_name.split('/')[-1]}. {e}"
        )


def load_project(zip_name, q, stop_event, tv, file_items, fus, file_usage_frame, pb, value_label):
    try:
        with zipfile.ZipFile(zip_name, 'r') as archive:
            filenames = archive.namelist()
            pb.configure(mode='determinate')
            pb.start()
            filenames = [item for item in filenames if not item.startswith('Images/')]

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

                    if '_FileUsageSync.csv' in filename:
                        value_label['text'] = f'Importing {filename} from {arc_name} project.'
                        pb.configure(mode='indeterminate')
                        pb.start()
                        fus.load_csv(data)
                        file_usage_frame.set_data(fus.df_data, filename.removesuffix("_FileUsageSync.csv"))
                        fus.df_data = pd.DataFrame()

                    if '_logs.csv' in filename:
                        value_label['text'] = f'Importing {filename} from {arc_name} project.'
                        pb.configure(mode='indeterminate')
                        pb.start()
                        send_data = []
                        df = pd.read_csv(data, dtype=str)
                        send_data.append(filename)
                        send_data.append(df)
                        q.put(send_data)

                    if '_thumbnails.csv' in filename:
                        value_label['text'] = f'Importing {filename} from {arc_name} project.'
                        pb.configure(mode='indeterminate')
                        pb.start()
                        send_data = []
                        send_data.append(filename)
                        send_data.append(data.read())
                        q.put(send_data)
                        

    except Exception as e:
        log.error(f'Error importing {zip_name.split("/")[-1]}. {e}')

    q.put(['done'])


def save_project(tv, file_items, zip_name, user_logs, root, fus, odt, pb, value_label):
    def find_children(count, item=''):
        children = tv.get_children(item)

        for child in children:
            count += 1
            row = [tv.parent(child), 'end', child]
            row.extend(list(tv.item(child).values()))
            csvwriter.writerow(row)

            if child in file_items:
                for i in file_items[child]:
                    count += 1
                    row = [child, 'end', i]
                    row.extend(list(tv.item(i).values()))
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

            py_images = root.tk.call("image", "names")

            for py_image in py_images:
                # Only save pyimage numbers > 67
                if not py_image.startswith("pyimage"):
                    continue
        
                try:
                    image_number = int(py_image[7:])
        
                    if image_number <= 67:
                        continue
        
                except ValueError:
                    continue
            
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        png_path = os.path.join(
                            temp_dir,
                            f"{py_image}.png"
                        )
        
                        # Tkinter writes the PhotoImage to a file
                        root.tk.call(
                            py_image,
                            "write",
                            png_path,
                            "-format",
                            "png"
                        )
        
                        # Read the PNG bytes
                        with open(png_path, "rb") as f:
                            png_data = f.read()
        
                        # Add directly to the ZIP
                        archive.writestr(
                            f"Images/{py_image}.png",
                            png_data
                        )
        
                except Exception as e:
                    log.warning(f"Unable to save {py_image}: {e}")

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

            if fus:
                for filename, records in fus.items():
                    csv_filename = f'{filename}_FileUsageSync.csv'

                    if records.empty:
                        continue

                    log.info(f'Saving {csv_filename} to {zip_name}.')

                    records.to_csv(
                        string_buffer,
                        index=False,
                        encoding="utf-8"
                    )
                
                    archive.writestr(
                        csv_filename,
                        string_buffer.getvalue()
                    )
                    
                    string_buffer.truncate(0)
                    string_buffer.seek(0)

            if not odt.empty:
                filename = '_thumbnails.csv'
                log.info(f'Saving {filename} to {zip_name}.')
                odt["thumbnail"] = odt["thumbnail"].apply(
                        lambda x: base64.b64encode(x).decode("ascii")
                        if isinstance(x, bytes)
                        else x
                    )
                
                odt.to_csv(string_buffer, index=False, encoding='utf-8')
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
