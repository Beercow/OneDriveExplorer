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
import logging
import codecs
import pandas as pd
from Registry import Registry
from ode.utils import unicode_strings, progress, progress_gui

log = logging.getLogger(__name__)


def parse_dat(usercid, reghive, recbin, start, gui=False, pb=False, value_label=False):
    usercid = (usercid).replace('/', '\\')

    if reghive:
        try:
            reghive = (reghive).replace('/', '\\')
        except AttributeError:
            pass

    log.info(f'Start parsing {usercid}. Registry hive: {reghive}')

    try:
        with open(usercid, 'rb') as f:
            total = len(f.read())
            f.seek(0)
            version = int(f.read(1).hex(), 16)
            uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
            personal = uuid4hex.search(f.read())
            if not personal:
                uuid4hex = re.compile(b'"({[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}},[0-9]*)"', re.I)
            f.seek(0)
            dir_index = []
            entries = re.finditer(uuid4hex, f.read())
            current = next(entries, total)
            while isinstance(current, re.Match):
                s = current.start()
                count = s
                n_current = next(entries, total)
                hash = ''
                size = ''
                ffoffset = s - 102
                if version <= 0x29:
                    ffoffset = s - 94
                f.seek(ffoffset)
                ff = f.read(1)
                if version <= 0x29:
                    f.seek(15, 1)
                else:
                    f.seek(23, 1)
                DriveItemId = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                ParentId = f.read(39).decode("utf-8").split('\u0000\u0000', 1)[0]
                eTag = f.read(56).decode("utf-8").split('\u0000\u0000', 1)[0]
                f.seek(26, 1)
                if ff == b'\x01':
                    type = 'File'
                else:
                    type = 'Folder'
                if type == 'File':
                    if personal:
                        hash = f'SHA1({f.read(20).hex()})'
                    else:
                        hash = f'quickXor({codecs.encode(f.read(20), "base64").decode("utf-8").rstrip()})'
                    if version <= 0x29:
                        f.seek(4, 1)
                    else:
                        f.seek(12, 1)
                    size = int.from_bytes(f.read(8), "little")
                try:
                    buffer = n_current.start() - f.tell()
                except AttributeError:
                    buffer = n_current - f.tell()
                name = unicode_strings(f.read(buffer), DriveItemId)
                if not dir_index:
                    if reghive and personal:
                        try:
                            reg_handle = Registry.Registry(reghive)
                            int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive\Personal')
                            for providers in int_keys.values():
                                if providers.name() == 'MountPoint':
                                    mountpoint = providers.value()
                        except Exception as e:
                            log.warning(f'Unable to read registry hive! {e}')
                            mountpoint = 'User Folder'
                    else:
                        mountpoint = 'User Folder'
                    input = {'ParentId': '',
                             'DriveItemId': ParentId,
                             'eTag': '',
                             'Type': 'Root Default',
                             'Name': mountpoint,
                             'Size': '',
                             'Hash': '',
                             'Children': []
                             }
                    dir_index.append(input)
                input = {'ParentId': ParentId,
                         'DriveItemId': DriveItemId,
                         'eTag': eTag,
                         'Type': type,
                         'Name': name.split('\u0000', 1)[0],
                         'Size': size,
                         'Hash': hash,
                         'Children': []
                         }

                dir_index.append(input)

                if gui:
                    progress_gui(total, count, pb, value_label, status='Building folder list. Please wait....')
                else:
                    progress(count, total, status='Building folder list. Please wait....')

                current = n_current

    except Exception as e:
        log.error(e)
        return pd.DataFrame, usercid, None

    print('\n')

    return pd.DataFrame.from_records(dir_index), f.name, personal
