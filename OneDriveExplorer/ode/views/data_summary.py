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
from datetime import datetime
import pandas as pd
import logging

log = logging.getLogger(__name__)


class DataSummaryFrame(ttk.Frame):
    """
    Data Summary Dashboard - Shows what data was loaded and provides an overview
    of the OneDrive analysis results.
    """

    def __init__(self, master, cache_data, rbin_df, df_scope, account, data_sources=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cache_data = cache_data
        self.rbin_df = rbin_df
        self.df_scope = df_scope
        self.account = account
        self.data_sources = data_sources or {}

        self.setup_ui()
        self.populate_summary()

    def setup_ui(self):
        """Create the UI components"""
        # Create a canvas with scrollbar for the entire summary
        canvas = tk.Canvas(self, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=10)

        title_label = ttk.Label(title_frame, text="OneDrive Data Summary Report",
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)

        timestamp_label = ttk.Label(title_frame,
                                    text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                    font=('Arial', 10))
        timestamp_label.pack(side=tk.RIGHT)

        # Create sections
        self.create_data_sources_section()
        self.create_account_section()
        self.create_statistics_section()
        self.create_completeness_section()

    def create_section(self, title, icon=""):
        """Create a collapsible section frame"""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=f"{icon} {title}",
                                       padding=15)
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        return section_frame

    def create_data_sources_section(self):
        """Create Data Sources section"""
        section = self.create_section("Data Sources Loaded", "📁")

        # Create table-like layout
        headers_frame = ttk.Frame(section)
        headers_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(headers_frame, text="Data Source", font=('Arial', 10, 'bold'),
                 width=30).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(headers_frame, text="Status", font=('Arial', 10, 'bold'),
                 width=15).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(headers_frame, text="Details", font=('Arial', 10, 'bold'),
                 width=40).grid(row=0, column=2, sticky='w', padx=5)

        # Separator
        ttk.Separator(section, orient='horizontal').pack(fill=tk.X, pady=5)

        # Data sources content (will be populated later)
        self.data_sources_content = ttk.Frame(section)
        self.data_sources_content.pack(fill=tk.X)

    def create_account_section(self):
        """Create Account Information section"""
        section = self.create_section("Account Information", "👤")
        self.account_content = ttk.Frame(section)
        self.account_content.pack(fill=tk.X)

    def create_statistics_section(self):
        """Create Statistics section"""
        section = self.create_section("Data Statistics", "📊")
        self.stats_content = ttk.Frame(section)
        self.stats_content.pack(fill=tk.X)

    def create_completeness_section(self):
        """Create Data Completeness section"""
        section = self.create_section("Data Completeness Indicators", "✓")
        self.completeness_content = ttk.Frame(section)
        self.completeness_content.pack(fill=tk.X)

    def add_data_source_row(self, source_name, status, details, row):
        """Add a data source row"""
        status_color = "green" if status == "✓ Loaded" else "red"
        status_icon = "✓" if status == "✓ Loaded" else "✗"

        ttk.Label(self.data_sources_content, text=source_name,
                 font=('Arial', 9)).grid(row=row, column=0, sticky='w', padx=5, pady=3)

        status_label = ttk.Label(self.data_sources_content, text=f"{status_icon} {status.replace('✓ ', '').replace('✗ ', '')}",
                                font=('Arial', 9))
        status_label.grid(row=row, column=1, sticky='w', padx=5, pady=3)

        ttk.Label(self.data_sources_content, text=details,
                 font=('Arial', 9)).grid(row=row, column=2, sticky='w', padx=5, pady=3)

    def populate_summary(self):
        """Populate the summary with actual data"""
        try:
            # Data Sources
            row = 0

            # Check what data sources were loaded
            sources_info = [
                ("SyncEngineDatabase.db", self.data_sources.get('sync_engine', False),
                 "Main OneDrive sync database"),
                ("SafeDelete.db", self.data_sources.get('safe_delete', False),
                 "Deleted files tracking"),
                ("DAT File", self.data_sources.get('dat_file', False),
                 "OneDrive settings and metadata"),
                ("FileUsageSync.db", self.data_sources.get('file_usage', False),
                 "File usage and collaboration data"),
                ("ODL Logs", self.data_sources.get('odl_logs', False),
                 "OneDrive debug logs"),
                ("Registry Hive", self.data_sources.get('registry', False),
                 "Windows registry data"),
                ("Recycle Bin", not self.rbin_df.empty,
                 f"{len(self.rbin_df)} deleted items" if not self.rbin_df.empty else "No data")
            ]

            for source_name, loaded, details in sources_info:
                status = "✓ Loaded" if loaded else "✗ Not Loaded"
                self.add_data_source_row(source_name, status, details, row)
                row += 1

            # Account Information
            if self.account:
                ttk.Label(self.account_content, text=f"Account: {self.account}",
                         font=('Arial', 11, 'bold')).pack(anchor='w', pady=3)

            if not self.df_scope.empty:
                for _, scope in self.df_scope.iterrows():
                    scope_id = scope.get('scopeID', 'Unknown')
                    scope_name = scope.get('Name', 'Unknown')
                    ttk.Label(self.account_content, text=f"Scope: {scope_name} (ID: {scope_id})",
                             font=('Arial', 10)).pack(anchor='w', pady=2, padx=10)

            # Statistics
            stats_grid = ttk.Frame(self.stats_content)
            stats_grid.pack(fill=tk.X)

            # Count files and folders
            total_items = 0
            total_files = 0
            total_folders = 0
            total_size = 0
            hydrated_files = 0
            shared_items = 0

            if self.cache_data:
                for item_id, item_data in self.cache_data.items():
                    if not isinstance(item_data, dict):
                        continue

                    total_items += 1
                    item_type = item_data.get('Type', '')

                    if item_type == 'File':
                        total_files += 1

                        # Parse size (format: "123 KB")
                        size_str = item_data.get('size', '0 KB')
                        if isinstance(size_str, str) and 'KB' in size_str:
                            try:
                                size_kb = int(size_str.replace('KB', '').replace(',', '').strip())
                                total_size += size_kb
                            except:
                                pass

                        # Check if hydrated
                        if item_data.get('firstHydrationTime'):
                            hydrated_files += 1

                    elif item_type == 'Folder':
                        total_folders += 1

                    # Check if shared
                    if item_data.get('sharedItem', 0) != 0:
                        shared_items += 1

            deleted_items = len(self.rbin_df) if not self.rbin_df.empty else 0

            # Display statistics in grid
            stats_data = [
                ("Total Items:", total_items),
                ("Files:", total_files),
                ("Folders:", total_folders),
                ("Total Size:", f"{total_size:,} KB ({total_size / 1024:.2f} MB)"),
                ("Hydrated Files:", f"{hydrated_files} ({(hydrated_files/total_files*100 if total_files > 0 else 0):.1f}%)"),
                ("Shared Items:", shared_items),
                ("Deleted Items:", deleted_items)
            ]

            for i, (label, value) in enumerate(stats_data):
                row_num = i // 2
                col_num = (i % 2) * 2

                ttk.Label(stats_grid, text=label, font=('Arial', 10, 'bold')).grid(
                    row=row_num, column=col_num, sticky='w', padx=(10, 5), pady=5)
                ttk.Label(stats_grid, text=str(value), font=('Arial', 10)).grid(
                    row=row_num, column=col_num+1, sticky='w', padx=(0, 20), pady=5)

            # Data Completeness
            completeness_items = [
                ("Timestamp Data", self.check_timestamp_completeness(), "✓" if self.check_timestamp_completeness() else "⚠"),
                ("Deletion History", not self.rbin_df.empty, "✓" if not self.rbin_df.empty else "⚠"),
                ("Hydration Data", hydrated_files > 0, "✓" if hydrated_files > 0 else "⚠"),
                ("Sharing Information", shared_items > 0, "✓" if shared_items > 0 else "⚠")
            ]

            for i, (item, complete, icon) in enumerate(completeness_items):
                status_text = "Available" if complete else "Limited or Unavailable"
                color = "green" if complete else "orange"

                item_frame = ttk.Frame(self.completeness_content)
                item_frame.pack(fill=tk.X, pady=3)

                ttk.Label(item_frame, text=f"{icon} {item}:", font=('Arial', 10, 'bold')).pack(
                    side=tk.LEFT, padx=10)
                ttk.Label(item_frame, text=status_text, font=('Arial', 10)).pack(
                    side=tk.LEFT)

        except Exception as e:
            log.error(f"Error populating summary: {e}")

    def check_timestamp_completeness(self):
        """Check if timestamp data is available"""
        if not self.cache_data:
            return False

        # Check if at least some items have timestamp data
        has_timestamps = False
        for item_id, item_data in self.cache_data.items():
            if not isinstance(item_data, dict):
                continue

            if (item_data.get('lastChange') or
                item_data.get('diskCreationTime') or
                item_data.get('diskLastAccessTime')):
                has_timestamps = True
                break

        return has_timestamps
