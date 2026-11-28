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
        print("  log | history  Show recent snapshot timeline")
        print("  web            Open remote repository in browser")
        print("  pr             Open Create Pull Request / Compare page")
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

    # One-shot fast CLI subcommands
    if args and args[0] in ("sync", "pull", "status", "s", "log", "history", "web", "pr"):
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
            has_id, _, _ = eng.check_git_identity()
            if not has_id:
                print(f"🪪 {t('identity_missing_desc')}")
                sys.exit(1)
            msg = " ".join(args[1:]).strip() or None
            ok, logs = eng.one_click_sync(msg)
            for l in logs:
                print(l)
            if ok:
                pr_url = eng.get_pr_compare_url()
                if pr_url:
                    print(t("pr_available_hint", url=pr_url))
            sys.exit(0 if ok else 1)
        elif subcmd == "pull":
            ok, msg = eng.safe_pull()
            print(msg)
            sys.exit(0 if ok else 1)
        elif subcmd in ("log", "history"):
            for item in eng.get_recent_history(10):
                parts = item.split("|")
                if len(parts) >= 4:
                    h, author, when, msg = parts[0], parts[1], parts[2], parts[3]
                    deco = f" {parts[4].strip()}" if len(parts) >= 5 and parts[4].strip() else ""
                    print(f"● {h}{deco}  ─  {msg} ({when} · {author})")
                else:
                    print(item)
            sys.exit(0)
        elif subcmd == "web":
            import webbrowser
            web_url = eng.get_remote_web_url()
            if not web_url:
                print(t("gui_no_web_remote"))
                sys.exit(1)
            webbrowser.open(web_url)
            print(t("opened_in_browser", url=web_url))
            sys.exit(0)
        elif subcmd == "pr":
            import webbrowser
            pr_url = eng.get_pr_compare_url()
            if not pr_url:
                print(t("pr_not_feature_branch"))
                sys.exit(1)
            webbrowser.open(pr_url)
            print(t("opened_in_browser", url=pr_url))
            sys.exit(0)
        else:
            info = eng.get_info()
            oid = f" ({info['commit_oid']})" if info.get("commit_oid") else ""
            print(f"📁 {info['name']}  🌿 {info['branch']}{oid}")
            print(f"⚡ {eng.get_sync_preview()}")
            if info.get("conflicts"):
                print(f"🚑 {t('conflict_banner_cli', count=len(info['conflicts']))}")
            sys.exit(0)

    target_dir = args[0] if args and not args[0].startswith("-") else "."
    cli = FoolGitCLI(target_dir=target_dir)
    cli.run()


if __name__ == "__main__":
    main()
