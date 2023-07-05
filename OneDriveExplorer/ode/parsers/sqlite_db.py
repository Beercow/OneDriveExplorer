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

import logging
import codecs
import pandas as pd
import sqlite3
from ode.utils import find_parent, parse_reg


log = logging.getLogger(__name__)


def parse_sql(sql_dir, reghive=False):
    account = sql_dir.rsplit('\\', 1)[-1]

    log.info(f'Start parsing {account}. Registry hive: {reghive}')

    try:
        SyncEngineDatabase = sqlite3.connect(f'file:/{sql_dir}/SyncEngineDatabase.db?mode=ro', uri=True)

        try:
            scope_df = pd.read_sql_query("SELECT scopeID FROM od_ScopeInfo_Records", SyncEngineDatabase)
            scope_df.rename(columns={"scopeID": "DriveItemId"}, inplace=True)
            scope_df.insert(0, 'ParentId', '')
            scope_df.insert(2, 'eTage', '')
            scope_df.insert(3, 'Type', 'Root Default')
            scope_df.insert(4, 'Name', 'User Folder')
            scope_df.insert(5, 'Size', '')
            scope_df.insert(6, 'Hash', '')
            scope_df['Children'] = [list() for x in range(len(scope_df.index))]

            df_file = pd.read_sql_query("SELECT parentResourceID, resourceID, etag, fileName, size, localHashDigest FROM od_ClientFile_Records", SyncEngineDatabase)

            df_file.rename(columns={"parentResourceID": "ParentId",
                                    "resourceID": "DriveItemId",
                                    "etag": "eTag",
                                    "fileName": "Name",
                                    "size": "Size",
                                    "localHashDigest": "Hash"
                                    }, inplace=True)

            df_file.insert(3, 'Type', 'File')
            df_file['Children'] = [list() for x in range(len(df_file.index))]

            if account == 'Personal':
                df_file['Hash'] = df_file['Hash'].apply(lambda x: f'SHA1({x.hex()})')
            else:
                df_file['Hash'] = df_file['Hash'].apply(lambda x: f'quickXor({codecs.encode(x, "base64").decode("utf-8").rstrip()})')

            df_folder = pd.read_sql_query("SELECT parentResourceID, resourceID, etag, folderName FROM od_ClientFolder_Records", SyncEngineDatabase)

            df_folder.rename(columns={"parentResourceID": "ParentId",
                                      "resourceID": "DriveItemId",
                                      "etag": "eTag",
                                      "folderName": "Name"
                                      }, inplace=True)

            df_folder.insert(3, 'Type', 'Folder')
            df_folder.insert(5, 'Size', '')
            df_folder.insert(6, 'Hash', '')
            df_folder['Children'] = [list() for x in range(len(df_folder.index))]

            df = pd.concat([scope_df, df_folder, df_file], ignore_index=True, axis=0)

        except Exception as e:
            log.warning(f'Unable to parse {sql_dir}\SyncEngineDatabase.db. {e}')
            df = pd.DataFrame()

        SyncEngineDatabase.close()

    except sqlite3.OperationalError:
        log.info('SyncEngineDatabase.db does not exist')
        df = pd.DataFrame()

    try:
        SafeDelete = sqlite3.connect(f'file:/{sql_dir}/SafeDelete.db?mode=ro', uri=True)

        try:
            rbin_df = pd.read_sql_query("SELECT parentResourceId, resourceId, itemName, notificationTime FROM items_moved_to_recycle_bin", SafeDelete)

            rbin_df.rename(columns={"parentResourceId": "ParentId",
                                    "resourceId": "DriveItemId",
                                    "itemName": "Name",
                                    "notificationTime": "DeleteTimeStamp"
                                    }, inplace=True)

            rbin_df['DeleteTimeStamp'] = pd.to_datetime(rbin_df['DeleteTimeStamp'], unit='s').astype(str)
            rbin_df.insert(2, 'eTag', '')
            rbin_df.insert(3, 'Type', 'File - deleted')
            rbin_df.insert(5, 'Size', '')
            rbin_df.insert(6, 'Hash', '')
            rbin_df.insert(7, 'Path', '')
            rbin_df['Children'] = [list() for x in range(len(rbin_df.index))]
            rbin_df.insert(10, 'Level', '')

        except Exception as e:
            log.warning(f'Unable to parse {sql_dir}\SafeDelete.db. {e}')
            rbin_df = pd.DataFrame()

        SafeDelete.close()

    except sqlite3.OperationalError:
        log.info('SafeDelete.db does not exist')
        rbin_df = pd.DataFrame()

    if df.empty:
        return df, rbin_df

    if reghive:
        try:
            df, od_keys = parse_reg(reghive, account, df)

        except Exception as e:
            log.warning(f'Unable to read registry hive! {e}')
            pass

    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
    df['Level'] = df['Path'].str.len()
    df['Path'] = df['Path'].str.join('\\')

    rbin_df['Path'] = rbin_df.ParentId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\'))
    rbin_df['Level'] = rbin_df['Path'].str.len()
    rbin_df['Path'] = rbin_df['Path'].str.join('\\')

    return df, rbin_df
