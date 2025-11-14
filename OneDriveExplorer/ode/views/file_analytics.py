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
from datetime import datetime
import pandas as pd
from pandastable import Table
import logging
from collections import Counter
import os

log = logging.getLogger(__name__)


class FileAnalyticsFrame(ttk.Frame):
    """
    File Analytics - Analyzes file sizes, types, access patterns, and usage statistics.
    """

    def __init__(self, master, cache_data, fileusage_data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cache_data = cache_data
        self.fileusage_data = fileusage_data

        self.setup_ui()
        self.analyze_files()

    def setup_ui(self):
        """Create the UI components"""
        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")

        # Tab 2: Largest Files
        self.largest_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.largest_frame, text="Largest Files")

        # Tab 3: File Types
        self.types_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.types_frame, text="File Types")

        # Tab 4: Recent Files
        self.recent_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recent_frame, text="Recent Files")

        # Tab 5: Quick Access
        self.quick_access_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quick_access_frame, text="Quick Access")

        # Tab 6: Recommended Files
        self.recommended_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recommended_frame, text="Recommended")

        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        self.status_label = ttk.Label(self.status_frame, text="Analyzing files...")
        self.status_label.pack(side=tk.LEFT)

        # Export button
        export_btn = ttk.Button(self.status_frame, text="Export Report (CSV)",
                               command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=5)

    def parse_size(self, size_str):
        """Convert size string (e.g., '1,234 KB') to integer KB"""
        try:
            if isinstance(size_str, str) and 'KB' in size_str:
                return int(size_str.replace('KB', '').replace(',', '').strip())
            return 0
        except:
            return 0

    def format_size(self, kb):
        """Format KB size to human readable"""
        if kb >= 1024 * 1024:
            return f"{kb / (1024 * 1024):.2f} GB"
        elif kb >= 1024:
            return f"{kb / 1024:.2f} MB"
        else:
            return f"{kb} KB"

    def get_file_extension(self, filename):
        """Extract file extension"""
        if isinstance(filename, str) and '.' in filename:
            return filename.rsplit('.', 1)[-1].lower()
        return 'no extension'

    def analyze_files(self):
        """Analyze file data"""
        try:
            files_list = []
            total_size_kb = 0
            extension_counts = Counter()
            extension_sizes = {}

            if self.cache_data:
                for item_id, item_data in self.cache_data.items():
                    if not isinstance(item_data, dict):
                        continue

                    if item_data.get('Type') == 'File':
                        name = item_data.get('Name', 'Unknown')
                        path = item_data.get('Path', '')
                        size_str = item_data.get('size', '0 KB')
                        size_kb = self.parse_size(size_str)
                        last_change = item_data.get('lastChange', '')
                        extension = self.get_file_extension(name)

                        files_list.append({
                            'Name': name,
                            'Path': path,
                            'Size': size_str,
                            'SizeKB': size_kb,
                            'Extension': extension,
                            'LastChange': last_change,
                            'FileStatus': item_data.get('fileStatus', 0),
                            'SharedItem': item_data.get('sharedItem', 0)
                        })

                        total_size_kb += size_kb
                        extension_counts[extension] += 1

                        # Track size by extension
                        if extension not in extension_sizes:
                            extension_sizes[extension] = 0
                        extension_sizes[extension] += size_kb

            # Create DataFrames
            self.files_df = pd.DataFrame(files_list)

            if not self.files_df.empty:
                # Sort by size for largest files
                self.largest_files_df = self.files_df.nlargest(100, 'SizeKB')[
                    ['Name', 'Path', 'Size', 'Extension', 'LastChange']
                ]

                # Sort by last change for recent files
                self.files_df['LastChange_dt'] = pd.to_datetime(self.files_df['LastChange'], errors='coerce')
                self.recent_files_df = self.files_df.nlargest(100, 'LastChange_dt', keep='first')[
                    ['Name', 'Path', 'Size', 'Extension', 'LastChange']
                ]

                # File type statistics
                type_stats = []
                for ext, count in extension_counts.most_common(50):
                    type_stats.append({
                        'Extension': ext,
                        'Count': count,
                        'TotalSize': self.format_size(extension_sizes[ext]),
                        'TotalSizeKB': extension_sizes[ext],
                        'AvgSize': self.format_size(extension_sizes[ext] // count if count > 0 else 0)
                    })
                self.file_types_df = pd.DataFrame(type_stats)
            else:
                self.largest_files_df = pd.DataFrame()
                self.recent_files_df = pd.DataFrame()
                self.file_types_df = pd.DataFrame()

            # Statistics
            self.stats = {
                'total_files': len(files_list),
                'total_size_kb': total_size_kb,
                'total_size_formatted': self.format_size(total_size_kb),
                'avg_file_size_kb': total_size_kb // len(files_list) if len(files_list) > 0 else 0,
                'largest_file_kb': max([f['SizeKB'] for f in files_list]) if files_list else 0,
                'unique_extensions': len(extension_counts),
                'most_common_extension': extension_counts.most_common(1)[0] if extension_counts else ('N/A', 0)
            }

            # Populate tabs
            self.populate_overview()
            self.populate_largest()
            self.populate_types()
            self.populate_recent()
            self.populate_quick_access()
            self.populate_recommended()

            self.status_label.config(text=f"Analysis complete - {self.stats['total_files']} files, "
                                         f"Total size: {self.stats['total_size_formatted']}")

        except Exception as e:
            log.error(f"Error analyzing files: {e}")
            self.status_label.config(text=f"Error: {e}")

    def populate_overview(self):
        """Populate overview tab"""
        for widget in self.overview_frame.winfo_children():
            widget.destroy()

        # Create scrollable canvas
        canvas = tk.Canvas(self.overview_frame)
        scrollbar = ttk.Scrollbar(self.overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        title = ttk.Label(scrollable_frame, text="File Analytics Overview",
                         font=('Arial', 14, 'bold'))
        title.pack(pady=10)

        # Summary statistics
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Storage Statistics", padding=15)
        summary_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_data = [
            ("Total Files:", self.stats['total_files']),
            ("Total Storage:", self.stats['total_size_formatted']),
            ("Average File Size:", self.format_size(self.stats['avg_file_size_kb'])),
            ("Largest File:", self.format_size(self.stats['largest_file_kb'])),
            ("Unique File Types:", self.stats['unique_extensions']),
            ("Most Common Type:", f".{self.stats['most_common_extension'][0]} ({self.stats['most_common_extension'][1]} files)")
        ]

        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(summary_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=col, sticky='w', padx=10, pady=5)
            ttk.Label(summary_frame, text=str(value), font=('Arial', 10)).grid(
                row=row, column=col+1, sticky='w', padx=(0, 20), pady=5)

        # Top file types by count
        if not self.file_types_df.empty:
            types_frame = ttk.LabelFrame(scrollable_frame, text="Top 10 File Types (by count)", padding=15)
            types_frame.pack(fill=tk.X, padx=20, pady=10)

            for i, row in self.file_types_df.head(10).iterrows():
                row_frame = ttk.Frame(types_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=f".{row['Extension']}", font=('Arial', 9, 'bold'),
                         width=15).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"{row['Count']} files",
                         font=('Arial', 9), width=15).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"Total: {row['TotalSize']}",
                         font=('Arial', 9), width=20).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"Avg: {row['AvgSize']}",
                         font=('Arial', 9)).pack(side=tk.LEFT)

        # Top file types by size
        if not self.file_types_df.empty:
            size_types_frame = ttk.LabelFrame(scrollable_frame, text="Top 10 File Types (by total size)", padding=15)
            size_types_frame.pack(fill=tk.X, padx=20, pady=10)

            top_by_size = self.file_types_df.nlargest(10, 'TotalSizeKB')
            for i, row in top_by_size.iterrows():
                row_frame = ttk.Frame(size_types_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=f".{row['Extension']}", font=('Arial', 9, 'bold'),
                         width=15).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"Total: {row['TotalSize']}",
                         font=('Arial', 9), width=20).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"{row['Count']} files",
                         font=('Arial', 9), width=15).pack(side=tk.LEFT)

                # Percentage of total
                pct = (row['TotalSizeKB'] / max(self.stats['total_size_kb'], 1)) * 100
                ttk.Label(row_frame, text=f"({pct:.1f}% of total)",
                         font=('Arial', 9), foreground='blue').pack(side=tk.LEFT)

    def populate_largest(self):
        """Populate largest files tab"""
        for widget in self.largest_frame.winfo_children():
            widget.destroy()

        if not self.largest_files_df.empty:
            table = Table(self.largest_frame, dataframe=self.largest_files_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.largest_frame, text="No file data available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_types(self):
        """Populate file types tab"""
        for widget in self.types_frame.winfo_children():
            widget.destroy()

        if not self.file_types_df.empty:
            # Drop the TotalSizeKB column for display
            display_df = self.file_types_df[['Extension', 'Count', 'TotalSize', 'AvgSize']]
            table = Table(self.types_frame, dataframe=display_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.types_frame, text="No file type data available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_recent(self):
        """Populate recent files tab"""
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        if not self.recent_files_df.empty:
            table = Table(self.recent_frame, dataframe=self.recent_files_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.recent_frame, text="No recent file data available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_quick_access(self):
        """Populate quick access files tab"""
        for widget in self.quick_access_frame.winfo_children():
            widget.destroy()

        # Check if we have FileUsageSync data
        if self.fileusage_data and hasattr(self.fileusage_data, 'qa_data'):
            if not self.fileusage_data.qa_data.empty:
                table = Table(self.quick_access_frame, dataframe=self.fileusage_data.qa_data,
                            showtoolbar=True, showstatusbar=True)
                table.show()
            else:
                ttk.Label(self.quick_access_frame,
                         text="No quick access data available from FileUsageSync.db",
                         font=('Arial', 12)).pack(pady=20)
        else:
            ttk.Label(self.quick_access_frame,
                     text="FileUsageSync.db not loaded - no quick access data available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_recommended(self):
        """Populate recommended files tab"""
        for widget in self.recommended_frame.winfo_children():
            widget.destroy()

        # Check if we have FileUsageSync data
        if self.fileusage_data and hasattr(self.fileusage_data, 'rf_data'):
            if not self.fileusage_data.rf_data.empty:
                table = Table(self.recommended_frame, dataframe=self.fileusage_data.rf_data,
                            showtoolbar=True, showstatusbar=True)
                table.show()
            else:
                ttk.Label(self.recommended_frame,
                         text="No recommended files data available from FileUsageSync.db",
                         font=('Arial', 12)).pack(pady=20)
        else:
            ttk.Label(self.recommended_frame,
                     text="FileUsageSync.db not loaded - no recommended files data available",
                     font=('Arial', 12)).pack(pady=20)

    def export_report(self):
        """Export file analytics report"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="file_analytics_report.csv"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("OneDrive File Analytics Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write("=== SUMMARY STATISTICS ===\n")
                    f.write(f"Total Files: {self.stats['total_files']}\n")
                    f.write(f"Total Storage: {self.stats['total_size_formatted']}\n")
                    f.write(f"Average File Size: {self.format_size(self.stats['avg_file_size_kb'])}\n")
                    f.write(f"Largest File: {self.format_size(self.stats['largest_file_kb'])}\n")
                    f.write(f"Unique File Types: {self.stats['unique_extensions']}\n\n")

                    if not self.largest_files_df.empty:
                        f.write("=== TOP 100 LARGEST FILES ===\n")
                        self.largest_files_df.to_csv(f, index=False)
                        f.write("\n")

                    if not self.file_types_df.empty:
                        f.write("=== FILE TYPE STATISTICS ===\n")
                        self.file_types_df[['Extension', 'Count', 'TotalSize', 'AvgSize']].to_csv(f, index=False)

                self.status_label.config(text=f"Report exported to {file_path}")
                log.info(f"File analytics report exported to {file_path}")

        except Exception as e:
            log.error(f"Error exporting report: {e}")
            self.status_label.config(text=f"Export error: {e}")
