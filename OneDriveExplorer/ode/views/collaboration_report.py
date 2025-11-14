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

log = logging.getLogger(__name__)


class CollaborationReportFrame(ttk.Frame):
    """
    Collaboration Report - Analyzes collaboration patterns including who created/modified files,
    sharing statistics, and top collaborators.
    """

    def __init__(self, master, cache_data, graphMetadata=None, fileusage_data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cache_data = cache_data
        self.graphMetadata = graphMetadata if graphMetadata is not None else pd.DataFrame()
        self.fileusage_data = fileusage_data or {}

        self.setup_ui()
        self.analyze_collaboration()

    def setup_ui(self):
        """Create the UI components"""
        # Create notebook for different collaboration views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")

        # Tab 2: Top Collaborators
        self.collaborators_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.collaborators_frame, text="Top Collaborators")

        # Tab 3: File Creators
        self.creators_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.creators_frame, text="File Creators")

        # Tab 4: File Modifiers
        self.modifiers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.modifiers_frame, text="File Modifiers")

        # Tab 5: Shared Files
        self.shared_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.shared_frame, text="Shared Files")

        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        self.status_label = ttk.Label(self.status_frame, text="Analyzing collaboration data...")
        self.status_label.pack(side=tk.LEFT)

        # Export button
        export_btn = ttk.Button(self.status_frame, text="Export Report (CSV)",
                               command=self.export_report)
        export_btn.pack(side=tk.RIGHT, padx=5)

    def analyze_collaboration(self):
        """Analyze collaboration data from all sources"""
        try:
            # Extract collaboration data from graphMetadata
            creators = []
            modifiers = []
            shared_files = []

            # Analyze cache data for shared items
            if self.cache_data:
                for item_id, item_data in self.cache_data.items():
                    if not isinstance(item_data, dict):
                        continue

                    # Check for shared items
                    if item_data.get('sharedItem', 0) != 0:
                        shared_files.append({
                            'Name': item_data.get('Name', 'Unknown'),
                            'Path': item_data.get('Path', ''),
                            'Type': item_data.get('Type', 'File'),
                            'Size': item_data.get('size', '0 KB'),
                            'LastChange': item_data.get('lastChange', ''),
                            'SharedStatus': item_data.get('sharedItem', 0)
                        })

                    # Extract metadata if available
                    metadata = item_data.get('Metadata', {})
                    if isinstance(metadata, dict):
                        created_by = metadata.get('createdBy', '')
                        modified_by = metadata.get('modifiedBy', '')

                        if created_by:
                            creators.append({
                                'User': created_by,
                                'File': item_data.get('Name', 'Unknown'),
                                'Path': item_data.get('Path', ''),
                                'Type': item_data.get('Type', 'File')
                            })

                        if modified_by:
                            modifiers.append({
                                'User': modified_by,
                                'File': item_data.get('Name', 'Unknown'),
                                'Path': item_data.get('Path', ''),
                                'Type': item_data.get('Type', 'File')
                            })

            # Create DataFrames
            self.creators_df = pd.DataFrame(creators)
            self.modifiers_df = pd.DataFrame(modifiers)
            self.shared_df = pd.DataFrame(shared_files)

            # Calculate statistics
            self.calculate_statistics()

            # Populate all tabs
            self.populate_overview()
            self.populate_collaborators()
            self.populate_creators()
            self.populate_modifiers()
            self.populate_shared()

            self.status_label.config(text=f"Analysis complete - {len(shared_files)} shared files, "
                                         f"{len(set([c['User'] for c in creators]))} creators, "
                                         f"{len(set([m['User'] for m in modifiers]))} modifiers")

        except Exception as e:
            log.error(f"Error analyzing collaboration: {e}")
            self.status_label.config(text=f"Error: {e}")

    def calculate_statistics(self):
        """Calculate collaboration statistics"""
        self.stats = {
            'total_shared_files': len(self.shared_df),
            'total_creators': len(self.creators_df['User'].unique()) if not self.creators_df.empty else 0,
            'total_modifiers': len(self.modifiers_df['User'].unique()) if not self.modifiers_df.empty else 0,
            'top_creators': {},
            'top_modifiers': {},
            'sharing_by_type': {}
        }

        # Top creators
        if not self.creators_df.empty:
            creator_counts = self.creators_df['User'].value_counts()
            self.stats['top_creators'] = dict(creator_counts.head(10))

        # Top modifiers
        if not self.modifiers_df.empty:
            modifier_counts = self.modifiers_df['User'].value_counts()
            self.stats['top_modifiers'] = dict(modifier_counts.head(10))

        # Sharing by file type
        if not self.shared_df.empty:
            type_counts = self.shared_df['Type'].value_counts()
            self.stats['sharing_by_type'] = dict(type_counts)

    def populate_overview(self):
        """Populate overview tab with statistics"""
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
        title = ttk.Label(scrollable_frame, text="Collaboration Overview",
                         font=('Arial', 14, 'bold'))
        title.pack(pady=10)

        # Summary statistics
        summary_frame = ttk.LabelFrame(scrollable_frame, text="Summary Statistics", padding=15)
        summary_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_grid = ttk.Frame(summary_frame)
        stats_grid.pack(fill=tk.X)

        stats_data = [
            ("Total Shared Files:", self.stats['total_shared_files']),
            ("Unique Creators:", self.stats['total_creators']),
            ("Unique Modifiers:", self.stats['total_modifiers']),
        ]

        for i, (label, value) in enumerate(stats_data):
            ttk.Label(stats_grid, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            ttk.Label(stats_grid, text=str(value), font=('Arial', 10)).grid(
                row=i, column=1, sticky='w', padx=10, pady=5)

        # Top Creators section
        if self.stats['top_creators']:
            creators_frame = ttk.LabelFrame(scrollable_frame, text="Top 10 File Creators", padding=15)
            creators_frame.pack(fill=tk.X, padx=20, pady=10)

            for i, (user, count) in enumerate(list(self.stats['top_creators'].items())[:10]):
                row_frame = ttk.Frame(creators_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=f"{i+1}.", width=3).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=user, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
                ttk.Label(row_frame, text=f"({count} files)",
                         font=('Arial', 9, 'italic')).pack(side=tk.LEFT)

        # Top Modifiers section
        if self.stats['top_modifiers']:
            modifiers_frame = ttk.LabelFrame(scrollable_frame, text="Top 10 File Modifiers", padding=15)
            modifiers_frame.pack(fill=tk.X, padx=20, pady=10)

            for i, (user, count) in enumerate(list(self.stats['top_modifiers'].items())[:10]):
                row_frame = ttk.Frame(modifiers_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=f"{i+1}.", width=3).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=user, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
                ttk.Label(row_frame, text=f"({count} modifications)",
                         font=('Arial', 9, 'italic')).pack(side=tk.LEFT)

        # Sharing by type section
        if self.stats['sharing_by_type']:
            sharing_frame = ttk.LabelFrame(scrollable_frame, text="Shared Files by Type", padding=15)
            sharing_frame.pack(fill=tk.X, padx=20, pady=10)

            for file_type, count in self.stats['sharing_by_type'].items():
                row_frame = ttk.Frame(sharing_frame)
                row_frame.pack(fill=tk.X, pady=2)

                ttk.Label(row_frame, text=file_type, font=('Arial', 9, 'bold'),
                         width=15).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"{count} files",
                         font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

    def populate_collaborators(self):
        """Populate top collaborators tab"""
        # Clear existing widgets
        for widget in self.collaborators_frame.winfo_children():
            widget.destroy()

        # Check if we have FileUsageSync data
        if self.fileusage_data and hasattr(self.fileusage_data, 'tc_data'):
            if not self.fileusage_data.tc_data.empty:
                table = Table(self.collaborators_frame, dataframe=self.fileusage_data.tc_data,
                            showtoolbar=True, showstatusbar=True)
                table.show()
            else:
                ttk.Label(self.collaborators_frame,
                         text="No top collaborators data available from FileUsageSync.db",
                         font=('Arial', 12)).pack(pady=20)
        else:
            ttk.Label(self.collaborators_frame,
                     text="FileUsageSync.db not loaded - no collaborator data available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_creators(self):
        """Populate file creators tab"""
        # Clear existing widgets
        for widget in self.creators_frame.winfo_children():
            widget.destroy()

        if not self.creators_df.empty:
            table = Table(self.creators_frame, dataframe=self.creators_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.creators_frame,
                     text="No file creator metadata available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_modifiers(self):
        """Populate file modifiers tab"""
        # Clear existing widgets
        for widget in self.modifiers_frame.winfo_children():
            widget.destroy()

        if not self.modifiers_df.empty:
            table = Table(self.modifiers_frame, dataframe=self.modifiers_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.modifiers_frame,
                     text="No file modifier metadata available",
                     font=('Arial', 12)).pack(pady=20)

    def populate_shared(self):
        """Populate shared files tab"""
        # Clear existing widgets
        for widget in self.shared_frame.winfo_children():
            widget.destroy()

        if not self.shared_df.empty:
            table = Table(self.shared_frame, dataframe=self.shared_df,
                        showtoolbar=True, showstatusbar=True)
            table.show()
        else:
            ttk.Label(self.shared_frame,
                     text="No shared files found",
                     font=('Arial', 12)).pack(pady=20)

    def export_report(self):
        """Export collaboration report to CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="collaboration_report.csv"
            )

            if file_path:
                # Create comprehensive report
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("OneDrive Collaboration Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    f.write("=== SUMMARY STATISTICS ===\n")
                    f.write(f"Total Shared Files: {self.stats['total_shared_files']}\n")
                    f.write(f"Unique Creators: {self.stats['total_creators']}\n")
                    f.write(f"Unique Modifiers: {self.stats['total_modifiers']}\n\n")

                    if self.stats['top_creators']:
                        f.write("=== TOP FILE CREATORS ===\n")
                        for user, count in self.stats['top_creators'].items():
                            f.write(f"{user},{count}\n")
                        f.write("\n")

                    if self.stats['top_modifiers']:
                        f.write("=== TOP FILE MODIFIERS ===\n")
                        for user, count in self.stats['top_modifiers'].items():
                            f.write(f"{user},{count}\n")
                        f.write("\n")

                    if not self.shared_df.empty:
                        f.write("=== SHARED FILES ===\n")
                        self.shared_df.to_csv(f, index=False)

                self.status_label.config(text=f"Report exported to {file_path}")
                log.info(f"Collaboration report exported to {file_path}")

        except Exception as e:
            log.error(f"Error exporting report: {e}")
            self.status_label.config(text=f"Export error: {e}")
