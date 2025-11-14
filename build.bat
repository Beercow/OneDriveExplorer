@echo off
REM ============================================================================
REM OneDriveExplorer GUI - Build Script
REM ============================================================================
REM This script builds the OneDriveExplorer GUI executable package
REM with all dependencies, resources, and new reporting views included.
REM
REM Requirements:
REM   - Python 3.8 or higher
REM   - All dependencies in requirements.txt installed
REM   - PyInstaller installed (pip install pyinstaller)
REM
REM Usage:
REM   build.bat              - Standard build
REM   build.bat clean        - Clean build (removes old builds first)
REM   build.bat onefile      - Single-file executable (slower startup)
REM ============================================================================

setlocal enabledelayedexpansion

REM Set colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

REM Configuration
set "APP_NAME=OneDriveExplorer_GUI"
set "SPEC_FILE=OneDriveExplorer_GUI.spec"
set "PYTHON_CMD=python"
set "BUILD_DIR=dist"
set "WORK_DIR=build"

REM ============================================================================
REM Banner
REM ============================================================================
echo.
echo %BLUE%============================================================================%NC%
echo %BLUE%   OneDriveExplorer GUI - Build System%NC%
echo %BLUE%   Version 2.0 - Enhanced Reporting Suite%NC%
echo %BLUE%============================================================================%NC%
echo.

REM ============================================================================
REM Check Python Installation
REM ============================================================================
echo %YELLOW%[1/8] Checking Python installation...%NC%
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Python not found in PATH!%NC%
    echo Please install Python 3.8 or higher and add to PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%Found Python %PYTHON_VERSION%%NC%
echo.

REM ============================================================================
REM Check PyInstaller
REM ============================================================================
echo %YELLOW%[2/8] Checking PyInstaller installation...%NC%
%PYTHON_CMD% -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo %RED%PyInstaller not found! Installing...%NC%
    %PYTHON_CMD% -m pip install pyinstaller
    if errorlevel 1 (
        echo %RED%ERROR: Failed to install PyInstaller%NC%
        pause
        exit /b 1
    )
)
echo %GREEN%PyInstaller is installed%NC%
echo.

REM ============================================================================
REM Check Dependencies
REM ============================================================================
echo %YELLOW%[3/8] Checking dependencies...%NC%
if exist requirements.txt (
    echo Verifying required packages...
    %PYTHON_CMD% -m pip check >nul 2>&1
    if errorlevel 1 (
        echo %YELLOW%Warning: Some package dependencies may have issues%NC%
        echo Installing/updating requirements...
        %PYTHON_CMD% -m pip install -r requirements.txt --upgrade
    ) else (
        echo %GREEN%All dependencies OK%NC%
    )
) else (
    echo %YELLOW%Warning: requirements.txt not found%NC%
)
echo.

REM ============================================================================
REM Handle Clean Build Option
REM ============================================================================
if "%1"=="clean" (
    echo %YELLOW%[4/8] Cleaning previous builds...%NC%
    if exist "%BUILD_DIR%" (
        echo Removing %BUILD_DIR%...
        rmdir /s /q "%BUILD_DIR%" 2>nul
    )
    if exist "%WORK_DIR%" (
        echo Removing %WORK_DIR%...
        rmdir /s /q "%WORK_DIR%" 2>nul
    )
    if exist "*.spec" (
        echo Cleaning .spec files...
        del /q *.spec 2>nul
    )
    echo %GREEN%Clean complete%NC%
    echo.
)

REM ============================================================================
REM Verify Source Files
REM ============================================================================
echo %YELLOW%[4/8] Verifying source files...%NC%

if not exist "OneDriveExplorer\OneDriveExplorer_GUI.py" (
    echo %RED%ERROR: OneDriveExplorer_GUI.py not found!%NC%
    echo Please run this script from the OneDriveExplorer root directory
    pause
    exit /b 1
)

if not exist "OneDriveExplorer\Images" (
    echo %RED%ERROR: Images directory not found!%NC%
    pause
    exit /b 1
)

if not exist "OneDriveExplorer\ode" (
    echo %RED%ERROR: ode package directory not found!%NC%
    pause
    exit /b 1
)

echo %GREEN%All source files present%NC%
echo.

REM ============================================================================
REM Verify New Reporting Views
REM ============================================================================
echo %YELLOW%[5/8] Verifying enhanced reporting views...%NC%

set "VIEWS_OK=1"
if not exist "OneDriveExplorer\ode\views\activity_timeline.py" (
    echo %RED%Missing: activity_timeline.py%NC%
    set "VIEWS_OK=0"
)
if not exist "OneDriveExplorer\ode\views\data_summary.py" (
    echo %RED%Missing: data_summary.py%NC%
    set "VIEWS_OK=0"
)
if not exist "OneDriveExplorer\ode\views\collaboration_report.py" (
    echo %RED%Missing: collaboration_report.py%NC%
    set "VIEWS_OK=0"
)
if not exist "OneDriveExplorer\ode\views\sync_status_dashboard.py" (
    echo %RED%Missing: sync_status_dashboard.py%NC%
    set "VIEWS_OK=0"
)
if not exist "OneDriveExplorer\ode\views\file_analytics.py" (
    echo %RED%Missing: file_analytics.py%NC%
    set "VIEWS_OK=0"
)

if "%VIEWS_OK%"=="0" (
    echo %YELLOW%Warning: Some enhanced reporting views are missing%NC%
    echo The build will continue but some features may not work
    timeout /t 5 >nul
) else (
    echo %GREEN%All 5 enhanced reporting views present:%NC%
    echo   - Activity Timeline
    echo   - Data Summary
    echo   - Collaboration Report
    echo   - Sync Status Dashboard
    echo   - File Analytics
)
echo.

REM ============================================================================
REM Build with PyInstaller
REM ============================================================================
echo %YELLOW%[6/8] Building executable...%NC%
echo.

if "%1"=="onefile" (
    echo Building single-file executable...
    echo %BLUE%Note: Single-file build takes longer to start but is easier to distribute%NC%
    echo.

    %PYTHON_CMD% -m PyInstaller ^
        --name="%APP_NAME%" ^
        --onefile ^
        --windowed ^
        --icon="OneDriveExplorer\Images\ode.ico" ^
        --splash="OneDriveExplorer\Images\splash.png" ^
        --add-data="OneDriveExplorer\Images;Images" ^
        --add-data="OneDriveExplorer\ode;ode" ^
        --hidden-import=tkinter ^
        --hidden-import=ttkthemes ^
        --hidden-import=PIL.Image ^
        --hidden-import=PIL.ImageTk ^
        --hidden-import=pandastable ^
        --hidden-import=ode.views.activity_timeline ^
        --hidden-import=ode.views.data_summary ^
        --hidden-import=ode.views.collaboration_report ^
        --hidden-import=ode.views.sync_status_dashboard ^
        --hidden-import=ode.views.file_analytics ^
        --exclude-module=matplotlib ^
        --exclude-module=scipy ^
        --noconfirm ^
        "OneDriveExplorer\OneDriveExplorer_GUI.py"
) else (
    if exist "%SPEC_FILE%" (
        echo Using spec file: %SPEC_FILE%
        echo %BLUE%Building with comprehensive configuration...%NC%
        echo.
        %PYTHON_CMD% -m PyInstaller --noconfirm "%SPEC_FILE%"
    ) else (
        echo %YELLOW%Spec file not found, using default build...%NC%
        echo.
        %PYTHON_CMD% -m PyInstaller ^
            --name="%APP_NAME%" ^
            --windowed ^
            --icon="OneDriveExplorer\Images\ode.ico" ^
            --splash="OneDriveExplorer\Images\splash.png" ^
            --add-data="OneDriveExplorer\Images;Images" ^
            --add-data="OneDriveExplorer\ode;ode" ^
            --hidden-import=tkinter ^
            --hidden-import=ttkthemes ^
            --hidden-import=PIL.Image ^
            --hidden-import=PIL.ImageTk ^
            --hidden-import=pandastable ^
            --hidden-import=ode.views.activity_timeline ^
            --hidden-import=ode.views.data_summary ^
            --hidden-import=ode.views.collaboration_report ^
            --hidden-import=ode.views.sync_status_dashboard ^
            --hidden-import=ode.views.file_analytics ^
            --exclude-module=matplotlib ^
            --exclude-module=scipy ^
            --noconfirm ^
            "OneDriveExplorer\OneDriveExplorer_GUI.py"
    )
)

if errorlevel 1 (
    echo.
    echo %RED%ERROR: Build failed!%NC%
    echo Check the output above for errors
    pause
    exit /b 1
)

echo.
echo %GREEN%Build completed successfully!%NC%
echo.

REM ============================================================================
REM Verify Build Output
REM ============================================================================
echo %YELLOW%[7/8] Verifying build output...%NC%

if "%1"=="onefile" (
    set "EXE_PATH=%BUILD_DIR%\%APP_NAME%.exe"
) else (
    set "EXE_PATH=%BUILD_DIR%\%APP_NAME%\%APP_NAME%.exe"
)

if exist "!EXE_PATH!" (
    echo %GREEN%Executable found: !EXE_PATH!%NC%

    REM Get file size
    for %%A in ("!EXE_PATH!") do set "SIZE=%%~zA"
    set /a SIZE_MB=!SIZE! / 1048576
    echo File size: !SIZE_MB! MB

    REM Check for required files in distribution
    if "%1" neq "onefile" (
        if exist "%BUILD_DIR%\%APP_NAME%\Images" (
            echo %GREEN%Images directory: OK%NC%
        ) else (
            echo %YELLOW%Warning: Images directory not found in distribution%NC%
        )

        if exist "%BUILD_DIR%\%APP_NAME%\ode" (
            echo %GREEN%ODE package: OK%NC%
        ) else (
            echo %YELLOW%Warning: ODE package not found in distribution%NC%
        )
    )
) else (
    echo %RED%ERROR: Executable not found at expected location%NC%
    echo Expected: !EXE_PATH!
    pause
    exit /b 1
)
echo.

REM ============================================================================
REM Build Summary
REM ============================================================================
echo %YELLOW%[8/8] Build Summary%NC%
echo.
echo %BLUE%============================================================================%NC%
echo %GREEN%BUILD SUCCESSFUL!%NC%
echo %BLUE%============================================================================%NC%
echo.
echo Build Type:        %1
if "%1"=="onefile" (
    echo Output Directory:  %BUILD_DIR%\
    echo Executable:        %APP_NAME%.exe
) else (
    echo Output Directory:  %BUILD_DIR%\%APP_NAME%\
    echo Executable:        %APP_NAME%.exe
)
echo.
echo %GREEN%New Features Included:%NC%
echo   [X] Activity Timeline Report
echo   [X] Data Summary Dashboard
echo   [X] Collaboration Report
echo   [X] Sync Status Dashboard
echo   [X] File Analytics
echo.
echo %YELLOW%Next Steps:%NC%
echo   1. Test the executable: !EXE_PATH!
echo   2. Create distribution package: package_dist.bat
echo   3. Test on clean Windows machine
echo.
echo %BLUE%============================================================================%NC%
echo.

REM ============================================================================
REM Ask to create distribution package
REM ============================================================================
set /p "CREATE_DIST=Create distribution ZIP package? (Y/N): "
if /i "%CREATE_DIST%"=="Y" (
    if exist "package_dist.bat" (
        echo.
        echo Creating distribution package...
        call package_dist.bat
    ) else (
        echo %YELLOW%package_dist.bat not found. Skipping...%NC%
    )
)

echo.
echo %GREEN%Done!%NC%
echo.
pause
