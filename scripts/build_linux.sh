#!/usr/bin/env bash
# ==============================================================================
# FoolGit Linux Compilation Script
# Builds standalone CLI and GUI binaries, plus a desktop menu entry.
# ==============================================================================

set -e

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
RED="\033[31m"
NC="\033[0m"

echo -e "${BOLD}${CYAN}=== Building FoolGit for Linux ===${NC}\n"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

if ! command -v pyinstaller &>/dev/null && ! python3 -m PyInstaller --version &>/dev/null; then
    echo -e "${RED}[ERROR] PyInstaller is required. Run: pip install pyinstaller PyQt6${NC}"
    exit 1
fi

rm -rf build dist

# 1. Build CLI binary
echo -e "${BOLD}[1/2] Compiling Linux CLI binary...${NC}"
python3 -m PyInstaller \
    --name "foolgit" \
    --onefile \
    --clean \
    --noconfirm \
    --add-data "foolgit_pkg:foolgit_pkg" \
    foolgit

# 2. Build GUI binary
echo -e "${BOLD}[2/2] Compiling Linux GUI binary...${NC}"
python3 -m PyInstaller \
    --name "foolgit-gui" \
    --onefile \
    --clean \
    --noconfirm \
    --add-data "foolgit_pkg:foolgit_pkg" \
    foolgit-gui

# Create a sample .desktop launcher
cat << EOF > dist/foolgit.desktop
[Desktop Entry]
Name=FoolGit
Comment=Simple & Foolproof Git Assistant
Exec=foolgit-gui
Terminal=false
Type=Application
Categories=Development;RevisionControl;
EOF

echo -e "\n${BOLD}${GREEN}=== Linux Build Complete! ===${NC}"
echo -e "Artifacts in dist/:"
echo -e "  • dist/foolgit (CLI)"
echo -e "  • dist/foolgit-gui (GUI)"
echo -e "  • dist/foolgit.desktop"
