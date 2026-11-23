# 💡 FoolGit

[English Documentation](README.md) | [简体中文说明](README_zh.md)

> **Simple, Foolproof, and Customizable Git Assistant with CLI & Modern Dark PyQt6 Desktop GUI.**  
> Designed for everyday developers and beginners who only need core Git commands without memorizing obscure flags or dealing with bloated GUI tools.

---

## 🌟 Why FoolGit? (Design Philosophy)

Most developers use only a small subset of Git commands daily: saving work, pulling updates, checking status, undoing mistakes, and switching branches. Traditional tools present two extremes:
- **Git CLI**: Steep learning curve, dozens of obscure flags, and cryptic error messages.
- **Heavy GUI Clients** (Sourcetree, GitKraken, etc.): Overcomplicated commit graph trees, heavy memory usage, and confusing terminology.

**FoolGit provides a clean third way:**
1. **Out-of-the-Box Simplicity**: Defaults strictly to the **6 core everyday actions**. Zero config required.
2. **Pure Multi-Language (Zero Mixed Language)**: Default **English** with optional **Simplified Chinese**. 100% pure text in both modes with zero awkward mixed phrases.
3. **Programmer Dark/Gray Aesthetic**: Modern PyQt6 GUI crafted with a dark charcoal aesthetic (`#121316`), responsive cards, and an integrated real-time hacker terminal console.
4. **Choice-Driven Interaction**: Number keys or one-click buttons instead of long typing.
5. **Extensible on Demand**: Enable extra built-in features (history, diff, tag, clean, multi-repo sync) or add your own custom Git commands with a single click.

---

## 📸 Overview & Interface

### PyQt6 Desktop GUI (Programmer Dark/Gray Theme)
```
┌─────────────────────────────────────────────────────────┐
│ ⚡ FoolGit   v1.0.0                  [Language: English]│
│ 📁 my-project               [main ▾] [+]                │
│ [✨ Clean, nothing to commit]                           │
├─────────────────────────────────────────────────────────┤
│ One-Click Sync & Save                                   │
│ Automatically pulls remote ➔ commits ➔ pushes           │
│ [ Commit message (leave blank for auto timestamp)...  ] │
│ [              🚀  One-Click Sync                     ] │
├─────────────────────────────────────────────────────────┤
│ QUICK ACTIONS                                           │
│ [ ⬇️ Pull Latest Code  ]    [ 🔍 View Changes & Status ]│
│ [ 💊 Undo / Discard    ]    [ 📦 Stash / Restore Edits ]│
├─────────────────────────────────────────────────────────┤
│ [ 📜 History ]   [ 🔍 Diff ]             [ ⚙️ Settings ] │
├─────────────────────────────────────────────────────────┤
│ > FoolGit Ready. Click 'One-Click Sync' to commit & push│
└─────────────────────────────────────────────────────────┘
```

### Interactive Terminal CLI
```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  FoolGit v1.0.0 ── Simple & Foolproof Git Assistant        ┃
┃  📁 Repo: my-project   🌿 Branch: main                     ┃
┃  ⚡ Status: ✎ 2 file(s) changed (Synced with remote ✓)     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

 [1] One-Click Sync [Recommended]
     Auto pull ➔ record changes ➔ commit ➔ push to remote
 [2] Pull Latest Code [Common]
     Safely fetch and merge latest remote updates
 [3] View Changes & Status [Status]
     Overview of changed files, staged files and sync status
 [4] Undo / Discard Changes [Safety]
     Discard unwanted edits or undo the last commit
 [5] Switch or Create Branch [Branch]
     Switch branch by number or create a new branch
 [6] Stash / Restore Edits [Stash]
     Temporarily stash unfinished work and restore anytime

 ----------------------------------------------------
 [+] FoolGit Settings & Feature Store
 [q] Quit

👉 Please select an option [Default: 1, q: Quit]: 
```

---

## ⚡ Core Feature Matrix

| # | Action | Purpose & Underlying Pipeline |
| :---: | :--- | :--- |
| **`[1]`** | **One-Click Sync** *(Recommended)* | Safely pulls remote updates ➔ stages all (`add -A`) ➔ commits (with optional or auto-timestamped message) ➔ pushes to remote. |
| **`[2]`** | **Pull Latest Code** | Fetches and safely merges remote tracking branch; gives clear conflict diagnosis. |
| **`[3]`** | **View Changes & Status** | Color-coded status of staged, modified, and untracked files + line change stats. |
| **`[4]`** | **Undo / Discard Changes** | 3-level safety net: ① Discard ALL uncommitted edits, ② Undo last commit (keep edited code in workspace), ③ Discard a single file. |
| **`[5]`** | **Switch or Create Branch** | Numbered picklist to switch local branches or press `n` to create a new branch. |
| **`[6]`** | **Stash / Restore Edits** | Temporarily packages work-in-progress to clean the working tree, and pops it back anytime. |

### Feature Store & Custom Shortcuts (Accessible via `[+]` or `Settings`)
- **Recent Commit History**: Clean oneline commit timeline with author and relative time.
- **Code Differences (Diff)**: Line-by-line inspection of unstaged/staged edits.
- **Clean Untracked Files**: Removes untracked build artifacts and temporary files.
- **Release Tag Management**: Create release tags (e.g. `v1.0.0`) and optionally push to remote.
- **Remote Configuration**: Inspect remote `origin` URLs.
- **Multi-Repository Batch Sync**: Automatically scan subdirectories for Git repositories and sync them all in batch (evolved from `gsyn`).
- **User Custom Commands**: Define any arbitrary Git command (e.g. `git push origin --tags`) to show up on the main menu.

---

## 🚀 Deployment & Installation

### Option 1: Automated Installer (macOS & Linux - Recommended)
Run the automated installation script inside the project folder:
```bash
./install.sh
```
This script will:
- Verify Python 3 and Git environment.
- Symlink `foolgit` (CLI) and `foolgit-gui` (PyQt6 Desktop GUI) globally to `/usr/local/bin` (or `~/.local/bin`).
- On macOS: Automatically generate `FoolGit.app` in `~/Applications` so you can launch it instantly via **Spotlight**, **Raycast**, or **Launchpad**!

To uninstall:
```bash
./uninstall.sh
```

---

### Option 2: Python `pip` Package Installation
Install directly as a standard Python package:
```bash
# Install core CLI
pip install -e .

# Install with PyQt6 GUI support
pip install -e ".[gui]"
```
Once installed, `foolgit` and `foolgit-gui` are available globally in your terminal.

---

### Option 3: Manual Symlinks
```bash
sudo ln -sf $(pwd)/foolgit /usr/local/bin/foolgit
sudo ln -sf $(pwd)/foolgit-gui /usr/local/bin/foolgit-gui
```

---

## 🛠️ Compilation & Packaging (Standalone Binaries)

FoolGit provides dedicated scripts to compile standalone, self-contained executables and application bundles without requiring users to install Python or PyQt6 manually.

### 🍎 1. macOS Build Guide (CLI, App Bundle & DMG)

Prerequisites:
```bash
pip install pyinstaller PyQt6
```

Run the macOS build script:
```bash
./scripts/build_macos.sh
# Or using the universal runner:
python3 scripts/build.py --all
```

**Generated Artifacts in `dist/`**:
1. **`dist/foolgit`**: Standalone single-binary executable for terminal.
2. **`dist/FoolGit.app`**: Complete macOS Application bundle. Double-click to run or drag into `/Applications`.
3. **`dist/FoolGit-1.0.0-macOS.dmg`**: Drag-and-drop macOS disk image installer.

---

### 🐧 2. Linux Build Guide
Run:
```bash
./scripts/build_linux.sh
```
**Generated Artifacts**:
- `dist/foolgit` (Standalone CLI binary)
- `dist/foolgit-gui` (Standalone GUI binary)
- `dist/foolgit.desktop` (Application menu launcher)

---

### 🪟 3. Windows Build Guide
Run in Command Prompt:
```cmd
scripts\build_windows.bat
```
**Generated Artifacts**:
- `dist\foolgit.exe` (CLI executable)
- `dist\foolgit-gui.exe` (Windowed GUI executable)

---

## 🌐 Language & Configuration Persistence

- **Default Language**: English (`en`)
- **Optional Language**: Simplified Chinese (`zh`)
- **How to Switch**:
  - **In CLI**: Press `+` ➔ Select `[4] Interface Language` to switch.
  - **In GUI**: Click the `Language` button in the top-right corner for live hot-reloading.
- **Configuration Storage**: Preferences are persisted in `~/.foolgit/config.json` (with automatic fallback to local directory if permissions are restricted).

---

## 📂 Project Structure

```text
FoolGit/
├── foolgit                 # Terminal CLI launcher script
├── foolgit-gui             # PyQt6 Desktop GUI launcher script
├── setup.py                # Standard setuptools configuration
├── pyproject.toml          # PEP 518 / 621 packaging metadata
├── install.sh              # One-click installer for macOS / Linux
├── uninstall.sh            # Uninstaller script
├── foolgit_pkg/
│   ├── __init__.py         # Package version and metadata
│   ├── cli_entry.py        # Central CLI entry dispatcher
│   ├── core.py             # Git core engine (CLI & GUI shared)
│   ├── config.py           # Configuration & language persistence
│   ├── i18n.py             # Pure multi-language localization engine
│   ├── presets.py          # Built-in feature library & metadata
│   ├── cli.py              # Minimalist interactive terminal UI
│   └── gui.py              # PyQt6 Modern Dark/Gray desktop UI
├── scripts/
│   ├── build.py            # Universal cross-platform build orchestrator
│   ├── build_macos.sh      # macOS compilation script (CLI, .app, .dmg)
│   ├── build_linux.sh      # Linux compilation script
│   └── build_windows.bat   # Windows compilation script
├── README.md               # English documentation
└── README_zh.md            # Simplified Chinese documentation
```

---

## 📄 License

MIT License. Free and open source.
