@echo off
REM ============================================================================
REM OneDriveExplorer GUI - Clean Build Artifacts
REM ============================================================================
REM This script removes all build artifacts, caches, and temporary files
REM Use this before a fresh build or when troubleshooting build issues
REM ============================================================================

setlocal

REM Set colors
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

echo.
echo %BLUE%============================================================================%NC%
echo %BLUE%   OneDriveExplorer - Clean Build Artifacts%NC%
echo %BLUE%============================================================================%NC%
echo.

echo %YELLOW%This will remove the following:%NC%
echo   - build/ directory
echo   - dist/ directory
echo   - *.spec files
echo   - __pycache__/ directories
echo   - *.pyc files
echo   - .pytest_cache/ directories
echo.

set /p "CONFIRM=Are you sure? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo %YELLOW%Cleaning build artifacts...%NC%
echo.

REM Remove build directory
if exist "build\" (
    echo Removing build\...
    rmdir /s /q "build\" 2>nul
    if errorlevel 1 (
        echo %RED%Warning: Could not remove build\ directory%NC%
    ) else (
        echo %GREEN%OK%NC%
    )
) else (
    echo build\ - not found
)

REM Remove dist directory
if exist "dist\" (
    echo Removing dist\...
    rmdir /s /q "dist\" 2>nul
    if errorlevel 1 (
        echo %RED%Warning: Could not remove dist\ directory%NC%
    ) else (
        echo %GREEN%OK%NC%
    )
) else (
    echo dist\ - not found
)

REM Remove .spec files
echo Removing *.spec files...
del /q "*.spec" 2>nul
if errorlevel 1 (
    echo No .spec files found
) else (
    echo %GREEN%OK%NC%
)

REM Remove __pycache__ directories
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo   Removing %%d
        rmdir /s /q "%%d" 2>nul
    )
)
echo %GREEN%OK%NC%

REM Remove .pyc files
echo Removing *.pyc files...
del /s /q "*.pyc" 2>nul
if errorlevel 1 (
    echo No .pyc files found
) else (
    echo %GREEN%OK%NC%
)

REM Remove .pytest_cache directories
echo Removing .pytest_cache directories...
for /d /r . %%d in (.pytest_cache) do (
    if exist "%%d" (
        echo   Removing %%d
        rmdir /s /q "%%d" 2>nul
    )
)
echo %GREEN%OK%NC%

REM Remove ode.settings if user wants
echo.
set /p "REMOVE_SETTINGS=Remove ode.settings? (Y/N): "
if /i "%REMOVE_SETTINGS%"=="Y" (
    if exist "OneDriveExplorer\ode.settings" (
        echo Removing ode.settings...
        del /q "OneDriveExplorer\ode.settings" 2>nul
        echo %GREEN%OK%NC%
    )
)

echo.
echo %GREEN%============================================================================%NC%
echo %GREEN%   Clean Complete!%NC%
echo %GREEN%============================================================================%NC%
echo.
echo You can now run build.bat for a fresh build
echo.
pause
