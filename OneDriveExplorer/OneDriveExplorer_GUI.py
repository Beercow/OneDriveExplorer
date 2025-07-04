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
import os
import sys
import colorsys
import re
import base64
import json
import psutil
import ctypes
import webbrowser
import argparse
import hashlib
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog, messagebox
import tkinter.font as tkFont
import threading
import traceback
from queue import Queue
from io import StringIO, BytesIO
from collections import defaultdict
import pandas as pd
import numpy as np
from pandastable import config
from PIL import ImageTk, Image, ImageGrab
from Registry import Registry
import time
import keyboard
from ruamel.yaml import YAML
import logging
from datetime import datetime
from cerberus import Validator
import warnings
from ode.renderers.json import print_json
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
from ode.renderers.project import save_project
from ode.renderers.project import load_project
from ode.renderers.project import load_images
import ode.parsers.dat as dat_parser
from ode.parsers.csv_file import parse_csv
import ode.parsers.offline as SQLiteTableExporter
import ode.parsers.fileusagesync as fileusagesync
import ode.parsers.onedrive as onedrive_parser
from ode.parsers.odl import parse_odl, load_cparser
import ode.parsers.sqlite_db as sqlite_parser
from ode.helpers.mft import live_hive
from ode.helpers import pandastablepatch
from ode.helpers import ScrollableNotebookpatch
from ode.utils import schema
from ode.helpers.AnimatedGif import AnimatedGif
from ode.views.fileusage import FileUsageFrame
from ode.views.multiselect import FileSelectDialog

warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

DATParser = dat_parser.DATParser()
OneDriveParser = onedrive_parser.OneDriveParser()
SQLiteParser = sqlite_parser.SQLiteParser()
fus = fileusagesync.SQLiteTableExporter()

# Per monitor DPI aware. This app checks for the DPI when it is
# created and adjusts the scale factor whenever the DPI changes.
# These applications are not automatically scaled by the system.
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# shortcuts to the WinAPI functionality
set_window_pos = ctypes.windll.user32.SetWindowPos
set_window_long = ctypes.windll.user32.SetWindowLongPtrW
get_window_long = ctypes.windll.user32.GetWindowLongPtrW
get_parent = ctypes.windll.user32.GetParent

# some of the WinAPI flags
GWL_STYLE = -16

WS_MINIMIZEBOX = 131072
WS_MAXIMIZEBOX = 65536

log_capture_string = StringIO()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s, %(levelname)s, %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(log_capture_string)]
                    )

__author__ = "Brian Maloney"
__version__ = "2025.06.27"
__email__ = "bmmaloney97@gmail.com"
rbin = []
user_logs = {}
s_image = {}
reghive = ''
recbin = ''
proj_name = None
cur_sel = ''
stop = threading.Event()
tipwindow = None
current_tab = None
menu_data = None
delay = None
cstruct_df = ''
v = Validator()
file_items = defaultdict(list)
folder_type = []
dragging_sash = False
sync_message = None

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    import pyi_splash

    def splash_loop():
        count = 0
        direction = 'right'
        while pyi_splash.is_alive():
            move = '\u0020' * count
            pyi_splash.update_text(f'{move}\u2588\u2588')
            if direction == 'right':
                if len(move) < 97:
                    count += 1
                else:
                    direction = 'left'
            else:
                if len(move) > 0:
                    count -= 1
                else:
                    direction = 'right'
            time.sleep(0.05)
    threading.Thread(target=splash_loop, daemon=True).start()
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if os.path.isfile('ode.settings'):
    with open("ode.settings", "r") as jsonfile:
        menu_data = json.load(jsonfile)
        if not v.validate(menu_data, schema.menu_data):
            logging.error(f'{jsonfile.name} is not valid. {v.errors}')
            menu_data = None
        jsonfile.close()


def report_callback_exception(exc, val, tb):
    error_msg = ''.join(traceback.format_exception(exc, val, tb))

    try:
        log_date = datetime.now().strftime("%Y-%m-%dT%H%M%S")
        with open(f'{application_path}\ODE_error_{log_date}.log', 'a', encoding='utf-8') as f:
            f.write('The following error has occured and ODE is shutting down.\n')
            f.write(f'For further assistance: {__email__}\n')
            f.write(f'OneDriveExplorer v{__version__}\n')
            f.write(error_msg + '\n')
    except Exception as file_err:
        print("Failed to write error to file:", file_err)

    messagebox.showerror("Unhandled Exception", f"See {application_path}\ODE_error_{log_date}.log for further assistance.\nAn error occurred:\n{error_msg}")
    root.quit()
    sys.exit(1)


def thread_exception_handler(args):
    error_msg = ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))

    try:
        log_date = datetime.now().strftime("%Y-%m-%dT%H%M%S")
        with open(f'{application_path}\ODE_error_{log_date}.log', 'a', encoding='utf-8') as f:
            f.write('The following error has occured and ODE is shutting down.\n')
            f.write(f'For further assistance: {__email__}\n')
            f.write(f'OneDriveExplorer v{__version__}\n')
            f.write(error_msg + '\n')
    except Exception as file_err:
        print("Failed to write error to file:", file_err)

    messagebox.showerror("Thread Exception", f"See {application_path}\ODE_error_{log_date}.log for further assistance.\nA thread error occurred:\n{error_msg}")
    root.quit()
    sys.exit(1)


threading.excepthook = thread_exception_handler

if menu_data is None:
    logging.info('Creating ode.settings file.')
    menu_data = json.loads('{"theme": "vista",\
                             "json": false,\
                             "pretty": false,\
                             "csv": false,\
                             "html": false,\
                             "path": ".",\
                             "hive": false,\
                             "odl": false,\
                             "odl_cor": false,\
                             "odl_save": false,\
                             "font": null,\
                             "Date_created": true,\
                             "Date_accessed": true,\
                             "Date_modified": true,\
                             "Size": true}'
                           )

    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


class QuitDialog:
    def __init__(self, root):
        self.root = root
        self.create_dialog()

    def create_dialog(self):
        self.win = tk.Toplevel(self.root)
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.win.title("Please confirm")
        self.win.wm_transient(self.root)
        self.win.iconbitmap(application_path + '/Images/titles/favicon.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)
        self.setup_window_style()

    def setup_window_style(self):
        hwnd = get_parent(self.win.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)

    def create_widgets(self):
        self.frame = ttk.Frame(self.win, relief='flat')
        self.inner_frame = ttk.Frame(self.frame, relief='groove', padding=5)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)

        self.label = ttk.Label(self.inner_frame, text="Are you sure you want to exit?", padding=5)
        self.yes = ttk.Button(self.inner_frame, text="Yes", takefocus=False, command=self.btn1)
        self.no = ttk.Button(self.inner_frame, text="No", takefocus=False, command=self.btn2)

        self.label.grid(row=0, column=0, columnspan=2)
        self.yes.grid(row=1, column=0, padx=5, pady=5)
        self.no.grid(row=1, column=1, padx=(0, 5), pady=5)

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def btn1(self):
        parent = psutil.Process(os.getpid())
        for child in parent.children(recursive=True):
            child.kill()
        self.win.destroy()
        sys.exit()

    def btn2(self):
        self.root.unbind("<Configure>")
        if sync_message:
            sync_message.bind_events()
        self.win.destroy()

    def __callback(self):
        return

    def sync_windows(self, event=None):
        try:
            x = self.root.winfo_x()
            qw = self.win.winfo_width()
            y = self.root.winfo_y()
            qh = self.win.winfo_height()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))
        except Exception:
            pass


class Preferences:
    def __init__(self, root):
        self.root = root
        self.load_menu_data()
        self.create_preferences_window()

    def load_menu_data(self):
        self.json_save = tk.BooleanVar(value=menu_data['json'])
        self.json_pretty = tk.BooleanVar(value=menu_data['pretty'])
        self.csv_save = tk.BooleanVar(value=menu_data['csv'])
        self.html_save = tk.BooleanVar(value=menu_data['html'])
        self.auto_path = tk.StringVar(value=menu_data['path'])
        self.skip_hive = tk.BooleanVar(value=menu_data['hive'])
        self.odl = tk.BooleanVar(value=menu_data['odl'])
        self.odl_cor = tk.BooleanVar(value=menu_data['odl_cor'])
        self.odl_save = tk.BooleanVar(value=menu_data['odl_save'])

    def create_preferences_window(self):
        self.win = tk.Toplevel(self.root)
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.win.wm_transient(self.root)
        self.win.title("Preferences")
        self.win.iconbitmap(application_path + '/Images/titles/controls.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)

    def create_widgets(self):
        self.frame = ttk.Frame(self.win)
        self.inner_frame = ttk.Frame(self.frame, relief='groove', padding=5)
        self.select_frame = ttk.LabelFrame(self.inner_frame, text="<UserCid>.dat/SQLite output")
        self.path_frame = ttk.Frame(self.inner_frame)
        self.hive_frame = ttk.Frame(self.inner_frame)
        self.odl_frame = ttk.LabelFrame(self.inner_frame, text="ODL settings")
        self.exit_frame = ttk.Frame(self.inner_frame)

        self.setup_grid_layout()

        self.create_checkbuttons()
        self.create_path_entry()
        self.create_buttons()

        self.disable_widgets()

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def setup_grid_layout(self):
        for i in range(5):
            self.inner_frame.grid_rowconfigure(i, weight=1)
            self.inner_frame.grid_columnconfigure(i, weight=1)

        self.frame.grid(row=0, column=0, sticky="nsew")
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.select_frame.grid(row=0, column=0, sticky="nsew")
        self.odl_frame.grid(row=1, column=0, pady=25, sticky="nsew")
        self.path_frame.grid(row=2, column=0, pady=(0, 25), sticky="nsew")
        self.hive_frame.grid(row=3, column=0, pady=(0, 25), sticky="nsew")
        self.exit_frame.grid(row=4, column=0, sticky="nsew")

    def create_checkbuttons(self):
        self.auto_json = ttk.Checkbutton(self.select_frame, text="Auto Save to JSON", var=self.json_save, offvalue=False, onvalue=True, takefocus=False, command=self.pretty_config)
        self.pretty = ttk.Checkbutton(self.select_frame, text="--pretty", var=self.json_pretty, offvalue=False, onvalue=True, takefocus=False)
        self.auto_csv = ttk.Checkbutton(self.select_frame, text="Auto Save to CSV", var=self.csv_save, offvalue=False, onvalue=True, takefocus=False)
        self.auto_html = ttk.Checkbutton(self.select_frame, text="Auto Save to HTML", var=self.html_save, offvalue=False, onvalue=True, takefocus=False)
        self.reghive = ttk.Checkbutton(self.hive_frame, text="Disable loading user hive dialog", var=self.skip_hive, offvalue=False, onvalue=True, takefocus=False)
        self.en_odl = ttk.Checkbutton(self.odl_frame, text="Enable ODL log parsing", var=self.odl, offvalue=False, onvalue=True, takefocus=False, command=self.odl_config)
        self.en_cor = ttk.Checkbutton(self.odl_frame, text="Enable ODL log correlation", var=self.odl_cor, offvalue=False, onvalue=True, takefocus=False)
        self.auto_odl = ttk.Checkbutton(self.odl_frame, text="Auto Save ODL", var=self.odl_save, offvalue=False, onvalue=True, takefocus=False)

        self.auto_json.grid(row=0, column=0, padx=5)
        self.pretty.grid(row=0, column=1, sticky="w")
        self.auto_csv.grid(row=1, column=0, columnspan=2, padx=5, sticky="w")
        self.auto_html.grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        self.reghive.grid(row=0, column=2, padx=5)
        self.en_odl.grid(row=0, column=0, padx=5, sticky="w")
        self.en_cor.grid(row=1, column=0, padx=(15, 5), sticky="w")
        self.auto_odl.grid(row=2, column=0, padx=5, sticky="w")

    def create_path_entry(self):
        self.label = ttk.Label(self.path_frame, text="Auto Save Path")
        self.save_path = ttk.Entry(self.path_frame, width=30, textvariable=self.auto_path, exportselection=0)
        self.btn = ttk.Button(self.path_frame, text='...', width=3, takefocus=False, command=self.select_dir)

        self.label.grid(row=0, column=0, padx=5, sticky="w")
        self.save_path.grid(row=0, column=1)
        self.btn.grid(row=0, column=2, padx=5)

    def create_buttons(self):
        self.save = ttk.Button(self.exit_frame, text="Save", takefocus=False, command=self.save_pref)
        self.cancel = ttk.Button(self.exit_frame, text="Cancel", takefocus=False, command=self.close_pref)

        self.save.grid(row=0, column=0, pady=5, sticky="e")
        self.cancel.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    def disable_widgets(self):
        if not menu_data['json']:
            self.pretty.configure(state="disabled")
        if not menu_data['odl']:
            self.en_cor.configure(state="disabled")
            self.auto_odl.configure(state="disabled")

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        try:
            self.win.geometry("+%d+%d" % (x + w/4, y + h/3))
        except Exception:
            pass

    def pretty_config(self):
        if self.json_save.get() is True:
            self.pretty.configure(state="normal")
        else:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

    def odl_config(self):
        if self.odl.get() is True:
            self.en_cor.configure(state="normal")
            self.auto_odl.configure(state="normal")
        else:
            self.en_cor.configure(state="disabled")
            self.auto_odl.configure(state="disabled")
            self.odl_cor.set(False)
            self.odl_save.set(False)

    def select_dir(self):
        dir_path = filedialog.askdirectory(initialdir="\\", title="Auto Save Location")

        if dir_path:
            dir_path = dir_path.replace('/', '\\')
            menu_data['path'] = dir_path
            self.save_path.delete(0, tk.END)
            self.save_path.insert(tk.END, dir_path)

    def save_pref(self):
        menu_data['json'] = self.json_save.get()
        menu_data['pretty'] = self.json_pretty.get()
        menu_data['csv'] = self.csv_save.get()
        menu_data['html'] = self.html_save.get()
        menu_data['path'] = self.auto_path.get()
        menu_data['hive'] = self.skip_hive.get()
        menu_data['odl'] = self.odl.get()
        menu_data['odl_cor'] = self.odl_cor.get()
        menu_data['odl_save'] = self.odl_save.get()

        if menu_data['odl']:
            file_menu.entryconfig("OneDrive logs", state='normal')
        else:
            file_menu.entryconfig("OneDrive logs", state='disable')

        if not menu_data['odl_cor']:
            for item in infoFrame.winfo_children():
                if '.!notebook.!frame.' in str(item):
                    item.destroy()

        if not os.path.exists(menu_data['path']):
            os.makedirs(menu_data['path'])

        with open("ode.settings", "w") as jsonfile:
            json.dump(menu_data, jsonfile)

        self.win.destroy()

    def __callback(self):
        return

    def close_pref(self):
        self.win.destroy()


class hive:
    def __init__(self, root, sql=False):
        self.root = root
        self.sql = sql
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("Load User Hive - NTUSER.DAT")
        self.win.iconbitmap(application_path + '/Images/titles/question.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_hive)

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.button_frame = ttk.Frame(self.inner_frame)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)
        self.button_frame.grid(row=2, column=0, columnspan=3)

        self.label_i = ttk.Label(self.inner_frame, image=reg_img)
        self.label = ttk.Label(self.inner_frame,
                               text="User's registry hive (NTUSER.DAT) allows the mount points of the SyncEngines to be resolved.\n\nDo you want to provide a registry hive?\n")

        self.label_l = ttk.Label(self.inner_frame, text="Note:")

        self.label_r = ttk.Label(self.inner_frame,
                                 text="To bypass this dialog and skip loading hive, hold SHIFT when loading <UserCid>.dat\nThis dialog can also be bypassed in the Preferences settings.\n")

        self.yes = ttk.Button(self.button_frame,
                              text="Yes",
                              takefocus=False,
                              command=self.get_hive)

        self.no = ttk.Button(self.button_frame,
                             text="No",
                             takefocus=False,
                             command=self.close_hive)

        self.label_i.grid(row=0, column=0, rowspan=2, padx=(0, 5), sticky='n')
        self.label.grid(row=0, column=1, columnspan=2, pady=(5, 0), sticky='w')
        self.label_l.grid(row=1, column=1, sticky='nw')
        self.label_r.grid(row=1, column=2, padx=5, sticky='w')
        self.yes.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='e')
        self.no.grid(row=0, column=1, pady=5, sticky='w')

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def __callback(self):
        return

    def close_hive(self):
        self.win.destroy()

    def get_hive(self):
        global reghive
        reghive = filedialog.askopenfilename(initialdir="/",
                                             title="Open User Registry Hive",
                                             filetypes=(("NTUSER.DAT",
                                                         "*.dat"),))
        if reghive:
            self.win.destroy()
            if not self.sql:
                root.wait_window(rec_bin(root).win)

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        try:
            self.win.geometry("+%d+%d" % (x + w/4, y + h/3))
        except Exception:
            pass


class rec_bin:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("$Recycle.Bin")
        self.win.iconbitmap(application_path + '/Images/titles/trashcan.ico')
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

        self.label_i = ttk.Label(self.inner_frame, image=trash_img)
        self.label = ttk.Label(self.inner_frame,
                               text="Providing the path to $Recycle.Bin allows retrieval of deleted files.\n\nDo you want to provide the location of $Recycle.Bin?\n")

        self.yes = ttk.Button(self.button_frame,
                              text="Yes",
                              takefocus=False,
                              command=self.get_rec_bin)

        self.no = ttk.Button(self.button_frame,
                             text="No",
                             takefocus=False,
                             command=self.close_rec_bin)

        self.label_i.grid(row=0, column=0, rowspan=2, sticky='n')
        self.label.grid(row=0, column=1, columnspan=2, pady=(5, 0), sticky='w')
        self.yes.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='e')
        self.no.grid(row=0, column=1, pady=5, sticky='w')

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def __callback(self):
        return

    def close_rec_bin(self):
        self.win.destroy()

    def get_rec_bin(self):
        global recbin
        recbin = filedialog.askdirectory(initialdir="/", title="Open")

        if recbin:
            self.win.destroy()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        try:
            self.win.geometry("+%d+%d" % (x + w/4, y + h/3))
        except Exception:
            pass


class Messages:
    def __init__(self, root):
        self.root = root
        self.initialize_window()

    def initialize_window(self):
        self.win = tk.Toplevel(self.root)
        self.win.title("Messages")
        self.win.wm_transient(self.root)
        self.win.iconbitmap(application_path + '/Images/titles/language_blue.ico')
        self.win.minsize(400, 300)
        self.win.grab_set()
        self.win.focus_force()
        self.win.protocol("WM_DELETE_WINDOW", self.close_mess)
        message['background'] = ''
        message['foreground'] = ''

        self.frame = ttk.Frame(self.win)
        self.inner_frame = ttk.Frame(self.frame, relief='groove', padding=5)
        self.create_widgets()
        self.restore_tree_messages()

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def create_widgets(self):
        self.create_frames()
        self.create_treeview()
        self.create_textbox()
        self.create_labels_buttons()
        self.tree.bind('<<TreeviewSelect>>', self.select)

    def create_frames(self):
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_rowconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(0, weight=1)

    def create_treeview(self):
        self.columns = ('Message Date', 'Message Type', 'Message')
        self.tree_scroll = ttk.Scrollbar(self.inner_frame)
        self.tree = ttk.Treeview(self.inner_frame, columns=self.columns, yscrollcommand=self.tree_scroll.set)
        self.tree.heading('Message Date', text='Message Date', anchor='w')
        self.tree.heading('Message Type', text='Message Type', anchor='w')
        self.tree.heading('Message', text='Message', anchor='w')
        self.tree.column('#0', minwidth=0, width=50, stretch=False, anchor='w')
        self.tree.column('Message Date', minwidth=0, width=150, stretch=False, anchor='w')
        self.tree.column('Message Type', minwidth=0, width=100, stretch=False, anchor='w')
        self.tree_scroll.config(command=self.tree.yview)
        self.tree.grid(row=0, column=0, columnspan=5, padx=(10, 0), pady=(10, 0), sticky='nsew')
        self.tree_scroll.grid(row=0, column=5, padx=(0, 10), pady=(10, 0), sticky="nsew")

    def create_textbox(self):
        self.tb_scroll = ttk.Scrollbar(self.inner_frame)
        self.tb = tk.Text(self.inner_frame, undo=False, height=10, width=87, yscrollcommand=self.tb_scroll.set)
        self.tb_scroll.config(command=self.tb.yview)
        self.tb.config(state='disable')
        self.tb.grid(row=1, column=0, columnspan=5, padx=(10, 0), pady=(5, 10), sticky='nsew')
        self.tb_scroll.grid(row=1, column=5, padx=(0, 10), pady=(5, 10), sticky="nsew")

    def create_labels_buttons(self):
        self.total = ttk.Label(self.inner_frame, text='Total messages:')
        self.value_label = ttk.Label(self.inner_frame, text='')
        self.pb = ttk.Progressbar(self.inner_frame, orient='horizontal', length=160, mode='indeterminate')
        self.clear = ttk.Button(self.inner_frame, text='Clear messages', takefocus=False, command=self.clear)
        self.export = ttk.Button(self.inner_frame, text='Export messages', takefocus=False, command=self.export_message)
        self.sg = ttk.Sizegrip(self.inner_frame)

        self.total.grid(row=2, column=0, padx=(10, 0), pady=(0, 5), stick='w')
        self.value_label.grid(row=2, column=1, padx=5, pady=(0, 5))
        self.pb.grid(row=2, column=2, pady=(0, 5))
        self.clear.grid(row=2, column=3, padx=5, pady=(0, 5), stick='e')
        self.export.grid(row=2, column=4, pady=(0, 5), stick='e')
        self.sg.grid(row=2, column=5, stick='se')
        self.pb.grid_remove()

    def clear(self):
        self.tb.config(state='normal')
        self.tb.delete('1.0', tk.END)
        self.tb.config(state='disable')
        log_capture_string.truncate(0)
        log_capture_string.seek(0)
        self.tree.delete(*self.tree.get_children())
        mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
        self.total['text'] = f'Total messages: {mcount}'
        message['text'] = mcount
        message['background'] = ''
        message['foreground'] = ''

    def export_message(self, event=None):
        path = filedialog.askdirectory(initialdir="/")

        if path:
            self.disable_export_buttons()

            self.value_label['text'] = "Exporting messages. Please wait..."
            self.pb.start()
            self.show_export_status()

            excel_name = self.generate_excel_name(path)

            try:
                with pd.ExcelWriter(excel_name) as writer:
                    self.write_dataframe_to_excel(writer)

                self.pb.stop()
                ExportResult(self.win, excel_name)

            except Exception as e:
                logging.error(e)
                ExportResult(self.win, e, failed=True)
                self.restore_tree_messages()

            self.hide_export_status()
            self.enable_export_buttons()

    def disable_export_buttons(self):
        self.clear.config(state='disable')
        self.export.config(state='disable')

    def enable_export_buttons(self):
        self.clear.config(state='normal')
        self.export.config(state='normal')

    def show_export_status(self):
        self.value_label.grid(row=2, column=1, pady=(0, 5))
        self.pb.grid(row=2, column=2, pady=(0, 5))

    def hide_export_status(self):
        self.value_label.grid_forget()
        self.pb.grid_forget()

    def generate_excel_name(self, path):
        return path + '\\OneDriveExplorerMessages_' + datetime.now().strftime("%Y-%m-%dT%H%M%S.xlsx")

    def write_dataframe_to_excel(self, writer):
        ids = self.tree.get_children()
        lst = []

        for id in ids:
            row = self.tree.item(id, 'values')
            lst.append(row)

        df = pd.DataFrame.from_records(lst, columns=['Message Data', 'Message Type', 'Message'])

        row_count = len(df.index)

        if row_count > 1048576:
            groups = df.groupby(np.arange(len(df.index))//1048575)

            for (frameno, frame) in groups:
                frame.to_excel(writer, f'OneDriveExplorer Messages {frameno}', index=False)
        else:
            df.to_excel(writer, 'OneDriveExplorer Messages', index=False)

    def restore_tree_messages(self):
        self.tree.delete(*self.tree.get_children())
        data = log_capture_string.getvalue().split('\n')

        for m in data:
            m = m.replace('\x00', '').split(', ', 2)
            try:
                if m[1] == 'INFO':
                    image = minfo_img
                if m[1] == 'WARNING':
                    image = warning_img
                if m[1] == 'ERROR':
                    image = merror_img
            except IndexError:
                image = ''
            try:
                self.tree.insert("", "end", values=m, image=image)
            except Exception:
                break

        mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
        self.total['text'] = f'Total messages: {mcount}'
        message['text'] = mcount

    def select(self, event=None):
        self.tb.config(state='normal')
        self.tb.delete('1.0', tk.END)
        curItem = self.tree.selection()
        values = self.tree.item(curItem, 'values')
        try:
            self.tb.insert(tk.END,
                           re.sub("(.{87})", "\\1\n", values[2], 0, re.DOTALL))
        except IndexError:
            pass
        self.tb.config(state='disable')

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.win.geometry("+%d+%d" % (x, y))

    def close_mess(self):
        self.root.unbind('<Configure>')
        self.win.unbind('<Configure>')
        self.win.destroy()

    def onmotion(self):
        self.update()


class ExportResult:
    def __init__(self, root, excel_name, failed=False):
        self.root = root
        self.failed = failed
        self.excel_name = excel_name.replace('/', '\\') if not failed else excel_name
        self.create_result_window()

    def create_result_window(self):
        title = "Export failed!" if self.failed else "Export successful!"
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title(title)
        self.win.iconbitmap(application_path + '/Images/titles/OneDrive.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame, relief='groove', padding=5)

        self.configure_grid_weights()
        self.configure_frames()
        self.create_widgets()

        self.sync_windows()
        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def configure_grid_weights(self):
        for widget in [self.win, self.frame, self.inner_frame]:
            widget.grid_rowconfigure(0, weight=1)
            widget.grid_columnconfigure(0, weight=1)

    def configure_frames(self):
        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5)

    def create_widgets(self):
        info_image = error_img if self.failed else info_img
        label_text = f'Messages {"failed to" if self.failed else "exported to"}:\n\n{self.excel_name}'

        self.label_i = ttk.Label(self.inner_frame, image=info_image)
        self.label = ttk.Label(self.inner_frame, text=label_text)
        self.btn = ttk.Button(self.inner_frame, text='OK', takefocus=False, command=self.ok)

        self.label_i.grid(row=0, column=0)
        self.label.grid(row=0, column=1, padx=(0, 5))
        self.btn.grid(row=1, column=0, columnspan=2, pady=5)

    def ok(self):
        self.win.destroy()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        try:
            self.win.geometry("+%d+%d" % (x + w / 2, y + h / 2))
        except Exception:
            pass


class CStructs:
    def __init__(self, root, df):
        self.root = root
        self.df = df

        self.win = tk.Toplevel(self.root)
        self.setup_window()

        self.frame = ttk.Frame(self.win)
        self.inner_frame = ttk.Frame(self.frame, relief='groove')

        self.cstruct_frame = ttk.Frame(self.inner_frame)
        self.mid_frame = ttk.Frame(self.inner_frame)
        self.mid_frame.columnconfigure(1, weight=1)
        self.bottom_frame = ttk.Frame(self.inner_frame)
        self.bottom_frame.columnconfigure(4, weight=1)

        self.setup_cstruct_frame()
        self.setup_mid_frame()
        self.setup_bottom_frame()

        if self.total['text'] == '0':
            self.disable_widgets()
        else:
            self.populate_plugin_list()
            self.sync_windows(self.win)
            self.grid_all_widgets()
            self.bind_events()

    def setup_window(self):
        self.win.title("CStructs")
        self.win.wm_transient(self.root)
        self.win.iconbitmap(application_path + '/Images/titles/cstruct.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_plugins)
        hwnd = get_parent(self.win.winfo_id())

        # Getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)

        # Building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX

        # Setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

    def setup_cstruct_frame(self):
        self.plugin_list = tk.Listbox(self.cstruct_frame, activestyle='dotbox',
                                      exportselection=False, width=70, bd=0, font='TkDefaultFont')
        self.scrollbv = ttk.Scrollbar(self.cstruct_frame, orient="vertical",
                                      command=self.plugin_list.yview)
        self.plugin_list.configure(yscrollcommand=self.scrollbv.set)

    def setup_mid_frame(self):
        # Assuming self.mid_frame is already created and configured
        self.code_label = ttk.Label(self.mid_frame, text="Code file", justify="left", anchor='w')
        self.entry1 = tk.Text(self.mid_frame, exportselection=False, font='TkDefaultFont',
                              cursor='arrow', width=49, height=1, padx=5)

        self.author_label = ttk.Label(self.mid_frame, text="Author", justify="left", anchor='w')
        self.entry2 = tk.Text(self.mid_frame, exportselection=False, font='TkDefaultFont',
                              cursor='arrow', width=49, height=1, padx=5)

        self.function_label = ttk.Label(self.mid_frame, text="Functions", justify="left", anchor='w')
        self.function_list = tk.Listbox(self.mid_frame, activestyle='none', font='TkDefaultFont',
                                        exportselection=False, width=48, relief='flat',
                                        height=5, bd=1, selectmode="SINGLE")
        self.fscrollbv = ttk.Scrollbar(self.mid_frame, orient="vertical", command=self.function_list.yview)
        self.function_list.configure(yscrollcommand=self.fscrollbv.set)

        self.version_label = ttk.Label(self.mid_frame, text="Version", justify="left", anchor='w')
        self.entry3 = tk.Text(self.mid_frame, exportselection=False, font='TkDefaultFont',
                              cursor='arrow', width=49, height=1, padx=5)

        self.id_label = ttk.Label(self.mid_frame, text="Internal GUID", justify="left", anchor='w')
        self.entry4 = tk.Text(self.mid_frame, exportselection=False, font='TkDefaultFont',
                              cursor='arrow', width=49, height=1, padx=5)

        self.description_label = ttk.Label(self.mid_frame, text="Description", justify="left", anchor='w')
        self.entry5 = tk.Text(self.mid_frame, exportselection=False, font='TkDefaultFont',
                              cursor='arrow', width=49, height=1, padx=5)

    def setup_bottom_frame(self):
        self.load_label = ttk.Label(self.bottom_frame, text="CStructs loaded:", justify="left", anchor='w')
        self.sl = ttk.Separator(self.bottom_frame, orient='vertical')
        self.total = ttk.Label(self.bottom_frame, text=f"{self.df.shape[0]}", anchor='center', width=3)
        self.sr = ttk.Separator(self.bottom_frame, orient='vertical')
        self.btn = ttk.Button(self.bottom_frame, text="Add'l. Info", takefocus=False, command=self.more_info)

    def close_plugins(self):
        self.root.unbind('<Configure>')
        self.win.unbind('<Configure>')
        self.win.destroy()

    def disable_widgets(self):
        self.btn.configure(state='disabled')
        self.entry1.configure(state="disabled")
        self.entry2.configure(state="disabled")
        self.entry3.configure(state="disabled")
        self.entry4.configure(state="disabled")
        self.entry5.configure(state="disabled")
        self.plugin_list.configure(state="disabled")

    def populate_plugin_list(self):
        if not self.df.empty:
            self.plugin_list.insert("end", *("\u2008" + str(item) for item in self.df.Code_File))
            self.plugin_list.select_set(0)
            self.selected_item(event=None)

    def grid_all_widgets(self):
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.cstruct_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nsew')
        self.mid_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.bottom_frame.grid(row=2, column=0, padx=10, pady=(5, 4), sticky='nsew')

        self.plugin_list.grid(row=0, column=0, sticky="nsew")
        self.scrollbv.grid(row=0, column=1, sticky="nsew")

        self.code_label.grid(row=0, column=0, pady=(0, 5), sticky='w')
        self.entry1.grid(row=0, column=1, columnspan=2, pady=(0, 5), sticky='e')
        self.author_label.grid(row=2, column=0, pady=(0, 5), sticky='w')
        self.entry2.grid(row=2, column=1, columnspan=2, pady=(0, 5), sticky='e')
        self.function_label.grid(row=3, column=0, pady=(0, 5), sticky='nw')
        self.function_list.grid(row=3, column=1, pady=(0, 5), sticky='e')
        self.fscrollbv.grid(row=3, column=2, pady=(0, 5), sticky="nsew")
        self.version_label.grid(row=4, column=0, pady=(0, 5), sticky='w')
        self.entry3.grid(row=4, column=1, columnspan=2, pady=(0, 5), sticky='e')
        self.id_label.grid(row=5, column=0, pady=(0, 5), sticky='w')
        self.entry4.grid(row=5, column=1, columnspan=2, pady=(0, 5), sticky='e')
        self.description_label.grid(row=6, column=0, pady=(0, 5), sticky='w')
        self.entry5.grid(row=6, column=1, columnspan=2, pady=(0, 5), sticky='e')

        self.load_label.grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.sl.grid(row=0, column=1, sticky='nsw')
        self.total.grid(row=0, column=2, sticky='w')
        self.sr.grid(row=0, column=3, sticky='nsw')
        self.btn.grid(row=0, column=4, pady=(0, 5), sticky='e')

    def bind_events(self):
        self.plugin_list.bind("<<ListboxSelect>>", self.selected_item)
        self.function_list.bind('<Button>', lambda a: "break")
        self.function_list.bind('<Motion>', lambda a: "break")
        self.entry1.bind('<Button-1>', lambda a: "break")
        self.entry2.bind('<Button-1>', lambda a: "break")
        self.entry3.bind('<Button-1>', lambda a: "break")
        self.entry4.bind('<Button-1>', lambda a: "break")
        self.entry5.bind('<Button-1>', lambda a: "break")
        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def selected_item(self, event):
        for i in self.plugin_list.curselection():
            text = self.df.loc[self.df.Code_File == self.plugin_list.get(i).strip('\u2008')].values.tolist()[0]

            self.function_list.delete(0, "end")
            for x in text[5]:
                self.function_list.insert("end", f"\u2008{x['Function']}")

            entry_data = [text[4], text[1], text[2], text[3], text[0]]
            entry_widgets = [self.entry1, self.entry2, self.entry3, self.entry4, self.entry5]

            for entry, data in zip(entry_widgets, entry_data):
                entry.configure(state="normal")
                entry.delete('1.0', "end")
                entry.insert("end", data)
                entry.configure(state="disabled")

    def more_info(self):
        self.info = tk.Toplevel(self.win)
        self.configure_info_window()

        self.info_frame = ttk.Frame(self.info)
        self.info_inner_frame = ttk.Frame(self.info_frame, padding=5, relief='groove')

        self.scrollb = ttk.Scrollbar(self.info_inner_frame)
        self.info_text = CustomText(self.info_inner_frame, yscrollcommand=self.scrollb.set,
                                    padx=5, pady=5, fg="DarkOrange2")
        self.scrollb.config(command=self.info_text.yview)

        self.configure_info_text_tags()

        yaml = YAML()
        yaml.compact(seq_seq=False, seq_map=False)
        string_stream = StringIO()

        for i in self.plugin_list.curselection():
            text = self.df.loc[self.df.Code_File == self.plugin_list.get(i).strip('\u2008')].values.tolist()[0]
            yaml.dump(text[5], string_stream)
            self.info_text.insert("end", string_stream.getvalue())
            self.highlight_patterns_in_info_text()

        self.grid_info_widgets()

        self.sync_windows(self.info)

        self.info_text.bind('<Key>', lambda a: "break")
        self.info_text.bind('<Button>', lambda a: "break")
        self.info_text.bind('<Motion>', lambda a: "break")

    def configure_info_window(self):
        self.info.title(f"{self.plugin_list.get(self.plugin_list.curselection()[0])}")
        self.info.iconbitmap(application_path + '/Images/titles/window_info.ico')
        self.info.grab_set()
        self.info.focus_force()
        self.info.resizable(False, False)
        hwnd = get_parent(self.info.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)

    def configure_info_text_tags(self):
        tags = ["blue", "black", "green", "gray", "dblue", "black2", "dgreen"]
        colors = ["blue", "black", "green", "dim gray", "DodgerBlue2", "black", "DarkSeaGreen3"]

        for tag, color in zip(tags, colors):
            self.info_text.tag_configure(tag, foreground=color)

    def highlight_patterns_in_info_text(self):
        self.info_text.highlight_pattern("Function|Description|Flags|Structure(?=:)", "blue", regexp=True)
        self.info_text.highlight_pattern(":\s|:\s\||\s.*?(?=;)", "black", regexp=True)
        self.info_text.highlight_pattern("#\s.*?$", "green", regexp=True)
        self.info_text.highlight_pattern("#define\s.*?$|{|}|;|(\];)|(?:\S)(\[)", "gray", regexp=True)
        self.info_text.highlight_pattern("(?:\S)(?=\[)", "black2", regexp=True)
        self.info_text.highlight_pattern("//.*?$", "dgreen", regexp=True)
        self.info_text.highlight_pattern("\s(BYTE|CHAR|DWORD|INT|INT128|INT16|INT32|INT64|INT8|LONG|LONG32|LONG64|LONGLONG|OWORD|QWORD|SHORT|UCHAR|UINT|UINT128|UINT16|UINT32|UINT64|UINT8|ULONG|ULONG64|ULONGLONG|USHORT|WCHAR|WORD|__int128|__int16|__int32|__int64|__int8|char|int|int128|int128_t|int16|int16_t|int32|int32_t|int64|int64_t|int8|int8_t|long long|long|short|signed char|signed int|signed long long|signed long|signed short|struct|u1|u16|u2|u4|u8|uchar|uint|uint128|uint128_t|uint16|uint16_t|uint32|uint32_t|uint64|uint64_t|uint8|uint8_t|ulong|unsigned __int128|unsigned char|unsigned int|unsigned long long|unsigned long|unsigned short|ushort|void|wchar|wchar_t)\s", "dblue", regexp=True)

    def grid_info_widgets(self):
        self.info_frame.grid(row=0, column=0)
        self.info_inner_frame.grid(row=0, column=0, padx=5, pady=5)
        self.info_text.grid(row=0, column=0, padx=(5, 0), pady=5)
        self.scrollb.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='nsew')

    def sync_windows(self, window, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.win.geometry("+%d+%d" % (x, y))


class Help:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Help")
        self.win.wm_transient(self.root)
        self.win.iconbitmap(application_path + '/Images/titles/question.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_help)
        self.configure_window()
        self.bgf = style.lookup('Treeview', 'background')
        self.fgf = style.lookup('Treeview', 'foreground')

        if not fgf:
            self.fgf = 'black'

        self.frame = ttk.Frame(self.win, relief='flat')
        self.create_text_widget()

        self.frame.grid(row=0, column=0)

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def configure_window(self):
        hwnd = get_parent(self.win.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)

    def create_text_widget(self):
        help_text = [
            "Settings Metadata\nTo load <UserCid>.dat, File -> OneDrive settings -> Load <UserCid>.dat",
            "Once <UserCid>.dat is loaded, OneDriveExplorer operates much like File Explorer.",
            "To load SQLite databases, File -> OneDrive settings -> Load from SQLite",
            "Once databases are loaded, OneDriveExplorer operates much like File Explorer.\n",
            "Context menu\nRight-click on folder/file to export Name, Path, Details, etc.",
            "ODL logs\nTo enable parsing, Options -> Preferences -> Enable ODL log parsing.\n",
            "Live System\nRun OneDriveExplorer as an administrator to activate.",
            "For full details, see the included manual."
        ]

        # Calculate the height needed based on line count
        num_lines = sum(text.count("\n") + 1 for text in help_text)

        # Calculate the width based on the longest line
        max_line_length = max(len(subline) for line in help_text for subline in line.splitlines())

        self.text_widget = tk.Text(self.frame, wrap="word", background=self.bgf, foreground=self.fgf, width=max_line_length, height=num_lines, relief='flat', state="normal")
        self.text_widget.bindtags((str(self.text_widget), str(self.root), "all"))
        self.text_widget.insert("1.0", "\n".join(help_text))

        # Add a tag to the word "manual"
        self.text_widget.tag_add("manual_tag", "14.35", "14.41")  # Assuming "manual" is at line 14, char 35-41
        self.text_widget.tag_config("manual_tag", foreground='#0563C1', underline=True)

        bold_font = tkFont.Font(self.text_widget, self.text_widget.cget("font"))
        bold_font.configure(weight="bold")
        self.text_widget.tag_add("bold_tag", "1.0", "1.17")
        self.text_widget.tag_add("bold_tag", "7.0", "7.12")
        self.text_widget.tag_add("bold_tag", "12.0", "12.11")
        self.text_widget.tag_config("bold_tag", font=bold_font)

        # Bind double-click event to the "manual_tag"
        self.text_widget.tag_bind("manual_tag", "<Double-1>", self.open_manual)
        # Bind mouse enter and leave events to change cursor
        self.text_widget.tag_bind("manual_tag", "<Enter>", lambda e: self.text_widget.config(cursor="hand2"))
        self.text_widget.tag_bind("manual_tag", "<Leave>", lambda e: self.text_widget.config(cursor=""))

        self.text_widget.configure(state="disabled")  # Make text read-only
        self.text_widget.grid(row=0, column=0, padx=(10, 30), pady=(10, 20), sticky='w')

    def open_manual(self, event=None):
        webbrowser.open_new_tab(application_path + '/ode/helpers/Manual/OneDriveExplorerManual.html')
        self.text_widget.tag_config("manual_tag", foreground='#954F72', underline=True)

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))

    def close_help(self):
        self.root.unbind('<Configure>')
        self.win.unbind('<Configure>')
        self.win.destroy()


class About:
    def __init__(self, root):
        self.root = root
        self.create_window()
        self.configure_window()
        self.create_widgets()

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def create_window(self):
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("About OneDriveExplorer")
        self.win.iconbitmap(application_path + '/Images/titles/favicon.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_about)

    def configure_window(self):
        hwnd = get_parent(self.win.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)

    def create_widgets(self):
        self.frame = ttk.Frame(self.win)
        self.label = ttk.Label(self.frame, image=ode_img, anchor='n')
        self.label1 = ttk.Label(self.frame, text="OneDriveExplorer", justify="left", anchor='w')
        self.label2 = ttk.Label(self.frame, text=f"Version {__version__}", justify="left", anchor='w')
        self.label3 = ttk.Label(self.frame, text=f"Copyright © {__version__[:4]}", justify="left", anchor='w')
        self.label4 = ttk.Label(self.frame, text="Brian Maloney", justify="left", anchor='w')
        self.label5 = ttk.Label(self.frame, text="L̲a̲t̲e̲s̲t̲_R̲e̲l̲e̲a̲s̲e̲", foreground='#0563C1', cursor="hand2", justify="left", anchor='w')
        self.text = tk.Text(self.frame, width=27, height=8, wrap=tk.WORD)
        self.text.insert(tk.END, "GUI based application for reconstructing the folder structure of OneDrive")
        self.text.config(state='disable')
        self.scrollbv = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbv.set)
        self.ok = ttk.Button(self.frame, text="OK", takefocus=False, command=self.close_about)

        self.bind_events()

        self.frame.grid(row=0, column=0)
        self.place_widgets()

    def bind_events(self):
        self.label5.bind("<Double-Button-1>", self.callback)

    def place_widgets(self):
        self.label.grid(row=0, column=0, rowspan=6, padx=10, pady=(10, 0), sticky='n')
        self.label1.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky='w')
        self.label2.grid(row=1, column=1, sticky='w')
        self.label3.grid(row=2, column=1, sticky='w')
        self.label4.grid(row=3, column=1, sticky='w')
        self.label5.grid(row=4, column=1, padx=(0, 10), pady=(0, 10), sticky='w')
        self.text.grid(row=5, column=1, sticky='w')
        self.scrollbv.grid(row=5, column=2, padx=(0, 10), sticky="nsew")
        self.ok.grid(row=6, column=1, padx=(0, 10), pady=10, sticky='e')

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))

    def callback(self, event=None):
        webbrowser.open_new_tab("https://github.com/Beercow/OneDriveExplorer/releases/latest")
        self.label5.configure(foreground='#954F72')

    def close_about(self):
        self.root.unbind('<Configure>')
        self.win.unbind('<Configure>')
        self.win.destroy()


class SyncMessage:
    def __init__(self, root):
        self.root = root
        self.create_window()
        self.configure_window()
        self.create_widgets()
        self.bind_events()

    def create_window(self):
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("")
        self.win.iconbitmap(application_path + '/Images/titles/favicon.ico')
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)
        hwnd = get_parent(self.win.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)
        self.win.overrideredirect(1)

    def configure_window(self):
        reg_font = ("Segoe UI", 14, "normal")
        bold_font = ("Segoe UI", 16, "bold")
        self.bgf = style.lookup('Treeview', 'background')

        self.lbl_with_my_gif = AnimatedGif(self.win, application_path + '/Images/gui/load.gif', 0.1, self.bgf)
        self.label = ttk.Label(self.win, text="Please wait           ", font=bold_font, background=self.bgf)
        self.label1 = ttk.Label(self.win, text="Working...", font=reg_font, background=self.bgf)

    def create_widgets(self):
        self.lbl_with_my_gif.grid(row=0, column=0, rowspan=2)
        self.label.grid(row=0, column=1, sticky="nsew")
        self.label1.grid(row=1, column=1, sticky="nsew")
        self.lbl_with_my_gif.start()

    def bind_events(self):
        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)
        self.root.bind("<Map>", self.bring_window_back)

    def bring_window_back(self, e):
        self.win.attributes('-topmost', 1)
        self.win.attributes('-topmost', 0)

    def sync_windows(self, event=None):
        on_top = self.root.tk.eval('wm stackorder '+str(self.win)+' isabove '+str(self.root))
        if on_top == '0':
            self.bring_window_back(event)

        if 'thread_load' in str(threading.enumerate()) and len(threading.enumerate()) <= 4:
            self.root.unbind("<Configure>")
            self.root.unbind("<Map>")
            self.win.destroy()
        if len(threading.enumerate()) <= 3:
            self.root.unbind("<Configure>")
            self.root.unbind("<Map>")
            self.win.destroy()
        try:
            x = self.root.winfo_x()
            qw = self.win.winfo_width()
            y = self.root.winfo_y()
            qh = self.win.winfo_height()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))
        except Exception:
            pass

    def close_sync(self):
        self.root.unbind("<Configure>")
        self.root.unbind("<Map>")
        self.win.destroy()

    def __callback(self):
        return


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()

        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
            if index == "":
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index}+{count.get()}c")
            self.tag_add(tag, "matchStart", "matchEnd")


class Result:

    def __init__(self, master, *args, folder=True, folderShared='', tags=''):
        self.master = master
        self.args = args
        self.folder = folder
        self.folderShared = folderShared
        self.tags = tags
        self.type = []
        self.status = []
        self.sha1 = hashlib.sha1()
        self.lock_list = ['AddListItems',
                          'EditListItems',
                          'DeleteListItems',
                          'DeleteVersions',
                          'ManageLists']

        self.process_args()

    def process_args(self):
        values_list = list(self.args[0])
        text = ''
        image_key = self.args[2]

        if image_key == str(root_drive_img):
            text = f'  {self.args[0][1]}\n  {self.args[0][2]}'
            self.type.append(hdd_big_img)
            self.folder = False

        elif image_key in [str(od_folder_img), str(od_p_folder_img), str(tenant_sync_img)]:
            spoPermissions = next(
                (ast.literal_eval(item.split('spoPermissions: ')[1]) for item in self.args[0] if 'spoPermissions: ' in item),
                ''
            )

            if '+' in self.args[0][2]:
                self.type.append(building_big_img)
            else:
                if image_key == str(od_p_folder_img):
                    self.type.append(cloud_p_big_img)
                else:
                    self.type.append(cloud_big_img)
            if not set(self.lock_list).intersection(spoPermissions) and '!' not in self.args[0][2]:
                self.status.append(locked_big_img)
            scope_item = next((value for value in self.args[0] if 'scopeid:' in value.lower()), None)
            remote_path_item = next((value for value in self.args[0] if 'remotepath:' in value.lower()), None)
            text = f'  {scope_item}\n  {remote_path_item}'
        else:
            name_item = next((value for value in self.args[0] if 'name:' in value.lower()), None)
            path_item = next((value for value in self.args[0] if 'path:' in value.lower()), None)
            text = f'  {name_item}\n  {path_item}'
            self.process_folder_status(values_list)

        values = tuple(values_list)
        image_creator = CreateImage(self.status, self.type)
        image_sha1 = image_creator.sha1_digest
        self.insert_into_treeview(self.args[1], image_sha1, text, values)

    def process_folder_status(self, values_list):
        if self.folder:
            folderColor = next((item.split(' ')[1] for item in self.args[0] if 'foldercolor:' in item.lower() and len(item.split(' ')) > 1), 0)
            if int(folderColor) in range(1, 16):
                self.type.append(self.get_folder_color(folderColor))
            else:
                self.type.append(directory_big_img)

            for num in ['5', '7', '9', '10', '11', '12']:
                if any('folderstatus:' in item.lower() and num in item for item in self.args[0]):
                    self.handle_folder_status(num, values_list)

        else:
            self.process_non_folder_status(values_list)

    def handle_folder_status(self, num, values_list):
        spoPermissions = next(
            (ast.literal_eval(item.split('spoPermissions: ')[1]) for item in self.args[0] if 'spoPermissions: ' in item),
            ''
        )

        # Might need to look into this.
        if num == '7' and len(values_list) > 13:
            shortcut_item = next((item for item in self.args[0] if 'shortcutitemindex:' in item.lower()), None)
            if shortcut_item and int(shortcut_item.split(' ')[1]) > 0:
                self.type.clear()
                self.type.append(vault_big_img if any(item == 'itemIndex: 0' for item in self.args[0]) else vault_open_big_img)
            else:
                self.type.append(link_big_img)
        elif num == '7':
            pass
        elif num == '5':
            self.status.append(self.get_status_image(num))
        else:
            self.type.append(self.get_type_image(num))

        sharedItem = next(
                (item.split(' ')[1] for item in self.args[0] if 'shareditem:' in item.lower() and len(item.split(' ')) > 1), 
                ''
            )

        if sharedItem == '1':
            self.status.append(shared_big_img)

        if not set(self.lock_list).intersection(spoPermissions):
            if len(spoPermissions) > 0:
                self.status.append(locked_big_img)

    def process_non_folder_status(self, values_list):
        if len(values_list) != 3:
            self.type.append(file_del_big_img) if self.tags == 'red' else self.type.append(file_yellow_big_img)
            values_list[0] = f'  Date modified: {self.args[0][0]}\n  Size: {self.args[0][1]}'
            spoPermissions = next(
                (ast.literal_eval(item.split('spoPermissions: ')[1]) for item in self.args[0] if 'spoPermissions: ' in item),
                ''
            )
            sharedItem = next(
                (item.split(' ')[1] for item in self.args[0] if 'shareditem:' in item.lower() and len(item.split(' ')) > 1),
                ''
            )

            hydrationType = next((item.split(' ')[1] for item in self.args[0] if 'lasthydrationtype:' in item.lower() and len(item.split(' ')) > 1), '')

            lastKnownPinState = next((item.split(' ')[1] for item in self.args[0] if 'lastknownpinstate:' in item.lower() and len(item.split(' ')) > 1), '')

            for num in ['2', '5', '6', '7', '8']:
                if any(('filestatus:' in item.lower() or 'inrecyclebin:' in item.lower()) and num in item for item in self.args[0]):
                    if lastKnownPinState in ['0', '1'] and num == '2':
                        self.status.append(self.get_pin_state(lastKnownPinState))
                    elif hydrationType.lower() == 'passive' and num == '2':
                        self.status.append(always_available_big_img)
                    elif num == '6' or num == '7':
                        self.type.append(self.get_type_image(num))
                        self.status.append(self.get_status_image(num))
                    else:
                        self.status.append(self.get_status_image(num))

            if sharedItem == '1' or self.folderShared == '1':
                self.status.append(shared_big_img)

            if not set(self.lock_list).intersection(spoPermissions) and not any('inrecyclebin:' in item.lower() for item in self.args[0]):
                self.status.append(locked_big_img)

    def get_folder_color(self, num):
        folder_color = {
            '1': f_1_big_img,
            '2': f_2_big_img,
            '3': f_3_big_img,
            '4': f_4_big_img,
            '5': f_5_big_img,
            '6': f_6_big_img,
            '7': f_7_big_img,
            '8': f_8_big_img,
            '9': f_9_big_img,
            '10': f_10_big_img,
            '11': f_11_big_img,
            '12': f_12_big_img,
            '13': f_13_big_img,
            '14': f_14_big_img,
            '15': f_15_big_img
        }
        return folder_color[num]

    def get_type_image(self, num):
        type_dict = {
            '6': not_sync_big_img,  # files
            '7': not_link_big_img,  # files
            '9': sync_big_img,
            '10': not_sync_big_img,  # folders
            '11': not_link_big_img,  # folders
            '12': unknown_big_img
        }
        return type_dict[num]

    def get_status_image(self, num):
        status_dict = {
            '2': available_big_img,
            '5': excluded_big_img,
            '6': online_not_sync_big_img,
            '7': online_not_link_big_img,
            '8': online_big_img,
            '9': sync_big_img,
            '10': not_sync_big_img,
            '11': not_link_big_img
        }
        return status_dict[num]

    def get_pin_state(self, num):
        pin_state = {
            '0': available_big_img,
            '1': always_available_big_img
        }
        return pin_state[num]

    def insert_into_treeview(self, iid, image_sha1, text, values):
        tvr.insert("", "end", iid=iid, image=s_image[image_sha1], text=text, values=values, tags=self.tags)


class PopupManager:
    def __init__(self, root, tv, application_path, details, breadcrumb):
        self.root = root
        self.tv = tv
        self.application_path = application_path
        self.details = details
        self.breadcrumb = breadcrumb

        self.rof_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/Icon11.ico'))
        self.copy_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/copy.png'))
        self.name_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/file_yellow_empty_new.png'))
        self.path_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/file_yellow_open.png'))
        self.details_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/language_window.png'))
        self.exp_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/hierarchy1_expanded.png'))
        self.col_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/hierarchy1.png'))
        self.log_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/table_new.png'))

    def do_popup(self, event):
        try:
            curItem = event.widget.identify_row(event.y)
            event.widget.selection_set(curItem)
            opened = event.widget.item(curItem, 'open')
            values = event.widget.item(curItem, 'values')
            image = event.widget.item(curItem, 'image')
            popup = tk.Menu(self.root, tearoff=0)
            copymenu = tk.Menu(self.root, tearoff=0)

            if image[0] == str(root_drive_img):
                popup.add_command(label="Remove OneDrive Folder",
                                  image=self.rof_img,
                                  compound='left',
                                  command=lambda: self.thread_del_folder(curItem))
                popup.add_separator()

            if image[0] != str(del_img):
                popup.add_cascade(label="Copy",
                                  image=self.copy_img,
                                  compound='left',
                                  menu=copymenu)

                if image[0] != str(tenant_sync_img) and image[0] != str(od_folder_img):
                    copymenu.add_command(label="Name",
                                         image=self.name_img,
                                         compound='left',
                                         command=lambda: self.copy_name(values))
                    copymenu.add_command(label="Path",
                                         image=self.path_img,
                                         compound='left',
                                         command=lambda: self.copy_path(values))
                copymenu.add_command(label="Details",
                                     image=self.details_img,
                                     compound='left', command=lambda: self.copy_details())

            if image[0] == str(root_drive_img):
                popup.entryconfig("Copy", state='disable')
            else:
                if image[0] != str(del_img):
                    popup.entryconfig("Copy", state='normal')

            if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame.!treeview':
                if image[0] != str(del_img):
                    popup.add_separator()
                popup.add_command(label="Expand folders",
                                  image=self.exp_img, compound='left',
                                  command=lambda: self.open_children(curItem),
                                  accelerator="Alt+Down")
                popup.add_command(label="Collapse folders",
                                  image=self.col_img,
                                  compound='left',
                                  command=lambda: self.close_children(curItem),
                                  accelerator="Alt+Up")
                if opened:
                    popup.entryconfig("Collapse folders", state='normal')
                else:
                    popup.entryconfig("Collapse folders", state='disable')
            le = None
            for item in infoFrame.winfo_children():
                if '.!notebook.!frame.!mytable' in str(item):
                    le = item
            if le:
                copymenu.add_command(label="Log Entries",
                                     image=self.log_img,
                                     compound='left', command=lambda: le.doExport())

            popup.tk_popup(event.x_root, event.y_root)
        except IndexError:
            pass
        finally:
            popup.grab_release()

    def open_children(self, parent):
        self.tv.item(parent, open=True)  # open parent
        for child in self.tv.get_children(parent):
            self.open_children(child)  # recursively open children

    def close_children(self, parent):
        self.tv.item(parent, open=False)  # close parent
        for child in self.tv.get_children(parent):
            self.close_children(child)  # recursively close children

    def copy_details(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.details.get("1.0", tk.END))

    def copy_path(self, values):
        # Find the items containing 'Name:' and 'Path:'
        name_item = next((value for value in values if 'name:' in value.lower()), None)
        path_item = next((value for value in values if 'path:' in value.lower()), None)

        # Construct the line if both items are found
        if name_item and path_item:
            line = f'{name_item.split("Name: ")[1]}: {path_item.split("Path: ")[1]}\\{name_item.split("Name: ")[1]}'
        else:
            line = ''

        self.root.clipboard_clear()
        self.root.clipboard_append(line)

    def copy_name(self, values):
        name_item = next((value for value in values if 'name:' in value.lower()), None)
        self.root.clipboard_clear()
        self.root.clipboard_append(name_item.split("Name: ")[1])

    def thread_del_folder(self, iid):
        global sync_message
        message.unbind('<Double-Button-1>', bind_id)
        value_label['text'] = ''
        sync_message = SyncMessage(root)
        t1 = threading.Thread(target=self.del_folder, args=(iid,), daemon=True)
        t1.start()
        root.after(200, check_if_ready, t1, "df")

    def del_folder(self, iid):
        global proj_name
        widgets_disable()
        search_entry.delete(0, 'end')
        search_entry.configure(state="disabled")
        search_entry.configure(cursor='arrow')
        btn.configure(state="disabled")
        clear_search()
        self.breadcrumb.clear()
        self.tv.grid_forget()
        file_manager.tv2.delete(*file_manager.tv2.get_children())
        file_manager.tv3.delete(*file_manager.tv3.get_children())
        self.details.config(state='normal')
        self.details.delete('1.0', tk.END)
        self.details.config(state='disable')
        delete_item_and_descendants(self.tv, iid)
        tv.delete(*tv.get_children(iid))
        tv.delete(iid)
        self.tv.grid(row=1, column=0, sticky="nsew")
        if len(self.tv.get_children()) == 0:
            odsmenu.entryconfig("Unload all files", state='disable')
            file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')
            if len(tv_frame.tabs()) == 1:
                projmenu.entryconfig("Save", state='disable')
                root.unbind('<Alt-s>')
                projmenu.entryconfig("SaveAs", state='disable')
                projmenu.entryconfig("Unload", state='disable')
                proj_name = None

        widgets_normal()


class ToolTipManager:
    def __init__(self):
        self.tipwindow = None
        self.current_tab = None

    def create_tooltip(self, widget, text, flip=False, single=False, motion=False):
        def enter(event, motion=False):
            self.show_tip(text, widget, flip, single)

        def leave(event):
            self.hide_tip()

        if motion:
            widget.after(1000, enter(None, motion=True))
        else:
            widget.bind('<Enter>', lambda event: widget.after(500, enter(event)))

        widget.bind('<Leave>', leave)

    def motion(self, event):
        if len(threading.enumerate()) > 3:
            return
        if event.widget.identify(event.x, event.y) == 'label':
            index = event.widget.index("@%d,%d" % (event.x, event.y))
            if index != 0:
                text = 'ODL Logs\n  Files contain to troubleshoot synchronization issues\n  caused by editing files offline in the desktop version\n  of OneDrive.'
            if self.current_tab != event.widget.tab(index, 'text'):
                self.current_tab = event.widget.tab(index, 'text')
                if event.widget.tab(index, 'text') == 'Details':
                    text = 'Details\n  Displays detailed information of the file/folder selected.'
                elif event.widget.tab(index, 'text') == 'Metadata':
                    text = 'Metadata\n  Displays metadata information of the file selected.\n  Created by, modified by, etc...'
                elif event.widget.tab(index, 'text') == 'MetadataJSON':
                    text = 'MetadataJSON\n  Displays metadata information of image/audio/video\n  file selected.'
                elif event.widget.tab(index, 'text') == 'filePolicies':
                    text = 'filePolicies\n  Displays policy information applied to the file selected.'
                elif event.widget.tab(index, 'text') == 'Log Entries':
                    text = 'Log Entries\n  Displays related logs to the file/folder selected. This\n  will only be populated if OneDrive logs are parsed\n  along with the <userCid>.dat file.'
                elif event.widget.tab(index, 'text') == 'OneDrive Folders  ':
                    text = 'OneDrive Folders\n  Displays the <UserCid>.dat files that have been loaded\n  and the folder structure of OneDrive.'
                self.create_tooltip(event.widget, text, flip=False, single=False, motion=True)
        elif event.widget.identify(event.x, event.y) == 'clear':
            if 'invalid' not in search_entry.state():
                search_entry.config(cursor='arrow')
                text = 'Clear\n        '
                self.create_tooltip(event.widget, text, flip=False, single=True, motion=True)
        else:
            search_entry.config(cursor='xterm')
            self.hide_tip()
            self.current_tab = None

    def show_tip(self, text, widget, flip=False, single=False):
        matches = ["start_parsing", "live_system", "odl", "load_project", "proj_parse"]

        if self.tipwindow or not text:
            return

        if any(x in str(threading.enumerate()) for x in matches):
            return

        x, y, cx, cy = widget.bbox(1)
        if flip:
            x = x + widget.winfo_pointerx() - 330
            y = y + cy + widget.winfo_pointery() + 20 - 90
        elif single:
            x = x + widget.winfo_pointerx()
            y = y + cy + widget.winfo_pointery()
        else:
            x = x + widget.winfo_pointerx()
            y = y + cy + widget.winfo_pointery() + 20

        self.tipwindow = tw = tk.Toplevel(widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        text = text.split('\n', 1)
        h = (text[1].count('\n') + 2)
        if single:
            h = 1
        reg_font = ("Segoe UI", 8, "normal")
        w = tkFont.Font(family="Segoe UI", size=8, weight="normal").measure(max(text[1].split('\n'), key=len))
        w2 = tkFont.Font(family="Segoe UI", size=8, weight="normal").metrics('linespace')
        h2 = w2 * (text[1].count('\n') + 2)

        if single:
            frame = tk.Frame(tw, width=w + 20, height=h2 - 1, background="grey81", padx=1, pady=1)
        else:
            frame = tk.Frame(tw, width=w + 20, height=h2 + 12, background="grey81", padx=1, pady=1)
        textbox = tk.Text(frame, height=h, font=reg_font, padx=8, relief="flat", bd=0, pady=5)

        bold_font = ("Segoe UI", 8, "bold")
        textbox.tag_configure("bold", font=bold_font)
        textbox.tag_configure("regular", font=reg_font)
        textbox.insert('end', text[0] + '\n', 'bold')
        textbox.insert('end', text[1], 'regular')
        textbox.configure(state='disable')

        frame.pack()
        frame.pack_propagate(0)
        textbox.pack()

        widget.after(5000, lambda: tw.destroy())

    def hide_tip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class FileManager:
    def __init__(self, tv, parent, cur_sel, handle, columns=('Date_created', 'Date_accessed', 'Date_modified', 'Size')):
        self.tv = tv
        self.bgf = style.lookup('Treeview', 'background')
        self.parent = parent
        self.columns = columns
        self.cur_sel = cur_sel
        self.handle = handle
        self.breadcrumb_list = breadcrumb
        self.stop = threading.Event()
        self.status = []
        self.file = False

        # Boolean variables for checkbuttons
        self.dateCreated = tk.BooleanVar(value=menu_data['Date_created'])
        self.dateAccessed = tk.BooleanVar(value=menu_data['Date_accessed'])
        self.dateModified = tk.BooleanVar(value=menu_data['Date_modified'])
        self.size = tk.BooleanVar(value=menu_data['Size'])

        # Treeview for the current directory
        self.tv2 = ttk.Treeview(parent, selectmode='browse', takefocus='false')

        # Treeview for the detailed information in a separate tab
        self.tab2 = ttk.Frame(parent)
        self.tv3 = ttk.Treeview(self.tab2, columns=columns, selectmode='browse', takefocus='false')

        self.fscrollbv = ttk.Scrollbar(self.tab2, orient="vertical", command=self.multiple_yview)
        self.tv2.configure(yscrollcommand=self.fscrollbv.set)
        self.tv3.configure(yscrollcommand=self.fscrollbv.set)

        self.configure_treeview()
        self.configure_columns()
        self.configure_tags()
        self.configure_bindings()

    def configure_treeview(self):
        self.tv2.heading('#0', text=' Name', command=lambda c='#0': self.sort_treeviews_mixed(self.tv2, self.tv3, c, True), anchor='w')
        self.tv2.column('#0', minwidth=80, width=170, stretch=True, anchor='w')
        self.tv3.heading('#0', text=' Status', anchor='w')
        self.tv3.heading('Date_created', text=' Date_created', command=lambda c='Date_created': self.sort_treeviews_mixed(self.tv3, self.tv2, c, False), anchor='w')
        self.tv3.heading('Date_accessed', text=' Date_accessed', command=lambda c='Date_accessed': self.sort_treeviews_mixed(self.tv3, self.tv2, c, False), anchor='w')
        self.tv3.heading('Date_modified', text=' Date_modified', command=lambda c='Date_modified': self.sort_treeviews_mixed(self.tv3, self.tv2, c, False), anchor='w')
        self.tv3.heading('Size', text=' Size', command=lambda c='Size': self.sort_treeviews_mixed(self.tv3, self.tv2, c, False), anchor='w')
        self.tv3.column('#0', minwidth=80, width=100, stretch=False, anchor='w')
        self.tv3.column('Date_created', minwidth=120, width=120, stretch=False, anchor='w')
        self.tv3.column('Date_accessed', minwidth=120, width=120, stretch=False, anchor='w')
        self.tv3.column('Date_modified', minwidth=120, width=120, stretch=False, anchor='w')
        self.tv3.column('Size', minwidth=70, width=80, stretch=False, anchor='e')

        self.tv3.grid(row=0, column=0, sticky="nsew")
        self.fscrollbv.grid(row=0, column=1, sticky="nsew")

        self.tab2.grid_rowconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(0, weight=1)

    def configure_tags(self):
        self.tv2.tag_configure('red', foreground="red")
        self.tv3.tag_configure('red', foreground="red")

    def configure_bindings(self):
        for tv in [self.tv2, self.tv3]:
            tv.bind('<<TreeviewSelect>>', self.multiple_select)
            tv.bind("<Button-3>", popup_manager.do_popup)
            tv.bind('<MouseWheel>', self.multiple_yview_scroll)

        self.tv2.bind('<Button-1>', self.handle_click)
        self.tv2.bind('<Button-3>', self.on_click)
        self.tv3.bind('<Button-3>', self.on_click)
        self.tv2.bind('<Motion>', self.handle_click)
        self.tv2.bind('<Double-Button-1>', self.handle_double_click)
        self.tv3.bind('<Double-Button-1>', self.handle_double_click)

    def configure_columns(self):
        visableColumns = []
        if self.dateCreated.get():
            visableColumns.append("Date_created")
        if self.dateAccessed.get():
            visableColumns.append("Date_accessed")
        if self.dateModified.get():
            visableColumns.append("Date_modified")
        if self.size.get():
            visableColumns.append("Size")

        menu_data['Date_created'] = self.dateCreated.get()
        menu_data['Date_accessed'] = self.dateAccessed.get()
        menu_data['Date_modified'] = self.dateModified.get()
        menu_data['Size'] = self.size.get()

        with open("ode.settings", "w") as jsonfile:
            json.dump(menu_data, jsonfile)

        self.tv3["displaycolumns"] = visableColumns

    def on_click(self, event):
        region = self.tv3.identify("region", event.x, event.y) or self.tv2.identify("region", event.x, event.y)
        if region == "heading" or region == "separator":

            # Create a Toplevel window to act as the "menu"
            headerMenu = tk.Toplevel(self.parent)
            headerMenu.wm_overrideredirect(True)  # Remove window decorations (border, title bar)
            headerMenu.geometry(f"+{event.x_root}+{event.y_root}")  # Position at the cursor location

            headerFrame = ttk.Frame(headerMenu, borderwidth=2, relief="solid")
            headerFrame.pack()

            ttk.Label(headerFrame, text="Select Columns").pack(padx=10, pady=(10, 0))
            # Create checkbuttons inside the Toplevel window
            ttk.Checkbutton(headerFrame, text="Date created", variable=self.dateCreated).pack(anchor='w', padx=10, pady=(10, 0))
            ttk.Checkbutton(headerFrame, text="Date accessed", variable=self.dateAccessed).pack(anchor='w', padx=10)
            ttk.Checkbutton(headerFrame, text="Date modified", variable=self.dateModified).pack(anchor='w', padx=10)
            ttk.Checkbutton(headerFrame, text="Size", variable=self.size).pack(anchor='w', padx=10, pady=(0, 10))

            # Function to close the menu when clicking outside
            def close_menu(event):
                self.configure_columns()
                headerMenu.destroy()  # Destroy the Toplevel window

            # Bind the FocusOut event to close the menu
            headerFrame.bind("<FocusOut>", close_menu)

            # Ensure the Toplevel menu is focused, so that it closes when clicking outside
            headerMenu.focus_set()

    def sort_treeviews_mixed(self, tree1, tree2, col, descending):
        # Sort tree1 by the tag first and then the specified column
        if col == '#0':  # If sorting by the tree's label column
            data = [(tree1.item(item, 'text'), item) for item in tree1.get_children('')]
        else:
            data = [(tree1.set(item, col), item) for item in tree1.get_children('')]

        # Get the tags for each item
        data_with_tags = [(self.tv3.item(item, 'tags')[0], row, item) for row, item in data]

        # Sort first by tag and then by the selected column
        if col == 'Size':
            sorted_data = sorted(data_with_tags, key=lambda x: (int(x[0]), self.extract_number(x[1])), reverse=descending)
        else:
            sorted_data = sorted(data_with_tags, key=lambda x: (x[0], x[1].lower()), reverse=descending)

        # Apply the sorted order to tree1 and tree2
        for index, (tags, val, item) in enumerate(sorted_data):
            tree1.move(item, '', index)
            tree2.move(item, '', index)

        # Reverse sort next time for both treeviews
        try:
            tree1.heading(col, command=lambda: self.sort_treeviews_mixed(tree1, tree2, col, not descending))
            tree2.heading(col, command=lambda: self.sort_treeviews_mixed(tree1, tree2, col, not descending))
        except Exception:
            pass

    def extract_number(self, s):
        match = re.search(r'\d+', s.replace(',', ''))
        return int(match.group()) if match else 0

    def handle_click(self, event):
        if self.tv2.identify_region(event.x, event.y) == "separator":
            return "break"

    def handle_double_click(self, event):
        cur_item = event.widget.selection()
        values = list(event.widget.item(cur_item, 'values'))
        if not any(('folderStatus:' in item or 'webURL:' in item) for item in values):
            # This is were I need to look for file selection
            try:
                if values[2] == '':
                    pass
                elif len(pwh.panes()) == 3:
                    for key, val in file_items.items():
                        if cur_item[0] in val:
                            self.file = cur_item[0]
                            parent = self.tv.parent(key)
                            self.tv.selection_set(key)
                            item_id = key
                else:
                    return
            except Exception:
                return
        else:
            parent = self.tv.parent(cur_item[0])
            self.tv.selection_set(cur_item[0])
            item_id = cur_item[0]
        while True:
            if item_id:
                parent = self.tv.parent(item_id)
            if parent:
                self.tv.item(parent, open=True)
                item_id = parent
            else:
                break

        clear_search()

    def multiple_yview(self, *args):
        self.tv2.yview(*args)
        self.tv3.yview(*args)

    def multiple_yview_scroll(self, event):
        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame3.!treeview':
            self.tv2.yview_scroll(-1 * int(event.delta / 120), "units")
        elif str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!treeview':
            self.tv3.yview_scroll(-1 * int(event.delta / 120), "units")

    def multiple_select(self, event):
        try:
            if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!treeview':
                cur_item = self.tv2.selection()
                cur_item2 = self.tv3.selection()
                if not cur_item2:
                    cur_item2 = ('0',)
                if cur_item[0] != cur_item2[0]:
                    self.tv3.selection_set(cur_item[0])

            elif str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame3.!treeview':
                cur_item = self.tv3.selection()
                cur_item2 = self.tv2.selection()
                if not cur_item2:
                    cur_item2 = ('0',)
                if cur_item[0] != cur_item2[0]:
                    self.tv2.selection_set(cur_item[0])
                self.new_selection(event)

        except Exception:
            pass

    def new_selection(self, event):
        matches = ["start_parsing", "live_system", "odl", "load_project", "proj_parse"]
        if any(x in str(threading.enumerate()) for x in matches):
            return

        cur_item = event.widget.selection()

        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame.!treeview':
            self.file_pane()
        self.select_item(event)

        try:
            if self.cur_sel == f'{event.widget}{cur_item[0]}':
                return
        except Exception:
            return
        else:
            self.cur_sel = f'{event.widget}{cur_item[0]}'

            if menu_data['odl_cor']:
                t1 = threading.Thread(target=self.get_info,
                                      args=(event,),
                                      daemon=True)

                if 'get_info' not in str(threading.enumerate()):
                    self.stop.clear()
                    t1.start()
                else:
                    self.stop.set()

    def select_item(self, event):
        cur_item = event.widget.selection()
        if cur_item == ():
            return
        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame3.!treeview':
            values = list(self.tv2.item(cur_item, 'values'))
        else:
            values = list(event.widget.item(cur_item, 'values'))
        if len(values) > 4:
            if values[0] != '':
                # Check for 'inRecycleBin' in any value
                in_recycle_bin = any('inrecyclebin' in value.lower() for value in values)
                # Determine the timestamp based on the conditions
                timestamp = "notificationTime: " if in_recycle_bin and values[1] == '' else ("DeleteTimeStamp: " if in_recycle_bin else "lastChange: ")

                if 'Date modified' in str(values[0]):
                    values[0] = str(values[0])[17:].split("\n")[0]
                values[0] = f'{timestamp}{values[0]}'
                values[1] = f'size: {values[1]}'

        try:
            tags = event.widget.item(cur_item, 'tags')[0]
        except Exception:
            tags = ''
        details.config(state='normal')
        details.delete('1.0', tk.END)
        for tab_index in reversed(range(1, details_frame.tab_count())):
            details_frame.delete_tab(tab_index)
        try:
            for line in values:
                if line == '' or line.startswith(('Metadata:', 'ListSync:', 'folderColor:')):
                    if line.startswith('Metadata:'):
                        _, value = line.split(": ", 1)
                        if not value:
                            continue
                        meta_result = ast.literal_eval(value)
                        tab2 = details_frame.add_tab('Metadata')
                        self.meta_frame = details_frame.add_frame(tab2)
                        self.get_resourceID(meta_result)
                        continue
                    if line.startswith('ListSync:'):
                        _, value = line.split(": ", 1)
                        if not value:
                            continue
                        offline_result = ast.literal_eval(value)
                        self.get_resourceID(offline_result)
                        continue
                    continue
                details.insert(tk.END, f'{line}\n', tags)
        except IndexError:
            pass

        details.config(state='disable')

    def get_resourceID(self, df_result):
        self.header_labels = []
        self.key_labels = []
        self.value_labels = []
        row_num = 0
        for key, value in df_result.items():
            if key == 'graphMetadataJSON':
                self.get_graphMetadataJSON(value)
                continue
            if key == 'filePolicies':
                self.get_filePolicies(value)
                continue
            if key == 'MediaServiceMetadata':
                self.get_ocr(value)
                continue
            if key == 'SharedWithDetails':
                self.get_shared_with(value)
                continue
            try:
                self.add_label_to_frame(self.meta_frame, key, value, row_num)
                row_num += 1
            except Exception:
                pass

    def get_graphMetadataJSON(self, value):
        if not value:
            return

        tab3 = details_frame.add_tab('MetadataJSON')
        self.json_frame = details_frame.add_frame(tab3)
        row_num = 0

        for k, v in value.items():
            if isinstance(v, dict):
                header_label = LabelSeparator(self.json_frame, text=f"{k}", width=15)
                header_label.grid(row=row_num, column=0, columnspan=2, sticky="ew")
                row_num += 1
                self.header_labels.append(header_label)

                for a, b in v.items():
                    key_label = HighlightableTextBox(self.json_frame, text=f"{a}:", font=default_font, wraplength='165p')
                    key_label.label.grid(row=row_num, column=0, padx=(0, 2), pady=(0, 5), sticky="nw")
                    self.key_labels.append(key_label)

                    value_label = HighlightableTextBox(self.json_frame, text=str(b), font=default_font, wraplength='165p')
                    value_label.label.grid(row=row_num, column=1, padx=(2, 0), pady=(0, 5), sticky="w")
                    self.value_labels.append(value_label)

                    row_num += 1

            else:
                logging.error(f'Issue parsing graphMetadataJSON. {type(v)} {k}:{v}')

    def get_filePolicies(self, value):
        if not value:
            return

        tab4 = details_frame.add_tab('filePolicies')
        policy_frame = details_frame.add_frame(tab4)

        row_num = 0

        for k, v in value.items():
            if isinstance(v, list):
                self.add_list_to_frame(policy_frame, k, v, row_num)
            else:
                self.add_label_to_frame(policy_frame, k, v, row_num)
            row_num += 1

        return policy_frame

    def get_ocr(self, value):
        if not value:
            return
        tab5 = details_frame.add_tab('OCR_Data')
        self.ocr_frame = details_frame.add_textbox(tab5)
        self.ocr_frame.insert(tk.END, f'{value}')
        self.ocr_frame.configure(font=default_font, background=bgf, foreground=fgf, relief='flat', undo=False, spacing3=3, width=50, padx=10, pady=10, state='disable')

        return self.ocr_frame

    def get_shared_with(self, value):
        if not value:
            return
        formatted_data = [
            (k.split("|")[-1], self.convert_timestamp(v["DateTime"]), v["LoginName"])
            for k, v in value.items()
        ]

        tab6 = details_frame.add_tab('SharedWith')

        self.tree = details_frame.add_treeview(tab6, columns=("Shared with", "Date", "Shared by"))
        self.tree.heading("Shared with", text="Shared with")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Shared by", text="Shared by")

        for row in formatted_data:
            self.tree.insert("", tk.END, values=row)

        self.autosize_and_expand(self.tree)

        return self.tree

    # Function to convert SharePoint timestamp to readable format
    def convert_timestamp(self, sp_timestamp):
        timestamp = int(sp_timestamp.strip("/Date()")) // 1000  # Convert to seconds
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def autosize_and_expand(self, tree):
        for col in tree["columns"]:
            tree.column(col, width=tkFont.Font().measure(col), stretch=True)

            max_width = 100  # Minimum width
            for item in tree.get_children():
                text = tree.item(item, "values")[tree["columns"].index(col)]
                max_width = max(max_width, tkFont.Font().measure(text) + 10)

            tree.column(col, width=max_width, minwidth=max_width)

    def add_list_to_frame(self, parent_frame, label_text, items, row_num):
        header_label = LabelSeparator(parent_frame, text=label_text, width=15)
        header_label.grid(row=row_num, column=0, columnspan=2, sticky="ew")
        self.header_labels.append(header_label)
        row_num += 1

        for item in items:
            if isinstance(item, dict):
                self.add_dict_to_frame(parent_frame, item, row_num)
                row_num += 1
            else:
                self.add_label_to_frame(parent_frame, '', item, row_num)
                row_num += 1

    def add_dict_to_frame(self, parent_frame, dictionary, row_num):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.header_frame_label = ttk.Label(parent_frame, text=f"{key}", font=default_font, background=self.bgf)
                self.header_frame = tk.LabelFrame(parent_frame, labelwidget=self.header_frame_label, padx=5, labelanchor="nw", bg=self.bgf)
                self.header_frame.grid(row=row_num, column=0, columnspan=2, sticky="ew")
                row_num += 1
                frow_num = 0
                for k, v in value.items():
                    self.add_label_to_frame(self.header_frame, k, v, frow_num)
                    frow_num += 1

                self.header_frame.bind('<Configure>', lambda event: self.update_theme())

            else:
                self.add_label_to_frame(parent_frame, key, value, row_num)
                row_num += 1

    def add_label_to_frame(self, parent_frame, key, value, row_num):
        key_label = HighlightableTextBox(parent_frame, text=f"{key}:", font=default_font, wraplength='165p')
        key_label.label.grid(row=row_num, column=0, padx=(0, 2), pady=(0, 5), sticky="nw")
        self.key_labels.append(key_label)

        value_label = HighlightableTextBox(parent_frame, text=str(value), font=default_font, wraplength='165p')
        value_label.label.grid(row=row_num, column=1, padx=(2, 0), pady=(0, 5), sticky="w")
        self.value_labels.append(value_label)

    def get_info(self, event):  # need to look into click performance
        df_list = []
        curItem = event.widget.selection()
        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame3.!treeview':
            values = self.tv2.item(curItem, 'values')
        else:
            values = event.widget.item(curItem, 'values')

        for item in root.winfo_children():
            for i in item.winfo_children():
                if '!mytable' in str(i):
                    df_list.append(i.model.df)

        if len(df_list) == 0:
            return

        for item in infoFrame.winfo_children():
            if '.!notebook.!frame.' in str(item):
                item.destroy()

        self.parent.update_idletasks()

        if len(values) <= 3:
            return

        infoNB.tab(infoFrame, text="Loading... ")
        root.update_idletasks()

        info = []

        # find logs for deleted files
        if any('inrecyclebin' in value.lower() for value in values):
            rid = next((value.split(" ")[1].split("+")[0] for value in values if 'resourceid:' in value.lower()), '')

            file_hash = next(
                (value.split("(")[1].strip(")") for value in values if 'sha1(' in value.lower() or 'quickxor(' in value.lower()),
                ''
            )

            if len(rid) != 0:
                info = pd.concat([df.loc[df.Params.astype('string').str.contains(rid, case=False, na=False)] for df in df_list])
            elif len(file_hash) != 0:
                if any('sha1(' in value.lower() for value in values):
                    info = pd.concat([df.loc[df.Params.astype('string').str.contains(file_hash, case=False, na=False)] for df in df_list])
                if any('quickxor(' in value.lower() for value in values):
                    data = ''.join(['{:02x}'.format(i) for i in base64.b64decode(file_hash)])
                    info = pd.concat([df.loc[df.Params.astype('string').str.contains(data, case=False, na=False)] for df in df_list])
            else:
                infoNB.tab(infoFrame, text="Log Entries")
                return

        # find logs for files/folders
        if any('status:' in value.lower() for value in values):
            # Find the item containing 'resourceID:' and extract the desired part
            resourceID = next((value.split(" ")[1].split("+")[0] for value in values if value.lower().startswith('resourceid:')), '')
            # Concatenate DataFrames containing the resource_id
            info = pd.concat([df.loc[df.Params.astype('string').str.contains(f'{resourceID}', case=False, na=False)] for df in df_list])

        if len(info) == 0 or stop.is_set():
            infoNB.tab(infoFrame, text="Log Entries")
            try:
                if event.widget.selection()[0] != curItem[0]:
                    stop.clear()
                    threading.Thread(target=self.get_info,
                                     args=(event,),
                                     daemon=True).start()
                return
            except Exception:
                return

        pt = pandastablepatch.MyTable(infoFrame,
                                      dataframe=info,
                                      maxcellwidth=900,
                                      showtoolbar=False,
                                      showstatusbar=False,
                                      enable_menus=True,
                                      editable=False)
        pt.adjustColumnWidths()
        pt.show()
        pt.redraw()

        if stop.is_set():
            for item in infoFrame.winfo_children():
                if '.!notebook.!frame.' in str(item):
                    item.destroy()
            if tv.selection()[0] != curItem[0]:
                stop.clear()
                threading.Thread(target=self.get_info,
                                 args=(event,),
                                 daemon=True).start()
        infoNB.tab(infoFrame, text="Log Entries")

    def file_pane(self):
        self.status.clear()
        lock_list = ['AddListItems',
                     'EditListItems',
                     'DeleteListItems',
                     'DeleteVersions',
                     'ManageLists']

        image_mapping = {
            '2': available_img,
            '5': excluded_img,
            '6': online_not_sync_img,  # fileStatus
            '7': online_not_link_img,  # fileStatus
            '8': online_img,
            '9': online_sync_img,
            '10': online_not_sync_img,  # folderStatus
            '11': online_not_link_img  # folderStatus
        }

        pin_state = {
            '0': available_img,
            '1': always_available_img
        }

        cur_item = self.tv.selection()
        if len(cur_item) == 0:
            self.tv2.delete(*self.tv2.get_children())
            self.tv3.delete(*self.tv3.get_children())
            self.breadcrumb_list.append(cur_item)
            return

        self.breadcrumb_list.append(cur_item[0])

        for item in self.tv2.get_children():
            self.tv2.delete(item)

        for item in self.tv3.get_children():
            self.tv3.delete(item)

        for child in self.tv.get_children(cur_item):
            item_data = self.tv.item(child)
            image_key = item_data["image"][0]
            text = f' {item_data["text"]}'
            values = item_data["values"]
            tags = item_data["tags"][0] if item_data["tags"] else ''

            self.tv2.insert("", "end", iid=child, image=image_key, text=text, values=values, tags=tags)

            folderStatus = next((item.split(' ')[1] for item in values if 'folderstatus:' in item.lower() and len(item.split(' ')) > 1), '')

            spoPermissions = next(
                    (ast.literal_eval(item.split('spoPermissions: ')[1]) for item in values if 'spoPermissions: ' in item),
                    ''
            )

            if folderStatus == '7':
                if image_key == str(link_directory_img):
                    self.status.append(online_link_img)
                else:
                    self.status.append(online_img)
            else:
                self.status.append(image_mapping.get(folderStatus, online_img))

            sharedItemF = next(
                        (item.split(' ')[1] for item in values if 'shareditem:' in item.lower() and len(item.split(' ')) > 1), 
                        ''
                    )

            if sharedItemF == '1':
                self.status.append(shared_img)

            if not set(lock_list).intersection(spoPermissions) and str(tags) != 'red':
                if len(spoPermissions) > 0:
                    self.status.append(locked_img)

            image_creator = CreateImage(self.status)
            image_sha1 = image_creator.sha1_digest

            if not tags:
                tags = 1
            self.insert_into_treeview(child, image_sha1, values, tags)
            self.status.clear()

        try:
            if cur_item[0] in file_items:
                folderShared = next(
                    (item.split(' ')[1] for item in self.tv.item(cur_item[0])["values"] if 'shareditem:' in item.lower() and len(item.split(' ')) > 1),
                    ''
                )

                for i in file_items[cur_item[0]]:
                    self.status.clear()
                    item_data_i = self.tv.item(i)
                    image_key_i = item_data_i["image"][0]
                    text_i = f' {item_data_i["text"]}'
                    values_i = item_data_i["values"]

                    if values_i[0] == '':
                        # Find the item containing 'notificationtime:' and perform the operations
                        notification_time_item = next((value for value in values_i if 'notificationtime:' in value.lower()), '')

                        values_i[0] = notification_time_item[18:]
                        index = values_i.index(notification_time_item)
                        values_i[index] = 'DeleteTimeStamp: '

                    tags_i = item_data_i["tags"][0] if item_data_i["tags"] else ''

                    heading_text = ' Date_deleted' if tags_i else ' Date_modified'
                    self.tv3.heading('Date_modified', text=heading_text, anchor='w')

                    self.tv2.insert("", "end", iid=i, image=image_key_i, text=text_i, values=values_i, tags=tags_i)

                    fileStatus = next((item.split(' ')[1] for item in values_i if ('filestatus:' in item.lower() or 'inrecyclebin' in item.lower()) and len(item.split(' ')) > 1), '')

                    hydrationType = next((item.split(' ')[1] for item in values_i if 'lasthydrationtype:' in item.lower() and len(item.split(' ')) > 1), '')

                    lastKnownPinState = next((item.split(' ')[1] for item in values_i if 'lastknownpinstate:' in item.lower() and len(item.split(' ')) > 1), '')

                    spoPermissions_i = next(
                        (ast.literal_eval(item.split('spoPermissions: ')[1]) for item in values_i if 'spopermissions: ' in item.lower()), 
                        ''
                    )

                    sharedItem = next(
                        (item.split(' ')[1] for item in values_i if 'shareditem:' in item.lower() and len(item.split(' ')) > 1), 
                        ''
                    )

                    if lastKnownPinState in ['0', '1'] and fileStatus == '2':
                        self.status.append(pin_state.get(lastKnownPinState, online_img))
                    elif hydrationType.lower() == 'passive' and fileStatus == '2':
                        self.status.append(always_available_img)
                    else:
                        self.status.append(image_mapping.get(fileStatus, online_img))

                    if sharedItem == '1' or folderShared == '1':
                        self.status.append(shared_img)

                    if not set(lock_list).intersection(spoPermissions_i) and str(tags_i) != 'red':
                        self.status.append(locked_img)

                    image_creator = CreateImage(self.status)
                    image_sha1 = image_creator.sha1_digest

                    if not tags_i:
                        tags_i = 2
                    self.insert_into_treeview(i, image_sha1, values_i, tags_i)

        except Exception:
            pass

        if self.file:
            cur_item = self.file
            self.file = False
            self.tv2.selection_set(cur_item)

        self.parent.update_idletasks()

    def insert_into_treeview(self, iid, image_sha1, values, tags):
        if not tags:
            print('no tag')
        creationDate = next((item.split(' ', 1)[1] for item in values if 'diskcreationtime:' in item.lower() and len(item.split(' ', 1)) > 1), '')
        accessDate = next((item.split(' ', 1)[1] for item in values if 'disklastaccesstime:' in item.lower() and len(item.split(' ', 1)) > 1), '')

        new_values = [creationDate, accessDate, values[0], values[1]]
        if iid:
            self.tv3.insert("", "end", iid=iid, image=s_image[image_sha1], values=new_values, tags=tags)
        else:
            self.tv3.insert("", "end", image=s_image[image_sha1], values=new_values, tags=tags)

    def update_theme(self):
        # Update background color and other theme-related properties
        new_bgf = style.lookup('Treeview', 'background')
        self.header_frame.config(bg=new_bgf)
        self.header_frame_label.configure(background=new_bgf)

    def update_header_labels_theme(self):
        for header_label in self.header_labels:
            header_label.update_theme()
        for key_label in self.key_labels:
            key_label.clear_highlight()
        for value_label in self.value_labels:
            value_label.clear_highlight()

    def update_font(self):
        try:
            # Update font for all key labels
            for key_label in self.key_labels:
                key_label.label.config(font=default_font)

            # Update font for all value labels
            for value_label in self.value_labels:
                value_label.label.config(font=default_font)

            # Update font for all header labels
            for header_label in self.header_labels:
                header_label.update_font()

            # Update font for all header frame labels
            if hasattr(self, 'header_frame_label'):
                self.header_frame_label.config(font=default_font)
        except Exception:
            pass


class TreeviewHeaderWidget(ttk.Frame):
    def __init__(self, master=None, columns=None, **kwargs):
        super().__init__(master, **kwargs)

        # Create TreeView widget
        self.treeview = ttk.Treeview(self, columns=columns, show="headings")

        # Add headers to the TreeView
        for col in columns:
            self.treeview.heading(col, text=col, anchor="w")

        # Set the height of the treeview to 0 to hide rows
        self.treeview["height"] = 0

        # Pack the TreeView inside the custom widget
        self.treeview.pack(fill=tk.BOTH, expand=True)


class LabelSeparator(tk.Frame):
    def __init__(self, parent, text="", width="", *args):
        tk.Frame.__init__(self, parent, *args)

        self.bgf = style.lookup('Treeview', 'background')

        self.configure(background=self.bgf)
        self.grid_columnconfigure(0, weight=1)

        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.grid(row=0, column=0, sticky="ew")

        self.label = ttk.Label(self, text=text, font=default_font, background=self.bgf)
        self.label.grid(row=0, column=0, padx=width, sticky="w")

    def update_font(self):
        self.label.config(font=default_font)

    def update_theme(self):
        new_bgf = style.lookup('Treeview', 'background')
        self.configure(background=new_bgf)
        self.label.configure(background=new_bgf)


class HighlightableTextBox:
    def __init__(self, master, text, font, wraplength=None):
        self.label = ttk.Label(master, text=text, font=font, background=style.lookup('Treeview', 'background'), wraplength=wraplength)
        self.label.bind("<Enter>", lambda event: self.on_enter())
        self.label.bind("<Leave>", lambda event: self.on_leave())
        self.label.bind("<Button-3>", lambda event: self.copy_text())
        self.highlighted = False

    def on_enter(self):
        if not self.highlighted:
            self.label.configure(background=details['selectbackground'])

    def on_leave(self):
        if not self.highlighted:
            self.label.configure(background=style.lookup('Treeview', 'background'))

    def clear_highlight(self):
        self.highlighted = False
        # below are fixes for when changing from breeze theme
        if str(self.label.cget('background')) == '#eff0f1':
            self.label['background'] = ''
            self.label['foreground'] = ''
        else:
            self.label.configure(background=style.lookup('Treeview', 'background'))

    def copy_text(self):
        selected_text = self.label["text"]
        root.clipboard_clear()
        root.clipboard_append(selected_text)


class Breadcrumb(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.my_list = []
        self.crumb_trail = []
        self.crumb_trail_index = -2
        self.crumb_length = 0
        self.update = True
        self.tv = tv
        self.breadcrumb_viewer()
        self.update_theme()
        self.unbind_left()
        self.unbind_right()
        self.unbind_up()

    def breadcrumb_viewer(self):
        self.leftArrow = ttk.Label(self, text=" \u2B60 ", font=('', 14, 'bold'))
        self.rightArrow = ttk.Label(self, text=" \u2B62 ", font=('', 14, 'bold'))
        self.upArrow = ttk.Label(self, text=" \u2B61 ", font=('', 14, 'bold'))
        self.crumb_frame = ttk.Frame(self)

        self.leftArrow.pack(side='left', anchor='w')
        self.rightArrow.pack(side='left', anchor='w')
        self.upArrow.pack(side='left', anchor='w')
        self.crumb_frame.pack(side='left', anchor='w', expand=True, fill='both')

        self.leftArrow.config(style=f'{self.leftArrow.cget("text")}Hover.TLabel')
        self.rightArrow.config(style=f'{self.rightArrow.cget("text")}Hover.TLabel')
        self.upArrow.config(style=f'{self.upArrow.cget("text")}Hover.TLabel')

        self.crumb_frame.bind("<Configure>", lambda event: self.on_resize(event))

    def unbind_left(self):
        self.leftArrow.config(state='disable')
        self.leftArrow.unbind("<Enter>")
        self.leftArrow.unbind("<Leave>")
        self.leftArrow.unbind("<Button-1>")

    def unbind_right(self):
        self.rightArrow.config(state='disable')
        self.rightArrow.unbind("<Enter>")
        self.rightArrow.unbind("<Leave>")
        self.rightArrow.unbind("<Button-1>")

    def unbind_up(self):
        self.upArrow.config(state='disable')
        self.upArrow.unbind("<Enter>")
        self.upArrow.unbind("<Leave>")
        self.upArrow.unbind("<Button-1>")

    def rebind_left(self):
        self.leftArrow.config(state='normal')
        self.leftArrow.bind("<Enter>", lambda event, l=self.leftArrow.cget("text"): self.on_enter(event, l))
        self.leftArrow.bind("<Leave>", lambda event, l=self.leftArrow.cget("text"): self.on_leave(event, l))
        self.leftArrow.bind("<Button-1>", self.crumb_left)

    def rebind_right(self):
        self.rightArrow.config(state='normal')
        self.rightArrow.bind("<Enter>", lambda event, l=self.rightArrow.cget("text"): self.on_enter(event, l))
        self.rightArrow.bind("<Leave>", lambda event, l=self.rightArrow.cget("text"): self.on_leave(event, l))
        self.rightArrow.bind("<Button-1>", self.crumb_right)

    def rebind_up(self):
        self.upArrow.config(state='normal')
        self.upArrow.bind("<Enter>", lambda event, l=self.upArrow.cget("text"): self.on_enter(event, l))
        self.upArrow.bind("<Leave>", lambda event, l=self.upArrow.cget("text"): self.on_leave(event, l))
        self.upArrow.bind("<Button-1>", self.up_one)

    def create_compact(self, i, my_list):
        my_list = my_list[:i+1]
        option_dict = {}
        optionList = ['']

        for i, value in reversed(list(enumerate(my_list))):
            item_data = self.tv.item(value)
            option_dict[item_data['text'].split('\\')[-1]] = value

        for key in list(option_dict.keys()):
            optionList.append(key)

        v = tk.StringVar()
        om = ttk.OptionMenu(self.crumb_frame, v, *optionList, command=lambda selected_option, dict_key=option_dict: self.on_option_selected(selected_option, dict_key))
        om.configure(style='no_label.TMenubutton')

        return om

    def create_widgets(self):
        total_width = self.total_width
        widgets = []

        for i, value in reversed(list(enumerate(self.my_list))):
            if isinstance(value, tuple):
                continue
            option_dict = {}
            optionList = []
            item_data = self.tv.item(value)
            option_dict[item_data['text'].split('\\')[-1]] = value
            for child in self.tv.get_children(value):
                option_dict[self.tv.item(child)['text']] = child
            optionList = list(option_dict.keys())
            v = tk.StringVar()
            v.set(optionList[0])

            # Use lambda to pass both the selected option and the corresponding dictionary
            om = ttk.OptionMenu(self.crumb_frame, v, *optionList, command=lambda selected_option, dict_key=option_dict: self.on_option_selected(selected_option, dict_key))
            if len(optionList) == 1:
                om.configure(style='no_button.TMenubutton')

            # Bind the left-click event to get the value before opening the dropdown
            om.bind("<Button-1>", lambda event, combo=v, dict_key=option_dict: self.on_left_click(event, combo, dict_key))
            om_width = om.winfo_reqwidth()
            total_width += om_width
            frame_width = self.winfo_width()

            if total_width > frame_width:
                om.destroy()
                om = self.create_compact(i, self.my_list)
                widgets.append(om)
                break

            widgets.append(om)

        self.crumb_length = total_width

        for widget in reversed(widgets):
            widget.pack(side='left', fill='y')

        widgets.clear()

    def clear(self):
        self.my_list = []
        self.crumb_trail = []
        self.crumb_trail_index = -1
        self.bindings()
        self.update_widgets()
        self.create_widgets()

    def bindings(self):
        if self.crumb_trail:
            self.rebind_left()
            if (len(self.crumb_trail) - 1 == self.crumb_trail_index) or (self.crumb_trail_index == -2):
                self.on_leave('', self.rightArrow.cget("text"))
                self.unbind_right()
            else:
                self.rebind_right()
        else:
            self.on_leave('', self.leftArrow.cget("text"))
            self.unbind_left()
            self.on_leave('', self.rightArrow.cget("text"))
            self.unbind_right()

        if self.crumb_trail_index == -1:
            self.on_leave('', self.leftArrow.cget("text"))
            self.unbind_left()

        if self.my_list and (self.my_list != [()]):
            self.rebind_up()
        else:
            self.on_leave('', self.upArrow.cget("text"))
            self.unbind_up()

    def disable_crumbs(self):
        for widget in self.winfo_children():
            if '!frame' in str(widget):
                for crumb in widget.winfo_children():
                    crumb.config(state='disable')

    def enable_crumbs(self):
        for widget in self.winfo_children():
            if '!frame' in str(widget):
                for crumb in widget.winfo_children():
                    crumb.config(state='normal')

    def append(self, value):
        if self.update:
            if self.crumb_trail_index != -2:
                del self.crumb_trail[self.crumb_trail_index:-1]
                if self.crumb_trail == [()]:
                    self.crumb_trail = []
                self.crumb_trail_index = -2
            try:
                if value != self.crumb_trail[-1]:
                    self.crumb_trail.append(value)
            except Exception:
                if value != ():
                    self.crumb_trail.append(value)

        self.find_parent_hierarchy(value)
        self.bindings()
        self.update_widgets()
        self.create_widgets()
        self.update = True

    def update_widgets(self):
        # Destroy existing optionmenus and recreate them with updated list
        for widget in self.winfo_children():
            if '!frame' in str(widget):
                for crumb in widget.winfo_children():
                    crumb.destroy()

    def find_parent_hierarchy(self, item):
        self.my_list.clear()
        parent_item = self.tv.parent(item)
        self.my_list = [item]

        while parent_item:
            self.my_list.insert(0, parent_item)
            parent_item = self.tv.parent(parent_item)

    def on_option_selected(self, selected_option, option_dict):
        clear_search()
        self.find_parent_hierarchy(option_dict[selected_option])
        self.update_treeview(option_dict[selected_option])

    def update_treeview(self, cur_item):
        parent = self.tv.parent(cur_item)
        self.tv.selection_set(cur_item)
        self.tv.item(parent, open=True)

    def on_left_click(self, event, combo, option_dict):
        # Get the value when left-clicking on the OptionMenu box
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify(x, y)
        if str(widget.cget('state')) == 'disable':
            return
        if 'label' in elem:
            clear_search()
            selected_option = combo.get()
            self.update_widgets()
            self.find_parent_hierarchy(option_dict[selected_option])
            self.update_treeview(option_dict[selected_option])

    def on_enter(self, event, label):
        # Lighten the default background color
        hover_color = self.change_color(self.default_background_color, 0.3)
        self.style.configure(f'{label}Hover.TLabel', background=hover_color, foreground='black')

    def on_leave(self, event, label):
        if self.default_foreground_color == '':
            self.default_foreground_color = 'black'
        self.style.configure(f'{label}Hover.TLabel', background=self.default_background_color, foreground=self.default_foreground_color)

    def on_resize(self, event):
        self.update_widgets()
        self.create_widgets()

    def up_one(self, event):
        try:
            move_up = self.my_list[-2]
        except IndexError:
            move_up = ''
        self.find_parent_hierarchy(move_up)
        self.update_treeview(move_up)

    def crumb_left(self, event):
        self.update = False
        if self.crumb_trail_index == 0:
            self.update_treeview('')
            self.crumb_trail_index += -1
            return
        elif self.crumb_trail_index == -1:
            self.update_treeview('')
            return
        elif self.crumb_trail_index == -2:
            self.crumb_trail_index = len(self.crumb_trail) - 2
            if self.crumb_trail_index == -1:
                self.update_treeview('')
                return
        else:
            self.crumb_trail_index += -1

        self.update_treeview(self.crumb_trail[self.crumb_trail_index])

    def crumb_right(self, event):
        self.update = False
        if self.crumb_trail_index < len(self.crumb_trail) - 1:
            self.crumb_trail_index += 1

        self.update_treeview(self.crumb_trail[self.crumb_trail_index])

    def change_color(self, hex_color, saturation_factor=0.2, brightness_factor=-0.2, lighten=True):
        hex_color = str(hex_color).lstrip('#')
        try:
            sbf_rgb = root.winfo_rgb(hex_color)
            hex_color = "{:02X}{:02X}{:02X}".format(sbf_rgb[0] // 256, sbf_rgb[1] // 256, sbf_rgb[2] // 256)
        except Exception:
            pass
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        hls = colorsys.rgb_to_hls(*[c / 255.0 for c in rgb])
        if lighten:
            change_hls = (hls[0], min(1, hls[1] + saturation_factor), hls[2])
        else:
            change_hls = (hls[0], max(0, hls[1] - saturation_factor), max(0, hls[2] + brightness_factor))
        change_rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(*change_hls))
        change_hex = "#{:02X}{:02X}{:02X}".format(*change_rgb)
        return change_hex

    def iter_layout(self, layout, ind=True):
        """Recursively prints the layout children."""
        elements = ''

        for element, child in layout:
            if 'indicator' in element and ind is True:
                continue
            if 'label' in element and ind is False:
                continue

            elements += f"('{element}', {{"

            for key, value in child.items():
                if isinstance(value, str):
                    elements += f"'{key}': '{value}', "
                else:
                    elements += f"'{key}': ["
                    elements += self.iter_layout(value, ind=ind)
                    elements += (']')

            elements += '})'

        return elements

    def update_theme(self):
        self.total_width = self.leftArrow.winfo_reqwidth() + self.rightArrow.winfo_reqwidth() + self.upArrow.winfo_reqwidth()
        self.style = ttk.Style(root)

        layout = self.style.layout('TMenubutton')

        no_button = self.iter_layout(layout)
        no_button = no_button.replace(")(", "), (").replace(", }", "}").replace(", 'children': []", "")  # Remove trailing commas
        no_button = ast.literal_eval(no_button)

        no_label = self.iter_layout(layout, ind=False)
        no_label = no_label.replace(")(", "), (").replace(", }", "}").replace(", 'children': []", "")  # Remove trailing commas
        no_label = ast.literal_eval(no_label)

        self.default_background_color = self.style.lookup('TLabel', 'background')
        self.default_foreground_color = self.style.lookup('TLabel', 'foreground')

        try:
            style.layout('no_button.TMenubutton', [no_button])
        except Exception:
            style.layout('no_button.TMenubutton', list(no_button))
        try:
            style.layout('no_label.TMenubutton', [no_label])
        except Exception:
            style.layout('no_label.TMenubutton', list(no_label))

        self.leftArrow['background'] = ''
        self.leftArrow['foreground'] = ''
        self.rightArrow['background'] = ''
        self.rightArrow['foreground'] = ''
        self.upArrow['background'] = ''
        self.upArrow['foreground'] = ''


class DetailsFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.text_boxes = []  # Keep track of text boxes for updating
        self.frames = []
        self.treeviews = []  # Track treeviews for potential updates
        self.current_bg = style.lookup('Treeview', 'background')  # Default background color

    def tab_count(self):
        """Returns the number of tabs in the notebook."""
        return len(self.notebook.tabs())

    def add_tab(self, tab_name):
        """Adds a new tab and returns its frame."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=tab_name)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return frame

    def delete_tab(self, index):
        """Deletes a tab by index if valid."""
        if 0 <= index < self.notebook.index("end"):
            self.notebook.forget(index)

    def add_textbox(self, tab):
        """Adds a text box with a scrollbar to a tab."""
        text_box = tk.Text(tab)
        text_box_scroll = ttk.Scrollbar(tab, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=text_box_scroll.set)
        text_box.tag_configure('red', foreground="red")
        text_box.grid(row=0, column=0, sticky="nsew")
        text_box_scroll.grid(row=0, column=1, sticky='ns')
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.text_boxes.append(text_box)
        return text_box

    def add_treeview(self, tab, columns=("Column1", "Column2")):
        """Adds a ttk.Treeview with a scrollbar to a tab."""
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky="nsew")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.treeviews.append(tree)
        return tree

    def add_frame(self, tab):
        """Adds a frame inside a text box on a tab."""
        text_box = tk.Text(tab)
        text_box_scroll = ttk.Scrollbar(tab, orient="vertical", command=text_box.yview)
        text_box.configure(yscrollcommand=text_box_scroll.set)
        frame = tk.Frame(text_box)
        frame.configure(bg=self.current_bg, padx=10, pady=10)
        text_box.window_create("1.0", window=frame)
        text_box.grid(row=0, column=0, sticky="nsew")
        text_box_scroll.grid(row=0, column=1, sticky='ns')
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        text_box.configure(background=self.current_bg, relief='flat',
                           undo=False, spacing3=3, width=50, state='disable')
        self.frames.append(frame)
        self.text_boxes.append(text_box)
        return frame

    def update_textbox_theme(self, bg, fg):
        """Updates the background color of all stored text boxes and frames."""
        self.current_bg = bg
        for frame in self.frames:
            frame.configure(background=bg)
        for text_box in self.text_boxes:
            text_box.configure(background=bg, foreground=fg)


class CreateImage():
    def __init__(self, status, type=False, small=False):
        self.status = status
        self.type = type
        self.small = small
        self.output_image = None
        self.sha1 = hashlib.sha1()

        self.create_output_image()
        self.sha1_digest = self.update_image_dictionary()

    def create_output_image(self):
        # Calculate total width for the output image
        if self.type:
            total_width = 84
        elif self.small:
            total_width = 16
        else:
            total_width = sum(img.width for img in self.status) + (33 if self.type else 0)

        # Determine the height for the output image (32 or 16)
        output_height = 32 if self.type else 16

        # Create a new RGBA image with the appropriate size
        self.output_image = Image.new("RGBA", (total_width, output_height), (0, 0, 0, 0))
        # If 'type' exists, paste it at the beginning
        width = 0
        if self.type:
            for s in self.type:
                self.output_image.paste(s, (0, 0), s)
            width = 33

        # Paste the status images next to 'type'
        for s in self.status:
            if self.small:
                self.output_image.paste(s, (0, 0), s)
            else:
                self.output_image.paste(s, (width, 0))
                width += s.width

    def update_image_dictionary(self):
        fp = BytesIO()
        self.output_image.save(fp, 'png')
        fp.seek(0)
        self.sha1.update(fp.read())
        digest = self.sha1.hexdigest()
        if digest not in s_image:
            image = ImageTk.PhotoImage(Image.open(fp))
            s_image[digest] = image

        return digest


def ButtonNotebook():
    def iter_layout(layout):
        """Recursively prints the layout children."""
        elements = ''
        for element, child in layout:
            if 'focus' in element:
                for key, value in child.items():
                    if not isinstance(value, str):
                        elements += iter_layout(value)
                continue
            elements += f"('{element}', {{"
            for key, value in child.items():
                if isinstance(value, str):
                    elements += f"'{key}': '{value}', "
                else:
                    elements += f"'{key}': ["
                    elements += iter_layout(value)
                    elements += (']')
            elements += '})'
        return elements

    TNotebook_map = style.map('TNotebook.Tab')
    style.map('CustomNotebook.Tab', **TNotebook_map)

    try:
        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "!invalid", "img_closepressed"),
                             ("active", "!disabled", "!invalid", "img_closeactive"),
                             ("invalid", "img_blank"),
                             border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client",
                                        {"sticky": "nswe"})])

        layout = style.layout('TNotebook.Tab')
        elements = iter_layout(layout)
        elements = elements.replace("label', {'sticky': 'nswe', }", "label', {'side': 'left', 'sticky': '', }").replace("label', {'side': 'top'", "label', {'side': 'left'").replace(", })", "}), ('Notebook.close', {'side': 'left', 'sticky': ''})")
        elements = ast.literal_eval(elements)

        try:
            style.layout("CustomNotebook.Tab", [elements])
        except Exception:
            style.layout("CustomNotebook.Tab", list(elements))

        style.configure('CustomNotebook.Tab', **style.configure('TNotebook.Tab'))
        style.configure('CustomNotebook', **style.configure('TNotebook'))
    except Exception:
        pass

    layout = style.layout('TNotebook.Tab')

    no_focus = iter_layout(layout)
    no_focus = no_focus.replace(")(", "), (").replace(", }", "}").replace(", 'children': []", "")  # Remove trailing commas
    no_focus = ast.literal_eval(no_focus)

    try:
        style.layout('TNotebook.Tab', [no_focus])
    except Exception:
        style.layout('TNotebook.Tab', list(no_focus))

    def on_close_press(event):
        """Called when the button is pressed over the close button"""

        if event.widget.winfo_class() != 'TNotebook':
            return
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify(x, y)

        try:
            index = widget.index("@%d,%d" % (x, y))
            if index == 0:
                # widget.state(['invalid'])
                return
        except Exception:
            return

        if "close" in elem:
            widget.state(['pressed'])
            widget.pressed_index = index

    def on_close_release(event):
        """Called when the button is released"""
        global proj_name

        if event.widget.winfo_class() != 'TNotebook':
            return

        x, y, widget = event.x, event.y, event.widget

        if not widget.instate(['pressed']):
            return

        elem = widget.identify(x, y)
        if "close" not in elem:
            # user moved the mouse off of the close button
            return

        index = widget.index("@%d,%d" % (x, y))

        if index == 0:
            return

        for item in root.winfo_children():
            try:
                if item.winfo_ismapped():
                    if str(item) == '.!frame' or str(item) == '.!notebook2':
                        pass
                    else:
                        item.destroy()
            except Exception:
                pass

        if "close" in elem and widget.pressed_index == index:
            try:
                del user_logs[f'{widget.tab(index, "text").replace(" L", "_l")}.csv']
            except Exception:
                pass

            widget.winfo_children()[index].destroy()
            widget.event_generate("<<NotebookClosedTab>>")
            if len(tv_frame.tabs()) == 1:
                for item in infoFrame.winfo_children():
                    if '.!notebook.!frame.' in str(item):
                        item.destroy()
                odlmenu.entryconfig("Unload all ODL logs", state='disable')
                if len(tv.get_children()) == 0:
                    projmenu.entryconfig("Save", state='disable')
                    root.unbind('<Alt-s>')
                    projmenu.entryconfig("SaveAs", state='disable')
                    projmenu.entryconfig("Unload", state='disable')
                    proj_name = None

        widget.state(["!pressed"])
        widget.pressed_index = None

    root.bind("<ButtonPress-1>", on_close_press, True)
    root.bind("<ButtonRelease-1>", on_close_release)


def ButtonEntry(do_bind=False):
    TEntry_map = style.map('TEntry')
    style.map('CustomEntry', **TEntry_map)

    try:
        style.element_create("clear", "image", "img_blank",
                             ("pressed", "!disabled", "img_closepressed"),
                             ("!invalid", "!disabled", "img_close"),
                             border=8, sticky='')
        style.layout("CustomEntry", [("CustomEntry.client",
                                      {"sticky": "nswe"})])
        style.layout("CustomEntry", [
            ('CustomEntry.field', {
                'sticky': 'nswe',
                'children': [
                    ('CustomEntry.fieldbackground', {
                        'sticky': 'nswe',
                        'children': [
                            ('CustomEntry.padding',
                                {'sticky': 'nswe',
                                    'children': [
                                        ('CustomEntry.textarea',
                                         {'side': 'left', 'sticky': ''}),
                                        ('CustomEntry.clear',
                                         {'side': 'left', 'sticky': ''}),
                                        ]
                                 })
                        ]
                    })
                ]
            })
        ])

        style.configure('CustomEntry', **style.configure('TEntry'))

    except Exception:
        pass

    def on_press(event):
        """Called when the button is pressed over the close button"""

        if event.widget.winfo_class() != 'TEntry':
            return
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify(x, y)

        if 'invalid' in widget.state():
            return

        if "clear" in elem:
            widget.state(['pressed'])

    def on_release(event):
        """Called when the button is released"""

        if event.widget.winfo_class() != 'TEntry':
            return

        x, y, widget = event.x, event.y, event.widget

        if not widget.instate(['pressed']):
            return

        elem = widget.identify(x, y)
        if "clear" not in elem:
            # user moved the mouse off of the close button
            widget.state(["!pressed"])
            return

        widget.state(["!pressed"])
        search_entry.state(['invalid'])
        search_entry.delete(0, 'end')
        clear_search()

    if do_bind:
        search_entry.state(['invalid'])
        search_entry.bind("<ButtonPress-1>", on_press, True)
        search_entry.bind("<ButtonRelease-1>", on_release)


def pane_config():
    sel_bg = style.lookup("Treeview", "background", state=["selected"])

    bg = style.lookup('TFrame', 'background')
    bgf = style.lookup('Treeview', 'background')
    fgf = style.lookup('Treeview', 'foreground')

    if not fgf:
        fgf = 'black'

    pwv.config(background=bg, sashwidth=6)
    pwh.config(background=bgf, sashwidth=6)
    details.config(background=bgf, foreground=fgf)
    details_frame.update_textbox_theme(bgf, fgf)
    file_usage_frame.email_header.update_textbox_theme(bgf, fgf)
    separator.config(bg=sel_bg)

    style.configure('Result.Treeview', rowheight=40)

    tv_pane_frame.configure(background=bgf)
    breadcrumb.update_theme()
    try:
        file_manager.update_header_labels_theme()
    except Exception:
        pass
    try:
        file_manager.update_theme()
    except Exception:
        pass
    ttk.Style().theme_use()

    # below are fixes for when changing from breeze theme
    if str(message.cget('background')) == '#eff0f1':
        message['background'] = ''
        message['foreground'] = ''

    # below are fixes for when changing from breeze theme
    for child in selector_frame.winfo_children():
        if isinstance(child, ttk.Label):
            bg = child.cget('background')
            if str(bg) == '#eff0f1':
                child.configure(background='', foreground='')

    value_label['background'] = ''
    value_label['foreground'] = ''

    la['background'] = ''
    la['foreground'] = ''

    ra['background'] = ''
    ra['foreground'] = ''


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

    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe'})
    ])

    return [elm for elm in style.map("Treeview", query_opt=option)
            if elm[:2] != ("!disabled", "!selected")]


def search(item=''):
    root.update()
    query = search_entry.get()
    if len(query) == 0:
        return
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    btn.configure(state="disabled")
    breadcrumb.unbind_left()
    breadcrumb.unbind_right()
    breadcrumb.unbind_up()
    breadcrumb.disable_crumbs()
    tv.grid_forget()
    file_manager.tv2.delete(*file_manager.tv2.get_children())
    file_manager.tv3.delete(*file_manager.tv3.get_children())
    children = tv.get_children(item)
    for child in children:
        if query.lower() in str(tv.item(child, 'values')).lower():
            values = tv.item(child, 'values')
            image_key = tv.item(child, 'image')[0]
            Result(root, values, child, image_key)
        if child in file_items:
            folderShared = next(
                (item.split(' ')[1] for item in tv.item(child, 'values') if 'shareditem:' in item.lower() and len(item.split(' ')) > 1),
                ''
            )
            for i in file_items[child]:
                if query.lower() in str(tv.item(i, 'values')).lower():
                    tags = ''
                    if tv.item(i, 'tags'):
                        tags = 'red'
                    values = tv.item(i, 'values')
                    image_key = tv.item(i, 'image')[0]
                    Result(root, values, i, image_key, folder=False, folderShared=folderShared, tags=tags)
        search(item=child)


def search_result():
    breadcrumb.bindings()
    breadcrumb.enable_crumbs()
    search_entry.configure(state="normal")
    search_entry.configure(cursor='xterm')
    btn.configure(state="normal")
    rebind()
    tv.grid(row=1, column=0, sticky="nsew")
    if len(search_entry.get()) == 0:
        return
    position = pwh.sash_coord(2)
    pwh.remove(file_manager.tv2)
    pwh.remove(file_manager.tab2)
    pwh.add(result_frame, minsize=327, after=tv_pane_frame)
    root.update_idletasks()
    pwh.sash_place(1, x=position[0], y=position[1])


def clear_search():
    global s_image

    position = None
    threading.Thread(target=clear_tvr,
                     daemon=True).start()
    if len(pwh.panes()) == 3:
        position = pwh.sash_coord(1)
    pwh.remove(result_frame)
    pwh.add(file_manager.tv2, minsize=80, width=170, after=tv_pane_frame)
    pwh.add(file_manager.tab2, minsize=247, after=file_manager.tv2)
    if position:
        pwh.sash_place(2, x=position[0], y=position[1])
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    for tab_index in reversed(range(1, details_frame.tab_count())):
        details_frame.delete_tab(tab_index)


def delete_item_and_descendants(tree, item=''):
    root.update()
    children = tree.get_children(item)
    for child in children:
        if child in file_items:
            for i in file_items[child]:
                root.after(0, tv.delete, i)
            del file_items[child]
        delete_item_and_descendants(tree, child)


def clear_all():
    global proj_name
    value_label['text'] = ''
    widgets_disable()
    clear_search()
    breadcrumb.clear()
    tv.grid_forget()
    root.update_idletasks()
    file_manager.tv2.delete(*file_manager.tv2.get_children())
    file_manager.tv3.delete(*file_manager.tv3.get_children())
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    odsmenu.entryconfig("Unload all files", state='disable')
    file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')
    search_entry.delete(0, 'end')
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    btn.configure(state="disabled")
    for tab_index in reversed(range(1, details_frame.tab_count())):
        details_frame.delete_tab(tab_index)
    delete_item_and_descendants(tv)
    tv.delete(*tv.get_children())
    tv.grid(row=1, column=0, sticky="nsew")
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
        root.unbind('<Alt-s>')
        projmenu.entryconfig("SaveAs", state='disable')
        projmenu.entryconfig("Unload", state='disable')
        proj_name = None


def clear_tvr():
    children = tvr.get_children()
    for child in children:
        tvr.delete(child)


def json_count(item='', file_count=0, del_count=0, folder_count=0):
    children = tv.get_children(item)

    for child in children:
        values = tv.item(child, 'values')

        folder_count += any('folderstatus:' in item.lower() for item in values)

        if child in file_items:
            for i in file_items[child]:
                values = tv.item(i, 'values')

                file_count += any('filestatus:' in item.lower() for item in values)
                del_count += any('inrecyclebin:' in item.lower() for item in values)

        file_count, del_count, folder_count = json_count(
            item=child,
            file_count=file_count,
            del_count=del_count,
            folder_count=folder_count
        )

    return file_count, del_count, folder_count


def parent_child(d, parent_id=None, account=False):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("",
                              "end",
                              image=root_drive_img,
                              text=f" {d['Name']}",
                              values=([f'{k}: {v}' for k, v in d.items() if 'Data' not in k and 'FileUsageSync' not in k]))

    if 'Data' in d:
        for c in d['Data']:
            if 'Children' in c:
                z = ('', '', '', '', '', '', '', '', '')
                parent_id = tv.insert(parent_id,
                                      "end",
                                      image=del_img,
                                      text=' Deleted',
                                      values=(z),
                                      tags='red')
                for b in c['Children']:
                    w = (b['DeleteTimeStamp'], b['size'])
                    x = ('', '', '', '', '', '')
                    y = [f'{k}: {v}' for k, v in b.items() if 'DeleteTimeStamp' not in k and 'size' not in k]
                    z = w + tuple(y) + x
                    iid = tv.insert(parent_id,
                                    "end",
                                    image=file_del_img,
                                    text=f" {b['Name']}",
                                    values=(z),
                                    tags='red')
                    parent = tv.parent(iid)
                    file_items[parent].append(iid)
                    tv.detach(iid)
            else:
                w = ('', '')
                x = ('', '', '')
                y = [f'{k}: {v}' if v is not None else f'{k}: ' for k, v in c.items() if 'Files' not in k and 'Folders' not in k and 'Scope' not in k]
                z = w + tuple(y) + x
                if '+' in c['scopeID']:
                    image = tenant_sync_img
                else:
                    if account == 'Personal':
                        image = od_p_folder_img
                    else:
                        image = od_folder_img
                text = f" {c['MountPoint']}" if c['MountPoint'] != '' else f" {c['scopeID']}"
                parent_child(c, tv.insert(parent_id,
                                          "end",
                                          image=image,
                                          text=text,
                                          values=(z)), account)

    if 'Files' in d:
        for c in d['Files']:
            x = (c['lastChange'], c['size'])
            y = [f'{k}: {v}' for k, v in c.items() if 'lastChange' not in k and 'size' not in k]
            z = x + tuple(y)
            if c['fileStatus'] == 6:
                image = not_sync_file_img
            elif c['fileStatus'] == 7:
                image = not_link_file_img
            else:
                image = file_img
            iid = tv.insert(parent_id,
                            "end",
                            image=image,
                            text=f" {c['Name']}",
                            values=(z))
            parent = tv.parent(iid)
            file_items[parent].append(iid)
            tv.detach(iid)

    if 'Folders' in d:
        for c in d['Folders']:
            folder_type.clear()
            x = ('', '')
            y = [f'{k}: {v}' for k, v in c.items() if 'Files' not in k and 'Folders' not in k and 'Scope' not in k]
            z = x + tuple(y)

            if 'folderColor' in c and c['folderColor'] in range(1, 16):
                folder_type.append(folder_color.get(c['folderColor']))
            else:
                folder_type.append(dir_img)
            if c['folderStatus'] == 9:
                folder_type.append(sync_img)
            elif c['folderStatus'] == 10:
                folder_type.append(not_sync_img)
            elif c['folderStatus'] == 11:
                folder_type.append(not_link_img)
            elif c['folderStatus'] == 12:
                folder_type.append(unknown_img)
            image_creator = CreateImage(folder_type, False, True)
            image_sha1 = image_creator.sha1_digest
            parent_child(c, tv.insert(parent_id,
                                      0,
                                      image=s_image[image_sha1],
                                      text=f" {c['Name']}",
                                      values=(z)), account)

    if 'Scope' in d:
        for c in d['Scope']:
            x = ('', '')
            y = [f'{k}: {v}' if v is not None else f'{k}: ' for k, v in c.items() if 'Links' not in k]

            for b in c['Links']:
                w = [f'{k}: {v}' for k, v in b.items() if 'Files' not in k and 'Folders' not in k]
                z = x + tuple(w) + tuple(y)

                if c['shortcutItemIndex'] > 0:
                    image = vault_closed_img
                else:
                    if 'folderColor' in b and b['folderColor'] in range(1, 16):
                        folder_type.append(folder_color.get(b['folderColor']))
                    else:
                        folder_type.append(dir_img)

                    if c['siteID'] == '' and '+' in c['scopeID']:
                        if b['folderStatus'] == 9:
                            folder_type.append(sync_img)
                        elif b['folderStatus'] == 10:
                            folder_type.append(not_sync_img)
                        elif b['folderStatus'] == 11:
                            folder_type.append(not_link_img)
                        elif b['folderStatus'] == 12:
                            folder_type.append(unknown_img)
                    else:
                        folder_type.append(link_img)

                    image_creator = CreateImage(folder_type, False, True)
                    image_sha1 = image_creator.sha1_digest
                    image = s_image[image_sha1]

                if ('Folders' in b or 'Files' in b) and str(image) == str(vault_closed_img):
                    image = vault_open_img

                parent_child(b, tv.insert(parent_id,
                                          0,
                                          image=image,
                                          text=f" {b['Name']}",
                                          values=(z)), account)

    if 'FileUsageSync' in d:
        if isinstance(d['FileUsageSync'], list):
            fus.load_data(d['FileUsageSync'])
            file_usage_frame.set_data(fus.df_data)


def live_system(menu):
    global reghive
    global recbin
    widgets_disable()
    clear_search()
    search_entry.delete(0, 'end')
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    breadcrumb.clear()
    file_manager.tv2.delete(*file_manager.tv2.get_children())
    file_manager.tv3.delete(*file_manager.tv3.get_children())
    pb.configure(mode='indeterminate')
    value_label['text'] = "Searching for OneDrive. Please wait..."
    pb.start()

    profile = {}
    users_folder = os.path.expandvars("%SystemDrive%\\Users\\")
    rec_folder = os.path.expandvars("%SystemDrive%\\$Recycle.Bin\\")
    user_names = [folder for folder in os.listdir(users_folder) if os.path.isdir(os.path.join(users_folder, folder))]
    settings_dir = re.compile(r'\\settings\\(?P<account>Personal|Business[0-9])$')
    listsync_settings_dir = re.compile(r'\\ListSync\\(?P<account>Business[0-9])\\settings$')
    logs_dir = re.compile(r'\\(?P<logs>logs)$')

    if os.path.exists(rec_folder):
        recbin = rec_folder

    for user in user_names:
        profile.setdefault(user, {})
        od_profile = os.path.join(users_folder, user, "AppData\\Local\\Microsoft\\OneDrive")

        for path, subdirs, files in os.walk(od_profile):
            settings_find = re.findall(settings_dir, path)
            listsync_find = re.findall(listsync_settings_dir, path)
            logs_find = re.findall(logs_dir, path)

            if settings_find:
                profile[user].setdefault(settings_find[0], {})
                profile[user][settings_find[0]].setdefault('settings', '')
                profile[user][settings_find[0]]['settings'] = path

            if listsync_find:
                profile[user].setdefault(listsync_find[0], {})
                profile[user][listsync_find[0]].setdefault('listsync', '')
                profile[user][listsync_find[0]]['listsync'] = path

            if logs_find:
                profile[user].setdefault(logs_find[0], [])
                profile[user][logs_find[0]].append(path)

    for key, value in profile.items():
        print(f'key: {key}')
        print(f'value: {value}')
        if has_settings(value):
            value_label['text'] = f"Searching for {key}'s NTUSER.DAT. Please wait...."
            pb.configure(mode='indeterminate')
            pb.start()
            reghive = live_hive(key, os.path.splitdrive(os.path.join(users_folder, key))[1].replace('\\', '/'))

        else:
            reghive = ''

        x = 'Profile'
        start_parsing(x, f'{users_folder}{key}\\AppData\\Local\\Microsoft\\OneDrive', reghive, recbin, True, value, key)

    reghive = ''
    recbin = ''
    pb.stop()
    pb.configure(mode='determinate')
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

    value_label['text'] = "All jobs complete"

    widgets_normal()
    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
        root.bind('<Alt-s>', lambda event=None: save_proj())
        projmenu.entryconfig("SaveAs", state='normal')


def has_settings(data):
    if isinstance(data, dict):
        if 'settings' in data:
            return True
        return any(has_settings(v) for v in data.values())
    return False


def open_profile(menu):
    global reghive
    global recbin

    folder_name = filedialog.askdirectory(initialdir="/", title="Open Profile folder")

    if folder_name:
        if keyboard.is_pressed('shift') or menu_data['hive']:
            pass
        else:
            root.wait_window(hive(root).win)

        x = menu.entrycget(0, "label")
        message.unbind('<Double-Button-1>', bind_id)
        threading.Thread(target=start_parsing,
                         args=(x, folder_name, reghive, recbin,),
                         daemon=True).start()

    reghive = ''
    recbin = ''


def import_json(menu):
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import OD JSON",
                                      filetypes=(("OneDrive json file",
                                                  "*.json"),))

    if filename:
        x = 'Import JSON'
        message.unbind('<Double-Button-1>', bind_id)
        threading.Thread(target=start_parsing,
                         args=(x, filename,),
                         daemon=True).start()


def import_csv(menu):
    fields = [
        ("OneDrive csv file", "_OneDrive.csv"),
        ("FileUsageSync csv file", "_FileUsageSync.csv")
    ]

    icon_path = application_path + '/Images/titles/table.ico'

    FileSelectDialog(root, fields=fields, callback=on_files_selected,
                     title="Import CSV Files", icon_path=icon_path)


def load_ind():
    fields = [
        ("Load <UserCid>.dat", "*.dat *.dat.previous"),
        ("Load SyncEngineDatabase.db", "SyncEngineDatabase.db"),
        ("Load SafeDelete.db", "SafeDelete.db"),
        ("Load Microsoft.ListSync.db", "Microsoft.ListSync.db"),
        ("Load Microsoft.FileUsageSync.db", "Microsoft.FileUsageSync.db"),
        ("Load NTUSER.DAT", "NTUSER.DAT"),
        ("Load $Recycle.Bin", "$Recycle.Bin")
    ]

    icon_path = application_path + '/Images/titles/files_yellow_combine.ico'

    FileSelectDialog(root, fields=fields, callback=threaded_on_files_selected,
                     title="Load Individual Files", icon_path=icon_path)


def threaded_on_files_selected(file_paths):
    # Run your function in a thread
    threading.Thread(target=on_files_selected, args=(file_paths,), daemon=True).start()


def on_files_selected(file_paths):
    if '_OneDrive.csv' in file_paths:
        if file_paths['_OneDrive.csv'] != '':
            x = 'Import CSV'
            message.unbind('<Double-Button-1>', bind_id)
            threading.Thread(target=start_parsing,
                             args=(x, file_paths,),
                             daemon=True).start()

        if file_paths['_FileUsageSync.csv'] != '':
            widgets_disable()
            fus.load_csv(file_paths['_FileUsageSync.csv'])
            file_usage_frame.set_data(fus.df_data)
            widgets_normal()

    if '*.dat *.dat.previous' in file_paths:
        reghive = ''
        recbin = ''
        if file_paths['NTUSER.DAT'] != '':
            try:
                Registry.Registry(file_paths['NTUSER.DAT'])
                reghive = file_paths['NTUSER.DAT']
            except Exception:
                try:
                    alt_path = os.path.split(os.path.splitdrive(file_paths['NTUSER.DAT'])[1])[0]
                    key = alt_path.split('/')[-1]
                    value_label['text'] = f"Searching for {key}'s NTUSER.DAT. Please wait...."
                    pb.configure(mode='indeterminate')
                    pb.start()
                    reghive = live_hive(key, alt_path)
                except Exception:
                    pass

        if file_paths['$Recycle.Bin'] != '':
            recbin = file_paths['$Recycle.Bin']

        x = 'loose'
        message.unbind('<Double-Button-1>', bind_id)
        threading.Thread(target=start_parsing,
                         args=(x, file_paths, reghive, recbin,),
                         daemon=True).start()


def open_odl():
    folder_name = filedialog.askdirectory(initialdir="/", title="Open log folder")

    if folder_name:
        threading.Thread(target=odl,
                         args=(folder_name,),
                         daemon=True).start()


def import_odl():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import log CSV",
                                      filetypes=(("ODL csv file",
                                                  "*.csv"),))
    if filename:
        threading.Thread(target=odl,
                         args=(filename, True,),
                         daemon=True).start()


def odl(folder_name, csv=False):
    widgets_disable()
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    breadcrumb.unbind_left()
    breadcrumb.unbind_right()
    breadcrumb.unbind_up()
    breadcrumb.disable_crumbs()
    file_manager.tv2.delete(*file_manager.tv2.get_children())
    file_manager.tv3.delete(*file_manager.tv3.get_children())
    key_find = re.compile(r'Users/(?P<user>[^/]+)/AppData')
    pb.stop()
    start = time.time()

    if csv:
        pname = folder_name.name.replace('/', '\\').split(os.sep)[-1].split('_')[0]
        key = folder_name.name.split('/')[-1].split('_')[0]
        header_list = ['Profile',
                       'Key_Type',
                       'Log_Type',
                       'Filename',
                       'File_Index',
                       'Timestamp',
                       'One_Drive_Version',
                       'OS_Version',
                       'Code_File',
                       'Flags',
                       'Function',
                       'Context_Data',
                       'Description',
                       'Params',
                       'Param1',
                       'Param2',
                       'Param3',
                       'Param4',
                       'Param5',
                       'Param6',
                       'Param7',
                       'Param8',
                       'Param9',
                       'Param10',
                       'Param11',
                       'Param12',
                       'Param13']

        pb.configure(mode='indeterminate')
        value_label['text'] = f'Parsing log files for {key}. Please wait....'
        pb.start()
        file = open(folder_name.name, 'r', encoding='utf-8')
        odl = pd.read_csv(file, dtype=str)
        import_headers = odl.axes[1]
        if list(set(import_headers) - set(header_list)):
            odl = pd.DataFrame()
            logging.error(f'{folder_name.name} not a valid ODL csv.')
    else:
        pname = folder_name.replace('/', '\\').split(os.sep)[-2]
        key = re.findall(key_find, folder_name)
        if len(key) == 0:
            key = 'ODL'
        else:
            key = key[-1]
        odl = parse_odl(folder_name, pname, pb, value_label, gui=True)

    tb = ttk.Frame()

    if not odl.empty:
        pt = pandastablepatch.MyTable(tb,
                                      dataframe=odl,
                                      maxcellwidth=900,
                                      showtoolbar=False,
                                      showstatusbar=False,
                                      enable_menus=True,
                                      editable=False)
        pt.adjustColumnWidths()
        tv_frame.add(tb, text=f'{pname} Logs  ')
        pt.show()
        user_logs.setdefault(f'{pname}_logs.csv', pt)
    pb.stop()

    if menu_data['odl_save'] is True and not csv:
        log_output = f'{menu_data["path"]}/{pname}_logs.csv'
        try:
            value_label['text'] = f"Saving {pname}_logs.csv. Please wait...."
            pb.configure(mode='indeterminate')
            pb.start()
            odl.to_csv(log_output, index=False)
        except Exception as e:
            logging.error(e)

    pb.stop()
    pb.configure(mode='determinate')
    value_label['text'] = f'Parsing complete. {format((time.time() - start), ".4f")} seconds'

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
    widgets_normal()

    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
        root.bind('<Alt-s>', lambda event=None: save_proj())
        projmenu.entryconfig("SaveAs", state='normal')


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def start_parsing(x, filename=False, reghive=False, recbin=False, live=False, live_profile=False, user=False):
    switch_view(od_btn, True)
    breadcrumb.clear()
    if len(tv.selection()) > 0:
        tv.selection_remove(tv.selection()[0])
        popup_manager.close_children('')
        file_manager.tv2.delete(*file_manager.tv2.get_children())
        file_manager.tv3.delete(*file_manager.tv3.get_children())
    search_entry.delete(0, 'end')
    search_entry.state(['invalid'])
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    clear_search()
    projmenu.entryconfig("Load", state='disable')
    root.unbind('<Alt-KeyPress-2>')
    if not live:
        widgets_disable()
    start = time.time()

    if x == 'loose':
        offline_db = pd.DataFrame(columns=['resourceID', 'ListSync'])

        if filename['Microsoft.ListSync.db'] != '':
            pb.configure(mode='indeterminate')
            value_label['text'] = 'Gathering offline data. Please wait....'
            pb.start()
            logging.info("Stared parsing Microsoft.ListSync.db")
            exporter = SQLiteTableExporter.SQLiteTableExporter(filename['Microsoft.ListSync.db'])
            offline_db = exporter.get_offline_data()
            pb.stop()
            value_label['text'] = 'Complete'

        if filename['Microsoft.FileUsageSync.db'] != '':
            cache = {"Path": '', "Name": '', "Hash": '', "Account": ''}
            has_menu_data = any(menu_data[key] for key in ['json', 'csv', 'html'])
            missing_all_files = not any([
                filename['*.dat *.dat.previous'],
                filename['SyncEngineDatabase.db'],
                filename['SafeDelete.db']
            ])
            directory, file = os.path.split(filename['Microsoft.FileUsageSync.db'])
            value_label['text'] = 'Gathering file usage data. Please wait....'
            fus.set_db_path(directory)
            logging.info("Stared parsing Microsoft.FileUsageSync.db")
            fus.get_recent_files_formatted_spo()
            file_usage_frame.set_data(fus.df_data)
            pb.stop()
            value_label['text'] = 'Complete'
            if has_menu_data and missing_all_files:
                save_output(cache, pd.DataFrame(), pd.DataFrame(), '')

        if filename['*.dat *.dat.previous'] != '':
            account = os.path.dirname(filename['*.dat *.dat.previous'].replace('/', '\\')).rsplit('\\', 1)[-1]
            name = f'{account}_{os.path.split(filename["*.dat *.dat.previous"])[1]}'

            od_settings = DATParser.parse_dat(filename['*.dat *.dat.previous'], account,
                                              gui=True, pb=pb,
                                              value_label=value_label)

            if od_settings:
                if not od_settings.df.empty:
                    parse_results(od_settings, filename['*.dat *.dat.previous'], name, start, x, reghive, recbin, offline_db, gui=True, pb=pb, value_label=value_label)

        if filename['SyncEngineDatabase.db'] != '' or filename['SafeDelete.db'] != '':
            sedb = filename['SyncEngineDatabase.db'].replace('/', '\\')
            sddb = filename['SafeDelete.db'].replace('/', '\\')
            filename = False

            pb.configure(mode='indeterminate')
            value_label['text'] = 'Building folder list. Please wait....'
            pb.start()
            od_settings = SQLiteParser.parse_sql(filename, sedb, sddb)

            if not filename:
                filename = [sedb, sddb]

            if od_settings:
                parse_results(od_settings, filename, od_settings.account, start, x, reghive, recbin, offline_db, gui=True, pb=pb, value_label=value_label)

    elif x == 'Profile':
        if live:
            profile = live_profile
        else:
            profile = {}
            filename = filename.replace('/', '\\')
            settings_dir = re.compile(r'\\settings\\(?P<account>Personal|Business[0-9])$')
            listsync_settings_dir = re.compile(r'\\ListSync\\(?P<account>Business[0-9])\\settings$')
            logs_dir = re.compile(r'\\(?P<logs>logs)$')

            if reghive:
                try:
                    Registry.Registry(reghive)
                except Exception:
                    try:
                        parts = os.path.splitdrive(reghive)[1].replace('\\', '/').rsplit('/', 2)
                        alt_path = f'{parts[0]}/{parts[1]}'
                        key = parts[-2]
                        value_label['text'] = f"Searching for {key}'s NTUSER.DAT. Please wait...."
                        pb.configure(mode='indeterminate')
                        pb.start()
                        reghive = live_hive(key, alt_path)
                    except Exception:
                        pass

            for path, subdirs, files in os.walk(filename):
                settings_find = re.findall(settings_dir, path)
                listsync_find = re.findall(listsync_settings_dir, path)
                logs_find = re.findall(logs_dir, path)

                if settings_find:
                    profile.setdefault(settings_find[0], {})
                    profile[settings_find[0]].setdefault('settings', '')
                    profile[settings_find[0]]['settings'] = path

                if listsync_find:
                    profile.setdefault(listsync_find[0], {})
                    profile[listsync_find[0]].setdefault('listsync', '')
                    profile[listsync_find[0]]['listsync'] = path

                if logs_find:
                    profile.setdefault(logs_find[0], [])
                    profile[logs_find[0]].append(path)

        for key, value in profile.items():
            offline_db = pd.DataFrame(columns=['resourceID', 'ListSync'])
            if key == 'logs':
                if menu_data['odl'] is True:
                    for folder_name in value:
                        if user:
                            pname = f'{user}_{folder_name.split(os.sep)[-2]}'
                        else:
                            pname = folder_name.split(os.sep)[-2]

                        odl = parse_odl(folder_name, pname, pb, value_label, gui=True)

                        tb = ttk.Frame()

                        if not odl.empty:
                            pt = pandastablepatch.MyTable(tb,
                                                          dataframe=odl,
                                                          maxcellwidth=900,
                                                          showtoolbar=False,
                                                          showstatusbar=False,
                                                          enable_menus=True,
                                                          editable=False)
                            tv_frame.add(tb, text=f'{pname} Logs  ')
                            pt.adjustColumnWidths()
                            pt.show()
                            user_logs.setdefault(f'{pname}_logs.csv', pt)

                        if menu_data['odl_save'] is True:
                            value_label['text'] = f"Saving {pname}_logs.csv. Please wait...."
                            pb.configure(mode='indeterminate')
                            pb.start()
                            log_output = f'{menu_data["path"]}/{pname}_logs.csv'
                            odl.to_csv(log_output, index=False)
                            pb.stop()

                continue

            # First, process "listsync" if it exists
            if "listsync" in value:
                v = value["listsync"].replace('/', '\\')
                pb.configure(mode='indeterminate')
                value_label['text'] = 'Gathering offline data. Please wait....'
                pb.start()
                logging.info("Stared parsing Microsoft.ListSync.db")
                exporter = SQLiteTableExporter.SQLiteTableExporter(f'{v}\\Microsoft.ListSync.db')
                offline_db = exporter.get_offline_data()
                value_label['text'] = 'Gathering file usage data. Please wait....'
                fus.set_db_path(f'{v}')
                logging.info("Stared parsing Microsoft.FileUsageSync.db")
                fus.get_recent_files_formatted_spo()
                file_usage_frame.set_data(fus.df_data)
                pb.stop()

            # Then process "settings" if it exists
            if "settings" in value:
                v = value["settings"].replace('/', '\\')
                pb.configure(mode='indeterminate')
                value_label['text'] = 'Building folder list. Please wait....'
                pb.start()
                for path, subdirs, files in os.walk(v):
                    for name in files:
                        if name.endswith('.dat') and not (name.endswith('import.dat') or name.endswith('screenshot.dat')):
                            od_settings = DATParser.parse_dat(f'{v}\\{name}', key,
                                                              gui=True, pb=pb,
                                                              value_label=value_label)
                            if od_settings:
                                if not od_settings.df.empty:
                                    if user:
                                        pname = f'{user}_{od_settings.account}_{name}'
                                    else:
                                        pname = f'{od_settings.account}_{name}'
                                    parse_results(od_settings, f'{v}\\{name}', pname, start, x, reghive, recbin, pd.DataFrame(columns=['resourceID', 'ListSync']), gui=True, pb=pb, value_label=value_label)
                pb.configure(mode='indeterminate')
                value_label['text'] = 'Building folder list. Please wait....'
                pb.start()
                od_settings = SQLiteParser.parse_sql(v)
                if od_settings:
                    if not od_settings.df.empty:
                        if user:
                            pname = f'{user}_{key}'
                        else:
                            pname = key
                        parse_results(od_settings, v, pname, start, x, reghive, recbin, offline_db, gui=True, pb=pb, value_label=value_label)
                pb.stop()

        pb.stop()
        pb.configure(mode='determinate')
        value_label['text'] = 'Profile complete'

    elif x == 'Import JSON':
        cache = json.load(filename)
        df = pd.DataFrame()
        rbin_df = pd.DataFrame()

        pb.stop()
        pb.configure(mode='indeterminate')
        value_label['text'] = "Building tree. Please wait..."
        pb.start()
        parent_child(cache, account=cache['Account'])
        pb.stop()

        od_counts(filename.name, df, rbin_df, start, x)

    elif x == 'Import CSV':
        pb.configure(mode='indeterminate')
        value_label['text'] = 'Building folder list. Please wait....'
        pb.start()
        account = ''
        od_settings = parse_csv(filename['_OneDrive.csv'])

        if od_settings:
            parse_results(od_settings, filename['_OneDrive.csv'], '', start, x, reghive, recbin, od_settings.offline_db, gui=True, pb=pb, value_label=value_label, save=False)

    elif x == 'Project':
        name = filename
        pass

    else:
        try:
            filename = filename.replace('/', '\\')
        except Exception:
            pass
        logging.warning(f'Unable to parse {filename}.')  # see about changing to name
        value_label['text'] = f'Unable to parse {filename}.'  # see about changing to name
        pb['value'] = 0
        pb.configure(mode='determinate')
        pb.stop()

    if len(tv.get_children()) > 0:
        odsmenu.entryconfig("Unload all files", state='normal')
        projmenu.entryconfig("Save", state='normal')
        root.bind('<Alt-s>', lambda event=None: save_proj())
        projmenu.entryconfig("SaveAs", state='normal')
        file_menu.entryconfig("Export 'OneDrive Folders'", state='normal')
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

    if not live:
        widgets_normal()


def parse_results(od_settings, filename, key, start, x, reghive, recbin, offline_db, gui, pb, value_label, save=True):
    pb.configure(mode='indeterminate')
    value_label['text'] = 'Building folder list. Please wait....'
    pb.start()
    cache, df, rbin_df = OneDriveParser.parse_onedrive(od_settings,
                                                       filename,
                                                       reghive,
                                                       recbin,
                                                       offline_db,
                                                       gui=True,
                                                       pb=pb,
                                                       value_label=value_label)

    pb.stop()
    pb.configure(mode='indeterminate')
    value_label['text'] = "Building tree. Please wait..."
    pb.start()
    if cache:
        parent_child(cache, None, od_settings.comment['Account'] if hasattr(od_settings, "comment") else od_settings.account)

    pb.stop()

    od_counts(key, df, rbin_df, start, x)
    if save:
        save_output(cache, df, rbin_df, key)


def od_counts(filename, df, rbin_df, start, x):
    if x == 'Import JSON':
        curItem = tv.get_children()[-1]
        file_count, del_count, folder_count = json_count(item=curItem)
    else:
        file_count = df.Type.value_counts().get('File', 0) if not df.empty else 0
        folder_count = df.Type.value_counts().get('Folder', 0) if not df.empty else 0
        del_count = len(rbin_df) if not rbin_df.empty else 0

    pb['value'] = 0
    pb.configure(mode='determinate')
    value_label['text'] = f'{file_count} file(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds'
    logging.info(f'{filename}: {file_count} file(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds')


def save_output(cache, df, rbin_df, name):
    if menu_data['json']:
        value_label['text'] = "Saving JSON. Please wait...."
        pb.configure(mode='indeterminate')
        pb.start()
        try:
            print_json(cache, name, fus.json_data, menu_data['pretty'], menu_data['path'])
        except Exception as e:
            logging.warning(f'Unable to save json. {e}')
        pb.stop()

    if menu_data['csv']:
        value_label['text'] = "Saving CSV. Please wait...."
        pb.configure(mode='indeterminate')
        pb.start()

        comment = {
            "Path": cache["Path"],
            "Name": cache["Name"],
            "Hash": cache["Hash"],
            "Account": cache["Account"]
        }

        comment_json = json.dumps(comment)

        try:
            print_csv(df, rbin_df, name, menu_data['path'], comment_json, fus.df_data)
        except Exception as e:
            logging.warning(f'Unable to save csv. {e}')
        pb.stop()

    if menu_data['html']:
        value_label['text'] = "Saving HTML. Please wait...."
        pb.configure(mode='indeterminate')
        pb.start()
        try:
            print_html(df, rbin_df, name, menu_data['path'], fus.df_data)
        except Exception as e:
            logging.warning(f'Unable to save html. {e}')
        pb.stop()

    pb['value'] = 0
    pb.configure(mode='determinate')
    value_label['text'] = 'Complete'


def del_logs():
    global proj_name
    for item in tv_frame.winfo_children():
        for i in item.winfo_children():
            if '.!frame.!frame.!myscrollablenotebook.!notebook2.' in str(i):
                if str(i) == '.!frame.!frame.!myscrollablenotebook.!notebook2.!frame':
                    continue
                i.destroy()

    for item in root.winfo_children():
        if '.!frame' in str(item):
            if str(item) == '.!frame':
                continue
            item.destroy()

    for item in infoFrame.winfo_children():
        if '.!notebook.!frame.' in str(item):
            item.destroy()

    user_logs.clear()
    odlmenu.entryconfig("Unload all ODL logs", state='disable')
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
        root.unbind('<Alt-s>')
        projmenu.entryconfig("SaveAs", state='disable')
        projmenu.entryconfig("Unload", state='disable')
        proj_name = None


def rebind():
    global bind_id
    bind_id = message.bind('<Double-Button-1>',
                           lambda event=None: Messages(root))


def log_tab():
    if tv_frame.index("current") != 0:
        pwv.remove(infoNB)
    else:
        pwv.add(infoNB, minsize=100)


def load_proj():
    global proj_name
    global s_image

    def thread_load():
        t1 = threading.Thread(target=clear_all, daemon=True)
        t1.start()
        root.after(200, check_if_ready, t1, "lp")
        SyncMessage(root)
        root.event_generate("<Configure>")
        tv.grid_forget()
        del_logs()
        t1.join()
        root.event_generate("<Configure>")
        proj_name = filename
        q = Queue()
        stop_event = threading.Event()
        threading.Thread(target=load_project,
                         args=(filename, q, stop_event, tv, file_items, fus, pb, value_label,),
                         daemon=True,).start()
        threading.Thread(target=proj_parse,
                         args=(q, proj_name,),
                         daemon=True,).start()

        projmenu.entryconfig("Unload", state='normal')

    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDriveExplorer project file",
                                                      "*.ode_proj"),
                                                     ))

    if filename:
        projmenu.entryconfig("Load", state='disable')
        root.unbind('<Alt-KeyPress-2>')
        message.unbind('<Double-Button-1>', bind_id)
        s_image.clear()
        s_image = load_images(filename)
        threading.Thread(target=thread_load, daemon=True).start()


def proj_parse(q, proj_name):
    widgets_disable()
    search_entry.delete(0, 'end')
    search_entry.state(['invalid'])
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    clear_search()

    while True:
        data = q.get()
        if '_logs.csv' in data[0]:
            key = data[0].split('_')[0]
            tb = ttk.Frame()
            pt = pandastablepatch.MyTable(tb,
                                          dataframe=data[1],
                                          maxcellwidth=900,
                                          showtoolbar=False,
                                          showstatusbar=False,
                                          enable_menus=True,
                                          editable=False)
            tv_frame.add(tb, text=f'{key} Logs  ')
            pt.adjustColumnWidths()
            pt.show()
            user_logs.setdefault(f'{key}_logs.csv', pt)
            q.task_done()

        if data[0] == 'done':
            pb.stop()
            break

    file_usage_frame.set_data(fus.df_data)
    widgets_normal()
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
    proj_name = proj_name.split('/')[-1]
    value_label['text'] = f"{proj_name} import complete"
    pb.configure(mode='determinate')
    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
    if len(tv.get_children()) > 0:
        odsmenu.entryconfig("Unload all files", state='normal')
        file_menu.entryconfig("Export 'OneDrive Folders'", state='normal')
    tv.grid(row=1, column=0, sticky="nsew")


def save_proj():
    global proj_name
    saveAs_proj(filename=proj_name)


def saveAs_proj(filename=None):
    global proj_name
    if filename is None:
        filename = filedialog.asksaveasfilename(defaultextension=".ode_proj")

    if filename:
        tv.grid_forget()
        message.unbind('<Double-Button-1>', bind_id)
        proj_name = filename
        threading.Thread(target=thread_save,
                         args=(filename,),
                         daemon=True).start()

        projmenu.entryconfig("Unload", state='normal')


def thread_save(filename):
    widgets_disable()
    file_manager.tv2.delete(*file_manager.tv2.get_children())
    file_manager.tv3.delete(*file_manager.tv3.get_children())
    search_entry.delete(0, 'end')
    search_entry.state(['invalid'])
    search_entry.configure(state="disabled")
    search_entry.configure(cursor='arrow')
    clear_search()
    breadcrumb.unbind_left()
    breadcrumb.unbind_right()
    breadcrumb.unbind_up()
    breadcrumb.disable_crumbs()

    save_project(tv, file_items, filename, user_logs, s_image, fus.df_data, pb, value_label)

    widgets_normal()
    breadcrumb.bindings()
    breadcrumb.enable_crumbs()
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
    tv.grid(row=1, column=0, sticky="nsew")


def export_tree(ext=None):
    filelocation = filedialog.asksaveasfilename(defaultextension=f'.{ext.lower()}')

    if filelocation:
        x = root.winfo_rootx()+main_frame.winfo_x()+tv_frame.winfo_x()+tv_inner_frame.winfo_x()+tv.winfo_x()
        y = root.winfo_rooty()+main_frame.winfo_y()+tv_frame.winfo_y()+tv_inner_frame.winfo_y()+tv.winfo_y()
        x1 = x+tv.winfo_width()
        y1 = y+tv.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(filelocation, ext, resolution=100.0)


def split_font(font):
    parts = []
    bracket_level = 0
    current = []
    # trick to remove special-case of trailing chars
    for c in (font + " "):
        if c == " " and bracket_level == 0:
            parts.append("".join(current))
            current = []
        else:
            if c == "{":
                bracket_level += 1
            elif c == "}":
                bracket_level -= 1
            current.append(c)

    if len(parts) == 2:
        parts.append('')

    return parts


def font_changed(font):
    global default_font
    root.tk.call('tk', 'fontchooser', 'configure', '-font', font)
    default_font = font
    pandastablepatch.default_font = font
    details.config(font=default_font)
    font = split_font(font)
    options = {'font': font[0],
               'fontsize': font[1],
               'fontstyle': ' '.join(font[2:])
               }
    for item in infoFrame.winfo_children():
        if '!mytable' in str(item):
            config.apply_options(options, item)
            item.redraw()
    style.configure('Result.Treeview', rowheight=40)
    menu_data['font'] = default_font
    file_manager.update_font()
    save_settings()


def apply_font_to_all(widget, font_obj):
    """Recursively apply the font to all child widgets."""
    try:
        widget["font"] = font_obj
    except tk.TclError:
        pass  # Some ttk widgets don't accept "font" directly

    for child in widget.winfo_children():
        apply_font_to_all(child, font_obj)


def click(event):
    if len(search_entry.get()) > 0:
        search_entry.state(['!invalid'])
    else:
        search_entry.state(['invalid'])
        clear_search()


def sync():
    if getattr(sys, 'frozen', False):
        t1 = threading.Thread(target=os.system,
                              args=("OneDriveExplorer.exe --sync --gui",),
                              daemon=True)
    else:
        t1 = threading.Thread(target=os.system,
                              args=("start /wait cmd /c OneDriveExplorer.py --sync --gui",),
                              daemon=True)

    t1.start()
    root.after(200, check_if_ready, t1, "s")


def check_if_ready(thread, t_string):
    global cstruct_df
    global sync_message
    if thread.is_alive():
        # not ready yet, run the check again soon
        root.after(200, check_if_ready, thread, t_string)
    else:
        if t_string == "ts":
            widgets_normal()
            search_result()
        if t_string == "s":
            cstruct_df = load_cparser(args.cstructs)
        if t_string == "tca" or t_string == "df":
            sync_message = None
            widgets_normal()
        if t_string == "lp":
            root.event_generate("<Configure>")
            return


def thread_search():
    clear_search()
    widgets_disable()
    message.unbind('<Double-Button-1>', bind_id)
    t1 = threading.Thread(target=search, daemon=True)
    t1.start()
    root.after(200, check_if_ready, t1, "ts")


def thread_clear_all():
    global sync_message
    message.unbind('<Double-Button-1>', bind_id)
    sync_message = SyncMessage(root)
    t1 = threading.Thread(target=clear_all, daemon=True)
    t1.start()
    root.after(200, check_if_ready, t1, "tca")


def widgets_disable():
    tabs = tb.tabs()
    for i, item in enumerate(tabs):
        if str(item).endswith('!frame'):
            continue
        tb.tab(item, state='disable')
    for item in infoFrame.winfo_children():
        if '.!notebook.!frame.' in str(item):
            item.destroy()
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    menubar.entryconfig("View", state="disabled")
    menubar.entryconfig("Help", state="disabled")
    btn.configure(state="disabled")
    for tab_index in reversed(range(1, details_frame.tab_count())):
        details_frame.delete_tab(tab_index)
    tv.grid_forget()
    unbind_events(od_btn)
    od_btn.config(state='disable')
    unbind_events(email_btn)
    email_btn.config(state='disable')
    unbind_events(t_meeting_btn)
    t_meeting_btn.config(state='disable')
    unbind_events(event_btn)
    event_btn.config(state='disable')
    unbind_events(chat_btn)
    chat_btn.config(state='disable')
    unbind_events(notes_btn)
    notes_btn.config(state='disable')
    unbind_events(sp_btn)
    sp_btn.config(state='disable')


def widgets_normal():
    tabs = tb.tabs()
    for i, item in enumerate(tabs):
        if str(item).endswith('!frame'):
            continue
        tb.tab(item, state="normal")
    rebind()
    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    menubar.entryconfig("View", state="normal")
    menubar.entryconfig("Help", state="normal")
    if len(tv.get_children()) > 0:
        search_entry.configure(state="normal")
        search_entry.configure(cursor='xterm')
        btn.configure(state="normal")
    tv.grid(row=1, column=0, sticky="nsew")
    bind_events(od_btn, on_enter, on_leave, lambda event: switch_view(od_btn, True))
    od_btn.config(state='normal')
    if len(file_usage_frame.emails_tree.get_children()) > 0:
        bind_events(email_btn, on_enter, on_leave, lambda event: [switch_view(email_btn), file_usage_frame.show_emails_list()])
        email_btn.config(state='normal')
    if len(file_usage_frame.meetings_tree.get_children()) > 0:
        bind_events(t_meeting_btn, on_enter, on_leave, lambda event: [switch_view(t_meeting_btn), file_usage_frame.show_meetings_list()])
        t_meeting_btn.config(state='normal')
    if len(file_usage_frame.events_tree.get_children()) > 0:
        bind_events(event_btn, on_enter, on_leave, lambda event: [switch_view(event_btn), file_usage_frame.show_events_list()])
        event_btn.config(state='normal')
    if len(file_usage_frame.chats_tree.get_children()) > 0:
        bind_events(chat_btn, on_enter, on_leave, lambda event: [switch_view(chat_btn), file_usage_frame.show_chats_list()])
        chat_btn.config(state='normal')
    if len(file_usage_frame.notes_tree.get_children()) > 0:
        bind_events(notes_btn, on_enter, on_leave, lambda event: [switch_view(notes_btn), file_usage_frame.show_notes_list()])
        notes_btn.config(state='normal')
    if len(file_usage_frame.files_tree.get_children()) > 0:
        bind_events(sp_btn, on_enter, on_leave, lambda event: [switch_view(sp_btn), file_usage_frame.show_sp_list()])
        sp_btn.config(state='normal')


def get_total_column_width():
    total_width = file_manager.tv3.column("#0", width=None)
    total_width += file_manager.tv2.column("#0", width=None)
    for col in file_manager.tv3["columns"]:
        if menu_data[str(col)]:
            total_width += file_manager.tv3.column(col, width=None)  # Get the current width of each column

    return total_width


# Function to limit sash movement
def restrict_sash(*args):
    if dragging_sash:
        sash0_position = pwh.sash_coord(0)[0]  # Get the current sash position
        sash2_position = pwh.sash_coord(2)[0]  # Get the current sash position
        total_treeview_width = get_total_column_width()  # Get total column width
        max_sash = sash0_position + total_treeview_width + file_manager.fscrollbv.winfo_width() + 12
        if sash2_position > max_sash:
            pwh.sash_place(2, max_sash, 1)  # Restrict sash to column width
        pwh.after(1, restrict_sash)


def switch_view(selected, od=False):
    separator.grid_forget()
    separator.grid(row=selected.grid_info()['row'], column=0, sticky="ns")

    if od:
        file_usage_frame.grid_forget()
        main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    else:
        main_frame.grid_forget()
        file_usage_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)


def on_enter(event, label, bg):
    # Lighten the default background color
    hover_color = change_color(bg, 0.3)
    style.configure(f'{label}Hover.TLabel', background=hover_color, foreground='black')


def on_leave(event, label):
    fg = style.lookup('TLabel', 'foreground')

    if fg == '':
        fg = 'black'
    style.configure(f'{label}Hover.TLabel', background=style.lookup('TLabel', 'background'), foreground=fg)


def change_color(hex_color, saturation_factor=0.2, brightness_factor=-0.2, lighten=True):
    hex_color = str(hex_color).lstrip('#')
    try:
        sbf_rgb = root.winfo_rgb(hex_color)
        hex_color = "{:02X}{:02X}{:02X}".format(sbf_rgb[0] // 256, sbf_rgb[1] // 256, sbf_rgb[2] // 256)
    except Exception:
        pass
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    hls = colorsys.rgb_to_hls(*[c / 255.0 for c in rgb])
    if lighten:
        change_hls = (hls[0], min(1, hls[1] + saturation_factor), hls[2])
    else:
        change_hls = (hls[0], max(0, hls[1] - saturation_factor), max(0, hls[2] + brightness_factor))
    change_rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(*change_hls))
    change_hex = "#{:02X}{:02X}{:02X}".format(*change_rgb)
    return change_hex


def update_theme_colors(event=None):
    global bg, bgf, fgf  # Ensure we update the global variables

    bg = style.lookup('TFrame', 'background')
    bgf = style.lookup('Treeview', 'background')
    fgf = style.lookup('Treeview', 'foreground') or "black"

    # Apply the updated colors to relevant widgets
    style.configure("Custom.TFrame", background=bg)
    style.configure("Treeview", background=bgf, foreground=fgf)

    style.configure("Disabled.TEntry", foreground="gray", fieldbackground="#bbbbbb")

    root.update_idletasks()  # Force a visual refresh


def bind_events(widget, enter_func, leave_func, click_func):
    widget.bind("<Enter>", lambda event, l=widget.cget("text"): enter_func(event, l, bgf))
    widget.bind("<Leave>", lambda event, l=widget.cget("text"): leave_func(event, l))
    widget.bind("<Button-1>", click_func)


def unbind_events(widget):
    widget.unbind("<Enter>")
    widget.unbind("<Leave>")
    widget.unbind("<Button-1>")


root = ThemedTk(gif_override=True)
root.report_callback_exception = report_callback_exception
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap(application_path + '/Images/titles/OneDrive.ico')
root.geometry('1440x880')
root.minsize(40, 40)
root.protocol("WM_DELETE_WINDOW", lambda: QuitDialog(root))

default_font = str(menu_data['font'])
pandastablepatch.root = root
pandastablepatch.default_font = default_font
pandastablepatch.application_path = application_path

root.tk.call('tk', 'fontchooser', 'configure', '-font', default_font,
             '-command', root.register(font_changed))

style = ttk.Style()
font = split_font(default_font)
style.configure('Result.Treeview', rowheight=40)
style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))

style.configure("Disabled.TEntry", foreground="gray", fieldbackground="#bbbbbb")

sel_bg = style.lookup("Treeview", "background", state=["selected"])
bg = style.lookup('TFrame', 'background')
bgf = style.lookup('Treeview', 'background')
fgf = style.lookup('Treeview', 'foreground')

if not fgf:
    fgf = 'black'

images = (
    tk.PhotoImage("img_close", data='''
        R0lGODlhCwALAPcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr
        /wBVAABVMwBVZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCq
        mQCqzACq/wDVAADVMwDVZgDVmQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMA
        MzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMrzDMr/zNVADNVMzNVZjNVmTNVzDNV
        /zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq/zPVADPVMzPVZjPV
        mTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YrAGYr
        M2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA
        /2aqAGaqM2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/
        mWb/zGb//5kAAJkAM5kAZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlV
        M5lVZplVmZlVzJlV/5mAAJmAM5mAZpmAmZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq
        /5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwAM8wAZswA
        mcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV/8yAAMyA
        M8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV
        /8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8r
        mf8rzP8r//9VAP9VM/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+q
        M/+qZv+qmf+qzP+q///VAP/VM//VZv/Vmf/VzP/V////AP//M///Zv//mf//zP//
        /wAAAAAAAAAAAAAAACH5BAEAAPwALAAAAAALAAsAAAhTAIlN6jVwYCNJtyZNEkiw
        YK9GjHxN2rfPIMVJjAZS3Ndooy2FBDdSlASRYEiKjG6RbHRyI6NeGXttlInyJSOK
        DyXhZBQzIy+VtngS44nxoNFJAQEAOw
        '''),
    tk.PhotoImage("img_closeactive", data='''
        R0lGODlhCwALAPcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr
        /wBVAABVMwBVZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCq
        mQCqzACq/wDVAADVMwDVZgDVmQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMA
        MzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMrzDMr/zNVADNVMzNVZjNVmTNVzDNV
        /zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq/zPVADPVMzPVZjPV
        mTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YrAGYr
        M2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA
        /2aqAGaqM2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/
        mWb/zGb//5kAAJkAM5kAZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlV
        M5lVZplVmZlVzJlV/5mAAJmAM5mAZpmAmZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq
        /5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwAM8wAZswA
        mcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV/8yAAMyA
        M8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV
        /8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8r
        mf8rzP8r//9VAP9VM/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+q
        M/+qZv+qmf+qzP+q///VAP/VM//VZv/Vmf/VzP/V////AP//M///Zv//mf//zP//
        /wAAAAAAAAAAAAAAACH5BAEAAPwALAAAAAALAAsAAAhUAN21Y3fOnEFz4L61W7jw
        HEGD4Got3LcPIsWE5tpRrLjxmy1zBTdeNPfNYEiKB2uBMyhyHzuEKzeak/ntGziU
        DlHWLLnyoLlytc7VqvVtaNGi5gICADs
        '''),
    tk.PhotoImage("img_closepressed", data='''
        R0lGODlhCwALAPcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr
        /wBVAABVMwBVZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCq
        mQCqzACq/wDVAADVMwDVZgDVmQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMA
        MzMAZjMAmTMAzDMA/zMrADMrMzMrZjMrmTMrzDMr/zNVADNVMzNVZjNVmTNVzDNV
        /zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzDOq/zPVADPVMzPVZjPV
        mTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YrAGYr
        M2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA
        /2aqAGaqM2aqZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/
        mWb/zGb//5kAAJkAM5kAZpkAmZkAzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlV
        M5lVZplVmZlVzJlV/5mAAJmAM5mAZpmAmZmAzJmA/5mqAJmqM5mqZpmqmZmqzJmq
        /5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwAM8wAZswA
        mcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV/8yAAMyA
        M8yAZsyAmcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV
        /8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8r
        mf8rzP8r//9VAP9VM/9VZv9Vmf9VzP9V//+AAP+AM/+AZv+Amf+AzP+A//+qAP+q
        M/+qZv+qmf+qzP+q///VAP/VM//VZv/Vmf/VzP/V////AP//M///Zv//mf//zP//
        /wAAAAAAAAAAAAAAACH5BAEAAPwALAAAAAALAAsAAAhqACVR0aKlEKGDBnkVJPSK
        0KJXtCC+0kJoWLtCrlwNG7bIFaFC7YS1q9jOHESDGs8NYzfslaKGhWgVYnnOVa2I
        DAm1G3ZO2LBaEAnVGmZumMZ2vGrVMshSIstaHoHajAj1Jq+GtYTGBMorIAA7
        '''),
    tk.PhotoImage("img_blank", data='''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAA
        AARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAATSURBVDhPYxgF
        o2AUjAIwYGAAAAQQAAGnRHxjAAAAAElFTkSuQmCC
        ''')
    )

ButtonNotebook()
ButtonEntry()

# menu images
live_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/computer_desktop.png'))
ods_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/cloud_cyan.png'))
proj_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/tables.png'))
saveas_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/floppy_35inch_black.png'))
exit_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/no.png'))
pro_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/profile.png'))
json_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/file_yellow_hierarchy1_expanded.png'))
csv_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/table.png'))
uaf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/delete_red.png'))
folderop_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/directory_open.png'))
loadl_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/table_new.png'))
save_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/floppy_35inch_green.png'))
ual_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/table_delete.png'))
png_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/PNG-16.png'))
pdf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/PDF-16.png'))
font_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/format_normal.png'))
skin_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/skin.png'))
gsync_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/arrow_plain_green_S.png'))
pref_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/controls.png'))
message_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/language_blue.png'))
cstruct_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/table_column.png'))
question_small_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/question_small.png'))
ode_small_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/ode_small.png'))
saved_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/saved.png'))
loadi_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/menu/files_yellow_combine.png'))

# gui images
search_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/magnifier.png'))  # main
root_drive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/hdd.png'))  # treeview 1
del_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/file_yellow_trashcan.png'))  # treeview 1
tenant_sync_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/Icon59.png'))  # treeview 1
vault_closed_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/Icon109.png'))  # treeview 1
vault_open_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/Icon114.png'))  # treeview 1
od_folder_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/Icon11.ico'))  # treeview 1 & popup
od_p_folder_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/popup/Icon282.ico'))  # treeview 1
merror_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/error_small.png'))  # messages
minfo_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/info_small.png'))  # messages
warning_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/warning.png'))  # messages
info_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/info.png'))  # ExportResult
error_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/error.png'))  # ExportResult
asc_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/table_sort_asc.png'))  # pandastable
desc_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/table_sort_desc.png'))  # pandastable
reg_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/registry.png'))  # hive
trash_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/trashcan.png'))  # recbin
ode_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/ode.png'))  # about
meta_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/tools.png'))  # about
calendar_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/calendar.png'))  # sidebar
chat_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/chat-bubble.png'))  # sidebar
onedrive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/onedrive.png'))  # sidebar
email_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/email.png'))  # sidebar
note_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/note.png'))  # sidebar
sharepoint_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/gui/sharepoint.png'))  # sidebar

# small file images
file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/files/file_yellow.png'))
file_del_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/files/file_yellow_delete.png'))
not_sync_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/files/not_sync_file.png'))
not_link_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/files/not_link_file.png'))

# small folder images
dir_img = Image.open(application_path + '/Images/folders/directory.png')
directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/folders/directory_closed.png'))
link_directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/folders/67.png'))
sync_directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/folders/sync_directory.png'))

# small folder images color
f_1_img = Image.open(application_path + '/Images/colors/1.png')
f_2_img = Image.open(application_path + '/Images/colors/2.png')
f_3_img = Image.open(application_path + '/Images/colors/3.png')
f_4_img = Image.open(application_path + '/Images/colors/4.png')
f_5_img = Image.open(application_path + '/Images/colors/5.png')
f_6_img = Image.open(application_path + '/Images/colors/6.png')
f_7_img = Image.open(application_path + '/Images/colors/7.png')
f_8_img = Image.open(application_path + '/Images/colors/8.png')
f_9_img = Image.open(application_path + '/Images/colors/9.png')
f_10_img = Image.open(application_path + '/Images/colors/10.png')
f_11_img = Image.open(application_path + '/Images/colors/11.png')
f_12_img = Image.open(application_path + '/Images/colors/12.png')
f_13_img = Image.open(application_path + '/Images/colors/13.png')
f_14_img = Image.open(application_path + '/Images/colors/14.png')
f_15_img = Image.open(application_path + '/Images/colors/15.png')
link_img = Image.open(application_path + '/Images/folders/link.png')
not_link_img = Image.open(application_path + '/Images/folders/not_link.png')
sync_img = Image.open(application_path + '/Images/folders/sync.png')
not_sync_img = Image.open(application_path + '/Images/folders/not_sync.png')
unknown_img = Image.open(application_path + '/Images/folders/unknown.png')

# big folder images color
f_1_big_img = Image.open(application_path + '/Images/colors/1_big.png')
f_2_big_img = Image.open(application_path + '/Images/colors/2_big.png')
f_3_big_img = Image.open(application_path + '/Images/colors/3_big.png')
f_4_big_img = Image.open(application_path + '/Images/colors/4_big.png')
f_5_big_img = Image.open(application_path + '/Images/colors/5_big.png')
f_6_big_img = Image.open(application_path + '/Images/colors/6_big.png')
f_7_big_img = Image.open(application_path + '/Images/colors/7_big.png')
f_8_big_img = Image.open(application_path + '/Images/colors/8_big.png')
f_9_big_img = Image.open(application_path + '/Images/colors/9_big.png')
f_10_big_img = Image.open(application_path + '/Images/colors/10_big.png')
f_11_big_img = Image.open(application_path + '/Images/colors/11_big.png')
f_12_big_img = Image.open(application_path + '/Images/colors/12_big.png')
f_13_big_img = Image.open(application_path + '/Images/colors/13_big.png')
f_14_big_img = Image.open(application_path + '/Images/colors/14_big.png')
f_15_big_img = Image.open(application_path + '/Images/colors/15_big.png')

# small status images
online_img = Image.open(application_path + '/Images/status/online.png')
online_link_img = Image.open(application_path + '/Images/status/online-link.png')
online_not_link_img = Image.open(application_path + '/Images/status/online_not_link.png')
online_sync_img = Image.open(application_path + '/Images/status/online_sync.png')
online_not_sync_img = Image.open(application_path + '/Images/status/online_not_sync.png')
excluded_img = Image.open(application_path + '/Images/status/excluded.png')
available_img = Image.open(application_path + '/Images/status/available.png')
always_available_img = Image.open(application_path + '/Images/status/always_available.png')
shared_img = Image.open(application_path + '/Images/status/shared.png')
locked_img = Image.open(application_path + '/Images/status/locked.png')

# search images
hdd_big_img = Image.open(application_path + '/Images/search/hdd.png')
cloud_big_img = Image.open(application_path + '/Images/search/cloud_big.png')
cloud_p_big_img = Image.open(application_path + '/Images/search/cloud_p_big.png')
building_big_img = Image.open(application_path + '/Images/search/building_big.png')
directory_big_img = Image.open(application_path + '/Images/search/directory_big.png')
vault_big_img = Image.open(application_path + '/Images/search/vault_big.png')
vault_open_big_img = Image.open(application_path + '/Images/search/vault_open_big.png')
file_yellow_big_img = Image.open(application_path + '/Images/search/file_yellow_big.png')
file_del_big_img = Image.open(application_path + '/Images/search/file_yellow_delete_big.png')
link_big_img = Image.open(application_path + '/Images/search/link_big.png')
not_link_big_img = Image.open(application_path + '/Images/search/not_link_big.png')
sync_big_img = Image.open(application_path + '/Images/search/sync_big.png')
not_sync_big_img = Image.open(application_path + '/Images/search/not_sync_big.png')
online_big_img = Image.open(application_path + '/Images/search/online_big.png')
online_not_sync_big_img = Image.open(application_path + '/Images/search/online_not_sync_big.png')
online_not_link_big_img = Image.open(application_path + '/Images/search/online_not_link_big.png')
available_big_img = Image.open(application_path + '/Images/search/available_big.png')
always_available_big_img = Image.open(application_path + '/Images/search/always_available_big.png')
excluded_big_img = Image.open(application_path + '/Images/search/excluded_big.png')
shared_big_img = Image.open(application_path + '/Images/search/shared_big.png')
locked_big_img = Image.open(application_path + '/Images/search/locked_big.png')
unknown_big_img = Image.open(application_path + '/Images/search/unknown_big.png')

folder_color = {
    1: f_1_img,
    2: f_2_img,
    3: f_3_img,
    4: f_4_img,
    5: f_5_img,
    6: f_6_img,
    7: f_7_img,
    8: f_8_img,
    9: f_9_img,
    10: f_10_img,
    11: f_11_img,
    12: f_12_img,
    13: f_13_img,
    14: f_14_img,
    15: f_15_img
}

pandastablepatch.asc_img = asc_img
pandastablepatch.desc_img = desc_img

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

menubar = tk.Menu(root)
root.config(menu=menubar)

outer_frame = ttk.Frame(root)
main_frame = ttk.Frame(outer_frame, relief='groove', padding=5)

bottom_frame = ttk.Frame(main_frame)

selector_frame = ttk.Frame(outer_frame)

outer_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
selector_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
bottom_frame.grid(row=1, column=0, pady=(5, 0), stick='nsew')

outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_rowconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(0, weight=1)

file_usage_frame = FileUsageFrame(outer_frame, padding=5, relief="groove")
od_btn = ttk.Label(selector_frame, text="OneDrive", image=onedrive_img, compound="top")
email_btn = ttk.Label(selector_frame, text="Email", image=email_img, compound="top")
t_meeting_btn = ttk.Label(selector_frame, text="Meeting", image=calendar_img, compound="top")
event_btn = ttk.Label(selector_frame, text="Events", image=calendar_img, compound="top")
chat_btn = ttk.Label(selector_frame, text="Chat", image=chat_img, compound="top")
notes_btn = ttk.Label(selector_frame, text="Notes", image=note_img, compound="top")
sp_btn = ttk.Label(selector_frame, text="SarePoint", image=sharepoint_img, compound="top")

od_btn.grid(row=0, column=1, sticky="ew")
email_btn.grid(row=1, column=1, sticky="ew")
t_meeting_btn.grid(row=2, column=1, sticky="ew")
event_btn.grid(row=3, column=1, sticky="ew")
chat_btn.grid(row=4, column=1, sticky="ew")
notes_btn.grid(row=5, column=1, sticky="ew")
sp_btn.grid(row=6, column=1, sticky="ew")

od_btn.config(state='disable', style=f'{od_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
email_btn.config(state='disable', style=f'{email_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
t_meeting_btn.config(state='disable', style=f'{t_meeting_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
event_btn.config(state='disable', style=f'{event_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
chat_btn.config(state='disable', style=f'{chat_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
notes_btn.config(state='disable', style=f'{notes_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)
sp_btn.config(state='disable', style=f'{sp_btn.cget("text")}Hover.TLabel', anchor="center", padding=5)

separator = tk.Frame(selector_frame, width=3, bg=sel_bg)

switch_view(od_btn, True)

pwv = tk.PanedWindow(main_frame, orient=tk.VERTICAL,
                     background=bg, sashwidth=6)

tv_frame = ScrollableNotebookpatch.MyScrollableNotebook(main_frame,
                                                        wheelscroll=True,
                                                        style='CustomNotebook')

tv_frame.enable_traversal()
tv_inner_frame = ttk.Frame(tv_frame)
tv_frame.add(tv_inner_frame, text='OneDrive Folders  ')

handle = tk.Frame(root, bg="black", cursor="sb_h_double_arrow")
pwh = tk.PanedWindow(tv_inner_frame, orient=tk.HORIZONTAL,
                     background=bgf, sashwidth=6, showhandle=False)

tv_pane_frame = tk.Frame(pwh, background=bgf)

tv_columns = [" Path"]
treeview_widget = TreeviewHeaderWidget(tv_pane_frame, columns=tv_columns)

tv = ttk.Treeview(tv_pane_frame,
                  show="tree",
                  selectmode='browse',
                  takefocus='false')
tv.heading('#0', text=' Path', anchor='w')
tv.column('#0', minwidth=40, width=250, stretch=True, anchor='w')

breadcrumb = Breadcrumb(tv_inner_frame)

find_frame = ttk.Frame(tv_inner_frame)

find_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(find_frame, width=30,
                         exportselection=0, style='CustomEntry')
btn = ttk.Button(find_frame,
                 image=search_img,
                 takefocus=False,
                 command=lambda: [thread_search(), SyncMessage(root)])
search_entry.configure(state="disabled")
search_entry.configure(cursor='arrow')
btn.configure(state="disabled")

sep = ttk.Separator(tv_inner_frame, orient=tk.HORIZONTAL)

scrollbv = ttk.Scrollbar(tv_pane_frame, orient="vertical", command=tv.yview)
scrollbh = ttk.Scrollbar(tv_pane_frame, orient="horizontal", command=tv.xview)

value_label = ttk.Label(bottom_frame, text='')
pb = ttk.Progressbar(bottom_frame, orient='horizontal',
                     length=160, mode='determinate')
sl = ttk.Separator(bottom_frame, orient='vertical')
message = ttk.Label(bottom_frame, text=0, background='red',
                    anchor='center', width=3)
sr = ttk.Separator(bottom_frame, orient='vertical')
sg = ttk.Sizegrip(bottom_frame)

details_frame = DetailsFrame(pwh)
tab1 = details_frame.add_tab("Details")
details = details_frame.add_textbox(tab1)
details.configure(font=default_font, background=bgf, foreground=fgf, relief='flat', undo=False, spacing3=3, width=50, padx=10, pady=10, state='disable')
details.tag_configure('red', foreground="red")
tv.configure(yscrollcommand=scrollbv.set, xscrollcommand=scrollbh.set)
tv.tag_configure('yellow', background="yellow", foreground="black")
tv.tag_configure('red', foreground="red")

tv_pane_frame.grid_rowconfigure(1, weight=1)
tv_pane_frame.grid_columnconfigure(0, weight=1)

details_frame.grid_rowconfigure(0, weight=1)
details_frame.grid_columnconfigure(0, weight=1)

tv_inner_frame.grid_rowconfigure(2, weight=1)
tv_inner_frame.grid_columnconfigure(0, weight=1)

result_frame = ttk.Frame(pwh)

result_frame.grid_rowconfigure(0, weight=1)
result_frame.grid_columnconfigure(0, weight=1)

tvr = ttk.Treeview(result_frame,
                   columns=('_'),
                   selectmode='browse',
                   takefocus='false',
                   show="tree",
                   style='Result.Treeview')
tvr.heading('#0', text='', anchor='w')
tvr.heading('_', text='', anchor='w')
tvr.column('_', stretch=False)
tvr.grid(row=0, column=0, sticky="nsew")
tvr.tag_configure('red', foreground="red")
rscrollbv = ttk.Scrollbar(result_frame, orient="vertical", command=tvr.yview)
tvr.configure(yscrollcommand=rscrollbv.set)
popup_manager = PopupManager(root, tv, application_path, details, breadcrumb)
file_manager = FileManager(tv, pwh, cur_sel, handle)
pwh.add(tv_pane_frame, minsize=40, width=250)
pwh.add(file_manager.tv2, minsize=80, width=170)
pwh.add(file_manager.tab2, minsize=247)
pwh.add(details_frame, minsize=40)

infoNB = ttk.Notebook()
infoFrame = ttk.Frame(infoNB)
infoNB.add(infoFrame, text='Log Entries')

pwv.add(tv_frame, minsize=100)
pwv.add(infoNB, minsize=100)

search_entry.grid(row=0, column=0, sticky="e", padx=(5, 0), pady=5)
btn.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="e")

pwv.grid(row=0, column=0, sticky="nsew")
breadcrumb.grid(row=0, column=0, sticky='ew')
find_frame.grid(row=0, column=1, sticky='ew')
sep.grid(row=1, column=0, columnspan=2, sticky="ew")
pwh.grid(row=2, column=0, columnspan=2, sticky="nsew")
treeview_widget.grid(row=0, column=0, sticky="ew")
tv.grid(row=1, column=0, sticky="nsew")
scrollbv.grid(row=0, column=1, rowspan=2, sticky="nsew")
scrollbh.grid(row=2, column=0, sticky="nsew")
rscrollbv.grid(row=0, column=1, sticky="nsew")
details.grid(row=0, column=0, sticky='nsew')

value_label.grid(row=0, column=0, sticky='se')
pb.grid(row=0, column=1, padx=5, sticky='se')
sl.grid(row=0, column=2, padx=(0, 1), sticky='ns')
message.grid(row=0, column=3, sticky='nse')
sr.grid(row=0, column=4, padx=(1, 2), sticky='nse')
sg.grid(row=0, column=5, sticky='se')

# needed for fixes when changing from breeze theme
la = root.nametowidget('.!frame.!frame.!myscrollablenotebook.!frame.!label')
ra = root.nametowidget('.!frame.!frame.!myscrollablenotebook.!frame.!label2')
tb = root.nametowidget('.!frame.!frame.!myscrollablenotebook.!notebook2')

tool_tip_manager = ToolTipManager()

tv.bind('<<TreeviewSelect>>', file_manager.new_selection)
tv.bind('<Button-1>', lambda event=None: clear_search())
tv.bind("<Button-3>", popup_manager.do_popup)
tvr.bind('<<TreeviewSelect>>', file_manager.new_selection)
tvr.bind('<Double-Button-1>', file_manager.handle_double_click)
tv.bind('<Alt-Down>', lambda event=None: popup_manager.open_children(tv.selection()))
tv.bind('<Alt-Up>', lambda event=None: popup_manager.close_children(tv.selection()))
root.bind('<Control-o>', lambda event=None: open_profile(file_menu))
root.bind('<Control-m>', lambda event=None: Messages(root))
root.bind('<Alt-KeyPress-0>', lambda event=None: clear_all())
root.bind('<Alt-KeyPress-2>', lambda event=None: load_proj())
root.bind('<Alt-s>', lambda event=None: save_proj())
root.bind('<<NotebookTabChanged>>', lambda event=None: log_tab())
search_entry.bind('<Return>',
                  lambda event=None: [thread_search(), SyncMessage(root)])
search_entry.bind('<KeyRelease>', click)
bind_id = message.bind('<Double-Button-1>', lambda event=None: Messages(root))
infoNB.bind('<Motion>', tool_tip_manager.motion)
search_entry.bind('<Motion>', tool_tip_manager.motion)
root.nametowidget('.!frame.!frame.!myscrollablenotebook.!notebook2').bind('<Motion>', tool_tip_manager.motion)
root.bind("<<ThemeChanged>>", update_theme_colors)

keyboard.is_pressed('shift')

file_menu = tk.Menu(menubar, tearoff=0)
odsmenu = tk.Menu(file_menu, tearoff=0)
importmenu = tk.Menu(odsmenu, tearoff=0)
odlmenu = tk.Menu(file_menu, tearoff=0)
projmenu = tk.Menu(file_menu, tearoff=0)
exportmenu = tk.Menu(file_menu, tearoff=0)

options_menu = tk.Menu(menubar, tearoff=0)
submenu = tk.Menu(options_menu, tearoff=0)

view_menu = tk.Menu(menubar, tearoff=0)

help_menu = tk.Menu(menubar, tearoff=0)

for theme_name in sorted(root.get_themes()):
    submenu.add_command(label=theme_name,
                        command=lambda t=theme_name: [submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background=''),
                                                      root.set_theme(t),
                                                      style.map("Treeview",
                                                                foreground=fixed_map("foreground"),
                                                                background=fixed_map("background")),
                                                      submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background='grey'),
                                                      save_settings(), pane_config(), ButtonNotebook(), ButtonEntry()])

importmenu.add_command(label="Import JSON", image=json_img,
                       compound='left', command=lambda: import_json(odsmenu))
importmenu.add_command(label="Import CSV", image=csv_img, compound='left',
                       command=lambda: import_csv(odsmenu))

odsmenu.add_command(label="Profile", image=pro_img, compound='left',
                    command=lambda: threading.Thread(target=open_profile,
                                                     args=(odsmenu,),
                                                     daemon=True).start(),
                    accelerator="Ctrl+O")
odsmenu.add_separator()
odsmenu.add_command(label="Load Individual Files", image=loadi_img,
                    compound='left', command=lambda: load_ind())
odsmenu.add_cascade(label="Import Saved Data", image=saved_img, compound='left',
                    menu=importmenu)
odsmenu.add_separator()
odsmenu.add_command(label="Unload all files", image=uaf_img, compound='left',
                    command=lambda: thread_clear_all(), accelerator="Alt+0")
odsmenu.entryconfig("Unload all files", state='disable')

odlmenu.add_command(label="Load ODL logs", image=folderop_img, compound='left',
                    command=lambda: open_odl())
odlmenu.add_command(label="Import CSV", image=csv_img, compound='left',
                    command=lambda: import_odl())
odlmenu.add_command(label="Unload all ODL logs", image=uaf_img,
                    compound='left', command=lambda: del_logs())
odlmenu.entryconfig("Unload all ODL logs", state='disable')

projmenu.add_command(label="Load", image=loadl_img, compound='left',
                     accelerator="Alt+2", command=lambda: load_proj())
projmenu.add_command(label="Save", image=save_img, compound='left',
                     accelerator="Alt+S", command=lambda: save_proj())
projmenu.add_command(label="SaveAs", image=saveas_img, compound='left',
                     command=lambda: saveAs_proj())
projmenu.add_command(label="Unload", image=ual_img, compound='left',
                     command=lambda: [thread_clear_all(), del_logs()])
projmenu.entryconfig("Save", state='disable')
root.unbind('<Alt-s>')
projmenu.entryconfig("SaveAs", state='disable')
projmenu.entryconfig("Unload", state='disable')

exportmenu.add_command(label="PNG", image=png_img, compound='left',
                       command=lambda: export_tree(ext='PNG'))
exportmenu.add_command(label="PDF",  image=pdf_img, compound='left',
                       command=lambda widget=tv: export_tree(ext='PDF'))

file_menu.add_command(label="Live system",
                      image=live_img, compound='left',
                      command=lambda: [message.unbind('<Double-Button-1>', bind_id),
                                       threading.Thread(target=live_system,
                                       args=(file_menu,),
                                       daemon=True).start()])

file_menu.add_cascade(label="OneDrive metadata", menu=odsmenu,
                      image=ods_img, compound='left')

file_menu.add_cascade(label="OneDrive logs", menu=odlmenu,
                      image=directory_img, compound='left')
file_menu.entryconfig("OneDrive logs", state='disable')
if menu_data['odl'] is True:
    file_menu.entryconfig("OneDrive logs", state='normal')
file_menu.add_separator()
file_menu.add_cascade(label="Project", menu=projmenu,
                      image=proj_img, compound='left')
file_menu.add_separator()
file_menu.add_cascade(label="Export 'OneDrive Folders'", menu=exportmenu,
                      image=saveas_img, compound='left')
file_menu.add_separator()
file_menu.add_command(label="Exit", image=exit_img, compound='left',
                      command=lambda: QuitDialog(root))

file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')

options_menu.add_command(label="Font", image=font_img, compound='left',
                         command=lambda: root.tk.call('tk', 'fontchooser', 'show'))
options_menu.add_cascade(label="Skins", image=skin_img,
                         compound='left', menu=submenu)
options_menu.add_separator()
options_menu.add_command(label="Sync with Github", image=gsync_img,
                         compound='left', command=lambda: [sync(), SyncMessage(root)])
options_menu.add_separator()
options_menu.add_command(label="Preferences", image=pref_img,
                         compound='left', command=lambda: Preferences(root))

view_menu.add_command(label="Messages", image=message_img, accelerator="Ctrl+M",
                      compound='left', command=lambda: Messages(root))
view_menu.add_separator()
view_menu.add_command(label="CStructs", image=cstruct_img,
                      compound='left', command=lambda: CStructs(root, cstruct_df))

help_menu.add_command(label="Quick help", image=question_small_img,
                      compound='left', command=lambda: Help(root))
help_menu.add_command(label="About", image=ode_small_img,
                      compound='left', command=lambda: About(root))

menubar.add_cascade(label="File",
                    menu=file_menu)
menubar.add_cascade(label="Options",
                    menu=options_menu)
menubar.add_cascade(label="View",
                    menu=view_menu)
menubar.add_cascade(label="Help",
                    menu=help_menu)
submenu.entryconfig(submenu.index(ttk.Style().theme_use()),
                    background='grey')

if not ctypes.windll.shell32.IsUserAnAdmin():
    file_menu.entryconfig("Live system", state="disabled")

tool_tip_manager.create_tooltip(message, text='Total messages\n'
                                '  Contains the total number of messages available. A yellow\n'
                                '  background indicates a warning message is available. A red\n'
                                '  background indicates an error message is available.',
                                flip=True)


logging.info(f'OneDriveExplorer {__version__} ready!')

parser = argparse.ArgumentParser()
parser.add_argument("--cstructs", help="The path where ODL cstructs are located. Defaults to 'cstructs' folder where program was executed.")
args = parser.parse_args()
cstruct_df = load_cparser(args.cstructs)
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

if getattr(sys, 'frozen', False):
    pyi_splash.close()

ButtonEntry(do_bind=True)

root.mainloop()
