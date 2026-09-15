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
import pandas as pd
import logging
from io import BytesIO
from PIL import Image

log = logging.getLogger(__name__)



def image_to_html(image_data, width=150, height=150):
    if image_data is None:
        return ""

    if isinstance(image_data, (bytearray, memoryview)):
        image_data = bytes(image_data)

    if not isinstance(image_data, bytes) or not image_data:
        return ""

    try:
        with Image.open(BytesIO(image_data)) as image:
            image_format = image.format.lower()

        mime_types = {
            "png": "image/png",
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "bmp": "image/bmp",
            "tiff": "image/tiff",
            "ico": "image/x-icon",
        }

        mime_type = mime_types.get(image_format)

        if not mime_type:
            return ""

        encoded = base64.b64encode(image_data).decode("ascii")
        src = f"data:{mime_type};base64,{encoded}"

        return (
            f'<img src="{src}" '
            f'class="thumbnail" '
            f'width="150">'
        )

    except Exception:
        return ""

def print_html(df, rbin_df, name, html_path, db_name, fus, odt):
    log.info('Started writing HTML file')

    if not os.path.exists(html_path):
        os.makedirs(html_path)

    if not df.empty:
        parent_col = 'parentResourceID' if 'parentResourceID' in df.columns else 'ParentFileSystemId'
        df = df.sort_values(by=['Level', parent_col, 'Type', 'FileSort', 'FolderSort', 'libraryType'],
                            ascending=[False, False, False, True, False, False])

        df = df.drop(['Level', 'FileSort', 'FolderSort'], axis=1)

    if not rbin_df.empty:
        df = pd.concat([df, rbin_df], ignore_index=True, axis=0)

    if not df.empty:
        df = df.apply(lambda x: x.fillna(0) if x.dtype == 'Int64' else x.fillna('') if x.dtype == 'object' else x)

    html_file = os.path.basename(name).split('.')[0]+"_OneDrive.html"
    fus_file = os.path.basename(name).split('.')[0]+"_FileUsageSync.html"
    odt_file = os.path.basename(name).split('.')[0]+"_thumbnails.html"
    file_extension = os.path.splitext(name)[1][1:]

    if db_name == 'Microsoft.ListSync.db':
        html_file = os.path.basename(name).split('.')[0]+"_OneDrive_list_sync.html"

    if db_name == 'Microsoft.FilesOnDemand.db':
        html_file = os.path.basename(name).split('.')[0]+"_OneDrive_fod.html"

    if file_extension == 'previous':
        html_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.html"
        fus_file = os.path.basename(name).split('.')[0]+"_"+file_extension+"_FileUsageSync.html"

    if not df.empty:
        output = open(html_path + '/' + html_file, 'w', encoding='utf-8')
        output.write(df.to_html(index=False))
        output.close()

    if not fus.empty:
        output = open(html_path + '/' + fus_file, 'w', encoding='utf-8')
        output.write(fus.to_html(index=False))
        output.close()

    if not odt.empty:
        odt_copy = odt.copy()
        odt_copy["thumbnail"] = odt_copy["thumbnail"].apply(image_to_html)
        
        output = open(html_path + '/' + odt_file, 'w', encoding='utf-8')

        output.write(
            """
            <script>
            document.addEventListener("dblclick", function(event) {
            
                if (event.target.tagName !== "IMG") {
                    return;
                }
            
                const dataUrl = event.target.src;
            
                if (!dataUrl.startsWith("data:image/")) {
                    return;
                }
            
                const parts = dataUrl.split(",");
            
                const mime = parts[0].match(/data:(.*?);base64/)[1];
                const binary = atob(parts[1]);
            
                const bytes = new Uint8Array(binary.length);
            
                for (let i = 0; i < binary.length; i++) {
                    bytes[i] = binary.charCodeAt(i);
                }
            
                const blob = new Blob([bytes], { type: mime });
                const blobUrl = URL.createObjectURL(blob);
            
                window.open(blobUrl, "_blank");
            
            });
            </script>
            """
            )
            
        output.write(odt_copy.to_html(escape=False, index=False))
        output.close()
