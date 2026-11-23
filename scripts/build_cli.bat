@echo off
REM ==============================================================================
REM FoolGit Windows Standalone CLI Compilation Script
REM Builds a lightweight foolgit.exe with zero Qt dependencies.
REM ==============================================================================

echo === Building FoolGit CLI (Standalone Windows Executable) ===

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller is required.
    echo Please run: pip install pyinstaller
    exit /b 1
)

if not exist build mkdir build
if not exist dist mkdir dist

echo Compiling dist\foolgit.exe ...
python -m PyInstaller ^
    --name "foolgit" ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --exclude-module PyQt6 ^
    --exclude-module PyQt5 ^
    --exclude-module tkinter ^
    --add-data "foolgit_pkg;foolgit_pkg" ^
    scripts\cli_main.py

echo.
echo === CLI Build Complete! ===
echo Generated executable: dist\foolgit.exe
