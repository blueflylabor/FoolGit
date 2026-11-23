#!/usr/bin/env bash
# ==============================================================================
# FoolGit Uninstaller
# Removes global symlinks and macOS application bundle.
# ==============================================================================

set -e

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
NC="\033[0m"

echo -e "${BOLD}=== Uninstalling FoolGit ===${NC}\n"

# Remove symlinks
for dir in "/usr/local/bin" "${HOME}/.local/bin"; do
    if [ -L "${dir}/foolgit" ]; then
        if [ -w "${dir}" ]; then
            rm -f "${dir}/foolgit" "${dir}/foolgit-gui"
        else
            sudo rm -f "${dir}/foolgit" "${dir}/foolgit-gui"
        fi
        echo -e "Removed symlinks from ${dir}"
    fi
done

# Remove macOS Application
if [ -d "${HOME}/Applications/FoolGit.app" ]; then
    rm -rf "${HOME}/Applications/FoolGit.app"
    echo -e "Removed macOS Application ${HOME}/Applications/FoolGit.app"
fi

echo -e "\n${BOLD}${GREEN}FoolGit uninstalled successfully.${NC}"
