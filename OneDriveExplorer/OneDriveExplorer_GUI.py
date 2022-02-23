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
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

__author__ = "Brian Maloney"
__version__ = "2022.02.23"
__email__ = "bmmaloney97@gmail.com"

ASCII_BYTE = rb" !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
String = namedtuple("String", ["s", "offset"])
uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
found = []
folder_structure = []

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
    menu_data = json.loads('{"theme": "vista", "json": false, "pretty": false, "csv": false, "html": false, "path": "."}')
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
        self.pretty_reset = tk.BooleanVar(value=menu_data['pretty'])
        self.auto_path = tk.StringVar(value=menu_data['path'])

        self.frame = ttk.Frame(self.win)

        self.inner_frame = ttk.Frame(self.frame,
                                     relief='groove',
                                     padding=5)

        self.select_frame = ttk.Frame(self.inner_frame)
        self.path_frame = ttk.Frame(self.inner_frame)
        self.exit_frame = ttk.Frame(self.inner_frame)

        self.exit_frame.grid_rowconfigure(0, weight=1)
        self.exit_frame.grid_columnconfigure(0, weight=1)

        self.frame.grid(row=0, column=0, sticky="nsew")
        self.inner_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.select_frame.grid(row=0, column=0, sticky="nsew")
        self.path_frame.grid(row=1, column=0, pady=25, sticky="nsew")
        self.exit_frame.grid(row=2, column=0, sticky="nsew")

        self.auto_json = ttk.Checkbutton(self.select_frame, text="Auto Save to JSON", var=self.json_save, offvalue=False, onvalue=True, takefocus=False)
        self.pretty = ttk.Radiobutton(self.select_frame, text="--pretty", var=self.json_pretty, takefocus=False, command=self.reset)
        self.auto_csv = ttk.Checkbutton(self.select_frame, text="Auto Save to CSV", var=self.csv_save, offvalue=False, onvalue=True, takefocus=False)
        self.auto_html = ttk.Checkbutton(self.select_frame, text="Auto Save to HTML", var=self.html_save, offvalue=False, onvalue=True, takefocus=False)

        self.label = ttk.Label(self.path_frame, text="Auto Save Path")
        self.save_path = ttk.Entry(self.path_frame, width=30, textvariable=self.auto_path)
        self.btn = ttk.Button(self.path_frame, text='...', width=3, command=self.select_dir)

        self.save = ttk.Button(self.exit_frame, text="Save", command=self.save_pref)
        self.cancel = ttk.Button(self.exit_frame, text="Cancel", command=self.close_pref)

        self.auto_json.grid(row=0, column=0, padx=5)
        self.pretty.grid(row=0, column=1, sticky="w")
        self.auto_csv.grid(row=1, column=0, columnspan=2, padx=5, sticky="w")
        self.auto_html.grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        self.label.grid(row=0, column=0, padx=5, sticky="w")
        self.save_path.grid(row=0, column=1)
        self.btn.grid(row=0, column=2, padx=5)
        self.save.grid(row=0, column=0, pady=5, sticky="e")
        self.cancel.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.sync_windows()

    def sync_windows(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/4, y + h/3))

    def reset(self):
        if self.pretty_reset.get() is False:
            self.json_pretty.set(True)
            self.pretty_reset.set(True)
        else:
            self.json_pretty.set(False)
            self.pretty_reset.set(False)

    def select_dir(self):
        dir_path = filedialog.askdirectory(initialdir="\\", title="Auto Save Location")

        if dir_path:
            dir_path = dir_path.replace('/', '\\')
            self.auto_path.set(dir_path)

    def save_pref(self):
        menu_data['json'] = self.json_save.get()
        menu_data['pretty'] = self.json_pretty.get()
        menu_data['csv'] = self.csv_save.get()
        menu_data['html'] = self.html_save.get()
        menu_data['path'] = self.auto_path.get()
        if not os.path.exists(menu_data['path']):
            os.makedirs(menu_data['path'])
        with open("ode.settings", "w") as jsonfile:
            json.dump(menu_data, jsonfile)
        self.win.destroy()

    def close_pref(self):
        self.win.destroy()


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
        return match.group()[:-3].decode("utf-16")
    return 'null'


def clear_all():
    tv.delete(*tv.get_children())
    file_menu.entryconfig("Unload all folders", state='disable')


def progress(total, count, ltext):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total))
        value_label['text'] = f"{ltext}: {pb['value']}%"


def parse_dat(usercid, start):
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
        uuid4hex = re.compile(b'[A-F0-9]{16}![0-9]*\.')
        personal = uuid4hex.search(f.read())
        if not personal:
            uuid4hex = re.compile(b'{[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}', re.I)
        f.seek(0)
        df = pd.DataFrame(columns=['ParentId',
                                   'DriveItemId',
                                   'Type',
                                   'Name',
                                   'Children'])
        dir_index = []
        for match in re.finditer(uuid4hex, f.read()):
            s = match.start()
            count = s
            diroffset = s - 40
            objoffset = s - 79
            f.seek(diroffset)
            duuid = f.read(32).decode("utf-8").strip('\u0000')
            f.seek(objoffset)
            ouuid = f.read(32).decode("utf-8").strip('\u0000')
            name = unicode_strings(f.read(400))
            if not dir_index:
                input = {'ParentId': '',
                         'DriveItemId': duuid,
                         'Type': 'Root',
                         'Name': 'User Folder',
                         'Children': []
                         }
                dir_index.append(input)
            input = {'ParentId': duuid,
                     'DriveItemId': ouuid,
                     'Type': 'File',
                     'Name': name,
                     'Children': []
                     }

            dir_index.append(input)
            progress(total, count, 'Building folder list. Please wait....')

    df = pd.DataFrame.from_records(dir_index)
    df.loc[df.DriveItemId.isin(df.ParentId), 'Type'] = 'Folder'
    df.at[0, 'Type'] = 'Root'
    parse_onederive(f.name, df, start, dat=True)


def parse_csv(filename, start):
    start = time.time()
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Options", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    df = pd.read_csv(filename, usecols=['ParentId', 'DriveItemId', 'Type', 'Name'])
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

    return find_parent(value, id_name_dict, parent_dict) +"\\\\"+ str(id_name_dict.get(value))


def parse_onederive(name, df, start, dat=False):
    id_name_dict = dict(zip(df.DriveItemId, df.Name))
    parent_dict = dict(zip(df.DriveItemId, df.ParentId))

    df['Level'] = df.DriveItemId.apply(lambda x: len(find_parent(x, id_name_dict, parent_dict).lstrip('\\\\').split('\\\\')))

    share_df = df.loc[(df.Level == 1) & (~df.ParentId.isin(df.DriveItemId)) & (df.Type != 'Root')]
    share_list = list(set(share_df.ParentId))
    share_root = []
    for x in share_list:
        input = {'ParentId': '',
                 'DriveItemId': x,
                 'Type': 'Root',
                 'Name': 'Shared with user',
                 'Children': [],
                 'Level': 1
                 }
        share_root.append(input)
    share_df = pd.DataFrame.from_records(share_root)
    df = pd.concat([df, share_df], ignore_index=True, axis=0)

    file_count = df.Type.value_counts()['File']
    folder_count = df.Type.value_counts()['Folder']

    def subset(dict_, keys):
        return {k: dict_[k] for k in keys}

    cache = {}
    final = []

    for row in df.sort_values(by=['Level', 'ParentId', 'Type'], ascending=[False, False, False]).to_dict('records'):
        file = subset(row, keys=('ParentId', 'DriveItemId', 'Type', 'Name', 'Children'))
        if row['Type'] == 'File':
            folder = cache.setdefault(row['ParentId'], {})
            folder.setdefault('Children', []).append(file)
        else:
            folder = cache.get(row['DriveItemId'], {})
            temp = {**file, **folder}
            folder_merge = cache.setdefault(row['ParentId'], {})
            if row['Type'] == 'Root':
                final.append(temp)
            else:
                folder_merge.setdefault('Children', []).append(temp)

    cache = {'ParentId': '',
             'DriveItemId': '',
             'Type': 'Root Drive',
             'Name': name,
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


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("", "end", image=root_drive_img, text=d['Name'], values=(d['ParentId'], d['DriveItemId'], d['Name'], d['Type'], len(d['Children'])))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        if len(c['Children']) == 0:
            parent_child(c, tv.insert(parent_id, "end", image=file_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['Name'], c['Type'], len(c['Children']))))
        elif c['Type'] == 'Root':
            parent_child(c, tv.insert(parent_id, "end", image=root_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['Name'], c['Type'], len(c['Children']))))
        else:
            parent_child(c, tv.insert(parent_id, 0, image=folder_img, text=c['Name'], values=(c['ParentId'], c['DriveItemId'], c['Name'], c['Type'], len(c['Children']))))


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
        line = f'Name: {values[2]}\nType: {values[3]}\nParentId: {values[0]}\nDriveItemId: {values[1]}'
        if values[3] == 'Folder' or values[3] == 'Root':
            line += f'\n\n# Children: {values[4]}'
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
        start = time.time()
        threading.Thread(target=parse_dat, args=(filename, start,), daemon=True).start()


def import_json():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import JSON",
                                      filetypes=(("OneDrive dat file", "*.json"),))

    if filename:
        value_label['text'] = ''
        details.config(state='normal')
        details.delete('1.0', tk.END)
        details.config(state='disable')
        parent_child(json.load(filename))
        filename.close()
        if len(tv.get_children()) > 0:
            file_menu.entryconfig("Unload all folders", state='normal')


def import_csv():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import CSV",
                                      filetypes=(("OneDrive dat file", "*.csv"),))

    if filename:
        start = time.time()
        parse_csv(filename, start)


def save_settings():
    menu_data['theme'] = ttk.Style().theme_use()
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


def fixed_map(option):
    # Returns the style map for 'option' with any styles starting with
    # ("!disabled", "!selected", ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
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

        if values[3] == 'Root Drive':
            popup.add_command(label="Remove OneDrive Folder", image=rof_img, compound='left', command=lambda: del_folder(curItem))
            popup.add_separator()

        popup.add_command(label="Copy", image=copy_img, compound='left', command=lambda: copy_item(values))

        if values[3] == 'Folder' or values[3] == 'Root':
            popup.add_separator()
            popup.add_command(label="Expand folders", image=exp_img, compound='left', command=lambda: open_children(curItem), accelerator="Alt+Down")
            popup.add_command(label="Collapse folders", image=col_img, compound='left', command=lambda: close_children(curItem), accelerator="Alt+Up")
        popup.tk_popup(event.x_root, event.y_root)
    finally:
        popup.grab_release()


def del_folder(iid):
    tv.delete(iid)
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    if len(tv.get_children()) == 0:
        file_menu.entryconfig("Unload all folders", state='disable')


def open_children(parent):
    tv.item(parent, open=True)  # open parent
    for child in tv.get_children(parent):
        open_children(child)    # recursively open children


def close_children(parent):
    tv.item(parent, open=False)  # close parent
    for child in tv.get_children(parent):
        close_children(child)    # recursively close children


def copy_item(values):
    line = f'Name: {values[2]}\nType: {values[3]}\nParentId: {values[0]}\nDriveItemId: {values[1]}'
    if values[3] == 'Folder':
        line += f'\n\n# Children: {values[4]}'
    root.clipboard_append(line)


root = ThemedTk()
ttk.Style().theme_use(menu_data['theme'])
root.title(f'OneDriveExplorer v{__version__}')
root.iconbitmap(application_path + '/Images/OneDrive.ico')
root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
style = ttk.Style()
style.map("Treeview",
          foreground=fixed_map("foreground"),
          background=fixed_map("background"))

root_drive_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/hdd.png'))
root_img = ImageTk.PhotoImage(Image.open(application_path + '/Images/file_yellow_hierarchy1_expanded_open_hdd.png'))
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
options_menu.add_cascade(label="Skins", image=skin_img, compound='left',menu=submenu)
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

outer_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(main_frame, width=30)
btn = ttk.Button(main_frame, text="Find", image=search_img, compound='right', command=lambda: [clear_search(), search()])

pw = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)

tv_frame = ttk.Frame(main_frame)
tv = ttk.Treeview(tv_frame, show='tree', selectmode='browse')
scrollbv = ttk.Scrollbar(tv_frame, orient="vertical", command=tv.yview)
scrollbh = ttk.Scrollbar(tv_frame, orient="horizontal", command=tv.xview)
tabControl = ttk.Notebook(main_frame)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Details')
pb = ttk.Progressbar(main_frame, orient='horizontal', length=160, mode='determinate')
value_label = ttk.Label(main_frame, text='')
sg = ttk.Sizegrip(main_frame)

details = tk.Text(tab1, undo=False, width=50, cursor='arrow', state='disable')
tv.configure(yscrollcommand=scrollbv.set, xscrollcommand=scrollbh.set)
tv.tag_configure('yellow', background="yellow", foreground="black")

tabControl.grid_rowconfigure(0, weight=1)
tabControl.grid_columnconfigure(0, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab1.grid_columnconfigure(0, weight=1)

tv_frame.grid_rowconfigure(0, weight=1)
tv_frame.grid_columnconfigure(0, weight=1)

pw.add(tv_frame)
pw.add(tabControl)

search_entry.grid(row=0, column=1, sticky="e", padx=(0, 5))
btn.grid(row=0, column=2, sticky="e", padx=(5, 5))
tv.grid(row=0, column=0, sticky="nsew")
scrollbv.grid(row=0, column=1, sticky="nsew")
scrollbh.grid(row=1, column=0, sticky="nsew")
sg.grid(row=2, column=2, sticky='se')
details.grid(row=0, column=0, sticky="nsew")
pb.grid(row=2, column=1, sticky='se', pady=(5, 3), padx=(0, 20), columnspan=2)
value_label.grid(row=2, column=0, sticky='se', padx=(0, 110), columnspan=2)
pw.grid(row=1, column=0, columnspan=3, sticky="nsew")

tv.bind('<<TreeviewSelect>>', selectItem)
tv.bind("<Button-3>", do_popup)
tv.bind('<Alt-Down>', lambda event=None: open_children(tv.selection()))
tv.bind('<Alt-Up>', lambda event=None: close_children(tv.selection()))
root.bind('<Control-o>', lambda event=None: open_dat())
root.bind('<Alt-0>', lambda event=None: clear_all())
details.bind('<Key>', lambda a: "break")
details.bind('<Button>', lambda a: "break")
details.bind('<Motion>', lambda a: "break")

if getattr(sys, 'frozen', False):
    pyi_splash.close()
root.mainloop()
