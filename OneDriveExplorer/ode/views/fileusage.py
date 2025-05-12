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
from tkinter import ttk
from tkinter import font
import pandas as pd
import textwrap


def wrap(string, lenght=56):
    return '\n'.join(textwrap.wrap(string, lenght))


class AutoScrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._geom_manager = None
        self._geom_options = {}

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self._hide()
        else:
            self._show()
        super().set(lo, hi)

    def pack(self, **kwargs):
        self._geom_manager = "pack"
        self._geom_options = kwargs
        super().pack(**kwargs)

    def grid(self, **kwargs):
        self._geom_manager = "grid"
        self._geom_options = kwargs
        super().grid(**kwargs)

    def place(self, **kwargs):
        raise tk.TclError("AutoScrollbar does not support place()")

    def _hide(self):
        if self._geom_manager == "pack":
            super().pack_forget()
        elif self._geom_manager == "grid":
            super().grid_remove()

    def _show(self):
        if self._geom_manager == "pack":
            super().pack(**self._geom_options)
        elif self._geom_manager == "grid":
            super().grid(**self._geom_options)


class EmailHeaderFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        style = ttk.Style()
        bg = style.lookup('TFrame', 'background')
        fg = style.lookup('TFrame', 'foreground')
        if not fg:
            fg = 'black'

        # Subject Label
        self.subject_label = ttk.Label(self, text="Subject: ", font=("Arial", 12, "bold"))
        self.subject_data = ttk.Label(self, font=("Arial", 12, "bold"))
        self.subject_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        self.subject_data.grid(row=0, column=1, columnspan=2, sticky="w", pady=(5, 0))

        # ConversationId Label
        self.cId_label = ttk.Label(self, text="ConversationId: ", font=("Arial", 10, "bold"))
        self.cId_data = ttk.Label(self, font=("Arial", 11, "bold"))
        self.cId_label.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
        self.cId_data.grid(row=1, column=1, sticky="w", pady=(5, 0))

        # Sender Label
        self.sender_label = ttk.Label(self, text="From: ", font=("Arial", 10, "bold"))
        self.sender_data = ttk.Label(self, font=("Arial", 10, "bold"))
        self.sender_label.grid(row=2, column=0, sticky="w", padx=5)
        self.sender_data.grid(row=2, column=1, columnspan=2, sticky="w", pady=(5, 0))

        # "To" Recipients Label & Text Box
        self.to_label = ttk.Label(self, text="To:", font=("Arial", 10, "bold"))
        self.to_label.grid(row=3, column=0, sticky="nw", padx=5, pady=(5, 0))

        # Frame to contain text and scrollbar
        self.to_frame = ttk.Frame(self)
        self.to_frame.grid(row=3, column=1, sticky="w", padx=5, pady=(10, 0))

        # Create the scrollbar for "To" text
        self.to_scrollbar = AutoScrollbar(self.to_frame)

        # Create the "To" Text widget with yscrollcommand linked to the scrollbar
        self.to_text = tk.Text(
            self.to_frame,
            wrap="word",
            height=4,
            width=50,
            state="disabled",
            relief="flat",
            yscrollcommand=self.to_scrollbar.set
        )

        # Configure the scrollbar to scroll the "To" Text widget
        self.to_scrollbar.config(command=self.to_text.yview)

        self.to_text.configure(background=bg, foreground=fg)

        # Pack the "To" Text widget and scrollbar inside the frame
        self.to_text.pack(side="left", fill="both", expand=True)
        self.to_scrollbar.pack(side="right", fill="y")

        # Date Label
        self.date = ttk.Label(self, font=("Arial", 10, "bold"))
        self.date.grid(row=3, column=2, sticky="nw", padx=5, pady=(10, 0))

        # "Cc" Recipients Label & Text Box (Only Created if Cc Exists)
        self.cc_label = None
        self.cc_text = None
        self.cc_frame = None
        self.cc_scrollbar = None

        # File Info Label (Initially Hidden)
        self.file_info_label = ttk.Label(self, font=("Arial", 10, "italic"), padding=5, relief="solid")

    def update_email(self, email_data, file_data):
        """Updates the email header based on the selected email."""
        self.subject_data.config(text=f"{email_data.get('Subject', 'N/A')}")
        self.cId_data.config(text=f"{email_data.get('ConversationId', 'N/A')}")
        self.sender_data.config(text=f"{email_data.get('SharedByDisplayName', 'N/A')} <{email_data.get('SharedBySmtp', 'N/A')}>\rAADID: {email_data.get('SharedByAadId', 'N/A')}")

        # Update "To" Recipients
        to_recipients = [p["DisplayName"] for p in email_data.get("Participants", []) if p["Type"] == "To"]
        to_text = "; ".join(to_recipients)

        self.to_text.config(state="normal")
        self.to_text.delete("1.0", "end")
        self.to_text.insert("1.0", to_text)
        self.to_text.config(state="disabled")

        # Update date
        self.date.config(text=email_data.get('SharedByTime', 'N/A'))

        # Handle "Cc" Recipients
        cc_recipients = [p["DisplayName"] for p in email_data.get("Participants", []) if p["Type"] == "Cc"]

        if cc_recipients:
            if not self.cc_label:
                self.cc_label = ttk.Label(self, text="Cc:", font=("Arial", 10, "bold"))
                self.cc_label.grid(row=4, column=0, sticky="nw", padx=5, pady=(5, 0))

            if not self.cc_text:
                style = ttk.Style()
                bg = style.lookup('TFrame', 'background')
                fg = style.lookup('TFrame', 'foreground')
                if not fg:
                    fg = 'black'

                # Create a frame to hold cc_text and the scrollbar
                self.cc_frame = ttk.Frame(self)
                self.cc_frame.grid(row=4, column=1, sticky="w", padx=5, pady=(10, 0))

                # Create the scrollbar for "Cc" Text
                self.cc_scrollbar = AutoScrollbar(self.cc_frame)

                # Create the "Cc" Text widget with yscrollcommand linked to the scrollbar
                self.cc_text = tk.Text(
                    self.cc_frame,
                    wrap="word",
                    height=4,
                    width=50,
                    state="disabled",
                    relief="flat",
                    yscrollcommand=self.cc_scrollbar.set
                )

                # Configure the scrollbar to scroll the "Cc" Text widget
                self.cc_scrollbar.config(command=self.cc_text.yview)

                self.cc_text.configure(background=bg, foreground=fg)

                # Pack the "Cc" Text widget and scrollbar inside the frame
                self.cc_text.pack(side="left", fill="both", expand=True)

            cc_text = "; ".join(cc_recipients)
            self.cc_text.config(state="normal")
            self.cc_text.delete("1.0", "end")
            self.cc_text.insert("1.0", cc_text)
            self.cc_text.config(state="disabled")

            file_info_row = 5  # Place after Cc

        else:
            # Remove Cc if it exists but is now empty
            if self.cc_label:
                self.cc_label.destroy()
                self.cc_label = None

            if self.cc_text:
                self.cc_text.destroy()
                self.cc_text = None

            if self.cc_frame:
                self.cc_frame.destroy()
                self.cc_frame = None

            if self.cc_scrollbar:
                self.cc_scrollbar.destroy()
                self.cc_scrollbar = None

            file_info_row = 4  # Place after To if Cc doesn't exist

        # Update file info label
        file_name = file_data.get("file.FileName", "Unknown File")
        file_size = file_data.get("file.FileSize", "Unknown Size")
        self.file_info_label.config(text=f"{file_name}\r{file_size} bytes")

        # Move the label dynamically
        self.file_info_label.grid(row=file_info_row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 15))

    def update_textbox_theme(self, bg, fg):
        """Updates the background color of all stored text boxes and frames."""
        self.to_text.configure(background=bg, foreground=fg)
        try:
            self.cc_text.configure(background=bg, foreground=fg)
        except Exception:
            pass

    def clear_email(self):
        self.subject_data.config(text='')
        self.cId_data.config(text='')
        self.sender_data.config(text='')
        self.date.config(text='')
        self.file_info_label.grid_forget()
        self.to_text.config(state='normal')
        self.to_text.delete('1.0', tk.END)
        self.to_text.config(state='disable')
        try:
            self.cc_text.config(state='normal')
            self.cc_text.delete('1.0', tk.END)
            self.cc_text.config(state='disable')
        except Exception:
            pass


class MeetingHeaderFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.subject_data = ttk.Label(self, font=("Arial", 12, "bold"))

        self.srh = ttk.Separator(self, orient='horizontal')

        self.icaluid_label = ttk.Label(self, text="ICalUid: ", font=("Arial", 10, "bold"))
        self.icaluid_data = ttk.Label(self, font=("Arial", 10, "bold"))

        self.cId_label = ttk.Label(self, text="ConversationId: ", font=("Arial", 10, "bold"))
        self.cId_data = ttk.Label(self, font=("Arial", 10, "bold"))

        self.meetingStartTime_label = ttk.Label(self, text="MeetingStartTime: ", font=("Arial", 10, "bold"))
        self.meetingStartTime_data = ttk.Label(self, font=("Arial", 10, "bold"))

        self.isRecurring_label = ttk.Label(self, text="isRecurring: ", font=("Arial", 10, "bold"))
        self.isRecurring_data = ttk.Label(self, font=("Arial", 10, "bold"))

        self.srh2 = ttk.Separator(self, orient='horizontal')

        self.file_info_label = ttk.Label(self, font=("Arial", 10, "italic"), padding=5, relief="solid")

        self.file_info_frame = ttk.Frame(self)

        self.displayName_label = ttk.Label(self.file_info_frame, text="SharedByDisplayName: ", font=("Arial", 10, "bold"))
        self.displayName_data = ttk.Label(self.file_info_frame, font=("Arial", 10, "bold"))

        self.smtp_label = ttk.Label(self.file_info_frame, text="SharedBySmtp: ", font=("Arial", 10, "bold"))
        self.smtp_data = ttk.Label(self.file_info_frame, font=("Arial", 10, "bold"))

        self.aadId_label = ttk.Label(self.file_info_frame, text="SharedByAadid: ", font=("Arial", 10, "bold"))
        self.aadId_data = ttk.Label(self.file_info_frame, font=("Arial", 10, "bold"))

        self.time_label = ttk.Label(self.file_info_frame, text="SharedByTime: ", font=("Arial", 10, "bold"))
        self.time_data = ttk.Label(self.file_info_frame, font=("Arial", 10, "bold"))

        self.subject_data.grid(row=0, column=0, columnspan=4, sticky="nw", pady=(5, 0))
        self.srh.grid(row=1, column=0, columnspan=4, sticky="ew")
        self.icaluid_label.grid(row=2, column=0, sticky="w", padx=5, pady=(5, 0))
        self.icaluid_data.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        self.cId_label.grid(row=3, column=0, sticky="w", padx=5, pady=(5, 0))
        self.cId_data.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        self.meetingStartTime_label.grid(row=4, column=0, sticky="w", padx=5, pady=(5, 0))
        self.meetingStartTime_data.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        self.isRecurring_label.grid(row=5, column=0, sticky="w", padx=5, pady=(5, 0))
        self.isRecurring_data.grid(row=5, column=1, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        self.srh2.grid(row=6, column=0, columnspan=4, sticky="ew")
        self.file_info_frame.grid(row=7, column=2, sticky="w", pady=(10, 15))
        self.displayName_label.grid(row=0, column=0, sticky="w")
        self.displayName_data.grid(row=0, column=1, sticky="w")
        self.smtp_label.grid(row=1, column=0, sticky="w")
        self.smtp_data.grid(row=1, column=1, sticky="w")
        self.aadId_label.grid(row=2, column=0, sticky="w")
        self.aadId_data.grid(row=2, column=1, sticky="w")
        self.time_label.grid(row=3, column=0, sticky="w")
        self.time_data.grid(row=3, column=1, sticky="w")

    def update_meeting(self, meeting_data, file_data):
        self.subject_data.config(text=f"{meeting_data.get('Subject', 'N/A')}")
        self.icaluid_data.config(text=wrap(f"{meeting_data.get('ICalUid', 'N/A')}"))
        self.cId_data.config(text=f"{meeting_data.get('ConversationId', 'N/A')}")
        self.meetingStartTime_data.config(text=f"{meeting_data.get('MeetingStartTime', 'N/A')}")
        self.isRecurring_data.config(text=f"{meeting_data.get('isRecurring', 'N/A')}")

        # Update file info label
        file_name = file_data.get("file.FileName", "Unknown File")
        file_size = file_data.get("file.FileSize", "Unknown Size")
        self.file_info_label.config(text=f"{file_name}\r{file_size} bytes")

        # Move the label dynamically
        self.file_info_label.grid(row=7, column=0, columnspan=2, sticky="nw", padx=5, pady=(10, 15))

        self.displayName_data.config(text=f"{meeting_data.get('SharedByDisplayName', 'N/A')}")
        self.smtp_data.config(text=f"{meeting_data.get('SharedBySmtp', 'N/A')}")
        self.aadId_data.config(text=f"{meeting_data.get('SharedByAadId', 'N/A')}")
        self.time_data.config(text=f"{meeting_data.get('SharedByTime', 'N/A')}")

    def clear_meeting(self):
        self.subject_data.config(text='')
        self.icaluid_data.config(text='')
        self.cId_data.config(text='')
        self.meetingStartTime_data.config(text='')
        self.isRecurring_data.config(text='')
        self.file_info_label.grid_forget()
        self.displayName_data.config(text='')
        self.smtp_data.config(text='')
        self.aadId_data.config(text='')
        self.time_data.config(text='')


class TreeViewWidget(ttk.Frame):
    def __init__(self, parent, excluded_columns=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.excluded_columns = set(excluded_columns) if excluded_columns else set()
        self.style = ttk.Style()

        # Frame to hold the treeview and scrollbars
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create scrollbars
        self.v_scrollbar = AutoScrollbar(container, orient="vertical")
        self.h_scrollbar = AutoScrollbar(container, orient="horizontal")

        # TreeView Widget
        self.tree = ttk.Treeview(
            container,
            columns=("Value",),
            show="tree",
            style="File.Treeview",
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        self.tree.heading("#0", text="Column Name", anchor="w")
        self.tree.heading("Value", text="Value", anchor="w")
        self.tree.column("#0", anchor="w", width=370, stretch=False)
        self.tree.column("Value", anchor="w", width=250, stretch=False)

        # Link scrollbars to treeview
        self.v_scrollbar.config(command=self.tree.yview)
        self.h_scrollbar.config(command=self.tree.xview)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self._apply_treeview_style()

    def _apply_treeview_style(self):
        bg = self.style.lookup('TLabel', 'background')
        fg = self.style.lookup('TLabel', 'foreground') or 'black'

        self.style.configure("File.Treeview",
                             background=bg,
                             foreground=fg,
                             fieldbackground=bg)

        self.tree.tag_configure("highlight", background=bg, foreground=fg)

    def adjust_column_widths(self):
        style = ttk.Style()
        treeview_font = font.nametofont(style.lookup("Treeview", "font"))
        for col in self.tree["columns"]:
            max_width = treeview_font.measure(col)

            def recurse_items(item=""):
                nonlocal max_width
                for child in self.tree.get_children(item):
                    value = self.tree.set(child, col)
                    max_width = max(max_width, treeview_font.measure(value))
                    recurse_items(child)

            recurse_items()
            self.tree.column(col, width=max_width + 10)

    def set_data(self, row_data):
        """Update the tree with new data from a single row."""
        self.tree.delete(*self.tree.get_children())  # Clear existing data
        nested_data = self.build_nested_dict(row_data)
        root_node = self.tree.insert("", "end", text="Root", values=(""), tags=("highlight",))  # Root placeholder
        self.insert_tree(root_node, nested_data)

    def build_nested_dict(self, row):
        """Convert a flat row dictionary to a nested dictionary while excluding certain columns."""
        nested = {}
        for key, value in row.items():
            if key in self.excluded_columns:
                continue

            parts = key.split(".")
            d = nested
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = value
        return nested

    def insert_tree(self, parent, data):
        """Recursively insert dictionary data into the TreeView."""
        for key, value in data.items():
            if isinstance(value, dict):
                node = self.tree.insert(parent, "end", text=key, values=(""), tags=("highlight",))  # Category node
                self.insert_tree(node, value)  # Recursively insert sub-levels
            else:
                self.tree.insert(parent, "end", text=key, values=(value,), tags=("highlight",))  # Leaf node

        self.adjust_column_widths()

    def clear(self):
        """Remove all items from the treeview."""
        self.tree.delete(*self.tree.get_children())
        self.tree.column("Value", width=250)

    def disable_selection(self, event):
        if len(self.tree.selection()) > 0:
            self.tree.selection_remove(self.tree.selection()[0])


class SPHeaderFrame(tk.PanedWindow):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, orient="vertical", *args, **kwargs)

        # Create the top pane that contains all the widgets
        self.top_pane = tk.Frame(self)
        self.bottom_pane = tk.Frame(self)  # Empty for now

        # Subject Label
        self.subject_data = ttk.Label(self.top_pane, font=("Arial", 12, "bold"))
        self.subject_data.pack(fill="x")

        # Frame to contain TreeView and scrollbar
        self.tree_frame = tk.Frame(self.top_pane)
        self.tree_frame.pack(fill="both", expand=True)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        # Scrollbar for TreeView
        self.tree_scrollbar = AutoScrollbar(self.tree_frame)

        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name",), show="headings", yscrollcommand=self.tree_scrollbar.set)
        self.tree.heading("Name", text="Name", anchor="w")
        self.tree.column("Name", anchor="w", stretch=True)

        # Link scrollbar to TreeView
        self.tree_scrollbar.config(command=self.tree.yview)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns")

        # Separator
        separator = ttk.Separator(self.tree_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, pady=(2, 0), sticky="ew")

        # Add other treeview but hide it initially
        self.o_file_treeview = TreeViewWidget(self.bottom_pane)
        self.o_file_treeview.pack(fill="both", expand=True)

        self.bottom_pane.grid_rowconfigure(0, weight=1)
        self.bottom_pane.grid_columnconfigure(0, weight=1)

        # Add the top pane with all widgets and an empty bottom pane
        self.add(self.top_pane)
        self.add(self.bottom_pane)  # Empty bottom pane

        # Adjust sash position to give more space to the top pane
        self.update_idletasks()
        self.sash_place(0, 0, 200)  # Adjust as needed

        self.o_file_treeview.tree.bind("<<TreeviewSelect>>", self.o_file_treeview.disable_selection)

    def build_tree(self, subject, file_name, index):
        self.subject_data.config(text=subject)
        self.tree.insert("", "end", values=(file_name, index))

    def clear_sp(self):
        self.tree.delete(*self.tree.get_children())


class FileUsageFrame(ttk.Frame):
    def __init__(self, master, data=None, email_data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.style = ttk.Style()
        self.bg = self.style.lookup('TFrame', 'background')
        self.bgf = self.style.lookup('TLabel', 'background')
        self.fg = self.style.lookup('TLabel', 'foreground')
        if not self.fg:
            self.fg = 'black'

        self.data = None  # Placeholder for meetings data
        self.email_data = None  # Placeholder for emails data
        self.tree_data = {}

        # Create a paned window
        self.paned_window = tk.PanedWindow(self, orient="horizontal")
        self.paned_window.config(background=self.bg, sashwidth=6)

        # Create two frames for the panes
        self.left_pane = ttk.Frame(self.paned_window, padding=5, relief="flat")
        self.middle_pane = ttk.Frame(self.paned_window, padding=5, relief="flat")  # Empty for now

        # Create frames
        self.right_pane = ttk.Frame(self, padding=5, relief="flat")
        self.bottom_pane = ttk.Frame(self, padding=5, relief="flat")

        # Create size grip
        self.sg = ttk.Sizegrip(self.bottom_pane)

        # Add frames to the paned window
        self.paned_window.add(self.left_pane, minsize=200, width=400)   # Meeting or Email List
        self.paned_window.add(self.middle_pane)  # Empty Space (for later use)

        # Grid placement
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        self.right_pane.grid(row=0, column=1, sticky="nsew")
        self.bottom_pane.grid(row=1, column=1, columnspan=2, sticky="se")
        self.sg.grid(row=0, column=0, sticky='se')

        # Configure grid expansion
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.middle_pane.grid_columnconfigure(0, weight=1)
        self.middle_pane.grid_rowconfigure(0, weight=1)

        # Initialize UI components
        self.create_meetings_list()
        self.create_events_list()
        self.create_emails_list()
        self.create_chats_list()
        self.create_notes_list()
        self.create_details_view()
        self.create_sp_list()

        self.email_header = EmailHeaderFrame(self.middle_pane)
        self.meeting_header = MeetingHeaderFrame(self.middle_pane)
        self.sp_header = SPHeaderFrame(self.middle_pane)
        self.sp_header.config(background=self.bg, sashwidth=6)
        self.sp_header.tree_frame.config(background=self.bg)
        self.file_treeview = TreeViewWidget(self.middle_pane)
        self.file_treeview.tree.bind("<<TreeviewSelect>>", self.file_treeview.disable_selection)
        self.bind("<<ThemeChanged>>", self.update_theme_colors)

    def create_meetings_list(self):
        """Create the treeview for meetings (left pane)."""
        self.meetings_tree = ttk.Treeview(self.left_pane, columns=("MeetingSubject",), show="headings")
        self.meetings_tree.heading("MeetingSubject", text="Meeting Subject")
        self.meetings_tree.column("MeetingSubject", width=200)

        # Add scrollbar
        self.meetings_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.meetings_tree.yview)
        self.meetings_tree.configure(yscrollcommand=self.meetings_scroll.set)

        # Pack the treeview and scrollbar
        self.meetings_tree.pack(side="left", fill="both", expand=True)
        self.meetings_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.meetings_tree.bind("<<TreeviewSelect>>", lambda event: [self.display_meeting_header(event), self.on_item_select(self.meetings_tree)])

    def create_events_list(self):
        """Create the treeview for emails (left pane)."""
        self.events_tree = ttk.Treeview(self.left_pane, columns=("EventSubject",), show="headings")
        self.events_tree.heading("EventSubject", text="Event Subject")
        self.events_tree.column("EventSubject", width=200)

        # Add scrollbar
        self.events_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=self.events_scroll.set)

        # Pack the treeview and scrollbar
        self.events_tree.pack(side="left", fill="both", expand=True)
        self.events_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.events_tree.bind("<<TreeviewSelect>>", lambda event: [self.display_event_header(event), self.on_item_select(self.events_tree)])

    def create_emails_list(self):
        """Create the treeview for emails (left pane)."""
        style = ttk.Style()
        self.emails_tree = ttk.Treeview(self.left_pane, columns=("EmailSubject","Date",), show="headings", style='Email.Treeview')
        self.emails_tree.heading("EmailSubject", text="Email Subject")
        self.emails_tree.column("EmailSubject", minwidth=200, width=200)
        self.emails_tree.column("Date", minwidth=90, width=90, stretch=False, anchor="e")
        style.configure('Email.Treeview', rowheight=40)

        # Add scrollbar
        self.emails_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.emails_tree.yview)
        self.emails_tree.configure(yscrollcommand=self.emails_scroll.set)

        # Pack the treeview and scrollbar
        self.emails_tree.pack(side="left", fill="both", expand=True)
        self.emails_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.emails_tree.bind("<<TreeviewSelect>>", self.display_email_header)

    def create_chats_list(self):
        """Create the treeview for emails (left pane)."""
        self.chats_tree = ttk.Treeview(self.left_pane, columns=("ChatSubject",), show="headings")
        self.chats_tree.heading("ChatSubject", text="Chat Subject")
        self.chats_tree.column("ChatSubject", width=200)

        # Add scrollbar
        self.chats_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.chats_tree.yview)
        self.chats_tree.configure(yscrollcommand=self.chats_scroll.set)

        # Pack the treeview and scrollbar
        self.chats_tree.pack(side="left", fill="both", expand=True)
        self.chats_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.chats_tree.bind("<<TreeviewSelect>>", lambda event: self.on_item_select(self.chats_tree))

    def create_notes_list(self):
        """Create the treeview for emails (left pane)."""
        self.notes_tree = ttk.Treeview(self.left_pane, columns=("NoteSubject",), show="headings")
        self.notes_tree.heading("NoteSubject", text="Note Subject")
        self.notes_tree.column("NoteSubject", width=200)

        # Add scrollbar
        self.notes_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=self.notes_scroll.set)

        # Pack the treeview and scrollbar
        self.notes_tree.pack(side="left", fill="both", expand=True)
        self.notes_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.notes_tree.bind("<<TreeviewSelect>>", lambda event: self.on_item_select(self.notes_tree))

    def create_sp_list(self):
        """Create the treeview for emails (left pane)."""
        self.files_tree = ttk.Treeview(self.left_pane, show="tree")

        # Add scrollbar
        self.files_scroll = ttk.Scrollbar(self.left_pane, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=self.files_scroll.set)

        # Pack the treeview and scrollbar
        self.files_tree.pack(side="left", fill="both", expand=True)
        self.files_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.files_tree.bind("<<TreeviewSelect>>", self.on_sp_select)

    def create_details_view(self):
        """Create the treeview for meeting/email details (right pane)."""
        self.sr = ttk.Separator(self.right_pane, orient='vertical')
        self.details_tree = ttk.Treeview(self.right_pane, columns=("Field", "Value"), show="tree")
        self.details_tree.heading("#0", text="")
        self.details_tree.heading("Field", text="Field")
        self.details_tree.heading("Value", text="Value")
        self.details_tree.column("#0", width=0, stretch=False)
        self.details_tree.column("Field", minwidth=75, width=75, stretch=False, anchor="w")
        self.details_tree.column("Value", minwidth=175, width=175, stretch=False, anchor="w")

        # Add scrollbar
        details_scroll = AutoScrollbar(self.right_pane)
        self.details_tree.configure(yscrollcommand=details_scroll.set)
        details_scroll.config(command=self.details_tree.yview)

        # Pack the treeview and scrollbar
        self.sr.pack(side="left", fill="y", padx=(0, 5))
        self.details_tree.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")

    def clear_details_tree(self):
        """Clear all items from the details treeview."""
        self.details_tree.delete(*self.details_tree.get_children())

    def set_data(self, data: pd.DataFrame):
        """Set and filter the meetings dataframe, then populate the meetings list."""
        self.data = data
        self.populate_list()

    def populate_list(self):
        """Populate the meetings treeview."""
        self.meetings_tree.delete(*self.meetings_tree.get_children())
        self.events_tree.delete(*self.events_tree.get_children())
        self.emails_tree.delete(*self.emails_tree.get_children())
        self.chats_tree.delete(*self.chats_tree.get_children())
        self.notes_tree.delete(*self.notes_tree.get_children())
        self.files_tree.delete(*self.files_tree.get_children())

        if self.data is None:
            return

        for index, row in self.data.iterrows():
            instances = row.get("file.AllExtensions.SharingHistory.Instances", [])

            if instances and not isinstance(instances, float):  # Ensure there are meetings
                for count, data in enumerate(instances):
                    unique_id = f"{index}_{count}"  # Ensure unique ID
                    has_sender = any(participant['Type'] == 'Sender' for participant in data['Participants'])
                    has_organizer = any(participant['Type'] == 'Organizer' for participant in data['Participants'])
                    if has_organizer:
                        self.events_tree.insert("", "end", values=(data["Subject"],), iid=unique_id)
                    elif data.get('MeetingSubject') is not None:
                        self.meetings_tree.insert("", "end", values=(data["Subject"],), iid=unique_id)
                    elif has_sender:
                        self.emails_tree.insert("", "end", values=(f'{data["SharedByDisplayName"]}\r{data["Subject"]}',f'{data["SharedByTime"][:10]}\r ',), iid=unique_id)
                    elif 'notes' in row.get("file.ItemProperties.Shared.TeamsMessageThreadId"):
                        if data["Subject"] == '':
                            text = data["SharedByDisplayName"]
                        else:
                            text = data["Subject"]
                        self.notes_tree.insert("", "end", values=(text,), iid=unique_id)
                    else:
                        chat_subject = self.get_chat_subject(data)
                        self.chats_tree.insert("", "end", values=(chat_subject,), iid=unique_id)
            else:
                parts = row.get("file.ItemProperties.SemanticProperties.ContainerName", "N/A").split(" - ", 1)
                team = parts[0].strip()
                sub = parts[1].strip() if len(parts) > 1 else None

                if team not in self.tree_data:
                    self.tree_data[team] = {"indexes": set(), "children": {}}  # Store team index & children

                if sub:
                    if sub not in self.tree_data[team]["children"]:
                        self.tree_data[team]["children"][sub] = set()
                    self.tree_data[team]["children"][sub].add(index)

                else:
                    self.tree_data[team]["indexes"].add(index)

        for parent, data in self.tree_data.items():
            team_indexes = data["indexes"]  # Get team indexes

            parent_id = self.files_tree.insert("", "end", text=parent, values=(team_indexes,))  # Parent node

            for child, child_indexes in sorted(data["children"].items()):
                self.files_tree.insert(parent_id, "end", text=child, values=(child_indexes,))  # Add child node

    def get_chat_subject(self, chat_data):
        """Return the chat subject or a comma-separated list of participants if subject is empty."""
        subject = chat_data.get("Subject", "").strip()

        if not subject:  # If subject is empty, use participants
            participants = [p["DisplayName"] for p in chat_data.get("Participants", [])]
            subject = ", ".join(participants)

        return subject

    def on_item_select(self, tree):
        """Shared logic for handling selection from a Treeview."""
        selected_item = tree.selection()
        if not selected_item or self.data is None:
            return

        row_index, instance_index = map(int, selected_item[0].split("_"))

        row = self.data.iloc[row_index]
        instances = row.get("file.AllExtensions.SharingHistory.Instances", [])

        self.file_treeview.set_data(row.drop("file.AllExtensions.SharingHistory.Instances"))

        if instances and 0 <= instance_index < len(instances):
            meeting = instances[instance_index]
            self.details_tree.delete(*self.details_tree.get_children())

            self.details_tree.insert("", "end", values=("", "Participants:"))
            for participant in meeting.get("Participants", []):
                self.details_tree.insert("", "end", values=(
                    participant.get("Type", "N/A"), 
                    participant.get("DisplayName", "N/A")
                ))

    def on_sp_select(self, event):
        """Populate the right Treeview when a meeting is selected."""
        self.sp_header.clear_sp()
        self.sp_header.o_file_treeview.clear()
        selected_item = self.files_tree.selection()
        if not selected_item or self.data is None:
            return

        values = self.files_tree.item(selected_item, 'values')
        text = self.files_tree.item(selected_item, 'text')
        indexes = set(map(int, values[0].strip('{}').split(', ')))
        for idx in indexes:
            file_name = self.data.iloc[idx].get("file.FileName")
            self.sp_header.build_tree(text, file_name, idx)

        self.sp_header.tree.bind("<<TreeviewSelect>>", self.on_teams_file_select)

    def on_teams_file_select(self, event):
        selected_item = self.sp_header.tree.selection()
        if not selected_item or self.data is None:
            return

        row_index = int(self.sp_header.tree.item(selected_item, 'values')[1])

        self.sp_header.o_file_treeview.set_data(self.data.iloc[row_index].drop("file.AllExtensions.SharingHistory.Instances"))

    def display_email_header(self, event):
        """Update email header frame when a meeting is selected."""
        selected_item = self.emails_tree.selection()
        if not selected_item:
            return
        email_id = selected_item[0]
        row_index, instance_index = map(int, email_id.split("_"))  # Extract numbers

        # Retrieve instances for the correct row
        instances = self.data.iloc[row_index].get("file.AllExtensions.SharingHistory.Instances", [])

        self.file_treeview.set_data(self.data.iloc[row_index].drop("file.AllExtensions.SharingHistory.Instances"))

        if instances and 0 <= instance_index < len(instances):
            email = instances[instance_index]  # Get the correct instance
            self.email_header.update_email(email, self.data.iloc[row_index])

    def display_meeting_header(self, event):
        selected_item = self.meetings_tree.selection()
        if not selected_item:
            return
        meeting_id = selected_item[0]
        row_index, instance_index = map(int, meeting_id.split("_"))  # Extract numbers

        # Retrieve instances for the correct row
        instances = self.data.iloc[row_index].get("file.AllExtensions.SharingHistory.Instances", [])

        self.file_treeview.set_data(self.data.iloc[row_index].drop("file.AllExtensions.SharingHistory.Instances"))

        if instances and 0 <= instance_index < len(instances):
            meeting = instances[instance_index]  # Get the correct instance
            self.meeting_header.update_meeting(meeting, self.data.iloc[row_index])

    def display_event_header(self, event):
        selected_item = self.events_tree.selection()
        if not selected_item:
            return
        meeting_id = selected_item[0]
        row_index, instance_index = map(int, meeting_id.split("_"))  # Extract numbers

        # Retrieve instances for the correct row
        instances = self.data.iloc[row_index].get("file.AllExtensions.SharingHistory.Instances", [])

        self.file_treeview.set_data(self.data.iloc[row_index].drop("file.AllExtensions.SharingHistory.Instances"))

        if instances and 0 <= instance_index < len(instances):
            meeting = instances[instance_index]  # Get the correct instance
            self.meeting_header.update_meeting(meeting, self.data.iloc[row_index])

    def show_list(self, tree, scroll, panes=("middle", "right"), show_header=False):
        """Show the specified treeview and hide all others."""

        # Ensure panes are removed before re-adding
        self.paned_window.forget(self.middle_pane)
        try:
            self.right_pane.grid_forget()
        except Exception:
            pass

        self.meeting_header.clear_meeting()
        self.email_header.clear_email()

        # Add specified panes
        if "middle" in panes:
            self.paned_window.add(self.middle_pane)
        if "right" in panes:
            self.right_pane.grid(row=0, column=1, sticky="nsew")

        # Pack the specified treeview and scroll
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Clear and reset other UI elements
        self.clear_details_tree()
        self.file_treeview.clear()

        if show_header == 'email':
            self.file_treeview.pack_forget()
            self.meeting_header.pack_forget()
            self.sp_header.pack_forget()
            self.email_header.pack(side="top", fill="both", expand=False)
            self.file_treeview.pack(side="top", fill="both", expand=True)
        elif show_header == 'meeting':
            self.file_treeview.pack_forget()
            self.email_header.pack_forget()
            self.sp_header.pack_forget()
            self.meeting_header.pack(side="top", fill="x", expand=False)
            self.file_treeview.pack(side="top", fill="both", expand=True)
        elif show_header == 'sp':
            self.file_treeview.pack_forget()
            self.meeting_header.pack_forget()
            self.email_header.pack_forget()
            self.sp_header.pack(side="top", fill="both", expand=True)
        else:
            self.email_header.pack_forget()
            self.meeting_header.pack_forget()
            self.sp_header.pack_forget()
            self.file_treeview.pack(fill="both", expand=True)

        # Hide all treeviews and their scrollbars except the selected one
        all_trees = [
            (self.meetings_tree, self.meetings_scroll),
            (self.events_tree, self.events_scroll),
            (self.emails_tree, self.emails_scroll),
            (self.chats_tree, self.chats_scroll),
            (self.notes_tree, self.notes_scroll),
            (self.files_tree, self.files_scroll),
        ]

        for t, s in all_trees:
            if t != tree:
                t.pack_forget()
                s.pack_forget()

    # Specific methods for each type of list
    def show_meetings_list(self):
        self.show_list(self.meetings_tree, self.meetings_scroll, panes=("middle", "right",), show_header='meeting')

    def show_events_list(self):
        self.show_list(self.events_tree, self.events_scroll, panes=("middle", "right",), show_header='meeting')

    def show_emails_list(self):
        self.show_list(self.emails_tree, self.emails_scroll, panes=("middle",), show_header='email')

    def show_chats_list(self):
        self.show_list(self.chats_tree, self.chats_scroll)

    def show_notes_list(self):
        self.show_list(self.notes_tree, self.notes_scroll)

    def show_sp_list(self):
        self.show_list(self.files_tree, self.files_scroll, panes=("middle",), show_header='sp')

    def update_theme_colors(self, event=None):
        self.style = ttk.Style()
        self.bg = self.style.lookup('TFrame', 'background')
        self.fg = self.style.lookup('TFrame', 'foreground') or "black"
        self.email_header.update_textbox_theme(self.bg, self.fg)
        self.paned_window.config(background=self.bg, sashwidth=6)
        self.sp_header.config(background=self.bg, sashwidth=6)
        self.sp_header.tree_frame.config(background=self.bg)
        self.sp_header.o_file_treeview._apply_treeview_style()
        self.style.configure('Email.Treeview', rowheight=40)
        self.file_treeview._apply_treeview_style()

        self._apply_label_theme(self)

    # below are fixes for when changing from breeze theme
    def _apply_label_theme(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Label):
                bg = child.cget('background')
                if str(bg) == '#eff0f1':
                    child.configure(background='', foreground='')
            else:
                self._apply_label_theme(child)
