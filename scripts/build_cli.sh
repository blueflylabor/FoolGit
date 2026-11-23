#!/usr/bin/env bash
# ==============================================================================
# FoolGit Standalone CLI Compilation Script (macOS & Linux)
# Builds a lightweight, single-file executable for the terminal version.
# Requires ONLY Python 3 and PyInstaller (NO Qt / GUI dependencies needed).
# ==============================================================================

set -e

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m"

echo -e "${BOLD}${CYAN}=== Building FoolGit CLI (Standalone Binary) ===${NC}\n"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# 1. Locate Python with PyInstaller
PY_BIN=""
if python3 -c "import PyInstaller" &>/dev/null; then
    PY_BIN="python3"
elif [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python" ]; then
    PY_BIN="/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python"
elif [ -f "${HOME}/miniconda3/envs/playground/bin/python" ]; then
    PY_BIN="${HOME}/miniconda3/envs/playground/bin/python"
fi

if [ -z "${PY_BIN}" ]; then
    echo -e "${RED}[ERROR] PyInstaller was not found in your Python environment.${NC}"
    echo -e "Install it with: ${BOLD}pip install pyinstaller${NC}"
    exit 1
fi

echo -e "▸ Compiler Python: ${GREEN}${PY_BIN}${NC}"
echo -e "▸ Target binary: ${BOLD}dist/foolgit${NC}"

# Clean previous build
mkdir -p build/pyinstaller_cache dist
export PYINSTALLER_CONFIG_DIR="${PROJECT_ROOT}/build/pyinstaller_cache"

# 2. Compile lightweight CLI binary
# Explicitly exclude PyQt6 and heavy GUI frameworks to keep binary lean (~12MB)
echo -e "\n${BOLD}▸ Compiling standalone CLI binary with PyInstaller...${NC}"
${PY_BIN} -m PyInstaller \
    --name "foolgit" \
    --onefile \
    --clean \
    --noconfirm \
    --exclude-module PyQt6 \
    --exclude-module PyQt5 \
    --exclude-module PySide6 \
    --exclude-module PySide2 \
    --exclude-module tkinter \
    --add-data "foolgit_pkg:foolgit_pkg" \
    scripts/cli_main.py

echo -e "\n${BOLD}${GREEN}=== CLI Build Successful! ===${NC}"
echo -e "Executable generated at: ${BOLD}${CYAN}${PROJECT_ROOT}/dist/foolgit${NC}"
echo -e "\nTo install it system-wide, simply run:"
echo -e "  ${BOLD}sudo cp dist/foolgit /usr/local/bin/${NC}"
echo -e "Or add it to your user local bin:"
echo -e "  ${BOLD}cp dist/foolgit ~/.local/bin/${NC}\n"
