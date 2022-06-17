import os
import sys
import re
import json
import ctypes
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog
import threading
from queue import Queue
import pandas as pd
from pandastable import Table
from PIL import ImageTk, Image
import time
import keyboard
import logging
from io import StringIO as StringBuffer
from datetime import datetime
import warnings
from ode.renderers.json import print_json_gui
from ode.renderers.csv_file import print_csv
from ode.renderers.html import print_html
from ode.renderers.project import save_project
from ode.renderers.project import load_project
from ode.parsers.dat_new import parse_dat
from ode.parsers.csv_file import parse_csv
from ode.parsers.onedrive import parse_onedrive
from ode.parsers.odl import parse_odl
from ode.helpers.mft import live_hive
import ode.helpers.ScrollableNotebook as ScrollableNotebook
warnings.filterwarnings("ignore", category=UserWarning)

ctypes.windll.shcore.SetProcessDpiAwareness(2)

log_capture_string = StringBuffer()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s, %(levelname)s, %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(log_capture_string)]
                    )

__author__ = "Brian Maloney"
__version__ = "2022.06.17"
__email__ = "bmmaloney97@gmail.com"
rbin = []
found = []
detached_items = []
user_logs = {}
reghive = ''
recbin = ''
proj_name = None

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
        jsonfile.close()
else:
    menu_data = json.loads('{"theme": "vista",\
                             "json": false,\
                             "pretty": false,\
                             "csv": false,\
                             "html": false,\
                             "path": ".",\
                             "hive": false,\
                             "odl": false,\
                             "odl_save": false}'
                           )

    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


class quit:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
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
        self.win.protocol("WM_DELETE_WINDOW", self.close_pref)

        s = ttk.Style()
        s.map('Red.TCheckbutton',
              foreground=[("!disabled", "red"), ("disabled", "pink")])

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

        self.exp_label = ttk.Label(self.inner_frame,
                                   text='Experimental',
                                   foreground='red'
                                   )

        self.select_frame = ttk.Frame(self.inner_frame)
        self.path_frame = ttk.Frame(self.inner_frame)
        self.hive_frame = ttk.Frame(self.inner_frame)
        self.exp_frame = ttk.LabelFrame(self.inner_frame,
                                        labelwidget=self.exp_label)
        self.exit_frame = ttk.Frame(self.inner_frame)

        self.exit_frame.grid_rowconfigure(0, weight=1)
        self.exit_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0, sticky="nsew")
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.select_frame.grid(row=0, column=0, sticky="nsew")
        self.path_frame.grid(row=1, column=0, pady=25, sticky="nsew")
        self.hive_frame.grid(row=2, column=0, pady=(0, 25), sticky="nsew")
        self.exp_frame.grid(row=3, column=0, pady=(0, 25), sticky="nsew")
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

        self.exp = ttk.Checkbutton(self.exp_frame,
                                   text="Enable ODL log parsing",
                                   var=self.odl,
                                   offvalue=False,
                                   onvalue=True,
                                   takefocus=False,
                                   command=self.odl_config,
                                   style='Red.TCheckbutton'
                                   )

        self.exp_save = ttk.Checkbutton(self.exp_frame,
                                        text="Auto Save ODL",
                                        var=self.odl_save,
                                        offvalue=False,
                                        onvalue=True,
                                        takefocus=False,
                                        style='Red.TCheckbutton'
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
        self.exp.grid(row=0, column=0, padx=5, sticky="w")
        self.exp_save.grid(row=1, column=0, padx=5, sticky="w")
        self.save.grid(row=0, column=0, pady=5, sticky="e")
        self.cancel.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        if self.json_save.get() is False:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

        if self.odl.get() is False:
            self.exp_save.configure(state="disabled")
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
        except:
            pass

    def pretty_config(self):
        if self.json_save.get() is True:
            self.pretty.configure(state="normal")
        else:
            self.pretty.configure(state="disabled")
            self.json_pretty.set(False)

    def odl_config(self):
        if self.odl.get() is True:
            self.exp_save.configure(state="normal")
        else:
            self.exp_save.configure(state="disabled")
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

    def close_pref(self):
        self.win.destroy()


class hive:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("Load User Hive")
        self.win.iconbitmap(application_path + '/Images/OneDrive.ico')
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
            root.wait_window(rec_bin(root).win)

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        try:
            self.win.geometry("+%d+%d" % (x + w/4, y + h/3))
        except:
            pass


class rec_bin:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
        self.win.title("$Recycle.Bin")
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
        except:
            pass


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
        self.clear = ttk.Button(self.inner_frame, text='Clear messages',
                                takefocus=False, command=self.clear)
        self.export = ttk.Button(self.inner_frame, text='Export messages',
                                 takefocus=False, command=self.export)
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
            self.tree.insert("", "end", values=m, image=image)

        self.tree.grid(row=0, column=0, columnspan=3, padx=(10, 0),
                       pady=(10, 0), sticky='nsew')
        self.tree_scroll.grid(row=0, column=3, padx=(0, 10),
                              pady=(10, 0), sticky="nsew")
        self.tb.grid(row=1, column=0, columnspan=3, padx=(10, 0),
                     pady=(5, 10), sticky='nsew')
        self.tb_scroll.grid(row=1, column=3, padx=(0, 10),
                            pady=(5, 10), sticky="nsew")
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
        self.excel_name = excel_name.replace('/', '\\')
        self.failed = failed
        self.win = tk.Toplevel(self.root)
        self.win.wm_transient(self.root)
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
        except:
            pass


def ButtonNotebook():

    style.element_create("close", "image", "img_close",
                         ("active", "pressed", "!disabled", "img_closepressed"),
                         ("active", "!disabled", "img_closeactive"),
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
                        ("CustomNotebook.focus", {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [
                                ("CustomNotebook.label",
                                 {"side": "left", "sticky": ''}),
                                ("CustomNotebook.close",
                                 {"side": "left", "sticky": ''}),
                            ]
                        })
                    ]
                })
            ]
        })
    ])

    def on_close_press(event):
        """Called when the button is pressed over the close button"""

        if event.widget.winfo_class() != 'TNotebook':
            return
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify(x, y)
        try:
            index = widget.index("@%d,%d" % (x, y))
            if index == 0:
                return
        except:
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
                    if str(item) == '.!frame':
                        pass
                    else:
                        item.destroy()
            except:
                pass

        if "close" in elem and widget.pressed_index == index:
            try:
                del user_logs[f'{widget.tab(index, "text").replace(" L", "_l")}.csv']
            except:
                pass

            widget.winfo_children()[index].destroy()
            widget.event_generate("<<NotebookClosedTab>>")
            if len(tv_frame.tabs()) == 1:
                odlmenu.entryconfig("Unload all ODL logs", state='disable')
                if len(tv.get_children()) == 0:
                    projmenu.entryconfig("Save", state='disable')
                    projmenu.entryconfig("SaveAs", state='disable')
                    projmenu.entryconfig("Unload", state='disable')
                    proj_name = None

        widget.state(["!pressed"])
        widget.pressed_index = None

    root.bind("<ButtonPress-1>", on_close_press, True)
    root.bind("<ButtonRelease-1>", on_close_release)


def pane_config():
    bg = style.lookup('TFrame', 'background')
    pw.config(background=bg, sashwidth=6)
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

    return [elm for elm in style.map("Treeview", query_opt=option)
            if elm[:2] != ("!disabled", "!selected")]


def search(item=''):
    query = search_entry.get()
    if len(query) == 0:
        found.append('0')
        return
    children = tv.get_children(item)
    for child in children:
        for x in tv.item(child)['values']:
            if query.lower() in str(x).lower():
                tv.see(child)
                tags = list(tv.item(child, 'tags'))
                tags.append('yellow')
                tv.item(child, tags=tags)
                found.append(child)
        search(item=child)


def search_result():
    if len(found) == 0:
        d = tv.get_children()
        for i in d:
            detached_items.append(i)
            tv.detach(i)


def clear_search():
    for i in detached_items:
        tv.reattach(i, '', "end")
        close_children(i)
    detached_items.clear()

    for hit in found:
        try:
            tags = list(tv.item(hit, 'tags'))
            tags = [x for x in tags if x == 'red']
            tv.item(hit, tags=tags)
        except:
            pass
    found.clear()
    if len(tv.selection()) > 0:
        tv.selection_remove(tv.selection()[0])


def clear_all():
    global proj_name
    tv.delete(*tv.get_children())
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    odsmenu.entryconfig("Unload all files", state='disable')
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
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


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("",
                              "end",
                              image=root_drive_img,
                              text=d['Name'],
                              values=('',
                                      '',
                                      d['ParentId'],
                                      d['DriveItemId'],
                                      d['eTag'],
                                      d['Name'],
                                      d['Type'],
                                      d['Size'],
                                      d['Hash'],
                                      len(d['Children']),
                                      d['Path']))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        if c['Type'] == 'Folder':
            folder_count, file_count = ff_count(c['Children'])
            parent_child(c, tv.insert(parent_id,
                                      0,
                                      image=folder_img,
                                      text=c['Name'],
                                      values=(folder_count,
                                              file_count,
                                              c['ParentId'],
                                              c['DriveItemId'],
                                              c['eTag'],
                                              c['Name'],
                                              c['Type'],
                                              c['Size'],
                                              c['Hash'],
                                              len(c['Children']),
                                              c['Path'])))
        elif c['Type'] == 'Root Default':
            parent_child(c, tv.insert(parent_id,
                                      0,
                                      image=default_img,
                                      text=c['Name'],
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
                                              c['Path'])))
        elif c['Type'] == 'Root Shared':
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=shared_img,
                                      text=c['Name'],
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
                                              c['Path'])))
        elif c['Type'] == 'Root Deleted':
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=del_img,
                                      text=c['Name'],
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
                                      image=file_img,
                                      text=c['Name'],
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
            parent_child(c, tv.insert(parent_id,
                                      "end",
                                      image=file_img,
                                      text=c['Name'],
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
                                              c['Path'])))
        root.update_idletasks()


def selectItem(a):
    curItem = tv.selection()
    values = tv.item(curItem, 'values')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    try:
        if values[6] == 'Root Drive':
            line = f'Name: {values[5]}\nType: {values[6]}'
        elif values[6] == 'Root Shared' or values[6] == 'Root Default':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[10]}\nDriveItemId: {values[3]}'
        elif values[6] == 'Folder':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[10]}\nParentId: {values[2]}\nDriveItemId: {values[3]}\neTag:{values[4]}'
        elif values[6] == 'Root Deleted':
            line = f'Name: {values[5]}\nType: {values[6]}'
        elif values[6] == 'File - deleted':
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[10]}\nSize: {values[7]}\nHash: {values[8]}\nDeleteTimeStamp: {values[11]} UTC'
        else:
            line = f'Name: {values[5]}\nType: {values[6]}\nPath: {values[10]}\nSize: {values[7]}\nHash: {values[8]}\nParentId: {values[2]}\nDriveItemId: {values[3]}\neTag:{values[4]}'
        if values[6] == 'Folder' or 'Root' in values[6]:
            line += f'\n\n# Children: {values[9]}'
        if 'deleted' in values[6].lower():
            details.insert(tk.END, line, 'red')
        else:
            details.insert(tk.END, line)
        details.see(tk.END)
    except IndexError:
        pass

    details.config(state='disable')


def live_system(menu):
    global reghive
    global recbin
    message.unbind('<Double-Button-1>', bind_id)
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    d = {}
    dat = re.compile(r'/Users\\(?P<user>.*)?\\AppData\\Local\\Microsoft\\OneDrive\\settings')
    log_dir = re.compile(r'/Users\\(?P<user>.*)?\\AppData\\Local\\Microsoft\\OneDrive\\logs$')
    rootDir = r'/'
    pb.configure(mode='indeterminate')
    value_label['text'] = "Searching for OneDrive. Please wait..."
    pb.start()
    for path, subdirs, files in os.walk(rootDir):
        dat_find = re.findall(dat, path)
        log_find = re.findall(log_dir, path)
        if path == '/$Recycle.Bin':
            recbin = path
        if dat_find:
            for name in files:
                if '.dat' in name:
                    d.setdefault(dat_find[0], {})
                    d[dat_find[0]].setdefault('files', []).append(os.path.join(path, name))
        if log_find:
            d.setdefault(log_find[0], {})
            d[log_find[0]].setdefault('logs', []).append(path)

    for key, value in d.items():
        filenames = []
        for k, v in value.items():
            if k == 'files':
                filenames = v

            if len(filenames) != 0:
                logging.info(f'Parsing OneDrive data for {key}')
                menubar.entryconfig("File", state="disabled")
                menubar.entryconfig("Options", state="disabled")
                search_entry.configure(state="disabled")
                btn.configure(state="disabled")
                value_label['text'] = f"Searching for {key}'s NTUSER.DAT. Please wait...."
                pb.configure(mode='indeterminate')
                pb.start()
                reghive = live_hive(key)
                pb.configure(mode='determinate')

                for filename in filenames:
                    x = menu.entrycget(0, "label")
                    start_parsing(x, filename, reghive, recbin)

    if menu_data['odl'] is True:
        for key, value in d.items():
            for k, v in value.items():
                if k == 'logs':
                    logs = v
                    pb.stop()
                    odl = parse_odl(logs[0], key, pb, value_label, gui=True)
                    tb = ttk.Frame()
                    pt = Table(tb, dataframe=odl, showtoolbar=False, showstatusbar=False)
                    tv_frame.add(tb, text=f'{key} Logs')
                    pt.show()
                    user_logs.setdefault(f'{key}_logs.csv', pt)
                    if menu_data['odl_save'] is True:
                        log_output = f'{key}_logs.csv'
                        odl.to_csv(log_output, index=False)

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
    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
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


def import_json(menu):
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import JSON",
                                      filetypes=(("OneDrive dat file",
                                                  "*.json"),))

    if filename:
        x = menu.entrycget(1, "label")
        threading.Thread(target=start_parsing,
                         args=(x, filename,),
                         daemon=True).start()


def import_csv(menu):
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import CSV",
                                      filetypes=(("OneDrive dat file",
                                                  "*.csv"),))

    if filename:
        x = menu.entrycget(2, "label")
        threading.Thread(target=start_parsing,
                         args=(x, filename,),
                         daemon=True).start()


def open_odl():
#    pass
    folder_name = filedialog.askdirectory(initialdir="/", title="Open")

    if folder_name:
        threading.Thread(target=odl,
                         args=(folder_name,),
                         daemon=True).start()


def odl(folder_name):
    message.unbind('<Double-Button-1>', bind_id)
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    key_find = re.compile(r'Users/(?P<user>.*)?/AppData')
    key = re.findall(key_find, folder_name)
    if len(key) == 0:
        key = 'ODL'
    else:
        key = key[0]
    pb.stop()
    odl = parse_odl(folder_name, key, pb, value_label, gui=True)
    tb = ttk.Frame()
    pt = Table(tb, dataframe=odl, showtoolbar=False, showstatusbar=False)
    tv_frame.add(tb, text=f'{key} Logs')
    pt.show()
    user_logs.setdefault(f'{key}_logs.csv', pt)
    pb.stop()
    value_label['text'] = "Parsing complete"

    if menu_data['odl_save'] is True:
        log_output = f'{key}_logs.csv'
        try:
            odl.to_csv(log_output, index=False)
        except Exception as e:
            logging.error(e)

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

    if len(tv_frame.tabs()) > 1:
        odlmenu.entryconfig("Unload all ODL logs", state='normal')
        projmenu.entryconfig("Save", state='normal')
        projmenu.entryconfig("SaveAs", state='normal')


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def start_parsing(x, filename=False, reghive=False, recbin=False, df=False):
    try:
        message.unbind('<Double-Button-1>', bind_id)
    except:
        pass
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")

    start = time.time()
    dat = False

    if x == 'Live system':
        df, name, personal = parse_dat(filename, reghive, recbin, start,
                                       gui=True, pb=pb, value_label=value_label)
        df, rbin_df = parse_onedrive(df, reghive, recbin, personal)
        dat = True

    if x == 'Load <UserCid>.dat' + (' '*10):
        df, name, personal = parse_dat(filename, reghive, recbin, start,
                                       gui=True, pb=pb, value_label=value_label)
        df, rbin_df = parse_onedrive(df, reghive, recbin, personal)
        dat = True

    if x == 'Import JSON':
        cache = json.load(filename)
        df = pd.DataFrame()

    if x == 'Import CSV':
        df, name = parse_csv(filename)
        df, rbin_df = parse_onedrive(df)

    if x == 'Project':
        name = filename
        pass

    if not df.empty:
        try:
            file_count = df.Type.value_counts()['File']

        except KeyError:
            logging.warning("KeyError: 'File'")
            file_count = 0

        try:
            del_count = df.Type.value_counts()['File - deleted']

        except KeyError:
            logging.warning("KeyError: 'File - deleted'")
            del_count = 0

        try:
            folder_count = df.Type.value_counts()['Folder']

        except KeyError:
            logging.warning("KeyError: 'Folder'")
            folder_count = 0

        def subset(dict_, keys):
            return {k: dict_[k] for k in keys}

        cache = {}
        final = []
        is_del = []

        df.loc[df.Type == 'File', ['FileSort']] = df['Name'].str.lower()
        df.loc[df.Type == 'Folder', ['FolderSort']] = df['Name'].str.lower()

        for row in df.sort_values(by=['Level', 'ParentId', 'Type', 'FileSort', 'FolderSort'], ascending=[False, False, False, True, False]).to_dict('records'):
            if 'DeleteTimeStamp' in df.columns:
                file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'DeleteTimeStamp', 'Children'))
            else:
                file = subset(row, keys=('ParentId', 'DriveItemId', 'eTag', 'Type', 'Path', 'Name', 'Size', 'Hash', 'Children'))
            if row['Type'] == 'File':
                folder = cache.setdefault(row['ParentId'], {})
                folder.setdefault('Children', []).append(file)
            elif row['Type'] == 'File - deleted':
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
                logging.warning("KeyError: 'File - deleted'")
                del_count = 0

        cache = {'ParentId': '',
                 'DriveItemId': '',
                 'eTag': '',
                 'Type': 'Root Drive',
                 'Path': '',
                 'Name': name.replace('/', '\\'),
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

    if not df.empty or x == 'Import JSON':

        pb.configure(mode='indeterminate')
        value_label['text'] = "Building tree. Please wait..."
        pb.start()
        parent_child(cache)
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

    else:
        try:
            filename = filename.replace('/', '\\')
        except:
            pass
        logging.warning(f'Unable to parse {filename}.')
        value_label['text'] = f'Unable to parse {filename}.'

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")

    if len(tv.get_children()) > 0:
        odsmenu.entryconfig("Unload all files", state='normal')
        projmenu.entryconfig("Save", state='normal')
        projmenu.entryconfig("SaveAs", state='normal')
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
        curItem = tv.identify_row(event.y)
        tv.selection_set(curItem)
        opened = tv.item(curItem, 'open')
        values = tv.item(curItem, 'values')
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
                             command=lambda: copy_path(values, curItem))
        copymenu.add_command(label="Details",
                             image=details_img,
                             compound='left', command=lambda: copy_details())

        if values[6] == 'Root Drive':
            popup.entryconfig("Copy", state='disable')
        else:
            popup.entryconfig("Copy", state='normal')

        if values[6] == 'Folder' or 'Root' in values[6]:
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
    tv.delete(iid)
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    if len(tv.get_children()) == 0:
        odsmenu.entryconfig("Unload all files", state='disable')
        search_entry.configure(state="disabled")
        btn.configure(state="disabled")
        if len(tv_frame.tabs()) == 1:
            projmenu.entryconfig("Save", state='disable')
            projmenu.entryconfig("SaveAs", state='disable')
            projmenu.entryconfig("Unload", state='disable')
            proj_name = None


def del_logs():
    global proj_name
    for item in tv_frame.winfo_children():
        for i in item.winfo_children():
            if '.!frame.!frame.!scrollablenotebook.!notebook2.' in str(i):
                if str(i) == '.!frame.!frame.!scrollablenotebook.!notebook2.!frame':
                    continue
                i.destroy()

    for item in root.winfo_children():
        if '.!frame' in str(item):
            if str(item) == '.!frame':
                continue
            item.destroy()

    user_logs.clear()
    odlmenu.entryconfig("Unload all ODL logs", state='disable')
    if len(tv.get_children()) == 0 and len(tv_frame.tabs()) == 1:
        projmenu.entryconfig("Save", state='disable')
        projmenu.entryconfig("SaveAs", state='disable')
        projmenu.entryconfig("Unload", state='disable')
        proj_name = None


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


def copy_path(values, curItem):
    parentiid = tv.parent(curItem)
    file_name = tv.item(curItem, 'text')
    while parentiid != '':
        file_name = tv.item(parentiid, 'text')
        parentiid = tv.parent(parentiid)

    line = f'{file_name}: {values[10]}\\{values[5]}'
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
        pw.remove(tabControl)
    else:
        pw.add(tabControl, width=400)


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
            pt = Table(tb, dataframe=data[1], showtoolbar=False, showstatusbar=False)
            tv_frame.add(tb, text=f'{key} Logs')
            pt.show()
            user_logs.setdefault(f'{key}_logs.csv', pt)
            q.task_done()
            pb.stop()

        if data[0] == 'wait':
            try:
                message.unbind('<Double-Button-1>', bind_id)
            except:
                pass
            details.config(state='normal')
            details.delete('1.0', tk.END)
            details.config(state='disable')
            menubar.entryconfig("File", state="disabled")
            menubar.entryconfig("Options", state="disabled")
            search_entry.configure(state="disabled")
            btn.configure(state="disabled")
            pb.configure(mode='indeterminate')
            value_label['text'] = f'Loading {data[1]}. Please wait....'
            pb.start()
            q.task_done()

        if data[0] == 'done':
            print(q.empty())
            break

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Options", state="normal")
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
                         args=(tv, filename, user_logs, pb, value_label,),
                         daemon=True).start()

        projmenu.entryconfig("Unload", state='normal')


root = ThemedTk()
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap(application_path + '/Images/OneDrive.ico')
root.geometry('835x500')
root.minsize(835, 500)
root.protocol("WM_DELETE_WINDOW", lambda: quit(root))

style = ttk.Style()

style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))

bg = style.lookup('TFrame', 'background')

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
        ''')
    )

ButtonNotebook()

root_drive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hdd.png'))
default_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_open_hdd.png'))
shared_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_save_hdd.png'))
folder_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/directory_closed.png'))
folderop_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/directory_open.png'))
file_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow.png'))
del_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_trashcan.png'))
load_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/repeat_green.png'))
live_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/computer_desktop.png'))
json_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded.png'))
csv_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/table.png'))
uaf_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/delete_red.png'))
search_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/magnifier.png'))
exit_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/no.png'))
skin_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/skin.png'))
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

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
odsmenu = tk.Menu(file_menu, tearoff=0)
odlmenu = tk.Menu(file_menu, tearoff=0)
projmenu = tk.Menu(file_menu, tearoff=0)

options_menu = tk.Menu(menubar, tearoff=0)
submenu = tk.Menu(options_menu, tearoff=0)

for theme_name in sorted(root.get_themes()):
    submenu.add_command(label=theme_name,
                        command=lambda t=theme_name: [submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background=''),
                                                      root.set_theme(t),
                                                      style.map("Treeview",
                                                                foreground=fixed_map("foreground"),
                                                                background=fixed_map("background")),
                                                      submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background='grey'),
                                                      save_settings(), pane_config(), ButtonNotebook()])

odsmenu.add_command(label="Load <UserCid>.dat" + (' '*10),
                    image=load_img, compound='left',
                    command=lambda: open_dat(odsmenu),
                    accelerator="Ctrl+O")
odsmenu.add_command(label="Import JSON", image=json_img,
                    compound='left', command=lambda: import_json(odsmenu))
odsmenu.add_command(label="Import CSV", image=csv_img, compound='left',
                    command=lambda: import_csv(odsmenu))
odsmenu.add_command(label="Unload all files", image=uaf_img, compound='left',
                    command=lambda: clear_all(), accelerator="Alt+0")
odsmenu.entryconfig("Unload all files", state='disable')

odlmenu.add_command(label="Load ODL logs", image=folderop_img, compound='left', command=lambda: open_odl())
odlmenu.add_command(label="Unload all ODL logs", image=uaf_img, compound='left', command=lambda: del_logs())
odlmenu.entryconfig("Unload all ODL logs", state='disable')

projmenu.add_command(label="Load", image=loadl_img, compound='left', accelerator="Alt+2", command=lambda: load_proj())
projmenu.add_command(label="Save", image=save_img, compound='left', accelerator="Alt+S", command=lambda: save_proj())
projmenu.add_command(label="SaveAs", image=saveas_img, compound='left', command=lambda: saveAs_proj())
projmenu.add_command(label="Unload", image=ual_img, compound='left', command=lambda: [clear_all(), del_logs()])
projmenu.entryconfig("Save", state='disable')
projmenu.entryconfig("SaveAs", state='disable')
projmenu.entryconfig("Unload", state='disable')

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
file_menu.add_command(label="Exit", image=exit_img, compound='left',
                      command=lambda: quit(root))

options_menu.add_cascade(label="Skins", image=skin_img,
                         compound='left', menu=submenu)
options_menu.add_separator()
options_menu.add_command(label="Preferences", image=pref_img,
                         compound='left', command=lambda: preferences(root))
menubar.add_cascade(label="File",
                    menu=file_menu)
menubar.add_cascade(label="Options",
                    menu=options_menu)
submenu.entryconfig(submenu.index(ttk.Style().theme_use()),
                    background='grey')

if not ctypes.windll.shell32.IsUserAnAdmin():
    file_menu.entryconfig("Live system", state="disabled")

outer_frame = ttk.Frame(root)
main_frame = ttk.Frame(outer_frame,
                       relief='groove',
                       padding=5)

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

pw = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, background=bg, sashwidth=6)

columns = ('folder_count', 'file_count')

tv_frame = ScrollableNotebook.ScrollableNotebook(main_frame,
                                                 wheelscroll=True,
                                                 style='CustomNotebook')

tv_frame.enable_traversal()
tv_inner_frame = ttk.Frame(tv_frame)
tv_frame.add(tv_inner_frame, text='OneDrive Folders')
tv = ttk.Treeview(tv_inner_frame,
                  columns=columns,
                  selectmode='browse',
                  takefocus='false')
tv.heading('#0', text=' Path', anchor='w')
tv.heading('folder_count', text=' # folders', anchor='w')
tv.heading('file_count', text=' # files', anchor='w')
tv.column('#0', minwidth=300, width=300, stretch=True, anchor='w')
tv.column('folder_count', minwidth=60, width=60, stretch=False, anchor='e')
tv.column('file_count', minwidth=55, width=55, stretch=False, anchor='e')

find_frame = ttk.Frame(tv_inner_frame)
search_entry = ttk.Entry(find_frame, width=30, exportselection=0)
btn = ttk.Button(find_frame,
                 text="Find",
                 image=search_img,
                 takefocus=False,
                 compound='right',
                 command=lambda: [clear_search(), search(), search_result()])
search_entry.configure(state="disabled")
btn.configure(state="disabled")

scrollbv = ttk.Scrollbar(tv_inner_frame, orient="vertical", command=tv.yview)
scrollbh = ttk.Scrollbar(tv_inner_frame, orient="horizontal", command=tv.xview)
tabControl = ttk.Notebook()
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Details')
value_label = ttk.Label(bottom_frame, text='')
pb = ttk.Progressbar(bottom_frame, orient='horizontal',
                     length=160, mode='determinate')
sl = ttk.Separator(bottom_frame, orient='vertical')
message = ttk.Label(bottom_frame, text=0, background='red',
                    anchor='center', width=3)
sr = ttk.Separator(bottom_frame, orient='vertical')
sg = ttk.Sizegrip(bottom_frame)

details = tk.Text(tab1, undo=False, width=50, state='disable')
details.tag_configure('red', foreground="red")
tv.configure(yscrollcommand=scrollbv.set, xscrollcommand=scrollbh.set)
tv.tag_configure('yellow', background="yellow", foreground="black")
tv.tag_configure('red', foreground="red")

tabControl.grid_rowconfigure(0, weight=1)
tabControl.grid_columnconfigure(0, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_columnconfigure(0, weight=1)

tv_inner_frame.grid_rowconfigure(1, weight=1)
tv_inner_frame.grid_columnconfigure(0, weight=1)

pw.add(tv_frame, minsize=435)
pw.add(tabControl, width=400)

search_entry.grid(row=0, column=0, sticky="e", padx=5)
btn.grid(row=0, column=1, padx=5, pady=5)

pw.grid(row=0, column=0, sticky="nsew")
find_frame.grid(row=0, column=0, sticky='ew')
tv.grid(row=1, column=0, sticky="nsew")
scrollbv.grid(row=1, column=1, sticky="nsew")
scrollbh.grid(row=2, column=0, sticky="nsew")
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
root.bind('<Control-o>', lambda event=None: open_dat(file_menu))
root.bind('<Alt-0>', lambda event=None: clear_all())
root.bind('<<NotebookTabChanged>>', lambda event=None: log_tab())
search_entry.bind('<Return>',
                  lambda event=None: [clear_search(), search(), search_result()])
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
