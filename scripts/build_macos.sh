#!/usr/bin/env bash
# ==============================================================================
# FoolGit macOS Compilation & Packaging Script
# Builds standalone CLI binary, FoolGit.app bundle, and optional DMG installer.
# ==============================================================================

set -e

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m"

echo -e "${BOLD}${CYAN}=== Building FoolGit for macOS ===${NC}\n"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# 1. Detect Python with PyInstaller & PyQt6
PY_BIN=""
if python3 -c "import PyInstaller, PyQt6" &>/dev/null; then
    PY_BIN="python3"
elif [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python" ]; then
    PY_BIN="/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python"
elif [ -f "${HOME}/miniconda3/envs/playground/bin/python" ]; then
    PY_BIN="${HOME}/miniconda3/envs/playground/bin/python"
fi

if [ -z "${PY_BIN}" ]; then
    echo -e "${RED}[ERROR] Could not find Python environment with both 'PyInstaller' and 'PyQt6'.${NC}"
    echo -e "Please install them via: ${BOLD}pip install pyinstaller PyQt6${NC}"
    exit 1
fi

echo -e "▸ Using Python: ${GREEN}${PY_BIN}${NC}"
${PY_BIN} --version

# Clean previous build artifacts
rm -rf build dist
export PYINSTALLER_CONFIG_DIR="${PROJECT_ROOT}/build/pyinstaller_cache"

# 2. Build Standalone CLI Binary (foolgit)
echo -e "\n${BOLD}[1/3] Compiling CLI binary (foolgit)...${NC}"
${PY_BIN} -m PyInstaller \
    --name "foolgit" \
    --onefile \
    --clean \
    --noconfirm \
    --add-data "foolgit_pkg:foolgit_pkg" \
    foolgit

echo -e "${GREEN}✓ CLI binary built at dist/foolgit${NC}"

# 3. Build Standalone macOS App Bundle (FoolGit.app)
echo -e "\n${BOLD}[2/3] Compiling macOS Desktop App (FoolGit.app)...${NC}"
${PY_BIN} -m PyInstaller \
    --name "FoolGit" \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --osx-bundle-identifier "com.foolgit.app" \
    --add-data "foolgit_pkg:foolgit_pkg" \
    foolgit-gui

echo -e "${GREEN}✓ macOS Application built at dist/FoolGit.app${NC}"

# 4. Optional: Create macOS DMG image using native hdiutil
echo -e "\n${BOLD}[3/3] Packaging into DMG installer (FoolGit.dmg)...${NC}"
DMG_NAME="dist/FoolGit-1.0.0-macOS.dmg"
DMG_TEMP_DIR="dist/dmg_staging"
rm -rf "${DMG_TEMP_DIR}" "${DMG_NAME}"
mkdir -p "${DMG_TEMP_DIR}"

# Copy App to staging
cp -R "dist/FoolGit.app" "${DMG_TEMP_DIR}/"
# Create symlink to /Applications for drag-and-drop installation
ln -s /Applications "${DMG_TEMP_DIR}/Applications"

# Build DMG
hdiutil create -volname "FoolGit" -srcfolder "${DMG_TEMP_DIR}" -ov -format UDZO "${DMG_NAME}"
rm -rf "${DMG_TEMP_DIR}"

echo -e "${GREEN}✓ DMG installer created at ${DMG_NAME}${NC}"

echo -e "\n${BOLD}${GREEN}=== macOS Build Completed Successfully! ===${NC}"
echo -e "Artifacts generated in ${BOLD}dist/${NC}:"
echo -e "  • ${CYAN}dist/foolgit${NC}                   (Standalone Terminal CLI executable)"
echo -e "  • ${CYAN}dist/FoolGit.app${NC}               (macOS Application bundle)"
echo -e "  • ${CYAN}dist/FoolGit-1.0.0-macOS.dmg${NC}   (macOS Drag-and-Drop DMG Installer)\n"
