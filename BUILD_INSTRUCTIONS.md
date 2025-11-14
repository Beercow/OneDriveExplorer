# OneDriveExplorer GUI - Build Instructions

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Build Process](#build-process)
- [Build Options](#build-options)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)
- [Advanced Configuration](#advanced-configuration)

---

## 🔧 Prerequisites

### Required Software
1. **Python 3.8 or higher**
   - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Git** (optional, for version control)
   - Download from https://git-scm.com/

### Required Python Packages
All dependencies are listed in `requirements.txt`:
- pandas (data processing)
- numpy (numerical operations)
- ttkthemes (themed GUI)
- Pillow (image processing)
- python-registry (Windows registry)
- dissect.cstruct (binary parsing)
- pycryptodome (encryption)
- ruamel.yaml (YAML processing)
- cerberus (validation)
- pandastable (table display)
- keyboard (keyboard hooks)
- psutil (system utilities)
- pytsk3 (file system analysis)
- quickxorhash (hash calculation)
- openpyxl (Excel export)
- pyinstaller (building executables)

---

## 🚀 Quick Start

### Standard Build (Recommended)

```batch
REM 1. Install dependencies
python -m pip install -r requirements.txt

REM 2. Build the application
build.bat

REM 3. Create distribution package
package_dist.bat
```

The executable will be in: `dist\OneDriveExplorer_GUI\OneDriveExplorer_GUI.exe`

### Single-File Build

```batch
REM Build as single .exe file (slower startup but easier distribution)
build.bat onefile
```

The executable will be in: `dist\OneDriveExplorer_GUI.exe`

### Clean Build

```batch
REM Remove all build artifacts and rebuild from scratch
build.bat clean
```

---

## 🔨 Build Process

### Step-by-Step Process

**1. Setup Environment**
```batch
REM Clone or download the repository
git clone https://github.com/Beercow/OneDriveExplorer.git
cd OneDriveExplorer

REM Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

REM Install dependencies
python -m pip install -r requirements.txt
```

**2. Verify Installation**
```batch
REM Test that all imports work
python -c "import pandas, numpy, PIL, ttkthemes; print('All dependencies OK')"

REM Test that OneDrive Explorer runs
cd OneDriveExplorer
python OneDriveExplorer_GUI.py
```

**3. Build Executable**
```batch
REM Return to root directory
cd ..

REM Run build script
build.bat
```

**4. Verify Build**
```batch
REM Test the executable
dist\OneDriveExplorer_GUI\OneDriveExplorer_GUI.exe

REM Check that all 5 new reporting tabs appear:
REM - Data Summary
REM - Activity Timeline
REM - Sync Status
REM - File Analytics
REM - Collaboration
```

**5. Create Distribution**
```batch
REM Create distribution package
package_dist.bat

REM This creates:
REM - OneDriveExplorer_v2.0\ folder with all files
REM - OneDriveExplorer_v2.0_Windows.zip for distribution
```

---

## ⚙️ Build Options

### Using build.bat

**Standard Build (Multi-file)**
```batch
build.bat
```
- Faster startup
- Easier debugging
- Larger folder size
- Recommended for development

**Single-File Build**
```batch
build.bat onefile
```
- Slower startup (extracts on run)
- Single executable
- Easier distribution
- Recommended for end users

**Clean Build**
```batch
build.bat clean
```
- Removes all build artifacts
- Forces fresh build
- Use when troubleshooting

### Using PyInstaller Directly

**With Spec File (Recommended)**
```batch
python -m PyInstaller --noconfirm OneDriveExplorer_GUI.spec
```

**Manual Build**
```batch
python -m PyInstaller ^
    --name=OneDriveExplorer_GUI ^
    --windowed ^
    --icon=OneDriveExplorer\Images\ode.ico ^
    --add-data="OneDriveExplorer\Images;Images" ^
    --add-data="OneDriveExplorer\ode;ode" ^
    OneDriveExplorer\OneDriveExplorer_GUI.py
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "Python not found"
**Solution:**
- Install Python from https://www.python.org/
- Make sure "Add Python to PATH" was checked during installation
- Restart command prompt after installation
- Verify: `python --version`

#### Issue: "PyInstaller not found"
**Solution:**
```batch
python -m pip install pyinstaller
```

#### Issue: "Module not found" during build
**Solution:**
```batch
REM Reinstall all requirements
python -m pip install -r requirements.txt --upgrade

REM Or install specific missing module
python -m pip install <module-name>
```

#### Issue: "Import Error" when running executable
**Solution:**
- Check `hiddenimports` in .spec file
- Add missing module:
```python
hiddenimports=[
    'your.missing.module',
    # ... other imports
],
```
- Rebuild: `build.bat clean`

#### Issue: Images/Icons not showing in executable
**Solution:**
- Verify `OneDriveExplorer\Images\` directory exists
- Check `datas` in .spec file includes Images
- Rebuild to ensure images are packaged

#### Issue: Build successful but exe crashes on startup
**Solution:**
```batch
REM Run exe from command line to see errors
dist\OneDriveExplorer_GUI\OneDriveExplorer_GUI.exe

REM Check for missing dependencies
REM Look for import errors in console output

REM Try clean build
clean_build.bat
build.bat
```

#### Issue: "Access denied" during build
**Solution:**
- Close any running OneDriveExplorer instances
- Disable antivirus temporarily
- Run command prompt as Administrator
- Use `clean_build.bat` first

#### Issue: Extremely large executable size
**Solution:**
```python
# In .spec file, add exclusions:
excludes=[
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    # Add other unused large packages
],
```

#### Issue: "Failed to execute script" error
**Solution:**
- Check Python version compatibility (3.8+)
- Verify all imports work in source code
- Check antivirus isn't blocking
- Look for dependency conflicts:
```batch
python -m pip check
```

---

## 📦 Distribution

### Creating Distribution Package

**Automated (Recommended)**
```batch
REM Build and package in one step
build.bat
package_dist.bat
```

**Manual**
1. Build executable: `build.bat`
2. Copy `dist\OneDriveExplorer_GUI\` folder
3. Add documentation:
   - README.md
   - ENHANCEMENT_SUMMARY.md
   - COMPREHENSIVE_REPORTING_GUIDE.md
   - LICENSE
4. Create ZIP file

### Distribution Package Contents
```
OneDriveExplorer_v2.0\
├── OneDriveExplorer_GUI.exe     (Main executable)
├── Images\                       (Icons and graphics)
├── ode\                         (Python package)
│   ├── helpers\
│   ├── parsers\
│   ├── renderers\
│   └── views\                   (NEW: All 5 reporting views)
├── _internal\                   (PyInstaller dependencies)
├── QUICK_START.txt              (Quick start guide)
├── ENHANCEMENT_SUMMARY.md       (New features overview)
├── COMPREHENSIVE_REPORTING_GUIDE.md  (Complete guide)
├── VERSION.txt                  (Version information)
└── README.md                    (Full documentation)
```

### Testing Distribution

**Test on Clean Machine**
1. Use Windows VM or clean test PC
2. Extract distribution package
3. Run OneDriveExplorer_GUI.exe
4. Test all features:
   - Load sample OneDrive data
   - Verify all 5 new reporting tabs work
   - Test export functions
   - Check error handling

**Checklist:**
- [ ] Application starts without errors
- [ ] All menus accessible
- [ ] Can load OneDrive data
- [ ] Data Summary tab shows statistics
- [ ] Activity Timeline displays events
- [ ] Sync Status shows health score
- [ ] File Analytics calculates sizes
- [ ] Collaboration Report shows creators/modifiers
- [ ] Export functions work (CSV, HTML)
- [ ] No crashes or freezes

---

## 🔬 Advanced Configuration

### Customizing PyInstaller Spec File

**Add Hidden Imports**
```python
hiddenimports=[
    'your.custom.module',
    'another.module',
],
```

**Exclude Large Unused Packages**
```python
excludes=[
    'matplotlib',
    'scipy',
    'test',
    'unittest',
],
```

**Add Additional Data Files**
```python
datas=[
    ('path/to/data', 'destination'),
    ('config.ini', '.'),
],
```

**Enable Debug Mode**
```python
debug=True,  # Shows console for debugging
```

**Optimize with UPX**
```python
upx=True,
upx_exclude=[],  # Compress executable
```

### Version Information

Create `version_info.txt`:
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'OneDriveExplorer'),
        StringStruct(u'FileDescription', u'OneDrive Forensics Tool'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'OneDriveExplorer_GUI'),
        StringStruct(u'LegalCopyright', u'Copyright 2025'),
        StringStruct(u'OriginalFilename', u'OneDriveExplorer_GUI.exe'),
        StringStruct(u'ProductName', u'OneDriveExplorer'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

Add to spec file:
```python
version_file='version_info.txt',
```

### Code Signing (Optional)

**After Build:**
```batch
REM Sign executable with certificate
signtool sign /f mycert.pfx /p password /t http://timestamp.digicert.com dist\OneDriveExplorer_GUI\OneDriveExplorer_GUI.exe
```

### Build Optimization Tips

**Reduce Size:**
1. Use `excludes` to remove unused packages
2. Enable UPX compression
3. Remove debug symbols
4. Use `--onefile` for single executable

**Improve Startup Time:**
1. Use multi-file build (not `--onefile`)
2. Disable UPX compression
3. Reduce number of hidden imports

**Better Error Messages:**
1. Set `console=True` during development
2. Use `debug=True` for verbose output
3. Add logging to catch startup issues

---

## 📊 Build Metrics

### Typical Build Times
| Configuration | Build Time | Size |
|--------------|------------|------|
| Standard (Multi-file) | 2-3 min | ~300 MB |
| Single File | 3-5 min | ~120 MB |
| Clean Build | 3-4 min | ~300 MB |
| With UPX | 4-6 min | ~250 MB |

### System Requirements for Building
- **CPU**: Any modern processor
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk**: 2 GB free space
- **OS**: Windows 10 or later

---

## 🆘 Getting Help

### Resources
- **Documentation**: See COMPREHENSIVE_REPORTING_GUIDE.md
- **Issues**: https://github.com/Beercow/OneDriveExplorer/issues
- **PyInstaller Docs**: https://pyinstaller.readthedocs.io/

### Reporting Build Issues
When reporting issues, include:
1. Python version (`python --version`)
2. PyInstaller version (`pyinstaller --version`)
3. Operating System and version
4. Full error message or traceback
5. Build command used
6. Contents of build log

### Community Support
- GitHub Issues for bug reports
- Stack Overflow for general questions
- PyInstaller documentation for packaging issues

---

## ✅ Build Checklist

Before distributing:
- [ ] Tested on clean Windows machine
- [ ] All 5 new reporting views work
- [ ] No console window appears (unless debug build)
- [ ] Images and icons display correctly
- [ ] Export functions work (CSV, HTML)
- [ ] No import errors
- [ ] File size reasonable (<400 MB)
- [ ] Antivirus doesn't flag as malware
- [ ] Version information correct
- [ ] Documentation included
- [ ] License files included

---

## 📝 Notes

- Build times vary based on system performance
- First build is slower (PyInstaller caches data)
- Antivirus may slow down or block build process
- Virtual environments recommended for clean builds
- Test distribution on multiple Windows versions
- Keep build scripts under version control

---

**Last Updated**: 2025-11-14
**Version**: 2.0
**Build System**: PyInstaller 5.0+
