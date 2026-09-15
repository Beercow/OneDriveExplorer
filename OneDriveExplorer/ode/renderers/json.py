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

import base64
import os
import json
import logging
import pandas as pd

log = logging.getLogger(__name__)


def print_json(cache, name, fus, odt, pretty, json_path):
    log.info('Started writing JSON file')

    if not os.path.exists(json_path):
        os.makedirs(json_path)

    if fus:
        cache["FileUsageSync"] = fus

    # Determine output filename before changing cache
    file_extension = os.path.splitext(name)[1][1:]

    if file_extension == 'previous':
        output_name = (
            os.path.basename(name).split('.')[0]
            + "_"
            + file_extension
            + "_OneDrive.json"
        )

    elif cache.get('Name') == 'Microsoft.ListSync.db':
        output_name = (
            os.path.basename(name).split('.')[0]
            + "_OneDrive_list_sync.json"
        )

    elif cache.get('Name') == 'Microsoft.FilesOnDemand.db':
        output_name = (
            os.path.basename(name).split('.')[0]
            + "_OneDrive_fod.json"
        )

    elif not odt.empty:
        output_name = (
            os.path.basename(name).split('.')[0]
            + "_thumbnails.json"
        )

    else:
        output_name = (
            os.path.basename(name).split('.')[0]
            + "_OneDrive.json"
        )

    # Convert thumbnails DataFrame to JSON-compatible Python object
    if not odt.empty:
        odt = odt.copy()

        odt["thumbnail"] = odt["thumbnail"].apply(
            lambda x: base64.b64encode(x).decode("ascii")
            if isinstance(x, bytes)
            else x
        )

        cache = odt.to_dict(orient="records")

    # Serialize everything once
    if pretty:
        json_object = json.dumps(
            cache,
            sort_keys=False,
            indent=4,
            separators=(',', ': ')
        )
    else:
        json_object = json.dumps(cache)

    if json_object == '{}':
        return

    output_path = os.path.join(json_path, output_name)

    with open(output_path, 'w', encoding='utf-8') as output:
        output.write(json_object)