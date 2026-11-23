"""
FoolGit CLI 可执行入口模块 (用于 setup.py / pyproject.toml entry_points 与 CLI 分发)
"""

import sys
import os

from . import __version__
from .cli import FoolGitCLI


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "."

    if "-v" in sys.argv or "--version" in sys.argv:
        print(f"FoolGit version {__version__}")
        sys.exit(0)

    if "-h" in sys.argv or "--help" in sys.argv:
        print("FoolGit - Simple & Foolproof Git Assistant")
        print("Usage: foolgit [path] [options]")
        print("Options:")
        print("  -g, --gui      Launch PyQt6 lightweight desktop GUI")
        print("  -v, --version  Show version number")
        print("  -h, --help     Show this help message")
        print("\nRun 'foolgit' directly inside any Git repository to start.")
        sys.exit(0)

    if "-g" in sys.argv or "--gui" in sys.argv:
        try:
            import PyQt6
        except ImportError:
            candidate_pythons = [
                "/opt/homebrew/Caskroom/miniconda/base/envs/playground/bin/python",
                os.path.expanduser("~/miniconda3/envs/playground/bin/python"),
                os.path.expanduser("~/.conda/envs/playground/bin/python"),
            ]
            for py_bin in candidate_pythons:
                if os.path.exists(py_bin):
                    os.execv(py_bin, [py_bin] + sys.argv)
        from .gui import launch_gui
        launch_gui(target_dir=target_dir)
        sys.exit(0)

    cli = FoolGitCLI(target_dir=target_dir)
    cli.run()


if __name__ == "__main__":
    main()
