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


import io
import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

log = logging.getLogger(__name__)


class ThumbnailDataWindow(ttk.Frame):

    def __init__(self, parent, df, ico):
        super().__init__(parent)

        self.df = df

        self.ico = ico

        self.thumbnail_images = []

        self.configure_treeview_style()

        self.bind(
            "<<ThemeChanged>>",
            lambda event: self.configure_treeview_style()
        )

        self.create_widgets()
        self.populate_tree()

    def configure_treeview_style(self):
        style = ttk.Style()

        style.configure(
            "Thumbnail.Treeview",
            rowheight=140
        )

    def create_widgets(self):

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = ttk.Frame(self)
        frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(
            frame,
            relief="groove",
            padding=5
        )

        tree_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Remove the BLOB column and add an image column
        columns = [
            column
            for column in self.df.columns
            if column != "thumbnail"
        ]

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            style="Thumbnail.Treeview"
        )

        # Thumbnail column
        self.tree.heading(
            "#0",
            text="Thumbnail"
        )

        self.tree.column(
            "#0",
            width=150,
            minwidth=150,
            stretch=False,
            anchor="center"
        )

        # Data columns
        for column in columns:
            self.tree.heading(
                column,
                text=column,
                anchor="w"
            )

            self.tree.column(
                column,
                width=150,
                minwidth=100,
                stretch=False,
                anchor="w"
            )

        # Scrollbars
        y_scroll = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.tree.yview
        )

        x_scroll = ttk.Scrollbar(
            tree_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        export_button = ttk.Button(
            frame,
            text="Export All Images",
            command=self.export_all_images
        )

        export_button.grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.tree.bind(
            "<Double-Button-1>",
            self.on_row_double_click
        )

    def populate_tree(self):

        for _, row in self.df.iterrows():

            thumbnail = row["thumbnail"]

            photo = None

            if isinstance(thumbnail, bytes):

                try:
                    image = Image.open(
                        io.BytesIO(thumbnail)
                    )

                    # Resize for the Treeview
                    image.thumbnail(
                        (128, 128),
                        Image.Resampling.LANCZOS
                    )

                    photo = ImageTk.PhotoImage(image)

                    # Keep reference alive
                    self.thumbnail_images.append(photo)

                except Exception:
                    photo = None

            # Everything except the BLOB
            values = []

            for column in self.df.columns:

                if column == "thumbnail":
                    continue

                value = row[column]

                if pd.isna(value):
                    value = ""

                elif isinstance(value, bytes):
                    value = value.hex()

                values.append(value)

            self.tree.insert(
                "",
                "end",
                image=photo,
                values=values,
                tags=(str(row.name),)
            )

    def on_row_double_click(self, event):

        item_id = self.tree.identify_row(event.y)

        if not item_id:
            return

        # Get the DataFrame index stored on the Treeview item
        item_index = self.tree.item(item_id, "tags")

        if not item_index:
            return

        df_index = item_index[0]

        row = self.df.loc[int(df_index)]

        thumbnail = row.get("thumbnail")

        if not isinstance(thumbnail, bytes):
            return

        try:
            image = Image.open(
                io.BytesIO(thumbnail)
            )

            # Actual dimensions contained in the BLOB
            width, height = image.size

            self.show_image_popup(
                image,
                width,
                height
            )

        except Exception as e:
            log.warning(f"Unable to open thumbnail: {e}")

    def show_image_popup(self, image, width, height):

        popup = tk.Toplevel(self)

        popup.title(
            f"Thumbnail - {width}x{height}"
        )

        popup.iconbitmap(self.ico)

        popup.geometry("800x600")

        # -------------------------------------------------
        # Main bordered frame
        # -------------------------------------------------

        o_main_frame = ttk.Frame(popup)

        o_main_frame.pack(
            fill="both",
            expand=True
        )

        main_frame = ttk.Frame(
            o_main_frame,
            relief="groove",
            padding=5
        )

        main_frame.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Keep original image
        original_image = image.copy()

        # Zoom state
        zoom = 1.0

        # Keep PhotoImage alive
        popup.photo = None

        # -------------------------------------------------
        # Image frame
        # -------------------------------------------------

        o_image_frame = ttk.Frame(
            main_frame,
            relief="groove",
            padding=3
        )

        o_image_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        image_frame = ttk.Frame(
            o_image_frame
        )

        image_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        o_image_frame.columnconfigure(0, weight=1)
        o_image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)

        # -------------------------------------------------
        # Canvas
        # -------------------------------------------------

        canvas = tk.Canvas(
            image_frame,
            highlightthickness=0,
            borderwidth=0
        )

        canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        def update_canvas_theme(event=None):

            style = ttk.Style()

            background = style.lookup(
                "TFrame",
                "background"
            )

            canvas.configure(
                background=background
            )

        # Set initial background
        update_canvas_theme()

        # Update when theme changes
        popup.bind(
            "<<ThemeChanged>>",
            update_canvas_theme
        )

        # -------------------------------------------------
        # Scrollbars
        # -------------------------------------------------

        x_scroll = ttk.Scrollbar(
            image_frame,
            orient="horizontal",
            command=canvas.xview
        )

        y_scroll = ttk.Scrollbar(
            image_frame,
            orient="vertical",
            command=canvas.yview
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        canvas.configure(
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set
        )

        # -------------------------------------------------
        # Image
        # -------------------------------------------------

        image_id = None

        def update_image():

            nonlocal zoom
            nonlocal image_id

            new_width = max(
                1,
                int(original_image.width * zoom)
            )

            new_height = max(
                1,
                int(original_image.height * zoom)
            )

            resized = original_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            photo = ImageTk.PhotoImage(
                resized
            )

            popup.photo = photo

            canvas.delete("all")

            image_id = canvas.create_image(
                0,
                0,
                image=photo,
                anchor="nw"
            )

            canvas.configure(
                scrollregion=(
                    0,
                    0,
                    new_width,
                    new_height
                )
            )

            zoom_label.configure(
                text=f"{int(zoom * 100)}%"
            )

            # Center image if it is smaller than the canvas
            center_image()

        # -------------------------------------------------
        # Center image
        # -------------------------------------------------

        def center_image():

            if image_id is None:
                return

            canvas.update_idletasks()

            bbox = canvas.bbox(image_id)

            if not bbox:
                return

            image_width = bbox[2] - bbox[0]
            image_height = bbox[3] - bbox[1]

            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Center horizontally if image is smaller
            if image_width < canvas_width:
                x = (canvas_width - image_width) // 2

                canvas.coords(
                    image_id,
                    x,
                    canvas.coords(image_id)[1]
                )

            # Center vertically if image is smaller
            if image_height < canvas_height:
                y = (canvas_height - image_height) // 2

                canvas.coords(
                    image_id,
                    canvas.coords(image_id)[0],
                    y
                )

        # -------------------------------------------------
        # Zoom
        # -------------------------------------------------

        def zoom_in():

            nonlocal zoom

            zoom *= 1.25

            update_image()

        def zoom_out():

            nonlocal zoom

            zoom /= 1.25

            zoom = max(
                zoom,
                0.1
            )

            update_image()

        def zoom_reset():

            nonlocal zoom

            zoom = 1.0

            update_image()

        # -------------------------------------------------
        # Pan with left mouse button
        # -------------------------------------------------

        def pan_start(event):

            canvas.scan_mark(
                event.x,
                event.y
            )

        def pan_move(event):

            canvas.scan_dragto(
                event.x,
                event.y,
                gain=1
            )

        canvas.bind(
            "<ButtonPress-1>",
            pan_start
        )

        canvas.bind(
            "<B1-Motion>",
            pan_move
        )

        # -------------------------------------------------
        # Mouse wheel zoom
        # -------------------------------------------------

        def mouse_wheel(event):

            if event.delta > 0:
                zoom_in()
            else:
                zoom_out()

        canvas.bind(
            "<MouseWheel>",
            mouse_wheel
        )

        # -------------------------------------------------
        # Zoom controls
        # -------------------------------------------------

        controls = ttk.Frame(
            main_frame
        )

        controls.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(5, 0)
        )

        ttk.Button(
            controls,
            text="−",
            width=4,
            command=zoom_out
        ).pack(
            side="left"
        )

        ttk.Button(
            controls,
            text="+",
            width=4,
            command=zoom_in
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            controls,
            text="100%",
            command=zoom_reset
        ).pack(
            side="left"
        )

        zoom_label = ttk.Label(
            controls,
            text="100%"
        )

        zoom_label.pack(
            side="left",
            padx=10
        )

        sg = ttk.Sizegrip(controls)

        sg.pack(
            side="right"
        )

        # -------------------------------------------------
        # Keyboard shortcuts
        # -------------------------------------------------

        popup.bind(
            "+",
            lambda event: zoom_in()
        )

        popup.bind(
            "=",
            lambda event: zoom_in()
        )

        popup.bind(
            "-",
            lambda event: zoom_out()
        )

        popup.bind(
            "0",
            lambda event: zoom_reset()
        )

        # -------------------------------------------------
        # Re-center when popup is resized
        # -------------------------------------------------

        canvas.bind(
            "<Configure>",
            lambda event: center_image()
        )

        # -------------------------------------------------
        # Initial image
        # -------------------------------------------------

        update_image()

        popup.focus_set()

    def export_all_images(self):

        folder = filedialog.askdirectory(
            parent=self,
            title="Select Export Folder"
        )

        if not folder:
            return

        exported = 0
        failed = 0

        for index, row in self.df.iterrows():

            thumbnail = row.get("thumbnail")

            if not isinstance(thumbnail, bytes):
                failed += 1
                continue

            try:
                image = Image.open(
                    io.BytesIO(thumbnail)
                )

                # Get a useful filename
                file_id = f'thumbnail_{index}_{row.get("driveItemId")}'

                # Remove characters that Windows doesn't allow
                invalid_chars = '<>:"/\\|?*'

                for char in invalid_chars:
                    file_id = file_id.replace(char, "_")

                extension = image.format.lower()

                output_path = os.path.join(
                    folder,
                    f"{file_id}.{extension}"
                )

                image.save(output_path)

                exported += 1

            except Exception as e:
                log.error(
                    f"Unable to export thumbnail {index}: {e}"
                )
                failed += 1

        messagebox.showinfo(
            "Export Complete",
            f"Exported: {exported}\n"
            f"Failed: {failed}",
            parent=self
        )
