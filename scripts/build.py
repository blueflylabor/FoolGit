#!/usr/bin/env python3
"""
FoolGit Universal Build Runner
Compiles CLI and GUI standalone binaries for the current operating system.
Usage:
    python scripts/build.py [--all] [--cli] [--gui] [--dmg]
"""

import sys
import os
import shutil
import platform
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_pyinstaller():
    """Find Python executable with PyInstaller and PyQt6"""
    # 1. Current Python
    try:
        import PyInstaller
        return sys.executable
    except ImportError:
        pass

    # 2. Known virtualenvs / conda envs
    candidates = [
        "/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python",
        os.path.expanduser("~/miniconda3/envs/playground/bin/python"),
        os.path.expanduser("~/.conda/envs/playground/bin/python"),
    ]
    for c in candidates:
        if os.path.exists(c):
            res = subprocess.run([c, "-c", "import PyInstaller; print('ok')"], capture_output=True, text=True)
            if res.returncode == 0:
                return c
    return None


def build_cli(py_bin: str):
    """Build standalone CLI binary (Lightweight, excludes GUI/Qt)"""
    print("\n📦 Building standalone CLI executable...")
    sep = ";" if platform.system() == "Windows" else ":"
    env = os.environ.copy()
    cache_dir = str(PROJECT_ROOT / "build" / "pyinstaller_cache")
    env["PYINSTALLER_CONFIG_DIR"] = cache_dir

    cmd = [
        py_bin, "-m", "PyInstaller",
        "--name", "foolgit",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--exclude-module", "PyQt6",
        "--exclude-module", "PyQt5",
        "--exclude-module", "PySide6",
        "--exclude-module", "tkinter",
        "--add-data", f"foolgit_pkg{sep}foolgit_pkg",
        str(PROJECT_ROOT / "scripts" / "cli_main.py")
    ]
    subprocess.check_call(cmd, cwd=str(PROJECT_ROOT), env=env)
    print("✅ CLI build complete: dist/foolgit")


def build_gui(py_bin: str):
    """Build standalone GUI desktop app"""
    print("\n🖥️  [2/2] Building desktop GUI...")
    sep = ";" if platform.system() == "Windows" else ":"
    is_mac = platform.system() == "Darwin"
    env = os.environ.copy()
    cache_dir = str(PROJECT_ROOT / "build" / "pyinstaller_cache")
    env["PYINSTALLER_CONFIG_DIR"] = cache_dir

    cmd = [
        py_bin, "-m", "PyInstaller",
        "--name", "FoolGit" if is_mac else "foolgit-gui",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data", f"foolgit_pkg{sep}foolgit_pkg",
    ]
    
    if is_mac:
        cmd.extend([
            "--onedir",
            "--osx-bundle-identifier", "com.foolgit.app",
        ])
    else:
        cmd.append("--onefile")

    cmd.append(str(PROJECT_ROOT / "foolgit-gui"))
    subprocess.check_call(cmd, cwd=str(PROJECT_ROOT), env=env)
    
    if is_mac:
        print("✅ macOS App complete: dist/FoolGit.app")
    else:
        print("✅ GUI build complete: dist/foolgit-gui")


def build_dmg():
    """Build macOS DMG installer"""
    if platform.system() != "Darwin":
        print("⚠️ DMG creation is only supported on macOS.")
        return
    print("\n💿 Packaging macOS DMG installer...")
    dmg_out = PROJECT_ROOT / "dist" / "FoolGit-1.0.0-macOS.dmg"
    staging = PROJECT_ROOT / "dist" / "dmg_staging"
    
    if staging.exists():
        shutil.rmtree(staging)
    if dmg_out.exists():
        dmg_out.unlink()

    staging.mkdir(parents=True)
    app_source = PROJECT_ROOT / "dist" / "FoolGit.app"
    if not app_source.exists():
        print("❌ Error: dist/FoolGit.app not found. Build GUI first.")
        return

    shutil.copytree(app_source, staging / "FoolGit.app")
    os.symlink("/Applications", staging / "Applications")

    subprocess.check_call([
        "hdiutil", "create",
        "-volname", "FoolGit",
        "-srcfolder", str(staging),
        "-ov", "-format", "UDZO",
        str(dmg_out)
    ])
    shutil.rmtree(staging)
    print(f"🎉 DMG ready: {dmg_out}")


def main():
    py_bin = find_pyinstaller()
    if not py_bin:
        print("❌ Error: Could not find Python environment with PyInstaller.")
        print("Please run: pip install pyinstaller PyQt6")
        sys.exit(1)

    print(f"🔧 Using Python with PyInstaller: {py_bin}")
    os.chdir(str(PROJECT_ROOT))

    args = sys.argv[1:]
    build_all = not args or "--all" in args

    if build_all or "--cli" in args:
        build_cli(py_bin)
    if build_all or "--gui" in args:
        build_gui(py_bin)
    if (build_all and platform.system() == "Darwin") or "--dmg" in args:
        build_dmg()

    print("\n✨ All requested build tasks finished! Check the 'dist/' folder.")


if __name__ == "__main__":
    main()
