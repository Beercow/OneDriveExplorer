# -*- mode: python ; coding: utf-8 -*-
"""
OneDriveExplorer PyInstaller Specification File
Builds the complete GUI application with all dependencies and resources
"""

block_cipher = None

# Analysis: Scan all Python files and dependencies
a = Analysis(
    ['OneDriveExplorer\\OneDriveExplorer_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include all images and icons
        ('OneDriveExplorer\\Images', 'Images'),

        # Include all ODE package files
        ('OneDriveExplorer\\ode\\helpers', 'ode\\helpers'),
        ('OneDriveExplorer\\ode\\parsers', 'ode\\parsers'),
        ('OneDriveExplorer\\ode\\renderers', 'ode\\renderers'),
        ('OneDriveExplorer\\ode\\views', 'ode\\views'),
        ('OneDriveExplorer\\ode\\utils.py', 'ode'),
        ('OneDriveExplorer\\ode\\__init__.py', 'ode'),

        # Include helper files
        ('OneDriveExplorer\\ode\\helpers\\structures', 'ode\\helpers'),
        ('OneDriveExplorer\\ode\\helpers\\schema', 'ode\\helpers'),
        ('OneDriveExplorer\\ode\\helpers\\Manual', 'ode\\helpers\\Manual'),
    ],
    hiddenimports=[
        # Core imports
        'tkinter',
        'tkinter.ttk',
        'ttkthemes',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageGrab',

        # Data processing
        'pandas',
        'numpy',
        'pandastable',

        # ODE modules
        'ode.helpers.pandastablepatch',
        'ode.helpers.ScrollableNotebookpatch',
        'ode.helpers.AnimatedGif',
        'ode.helpers.mft',
        'ode.helpers.structures',

        # Parsers
        'ode.parsers.dat',
        'ode.parsers.dat_legacy',
        'ode.parsers.odl',
        'ode.parsers.sqlite_db',
        'ode.parsers.onedrive',
        'ode.parsers.csv_file',
        'ode.parsers.recbin',
        'ode.parsers.Nucleus.listsync',
        'ode.parsers.Nucleus.fileusagesync',
        'ode.parsers.Nucleus.filesondemand',

        # Renderers
        'ode.renderers.json',
        'ode.renderers.csv_file',
        'ode.renderers.html',
        'ode.renderers.project',

        # Views (NEW - All reporting views)
        'ode.views.fileusage',
        'ode.views.multiselect',
        'ode.views.activity_timeline',
        'ode.views.data_summary',
        'ode.views.collaboration_report',
        'ode.views.sync_status_dashboard',
        'ode.views.file_analytics',

        # Utils
        'ode.utils',

        # Registry
        'Registry',

        # Crypto
        'Crypto.Cipher.AES',
        'Crypto.Util.Padding',

        # YAML
        'ruamel.yaml',

        # Other
        'dissect.cstruct',
        'cerberus',
        'keyboard',
        'psutil',
        'pytsk3',
        'quickxorhash',
        'openpyxl',

        # Collections
        'collections.defaultdict',
        'queue',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude if not used
        'scipy',       # Exclude if not used
        'IPython',     # Exclude if not used
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ: Create the archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Splash screen configuration
splash = Splash(
    'OneDriveExplorer\\Images\\splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(10, 250),
    text_size=10,
    text_color='white',
    text_default='Loading OneDriveExplorer...',
)

# EXE: Create the executable
exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    [],
    exclude_binaries=True,
    name='OneDriveExplorer_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='OneDriveExplorer\\Images\\ode.ico',
    version_file=None,  # Can add version_info.txt if created
)

# COLLECT: Collect all files into distribution folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OneDriveExplorer_GUI',
)
