import os
import sys
import re
import base64
import json
import ctypes
import webbrowser
import argparse
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog
import tkinter.font as tkFont
import threading
from queue import Queue
from io import StringIO
from collections import defaultdict
import pandas as pd
import numpy as np
from pandastable import config
from PIL import ImageTk, Image, ImageGrab
import time
import keyboard
from ruamel.yaml import YAML
import logging
from io import StringIO as StringBuffer
from datetime import datetime
from cerberus import Validator
import warnings
from ode.renderers.json import print_json_gui
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
from ode.renderers.project import save_project
from ode.renderers.project import load_project
from ode.parsers.dat_new import parse_dat
from ode.parsers.csv_file import parse_csv
from ode.parsers.onedrive import parse_onedrive
from ode.parsers.odl import parse_odl, load_cparser
from ode.parsers.sqlite_db import parse_sql
from ode.helpers.mft import live_hive
from ode.helpers import pandastablepatch
from ode.helpers import ScrollableNotebookpatch
from ode.utils import schema
from ode.helpers.AnimatedGif import AnimatedGif
warnings.filterwarnings("ignore", category=UserWarning)

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

log_capture_string = StringBuffer()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s, %(levelname)s, %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(log_capture_string)]
                    )

__author__ = "Brian Maloney"
__version__ = "2023.09.13"
__email__ = "bmmaloney97@gmail.com"
rbin = []
user_logs = {}
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
                             "odl_save": false,\
                             "font": null}'
                           )

    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


class quit:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("Please confirm")
        self.win.iconbitmap(application_path + '/Images/favicon.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)
        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

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
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))


class preferences:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("Preferences")
        self.win.iconbitmap(application_path + '/Images/controls.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)

        self.json_save = tk.BooleanVar(value=menu_data['json'])
        self.json_pretty = tk.BooleanVar(value=menu_data['pretty'])
        self.csv_save = tk.BooleanVar(value=menu_data['csv'])
        self.html_save = tk.BooleanVar(value=menu_data['html'])
        self.auto_path = tk.StringVar(value=menu_data['path'])
        self.skip_hive = tk.BooleanVar(value=menu_data['hive'])
        self.odl = tk.BooleanVar(value=menu_data['odl'])
        self.odl_save = tk.BooleanVar(value=menu_data['odl_save'])

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.select_frame = ttk.LabelFrame(self.inner_frame,
                                           text="<UserCid>.dat output")
        self.path_frame = ttk.Frame(self.inner_frame)
        self.hive_frame = ttk.Frame(self.inner_frame)
        self.odl_frame = ttk.LabelFrame(self.inner_frame,
                                        text="ODL settings")
        self.exit_frame = ttk.Frame(self.inner_frame)

        self.exit_frame.grid_rowconfigure(0, weight=1)
        self.exit_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0, sticky="nsew")
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.select_frame.grid(row=0, column=0, sticky="nsew")
        self.odl_frame.grid(row=1, column=0, pady=25, sticky="nsew")
        self.path_frame.grid(row=2, column=0, pady=(0, 25), sticky="nsew")
        self.hive_frame.grid(row=3, column=0, pady=(0, 25), sticky="nsew")
        self.exit_frame.grid(row=4, column=0, sticky="nsew")

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
                                   textvariable=self.auto_path,
                                   exportselection=0)
        self.btn = ttk.Button(self.path_frame, text='...', width=3,
                              takefocus=False, command=self.select_dir)

        self.reghive = ttk.Checkbutton(self.hive_frame,
                                       text="Disable loading user hive dialog",
                                       var=self.skip_hive,
                                       offvalue=False,
                                       onvalue=True,
                                       takefocus=False
                                       )

        self.en_odl = ttk.Checkbutton(self.odl_frame,
                                      text="Enable ODL log parsing",
                                      var=self.odl,
                                      offvalue=False,
                                      onvalue=True,
                                      takefocus=False,
                                      command=self.odl_config
                                      )

        self.auto_odl = ttk.Checkbutton(self.odl_frame,
                                        text="Auto Save ODL",
                                        var=self.odl_save,
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
        self.en_odl.grid(row=0, column=0, padx=5, sticky="w")
        self.auto_odl.grid(row=1, column=0, padx=5, sticky="w")
        self.save.grid(row=0, column=0, pady=5, sticky="e")
        self.cancel.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        if self.json_save.get() is False:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

        if self.odl.get() is False:
            self.auto_odl.configure(state="disabled")
            self.odl_save.set(False)

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

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
            self.auto_odl.configure(state="normal")
        else:
            self.auto_odl.configure(state="disabled")
            self.odl_save.set(False)

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
        menu_data['odl'] = self.odl.get()
        menu_data['odl_save'] = self.odl_save.get()
        if menu_data['odl'] is True:
            file_menu.entryconfig("OneDrive logs", state='normal')
        else:
            file_menu.entryconfig("OneDrive logs", state='disable')
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
        self.win.title("Load User Hive")
        self.win.iconbitmap(application_path + '/Images/question.ico')
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

        self.label_i = ttk.Label(self.inner_frame, image=question_img)
        self.label = ttk.Label(self.inner_frame,
                               text="User's registry hive allows the mount points of the SyncEngines to be resolved.\n\nDo you want to provide a registry hive?\n")

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

        self.label_i.grid(row=0, column=0, rowspan=2, sticky='n')
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
                                             title="Open",
                                             filetypes=(("Load user hive",
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
        self.win.iconbitmap(application_path + '/Images/trashcan.ico')
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


class messages:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Messages")
        self.win.iconbitmap(application_path + '/Images/language_blue.ico')
        self.win.minsize(400, 300)
        self.win.grab_set()
        self.win.focus_force()
        self.win.protocol("WM_DELETE_WINDOW", self.close_mess)
        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)
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
        self.tree = ttk.Treeview(self.inner_frame,
                                 columns=self.columns,
                                 yscrollcommand=self.tree_scroll.set)
        self.tb_scroll = ttk.Scrollbar(self.inner_frame)
        self.tb = tk.Text(self.inner_frame,
                          undo=False,
                          height=10,
                          width=87,
                          yscrollcommand=self.tb_scroll.set)
        self.total = ttk.Label(self.inner_frame, text='Total messages:')
        self.value_label = ttk.Label(self.inner_frame, text='')
        self.pb = ttk.Progressbar(self.inner_frame, orient='horizontal',
                                  length=160, mode='indeterminate')
        self.clear = ttk.Button(self.inner_frame, text='Clear messages',
                                takefocus=False, command=self.clear)
        self.export = ttk.Button(self.inner_frame, text='Export messages',
                                 takefocus=False,
                                 command=lambda: threading.Thread(target=self.exportmessage,
                                                                  daemon=True).start())
        self.sg = ttk.Sizegrip(self.inner_frame)

        self.tree.heading('Message Date', text='Message Date', anchor='w')
        self.tree.heading('Message Type', text='Message Type', anchor='w')
        self.tree.heading('Message', text='Message', anchor='w')
        self.tree.column('#0', minwidth=0, width=50, stretch=False, anchor='w')
        self.tree.column('Message Date', minwidth=0, width=150,
                         stretch=False, anchor='w')
        self.tree.column('Message Type', minwidth=0, width=100,
                         stretch=False, anchor='w')

        self.tree_scroll.config(command=self.tree.yview)
        self.tb_scroll.config(command=self.tb.yview)
        self.tb.config(state='disable')

        self.tree.grid(row=0, column=0, columnspan=5, padx=(10, 0),
                       pady=(10, 0), sticky='nsew')
        self.tree_scroll.grid(row=0, column=5, padx=(0, 10),
                              pady=(10, 0), sticky="nsew")
        self.tb.grid(row=1, column=0, columnspan=5, padx=(10, 0),
                     pady=(5, 10), sticky='nsew')
        self.tb_scroll.grid(row=1, column=5, padx=(0, 10),
                            pady=(5, 10), sticky="nsew")
        self.total.grid(row=2, column=0, padx=(10, 0), pady=(0, 5), stick='w')
        self.value_label.grid(row=2, column=1, padx=5, pady=(0, 5))
        self.pb.grid(row=2, column=2, pady=(0, 5))
        self.clear.grid(row=2, column=3, padx=5, pady=(0, 5), stick='e')
        self.export.grid(row=2, column=4, pady=(0, 5), stick='e')
        self.sg.grid(row=2, column=5, stick='se')
        self.sync_windows()
        self.tree.bind('<<TreeviewSelect>>', self.select)
        self.mcount = (len(log_capture_string.getvalue().split('\n')) - 1)
        self.total['text'] = f'Total messages: {self.mcount}'
        self.value_label.grid_remove()
        self.pb.grid_remove()

        data = log_capture_string.getvalue().split('\n')

        for m in data:
            m = m.split(', ', 2)
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
            self.win.update()

    def select(self, event=None):
        self.tb.config(state='normal')
        self.tb.delete('1.0', tk.END)
        curItem = self.tree.selection()
        values = self.tree.item(curItem, 'values')
        self.tb.insert(tk.END,
                       re.sub("(.{87})", "\\1\n", values[2], 0, re.DOTALL))
        self.tb.config(state='disable')

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

    def exportmessage(self, event=None):
        path = filedialog.askdirectory(initialdir="/")
        if path:
            self.clear.config(state='disable')
            self.export.config(state='disable')
            self.value_label['text'] = "Exporting messages. Please wait..."
            self.pb.start()
            self.value_label.grid(row=2, column=1, pady=(0, 5))
            self.pb.grid(row=2, column=2, pady=(0, 5))
            ids = self.tree.get_children()
            excel_name = path + '\\OneDriveExplorerMessages_' + datetime.now().strftime("%Y-%m-%dT%H%M%S.xlsx")
            lst = []
            for id in ids:
                row = self.tree.item(id, 'values')
                lst.append(row)
            df = pd.DataFrame.from_records(lst, columns=['Message Data',
                                                         'Message Type',
                                                         'Message'])

            try:  # need to thread
                with pd.ExcelWriter(excel_name) as writer:
                    row_count = len(df.index)
                    if row_count > 1048576:
                        groups = df.groupby(np.arange(len(df.index))//1048575)
                        for (frameno, frame) in groups:
                            frame.to_excel(writer,
                                           f'OneDriveExplorer Messages {frameno}',
                                           index=False)
                    else:
                        df.to_excel(writer,
                                    'OneDriveExplorer Messages',
                                    index=False)
                self.pb.stop()
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
            self.value_label.grid_forget()
            self.pb.grid_forget()
            self.clear.config(state='normal')
            self.export.config(state='normal')

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.win.geometry("+%d+%d" % (x, y))

    def close_mess(self):
        self.win.destroy()

    def onmotion(self):
        self.update()


class export_result:
    def __init__(self, root, excel_name, failed=False):
        self.root = root
        self.failed = failed
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        if self.failed:
            self.win.title("Export failed!")
            self.excel_name = excel_name
        else:
            self.win.title("Export successful!")
            self.excel_name = excel_name.replace('/', '\\')
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
        self.label = ttk.Label(self.inner_frame,
                               text=f'Messages exported to:\n\n{self.excel_name}')
        if self.failed:
            self.label_i['image'] = error_img
            self.label['text'] = f'Messages failed to export.\n\n{self.excel_name}'
        self.btn = ttk.Button(self.inner_frame, text='OK',
                              takefocus=False, command=self.ok)

        self.label_i.grid(row=0, column=0)
        self.label.grid(row=0, column=1, padx=(0, 5))
        self.btn.grid(row=1, column=0, columnspan=2, pady=5)

        self.sync_windows()
        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def ok(self):
        self.win.destroy()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        try:
            self.win.geometry("+%d+%d" % (x + w/2, y + h/2))
        except Exception:
            pass


class cstructs:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.win = tk.Toplevel(self.root)
        self.win.title("CStructs")
        self.win.iconbitmap(application_path + '/Images/cstruct.ico')
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_plugins)
        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove')

        self.cstruct_frame = ttk.Frame(self.inner_frame)

        self.bottom_frame = ttk.Frame(self.inner_frame)

        self.plugin_list = tk.Listbox(self.cstruct_frame, activestyle='dotbox',
                                      exportselection=False, width=100, bd=0)
        self.scrollbv = ttk.Scrollbar(self.cstruct_frame, orient="vertical",
                                      command=self.plugin_list.yview)
        self.plugin_list.configure(yscrollcommand=self.scrollbv.set)

        self.code_label = ttk.Label(self.inner_frame, text="Code file",
                                    justify="left", anchor='w')
        self.entry1 = ttk.Entry(self.inner_frame, width=88)
        self.author_label = ttk.Label(self.inner_frame, text="Author",
                                      justify="left", anchor='w')
        self.entry2 = ttk.Entry(self.inner_frame, width=88)
        self.function_label = ttk.Label(self.inner_frame, text="Functions",
                                        justify="left", anchor='w')
        self.function_list = tk.Listbox(self.inner_frame, activestyle='none',
                                        exportselection=False, width=86,
                                        height=3, bd=0, selectmode="SINGLE")
        self.fscrollbv = ttk.Scrollbar(self.inner_frame, orient="vertical",
                                       command=self.function_list.yview)
        self.function_list.configure(yscrollcommand=self.fscrollbv.set)
        self.version_label = ttk.Label(self.inner_frame, text="Version",
                                       justify="left", anchor='w')
        self.entry3 = ttk.Entry(self.inner_frame, width=88)
        self.id_label = ttk.Label(self.inner_frame, text="Internal GUID",
                                  justify="left", anchor='w')
        self.entry4 = ttk.Entry(self.inner_frame, width=88)
        self.description_label = ttk.Label(self.inner_frame, text="Description",
                                           justify="left", anchor='w')
        self.entry5 = ttk.Entry(self.inner_frame, width=88)

        self.load_label = ttk.Label(self.bottom_frame, text="CStructs loaded:",
                                    justify="left", anchor='w')
        self.sl = ttk.Separator(self.bottom_frame, orient='vertical')
        self.total = ttk.Label(self.bottom_frame, text=f"{self.df.shape[0]}",
                               anchor='center', width=3)
        self.sr = ttk.Separator(self.bottom_frame, orient='vertical')
        self.btn = ttk.Button(self.inner_frame, text="Add'l. Info",
                              takefocus=False, command=self.more_info)

        if self.total['text'] == '0':
            self.btn.configure(state='disabled')
            self.entry1.configure(state="disabled")
            self.entry2.configure(state="disabled")
            self.entry3.configure(state="disabled")
            self.entry4.configure(state="disabled")
            self.entry5.configure(state="disabled")
            self.plugin_list.configure(state="disabled")

        if not self.df.empty:
            self.plugin_list.insert("end", *self.df.Code_File)
            self.plugin_list.select_set(0)
            self.selected_item(event=None)

        self.sync_windows(self.win)

        self.frame.grid(row=0, column=0, sticky='nsew')
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.cstruct_frame.grid(row=0, column=0, columnspan=3,
                                padx=10, pady=10, sticky='nsew')
        self.bottom_frame.grid(row=7, column=0, columnspan=3, padx=10,
                               pady=(10, 2), sticky='sw')

        self.plugin_list.grid(row=0, column=0, sticky="nsew")
        self.scrollbv.grid(row=0, column=1, sticky="nsew")

        self.code_label.grid(row=1, column=0, padx=(10, 0),
                             pady=(0, 5), sticky='w')
        self.entry1.grid(row=1, column=1, padx=(0, 10), columnspan=2,
                         pady=(0, 5), sticky='e')
        self.author_label.grid(row=2, column=0, padx=(10, 0),
                               pady=(0, 5), sticky='w')
        self.entry2.grid(row=2, column=1, padx=(0, 10), columnspan=2,
                         pady=(0, 5), sticky='e')
        self.function_label.grid(row=3, column=0, padx=(10, 0),
                                 pady=(0, 5), sticky='nw')
        self.function_list.grid(row=3, column=1, padx=(4, 0),
                                pady=(0, 5), sticky='e')
        self.fscrollbv.grid(row=3, column=2,
                            padx=(0, 10), pady=(0, 5), sticky="nsew")
        self.version_label.grid(row=4, column=0, padx=(10, 0),
                                pady=(0, 5), sticky='w')
        self.entry3.grid(row=4, column=1, padx=(0, 10), columnspan=2,
                         pady=(0, 5), sticky='e')
        self.id_label.grid(row=5, column=0, padx=(10, 0),
                           pady=(0, 5), sticky='w')
        self.entry4.grid(row=5, column=1, padx=(0, 10), columnspan=2,
                         pady=(0, 5), sticky='e')
        self.description_label.grid(row=6, column=0, padx=(10, 0),
                                    pady=(0, 5), sticky='w')
        self.entry5.grid(row=6, column=1, padx=(0, 10), columnspan=2,
                         pady=(0, 5), sticky='e')

        self.load_label.grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.sl.grid(row=0, column=1, sticky='ns')
        self.total.grid(row=0, column=2)
        self.sr.grid(row=0, column=3, sticky='ns')
        self.btn.grid(row=7, column=1, columnspan=2,
                      padx=10, pady=(0, 5), sticky='e')

        ttk.Style().map('TEntry',
                        foreground=[('disabled',
                                    ttk.Style().lookup('TEntry',
                                                       'foreground'))])

        self.plugin_list.bind("<<ListboxSelect>>", self.selected_item)
        self.function_list.bind('<Button>', lambda a: "break")
        self.function_list.bind('<Motion>', lambda a: "break")

    def selected_item(self, event):
        for i in self.plugin_list.curselection():
            text = self.df.loc[self.df.Code_File == self.plugin_list.get(i)].values.tolist()[0]
            self.function_list.delete(0, "end")
            for x in text[5]:
                self.function_list.insert("end", f"\u2008{x['Function']}")
            self.entry1.configure(state="normal")
            self.entry2.configure(state="normal")
            self.entry3.configure(state="normal")
            self.entry4.configure(state="normal")
            self.entry5.configure(state="normal")
            self.entry1.delete(0, "end")
            self.entry2.delete(0, "end")
            self.entry3.delete(0, "end")
            self.entry4.delete(0, "end")
            self.entry5.delete(0, "end")
            self.entry1.insert(0, text[4])
            self.entry2.insert(0, text[1])
            self.entry3.insert(0, text[2])
            self.entry4.insert(0, text[3])
            self.entry5.insert(0, text[0])
            self.entry1.configure(state="disabled")
            self.entry2.configure(state="disabled")
            self.entry3.configure(state="disabled")
            self.entry4.configure(state="disabled")
            self.entry5.configure(state="disabled")

    def more_info(self):
        self.info = tk.Toplevel(self.win)
        self.info.title("CStructs")
        self.info.iconbitmap(application_path + '/Images/cstruct.ico')
        self.info.grab_set()
        self.info.focus_force()
        self.info.resizable(False, False)
        hwnd = get_parent(self.info.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

        self.info_frame = ttk.Frame(self.info)

        self.info_inner_frame = ttk.Frame(self.info_frame, padding=5,
                                          relief='groove')

        self.scrollb = ttk.Scrollbar(self.info_inner_frame)
        self.info_text = CustomText(self.info_inner_frame,
                                    yscrollcommand=self.scrollb.set,
                                    padx=5,
                                    pady=5,
                                    fg="DarkOrange2")
        self.scrollb.config(command=self.info_text.yview)

        self.info_text.tag_configure("blue", foreground="blue")
        self.info_text.tag_configure("black", foreground="black")
        self.info_text.tag_configure("green", foreground="green")
        self.info_text.tag_configure("gray", foreground="dim gray")
        self.info_text.tag_configure("dblue", foreground="DodgerBlue2")
        self.info_text.tag_configure("black2", foreground="black")
        self.info_text.tag_configure("dgreen", foreground="DarkSeaGreen3")

        yaml = YAML()
        yaml.compact(seq_seq=False, seq_map=False)
        string_stream = StringIO()

        for i in self.plugin_list.curselection():
            text = self.df.loc[self.df.Code_File == self.plugin_list.get(i)].values.tolist()[0]
            yaml.dump(text[5], string_stream)
            self.info_text.insert("end", string_stream.getvalue())
            self.info_text.highlight_pattern("Function|Description|Flags|Structure(?=:)", "blue", regexp=True)
            self.info_text.highlight_pattern(":\s|:\s\||\s.*?(?=;)", "black", regexp=True)
            self.info_text.highlight_pattern("#\s.*?$", "green", regexp=True)
            self.info_text.highlight_pattern("#define\s.*?$|{|}|;|(\];)|(?:\S)(\[)", "gray", regexp=True)
            self.info_text.highlight_pattern("(?:\S)(?=\[)", "black2", regexp=True)
            self.info_text.highlight_pattern("//.*?$", "dgreen", regexp=True)
            self.info_text.highlight_pattern("\s(BYTE|CHAR|DWORD|INT|INT128|INT16|INT32|INT64|INT8|LONG|LONG32|LONG64|LONGLONG|OWORD|QWORD|SHORT|UCHAR|UINT|UINT128|UINT16|UINT32|UINT64|UINT8|ULONG|ULONG64|ULONGLONG|USHORT|WCHAR|WORD|__int128|__int16|__int32|__int64|__int8|char|int|int128|int128_t|int16|int16_t|int32|int32_t|int64|int64_t|int8|int8_t|long long|long|short|signed char|signed int|signed long long|signed long|signed short|struct|u1|u16|u2|u4|u8|uchar|uint|uint128|uint128_t|uint16|uint16_t|uint32|uint32_t|uint64|uint64_t|uint8|uint8_t|ulong|unsigned __int128|unsigned char|unsigned int|unsigned long long|unsigned long|unsigned short|ushort|void|wchar|wchar_t)\s", "dblue", regexp=True)

        self.info_frame.grid(row=0, column=0)
        self.info_inner_frame.grid(row=0, column=0)
        self.info_text.grid(row=0, column=0)
        self.scrollb.grid(row=0, column=1, sticky='nsew')

        self.sync_windows(self.info)

        self.info_text.bind('<Key>', lambda a: "break")
        self.info_text.bind('<Button>', lambda a: "break")
        self.info_text.bind('<Motion>', lambda a: "break")

    def sync_windows(self, window, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        window.geometry("+%d+%d" % (x, y))

    def close_plugins(self):
        self.win.destroy()


class help:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.title("Help")
        self.win.iconbitmap(application_path + '/Images/question.ico')
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_help)

        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

        self.frame = ttk.Frame(self.win)
        self.label1 = ttk.Label(self.frame, text="To load <UserCid>.dat, File -> OneDrive settings -> Load <UserCid>.dat", justify="left", anchor='w')
        self.label2 = ttk.Label(self.frame, text="Once <UserCid>.dat is loaded, OneDriveExplorer operates much like File Explorer.", justify="left", anchor='w')
        self.label3 = ttk.Label(self.frame, text="Context menu\nRight click on folder/file to export Name, Path, Details, etc.", justify="left", anchor='w')
        self.label4 = ttk.Label(self.frame, text="ODL logs\nTo enable parsing, Options -> Preferences -> Enable ODL log parsing.", justify="left", anchor='w')
        self.label5 = ttk.Label(self.frame, text="Live System\nRun OneDriveExplorer as administrator to activate.", justify="left", anchor='w')
        self.label6 = ttk.Label(self.frame, text="For full details, see the included manual.", justify="left", anchor='w')

        self.frame.grid(row=0, column=0)
        self.label1.grid(row=0, column=0,
                         padx=(10, 30), pady=(5, 0), sticky='w')
        self.label2.grid(row=1, column=0, padx=(10, 30), sticky='w')
        self.label3.grid(row=2, column=0, padx=(10, 30), sticky='w')
        self.label4.grid(row=3, column=0, padx=(10, 30), sticky='w')
        self.label5.grid(row=4, column=0, padx=(10, 30), sticky='w')
        self.label6.grid(row=5, column=0,
                         padx=(10, 30), pady=(0, 20), sticky='w')
        self.sync_windows()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))

    def close_help(self):
        self.win.destroy()


class about:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("About OneDriveExplorer")
        self.win.iconbitmap(application_path + '/Images/favicon.ico')
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close_about)

        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)

        self.frame = ttk.Frame(self.win)
        self.label = ttk.Label(self.frame, image=ode_img, anchor='n')
        self.label1 = ttk.Label(self.frame, text="OneDriveExplorer",
                                justify="left", anchor='w')
        self.label2 = ttk.Label(self.frame, text=f"Version {__version__}",
                                justify="left", anchor='w')
        self.label3 = ttk.Label(self.frame, text=f"Copyright © {__version__[:4]}",
                                justify="left", anchor='w')
        self.label4 = ttk.Label(self.frame, text="Brian Maloney",
                                justify="left", anchor='w')
        self.label5 = ttk.Label(self.frame, text="L̲a̲t̲e̲s̲t̲_R̲e̲l̲e̲a̲s̲e̲",
                                foreground='#0563C1', cursor="hand2",
                                justify="left", anchor='w')
        self.text = tk.Text(self.frame, width=27, height=8, wrap=tk.WORD)
        line = "GUI based application for reconstructing the folder structure of OneDrive"
        self.text.insert(tk.END, line)
        self.text.config(state='disable')
        self.scrollbv = ttk.Scrollbar(self.frame, orient="vertical",
                                      command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbv.set)

        self.ok = ttk.Button(self.frame,
                             text="OK",
                             takefocus=False,
                             command=self.close_about)

        self.frame.grid(row=0, column=0)
        self.label.grid(row=0, column=0, rowspan=6,
                        padx=10, pady=(10, 0), sticky='n')
        self.label1.grid(row=0, column=1,
                         padx=(0, 10), pady=(10, 0), sticky='w')
        self.label2.grid(row=1, column=1, sticky='w')
        self.label3.grid(row=2, column=1, sticky='w')
        self.label4.grid(row=3, column=1, sticky='w')
        self.label5.grid(row=4, column=1,
                         padx=(0, 10), pady=(0, 10), sticky='w')
        self.text.grid(row=5, column=1, sticky='w')
        self.scrollbv.grid(row=5, column=2, padx=(0, 10), sticky="nsew")
        self.ok.grid(row=6, column=1, padx=(0, 10), pady=10, sticky='e')

        self.label5.bind("<Double-Button-1>", self.callback)
        self.sync_windows()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/4 - qw/4, y + h/2 - qh/2))

    def callback(self, event=None):
        webbrowser.open_new_tab("https://github.com/Beercow/OneDriveExplorer/releases/latest")
        self.label5.configure(foreground='#954F72')

    def close_about(self):
        self.win.destroy()


class sync_message:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("")
        self.win.iconbitmap(application_path + '/Images/favicon.ico')
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)
        hwnd = get_parent(self.win.winfo_id())
        #   getting the old style
        old_style = get_window_long(hwnd, GWL_STYLE)
        #   building the new style (old style AND NOT Maximize AND NOT Minimize)
        new_style = old_style & ~ WS_MAXIMIZEBOX & ~ WS_MINIMIZEBOX
        #   setting new style
        set_window_long(hwnd, GWL_STYLE, new_style)
        self.win.overrideredirect(1)

        reg_font = ("Segoe UI", 8, "normal")
        bold_font = ("Segoe UI", 16, "bold")

        self.lbl_with_my_gif = AnimatedGif(self.win, application_path + '/Images/load.gif', 0.1)
        self.label = ttk.Label(self.win, text="Please wait           ", font=bold_font)
        self.label1 = ttk.Label(self.win, text="Working...", font=reg_font)

        self.lbl_with_my_gif.grid(row=0, column=0, rowspan=2)
        self.label.grid(row=0, column=1, sticky="nsew")
        self.label1.grid(row=1, column=1, sticky="nsew")

        self.lbl_with_my_gif.start()

        self.sync_windows()

        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def sync_windows(self, event=None):
        if len(threading.enumerate()) <= 3:
            self.root.unbind("<Configure>")
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
        self.win.destroy()

    def __callback(self):
        return


class CustomText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "":
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


class result:

    def __init__(self, master, *args):
        l = list(args[0])
        l[0] = f'  Date modified: {args[0][0]}\n  Size: {args[0][1]}'
        if args[0][6] == 'File - deleted':
            l[0] = f'  DeleteTimeStamp: {args[0][11]}\n  Size: {args[0][1]}'
        values = tuple(l)
        if args[0][6] == 'File':
            if args[0][9] == '2':
                if args[0][11] == '1':
                    tvr.insert("", "end", image=available_shared_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
                else:
                    tvr.insert("", "end", image=available_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
            elif args[0][9] == '5':
                if args[0][11] == '1':
                    tvr.insert("", "end", image=excluded_shared_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
                else:
                    tvr.insert("", "end", image=excluded_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
            elif args[0][9] == '8':
                if args[0][11] == '1':
                    tvr.insert("", "end", image=online_shared_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
                else:
                    tvr.insert("", "end", image=online_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)

            else:  # needs image big file
                if args[0][11] == '1':
                    tvr.insert("", "end", image=shared_file_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
                else:
                    tvr.insert("", "end", image=file_big_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)

        elif args[0][6] == 'File - deleted':
            tvr.insert("", "end", image=file_del_big_img, text=f'  {args[0][5]}\n  {args[0][10]}', values=values, tags='red')

        else:
            if args[0][9] == '5':
                tvr.insert("", "end", image=excluded_directory_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)
            else:
                tvr.insert("", "end", image=online_directory_img, text=f'  {args[0][5]}\n  {args[0][13]}', values=values)


def showtip(text, widget, flip=False, single=False):
    global tipwindow
    matches = ["start_parsing", "live_system", "odl", "load_project", "proj_parse"]

    "Display text in tooltip window"
    if tipwindow or not text:
        return

    # disables tooltip if parsing data
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

    tipwindow = tw = tk.Toplevel(widget)
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
        frame = tk.Frame(tw, width=w+20, height=h2-1, background="grey81", padx=1, pady=1)
    else:
        frame = tk.Frame(tw, width=w+20, height=h2+12, background="grey81", padx=1, pady=1)
    textbox = tk.Text(frame, height=h, font=reg_font, padx=8, relief="flat",
                      bd=0, pady=5)

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


def hidetip():
    global tipwindow
    tw = tipwindow
    tipwindow = None
    if tw:
        tw.destroy()


def CreateToolTip(widget, text, flip=False, single=False, motion=False):
    def enter(event, motion=False):
        showtip(text, widget, flip, single)

    def leave(event):
        hidetip()

    if motion:
        enter(None, motion=True)

    else:
        widget.bind('<Enter>', enter)

    widget.bind('<Leave>', leave)


def motion(event):
    global current_tab
    if event.widget.identify(event.x, event.y) == 'label':
        index = event.widget.index("@%d,%d" % (event.x, event.y))
        if index != 0:
            return
        if current_tab != event.widget.tab(index, 'text'):
            current_tab = event.widget.tab(index, 'text')
            if event.widget.tab(index, 'text') == 'Details':
                text = 'Details\n  Displays detailed information of the file/folder selected.'
            if event.widget.tab(index, 'text') == 'Log Entries':
                text = 'Log Entries\n  Displays related logs to the file/folder selected. This\n  will only be populated if OneDrive logs are parsed\n  along with the <userCid>.dat file.'
            if event.widget.tab(index, 'text') == 'OneDrive Folders  ':
                text = 'OneDrive Folders\n  Displays the <UserCid>.dat files that have been loaded\n  and the folder structure of OneDrive.'
            CreateToolTip(event.widget, text, flip=False, single=False, motion=True)

    elif event.widget.identify(event.x, event.y) == 'clear':
        if 'invalid' not in search_entry.state():
            search_entry.config(cursor='arrow')
            text = 'Clear\n        '
            CreateToolTip(event.widget, text, flip=False, single=True, motion=True)

    else:
        search_entry.config(cursor='xterm')
        hidetip()
        current_tab = None


def ButtonNotebook():

    test = style.map('TNotebook.Tab')
    style.map('CustomNotebook.Tab', **test)

    try:
        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "!invalid", "img_closepressed"),
                             ("active", "!disabled", "!invalid", "img_closeactive"),
                             ("invalid", "img_blank"),
                             border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client",
                                        {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            # ("CustomNotebook.focus", {
                                # "side": "top",
                                # "sticky": "nswe",
                                # "children": [
                                ("CustomNotebook.label",
                                 {"side": "left", "sticky": ''}),
                                ("CustomNotebook.close",
                                 {"side": "left", "sticky": ''}),
                                ]
                            # })
                        # ]
                    })
                ]
            })
        ])
        style.configure('CustomNotebook.Tab', **style.configure('TNotebook.Tab'))
        style.configure('CustomNotebook', **style.configure('TNotebook'))
    except Exception:
        pass

    # Nothing to do with ButtonNotebook, removing focus lines from other tabs
    style.layout("TNotebook.Tab", [
        ('Notebook.tab', {
            'sticky': 'nswe',
            'children': [
                ('Notebook.padding', {
                    'side': 'top',
                    'sticky': 'nswe',
                    'children': [
                        # ('Notebook.focus', {
                            # 'side': 'top',
                            # 'sticky': 'nswe',
                            # 'children': [
                            ('Notebook.label',
                                {'side': 'top', 'sticky': ''})],
                })],
            })],
        # })]
    )

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
                    if '.!notebook2.!frame.' in str(item):
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

    test = style.map('TEntry')
    style.map('CustomEntry', **test)

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
    bg = style.lookup('TFrame', 'background')
    bgf = style.lookup('Treeview', 'background')
    fgf = style.lookup('Treeview', 'foreground')

    if not fgf:
        fgf = 'black'

    pwv.config(background=bg, sashwidth=6)
    pwh.config(background=bgf, sashwidth=2)
    details.config(background=bgf, foreground=fgf)
    style.configure('Result.Treeview', rowheight=40)
    ttk.Style().theme_use()


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
    query = search_entry.get()
    if len(query) == 0:
        return

    children = tv.get_children(item)
    for child in children:
        if query.lower() in str(tv.item(child, 'values')).lower():
            values = tv.item(child, 'values')
            result(root, values)
        if child in file_items:
            for i in file_items[child]:
                if query.lower() in str(tv.item(i, 'values')).lower():
                    values = tv.item(i, 'values')
                    result(root, values)
        search(item=child)


def search_result():
    if len(search_entry.get()) == 0:
        return
    position = pwh.sash_coord(2)
    pwh.remove(tv2)
    pwh.remove(tab2)
    pwh.add(result_frame, minsize=327, after=tv_pane_frame)
    root.update_idletasks()
    pwh.sash_place(1, x=position[0], y=position[1])


def clear_search():
    position = None
    children = tvr.get_children()
    for child in children:
        tvr.delete(child)
    if len(pwh.panes()) == 3:
        position = pwh.sash_coord(1)
    pwh.remove(result_frame)
    pwh.add(tv2, minsize=80, width=340, after=tv_pane_frame)
    pwh.add(tab2, minsize=247, after=tv2)
    if position:
        pwh.sash_place(2, x=position[0], y=position[1])
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')


def clear_all():
    global proj_name
    clear_search()
    tv.delete(*tv.get_children())
    tv2.delete(*tv2.get_children())
    tv3.delete(*tv3.get_children())
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    odsmenu.entryconfig("Unload all files", state='disable')
    file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')
    search_entry.delete(0, 'end')
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
        root.unbind('<Alt-s>')
        projmenu.entryconfig("SaveAs", state='disable')
        projmenu.entryconfig("Unload", state='disable')
        proj_name = None


def json_count(item='', file_count=0, del_count=0, folder_count=0):
    children = tv.get_children(item)
    for child in children:
        values = tv.item(child, 'values')
        if values[6] == 'Folder':
            folder_count += 1
        if values[6] == 'File':
            file_count += 1
        if values[6] == 'File - deleted':
            del_count += 1
        if child in file_items:
            for i in file_items[child]:
                values = tv.item(i, 'values')
                if values[6] == 'Folder':
                    folder_count += 1
                if values[6] == 'File':
                    file_count += 1
                if values[6] == 'File - deleted':
                    del_count += 1
        file_count, del_count, folder_count = json_count(item=child,
                                                         file_count=file_count,
                                                         del_count=del_count,
                                                         folder_count=folder_count)
    return file_count, del_count, folder_count


def ff_count(f, folder_count=0, file_count=0):
    for c in f:
        if c['Type'] == 'Folder':
            folder_count += 1
        if c['Type'] == 'File':
            file_count += 1
    return folder_count, file_count


file_items = defaultdict(list)


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("",
                              "end",
                              image=root_drive_img,
                              text=f" {d['Name']}",
                              values=('',
                                      '',
                                      d['ParentId'],
                                      d['DriveItemId'],
                                      d['eTag'],
                                      d['Name'],
                                      d['Type'],
                                      d['Size'],
                                      d['Hash'],
                                      d['Status'],
                                      d['Date_modified'],
                                      d['Shared'],
                                      len(d['Children']),
                                      d['Path']))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        if c['Type'] == 'Folder':
            parent_child(c, tv.insert(parent_id,
                                      0,
                                      image=folder_img,
                                      text=f" {c['Name']}",
                                      values=('',
                                              '',
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              c['Status'],
                                              c['Date_modified'],
                                              c['Shared'],
                                              len(c['Children']),
                                              c['Path'])))
        elif c['Type'] == 'Root Default':
            parent_child(c, tv.insert(parent_id,
                                      0,
                                      image=default_img,
                                      text=f" {c['Name']}",
                                      values=('',
                                              '',
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              c['Status'],
                                              c['Date_modified'],
                                              c['Shared'],
                                              len(c['Children']),
                                              c['Path'])))
        elif c['Type'] == 'Root Shared':
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=shared_img,
                                      text=f" {c['Name']}",
                                      values=('',
                                              '',
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              c['Status'],
                                              c['Date_modified'],
                                              c['Shared'],
                                              len(c['Children']),
                                              c['Path'])))
        elif c['Type'] == 'Root Deleted':
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=del_img,
                                      text=f" {c['Name']}",
                                      values=('',
                                              '',
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              len(c['Children']),
                                              c['Path']),
                                      tags='red'))
        elif c['Type'] == 'File - deleted':
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=file_del_img,
                                      text=f" {c['Name']}",
                                      values=('',
                                              '',
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              len(c['Children']),
                                              c['Path'],
                                              c['DeleteTimeStamp']),
                                      tags='red'))
        else:
            iid = tv.insert(parent_id,
                            "end",
                            image=file_img,
                            text=f" {c['Name']}",
                            values=(c['Date_modified'],
                                    c['Size'],
                                    c['ParentId'],
                                    c['DriveItemId'],
                                    c['eTag'],
                                    c['Name'],
                                    c['Type'],
                                    c['Size'],
                                    c['Hash'],
                                    c['Status'],
                                    c['Date_modified'],
                                    c['Shared'],
                                    len(c['Children']),
                                    c['Path']))
            parent = tv.parent(iid)
            file_items[parent].append(iid)
            tv.detach(iid)
#        root.update_idletasks()


def live_system(menu):
    global reghive
    global recbin

    message.unbind('<Double-Button-1>', bind_id)
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    menubar.entryconfig("View", state="disabled")
    menubar.entryconfig("Help", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")

    pb.configure(mode='indeterminate')
    value_label['text'] = "Searching for OneDrive. Please wait..."
    pb.start()

    d = {}
    users_folder = os.path.expandvars("%SystemDrive%\\Users\\")
    rec_folder = os.path.expandvars("%SystemDrive%\\$Recycle.Bin\\")
    user_folders = [folder for folder in os.listdir(users_folder) if os.path.isdir(os.path.join(users_folder, folder))]

    settings_folders = []
    logs_folders = []

    sql_dir = re.compile(r'\\Users\\(?P<user>.*?)\\AppData\\Local\\Microsoft\\OneDrive\\settings\\(?P<account>Personal|Business[0-9])$')

    if os.path.exists(rec_folder):
        recbin = rec_folder

    for user in user_folders:
        settings_path = os.path.join(users_folder, user, "AppData\\Local\\Microsoft\\OneDrive\\settings")
        logs_path = os.path.join(users_folder, user, "AppData\\Local\\Microsoft\\OneDrive\\logs")
        if os.path.exists(settings_path):
            for path, subdirs, files in os.walk(settings_path):
                sql_find = re.findall(sql_dir, path)
                if sql_find:
                    d.setdefault(sql_find[0][0], {})
                    d[sql_find[0][0]].setdefault('sql', {})[f'{sql_find[0][1]}'] = path
                for name in files:
                    if '.dat' in name:
                        d.setdefault(user, {})
                        d[user].setdefault('files', []).append(os.path.join(path, name))
            settings_folders.append(settings_path)
        if os.path.exists(logs_path):
            d.setdefault(user, {})
            d[user].setdefault('logs', []).append(logs_path)
            logs_folders.append(logs_path)

    for key, value in d.items():
        filenames = []
        value_label['text'] = f"Searching for {key}'s NTUSER.DAT. Please wait...."
        pb.configure(mode='indeterminate')
        pb.start()
        reghive = live_hive(key, os.path.splitdrive(os.path.join(users_folder, key))[1].replace('\\', '/'))
        for k, v in value.items():
            if k == 'files':
                filenames = v

                if len(filenames) != 0:
                    logging.info(f'Parsing OneDrive dat for {key}')
                    menubar.entryconfig("File", state="disabled")
                    menubar.entryconfig("Options", state="disabled")
                    menubar.entryconfig("View", state="disabled")
                    menubar.entryconfig("Help", state="disabled")
                    search_entry.configure(state="disabled")
                    btn.configure(state="disabled")

                    for filename in filenames:
                        x = menu.entrycget(0, "label")
                        start_parsing(x, filename, reghive, recbin)

            if k == 'sql':
                logging.info(f'Parsing OneDrive SQLite for {key}')
                menubar.entryconfig("File", state="disabled")
                menubar.entryconfig("Options", state="disabled")
                menubar.entryconfig("View", state="disabled")
                menubar.entryconfig("Help", state="disabled")
                search_entry.configure(state="disabled")
                btn.configure(state="disabled")

                for account, sql_dir in v.items():
                    x = 'Load from SQLite'
                    start_parsing(x, sql_dir, reghive, recbin)

    if menu_data['odl'] is True:
        menubar.entryconfig("File", state="disabled")
        menubar.entryconfig("Options", state="disabled")
        menubar.entryconfig("View", state="disabled")
        menubar.entryconfig("Help", state="disabled")
        search_entry.configure(state="disabled")
        btn.configure(state="disabled")
        for key, value in d.items():
            for k, v in value.items():
                if k == 'logs':
                    logs = v
                    pb.stop()
                    odl = parse_odl(logs[0], key, pb, value_label, gui=True)
                    tb = ttk.Frame()
                    pt = pandastablepatch.MyTable(tb,
                                                  dataframe=odl,
                                                  maxcellwidth=900,
                                                  showtoolbar=False,
                                                  showstatusbar=False,
                                                  enable_menus=True,
                                                  editable=False)
                    tv_frame.add(tb, text=f'{key} Logs')
                    pt.adjustColumnWidths()
                    pt.show()
                    user_logs.setdefault(f'{key}_logs.csv', pt)
                    if menu_data['odl_save'] is True:
                        value_label['text'] = f"Saving {key}_logs.csv. Please wait...."
                        pb.configure(mode='indeterminate')
                        pb.start()
                        log_output = f'{menu_data["path"]}/{key}_logs.csv'
                        odl.to_csv(log_output, index=False)
                        pb.stop()

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

    rebind()

    value_label['text'] = "All jobs complete"

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    menubar.entryconfig("View", state="normal")
    menubar.entryconfig("Help", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")

    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
        root.bind('<Alt-s>', lambda event=None: save_proj())
        projmenu.entryconfig("SaveAs", state='normal')


def open_dat(menu):
    global reghive
    global recbin
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDrive dat file",
                                                      "*.dat *.dat.previous"),
                                                     ))

    if filename:
        if keyboard.is_pressed('shift') or menu_data['hive']:
            pass
        else:
            root.wait_window(hive(root).win)

        x = menu.entrycget(0, "label")
        threading.Thread(target=start_parsing,
                         args=(x, filename, reghive, recbin,),
                         daemon=True).start()

    reghive = ''
    recbin = ''


def read_sql(menu):
    global reghive
    folder_name = filedialog.askdirectory(initialdir="/", title="Open")

    if folder_name:
        if keyboard.is_pressed('shift') or menu_data['hive']:
            pass
        else:
            root.wait_window(hive(root, sql=True).win)

        x = menu.entrycget(1, "label")
        threading.Thread(target=start_parsing,
                         args=(x, folder_name, reghive,),
                         daemon=True).start()
    reghive = ''


def import_json(menu):
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import JSON",
                                      filetypes=(("OneDrive dat file",
                                                  "*.json"),))

    if filename:
        x = menu.entrycget(2, "label")
        threading.Thread(target=start_parsing,
                         args=(x, filename,),
                         daemon=True).start()


def import_csv(menu):
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import CSV",
                                      filetypes=(("OneDrive dat file",
                                                  "*.csv"),))

    if filename:
        x = menu.entrycget(3, "label")
        threading.Thread(target=start_parsing,
                         args=(x, filename,),
                         daemon=True).start()


def open_odl():
    folder_name = filedialog.askdirectory(initialdir="/", title="Open")

    if folder_name:
        threading.Thread(target=odl,
                         args=(folder_name,),
                         daemon=True).start()


def import_odl():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import CSV",
                                      filetypes=(("ODL csv file",
                                                  "*.csv"),))
    if filename:
        threading.Thread(target=odl,
                         args=(filename, True,),
                         daemon=True).start()


def odl(folder_name, csv=False):
    message.unbind('<Double-Button-1>', bind_id)
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    menubar.entryconfig("View", state="disabled")
    menubar.entryconfig("Help", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    key_find = re.compile(r'Users/(?P<user>.*)?/AppData')
    if csv:
        key = folder_name.name.split('/')[-1].split('_')[0]
    else:
        key = re.findall(key_find, folder_name)
        if len(key) == 0:
            key = 'ODL'
        else:
            key = key[0]
    pb.stop()
    if csv:
        header_list = ['Filename',
                       'File_Index',
                       'Timestamp',
                       'One_Drive_Version',
                       'OS_Version',
                       'Code_File',
                       'Flags',
                       'Function',
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
        odl = pd.read_csv(folder_name, dtype=str)
        import_headers = odl.axes[1]
        if list(set(import_headers) - set(header_list)):
            odl = pd.DataFrame()
            logging.error(f'{folder_name.name} not a valid ODL csv.')
    else:
        odl = parse_odl(folder_name, key, pb, value_label, gui=True)

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
        tv_frame.add(tb, text=f'{key} Logs')
        pt.show()
        user_logs.setdefault(f'{key}_logs.csv', pt)
    pb.stop()

    if menu_data['odl_save'] is True and not csv:
        log_output = f'{menu_data["path"]}/{key}_logs.csv'
        try:
            value_label['text'] = f"Saving {key}_logs.csv. Please wait...."
            pb.configure(mode='indeterminate')
            pb.start()
            odl.to_csv(log_output, index=False)
        except Exception as e:
            logging.error(e)

    pb.stop()
    pb.configure(mode='determinate')
    value_label['text'] = "Parsing complete"

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
    menubar.entryconfig("View", state="normal")
    menubar.entryconfig("Help", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")
    rebind()

    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
        root.bind('<Alt-s>', lambda event=None: save_proj())
        projmenu.entryconfig("SaveAs", state='normal')


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def start_parsing(x, filename=False, reghive=False, recbin=False, df=False):
    try:
        message.unbind('<Double-Button-1>', bind_id)
    except Exception:
        pass
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    menubar.entryconfig("View", state="disabled")
    menubar.entryconfig("Help", state="disabled")
    search_entry.delete(0, 'end')
    search_entry.state(['invalid'])
    search_entry.configure(state="disabled")
    clear_search()
    btn.configure(state="disabled")

    start = time.time()
    dat = False

    if x == 'Live system':
        account = os.path.dirname(filename.replace('/', '\\')).rsplit('\\', 1)[-1]
        df, name = parse_dat(filename, reghive, recbin, start, account,
                             gui=True, pb=pb, value_label=value_label)
        df, rbin_df = parse_onedrive(df, account, reghive, recbin, gui=True,
                                     pb=pb, value_label=value_label)
        dat = True

    if x == 'Load <UserCid>.dat' + (' '*10):
        account = os.path.dirname(filename.replace('/', '\\')).rsplit('\\', 1)[-1]
        df, name = parse_dat(filename, reghive, recbin, start, account,
                             gui=True, pb=pb, value_label=value_label)
        df, rbin_df = parse_onedrive(df, account, reghive, recbin, gui=True,
                                     pb=pb, value_label=value_label)
        dat = True

    if x == 'Load from SQLite':
        filename = filename.replace('/', '\\')
        sql_dir = re.compile(r'\\Users\\(?P<user>.*?)\\AppData\\Local\\Microsoft\\OneDrive\\settings\\(?P<account>.*?)$')
        sql_find = re.findall(sql_dir, filename)
        try:
            name = f'{sql_find[0][0]}_{sql_find[0][1]}'
        except Exception:
            name = 'SQLite_DB'

        df, rbin_df = parse_sql(filename, reghive, recbin, gui=True, pb=pb, value_label=value_label)

        dat = True

    if x == 'Import JSON':
        cache = json.load(filename)
        df = pd.DataFrame()

    if x == 'Import CSV':
        df, name = parse_csv(filename)
        if not df.empty:
            df, rbin_df = parse_onedrive(df)

    if x == 'Project':
        name = filename
        pass

    if not df.empty:
        try:
            file_count = df.Type.value_counts()['File']

        except KeyError:
            file_count = 0

        try:
            del_count = df.Type.value_counts()['File - deleted']

        except KeyError:
            del_count = 0

        try:
            folder_count = df.Type.value_counts()['Folder']

        except KeyError:
            folder_count = 0

        def subset(dict_, keys):
            return {k: dict_[k] for k in keys}

        cache = {}
        final = []
        is_del = []

        df.loc[df.Type == 'File', ['FileSort']] = df['Name'].str.lower()
        df.loc[df.Type == 'Folder', ['FolderSort']] = df['Name'].str.lower()

        for row in df.sort_values(by=['Level', 'ParentId', 'Type', 'FileSort', 'FolderSort'], ascending=[False, False, False, True, False]).to_dict('records'):
            file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'Status', 'Date_modified', 'Shared', 'Children'))
            if row['Type'] == 'File':
                folder = cache.setdefault(row['ParentId'], {})
                folder.setdefault('Children', []).append(file)
            elif row['Type'] == 'File - deleted':
                file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'DeleteTimeStamp', 'Children'))
                is_del.append(file)
            else:
                folder = cache.get(row['DriveItemId'], {})
                temp = {**file, **folder}
                folder_merge = cache.setdefault(row['ParentId'], {})
                if 'Root' in row['Type']:
                    final.insert(0, temp)
                else:
                    folder_merge.setdefault('Children', []).append(temp)

        if dat:
            for row in rbin_df.to_dict('records'):
                file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'DeleteTimeStamp', 'Children'))
                is_del.append(file)
            try:
                del_count = rbin_df.Type.value_counts()['File - deleted']

            except (KeyError, AttributeError):
                del_count = 0

        cache = {'ParentId': '',
                 'DriveItemId': '',
                 'eTag': '',
                 'Type': 'Root Drive',
                 'Path': '',
                 'Name': name.replace('/', '\\'),
                 'Size': '',
                 'Hash': '',
                 'Status': '',
                 'Date_modified': '',
                 'Shared': '',
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
                   'DeleteTimeStamp': '',
                   'Children': ''
                   }

        if is_del:
            deleted['Children'] = is_del
            final.append(deleted)

        cache['Children'] = final

    if not df.empty or x == 'Import JSON':

        pb.configure(mode='indeterminate')
        value_label['text'] = "Building tree. Please wait..."
        pb.start()
        tv.grid_forget()
        parent_child(cache)
        tv.grid(row=1, column=0, sticky="nsew")
        if x == 'Import JSON':
            curItem = tv.get_children()[-1]
            file_count, del_count, folder_count = json_count(item=curItem)
        if x != 'Live system':
            pb.stop()
            pb.configure(mode='determinate')

        if menu_data['json'] and dat:
            print_json_gui(cache, name, menu_data['pretty'], menu_data['path'])

        if menu_data['csv'] and dat:
            print_csv(df, rbin_df, name, menu_data['path'])

        if menu_data['html'] and dat:
            print_html(df, rbin_df, name, menu_data['path'])

        if x != 'Live system':
            pb['value'] = 0
        value_label['text'] = f'{file_count} file(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds'
        try:
            filename = filename.replace('/', '\\')
        except Exception:
            filename = filename.name.replace('/', '\\')
        logging.info(f'{filename}: {file_count} file(s) - {del_count} deleted, {folder_count} folder(s) in {format((time.time() - start), ".4f")} seconds')

    else:
        try:
            filename = filename.replace('/', '\\')
        except Exception:
            pass
        logging.warning(f'Unable to parse {filename}.')  # see about changing to name
        value_label['text'] = f'Unable to parse {filename}.'  # see about changing to name

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    menubar.entryconfig("View", state="normal")
    menubar.entryconfig("Help", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")

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
    if x != 'Live system':
        rebind()


def do_popup(event):
    rof_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/Icon11.ico'))
    copy_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/copy.png'))
    name_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_empty_new.png'))
    path_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_open.png'))
    details_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/language_window.png'))
    exp_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hierarchy1_expanded.png'))
    col_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hierarchy1.png'))
    try:
        curItem = event.widget.identify_row(event.y)
        event.widget.selection_set(curItem)
        opened = event.widget.item(curItem, 'open')
        values = event.widget.item(curItem, 'values')
        popup = tk.Menu(root, tearoff=0)
        copymenu = tk.Menu(root, tearoff=0)

        if values[6] == 'Root Drive':
            popup.add_command(label="Remove OneDrive Folder",
                              image=rof_img,
                              compound='left',
                              command=lambda: del_folder(curItem))
            popup.add_separator()

        popup.add_cascade(label="Copy",
                          image=copy_img,
                          compound='left',
                          menu=copymenu)
        copymenu.add_command(label="Name",
                             image=name_img,
                             compound='left',
                             command=lambda: copy_name(values))
        copymenu.add_command(label="Path",
                             image=path_img,
                             compound='left',
                             command=lambda: copy_path(values))
        copymenu.add_command(label="Details",
                             image=details_img,
                             compound='left', command=lambda: copy_details())

        if values[6] == 'Root Drive':
            popup.entryconfig("Copy", state='disable')
        else:
            popup.entryconfig("Copy", state='normal')

        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame.!treeview' and (values[6] == 'Folder' or 'Root' in values[6]):
            popup.add_separator()
            popup.add_command(label="Expand folders",
                              image=exp_img, compound='left',
                              command=lambda: open_children(curItem),
                              accelerator="Alt+Down")
            popup.add_command(label="Collapse folders",
                              image=col_img,
                              compound='left',
                              command=lambda: close_children(curItem),
                              accelerator="Alt+Up")
            if opened:
                popup.entryconfig("Collapse folders", state='normal')
            else:
                popup.entryconfig("Collapse folders", state='disable')
        popup.tk_popup(event.x_root, event.y_root)
    except IndexError:
        pass
    finally:
        popup.grab_release()


def del_folder(iid):
    global proj_name
    clear_search()
    tv.delete(iid)
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    if len(tv.get_children()) == 0:
        odsmenu.entryconfig("Unload all files", state='disable')
        file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')
        search_entry.delete(0, 'end')
        search_entry.configure(state="disabled")
        btn.configure(state="disabled")
        if len(tv_frame.tabs()) == 1:
            projmenu.entryconfig("Save", state='disable')
            root.unbind('<Alt-s>')
            projmenu.entryconfig("SaveAs", state='disable')
            projmenu.entryconfig("Unload", state='disable')
            proj_name = None


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
        if '.!notebook2.!frame.' in str(item):
            item.destroy()

    user_logs.clear()
    odlmenu.entryconfig("Unload all ODL logs", state='disable')
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
        root.unbind('<Alt-s>')
        projmenu.entryconfig("SaveAs", state='disable')
        projmenu.entryconfig("Unload", state='disable')
        proj_name = None


def new_selection(event):
    global cur_sel
    curItem = event.widget.selection()

    if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame.!treeview':
        file_pane()
    selectItem(event)

    try:
        if cur_sel == f'{event.widget}{curItem[0]}':
            return
    except Exception:
        return
    else:
        cur_sel = f'{event.widget}{curItem[0]}'

        t1 = threading.Thread(target=get_info,
                              args=(event,),
                              daemon=True)

        if 'get_info' not in str(threading.enumerate()):
            stop.clear()
            t1.start()
        else:
            stop.set()


def selectItem(event):
    curItem = event.widget.selection()
    values = event.widget.item(curItem, 'values')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    try:
        if values[6] == 'Root Drive':
            line = f'Name: {values[5]}\nType: {values[6]}'
        elif values[6] == 'Root Shared' or values[6] == 'Root Default':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[13]}\nDriveItemId: {values[3]}'
        elif values[6] == 'Folder':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[13]}\nParentId: {values[2]}\nDriveItemId: {values[3]}\neTag: {values[4]}'
        elif values[6] == 'Root Deleted':
            line = f'Name: {values[5]}\nType: {values[6]}'
        elif values[6] == 'File - deleted':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[10]}\nSize: {values[7]}\nHash: {values[8]}\nDeleteTimeStamp: {values[11]} UTC'
        else:
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[13]}\nSize: {values[7]}\nHash: {values[8]}\nParentId: {values[2]}\nDriveItemId: {values[3]}\neTag: {values[4]}'
        if 'deleted' in values[6].lower():
            details.insert(tk.END, line, 'red')
        else:
            details.insert(tk.END, line)
        details.see(tk.END)
    except IndexError:
        pass

    details.config(state='disable')


def file_pane():
    curItem = tv.selection()

    for item in tv2.get_children():
        tv2.delete(item)

    for item in tv3.get_children():
        tv3.delete(item)

    for child in tv.get_children(curItem):
        if tv.item(child)["tags"]:
            tv2.insert("", "end", image=tv.item(child)["image"],
                       text=f' {tv.item(child)["text"]}', values=tv.item(child)["values"], tags=tv.item(child)["tags"][0])
        else:
            tv2.insert("", "end", image=tv.item(child)["image"],
                       text=f' {tv.item(child)["text"]}', values=tv.item(child)["values"])

        if 'deleted' in tv.item(child, 'values')[6].lower():
            tv3.insert("", "end", values=tv.item(child)["values"])

        elif tv.item(child, 'values')[9] == '5':
            tv3.insert("", "end", image=excluded_img, values=tv.item(child)["values"])

        else:
            tv3.insert("", "end", image=online_img, text=tv.item(child, 'values')[9], values=tv.item(child)["values"])
    try:
        if curItem[0] in file_items:
            for i in file_items[curItem[0]]:
                tv2.insert("", "end", image=tv.item(i)["image"],
                           text=f' {tv.item(i)["text"]}', values=tv.item(i)["values"])

                if tv.item(i, 'values')[9] == '2':
                    if tv.item(i, "values")[11] == '1':
                        tv3.insert("", "end", image=available_shared_img,
                                   values=tv.item(i)["values"])
                    else:
                        tv3.insert("", "end", image=available_img,
                                   values=tv.item(i)["values"])
                elif tv.item(i, 'values')[9] == '5':
                    if tv.item(i, "values")[11] == '1':
                        tv3.insert("", "end", image=excluded_shared_img,
                                   values=tv.item(i)["values"])
                    else:
                        tv3.insert("", "end", image=excluded_img,
                                   values=tv.item(i)["values"])
                elif tv.item(i, 'values')[9] == '8':
                    if tv.item(i, "values")[11] == '1':
                        tv3.insert("", "end", image=online_shared_img,
                                   values=tv.item(i)["values"])
                    else:
                        tv3.insert("", "end", image=online_img,
                                   values=tv.item(i)["values"])
                else:
                    if tv.item(i, "values")[11] == '1':
                        tv3.insert("", "end", image=onedrive_shared_img, text=tv.item(i, 'values')[9],
                                   values=tv.item(i)["values"])
                    else:

                        tv3.insert("", "end", text=tv.item(i, 'values')[9],
                                   values=tv.item(i)["values"])
    except Exception:
        pass

    root.update_idletasks()


def get_info(event):
    df_list = []
    curItem = event.widget.selection()
    values = event.widget.item(curItem, 'values')
    for item in root.winfo_children():
        for i in item.winfo_children():
            if '!mytable' in str(i):
                df_list.append(i.model.df)

    if len(df_list) == 0:
        return

    for item in infoFrame.winfo_children():
        if '.!notebook2.!frame.' in str(item):
            item.destroy()

    root.update_idletasks()

    if f'{values[6]}' != 'File - deleted' and len(values[3]) == 0:
        return

    infoNB.tab(infoFrame, text="Loading... ")
    root.update_idletasks()

    info = []

    # find logs for deleted files
    if f'{values[6]}' == 'File - deleted' and len(values[8]) != 0:
        file_hash = values[8].split("(")

        if file_hash[0] == 'SHA1':
            info = pd.concat([df.loc[df.Params.astype('string').str.contains(f'{values[8].split("(")[1].strip(")")}', case=False, na=False)] for df in df_list])
        if file_hash[0] == 'quickXor':
            data = ''.join(['{:02x}'.format(i) for i in base64.b64decode(file_hash[1].strip(")"))])
            info = pd.concat([df.loc[df.Params.astype('string').str.contains(data, case=False, na=False)] for df in df_list])

    # find logs for files
    if f'{values[6]}' != 'File - deleted' and len(values[3]) != 0:
        info = pd.concat([df.loc[df.Params.astype('string').str.contains(f'{values[3].split("+")[0]}', case=False, na=False)] for df in df_list])

    if len(info) == 0 or stop.is_set():
        infoNB.tab(infoFrame, text="Log Entries")
        if event.widget.selection()[0] != curItem[0]:
            stop.clear()
            threading.Thread(target=get_info,
                             args=(event,),
                             daemon=True).start()
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
            if '.!notebook2.!frame.' in str(item):
                item.destroy()
        if tv.selection()[0] != curItem[0]:
            stop.clear()
            threading.Thread(target=get_info,
                             args=(event,),
                             daemon=True).start()
    infoNB.tab(infoFrame, text="Log Entries")


def open_children(parent):
    tv.item(parent, open=True)  # open parent
    for child in tv.get_children(parent):
        open_children(child)    # recursively open children


def close_children(parent):
    tv.item(parent, open=False)  # close parent
    for child in tv.get_children(parent):
        close_children(child)    # recursively close children


def copy_details():
    root.clipboard_clear()
    root.clipboard_append(details.get("1.0", tk.END))


def copy_path(values):
    line = f'{values[5]}: {values[13]}\\{values[5]}'
    root.clipboard_clear()
    root.clipboard_append(line)


def copy_name(values):
    root.clipboard_clear()
    root.clipboard_append(values[5])


def rebind():
    global bind_id
    bind_id = message.bind('<Double-Button-1>',
                           lambda event=None: messages(root))


def log_tab():
    if tv_frame.index("current") != 0:
        pwv.remove(infoNB)
    else:
        pwv.add(infoNB, minsize=100)


def load_proj():
    global proj_name
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDriveExplorer project file",
                                                      "*.ode_proj"),
                                                     ))

    if filename:
        proj_name = filename
        q = Queue()
        stop_event = threading.Event()
        threading.Thread(target=load_project,
                         args=(filename, q, stop_event,),
                         daemon=True,).start()
        threading.Thread(target=proj_parse,
                         args=(q, proj_name,),
                         daemon=True,).start()

        projmenu.entryconfig("Unload", state='normal')


def proj_parse(q, proj_name):
    while True:
        data = q.get()

        if '_OneDrive.csv' in data[0]:
            x = 'Project'
            start_parsing(x, filename=data[0], df=data[1])
            q.task_done()

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
            tv_frame.add(tb, text=f'{key} Logs')
            pt.adjustColumnWidths()
            pt.show()
            user_logs.setdefault(f'{key}_logs.csv', pt)
            q.task_done()
            pb.stop()

        if data[0] == 'wait':
            try:
                message.unbind('<Double-Button-1>', bind_id)
            except Exception:
                pass
            details.config(state='normal')
            details.delete('1.0', tk.END)
            details.config(state='disable')
            menubar.entryconfig("File", state="disabled")
            menubar.entryconfig("Options", state="disabled")
            menubar.entryconfig("View", state="disabled")
            menubar.entryconfig("Help", state="disabled")
            search_entry.configure(state="disabled")
            btn.configure(state="disabled")
            pb.configure(mode='indeterminate')
            value_label['text'] = f'Loading {data[1]}. Please wait....'
            pb.start()
            q.task_done()

        if data[0] == 'done':
            break

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    menubar.entryconfig("View", state="normal")
    menubar.entryconfig("Help", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")
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


def save_proj():
    global proj_name
    saveAs_proj(filename=proj_name)


def saveAs_proj(filename=None):
    global proj_name
    if filename is None:
        filename = filedialog.asksaveasfilename(defaultextension=".ode_proj")

    if filename:
        proj_name = filename
        threading.Thread(target=save_project,
                         args=(tv, file_items, filename, user_logs, pb, value_label,),
                         daemon=True).start()

        projmenu.entryconfig("Unload", state='normal')


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
    menu_data['font'] = default_font
    save_settings()


def click(event):
    if len(search_entry.get()) > 0:
        search_entry.state(['!invalid'])
    else:
        search_entry.state(['invalid'])
        clear_search()


def handle_click(event):
    if tv2.identify_region(event.x, event.y) == "separator":
        return "break"


def multiple_yview(*args):
    tv2.yview(*args)
    tv3.yview(*args)


def multiple_yview_scroll(event):
    if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame2.!treeview':
        tv2.yview_scroll(-1 * int(event.delta / 120), "units")
    if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!treeview':
        tv3.yview_scroll(-1 * int(event.delta / 120), "units")


def multiple_select(event):
    try:
        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!treeview':
            curItem = tv2.selection()
            curItem2 = tv3.selection()
            if not curItem2:
                curItem2 = ('0',)
            if curItem[0] != curItem2[0]:
                tv3.selection_set(curItem[0])

        if str(event.widget) == '.!frame.!frame.!myscrollablenotebook.!frame2.!panedwindow.!frame2.!treeview':
            curItem = tv3.selection()
            curItem2 = tv2.selection()
            if not curItem2:
                curItem2 = ('0',)
            if curItem[0] != curItem2[0]:
                tv2.selection_set(curItem[0])
            new_selection(event)

    except Exception:
        pass


def sync():
#    global cstruct_df
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
    if thread.is_alive():
        # not ready yet, run the check again soon
        root.after(200, check_if_ready, thread, t_string)
    else:
        if t_string == "ts":
            search_result()
        if t_string == "s":
            cstruct_df = load_cparser(args.cstructs)


def thread_search():
    clear_search()
    t1 = threading.Thread(target=search, daemon=True)
    t1.start()
    root.after(200, check_if_ready, t1, "ts")


root = ThemedTk()
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap(application_path + '/Images/OneDrive.ico')
root.geometry('1440x880')
root.minsize(40, 40)
root.protocol("WM_DELETE_WINDOW", lambda: quit(root))

default_font = str(menu_data['font'])
pandastablepatch.root = root
pandastablepatch.default_font = default_font
pandastablepatch.application_path = application_path

root.tk.call('tk', 'fontchooser', 'configure', '-font', default_font,
             '-command', root.register(font_changed))

style = ttk.Style()
style.configure('Result.Treeview', rowheight=40)
style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))

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

root_drive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hdd.png'))
default_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_open_hdd.png'))
shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_save_hdd.png'))
folder_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/directory_closed.png'))
folderop_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/directory_open.png'))
file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow.png'))
file_del_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_delete.png'))
del_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_trashcan.png'))
load_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/repeat_green.png'))
live_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/computer_desktop.png'))
sql_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/IDI_DB4S-1.png'))
json_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded.png'))
csv_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table.png'))
uaf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/delete_red.png'))
search_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/magnifier.png'))
exit_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/no.png'))
font_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/format_normal.png'))
skin_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/skin.png'))
sync_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/arrow_plain_green_S.png'))
pref_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/controls.png'))
question_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/question.png'))
trash_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/trashcan.png'))
info_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/info.png'))
error_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/error.png'))
merror_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/error_small.png'))
minfo_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/info_small.png'))
warning_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/warning.png'))
ods_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/cloud_cyan.png'))
saveas_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/floppy_35inch_black.png'))
save_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/floppy_35inch_green.png'))
ual_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table_delete.png'))
loadl_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table_new.png'))
proj_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/tables.png'))
png_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/PNG-16.png'))
pdf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/PDF-16.png'))
message_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/language_blue.png'))
cstruct_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table_column.png'))
question_small_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/question_small.png'))
ode_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/ode.png'))
ode_small_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/ode_small.png'))
online_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online-8.png'))
online_directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online_directory.png'))
online_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online_file.png'))
online_shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online-shared.png'))
online_shared_directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online_shared_directory.png'))
online_shared_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/online_shared_file.png'))
available_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/available-8.png'))
available_shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/available-shared.png'))
available_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/available_file.png'))
available_shared_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/available_shared_file.png'))
file_del_big_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_delete_big.png'))
file_big_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_big.png'))
asc_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table_sort_asc.png'))
desc_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table_sort_desc.png'))
onedrive_shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/shared-8.png'))
shared_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/shared_file.png'))
excluded_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/excluded-10.png'))
excluded_shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/excluded_shared.png'))
excluded_directory_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/excluded_directory.png'))
excluded_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/excluded_file.png'))
excluded_shared_file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/excluded_shared_file.png'))

pandastablepatch.asc_img = asc_img
pandastablepatch.desc_img = desc_img

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

menubar = tk.Menu(root)
root.config(menu=menubar)

outer_frame = ttk.Frame(root)
main_frame = ttk.Frame(outer_frame, relief='groove', padding=5)

bottom_frame = ttk.Frame(main_frame)

outer_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
bottom_frame.grid(row=1, column=0, pady=(5, 0), stick='nsew')

outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_rowconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(0, weight=1)

pwv = tk.PanedWindow(main_frame, orient=tk.VERTICAL,
                     background=bg, sashwidth=6)

columns = ('Date_modified', 'Size')

tv_frame = ScrollableNotebookpatch.MyScrollableNotebook(main_frame,
                                                        wheelscroll=True,
                                                        style='CustomNotebook')

tv_frame.enable_traversal()
tv_inner_frame = ttk.Frame(tv_frame)
tv_frame.add(tv_inner_frame, text='OneDrive Folders  ')

pwh = tk.PanedWindow(tv_inner_frame, orient=tk.HORIZONTAL,
                     background=bgf, sashwidth=2)

tv_pane_frame = ttk.Frame(pwh)

tv_lable = ttk.Label(tv_pane_frame, text="Path",
                     justify="left", anchor='w')
tv = ttk.Treeview(tv_pane_frame,
                  show="tree",
                  selectmode='browse',
                  takefocus='false')
tv.heading('#0', text=' Path', anchor='w')
tv.column('#0', minwidth=40, width=250, stretch=True, anchor='w')


find_frame = ttk.Frame(tv_inner_frame)

find_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(find_frame, width=30,
                         exportselection=0, style='CustomEntry')
btn = ttk.Button(find_frame,
                 text="Find",
                 image=search_img,
                 takefocus=False,
                 compound='right',
                 command=lambda: [thread_search(), sync_message(root)])
search_entry.configure(state="disabled")
btn.configure(state="disabled")

scrollbv = ttk.Scrollbar(tv_pane_frame, orient="vertical", command=tv.yview)
scrollbh = ttk.Scrollbar(tv_pane_frame, orient="horizontal", command=tv.xview)

tv2 = ttk.Treeview(pwh,
                   selectmode='browse',
                   takefocus='false')
tv2.heading('#0', text=' Name', anchor='w')
tv2.column('#0', minwidth=80, width=340, stretch=True, anchor='w')

tab2 = ttk.Frame(pwh)
tv3 = ttk.Treeview(tab2,
                   columns=columns,
                   selectmode='browse',
                   takefocus='false')
tv3.heading('#0', text=' Status', anchor='w')
tv3.heading('Date_modified', text=' Date_modified', anchor='w')
tv3.heading('Size', text=' Size', anchor='w')
tv3.column('#0', minwidth=80, width=100, stretch=False, anchor='w')
tv3.column('Date_modified', minwidth=80, width=180, stretch=False, anchor='w')
tv3.column('Size', minwidth=70, width=80, stretch=False, anchor='e')

fscrollbv = ttk.Scrollbar(tab2, orient="vertical", command=multiple_yview)
tv2.configure(yscrollcommand=fscrollbv.set)
tv3.configure(yscrollcommand=fscrollbv.set)

value_label = ttk.Label(bottom_frame, text='')
pb = ttk.Progressbar(bottom_frame, orient='horizontal',
                     length=160, mode='determinate')
sl = ttk.Separator(bottom_frame, orient='vertical')
message = ttk.Label(bottom_frame, text=0, background='red',
                    anchor='center', width=3)
sr = ttk.Separator(bottom_frame, orient='vertical')
sg = ttk.Sizegrip(bottom_frame)

details = tk.Text(pwh, font=default_font, background=bgf, foreground=fgf, relief='flat', undo=False, width=50, state='disable')
details.tag_configure('red', foreground="red")
tv.configure(yscrollcommand=scrollbv.set, xscrollcommand=scrollbh.set)
tv.tag_configure('yellow', background="yellow", foreground="black")
tv.tag_configure('red', foreground="red")
tv2.tag_configure('red', foreground="red")

tv_pane_frame.grid_rowconfigure(1, weight=1)
tv_pane_frame.grid_columnconfigure(0, weight=1)
tab2.grid_rowconfigure(0, weight=1)
tab2.grid_columnconfigure(0, weight=1)

tv_inner_frame.grid_rowconfigure(1, weight=1)
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
pwh.add(tv_pane_frame, minsize=40, width=250)
pwh.add(tv2, minsize=80, width=340)
pwh.add(tab2, minsize=247)
pwh.add(details, minsize=20)

infoNB = ttk.Notebook()
infoFrame = ttk.Frame(infoNB)
infoNB.add(infoFrame, text='Log Entries')

pwv.add(tv_frame, minsize=100)
pwv.add(infoNB, minsize=100)

search_entry.grid(row=0, column=0, sticky="e", padx=5)
btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")

pwv.grid(row=0, column=0, sticky="nsew")
pwh.grid(row=1, column=0, sticky="nsew")
find_frame.grid(row=0, column=0, sticky='ew')
tv_lable.grid(row=0, column=0, sticky="nw")
tv.grid(row=1, column=0, sticky="nsew")
scrollbv.grid(row=0, column=1, rowspan=2, sticky="nsew")
scrollbh.grid(row=2, column=0, sticky="nsew")
tv3.grid(row=0, column=0, sticky="nsew")
fscrollbv.grid(row=0, column=1, sticky="nsew")
rscrollbv.grid(row=0, column=1, sticky="nsew")

value_label.grid(row=0, column=0, sticky='se')
pb.grid(row=0, column=1, padx=5, sticky='se')
sl.grid(row=0, column=2, padx=(0, 1), sticky='ns')
message.grid(row=0, column=3, sticky='nse')
sr.grid(row=0, column=4, padx=(1, 2), sticky='nse')
sg.grid(row=0, column=5, sticky='se')


tv.bind('<<TreeviewSelect>>', new_selection)
tv.bind('<Button-1>', lambda event=None: clear_search())
tv2.bind('<<TreeviewSelect>>', multiple_select)
tv3.bind('<<TreeviewSelect>>', multiple_select)
tv.bind("<Button-3>", do_popup)
tv2.bind("<Button-3>", do_popup)
tv3.bind("<Button-3>", do_popup)
tvr.bind('<<TreeviewSelect>>', new_selection)
tv.bind('<Alt-Down>', lambda event=None: open_children(tv.selection()))
tv.bind('<Alt-Up>', lambda event=None: close_children(tv.selection()))
tv2.bind('<Button-1>', handle_click)
tv2.bind('<Motion>', handle_click)
tv2.bind('<MouseWheel>', multiple_yview_scroll)
tv3.bind('<MouseWheel>', multiple_yview_scroll)
root.bind('<Control-o>', lambda event=None: open_dat(file_menu))
root.bind('<Control-m>', lambda event=None: messages(root))
root.bind('<Alt-KeyPress-0>', lambda event=None: clear_all())
root.bind('<Alt-KeyPress-2>', lambda event=None: load_proj())
root.bind('<Alt-s>', lambda event=None: save_proj())
root.bind('<<NotebookTabChanged>>', lambda event=None: log_tab())
search_entry.bind('<Return>',
                  lambda event=None: [thread_search(), sync_message(root)])
search_entry.bind('<KeyRelease>', click)
bind_id = message.bind('<Double-Button-1>', lambda event=None: messages(root))
infoNB.bind('<Motion>', motion)
search_entry.bind('<Motion>', motion)
root.nametowidget('.!frame.!frame.!myscrollablenotebook.!notebook2').bind('<Motion>', motion)

keyboard.is_pressed('shift')

file_menu = tk.Menu(menubar, tearoff=0)
odsmenu = tk.Menu(file_menu, tearoff=0)
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

odsmenu.add_command(label="Load <UserCid>.dat" + (' '*10),
                    image=load_img, compound='left',
                    command=lambda: open_dat(odsmenu),
                    accelerator="Ctrl+O")
odsmenu.add_command(label="Load from SQLite",
                    image=sql_img, compound='left',
                    command=lambda: read_sql(odsmenu))
odsmenu.add_command(label="Import JSON", image=json_img,
                    compound='left', command=lambda: import_json(odsmenu))
odsmenu.add_command(label="Import CSV", image=csv_img, compound='left',
                    command=lambda: import_csv(odsmenu))
odsmenu.add_command(label="Unload all files", image=uaf_img, compound='left',
                    command=lambda: clear_all(), accelerator="Alt+0")
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
                     command=lambda: [clear_all(), del_logs()])
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
                      command=lambda: threading.Thread(target=live_system,
                                                       args=(file_menu,),
                                                       daemon=True).start())

file_menu.add_cascade(label="OneDrive settings", menu=odsmenu,
                      image=ods_img, compound='left')

file_menu.add_cascade(label="OneDrive logs", menu=odlmenu,
                      image=folder_img, compound='left')
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
                      command=lambda: quit(root))

file_menu.entryconfig("Export 'OneDrive Folders'", state='disable')

options_menu.add_command(label="Font", image=font_img, compound='left',
                         command=lambda: root.tk.call('tk', 'fontchooser', 'show'))
options_menu.add_cascade(label="Skins", image=skin_img,
                         compound='left', menu=submenu)
options_menu.add_separator()
options_menu.add_command(label="Sync with Github", image=sync_img,
                         compound='left', command=lambda: [sync(), sync_message(root)])
options_menu.add_separator()
options_menu.add_command(label="Preferences", image=pref_img,
                         compound='left', command=lambda: preferences(root))

view_menu.add_command(label="Messages", image=message_img, accelerator="Ctrl+M",
                      compound='left', command=lambda: messages(root))
view_menu.add_separator()
view_menu.add_command(label="CStructs", image=cstruct_img,
                      compound='left', command=lambda: cstructs(root, cstruct_df))

help_menu.add_command(label="Quick help", image=question_small_img,
                      compound='left', command=lambda: help(root))
help_menu.add_command(label="About", image=ode_small_img,
                      compound='left', command=lambda: about(root))

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

CreateToolTip(message, text='Total messages\n'
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
