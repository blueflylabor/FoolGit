#!/usr/bin/env bash
# ==============================================================================
# FoolGit Installer (macOS & Linux)
# Installs 'foolgit' (CLI) and 'foolgit-gui' (PyQt6 Desktop GUI) globally.
# ==============================================================================

set -e

# ANSI Color codes
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m"

echo -e "${BOLD}${CYAN}=== Installing FoolGit ===${NC}\n"

# 1. Resolve source repository root
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "▸ Source directory: ${SOURCE_DIR}"

# 2. Check Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python 3 is required but was not found in PATH.${NC}"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "▸ Detected Python version: ${GREEN}${PY_VER}${NC}"

# 3. Check Git
if ! command -v git &>/dev/null; then
    echo -e "${YELLOW}[WARN] Git is not installed or not in PATH.${NC}"
fi

# 4. Check PyQt6 for GUI
if python3 -c "import PyQt6" &>/dev/null; then
    echo -e "▸ PyQt6 detected: ${GREEN}OK (GUI ready)${NC}"
else
    # Check playground conda environment
    if [ -f "/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python" ]; then
        echo -e "▸ Found PyQt6 in conda playground environment: ${GREEN}OK${NC}"
    else
        echo -e "▸ ${YELLOW}Note: PyQt6 is not in default Python. For GUI, install via: pip install PyQt6${NC}"
    fi
fi

# Ensure scripts are executable
chmod +x "${SOURCE_DIR}/foolgit"
chmod +x "${SOURCE_DIR}/foolgit-gui"

# 5. Determine installation target directory
INSTALL_BIN_DIR="/usr/local/bin"
USE_SUDO=false

if [ "$1" == "--dest" ]; then
    INSTALL_BIN_DIR="$2"
    mkdir -p "${INSTALL_BIN_DIR}"
    echo -e "▸ Custom destination: ${INSTALL_BIN_DIR}"
elif [ "$1" == "--user" ]; then
    INSTALL_BIN_DIR="${HOME}/.local/bin"
    mkdir -p "${INSTALL_BIN_DIR}"
    echo -e "▸ Installing in user mode to: ${INSTALL_BIN_DIR}"
elif [ ! -w "${INSTALL_BIN_DIR}" ]; then
    # If sudo is available and can run passwordless or user explicitly accepts
    if sudo -n true 2>/dev/null; then
        USE_SUDO=true
    elif [ "$EUID" -eq 0 ]; then
        USE_SUDO=false
    else
        # Graceful fallback to user directory ~/.local/bin
        INSTALL_BIN_DIR="${HOME}/.local/bin"
        mkdir -p "${INSTALL_BIN_DIR}" 2>/dev/null || true
        echo -e "▸ /usr/local/bin requires root. Installing to: ${INSTALL_BIN_DIR}"
    fi
fi

# Link CLI and GUI binaries
if [ "$USE_SUDO" = true ]; then
    sudo ln -sf "${SOURCE_DIR}/foolgit" "${INSTALL_BIN_DIR}/foolgit"
    sudo ln -sf "${SOURCE_DIR}/foolgit-gui" "${INSTALL_BIN_DIR}/foolgit-gui"
else
    ln -sf "${SOURCE_DIR}/foolgit" "${INSTALL_BIN_DIR}/foolgit"
    ln -sf "${SOURCE_DIR}/foolgit-gui" "${INSTALL_BIN_DIR}/foolgit-gui"
fi

echo -e "✅ Linked ${BOLD}foolgit${NC} -> ${INSTALL_BIN_DIR}/foolgit"
echo -e "✅ Linked ${BOLD}foolgit-gui${NC} -> ${INSTALL_BIN_DIR}/foolgit-gui"

# 6. macOS Specific: Create a Desktop / Spotlight launcher (.app)
if [ "$(uname)" == "Darwin" ]; then
    APP_DIR="${HOME}/Applications/FoolGit.app"
    if mkdir -p "${APP_DIR}/Contents/MacOS" "${APP_DIR}/Contents/Resources" 2>/dev/null; then
        cat << 'EOF' > "${APP_DIR}/Contents/MacOS/FoolGit"
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "/usr/local/bin/foolgit-gui" ]; then
    exec /usr/local/bin/foolgit-gui "$@"
elif [ -f "${HOME}/.local/bin/foolgit-gui" ]; then
    exec "${HOME}/.local/bin/foolgit-gui" "$@"
fi
EOF
        chmod +x "${APP_DIR}/Contents/MacOS/FoolGit"

        cat << EOF > "${APP_DIR}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FoolGit</string>
    <key>CFBundleIdentifier</key>
    <string>com.foolgit.app</string>
    <key>CFBundleName</key>
    <string>FoolGit</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
        echo -e "✅ Created macOS Application: ${GREEN}${APP_DIR}${NC} (Searchable in Spotlight/Launchpad!)"
    fi
fi

echo -e "\n${BOLD}${GREEN}🎉 FoolGit successfully installed!${NC}"
echo -e "You can now run:"
echo -e "  • ${CYAN}foolgit${NC}       - Open terminal interactive assistant"
echo -e "  • ${CYAN}foolgit-gui${NC}   - Open modern dark PyQt6 desktop app"
echo -e "  • ${CYAN}foolgit --gui${NC} - Open GUI via CLI flag\n"
