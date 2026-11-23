@echo off
REM ==============================================================================
REM FoolGit Windows Compilation Script
REM Builds standalone foolgit.exe (CLI) and foolgit-gui.exe (GUI)
REM ==============================================================================

echo === Building FoolGit for Windows ===

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    exit /b 1
)

python -c "import PyInstaller, PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller and PyQt6 are required.
    echo Please run: pip install pyinstaller PyQt6
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [1/2] Compiling Windows CLI binary (foolgit.exe)...
python -m PyInstaller ^
    --name "foolgit" ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --add-data "foolgit_pkg;foolgit_pkg" ^
    foolgit

echo [2/2] Compiling Windows GUI binary (foolgit-gui.exe)...
python -m PyInstaller ^
    --name "foolgit-gui" ^
    --windowed ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --add-data "foolgit_pkg;foolgit_pkg" ^
    foolgit-gui

echo.
echo === Windows Build Complete! ===
echo Output binaries located in dist\
echo   - dist\foolgit.exe
echo   - dist\foolgit-gui.exe
