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

log = logging.getLogger(__name__)


class SyncStatusDashboard(ttk.Frame):
    """
    Sync Status Dashboard - Analyzes OneDrive sync status including files not synced,
    sync errors, hydration status, and pin states.
    """

    def __init__(self, master, cache_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cache_data = cache_data

        # File status codes (from OneDrive)
        self.file_status_codes = {
            0: 'Unknown',
            1: 'Synced',
            2: 'Synced (Available)',
            3: 'Syncing',
            4: 'Sync Pending',
            5: 'Sync Error',
            6: 'Online Only (Not Synced)',
            7: 'Not Linked',
            8: 'Excluded',
            9: 'Pinned'
        }

        # Folder status codes
        self.folder_status_codes = {
            8: 'Synced',
            9: 'Synced',
            10: 'Not Synced',
            11: 'Not Linked',
            12: 'Unknown'
        }

        # Hydration types
        self.hydration_types = {
            'active': 'User initiated download',
            'passive': 'System/background download',
            '': 'Never downloaded'
        }

        # Pin states
        self.pin_states = {
            0: 'Unpinned',
            1: 'Pinned',
            2: 'Excluded from sync'
        }

        self.setup_ui()
        self.analyze_sync_status()

    def setup_ui(self):
        """Create the UI components"""
        # Create notebook for different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")

        # Tab 2: Not Synced Files
        self.not_synced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.not_synced_frame, text="Not Synced")

        # Tab 3: Sync Errors
        self.errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.errors_frame, text="Sync Errors")

        # Tab 4: Hydration Status
        self.hydration_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hydration_frame, text="Hydration Status")

        # Tab 5: Pinned Files
        self.pinned_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pinned_frame, text="Pinned Files")

        # Tab 6: File Status Breakdown
        self.status_breakdown_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_breakdown_frame, text="Status Breakdown")

        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        self.status_label = ttk.Label(self.status_frame, text="Analyzing sync status...")
        self.status_label.pack(side=tk.LEFT)

        # Export button
        export_btn = ttk.Button(self.status_frame, text="Export Report (CSV)",
                               command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=5)

    def analyze_sync_status(self):
        """Analyze sync status from cache data"""
        try:
            not_synced = []
            sync_errors = []
            hydrated = []
            not_hydrated = []
            pinned = []
            status_counts = {}

            if self.cache_data:
                for item_id, item_data in self.cache_data.items():
                    if not isinstance(item_data, dict):
                        continue

                    item_type = item_data.get('Type', '')
                    name = item_data.get('Name', 'Unknown')
                    path = item_data.get('Path', '')

                    # Analyze files
                    if item_type == 'File':
                        file_status = item_data.get('fileStatus', 0)
                        size = item_data.get('size', '0 KB')
                        last_change = item_data.get('lastChange', '')

                        # Track status counts
                        status_name = self.file_status_codes.get(file_status, f'Unknown ({file_status})')
                        status_counts[status_name] = status_counts.get(status_name, 0) + 1

                        # Not synced files (status 6 or 7)
                        if file_status in [6, 7]:
                            not_synced.append({
                                'Name': name,
                                'Path': path,
                                'Size': size,
                                'Status': status_name,
                                'LastChange': last_change
                            })

                        # Sync errors (status 5)
                        if file_status == 5:
                            sync_errors.append({
                                'Name': name,
                                'Path': path,
                                'Size': size,
                                'LastChange': last_change
                            })

                        # Hydration status
                        first_hydration = item_data.get('firstHydrationTime', '')
                        last_hydration = item_data.get('lastHydrationTime', '')
                        hydration_type = item_data.get('lastHydrationType', '')
                        hydration_count = item_data.get('hydrationCount', 0)

                        if first_hydration and first_hydration != '':
                            hydrated.append({
                                'Name': name,
                                'Path': path,
                                'Size': size,
                                'FirstHydration': first_hydration,
                                'LastHydration': last_hydration,
                                'HydrationType': hydration_type,
                                'HydrationCount': hydration_count
                            })
                        else:
                            not_hydrated.append({
                                'Name': name,
                                'Path': path,
                                'Size': size,
                                'Status': status_name
                            })

                        # Pinned files
                        pin_state = item_data.get('lastKnownPinState', '')
                        if pin_state and pin_state != '':
                            pin_state_int = int(pin_state) if str(pin_state).isdigit() else 0
                            if pin_state_int in [1, 2]:
                                pinned.append({
                                    'Name': name,
                                    'Path': path,
                                    'Size': size,
                                    'PinState': self.pin_states.get(pin_state_int, f'Unknown ({pin_state})'),
                                    'LastChange': last_change
                                })

                    # Analyze folders
                    elif item_type == 'Folder':
                        folder_status = item_data.get('folderStatus', 0)
                        status_name = self.folder_status_codes.get(folder_status, f'Unknown ({folder_status})')

                        # Track folder status
                        folder_key = f"Folder - {status_name}"
                        status_counts[folder_key] = status_counts.get(folder_key, 0) + 1

                        # Not synced folders (status 10 or 11)
                        if folder_status in [10, 11]:
                            not_synced.append({
                                'Name': name,
                                'Path': path,
                                'Size': 'N/A (Folder)',
                                'Status': status_name,
                                'LastChange': ''
                            })

            # Create DataFrames
            self.not_synced_df = pd.DataFrame(not_synced)
            self.sync_errors_df = pd.DataFrame(sync_errors)
            self.hydrated_df = pd.DataFrame(hydrated)
            self.not_hydrated_df = pd.DataFrame(not_hydrated)
            self.pinned_df = pd.DataFrame(pinned)
            self.status_counts = status_counts

            # Calculate statistics
            self.stats = {
                'total_files': sum(1 for k, v in self.cache_data.items() if isinstance(v, dict) and v.get('Type') == 'File'),
                'total_folders': sum(1 for k, v in self.cache_data.items() if isinstance(v, dict) and v.get('Type') == 'Folder'),
                'not_synced_count': len(not_synced),
                'sync_errors_count': len(sync_errors),
                'hydrated_count': len(hydrated),
                'not_hydrated_count': len(not_hydrated),
                'pinned_count': len(pinned)
            }

            # Populate all tabs
            self.populate_overview()
            self.populate_not_synced()
            self.populate_errors()
            self.populate_hydration()
            self.populate_pinned()
            self.populate_status_breakdown()

            self.status_label.config(text=f"Analysis complete - {self.stats['not_synced_count']} not synced, "
                                         f"{self.stats['sync_errors_count']} errors, "
                                         f"{self.stats['hydrated_count']} hydrated")

        except Exception as e:
            log.error(f"Error analyzing sync status: {e}")
            self.status_label.config(text=f"Error: {e}")

    def populate_overview(self):
        """Populate overview tab"""
        # Clear existing widgets
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
        title = ttk.Label(scrollable_frame, text="Sync Status Overview",
                         font=('Arial', 14, 'bold'))
        title.pack(pady=10)

        # Summary statistics
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Summary Statistics", padding=15)
        summary_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_data = [
            ("Total Files:", self.stats['total_files']),
            ("Total Folders:", self.stats['total_folders']),
            ("Not Synced Items:", f"{self.stats['not_synced_count']} ({self.stats['not_synced_count']/max(self.stats['total_files']+self.stats['total_folders'],1)*100:.1f}%)"),
            ("Sync Errors:", self.stats['sync_errors_count']),
            ("Hydrated Files:", f"{self.stats['hydrated_count']} ({self.stats['hydrated_count']/max(self.stats['total_files'],1)*100:.1f}%)"),
            ("Not Hydrated:", f"{self.stats['not_hydrated_count']} ({self.stats['not_hydrated_count']/max(self.stats['total_files'],1)*100:.1f}%)"),
            ("Pinned Files:", self.stats['pinned_count']),
        ]

        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(summary_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=col, sticky='w', padx=10, pady=5)
            ttk.Label(summary_frame, text=str(value), font=('Arial', 10)).grid(
                row=row, column=col+1, sticky='w', padx=(0, 20), pady=5)

        # Status breakdown visualization
        if self.status_counts:
            status_frame = ttk.LabelFrame(scrollable_frame, text="File Status Distribution", padding=15)
            status_frame.pack(fill=tk.X, padx=20, pady=10)

            # Sort by count
            sorted_statuses = sorted(self.status_counts.items(), key=lambda x: x[1], reverse=True)

            for status_name, count in sorted_statuses:
                row_frame = ttk.Frame(status_frame)
                row_frame.pack(fill=tk.X, pady=3)

                # Status name
                ttk.Label(row_frame, text=status_name, font=('Arial', 9, 'bold'),
                         width=30).pack(side=tk.LEFT)

                # Count
                ttk.Label(row_frame, text=f"{count} items",
                         font=('Arial', 9)).pack(side=tk.LEFT, padx=10)

                # Percentage bar (simple text-based)
                total = self.stats['total_files'] + self.stats['total_folders']
                percentage = (count / max(total, 1)) * 100
                bar_width = int(percentage / 2)  # Scale to fit
                bar = "█" * bar_width
                ttk.Label(row_frame, text=f"{bar} {percentage:.1f}%",
                         font=('Arial', 8), foreground='blue').pack(side=tk.LEFT)

        # Health indicator
        health_frame = ttk.LabelFrame(scrollable_frame, text="Sync Health", padding=15)
        health_frame.pack(fill=tk.X, padx=20, pady=10)

        # Calculate health score
        total_items = self.stats['total_files'] + self.stats['total_folders']
        if total_items > 0:
            synced_items = total_items - self.stats['not_synced_count'] - self.stats['sync_errors_count']
            health_score = (synced_items / total_items) * 100

            if health_score >= 90:
                health_status = "Excellent"
                health_color = "green"
            elif health_score >= 70:
                health_status = "Good"
                health_color = "blue"
            elif health_score >= 50:
                health_status = "Fair"
                health_color = "orange"
            else:
                health_status = "Poor"
                health_color = "red"

            health_label = ttk.Label(health_frame,
                                    text=f"Health Score: {health_score:.1f}% - {health_status}",
                                    font=('Arial', 12, 'bold'))
            health_label.pack()

            # Recommendations
            if self.stats['sync_errors_count'] > 0:
                ttk.Label(health_frame, text=f"⚠ {self.stats['sync_errors_count']} files have sync errors - check Sync Errors tab",
                         font=('Arial', 9), foreground='red').pack(pady=2)

            if self.stats['not_synced_count'] > total_items * 0.1:
                ttk.Label(health_frame, text=f"ℹ {self.stats['not_synced_count']} items not synced - may be online-only",
                         font=('Arial', 9), foreground='orange').pack(pady=2)

    def populate_not_synced(self):
        """Populate not synced files tab"""
        for widget in self.not_synced_frame.winfo_children():
            widget.destroy()

        if not self.not_synced_df.empty:
            table = Table(self.not_synced_frame, dataframe=self.not_synced_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.not_synced_frame,
                     text="All files and folders are synced!",
                     font=('Arial', 12), foreground='green').pack(pady=20)

    def populate_errors(self):
        """Populate sync errors tab"""
        for widget in self.errors_frame.winfo_children():
            widget.destroy()

        if not self.sync_errors_df.empty:
            table = Table(self.errors_frame, dataframe=self.sync_errors_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.errors_frame,
                     text="No sync errors detected!",
                     font=('Arial', 12), foreground='green').pack(pady=20)

    def populate_hydration(self):
        """Populate hydration status tab"""
        for widget in self.hydration_frame.winfo_children():
            widget.destroy()

        # Create paned window for split view
        paned = ttk.PanedWindow(self.hydration_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Hydrated files
        hydrated_frame = ttk.LabelFrame(paned, text=f"Hydrated Files ({len(self.hydrated_df)})")
        paned.add(hydrated_frame, weight=1)

        if not self.hydrated_df.empty:
            table1 = Table(hydrated_frame, dataframe=self.hydrated_df,
                         showtoolbar=True, showstatusbar=True)
            table1.show()
        else:
            ttk.Label(hydrated_frame, text="No hydrated files",
                     font=('Arial', 10)).pack(pady=10)

        # Not hydrated files
        not_hydrated_frame = ttk.LabelFrame(paned, text=f"Not Hydrated (Online Only) ({len(self.not_hydrated_df)})")
        paned.add(not_hydrated_frame, weight=1)

        if not self.not_hydrated_df.empty:
            table2 = Table(not_hydrated_frame, dataframe=self.not_hydrated_df,
                         showtoolbar=True, showstatusbar=True)
            table2.show()
        else:
            ttk.Label(not_hydrated_frame, text="No online-only files",
                     font=('Arial', 10)).pack(pady=10)

    def populate_pinned(self):
        """Populate pinned files tab"""
        for widget in self.pinned_frame.winfo_children():
            widget.destroy()

        if not self.pinned_df.empty:
            table = Table(self.pinned_frame, dataframe=self.pinned_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.pinned_frame,
                     text="No pinned files found",
                     font=('Arial', 12)).pack(pady=20)

    def populate_status_breakdown(self):
        """Populate status breakdown tab"""
        for widget in self.status_breakdown_frame.winfo_children():
            widget.destroy()

        # Create DataFrame from status counts
        if self.status_counts:
            status_df = pd.DataFrame([
                {'Status': status, 'Count': count, 'Percentage': f"{count/max(self.stats['total_files']+self.stats['total_folders'],1)*100:.2f}%"}
                for status, count in sorted(self.status_counts.items(), key=lambda x: x[1], reverse=True)
            ])

            table = Table(self.status_breakdown_frame, dataframe=status_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.status_breakdown_frame,
                     text="No status data available",
                     font=('Arial', 12)).pack(pady=20)

    def export_report(self):
        """Export sync status report"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="sync_status_report.csv"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("OneDrive Sync Status Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write("=== SUMMARY STATISTICS ===\n")
                    f.write(f"Total Files: {self.stats['total_files']}\n")
                    f.write(f"Total Folders: {self.stats['total_folders']}\n")
                    f.write(f"Not Synced: {self.stats['not_synced_count']}\n")
                    f.write(f"Sync Errors: {self.stats['sync_errors_count']}\n")
                    f.write(f"Hydrated: {self.stats['hydrated_count']}\n")
                    f.write(f"Not Hydrated: {self.stats['not_hydrated_count']}\n")
                    f.write(f"Pinned: {self.stats['pinned_count']}\n\n")

                    if not self.not_synced_df.empty:
                        f.write("=== NOT SYNCED FILES ===\n")
                        self.not_synced_df.to_csv(f, index=False)
                        f.write("\n")

                    if not self.sync_errors_df.empty:
                        f.write("=== SYNC ERRORS ===\n")
                        self.sync_errors_df.to_csv(f, index=False)
                        f.write("\n")

                self.status_label.config(text=f"Report exported to {file_path}")
                log.info(f"Sync status report exported to {file_path}")

        except Exception as e:
            log.error(f"Error exporting report: {e}")
            self.status_label.config(text=f"Export error: {e}")
