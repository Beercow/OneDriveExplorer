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
import json
import logging

log = logging.getLogger(__name__)


def print_json(cache, name, pretty, json_path):
    log.info('Started writing JSON file')

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
