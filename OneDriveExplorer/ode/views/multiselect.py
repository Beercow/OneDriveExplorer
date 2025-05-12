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

import tkinter as tk
from tkinter import ttk, filedialog
import ctypes

# These are your Windows-specific style constants
GWL_STYLE = -16
WS_MAXIMIZEBOX = 0x00010000
WS_MINIMIZEBOX = 0x00020000

get_parent = ctypes.windll.user32.GetParent
get_window_long = ctypes.windll.user32.GetWindowLongW
set_window_long = ctypes.windll.user32.SetWindowLongW


class FileSelectDialog:
    def __init__(self, root, fields=None, callback=None, title="Select Files", icon_path=None):
        self.root = root
        self.fields = fields or [("Select .dat File", ".dat"), ("Select .sql File", ".sql")]
        self.callback = callback  # Called with result on submit
        self.icon_path = icon_path
        self.create_dialog(title)

    def create_dialog(self, title):
        self.win = tk.Toplevel(self.root)
        self.win.title(title)
        self.win.wm_transient(self.root)
        if self.icon_path:
            self.win.iconbitmap(self.icon_path)
        self.win.grab_set()
        self.win.focus_force()
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.setup_window_style()

        self.file_vars = {}
        self.build_widgets()
        self.sync_windows()
        self.root.bind('<Configure>', self.sync_windows)
        self.win.bind('<Configure>', self.sync_windows)

    def setup_window_style(self):
        hwnd = get_parent(self.win.winfo_id())
        old_style = get_window_long(hwnd, GWL_STYLE)
        new_style = old_style & ~WS_MAXIMIZEBOX & ~WS_MINIMIZEBOX
        set_window_long(hwnd, GWL_STYLE, new_style)

    def build_widgets(self):
        self.row_widgets = {}
        self.frame = ttk.Frame(self.win)
        self.inner_frame = ttk.Frame(self.frame, padding=10)

        self.frame.grid(row=0, column=0)
        self.inner_frame.grid(row=0, column=0)

        for idx, (label_text, ext) in enumerate(self.fields):
            var = tk.StringVar()
            self.file_vars[ext] = var
            var.trace_add("write", lambda *args, e=ext: self.check_field_states())

            label = ttk.Label(self.inner_frame, text=label_text)
            entry = ttk.Entry(self.inner_frame, textvariable=var, width=50)
            button = ttk.Button(self.inner_frame, text="Browse", command=lambda e=ext: self.browse_file(e))

            label.grid(row=idx, column=0, sticky='w', pady=5)
            entry.grid(row=idx, column=1, pady=5, padx=(5, 5))
            button.grid(row=idx, column=2, pady=5)

            self.row_widgets[ext] = (label, entry, button)

        # Buttons
        ttk.Button(self.inner_frame, text="Submit", command=self.on_submit).grid(row=len(self.fields), column=1, sticky='e', pady=10, padx=5)
        ttk.Button(self.inner_frame, text="Cancel", command=self.on_cancel).grid(row=len(self.fields), column=2, sticky='w', pady=10, padx=5)

        self.check_field_states()

    def check_field_states(self):
        try:
            dat_filled = bool(self.file_vars["*.dat *.dat.previous"].get().strip())
            sync_filled = bool(self.file_vars["SyncEngineDatabase.db"].get().strip())
            enable_listsync = dat_filled or sync_filled

            if enable_listsync:
                for widget in self.row_widgets["Microsoft.ListSync.db"]:
                    if 'entry' in str(widget):
                        widget.configure(style="TEntry", state="normal")
                    else:
                        widget.configure(state="normal")
            else:
                self.file_vars["Microsoft.ListSync.db"].set("")  # Clear it
                for widget in self.row_widgets["Microsoft.ListSync.db"]:
                    if 'entry' in str(widget):
                        widget.configure(style="Disabled.TEntry", state="disabled")
                    else:
                        widget.configure(state="disabled")

            ntuser_filled = bool(self.file_vars["NTUSER.DAT"].get().strip())
            enable_recycle = ntuser_filled

            if enable_recycle:
                for widget in self.row_widgets["$Recycle.Bin"]:
                    widget.configure(state="normal" if enable_recycle else "disabled")
            else:
                self.file_vars["$Recycle.Bin"].set("")  # Clear it
                for widget in self.row_widgets["$Recycle.Bin"]:
                    widget.configure(state="disabled")
        except Exception:
            pass

    def browse_file(self, ext):
        if ext == '$Recycle.Bin':
            path = filedialog.askdirectory(initialdir="/", title="Open")
        else:
            path = filedialog.askopenfilename(filetypes=[(f"{ext.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if path:
            self.file_vars[ext].set(path)

    def get_selected_paths(self):
        return {ext: var.get() for ext, var in self.file_vars.items()}

    def on_submit(self):
        if self.callback:
            self.callback(self.get_selected_paths())
        self.cleanup()

    def on_cancel(self):
        self.cleanup()

    def cleanup(self):
        self.root.unbind('<Configure>')
        self.win.destroy()

    def sync_windows(self, event=None):
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            qw = self.win.winfo_width()
            qh = self.win.winfo_height()
            self.win.geometry("+%d+%d" % (x + w / 2 - qw / 2, y + h / 2 - qh / 2))
        except Exception:
            pass
