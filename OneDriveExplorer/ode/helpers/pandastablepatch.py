# OneDriveExplorer
# Copyright (C) 2022
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

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import numpy as np
from pandastable import Table
from pandastable.data import TableModel
from pandastable.headers import ColumnHeader, RowHeader


root = ''
default_font = ''
application_path = ''
asc_img = ''
desc_img = ''


def MypopupMenu(self, event):
    df = self.table.model.df
    if len(df.columns) == 0:
        return
    multicols = self.table.multiplecollist
    colnames = list(df.columns[multicols])[:4]
    colnames = [str(i)[:20] for i in colnames]
    if len(colnames) > 2:
        colnames = ','.join(colnames[:2])+'+%s others' % str(len(colnames)-2)
    else:
        colnames = ','.join(colnames)
    popupmenu = tk.Menu(self, tearoff=0)
    formatmenu = tk.Menu(popupmenu, tearoff=0)
    highlightmenu = tk.Menu(formatmenu, tearoff=0)
    udmenu = tk.Menu(formatmenu, tearoff=0)

    formatmenu.add_cascade(label="Highlight Cell Rules", menu=highlightmenu)
    formatmenu.add_cascade(label="Unique/Duplicate Rules", menu=udmenu)
    formatmenu.add_command(label="Manage Rules...")
    highlightmenu.add_command(label="Greater Than...")
    highlightmenu.add_command(label="Less Than...")
    highlightmenu.add_command(label="Between...")
    highlightmenu.add_command(label="Equal To...")
    highlightmenu.add_command(label="Text That Contains...")
    highlightmenu.add_command(label="Custom Condition...")
    udmenu.add_command(label="Unique Values...")
    udmenu.add_command(label="Duplicate Values...")

    def popupFocusOut(event):
        popupmenu.unpost()
    popupmenu.add_command(label="Sort by " + colnames, image=asc_img, compound='left',
                          command=lambda: self.table.sortTable(ascending=[1 for i in multicols]))
    popupmenu.add_command(label="Sort by " + colnames, image=desc_img, compound='left',
                          command=lambda: self.table.sortTable(ascending=[0 for i in multicols]))
#    popupmenu.add_separator()
#    popupmenu.add_command(label="Group By This Column")
#    popupmenu.add_command(label="Hide Group By Box")
#    popupmenu.add_separator()
#    popupmenu.add_command(label="Hide This Column")
#    popupmenu.add_command(label="Column Chooser")
#    popupmenu.add_command(label="Best Fit")
#    popupmenu.add_command(label="Best Fit (all columns)")
#    popupmenu.add_separator()
#    popupmenu.add_command(label="Filter Editor...")
#    popupmenu.add_command(label="Hide Auto Filter Row")
#    popupmenu.add_separator()
#    popupmenu.add_cascade(label="Conditional Formatting", menu=formatmenu)
    popupmenu.bind("<FocusOut>", popupFocusOut)
    popupmenu.focus_set()
    popupmenu.post(event.x_root, event.y_root)
    return popupmenu


# disables row header popup
def Myhandle_right_click(self, event):
    """respond to a right click"""
    return


# Custom column header popup
ColumnHeader.popupMenu = MypopupMenu
# disables row header popup
RowHeader.handle_right_click = Myhandle_right_click


class MyTable(Table):
    """Custom table class inherits from Table. You can then override required methods"""
    def __init__(self, parent=None, model=None, dataframe=None,
                 width=None, height=None,
                 rows=20, cols=5, showtoolbar=False, showstatusbar=False,
                 editable=True, enable_menus=True,
                 **kwargs):
        Table.__init__(self, parent, model, dataframe,
                       width, height,
                       rows, cols, showtoolbar, showstatusbar,
                       editable, enable_menus,
                       **kwargs)
        if dataframe is not None:
            self.model = MyTableModel(dataframe=dataframe)
        elif model is not None:
            self.model = model
        else:
            self.model = MyTableModel(rows=rows, columns=cols)
        return

    # removed Control-f
    def doBindings(self):
        """Bind keys and mouse clicks, this can be overriden"""

        self.bind("<Button-1>", self.handle_left_click)
        self.bind("<Double-Button-1>", self.handle_double_click)
        self.bind("<Control-Button-1>", self.handle_left_ctrl_click)
        self.bind("<Shift-Button-1>", self.handle_left_shift_click)

        self.bind("<ButtonRelease-1>", self.handle_left_release)
        if self.ostyp == 'darwin':
            # For mac we bind Shift, left-click to right click
            self.bind("<Button-2>", self.handle_right_click)
            self.bind('<Shift-Button-1>', self.handle_right_click)
        else:
            self.bind("<Button-3>", self.handle_right_click)

        self.bind('<B1-Motion>', self.handle_mouse_drag)
        # self.bind('<Motion>', self.handle_motion)

        self.bind("<Control-c>", self.copy)
        # self.bind("<Control-x>", self.deleteRow)
        # self.bind_all("<Control-n>", self.addRow)
        self.bind("<Delete>", self.clearData)
        self.bind("<Control-v>", self.paste)
        self.bind("<Control-a>", self.selectAll)
        # self.bind("<Control-f>", self.findText)

        self.bind("<Right>", self.handle_arrow_keys)
        self.bind("<Left>", self.handle_arrow_keys)
        self.bind("<Up>", self.handle_arrow_keys)
        self.bind("<Down>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<KP_8>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Return>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Tab>", self.handle_arrow_keys)
        # if 'windows' in self.platform:
        self.bind("<MouseWheel>", self.mouse_wheel)
        self.bind('<Button-4>', self.mouse_wheel)
        self.bind('<Button-5>', self.mouse_wheel)
        self.focus_set()
        return

    def handle_double_click(self, event):
        self.root = root
        self.data = self.getSelectedDataFrame()
        self.cell = self.data.to_string(header=False, index=False, float_format=lambda x: '%.0f' % x)
        self.size = tk.StringVar()

        self.win = tk.Toplevel(self.root)
        self.win.geometry('800x450')
        self.win.minsize(800, 450)
        self.win.title("Cell contents")
        self.win.iconbitmap(application_path + '/Images/titles/windows_tile.ico')
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)

        self.ccFrame = ttk.Frame(self.win, padding=5)
        self.ccFrame.grid_rowconfigure(0, weight=1)
        self.ccFrame.grid_columnconfigure(0, weight=1)

        self.scrollb = ttk.Scrollbar(self.ccFrame)
        self.cc = tk.Text(self.ccFrame,
                          font=default_font,
                          undo=False,
                          yscrollcommand=self.scrollb.set)

        self.font = tkFont.Font(font=self.cc['font']).actual()
        self.size.set(self.font['size'])

        self.cc.insert(tk.END, self.cell)
        self.cc.config(state='disable')
        self.scrollb.config(command=self.cc.yview)

        self.fFrame = ttk.Frame(self.ccFrame)
        self.fLabel = ttk.Label(self.fFrame, text='Font size')
        self.fsize = tk.Spinbox(self.fFrame,
                                from_=2,
                                to=50,
                                width=4,
                                bd=0,
                                state='readonly',
                                justify=tk.RIGHT,
                                textvariable=self.size,
                                command=self.change_size)

        self.ccFrame.grid(row=0, column=0, sticky="nsew")
        self.cc.grid(row=0, column=0, sticky="nsew")
        self.scrollb.grid(row=0, column=1, sticky="ns")
        self.fFrame.grid(row=1, column=0, columnspan=2)
        self.fLabel.grid(row=0, column=0, pady=(5, 0), padx=(0, 5))
        self.fsize.grid(row=0, column=1, pady=(5, 0))

        self.size.trace_add("write", self.change_size)
        x = self.root.winfo_x()
        qw = self.win.winfo_width()
        y = self.root.winfo_y()
        qh = self.win.winfo_height()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.win.geometry("+%d+%d" % (x + w/2 - qw/2, y + h/2 - qh/2))
        return

    def change_size(self, *args):
        self.cc.config(font=(self.font['family'], self.fsize.get()))

    # disables cell popup
    def handle_right_click(self, event):
        """respond to a right click"""
        return


class MyTableModel(TableModel):
    """Custom tablemodel class inherits from TableModel. You can then override required methods"""
    def __init__(self, dataframe=None, **kwargs):
        TableModel.__init__(self, dataframe, **kwargs)
        return

    def getlongestEntry(self, colindex, n=500):
        """Get the longest string in the column for determining width. Just uses the first
         n rows for speed"""

        df = self.df
        col = df.columns[colindex]
        try:
            if df.dtypes[col] == 'float64':
                c = df[col].iloc[:n].round(3)
            else:
                c = df[col].iloc[:n]
        except Exception:
            return 1
        longest = c.astype('object').astype('str').str.len().max()
        if np.isnan(longest):
            return 1
        return longest
