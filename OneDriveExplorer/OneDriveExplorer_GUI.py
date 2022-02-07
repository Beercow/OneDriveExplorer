import os
import re
import io
import json
from collections import namedtuple
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog
import threading

__author__ = "Brian Maloney"
__version__ = "2022.02.08"
__email__ = "bmmaloney97@gmail.com"


class quit:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(self.root)
        self.win.attributes("-toolwindow", 1)
        self.win.attributes("-topmost", 1)
        self.win.title("Please confirm")
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.__callback)

        self.frame = ttk.Frame(self.win)

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
        menu_data['theme'] = ttk.Style().theme_use()
        with open("ode.settings", "w") as jsonfile:
            json.dump(menu_data, jsonfile)
        root.destroy()

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


ASCII_BYTE = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
String = namedtuple("String", ["s", "offset"])
uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
dir_list = []
folder_structure = {}


if os.path.isfile('ode.settings'):
    with open("ode.settings", "r") as jsonfile:
        menu_data = json.load(jsonfile)
        jsonfile.close()
else:
    menu_data = json.loads('{"theme": "vista"}')
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def unicode_strings(buf, n=4):
    reg = rb"((?:[%s]\x00){%d,})" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    return match.group().decode("utf-16")


def folder_search(dict_list, input, duuid, added):
    for k, v in dict_list.items():
        if(isinstance(v, list)):
            for dic in v:
                if duuid == dic['Object_UUID']:
                    dic['Children'].append(input)
                    added = True
                else:
                    r = folder_search(dic, input, duuid, added)
                    added = r
    return added


def clear_all():
    tv.delete(*tv.get_children())


def progress(total, count, ltext):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total))
        value_label['text'] = f"{ltext}: {pb['value']}%"


def parse_onederive(usercid):
    clear_all()
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Tools", state="disabled")
    misfits = []
    with open(usercid, 'rb') as f:
        b = f.read()
    data = io.BytesIO(b)
    if data.read(11)[10] != 1:
        value_label['text'] = 'Not a valid OneDrive file'
        menubar.entryconfig("File", state="normal")
        menubar.entryconfig("Tools", state="normal")
        return
    data.seek(-7, 1)
    if data.read(1) == b'\x01':
        uuid4hex = re.compile(b'[A-F0-9]{16}![0-9]*\.')
    else:
        uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
    total = len(b)
    for match in re.finditer(uuid4hex, b):
        s = match.start()
        count = s
        diroffset = s - 40
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8").strip('\u0000')
        if duuid not in dir_list:
            dir_list.append(duuid)
        progress(total, count, 'Building folder list')

    folder_structure = {'Folder_UUID': '',
                        'Object_UUID': dir_list[0],
                        'Type': 'Folder',
                        'Name': 'Root',
                        'Children': []
                        }

    pb['value'] = 0

    for match in re.finditer(uuid4hex, b):
        added = False
        s = match.start()
        count = s
        diroffset = s - 40
        objoffset = s - 79
        data.seek(diroffset)
        duuid = data.read(32).decode("utf-8").strip('\u0000')
        data.seek(objoffset)
        ouuid = data.read(32).decode("utf-8").strip('\u0000')
        name = unicode_strings(data.read())
        if ouuid in dir_list:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'Folder',
                     'Name': name,
                     'Children': []
                     }
            if duuid == folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                added = folder_search(folder_structure, input, duuid, added)
                if not added:
                    misfits.append(input)
        else:
            input = {'Folder_UUID': duuid,
                     'Object_UUID': ouuid,
                     'Type': 'File',
                     'Name': name,
                     'Children': []
                     }
            if duuid == folder_structure['Object_UUID']:
                folder_structure['Children'].append(input)
            else:
                added = folder_search(folder_structure, input, duuid, added)
                if not added:
                    misfits.append(input)
        progress(total, count, 'Recreating OneDrive folder')

    total = len(misfits)
    count = 0
    for i in misfits:
        added = folder_search(folder_structure, i, i['Folder_UUID'], added)
        count += 1
        progress(count, total, 'Adding missing files/folders')

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Tools", state="normal")
    parent_child(folder_structure)
    pb['value'] = 0
    value_label['text'] = 'Complete!'


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("", "end", text=d['Name'], values=(d['Folder_UUID'], d['Object_UUID'], d['Name'], d['Type'], len(d['Children'])))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        parent_child(c, tv.insert(parent_id, "end", text=c['Name'], values=(c['Folder_UUID'], c['Object_UUID'], c['Name'], c['Type'], len(c['Children']))))


def selectItem(a):
    curItem = tv.focus()

    values = tv.item(curItem, 'values')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    line = f'Name: {values[2]}\nType: {values[3]}\nFolder_UUID: {values[0]}\nObject_UUID: {values[1]}'
    if values[3] == 'Folder':
        line += f'\n\n# Children: {values[4]}'
    details.insert(tk.END, line)
    details.see(tk.END)
    details.config(state='disable')


def open_dat():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDrive dat file", "*.dat"),))

    if filename:
        threading.Thread(target=parse_onederive, args=(filename,), daemon=True).start()


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


root = ThemedTk()
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap('Images/OneDrive.ico')
root.protocol("WM_DELETE_WINDOW", lambda: quit(root))

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
tool_menu = tk.Menu(menubar, tearoff=0)
submenu = tk.Menu(tool_menu, tearoff=0)

for theme_name in sorted(root.get_themes()):
    submenu.add_command(label=theme_name,
                        command=lambda t=theme_name: [submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background=''),
                                                      root.set_theme(t),
                                                      submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background='grey'), save_settings()])

file_menu.add_command(label="Load <UsreCid>.dat", command=lambda: open_dat(), accelerator="Ctrl+O")
file_menu.add_command(label="Exit", command=lambda: quit(root))
tool_menu.add_cascade(label="Skins",
                      menu=submenu)
menubar.add_cascade(label="File",
                    menu=file_menu)
menubar.add_cascade(label="Tools",
                    menu=tool_menu)
submenu.entryconfig(submenu.index(ttk.Style().theme_use()),
                    background='grey')

outer_frame = ttk.Frame(root)
main_frame = ttk.Frame(outer_frame,
                       relief='groove',
                       padding=5)

outer_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

pw = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)

tv_frame = ttk.Frame(main_frame)
tv = ttk.Treeview(tv_frame, show='tree', selectmode='browse')
scrollb = ttk.Scrollbar(tv_frame, orient="vertical", command=tv.yview)
tabControl = ttk.Notebook(main_frame)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Details')
pb = ttk.Progressbar(main_frame, orient='horizontal', length=80, mode='determinate')
value_label = ttk.Label(main_frame, text='')
sg = ttk.Sizegrip(main_frame)

details = tk.Text(tab1, undo=False, width=50, cursor='arrow', state='disable')
tv.configure(yscrollcommand=scrollb.set)

tabControl.grid_rowconfigure(0, weight=1)
tabControl.grid_columnconfigure(0, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_columnconfigure(0, weight=1)

tv_frame.grid_rowconfigure(0, weight=1)
tv_frame.grid_columnconfigure(0, weight=1)

pw.add(tv_frame)
pw.add(tabControl)

tv.grid(row=0, column=0, sticky="nsew")
scrollb.grid(row=0, column=1, sticky="nsew")
sg.grid(row=1, column=2, sticky='se')
details.grid(row=0, column=0, sticky="nsew")
pb.grid(row=1, column=1, sticky='se')
value_label.grid(row=1, column=0, sticky='se')
pw.grid(row=0, column=0, columnspan=3, sticky="nsew")

tv.bind('<<TreeviewSelect>>', selectItem)
root.bind('<Control-o>', lambda event=None: open_dat())
details.bind('<Key>', lambda a: "break")
details.bind('<Button>', lambda a: "break")
details.bind('<Motion>', lambda a: "break")

root.mainloop()
