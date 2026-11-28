"""
FoolGit CLI 可执行入口模块 (用于 setup.py / pyproject.toml entry_points 与 CLI 分发)
"""

import sys
import os

from . import __version__
from .cli import FoolGitCLI


def main():
    args = sys.argv[1:]

    if "-v" in args or "--version" in args:
        print(f"FoolGit version {__version__}")
        sys.exit(0)

    if "-h" in args or "--help" in args:
        print("FoolGit - Simple & Foolproof Git Assistant")
        print("Usage: foolgit [path | command] [options]")
        print("Commands:")
        print("  sync [msg]     One-click pull, add, commit & push")
        print("  pull           Safely pull latest remote updates")
        print("  status | s     Show concise repo status & sync preview")
        print("  gui            Launch PyQt6 lightweight desktop GUI")
        print("Options:")
        print("  -g, --gui      Launch PyQt6 lightweight desktop GUI")
        print("  -v, --version  Show version number")
        print("  -h, --help     Show this help message")
        print("\nRun 'foolgit' directly inside any Git repository for interactive menu.")
        sys.exit(0)

    if "-g" in args or "--gui" in args or (args and args[0] == "gui"):
        target_dir = args[1] if (args and args[0] == "gui" and len(args) > 1) else (
            args[0] if (args and not args[0].startswith("-") and args[0] != "gui") else "."
        )
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
        import importlib
        gui_mod = importlib.import_module("foolgit_pkg.gui")
        gui_mod.launch_gui(target_dir=target_dir)
        sys.exit(0)

    # One-shot fast CLI subcommands (sync / pull / status / s)
    if args and args[0] in ("sync", "pull", "status", "s"):
        from .config import ConfigManager
        from .core import GitEngine, is_git_repo
        from .i18n import t
        ConfigManager()
        if not is_git_repo("."):
            print(t("not_git_error"))
            sys.exit(1)
        eng = GitEngine(".")
        subcmd = args[0]
        if subcmd == "sync":
            msg = " ".join(args[1:]).strip() or None
            ok, logs = eng.one_click_sync(msg)
            for l in logs:
                print(l)
            sys.exit(0 if ok else 1)
        elif subcmd == "pull":
            ok, msg = eng.safe_pull()
            print(msg)
            sys.exit(0 if ok else 1)
        else:
            info = eng.get_info()
            oid = f" ({info['commit_oid']})" if info.get("commit_oid") else ""
            print(f"📁 {info['name']}  🌿 {info['branch']}{oid}")
            print(f"⚡ {eng.get_sync_preview()}")
            sys.exit(0)

    target_dir = args[0] if args and not args[0].startswith("-") else "."
    cli = FoolGitCLI(target_dir=target_dir)
    cli.run()


if __name__ == "__main__":
    main()
