import os
import sys
import re
import json
from collections import namedtuple
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog
import threading
import pandas as pd
from PIL import ImageTk, Image
import time
from Registry import Registry
import keyboard
import logging
from io import StringIO as StringBuffer
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

log_capture_string = StringBuffer()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s, %(levelname)s, %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(log_capture_string)]
                    )

__author__ = "Brian Maloney"
__version__ = "2022.03.04"
__email__ = "bmmaloney97@gmail.com"

ASCII_BYTE = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
String = namedtuple("String", ["s", "offset"])
uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
found = []
folder_structure = []
reghive = None

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    import pyi_splash
    pyi_splash.update_text("PyInstaller is a great software!")
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if os.path.isfile('ode.settings'):
    with open("ode.settings", "r") as jsonfile:
        menu_data = json.load(jsonfile)
        jsonfile.close()
else:
    menu_data = json.loads('{"theme": "vista", "json": false, "pretty": false, "csv": false, "html": false, "path": ".", "hive": false}')
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


class quit:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.attributes("-toolwindow", 1)
        self.win.title("Please confirm")
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)

        self.frame = ttk.Frame(self.win, relief='groove')

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)

        self.label = ttk.Label(self.inner_frame,
                               text="Are you sure you want to exit?",
                               padding=5)

        self.yes = ttk.Button(self.inner_frame,
                              text="Yes",
                              takefocus=False,
                              command=lambda: self.btn1(root))

        self.no = ttk.Button(self.inner_frame,
                             text="No",
                             takefocus=False,
                             command=self.btn2)

        self.label.grid(row=0, column=0, columnspan=2)
        self.yes.grid(row=1, column=0, padx=5, pady=5)
        self.no.grid(row=1, column=1, padx=(0, 5), pady=5)

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def btn1(self, root):
        sys.exit()

    def btn2(self):
        self.root.unbind("<Configure>")
        self.win.destroy()

    def __callback(self):
        return

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2, y + h/2))


class preferences:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Preferences")
        self.win.iconbitmap(application_path + '/Images/controls.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_pref)

        self.json_save = tk.BooleanVar(value=menu_data['json'])
        self.json_pretty = tk.BooleanVar(value=menu_data['pretty'])
        self.csv_save = tk.BooleanVar(value=menu_data['csv'])
        self.html_save = tk.BooleanVar(value=menu_data['html'])
        self.auto_path = tk.StringVar(value=menu_data['path'])
        self.skip_hive = tk.BooleanVar(value=menu_data['hive'])

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.select_frame = ttk.Frame(self.inner_frame)
        self.path_frame = ttk.Frame(self.inner_frame)
        self.hive_frame = ttk.Frame(self.inner_frame)
        self.exit_frame = ttk.Frame(self.inner_frame)

        self.exit_frame.grid_rowconfigure(0, weight=1)
        self.exit_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0, sticky="nsew")
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.select_frame.grid(row=0, column=0, sticky="nsew")
        self.path_frame.grid(row=1, column=0, pady=25, sticky="nsew")
        self.hive_frame.grid(row=2, column=0, pady=(0, 25), sticky="nsew")
        self.exit_frame.grid(row=3, column=0, sticky="nsew")

        self.auto_json = ttk.Checkbutton(self.select_frame,
                                         text="Auto Save to JSON",
                                         var=self.json_save,
                                         offvalue=False,
                                         onvalue=True,
                                         takefocus=False,
                                         command=self.pretty_config
                                         )
        self.pretty = ttk.Checkbutton(self.select_frame,
                                      text="--pretty",
                                      var=self.json_pretty,
                                      offvalue=False,
                                      onvalue=True,
                                      takefocus=False
                                      )
        self.auto_csv = ttk.Checkbutton(self.select_frame,
                                        text="Auto Save to CSV",
                                        var=self.csv_save,
                                        offvalue=False,
                                        onvalue=True,
                                        takefocus=False
                                        )
        self.auto_html = ttk.Checkbutton(self.select_frame,
                                         text="Auto Save to HTML",
                                         var=self.html_save,
                                         offvalue=False,
                                         onvalue=True,
                                         takefocus=False
                                         )

        self.label = ttk.Label(self.path_frame, text="Auto Save Path")
        self.save_path = ttk.Entry(self.path_frame, width=30,
                                   textvariable=self.auto_path)
        self.btn = ttk.Button(self.path_frame, text='...', width=3,
                              takefocus=False, command=self.select_dir)

        self.reghive = ttk.Checkbutton(self.hive_frame,
                                       text="Disable loading user hive dialog",
                                       var=self.skip_hive,
                                       offvalue=False,
                                       onvalue=True,
                                       takefocus=False
                                       )

        self.save = ttk.Button(self.exit_frame, text="Save",
                               takefocus=False, command=self.save_pref)
        self.cancel = ttk.Button(self.exit_frame, text="Cancel",
                                 takefocus=False, command=self.close_pref)

        self.auto_json.grid(row=0, column=0, padx=5)
        self.pretty.grid(row=0, column=1, sticky="w")
        self.auto_csv.grid(row=1, column=0, columnspan=2, padx=5, sticky="w")
        self.auto_html.grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        self.label.grid(row=0, column=0, padx=5, sticky="w")
        self.save_path.grid(row=0, column=1)
        self.btn.grid(row=0, column=2, padx=5)
        self.reghive.grid(row=0, column=2, padx=5)
        self.save.grid(row=0, column=0, pady=5, sticky="e")
        self.cancel.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        if self.json_save.get() is False:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

        self.sync_windows()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/4, y + h/3))

    def pretty_config(self):
        if self.json_save.get() is True:
            self.pretty.configure(state="normal")
        else:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

    def select_dir(self):
        dir_path = filedialog.askdirectory(initialdir="\\",
                                           title="Auto Save Location")

        if dir_path:
            dir_path = dir_path.replace('/', '\\')
            self.auto_path.set(dir_path)

    def save_pref(self):
        menu_data['json'] = self.json_save.get()
        menu_data['pretty'] = self.json_pretty.get()
        menu_data['csv'] = self.csv_save.get()
        menu_data['html'] = self.html_save.get()
        menu_data['path'] = self.auto_path.get()
        menu_data['hive'] = self.skip_hive.get()
        if not os.path.exists(menu_data['path']):
            os.makedirs(menu_data['path'])
        with open("ode.settings", "w") as jsonfile:
            json.dump(menu_data, jsonfile)
        self.win.destroy()

    def close_pref(self):
        self.win.destroy()


class hive:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Load User Hive")
        self.win.iconbitmap(application_path + '/Images/OneDrive.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)\

        self.button_frame = ttk.Frame(self.inner_frame)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)
        self.button_frame.grid(row=2, column=0, columnspan=3)

        self.label_i = ttk.Label(self.inner_frame, image=warning_img)
        self.label = ttk.Label(self.inner_frame,
                               text="User's registry hive allows the mount points of the SyncEngines to be resolved.\n\nDo you want to provide a registry hive?\n")

        self.label_l = ttk.Label(self.inner_frame, text="Note:")

        self.label_r = ttk.Label(self.inner_frame, text="To bypass this dialog and skip loading hive, hold SHIFT when loading <UserCid>.dat\nThis dialog can also be bypassed in the Preferences settings.\n")

        self.yes = ttk.Button(self.button_frame,
                              text="Yes",
                              takefocus=False,
                              command=self.get_hive)

        self.no = ttk.Button(self.button_frame,
                             text="No",
                             takefocus=False,
                             command=self.close_hive)

        self.label_i.grid(row=0, column=0, rowspan=2)
        self.label.grid(row=0, column=1, columnspan=2, pady=(5, 0), sticky='w')
        self.label_l.grid(row=1, column=1, sticky='nw')
        self.label_r.grid(row=1, column=2, padx=5, sticky='w')
        self.yes.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='e')
        self.no.grid(row=0, column=1, pady=5, sticky='w')

        self.sync_windows()

    def __callback(self):
        return

    def close_hive(self):
        self.win.destroy()

    def get_hive(self):
        global reghive
        reghive = filedialog.askopenfilename(initialdir="/",
                                             title="Open",
                                             filetypes=(("Load user hive", "*.dat"),))
        if reghive:
            self.win.destroy()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/4, y + h/3))


class messages:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Messages")
        self.win.iconbitmap(application_path + '/Images/OneDrive.ico')
        self.win.minsize(400, 300)
        self.win.grab_set()
        self.win.focus_force()
        message['background'] = ''
        message['foreground'] = ''
        self.columns = ('Message Date', 'Message Type', 'Message')

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.frame.grid(row=0, column=0, sticky='nsew')
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(0, weight=1)

        self.tree_scroll = ttk.Scrollbar(self.inner_frame)
        self.tree = ttk.Treeview(self.inner_frame, columns=self.columns, show='headings', yscrollcommand=self.tree_scroll.set)
        self.tb_scroll = ttk.Scrollbar(self.inner_frame)
        self.tb = tk.Text(self.inner_frame, undo=False, height=10, yscrollcommand=self.tb_scroll.set)
        self.total = ttk.Label(self.inner_frame, text='Total messages:')
        self.clear = ttk.Button(self.inner_frame, text='Clear messages', takefocus=False, command=self.clear)
        self.export = ttk.Button(self.inner_frame, text='Export messages', takefocus=False, command=self.export)
        self.sg = ttk.Sizegrip(self.inner_frame)

        self.tree.heading('Message Date', text='Message Date', anchor='w')
        self.tree.heading('Message Type', text='Message Type', anchor='w')
        self.tree.heading('Message', text='Message', anchor='w')

        self.tree_scroll.config(command=self.tree.yview)
        self.tb_scroll.config(command=self.tb.yview)
        self.tb.config(state='disable')

        data = log_capture_string.getvalue().split('\n')
        for m in data:
            self.tree.insert("", "end", values=m.split(', '))

        self.tree.grid(row=0, column=0, columnspan=3, padx=(10, 0), pady=(10, 0), sticky='nsew')
        self.tree_scroll.grid(row=0, column=3, padx=(0, 10), pady=(10, 0), sticky="nsew")
        self.tb.grid(row=1, column=0, columnspan=3, padx=(10, 0), pady=(5, 10), sticky='nsew')
        self.tb_scroll.grid(row=1, column=3, padx=(0, 10), pady=(5, 10), sticky="nsew")
        self.total.grid(row=2, column=0, padx=(10, 0), pady=(0, 5), stick='w')
        self.clear.grid(row=2, column=1, padx=5, pady=(0, 5), stick='e')
        self.export.grid(row=2, column=2, pady=(0, 5), stick='e')
        self.sg.grid(row=2, column=3, stick='se')
        self.sync_windows()
        self.tree.bind('<<TreeviewSelect>>', self.select)
        self.mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
        self.total['text'] = f'Total messages: {self.mcount}'

    def select(self, event=None):
        self.tb.config(state='normal')
        self.tb.delete('1.0', tk.END)
        curItem = self.tree.selection()
        values = self.tree.item(curItem, 'values')
        self.tb.insert(tk.END, values[2])
        self.tb.config(state='disable')

    def clear(self):
        log_capture_string.truncate(0)
        log_capture_string.seek(0)
        self.tree.delete(*self.tree.get_children())
        mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
        self.total['text'] = f'Total messages: {mcount}'
        message['text'] = mcount
        message['background'] = ''
        message['foreground'] = ''

    def export(self):
        path = filedialog.askdirectory(initialdir="/")
        if path:
            ids = self.tree.get_children()
            excel_name = path + '\\OneDriveExplorerMessages_' + datetime.now().strftime("%Y-%m-%dT%H%M%S.xlsx")
            lst = []
            for id in ids:
                row = self.tree.item(id, 'values')
                lst.append(row)
            df = pd.DataFrame.from_records(lst, columns=['Message Data',
                                                         'Message Type',
                                                         'Message'])

            try:
                writer = pd.ExcelWriter(excel_name)
                df.to_excel(writer, 'OneDriveExplorer Messages', index=False)
                writer.save()
                export_result(self.win, excel_name)
            except Exception as e:
                logging.error(e)
                export_result(self.win, e, failed=True)
                self.tree.delete(*self.tree.get_children())
                data = log_capture_string.getvalue().split('\n')
                for m in data:
                    self.tree.insert("", "end", values=m.split(', '))
                mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
                self.total['text'] = f'Total messages: {mcount}'
                message['text'] = mcount

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.win.geometry("+%d+%d" % (x, y))


class export_result:
    def __init__(self, root, excel_name, failed=False):
        self.root = root
        self.excel_name = excel_name
        self.failed = failed
        self.win = tk.Toplevel(self.root)
        if self.failed:
            self.win.title("Export failed!")
        else:
            self.win.title("Export successful!")
        self.win.iconbitmap(application_path + '/Images/OneDrive.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)

        self.label_i = ttk.Label(self.inner_frame, image=info_img)
        self.label = ttk.Label(self.inner_frame, text=f'Messages exported to:\n\n{self.excel_name}')
        if self.failed:
            self.label_i['image'] = error_img
            self.label['text'] = f'Messages failed to export.\n\n{self.excel_name}'
        self.btn = ttk.Button(self.inner_frame, text='OK', takefocus=False, command=self.ok)

        self.label_i.grid(row=0, column=0)
        self.label.grid(row=0, column=1, padx=(0, 5))
        self.btn.grid(row=1, column=0, columnspan=2, pady=5)

        self.sync_windows()

    def ok(self):
        self.win.destroy()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2, y + h/2))


def search(item=''):
    query = search_entry.get()
    if len(query) == 0:
        return
    children = tv.get_children(item)
    for child in children:
        for x in tv.item(child)['values']:
            if query.lower() in str(x).lower():
                tv.see(child)
                tv.item(child, tags="yellow")
                found.append(child)
        search(item=child)


def clear_search():
    for hit in found:
        tv.item(hit, tags=())
    found.clear()
    if len(tv.selection()) > 0:
        tv.selection_remove(tv.selection()[0])


def unicode_strings(buf, n=1):
    reg = rb"((?:[%s]\x00){%d,}\x00\x00\xab)" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    if match:
        try:
            return match.group()[:-3].decode("utf-16"), match.start()
        except Exception as e:
            logging.warning(e)
    logging.warning('Name was not found!')
    return '??????????', '??????????'


def clear_all():
    tv.delete(*tv.get_children())
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    file_menu.entryconfig("Unload all folders", state='disable')
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")


def progress(total, count, ltext):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total))
        value_label['text'] = f"{ltext} {pb['value']}%"


def parse_dat(usercid, reghive, start):
    logging.info(f'Start pasrsing {usercid}. Registry hive: {reghive}')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    with open(usercid, 'rb') as f:
        total = len(f.read())
        f.seek(0)
        uuid4hex = re.compile(b'([A-F0-9]{16}![0-9]*\.[0-9]*)')
        personal = uuid4hex.search(f.read())
        if not personal:
            uuid4hex = re.compile(b'"({[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}},[0-9]*)"', re.I)
        f.seek(0)
        df = pd.DataFrame(columns=['ParentId',
                                   'DriveItemId',
                                   'eTag',
                                   'Type',
                                   'Name',
                                   'Size',
                                   'Children'])
        dir_index = []
        for match in re.finditer(uuid4hex, f.read()):
            s = match.start()
            eTag = match.group(1).decode("utf-8")
            count = s
            diroffset = s - 39
            objoffset = s - 78
            f.seek(objoffset)
            ouuid = f.read(32).decode("utf-8").strip('\u0000')
            f.seek(diroffset)
            duuid = f.read(32).decode("utf-8").strip('\u0000')
            name, name_s = unicode_strings(f.read(400))
            try:
                sizeoffset = diroffset + 24 + name_s
                f.seek(sizeoffset)
                size = int.from_bytes(f.read(8), "little")
            except:
                size = name_s
                f.seek(diroffset + 32)
                logging.error(f'An error occured trying to find the name of {ouuid}. Raw Data:{f.read(400)}')
            if not dir_index:
                if reghive and personal:
                    try:
                        reg_handle = Registry.Registry(reghive)
                        int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive\Personal')
                        for providers in int_keys.values():
                            if providers.name() == 'MountPoint':
                                mountpoint = providers.value()
                    except Exception as e:
                        logging.warning(f'Unable to read registry hive! {e}')
                        mountpoint = 'User Folder'
                else:
                    mountpoint = 'User Folder'
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'eTag': eTag,
                         'Type': 'Root Default',
                         'Name': mountpoint,
                         'Size': '',
                         'Children': []
                         }
                dir_index.append(input)
            input = {'ParentId': duuid,
                     'DriveItemId': ouuid,
                     'eTag': eTag,
                     'Type': 'File',
                     'Name': name,
                     'Size': size,
                     'Children': []
                     }

            dir_index.append(input)
            progress(total, count, 'Building folder list. Please wait....')

    df = pd.DataFrame.from_records(dir_index)
    df.loc[(df.DriveItemId.isin(df.ParentId)) | (df.Size == 2880154368), ['Type', 'Size']] = ['Folder', '']
    df.at[0, 'Type'] = 'Root Default'
    parse_onederive(f.name, df, start, dat=True, reghive=reghive)


def parse_json(filename):
    logging.info(f'Started parsing {filename.name}')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    pb.configure(mode='indeterminate')
    value_label['text'] = "Building tree. Please wait..."
    pb.start()
    parent_child(json.load(filename))
    pb.stop()
    pb.configure(mode='determinate')
    value_label['text'] = 'Complete'
    filename.close()
    mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
    message['text'] = mcount
    if "INFO," in log_capture_string.getvalue():
        message['background'] = ''
        message['foreground'] = ''
    if "WARNING," in log_capture_string.getvalue():
        message['background'] = 'yellow'
        message['foreground'] = 'black'
    if "ERROR," in log_capture_string.getvalue():
        message['background'] = 'red'
        message['foreground'] = ''
    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")
    rebind()


def parse_csv(filename, start):
    logging.info(f'Started parsing {filename.name}')
    start = time.time()
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    df = pd.read_csv(filename,
                     usecols=['ParentId', 'DriveItemId', 'eTag', 'Type', 'Name', 'Size'], dtype=str)
    df['Children'] = pd.Series([[] for x in range(len(df.index))])
    df = df.fillna('')
    parse_onederive(filename.name, df, start)


def find_parent(x, id_name_dict, parent_dict):
    value = parent_dict.get(x, None)
    if value is None:
        return x
    else:
        # Incase there is a id without name.
        if id_name_dict.get(value, None) is None:
            return find_parent(value, id_name_dict, parent_dict) + x

    return find_parent(value, id_name_dict, parent_dict) + "\\\\" + str(id_name_dict.get(value))


def parse_onederive(name, df, start, dat=False, reghive=False):
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Level'] = df.DriveItemId.apply(lambda x: len(find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\')))

    share_df = df.loc[(df.Level == 1) & (~df.ParentId.isin(df.DriveItemId)) & (~df.Type.str.contains('Root'))]
    share_list = list(set(share_df.ParentId))
    share_root = []
    for x in share_list:
        input = {'ParentId': '',
                 'DriveItemId': x,
                 'eTag': '',
                 'Type': 'Root Shared',
                 'Name': 'Shared with user',
                 'Size': '',
                 'Children': [],
                 'Level': 1
                 }
        share_root.append(input)
    share_df = pd.DataFrame.from_records(share_root)
    df = pd.concat([df, share_df], ignore_index=True, axis=0)

    if reghive:
        try:
            reg_handle = Registry.Registry(reghive)
            int_keys = reg_handle.open('SOFTWARE\\SyncEngines\\Providers\\OneDrive')
            for providers in int_keys.subkeys():
                df.loc[(df.DriveItemId == providers.name().split('+')[0]), ['Name']] = [x.value() for x in list(providers.values()) if x.name() =='MountPoint'][0]
        except Exception as e:
            logging.warning(f'Unable to read registry hive! {e}')
            pass

    try:
        file_count = df.Type.value_counts()['File']
    except KeyError:
        logging.warning("KeyError: 'File'")
        file_count = 0
    try:
        folder_count = df.Type.value_counts()['Folder']
    except KeyError:
        logging.warning("KeyError: 'Folder'")
        folder_count = 0

    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}

    cache = {}
    final = []

    for row in df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[False, False, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Name', 'Size', 'Children'))
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

    cache = {'ParentId': '',
             'DriveItemId': '',
             'eTag': '',
             'Type': 'Root Drive',
             'Name': name,
             'Size': '',
             'Children': ''
             }
    cache['Children'] = final

    pb.configure(mode='indeterminate')
    value_label['text'] = "Building tree. Please wait..."
    pb.start()
    parent_child(cache)
    pb.stop()
    pb.configure(mode='determinate')

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")

    if menu_data['json'] and dat:
        print_json(cache, name)

    if menu_data['csv'] and dat:
        print_csv(df, name)

    if menu_data['html'] and dat:
        print_html(df, name)

    pb['value'] = 0
    value_label['text'] = f'{file_count} file(s), {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds'
    if len(tv.get_children()) > 0:
        file_menu.entryconfig("Unload all folders", state='normal')
    mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
    message['text'] = mcount
    if "INFO," in log_capture_string.getvalue():
        message['background'] = ''
        message['foreground'] = ''
    if "WARNING," in log_capture_string.getvalue():
        message['background'] = 'yellow'
        message['foreground'] = 'black'
    if "ERROR," in log_capture_string.getvalue():
        message['background'] = 'red'
        message['foreground'] = ''
    rebind()


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("", "end", image=root_drive_img, text=d['Name'], values=(d['ParentId'], d['DriveItemId'], d['eTag'], d['Name'], d['Type'], d['Size'], len(d['Children'])))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        if c['Type'] == 'Folder':
            parent_child(c, tv.insert(parent_id, 0, image=folder_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['eTag'], c['Name'], c['Type'], c['Size'], len(c['Children']))))
        elif c['Type'] == 'Root Default':
            parent_child(c, tv.insert(parent_id, 0, image=default_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['eTag'], c['Name'], c['Type'], c['Size'], len(c['Children']))))
        elif c['Type'] == 'Root Shared':
            parent_child(c, tv.insert(parent_id, "end", image=shared_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['eTag'], c['Name'], c['Type'], c['Size'], len(c['Children']))))
        else:
            parent_child(c, tv.insert(parent_id, "end", image=file_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['eTag'], c['Name'], c['Type'], c['Size'], len(c['Children']))))
        root.update_idletasks()


def print_json(cache, name):
    if menu_data['pretty']:
        json_object = json.dumps(cache,
                                 sort_keys=False,
                                 indent=4,
                                 separators=(',', ': ')
                                 )
    else:
        json_object = json.dumps(cache)
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        output = open(menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.json", 'w')
    else:
        output = open(menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_OneDrive.json", 'w')
    output.write(json_object)
    output.close()


def print_csv(df, name):
    df = df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[True, False, False])
    df = df.drop(['Children', 'Level'], axis=1)
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\'))
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        output = open(menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.csv", 'w')
    else:
        output = open(menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_OneDrive.csv", 'w')
    df.to_csv(output, index=False)


def print_html(df, name):
    df = df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[True, False, False])
    df = df.drop(['Children', 'Level'], axis=1)
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Path'] = df.DriveItemId.apply(lambda x: find_parent(x, id_name_dict, parent_dict).lstrip('\\\\'))
    output = menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_OneDrive.html"
    file_extension = os.path.splitext(name)[1][1:]
    if file_extension == 'previous':
        output = menu_data['path'] + '\\' + os.path.basename(name).split('.')[0]+"_"+file_extension+"_OneDrive.html"

    output = open(output, 'w')
    output.write(df.to_html(index=False))
    output.close()


def selectItem(a):
    curItem = tv.selection()
    values = tv.item(curItem, 'values')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    try:
        line = f'Name: {values[3]}\nSize: {values[5]}\nType: {values[4]}\nParentId: {values[0]}\nDriveItemId: {values[1]}\neTag:{values[2]}'
        if values[4] == 'Folder' or 'Root' in values[4]:
            line += f'\n\n# Children: {values[6]}'
        details.insert(tk.END, line)
        details.see(tk.END)
    except IndexError:
        pass
    max_colum_widths = 0
    for child in tv.get_children():
        item = tv.item(child)
        new_length = tkFont.nametofont('TkTextFont').measure(str(item))
        if new_length > max_colum_widths:
            max_colum_widths = new_length
    if max_colum_widths < 50:
        tv.column('#0', width=50)
    else:
        tv.column('#0', width=max_colum_widths)
    details.config(state='disable')


def open_dat():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDrive dat file", "*.dat *.dat.previous"),))

    if filename:
        message.unbind('<Double-Button-1>', bind_id)
        if keyboard.is_pressed('shift') or menu_data['hive']:
            pass
        else:
            root.wait_window(hive(root).win)
        start = time.time()
        threading.Thread(target=parse_dat, args=(filename, reghive, start,), daemon=True).start()


def import_json():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import JSON",
                                      filetypes=(("OneDrive dat file", "*.json"),))

    if filename:
        message.unbind('<Double-Button-1>', bind_id)
        value_label['text'] = ''
        details.config(state='normal')
        details.delete('1.0', tk.END)
        details.config(state='disable')
        threading.Thread(target=parse_json, args=(filename,), daemon=True).start()
        if len(tv.get_children()) > 0:
            file_menu.entryconfig("Unload all folders", state='normal')
            search_entry.configure(state="normal")
            btn.configure(state="normal")


def import_csv():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import CSV",
                                      filetypes=(("OneDrive dat file", "*.csv"),))

    if filename:
        message.unbind('<Double-Button-1>', bind_id)
        start = time.time()
        threading.Thread(target=parse_csv, args=(filename, start,), daemon=True).start()


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def fixed_map(option):
    # Returns the style map for 'option' with any styles starting with
    # ("!disabled", "!selected", ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
    style.layout("Treeview.Item",
                 [('Treeitem.padding', {'sticky': 'nswe', 'children':
                  [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                   ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                   # ('Treeitem.focus', {'side': 'left', 'sticky': '', 'children': [
                   ('Treeitem.text', {'side': 'left', 'sticky': ''}),
                   # ]})
                   ],
                 })]
                 )
    return [elm for elm in style.map("Treeview", query_opt=option)
            if elm[:2] != ("!disabled", "!selected")]


def do_popup(event):
    rof_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/Icon11.ico'))
    copy_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/copy.png'))
    exp_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hierarchy1_expanded.png'))
    col_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hierarchy1.png'))
    try:
        curItem = tv.identify_row(event.y)
        values = tv.item(curItem, 'values')
        popup = tk.Menu(root, tearoff=0)

        if values[4] == 'Root Drive':
            popup.add_command(label="Remove OneDrive Folder", image=rof_img, compound='left', command=lambda: del_folder(curItem))
            popup.add_separator()

        popup.add_command(label="Copy", image=copy_img, compound='left', command=lambda: copy_item(values))

        if values[4] == 'Folder' or 'Root' in values[4]:
            popup.add_separator()
            popup.add_command(label="Expand folders", image=exp_img, compound='left', command=lambda: open_children(curItem), accelerator="Alt+Down")
            popup.add_command(label="Collapse folders", image=col_img, compound='left', command=lambda: close_children(curItem), accelerator="Alt+Up")
        popup.tk_popup(event.x_root, event.y_root)
    except IndexError:
        pass
    finally:
        popup.grab_release()


def del_folder(iid):
    tv.delete(iid)
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    if len(tv.get_children()) == 0:
        file_menu.entryconfig("Unload all folders", state='disable')
        search_entry.configure(state="disabled")
        btn.configure(state="disabled")


def open_children(parent):
    tv.item(parent, open=True)  # open parent
    for child in tv.get_children(parent):
        open_children(child)    # recursively open children


def close_children(parent):
    tv.item(parent, open=False)  # close parent
    for child in tv.get_children(parent):
        close_children(child)    # recursively close children


def copy_item(values):
    line = f'Name: {values[3]}\nSize: {values[5]}\nType: {values[4]}\nParentId: {values[0]}\nDriveItemId: {values[1]}\neTag: {values[2]}'
    if values[4] == 'Folder':
        line += f'\n\n# Children: {values[6]}'
    root.clipboard_append(line)


def rebind():
    global bind_id
    bind_id = message.bind('<Double-Button-1>', lambda event=None: messages(root))


root = ThemedTk()
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap(application_path + '/Images/OneDrive.ico')
root.minsize(400, 300)
root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
style = ttk.Style()
style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))
style.layout("Treeview.Item",
             [('Treeitem.padding', {'sticky': 'nswe', 'children':
              [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
               ('Treeitem.image', {'side': 'left', 'sticky': ''}),
               # ('Treeitem.focus', {'side': 'left', 'sticky': '', 'children': [
               ('Treeitem.text', {'side': 'left', 'sticky': ''}),
               # ]})
               ],
             })]
             )

root_drive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hdd.png'))
default_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_open_hdd.png'))
shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_save_hdd.png'))
folder_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/directory_closed.png'))
file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow.png'))
load_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/repeat_green.png'))
json_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded.png'))
csv_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table.png'))
uaf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/delete_red.png'))
search_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/magnifier.png'))
exit_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/no.png'))
skin_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/skin.png'))
pref_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/controls.png'))
warning_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/warning.png'))
info_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/info.png'))
error_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/error.png'))

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
options_menu = tk.Menu(menubar, tearoff=0)
submenu = tk.Menu(options_menu, tearoff=0)

for theme_name in sorted(root.get_themes()):
    submenu.add_command(label=theme_name,
                        command=lambda t=theme_name: [submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background=''),
                                                      root.set_theme(t), style.map("Treeview", foreground=fixed_map("foreground"),
                                                                                   background=fixed_map("background")),
                                                      submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background='grey'),
                                                      save_settings()])

file_menu.add_command(label="Load <UsreCid>.dat" + (' '*10), image=load_img, compound='left', command=lambda: open_dat(), accelerator="Ctrl+O")
file_menu.add_command(label="Import JSON", image=json_img, compound='left', command=lambda: import_json())
file_menu.add_command(label="Import CSV", image=csv_img, compound='left', command=lambda: import_csv())
file_menu.add_command(label="Unload all folders", image=uaf_img, compound='left', command=lambda: clear_all(), accelerator="Alt+0")
file_menu.add_separator()
file_menu.add_command(label="Exit", image=exit_img, compound='left', command=lambda: quit(root))
file_menu.entryconfig("Unload all folders", state='disable')
options_menu.add_cascade(label="Skins", image=skin_img, compound='left', menu=submenu)
options_menu.add_separator()
options_menu.add_command(label="Preferences", image=pref_img, compound='left', command=lambda: preferences(root))
menubar.add_cascade(label="File",
                    menu=file_menu)
menubar.add_cascade(label="Options",
                    menu=options_menu)
submenu.entryconfig(submenu.index(ttk.Style().theme_use()),
                    background='grey')

outer_frame = ttk.Frame(root)
main_frame = ttk.Frame(outer_frame,
                       relief='groove',
                       padding=5)
top_frame = ttk.Frame(main_frame)
bottom_frame = ttk.Frame(main_frame)

outer_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
top_frame.grid(row=0, column=0, sticky="nsew")
bottom_frame.grid(row=2, column=0, pady=(5, 0), stick='nsew')

outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_rowconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(top_frame, width=30)
btn = ttk.Button(top_frame, text="Find", image=search_img, takefocus=False, compound='right', command=lambda: [clear_search(), search()])
search_entry.configure(state="disabled")
btn.configure(state="disabled")

pw = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)

tv_frame = ttk.Frame(main_frame, relief='groove')
tv_inner_frame = ttk.Frame(tv_frame)
tv_inner_frame.grid(row=0, column=0, padx=0.5, pady=0.5, sticky="nsew")
tv = ttk.Treeview(tv_inner_frame, show='tree', selectmode='browse', takefocus='false')
scrollbv = ttk.Scrollbar(tv_inner_frame, orient="vertical", command=tv.yview)
scrollbh = ttk.Scrollbar(tv_inner_frame, orient="horizontal", command=tv.xview)
tabControl = ttk.Notebook(main_frame)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Details')
value_label = ttk.Label(bottom_frame, text='')
pb = ttk.Progressbar(bottom_frame, orient='horizontal', length=160, mode='determinate')
sl = ttk.Separator(bottom_frame, orient='vertical')
message = ttk.Label(bottom_frame, text=0, background='red', anchor='center', width=3)
sr = ttk.Separator(bottom_frame, orient='vertical')
sg = ttk.Sizegrip(bottom_frame)

details = tk.Text(tab1, undo=False, width=50, cursor='arrow', state='disable')
tv.configure(yscrollcommand=scrollbv.set, xscrollcommand=scrollbh.set)
tv.tag_configure('yellow', background="yellow", foreground="black")

tabControl.grid_rowconfigure(0, weight=1)
tabControl.grid_columnconfigure(0, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_columnconfigure(0, weight=1)

tv_frame.grid_rowconfigure(0, weight=1)
tv_frame.grid_columnconfigure(0, weight=1)
tv_inner_frame.grid_rowconfigure(0, weight=1)
tv_inner_frame.grid_columnconfigure(0, weight=1)

pw.add(tv_frame)
pw.add(tabControl)

search_entry.grid(row=0, column=2, sticky="e", padx=(0, 5))
btn.grid(row=0, column=3, sticky="e", padx=(5, 5))

pw.grid(row=1, column=0, sticky="nsew")
tv.grid(row=0, column=0, sticky="nsew")
scrollbv.grid(row=0, column=1, sticky="nsew")
scrollbh.grid(row=1, column=0, sticky="nsew")
details.grid(row=0, column=0, sticky="nsew")

value_label.grid(row=0, column=0, sticky='se')
pb.grid(row=0, column=1, padx=5, sticky='se')
sl.grid(row=0, column=2, padx=(0, 1), sticky='ns')
message.grid(row=0, column=3, sticky='nse')
sr.grid(row=0, column=4, padx=(1, 2), sticky='nse')
sg.grid(row=0, column=5, sticky='se')


tv.bind('<<TreeviewSelect>>', selectItem)
tv.bind("<Button-3>", do_popup)
tv.bind('<Alt-Down>', lambda event=None: open_children(tv.selection()))
tv.bind('<Alt-Up>', lambda event=None: close_children(tv.selection()))
root.bind('<Control-o>', lambda event=None: open_dat())
root.bind('<Alt-0>', lambda event=None: clear_all())
details.bind('<Key>', lambda a: "break")
details.bind('<Button>', lambda a: "break")
details.bind('<Motion>', lambda a: "break")
bind_id = message.bind('<Double-Button-1>', lambda event=None: messages(root))

keyboard.is_pressed('shift')

if getattr(sys, 'frozen', False):
    pyi_splash.close()

logging.info(f'OneDriveExplorer {__version__} ready!')
mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
message['text'] = f"{mcount}"
if "INFO," in log_capture_string.getvalue():
    message['background'] = ''
    message['foreground'] = ''
if "WARNING," in log_capture_string.getvalue():
    message['background'] = 'yellow'
    message['foreground'] = 'black'
if "ERROR," in log_capture_string.getvalue():
    message['background'] = 'red'
    message['foreground'] = ''

root.mainloop()
