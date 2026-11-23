#!/usr/bin/env python3
"""
FoolGit 纯 CLI 入口 (用于独立打包 CLI 二进制程序)
零外部依赖，完全不引用 PyQt6 或任何 GUI 库，确保打包出的二进制体积极小、启动极快。
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from foolgit_pkg import __version__
from foolgit_pkg.cli import FoolGitCLI


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "."

    if "-v" in sys.argv or "--version" in sys.argv:
        print(f"FoolGit version {__version__}")
        sys.exit(0)

    if "-h" in sys.argv or "--help" in sys.argv:
        print("FoolGit - Simple & Foolproof Git Assistant (CLI Edition)")
        print("Usage: foolgit [path] [options]")
        print("Options:")
        print("  -v, --version  Show version number")
        print("  -h, --help     Show this help message")
        print("\nRun 'foolgit' directly inside any Git repository to start.")
        sys.exit(0)

    cli = FoolGitCLI(target_dir=target_dir)
    cli.run()


if __name__ == "__main__":
    main()
