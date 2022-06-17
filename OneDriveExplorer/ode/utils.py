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

import re
import sys
import logging

log = logging.getLogger(__name__)


def find_parent(x, id_name_dict, parent_dict):
    value = parent_dict.get(x, None)
    if value is None:
        return x
    else:
        # Incase there is a id without name.
        if id_name_dict.get(value, None) is None:
            return find_parent(value, id_name_dict, parent_dict) + x

    return find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))


def unicode_strings(buf, ouuid):
    uni_re = re.compile("(?:["
                        "\w"
                        "\s"
                        u"\u0020-\u007f"
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U00002500-\U00002BEF"  # chinese char
                        u"\U00002702-\U000027B0"
                        u"\U00002702-\U000027B0"
                        u"\U000024C2-\U0001F251"
                        u"\U0001f926-\U0001f937"
                        u"\U00010000-\U0010ffff"
                        u"\u2640-\u2642"
                        u"\u2600-\u2B55"
                        u"\u200d"
                        u"\u23cf"
                        u"\u23e9"
                        u"\u231a"
                        u"\ufe0f"  # dingbats
                        u"\u3030"
                        "]{1,}\x00[\uabab|\x00\x00]?)", flags=re.UNICODE)
    match = uni_re.search(buf.decode("utf-16", errors='ignore'))

    if match:
        try:
            return match.group()
        except Exception as e:
            log.warning(e)

    log.error(f'An error occured trying to find the name of {ouuid}. Raw Data:{buf}')
    return '??????????'


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f'[{bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def progress_gui(total, count, pb, value_label, status=False):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total))
        value_label['text'] = f"{status} {pb['value']}%"
