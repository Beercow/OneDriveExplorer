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
import json
import logging

log = logging.getLogger(__name__)


def print_json(df, rbin_df, name, pretty, json_path):
    log.info(f'Started writing JSON file')

    if not os.path.exists(json_path):
        os.makedirs(json_path)

    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}

    cache = {}
    final = []
    is_del = []

    df.loc[df.Type == 'File', ['FileSort']] = df['Name'].str.lower()
    df.loc[df.Type == 'Folder', ['FolderSort']] = df['Name'].str.lower()

    for row in df.sort_values(by=['Level', 'ParentId', 'Type', 'FileSort', 'FolderSort'], ascending=[False, False, False, True, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'Children'))

        if row['Type'] == 'File':
            folder = cache.setdefault(row['ParentId'], {})
            folder.setdefault('Children', []).append(file)
        else:
            folder = cache.get(row['DriveItemId'], {})
            temp = {**file, **folder}
            folder_merge = cache.setdefault(row['ParentId'], {})

            if 'Root' in row['Type']:
                final.insert(0, temp)
            else:
                folder_merge.setdefault('Children', []).append(temp)

    for row in rbin_df.to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'DeleteTimeStamp', 'Children'))
        is_del.append(file)

    cache = {'ParentId': '',
             'DriveItemId': '',
             'eTag': '',
             'Type': 'Root Drive',
             'Path': '',
             'Name': name,
             'Size': '',
             'Hash': '',
             'Children': ''
             }

    deleted = {'ParentId': '',
               'DriveItemId': '',
               'eTag': '',
               'Type': 'Root Deleted',
               'Path': '',
               'Name': 'Deleted Files',
               'Size': '',
               'Hash': '',
               'Children': ''
               }

    if is_del:
        deleted['Children'] = is_del
        final.append(deleted)

    cache['Children'] = final

    if pretty:
        json_object = json.dumps(cache,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(cache)

    json_file = os.path.basename(name).split('.')[0]+"_OneDrive.json"
    file_extension = os.path.splitext(name)[1][1:]

    if file_extension == 'previous':
        json_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.json"

    if json_path:
        json_file = json_path + '/' + json_file

    output = open(json_file, 'w')
    output.write(json_object)
    output.close()


def print_json_gui(cache, name, pretty, json_path):
    log.info(f'Started writing JSON file')

    if not os.path.exists(json_path):
        os.makedirs(json_path)

    if pretty:
        json_object = json.dumps(cache,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(cache)

    file_extension = os.path.splitext(name)[1][1:]

    if file_extension == 'previous':
        output = open(json_path + '\\' + os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.json", 'w')
    else:
        output = open(json_path + '\\' + os.path.basename(name).split('.')[0]+"_OneDrive.json", 'w')

    output.write(json_object)
    output.close()
