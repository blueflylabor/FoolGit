"""
FoolGit 终端交互 UI (CLI)
支持多语言 (默认英文 en，可选中文 zh) 与个性化设置持久化。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from .core import GitEngine, is_git_repo, scan_multi_repos, run_git
from .config import ConfigManager
from .presets import get_preset_info, ALL_PRESET_IDS
from .i18n import t, get_language

# 终端 ANSI 颜色常量 (轻量跨平台)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
GRAY = "\033[90m"


def c(text: str, color: str) -> str:
    """包装带颜色的文本"""
    return f"{color}{text}{RESET}"


def prompt_press_enter():
    """等待用户敲回车继续"""
    try:
        input(f"\n{c(t('press_enter_to_continue'), DIM)}")
    except (KeyboardInterrupt, EOFError):
        pass


class FoolGitCLI:
    """FoolGit 交互式控制台"""

    def __init__(self, target_dir: str = "."):
        self.target_dir = target_dir
        self.config_mgr = ConfigManager()

    def run(self):
        """主入口调度"""
        try:
            if not is_git_repo(self.target_dir):
                self._handle_non_git_dir()
            else:
                self._run_single_repo_menu()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{c(t('goodbye'), YELLOW)}")
            sys.exit(0)

    # ─────────────────────────────────────────────────────────
    # 单仓库主界面与流程
    # ─────────────────────────────────────────────────────────

    def _render_header(self, info: Dict[str, Any]):
        """渲染顶部直观健康卡片"""
        print()
        repo_name = info["name"]
        branch = info["branch"]
        clean_status = c(t("clean_status"), GREEN) if info["is_clean"] else c(t("dirty_status", count=info["total_changes"]), YELLOW)

        sync_status = ""
        if info["has_upstream"]:
            if info["ahead"] > 0 and info["behind"] > 0:
                sync_status = c(t("sync_diverged", ahead=info["ahead"], behind=info["behind"]), MAGENTA)
            elif info["ahead"] > 0:
                sync_status = c(t("sync_ahead", count=info["ahead"]), CYAN)
            elif info["behind"] > 0:
                sync_status = c(t("sync_behind", count=info["behind"]), BLUE)
            else:
                sync_status = c(t("sync_up_to_date"), GREEN)
        else:
            sync_status = c(t("no_upstream"), GRAY)

        title_text = t("app_title")
        print(c("┏" + "━" * 60 + "┓", CYAN))
        print(c("┃", CYAN) + f"  {BOLD}{title_text}{RESET}".ljust(68) + c("┃", CYAN))
        header_line = f"  📁 {t('repo_label')}: {c(repo_name, BOLD)}   🌿 {t('branch_label')}: {c(branch, GREEN)}"
        print(c("┃", CYAN) + header_line.ljust(68) + c("┃", CYAN))
        status_line = f"  ⚡ {t('status_label')}: {clean_status}{sync_status}"
        print(c("┃", CYAN) + status_line.ljust(76) + c("┃", CYAN))
        print(c("┗" + "━" * 60 + "┛", CYAN))
        print()

    def _run_single_repo_menu(self):
        """单仓库循环主菜单"""
        while True:
            engine = GitEngine(self.target_dir)
            info = engine.get_info()

            self._render_header(info)

            # 获取当前开启的菜单列表
            active_ids = self.config_mgr.get_active_preset_ids()
            custom_cmds = self.config_mgr.get_custom_commands()

            menu_items = []
            # 1. 预设功能 (动态本地化)
            for pid in active_ids:
                if pid in ALL_PRESET_IDS:
                    meta = get_preset_info(pid)
                    menu_items.append({
                        "type": "preset",
                        "id": pid,
                        "name": meta["name"],
                        "tag": meta.get("tag", ""),
                        "desc": meta["short_desc"],
                    })

            # 2. 自定义命令
            for c_cmd in custom_cmds:
                menu_items.append({
                    "type": "custom",
                    "id": c_cmd["id"],
                    "name": c_cmd["name"],
                    "tag": "Custom" if get_language() == "en" else "自定",
                    "desc": c_cmd["desc"],
                    "raw_cmd": c_cmd["cmd"],
                })

            # 打印菜单
            for idx, item in enumerate(menu_items, start=1):
                tag_str = f" {c('[' + item['tag'] + ']', MAGENTA)}" if item.get("tag") else ""
                highlight = c(f"[{idx}]", BOLD + GREEN if idx == 1 else BOLD + CYAN)
                print(f" {highlight} {BOLD}{item['name']}{RESET}{tag_str}")
                print(f"     {c(item['desc'], GRAY)}")

            print(f"\n {c('----------------------------------------------------', GRAY)}")
            print(f" {c('[+]', BOLD + YELLOW)} {BOLD}{t('settings_title')}{RESET}")
            print(f" {c('[q]', BOLD + RED)} {BOLD}Quit / 退出{RESET}")
            print()

            # 用户输入
            choice = input(f"{BOLD}{t('prompt_choice')}{RESET}").strip()

            if choice.lower() in ["q", "quit", "exit"]:
                print(c(t("goodbye"), GREEN))
                break

            if choice == "":
                choice = "1"

            if choice == "+":
                self._menu_manage_features()
                continue

            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(menu_items):
                    selected = menu_items[num - 1]
                    self._dispatch_action(engine, selected)
                else:
                    print(c(t("out_of_range", choice=choice), RED))
                    prompt_press_enter()
            else:
                print(c(t("invalid_choice"), RED))
                prompt_press_enter()

    def _dispatch_action(self, engine: GitEngine, item: Dict[str, Any]):
        """执行具体选项对应的操作"""
        itype = item["type"]
        item_id = item["id"]

        print()
        if itype == "custom":
            raw_cmd = item["raw_cmd"]
            print(c(f"🚀 Running custom command: {raw_cmd}", BOLD + CYAN))
            res = run_git(raw_cmd.replace("git ", "").split(), cwd=engine.repo_path)
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(c(res.stderr, YELLOW if res.success else RED))
            if res.success:
                print(c("✅ Completed!", GREEN))
            else:
                print(c("❌ Command failed.", RED))
            prompt_press_enter()
            return

        if item_id == "sync":
            self._action_sync(engine)
        elif item_id == "pull":
            self._action_pull(engine)
        elif item_id == "status":
            self._action_status(engine)
        elif item_id == "undo":
            self._action_undo(engine)
        elif item_id == "branch":
            self._action_branch(engine)
        elif item_id == "stash":
            self._action_stash(engine)
        elif item_id == "history":
            self._action_history(engine)
        elif item_id == "diff":
            self._action_diff(engine)
        elif item_id == "clean":
            self._action_clean(engine)
        elif item_id == "tag":
            self._action_tag(engine)
        elif item_id == "remote":
            self._action_remote(engine)
        elif item_id == "multi_sync":
            self._action_multi_sync()
        else:
            print(c(f"Feature [{item_id}] not found.", RED))
            prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 核心动作实现 (本地化)
    # ─────────────────────────────────────────────────────────

    def _action_sync(self, engine: GitEngine):
        """一键保存并同步"""
        print(c("══════════════════════════════════════════", CYAN))
        print(c(f"  {t('sync_banner')}", BOLD + GREEN))
        print(c("══════════════════════════════════════════", CYAN))
        print(t("sync_tip"))

        custom_msg = input(f"{BOLD}{t('commit_prompt')}{RESET}").strip()

        print(f"\n{t('syncing')}")
        success, logs = engine.one_click_sync(custom_msg if custom_msg else None)

        print()
        for log in logs:
            if log.startswith("❌"):
                print(c(log, RED))
            elif log.startswith("⚠️"):
                print(c(log, YELLOW))
            elif log.startswith("✅") or log.startswith("🎉") or log.startswith("✨"):
                print(c(log, GREEN))
            else:
                print(c(log, CYAN))

        prompt_press_enter()

    def _action_pull(self, engine: GitEngine):
        """一键拉取最新代码"""
        print(c(t("pulling"), BOLD + CYAN))
        ok, msg = engine.safe_pull()
        print()
        if ok:
            print(c(msg, GREEN))
        else:
            print(c(msg, RED if "❌" in msg else YELLOW))
        prompt_press_enter()

    def _action_status(self, engine: GitEngine):
        """查看改动详情"""
        info = engine.get_info()
        print(c(t("status_title"), BOLD + CYAN))
        print(t("work_dir", path=c(info['path'], DIM)))
        print()

        if info["is_clean"]:
            print(c(t("clean_workspace"), GREEN))
        else:
            if info["staged"]:
                print(c(t("staged_files"), GREEN))
                for f in info["staged"]:
                    print(f"  {c('+', GREEN)} {f}")
            if info["modified"]:
                print(c(t("modified_files"), YELLOW))
                for f in info["modified"]:
                    print(f"  {c('M', YELLOW)} {f}")
            if info["untracked"]:
                print(c(t("untracked_files"), CYAN))
                for f in info["untracked"]:
                    print(f"  {c('?', CYAN)} {f}")

        stat = engine.get_diff_stat()
        if stat:
            print(f"\n{c(t('diff_stat_title'), BOLD)}")
            print(stat)

        prompt_press_enter()

    def _action_undo(self, engine: GitEngine):
        """后悔药子菜单"""
        print(c(t("undo_title"), BOLD + MAGENTA))
        print(t("undo_opt_all"))
        print(t("undo_opt_commit"))
        print(t("undo_opt_file"))
        print(f" {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('undo_prompt')}{RESET}").strip()
        if sub == "1":
            confirm = input(c(t("discard_all_confirm"), RED)).strip().lower()
            if confirm == "y":
                ok, msg = engine.undo_action("discard_all")
                print(c(msg, GREEN if ok else RED))
            else:
                print(c(t("cancelled"), YELLOW))
        elif sub == "2":
            ok, msg = engine.undo_action("uncommit")
            print(c(msg, GREEN if ok else RED))
        elif sub == "3":
            fname = input(t("target_file_prompt")).strip()
            if fname:
                ok, msg = engine.undo_action("discard_file", target=fname)
                print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_branch(self, engine: GitEngine):
        """分支管理子菜单"""
        branches = engine.list_branches()
        print(c(t("branch_title"), BOLD + CYAN))
        print(t("local_branches"))
        for idx, b in enumerate(branches, start=1):
            curr_mark = c(f" {t('current_branch_mark')}", GREEN) if b["is_current"] else ""
            print(f"  [{idx}] {b['name']}{curr_mark}")

        print("\n" + t("branch_opt_switch"))
        print(t("branch_opt_new"))
        print(f"  {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('branch_prompt')}{RESET}").strip()
        if sub.lower() == "b":
            return
        if sub.lower() == "n":
            new_b = input(t("new_branch_prompt")).strip()
            if new_b:
                ok, msg = engine.create_and_switch_branch(new_b)
                print(c(msg, GREEN if ok else RED))
        elif sub.isdigit():
            idx = int(sub)
            if 1 <= idx <= len(branches):
                target_b = branches[idx - 1]["name"]
                ok, msg = engine.switch_branch(target_b)
                print(c(msg, GREEN if ok else RED))
            else:
                print(c(t("out_of_range", choice=sub), RED))
        prompt_press_enter()

    def _action_stash(self, engine: GitEngine):
        """暂存管理子菜单"""
        print(c(t("stash_title"), BOLD + CYAN))
        print(t("stash_opt_save"))
        print(t("stash_opt_pop"))
        print(f" {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('stash_prompt')}{RESET}").strip()
        if sub == "1":
            note = input(t("stash_note_prompt")).strip()
            ok, msg = engine.stash_save(note)
            print(c(msg, GREEN if ok else RED))
        elif sub == "2":
            ok, msg = engine.stash_pop()
            print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_history(self, engine: GitEngine):
        """提交历史"""
        hist = engine.get_recent_history(10)
        print(c(t("history_title"), BOLD + CYAN))
        if not hist:
            print(t("no_history"))
        else:
            for item in hist:
                parts = item.split("|")
                if len(parts) >= 4:
                    h, author, when, msg = parts[0], parts[1], parts[2], parts[3]
                    print(f" {c(h, YELLOW)} {BOLD}{msg}{RESET} {c('(' + when + ' by ' + author + ')', DIM)}")
                else:
                    print(f" {item}")
        prompt_press_enter()

    def _action_diff(self, engine: GitEngine):
        """代码差异"""
        print(c(t("diff_title"), BOLD + CYAN))
        res = run_git(["diff", "--color=always"], cwd=engine.repo_path)
        if res.stdout:
            print(res.stdout)
        else:
            print(c(t("no_diff"), GREEN))
        prompt_press_enter()

    def _action_clean(self, engine: GitEngine):
        """清理未跟踪文件"""
        confirm = input(c(t("clean_confirm"), RED)).strip().lower()
        if confirm == "y":
            res = run_git(["clean", "-fd"], cwd=engine.repo_path)
            if res.success:
                print(c("✅ Cleaned untracked files successfully!", GREEN))
            else:
                print(c(f"❌ Clean failed: {res.stderr}", RED))
        prompt_press_enter()

    def _action_tag(self, engine: GitEngine):
        """打标签"""
        tag_name = input(t("tag_name_prompt")).strip()
        if not tag_name:
            return
        tag_msg = input(t("tag_msg_prompt")).strip() or tag_name
        res = run_git(["tag", "-a", tag_name, "-m", tag_msg], cwd=engine.repo_path)
        if res.success:
            print(c(f"✅ Created local tag [{tag_name}]!", GREEN))
            push_yn = input(t("tag_push_prompt")).strip().lower()
            if push_yn != "n":
                pres = run_git(["push", "origin", tag_name], cwd=engine.repo_path)
                if pres.success:
                    print(c(f"🎉 Tag [{tag_name}] pushed to remote successfully!", GREEN))
                else:
                    print(c(f"⚠️ Tag created locally, but failed to push: {pres.stderr}", YELLOW))
        else:
            print(c(f"❌ Failed to create tag: {res.stderr}", RED))
        prompt_press_enter()

    def _action_remote(self, engine: GitEngine):
        """查看远程仓库"""
        res = run_git(["remote", "-v"], cwd=engine.repo_path)
        print(c("🌐 Remote Repositories:", BOLD + CYAN))
        if res.stdout:
            print(res.stdout)
        else:
            print(c("No remote repository configured.", YELLOW))
        prompt_press_enter()

    def _action_multi_sync(self):
        """多仓库巡检与同步"""
        self._handle_multi_repo_view()

    # ─────────────────────────────────────────────────────────
    # 功能库管理与个性化设置菜单
    # ─────────────────────────────────────────────────────────

    def _menu_manage_features(self):
        """设置与个性化主菜单"""
        while True:
            print()
            print(c("══════════════════════════════════════════", YELLOW))
            print(c(f"  {t('settings_title')}", BOLD + YELLOW))
            print(c("══════════════════════════════════════════", YELLOW))
            print(f" {t('settings_opt_presets')}")
            print(f" {t('settings_opt_add_custom')}")
            print(f" {t('settings_opt_remove_custom')}")
            curr_lang_name = "English" if get_language() == "en" else "简体中文"
            print(f" [4] 🌐 Switch Language / 切换语言 (Current: {c(curr_lang_name, GREEN)})")
            print(f" {t('settings_opt_reset')}")
            print(f" {t('back_to_main')}")
            print()

            sub = input(f"{BOLD}{t('select_setting')}{RESET}").strip()
            if sub.lower() in ["b", ""]:
                break
            elif sub == "1":
                self._menu_toggle_presets()
            elif sub == "2":
                self._menu_add_custom_cmd()
            elif sub == "3":
                self._menu_remove_custom_cmd()
            elif sub == "4":
                self._menu_switch_language()
            elif sub == "5":
                conf = input(c(t("reset_confirm"), RED)).strip().lower()
                if conf == "y":
                    self.config_mgr.reset_to_defaults()
                    print(c(t("reset_done"), GREEN))
                    prompt_press_enter()

    def _menu_switch_language(self):
        """语言切换菜单"""
        print()
        print(c(t("lang_switch_title"), BOLD + CYAN))
        print(f"  {t('lang_opt_en')}")
        print(f"  {t('lang_opt_zh')}")
        print(f"  {t('back_to_main')}")
        print()

        choice = input(f"{BOLD}Choose language [1/2, b to cancel]: {RESET}").strip()
        if choice == "1":
            self.config_mgr.set_language("en")
            print(c(t("lang_changed", lang="English"), GREEN))
        elif choice == "2":
            self.config_mgr.set_language("zh")
            print(c(t("lang_changed", lang="简体中文"), GREEN))
        prompt_press_enter()

    def _menu_toggle_presets(self):
        """开启或关闭官方备选功能"""
        while True:
            active_ids = self.config_mgr.get_active_preset_ids()

            print()
            print(c(t("feature_store_title"), BOLD + CYAN))
            for idx, pid in enumerate(ALL_PRESET_IDS, start=1):
                meta = get_preset_info(pid)
                is_on = pid in active_ids
                status_badge = c(t("feature_enabled"), GREEN) if is_on else c(t("feature_disabled"), GRAY)
                print(f"  [{idx}] {status_badge} {BOLD}{meta['name']}{RESET} ── {c(meta['short_desc'], DIM)}")

            print(f"\n{c(t('feature_toggle_hint'), DIM)}")
            choice = input(f"{BOLD}{t('feature_toggle_prompt')}{RESET}").strip()

            if choice.lower() in ["b", ""]:
                break

            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(ALL_PRESET_IDS):
                    target_id = ALL_PRESET_IDS[num - 1]
                    meta = get_preset_info(target_id)
                    if target_id in active_ids:
                        self.config_mgr.disable_preset(target_id)
                        print(c(t("feature_turned_off", name=meta['name']), YELLOW))
                    else:
                        self.config_mgr.enable_preset(target_id)
                        print(c(t("feature_turned_on", name=meta['name']), GREEN))
                else:
                    print(c(t("out_of_range", choice=choice), RED))

    def _menu_add_custom_cmd(self):
        """添加自定义命令"""
        print()
        print(c(t("add_custom_title"), BOLD + GREEN))
        name = input(t("custom_name_prompt")).strip()
        if not name:
            prompt_press_enter()
            return
        cmd = input(t("custom_cmd_prompt")).strip()
        if not cmd:
            prompt_press_enter()
            return
        desc = input(t("custom_desc_prompt")).strip()

        self.config_mgr.add_custom_command(name, cmd, desc)
        print(c(t("custom_added", name=name), GREEN))
        prompt_press_enter()

    def _menu_remove_custom_cmd(self):
        """删除自定义命令"""
        cmds = self.config_mgr.get_custom_commands()
        if not cmds:
            print(c(t("remove_custom_empty"), YELLOW))
            prompt_press_enter()
            return
        print()
        print(c(t("remove_custom_title"), BOLD + RED))
        for idx, item in enumerate(cmds, start=1):
            print(f"  [{idx}] {item['name']} ({item['cmd']})")
        choice = input(f"{BOLD}Select number [b to return]: {RESET}").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(cmds):
                item = cmds[idx - 1]
                self.config_mgr.remove_custom_command(item["id"])
                print(c(t("custom_removed", name=item['name']), GREEN))
            else:
                print(c(t("out_of_range", choice=choice), RED))
        prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 多仓库巡检与非 Git 目录引导 (继承 gsyn)
    # ─────────────────────────────────────────────────────────

    def _handle_non_git_dir(self):
        """非 Git 目录下的智能响应"""
        repos = scan_multi_repos(self.target_dir)
        if repos:
            print(c(t("non_git_sub_found", count=len(repos)), CYAN))
            self._handle_multi_repo_view(repos)
        else:
            print(c("┏" + "━" * 58 + "┓", YELLOW))
            print(c("┃", YELLOW) + f"  {BOLD}{t('non_git_title')}{RESET}".ljust(66) + c("┃", YELLOW))
            print(c("┗" + "━" * 58 + "┛", YELLOW))
            print()
            print(t("init_repo_opt"))
            print(t("clone_repo_opt"))
            print(f" [q] {t('goodbye')}")
            print()
            c_input = input(f"{BOLD}Select [1/2, q]: {RESET}").strip()
            if c_input == "1":
                res = run_git(["init"], cwd=self.target_dir)
                if res.success:
                    print(c("🎉 Git repository initialized successfully!", GREEN))
                    prompt_press_enter()
                    self._run_single_repo_menu()
                else:
                    print(c(f"Init failed: {res.stderr}", RED))
            elif c_input == "2":
                url = input(t("clone_url_prompt")).strip()
                if url:
                    print(f"Cloning {url} ...")
                    cres = run_git(["clone", url], cwd=self.target_dir)
                    if cres.success:
                        print(c("🎉 Cloned successfully!", GREEN))
                    else:
                        print(c(f"❌ Clone failed: {cres.stderr}", RED))
                prompt_press_enter()

    def _handle_multi_repo_view(self, repos: Optional[List[Dict[str, Any]]] = None):
        """多仓库巡检与批量同步界面"""
        if repos is None:
            repos = scan_multi_repos(self.target_dir)

        if not repos:
            print(c("No Git repositories found.", YELLOW))
            prompt_press_enter()
            return

        print()
        print(c(t("multi_repo_title", count=len(repos)), BOLD + CYAN))
        for idx, r in enumerate(repos, start=1):
            st_text = c(t("sync_up_to_date"), GREEN) if r["is_clean"] and r["ahead"] == 0 else c(t("dirty_status", count=r["total_changes"]), YELLOW)
            ahead_str = f" ↑{r['ahead']}" if r["ahead"] > 0 else ""
            behind_str = f" ↓{r['behind']}" if r["behind"] > 0 else ""
            print(f" [{idx}] {BOLD}{r['name']:<20}{RESET} {c(r['branch'], CYAN):<12} {st_text}{ahead_str}{behind_str}")

        print("\n" + t("multi_opt_enter"))
        print(t("multi_opt_all"))
        print(f"  {t('back_to_main')}")
        print()

        choice = input(f"{BOLD}Select option: {RESET}").strip()
        if choice.lower() == "a":
            print(c(f"\n🚀 Syncing {len(repos)} repositories in batch...", BOLD + CYAN))
            succ, fail = 0, 0
            for r in repos:
                print(f"\n▸ Syncing repo: {BOLD}{r['name']}{RESET} ({r['path']})")
                eng = GitEngine(r["path"])
                ok, logs = eng.one_click_sync()
                for l in logs:
                    print(f"  {l}")
                if ok:
                    succ += 1
                else:
                    fail += 1
            print(c(f"\nBatch sync completed: {succ} succeeded, {fail} failed.", GREEN if fail == 0 else YELLOW))
            prompt_press_enter()
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(repos):
                sub_cli = FoolGitCLI(target_dir=repos[idx - 1]["path"])
                sub_cli._run_single_repo_menu()
            else:
                print(c(t("out_of_range", choice=sub), RED))
                prompt_press_enter()
