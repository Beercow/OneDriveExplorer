import os
import sys
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
__version__ = "2022.02.11"
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
found = []
folder_structure = []

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if os.path.isfile('ode.settings'):
    with open("ode.settings", "r") as jsonfile:
        menu_data = json.load(jsonfile)
        jsonfile.close()
else:
    menu_data = json.loads('{"theme": "vista"}')
    with open("ode.settings", "w") as jsonfile:
        json.dump(menu_data, jsonfile)


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


def unicode_strings(buf, n=4):
    reg = rb"((?:[%s]\x00){%d,})" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    match = uni_re.search(buf)
    if match:
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
    file_menu.entryconfig("Unload all folders", state='disable')


def progress(total, count, ltext):
    if pb['value'] != 100:
        pb['value'] = round(100.0 * count / float(total))
        value_label['text'] = f"{ltext}: {pb['value']}%"


def parse_onederive(usercid):
#    clear_all()
    details.config(state='normal')
    details.delete('1.0', tk.END)
    details.config(state='disable')
    menubar.entryconfig("File", state="disabled")
    menubar.entryconfig("Tools", state="disabled")
    search_entry.configure(state="disabled")
    btn.configure(state="disabled")
    dir_list = []
    misfits = []
    with open(usercid, 'rb') as f:
        b = f.read()
    data = io.BytesIO(b)
    uuid4hex = re.compile(b'[A-F0-9]{16}![0-9]*\.')
    personal = uuid4hex.search(b)
    if not personal:
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
                        'Type': 'Root',
                        'Name': f.name,
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
        type = 'File'
        name = unicode_strings(data.read())
        if ouuid in dir_list:
            type = 'Folder'
        input = {'Folder_UUID': duuid,
                 'Object_UUID': ouuid,
                 'Type': type,
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

    pb.configure(mode='indeterminate')
    value_label['text'] = "Building tree. Please wait..."
    pb.start()
    parent_child(folder_structure)
    pb.stop()
    pb.configure(mode='determinate')

    menubar.entryconfig("File", state="normal")
    menubar.entryconfig("Tools", state="normal")
    search_entry.configure(state="normal")
    btn.configure(state="normal")

    json_object = json.dumps(folder_structure)
    file_extension = os.path.splitext(f.name)[1][1:]
    if file_extension == 'previous':
        output = open(os.path.basename(f.name).split('.')[0]+"_"+file_extension+"_OneDrive.json", 'w')
    else:
        output = open(os.path.basename(f.name).split('.')[0]+"_OneDrive.json", 'w')
    output.write(json_object)
    output.close()
    pb['value'] = 0
    value_label['text'] = 'Complete!'
    if len(tv.get_children()) > 0:
        file_menu.entryconfig("Unload all folders", state='normal')


def parent_child(d, parent_id=None):
    if parent_id is None:
        # This line is only for the first call of the function
        parent_id = tv.insert("", "end", text=d['Name'], values=(d['Folder_UUID'], d['Object_UUID'], d['Name'], d['Type'], len(d['Children'])))

    for c in d['Children']:
        # Here we create a new row object in the TreeView and pass its return value for recursion
        # The return value will be used as the argument for the first parameter of this same line of code after recursion
        if len(c['Children']) == 0:
            parent_child(c, tv.insert(parent_id, "end", text=c['Name'], values=(c['Folder_UUID'], c['Object_UUID'], c['Name'], c['Type'], len(c['Children']))))
        else:
            parent_child(c, tv.insert(parent_id, 0, text=c['Name'], values=(c['Folder_UUID'], c['Object_UUID'], c['Name'], c['Type'], len(c['Children']))))


def selectItem(a):
    curItem = tv.selection()
    values = tv.item(curItem, 'values')
    details.config(state='normal')
    details.delete('1.0', tk.END)
    try:
        line = f'Name: {values[2]}\nType: {values[3]}\nFolder_UUID: {values[0]}\nObject_UUID: {values[1]}'
        if values[3] == 'Folder':
            line += f'\n\n# Children: {values[4]}'
        details.insert(tk.END, line)
        details.see(tk.END)
    except IndexError:
        pass
    details.config(state='disable')


def open_dat():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Open",
                                          filetypes=(("OneDrive dat file", "*.dat *.dat.previous"),))

    if filename:
        threading.Thread(target=parse_onederive, args=(filename,), daemon=True).start()


def import_json():
    filename = filedialog.askopenfile(initialdir="/",
                                      title="Import JSON",
                                      filetypes=(("OneDrive dat file", "*.json"),))

    if filename:
#        clear_all()
        details.config(state='normal')
        details.delete('1.0', tk.END)
        details.config(state='disable')
        parent_child(json.load(filename))
        filename.close()
        if len(tv.get_children()) > 0:
            file_menu.entryconfig("Unload all folders", state='normal')


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
    try:
        curItem = tv.identify_row(event.y)
        values = tv.item(curItem, 'values')
        popup = tk.Menu(root, tearoff=0)
#        popup.add_command(label="Remove OneDrive Folder" + (' '*10), command=lambda: del_folder(curItem))
        if values[3] == 'Root':
            popup.add_command(label="Remove OneDrive Folder", command=lambda: del_folder(curItem))
            popup.add_separator()
        else:
            popup.add_command(label="Copy", command=lambda: copy_item(values))
        if values[3] == 'Folder' or values[3] == 'Root':
            if values[3] == 'Folder':
                popup.add_separator()
            popup.add_command(label="Expand folders", command=lambda: open_children(curItem), accelerator="Alt+Down")
            popup.add_command(label="Collapse folders", command=lambda: close_children(curItem), accelerator="Alt+Up")
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
    line = f'Name: {values[2]}\nType: {values[3]}\nFolder_UUID: {values[0]}\nObject_UUID: {values[1]}'
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
                                                      root.set_theme(t), style.map("Treeview", foreground=fixed_map("foreground"),
                                                                                   background=fixed_map("background")),
                                                      submenu.entryconfig(submenu.index(ttk.Style().theme_use()), background='grey'),
                                                      save_settings()])

file_menu.add_command(label="Load <UsreCid>.dat" + (' '*10), command=lambda: open_dat(), accelerator="Ctrl+O")
file_menu.add_command(label="Import JSON", command=lambda: import_json())
file_menu.add_command(label="Unload all folders", command=lambda: clear_all(), accelerator="Alt+0")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=lambda: quit(root))
file_menu.entryconfig("Unload all folders", state='disable')
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
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

search_entry = ttk.Entry(main_frame, width=30)
btn = ttk.Button(main_frame, text="Find", command=lambda: [clear_search(), search()])

pw = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)

tv_frame = ttk.Frame(main_frame)
tv = ttk.Treeview(tv_frame, show='tree', selectmode='browse')
scrollb = ttk.Scrollbar(tv_frame, orient="vertical", command=tv.yview)
tabControl = ttk.Notebook(main_frame)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Details')
pb = ttk.Progressbar(main_frame, orient='horizontal', length=160, mode='determinate')
value_label = ttk.Label(main_frame, text='')
sg = ttk.Sizegrip(main_frame)

details = tk.Text(tab1, undo=False, width=50, cursor='arrow', state='disable')
tv.configure(yscrollcommand=scrollb.set)
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
scrollb.grid(row=0, column=1, sticky="nsew")
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

root.mainloop()
