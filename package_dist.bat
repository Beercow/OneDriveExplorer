@echo off
REM ============================================================================
REM OneDriveExplorer GUI - Create Distribution Package
REM ============================================================================
REM This script creates a complete distribution package ready for deployment
REM Includes executable, documentation, licenses, and release notes
REM ============================================================================

setlocal enabledelayedexpansion

REM Set colors
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM Configuration
set "APP_NAME=OneDriveExplorer_GUI"
set "VERSION=2.0"
set "BUILD_DIR=dist"
set "PACKAGE_DIR=OneDriveExplorer_v%VERSION%"
set "ZIP_NAME=OneDriveExplorer_v%VERSION%_Windows.zip"

echo.
echo %BLUE%============================================================================%NC%
echo %BLUE%   OneDriveExplorer - Create Distribution Package%NC%
echo %BLUE%   Version %VERSION%%NC%
echo %BLUE%============================================================================%NC%
echo.

REM ============================================================================
REM Check if build exists
REM ============================================================================
echo %YELLOW%[1/5] Checking build...%NC%

if not exist "%BUILD_DIR%\%APP_NAME%\%APP_NAME%.exe" (
    echo %RED%ERROR: Built executable not found!%NC%
    echo Please run build.bat first to create the executable
    pause
    exit /b 1
)

echo %GREEN%Executable found%NC%
echo.

REM ============================================================================
REM Create package directory
REM ============================================================================
echo %YELLOW%[2/5] Creating package directory...%NC%

if exist "%PACKAGE_DIR%" (
    echo Removing old package directory...
    rmdir /s /q "%PACKAGE_DIR%" 2>nul
)

mkdir "%PACKAGE_DIR%" 2>nul

REM Copy the entire build
echo Copying executable and dependencies...
xcopy /E /I /H /Y "%BUILD_DIR%\%APP_NAME%\*" "%PACKAGE_DIR%\" >nul

if errorlevel 1 (
    echo %RED%ERROR: Failed to copy build files%NC%
    pause
    exit /b 1
)

echo %GREEN%Files copied%NC%
echo.

REM ============================================================================
REM Add documentation
REM ============================================================================
echo %YELLOW%[3/5] Adding documentation...%NC%

REM Copy README if exists
if exist "README.md" (
    echo Adding README.md...
    copy /Y "README.md" "%PACKAGE_DIR%\README.md" >nul
)

REM Copy enhancement documentation
if exist "ENHANCEMENT_SUMMARY.md" (
    echo Adding ENHANCEMENT_SUMMARY.md...
    copy /Y "ENHANCEMENT_SUMMARY.md" "%PACKAGE_DIR%\ENHANCEMENT_SUMMARY.md" >nul
)

if exist "COMPREHENSIVE_REPORTING_GUIDE.md" (
    echo Adding COMPREHENSIVE_REPORTING_GUIDE.md...
    copy /Y "COMPREHENSIVE_REPORTING_GUIDE.md" "%PACKAGE_DIR%\COMPREHENSIVE_REPORTING_GUIDE.md" >nul
)

REM Create quick start guide
echo Creating Quick Start Guide...
(
echo OneDriveExplorer GUI - Quick Start Guide
echo ========================================
echo.
echo VERSION: %VERSION%
echo.
echo WHAT'S NEW IN VERSION 2.0:
echo ---------------------------
echo This version includes a comprehensive reporting suite with 5 new analytics views:
echo.
echo 1. Data Summary Dashboard - Overview of loaded data and statistics
echo 2. Activity Timeline - Chronological history of all OneDrive activities
echo 3. Sync Status Dashboard - Comprehensive sync health analysis
echo 4. File Analytics - Storage usage and file type analysis
echo 5. Collaboration Report - User collaboration and sharing analysis
echo.
echo SYSTEM REQUIREMENTS:
echo --------------------
echo - Windows 10 or later
echo - 4 GB RAM minimum (8 GB recommended^)
echo - 500 MB free disk space
echo - Administrator rights (for some features^)
echo.
echo INSTALLATION:
echo -------------
echo 1. Extract all files to a folder (e.g., C:\OneDriveExplorer^)
echo 2. Run OneDriveExplorer_GUI.exe
echo 3. No installation required - portable application
echo.
echo USAGE:
echo ------
echo 1. Launch OneDriveExplorer_GUI.exe
echo 2. Use File menu to load OneDrive data:
echo    - Load ^<UserCid^>.dat files
echo    - Load SyncEngineDatabase.db
echo    - Load SafeDelete.db
echo    - Load Registry hive (NTUSER.DAT^)
echo.
echo 3. Explore the new reporting tabs:
echo    - Data Summary: Overview of what was loaded
echo    - Activity Timeline: Chronological activity history
echo    - Sync Status: Sync health and issues
echo    - File Analytics: Storage and file analysis
echo    - Collaboration: User collaboration patterns
echo.
echo DOCUMENTATION:
echo --------------
echo - ENHANCEMENT_SUMMARY.md: Quick overview of new features
echo - COMPREHENSIVE_REPORTING_GUIDE.md: Complete feature guide
echo - See ode\helpers\Manual\ for detailed help
echo.
echo TROUBLESHOOTING:
echo ----------------
echo - If app doesn't start, check Windows Event Viewer
echo - Error logs saved to ODE_error_*.log in application directory
echo - For help, visit: https://github.com/Beercow/OneDriveExplorer
echo.
echo LICENSE:
echo --------
echo MIT License - See LICENSE or COPYING files
echo.
echo CREDITS:
echo --------
echo Original Author: Brian Maloney
echo Enhanced Reporting: Claude AI Assistant (2025^)
echo.
echo Copyright (C^) 2025
echo.
) > "%PACKAGE_DIR%\QUICK_START.txt"

echo %GREEN%Documentation added%NC%
echo.

REM ============================================================================
REM Add version information
REM ============================================================================
echo %YELLOW%[4/5] Creating version info...%NC%

(
echo OneDriveExplorer GUI
echo Version: %VERSION%
echo Build Date: %DATE% %TIME%
echo.
echo FEATURES:
echo ---------
echo [X] OneDrive DAT file parsing
echo [X] SyncEngineDatabase analysis
echo [X] SafeDelete.db tracking
echo [X] Registry integration
echo [X] Recycle Bin analysis
echo [X] ODL log parsing
echo [X] FileUsageSync analysis
echo.
echo NEW IN v2.0:
echo ------------
echo [X] Data Summary Dashboard
echo [X] Activity Timeline Report
echo [X] Sync Status Dashboard
echo [X] File Analytics Report
echo [X] Collaboration Report
echo [X] Professional CSV/HTML exports
echo [X] Multi-source data correlation
echo [X] Advanced filtering and search
echo.
echo INCLUDED FILES:
echo ---------------
) > "%PACKAGE_DIR%\VERSION.txt"

REM List all files
dir /b "%PACKAGE_DIR%" >> "%PACKAGE_DIR%\VERSION.txt"

echo %GREEN%Version info created%NC%
echo.

REM ============================================================================
REM Create ZIP package
REM ============================================================================
echo %YELLOW%[5/5] Creating ZIP package...%NC%

REM Check if PowerShell is available for zip creation
powershell -Command "Get-Command Compress-Archive" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%PowerShell Compress-Archive not available%NC%
    echo %YELLOW%Please manually zip the '%PACKAGE_DIR%' folder%NC%
    echo.
    goto :skip_zip
)

REM Remove old ZIP if exists
if exist "%ZIP_NAME%" (
    echo Removing old ZIP file...
    del /q "%ZIP_NAME%" 2>nul
)

REM Create ZIP using PowerShell
echo Creating %ZIP_NAME%...
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%ZIP_NAME%' -CompressionLevel Optimal"

if errorlevel 1 (
    echo %RED%ERROR: Failed to create ZIP file%NC%
    echo Please manually zip the '%PACKAGE_DIR%' folder
) else (
    echo %GREEN%ZIP package created successfully!%NC%

    REM Get ZIP size
    for %%A in ("%ZIP_NAME%") do set "SIZE=%%~zA"
    set /a SIZE_MB=!SIZE! / 1048576
    echo ZIP size: !SIZE_MB! MB
)

:skip_zip

echo.

REM ============================================================================
REM Summary
REM ============================================================================
echo %BLUE%============================================================================%NC%
echo %GREEN%   DISTRIBUTION PACKAGE COMPLETE!%NC%
echo %BLUE%============================================================================%NC%
echo.
echo Package Directory: %PACKAGE_DIR%\
if exist "%ZIP_NAME%" (
    echo ZIP Package:       %ZIP_NAME%
)
echo.
echo %YELLOW%Contents:%NC%
echo   [X] OneDriveExplorer_GUI.exe
echo   [X] All dependencies and libraries
echo   [X] Images and resources
echo   [X] Enhanced reporting views
echo   [X] Documentation (README, guides^)
echo   [X] Quick Start Guide
echo   [X] Version information
echo.
echo %YELLOW%Next Steps:%NC%
echo   1. Test the package on a clean Windows machine
echo   2. Verify all features work correctly
echo   3. Test all 5 new reporting views
if exist "%ZIP_NAME%" (
    echo   4. Distribute %ZIP_NAME%
) else (
    echo   4. Manually create ZIP of %PACKAGE_DIR%
)
echo.
echo %BLUE%============================================================================%NC%
echo.

REM Ask to open folder
set /p "OPEN_FOLDER=Open package folder? (Y/N): "
if /i "%OPEN_FOLDER%"=="Y" (
    explorer "%CD%\%PACKAGE_DIR%"
)

pause
