"""
FoolGit 终端交互 UI (CLI)
纯净多语言支持：英文模式 100% 英文，中文模式 100% 中文，杜绝中英文混杂。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from .core import GitEngine, is_git_repo, scan_multi_repos, run_git
from .config import ConfigManager
from .presets import get_preset_info, ALL_PRESET_IDS
from .i18n import t, get_language

# 终端 ANSI 颜色常量
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
    # 单仓库主界面
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
        engine = GitEngine(self.target_dir)
        while True:
            info = engine.get_info()

            self._render_header(info)

            active_ids = self.config_mgr.get_active_preset_ids()
            custom_cmds = self.config_mgr.get_custom_commands()

            menu_items = []
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

            for c_cmd in custom_cmds:
                menu_items.append({
                    "type": "custom",
                    "id": c_cmd["id"],
                    "name": c_cmd["name"],
                    "tag": t("custom_tag"),
                    "desc": c_cmd["desc"],
                    "raw_cmd": c_cmd["cmd"],
                })

            for idx, item in enumerate(menu_items, start=1):
                tag_str = f" {c('[' + item['tag'] + ']', MAGENTA)}" if item.get("tag") else ""
                highlight = c(f"[{idx}]", BOLD + GREEN if idx == 1 else BOLD + CYAN)
                print(f" {highlight} {BOLD}{item['name']}{RESET}{tag_str}")
                print(f"     {c(item['desc'], GRAY)}")

            print(f"\n {c('----------------------------------------------------', GRAY)}")
            print(f" {c('[+]', BOLD + YELLOW)} {BOLD}{t('settings_title')}{RESET}")
            print(f" {c('[q]', BOLD + RED)} {BOLD}{t('menu_quit')}{RESET}")
            print()

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
            print(c(f"🚀 Running: {raw_cmd}", BOLD + CYAN))
            res = run_git(raw_cmd.replace("git ", "").split(), cwd=engine.repo_path)
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(c(res.stderr, YELLOW if res.success else RED))
            if res.success:
                print(c("✅ OK", GREEN))
            else:
                print(c("❌ Failed", RED))
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
        elif item_id == "gitignore":
            self._action_gitignore(engine)
        else:
            print(c(f"Feature [{item_id}] not found.", RED))
            prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 核心动作
    # ─────────────────────────────────────────────────────────

    def _action_sync(self, engine: GitEngine):
        """一键保存并同步"""
        print(c("══════════════════════════════════════════", CYAN))
        print(c(f"  🚀 {t('sync_banner')}", BOLD + GREEN))
        print(c("══════════════════════════════════════════", CYAN))
        print(f"💡 {t('sync_tip')}")

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
        """拉取最新代码"""
        print(c(f"⬇️  {t('pulling')}", BOLD + CYAN))
        ok, msg = engine.safe_pull()
        print()
        if ok:
            print(c(msg, GREEN))
        else:
            print(c(msg, RED if "❌" in msg else YELLOW))
            conflicts = engine.get_conflict_files()
            if conflicts:
                print()
                print(c(f"🚑 {t('conflict_title')}", BOLD + RED))
                print(t("conflict_files_label"))
                for cf in conflicts:
                    print(f"  {c('!', RED)} {cf}")
                print()
                print(f" {t('conflict_opt_abort')}")
                print(f" {t('conflict_opt_back')}")
                ans = input(f"{BOLD}{t('conflict_prompt')}{RESET}").strip().lower()
                if ans == "a":
                    ab_ok, ab_msg = engine.abort_merge()
                    print(c(ab_msg, GREEN if ab_ok else RED))
        prompt_press_enter()

    def _action_status(self, engine: GitEngine):
        """查看改动详情"""
        info = engine.get_info()
        print(c(f"🔍 {t('status_title')}", BOLD + CYAN))
        print(t("work_dir", path=c(info['path'], DIM)))
        print()

        if info["is_clean"]:
            print(c(f"✨ {t('clean_workspace')}", GREEN))
        else:
            if info["staged"]:
                print(c(f"● {t('staged_files')}", GREEN))
                for f in info["staged"]:
                    print(f"  {c('+', GREEN)} {f}")
            if info["modified"]:
                print(c(f"● {t('modified_files')}", YELLOW))
                for f in info["modified"]:
                    print(f"  {c('M', YELLOW)} {f}")
            if info["untracked"]:
                print(c(f"● {t('untracked_files')}", CYAN))
                for f in info["untracked"]:
                    print(f"  {c('?', CYAN)} {f}")

        stat = engine.get_diff_stat()
        if stat:
            print(f"\n{c('● ' + t('diff_stat_title'), BOLD)}")
            print(stat)

        prompt_press_enter()

    def _action_undo(self, engine: GitEngine):
        """后悔药子菜单"""
        print(c(f"💊 {t('undo_title')}", BOLD + MAGENTA))
        print(f" [1] {t('undo_opt_all')}")
        print(f" [2] {t('undo_opt_commit')}")
        print(f" [3] {t('undo_opt_file')}")
        print(f" [4] {t('undo_opt_amend')}")
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
            discardable = engine.get_discardable_files()
            if not discardable:
                print(c(t("discard_file_no_changes"), YELLOW))
            else:
                print(f"\n{c('● ' + t('undo_opt_file'), BOLD)}")
                for idx, f in enumerate(discardable, start=1):
                    color = YELLOW if f["status"] == "M" else (GREEN if f["status"] == "A" else CYAN)
                    print(f"  [{idx}] {c('[' + f['status'] + ']', color)} {f['path']}")
                sel = input(f"\n{BOLD}{t('discard_file_select_prompt')}{RESET}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(discardable):
                    target_f = discardable[int(sel) - 1]["path"]
                    confirm = input(c(t("discard_file_confirm", target=target_f), RED)).strip().lower()
                    if confirm == "y":
                        ok, msg = engine.undo_action("discard_file", target=target_f)
                        print(c(msg, GREEN if ok else RED))
                    else:
                        print(c(t("cancelled"), YELLOW))
        elif sub == "4":
            print(c(f"✏️  {t('amend_title')}", BOLD + CYAN))
            new_msg = input(t("amend_prompt")).strip()
            if new_msg:
                ok, msg = engine.amend_commit_message(new_msg)
                print(c(msg, GREEN if ok else RED))
            else:
                print(c(t("cancelled"), YELLOW))
        prompt_press_enter()

    def _action_branch(self, engine: GitEngine):
        """分支管理"""
        branches = engine.list_branches()
        print(c(f"🌿 {t('branch_title')}", BOLD + CYAN))
        print(t("local_branches"))
        for idx, b in enumerate(branches, start=1):
            curr_mark = c(f" {t('current_branch_mark')}", GREEN) if b["is_current"] else ""
            print(f"  [{idx}] {b['name']}{curr_mark}")

        print("\n" + t("branch_opt_switch"))
        print(t("branch_opt_new"))
        print(t("branch_opt_delete"))
        print(f"  {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('branch_prompt')}{RESET}").strip()
        if sub.lower() in ["b", ""]:
            return
        if sub.lower() == "n":
            new_b = input(t("new_branch_prompt")).strip()
            if new_b:
                ok, msg = engine.create_and_switch_branch(new_b)
                print(c(msg, GREEN if ok else RED))
        elif sub.lower() == "d":
            del_b = input(t("branch_delete_prompt")).strip()
            if del_b:
                force_yn = input(t("branch_delete_confirm", branch=del_b)).strip().lower()
                ok, msg = engine.delete_branch(del_b, force=(force_yn == "y"))
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
        """暂存管理"""
        while True:
            print(c(f"📦 {t('stash_title')}", BOLD + CYAN))
            print(f" [1] {t('stash_opt_save')}")
            print(f" [2] {t('stash_opt_pop')}")
            print(f" [3] {t('stash_opt_list')}")
            print(f" {t('back_to_main')}")
            print()

            sub = input(f"{BOLD}{t('stash_prompt')}{RESET}").strip()
            if sub.lower() in ["b", ""]:
                break
            elif sub == "1":
                note = input(t("stash_note_prompt")).strip()
                ok, msg = engine.stash_save(note)
                print(c(msg, GREEN if ok else RED))
                prompt_press_enter()
            elif sub == "2":
                ok, msg = engine.stash_pop()
                print(c(msg, GREEN if ok else RED))
                prompt_press_enter()
            elif sub == "3":
                self._action_stash_list(engine)
            else:
                print(c(t("invalid_choice"), RED))

    def _action_stash_list(self, engine: GitEngine):
        """查看 stash 列表并可应用/删除"""
        while True:
            stashes = engine.list_stashes()
            print()
            print(c(f"📋 {t('stash_list_title')}", BOLD + CYAN))
            if not stashes:
                print(c(t("stash_list_empty"), YELLOW))
                prompt_press_enter()
                return
            for idx, s in enumerate(stashes, start=1):
                print(f"  [{idx}] {c(s['ref'], YELLOW)} {s['desc']}")
            print()
            sel = input(f"{BOLD}{t('stash_list_prompt')}{RESET}").strip()
            if sel.lower() in ["b", ""]:
                break
            if sel.isdigit() and 1 <= int(sel) <= len(stashes):
                chosen_idx = int(sel) - 1
                chosen = stashes[chosen_idx]
                print(f"\n  {c(chosen['ref'], YELLOW)}: {chosen['desc']}")
                print(f"  {t('stash_entry_opt_apply')}")
                print(f"  {t('stash_entry_opt_drop')}")
                print(f"  {t('stash_entry_opt_back')}")
                action = input(f"{BOLD}{t('stash_entry_prompt')}{RESET}").strip().lower()
                if action == "a":
                    ok, msg = engine.stash_apply(chosen_idx)
                    print(c(msg, GREEN if ok else RED))
                    prompt_press_enter()
                elif action == "d":
                    ok, msg = engine.stash_drop(chosen_idx)
                    print(c(msg, GREEN if ok else RED))
                    prompt_press_enter()
            else:
                print(c(t("invalid_choice"), RED))

    def _action_history(self, engine: GitEngine):
        """提交历史及详情查看"""
        hist = engine.get_recent_history(10)
        print(c(f"📜 {t('history_menu_title')}", BOLD + CYAN))
        if not hist:
            print(t("no_history"))
            prompt_press_enter()
            return

        commit_hashes = []
        for idx, item in enumerate(hist, start=1):
            parts = item.split("|")
            if len(parts) >= 4:
                h, author, when, msg = parts[0], parts[1], parts[2], parts[3]
                commit_hashes.append(h)
                print(f"  [{idx}] {c(h, YELLOW)} {BOLD}{msg}{RESET} {c('(' + when + ' by ' + author + ')', DIM)}")
            else:
                commit_hashes.append(item.split()[0] if item.split() else "")
                print(f"  [{idx}] {item}")

        print()
        inspect_choice = input(t("history_prompt_inspect", count=len(commit_hashes))).strip()
        if inspect_choice.isdigit() and 1 <= int(inspect_choice) <= len(commit_hashes):
            target_hash = commit_hashes[int(inspect_choice) - 1]
            print()
            print(c(f"─── {t('history_commit_detail_title', commit=target_hash)} ───", BOLD + CYAN))
            detail = engine.get_commit_detail(target_hash)
            print(detail)

        prompt_press_enter()

    def _action_diff(self, engine: GitEngine):
        """代码差异查看子菜单"""
        print(c(f"🔍 {t('diff_menu_title')}", BOLD + CYAN))
        print(f" {t('diff_opt_unstaged')}")
        print(f" {t('diff_opt_staged')}")
        print(f" {t('diff_opt_file')}")
        print(f" {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('diff_prompt')}{RESET}").strip()
        if sub == "1":
            diff = engine.get_diff(staged=False, color=True)
            if diff:
                print(diff)
            else:
                print(c(t("no_diff"), GREEN))
        elif sub == "2":
            diff = engine.get_diff(staged=True, color=True)
            if diff:
                print(diff)
            else:
                print(c(t("no_diff"), GREEN))
        elif sub == "3":
            info = engine.get_info()
            mod_files = list(dict.fromkeys(info["modified"] + info["staged"]))
            if not mod_files:
                print(c(t("diff_no_modified_files"), GREEN))
            else:
                for idx, f in enumerate(mod_files, start=1):
                    print(f"  [{idx}] {f}")
                f_sel = input(f"\n{BOLD}{t('diff_file_prompt')}{RESET}").strip()
                if f_sel.isdigit() and 1 <= int(f_sel) <= len(mod_files):
                    target_f = mod_files[int(f_sel) - 1]
                    diff = engine.get_diff(file_path=target_f, color=True)
                    if diff:
                        print(diff)
                    else:
                        print(c(t("no_diff"), GREEN))
        prompt_press_enter()

    def _action_clean(self, engine: GitEngine):
        """清理未跟踪文件"""
        print(c(f"🧹 {t('clean_title')}", BOLD + CYAN))
        preview = engine.clean_preview()
        if not preview:
            print(c(f"✨ {t('clean_nothing')}", GREEN))
            prompt_press_enter()
            return

        print(c(t("clean_preview_title"), YELLOW))
        for p in preview:
            print(f"  🗑️  {p}")
        print()
        confirm = input(c(t("clean_confirm"), RED)).strip().lower()
        if confirm == "y":
            ok, msg = engine.clean_execute()
            print(c(msg, GREEN if ok else RED))
        else:
            print(c(t("cancelled"), YELLOW))
        prompt_press_enter()

    def _action_tag(self, engine: GitEngine):
        """版本标签管理子菜单"""
        print(c(f"🏷️  {t('tag_title')}", BOLD + CYAN))
        print(f" {t('tag_opt_list')}")
        print(f" {t('tag_opt_create')}")
        print(f" {t('tag_opt_delete')}")
        print(f" {t('tag_opt_push_all')}")
        print(f" {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('tag_prompt')}{RESET}").strip()
        if sub == "1":
            tags = engine.list_tags()
            if not tags:
                print(c(t("tag_none_found"), YELLOW))
            else:
                for t_name in tags:
                    print(f"  🏷️  {c(t_name, GREEN)}")
        elif sub == "2":
            tag_name = input(t("tag_name_prompt")).strip()
            if tag_name:
                tag_msg = input(t("tag_msg_prompt")).strip() or tag_name
                push_yn = input(t("tag_push_prompt")).strip().lower()
                ok, msg = engine.create_tag(tag_name, tag_msg, push=(push_yn != "n"))
                print(c(msg, GREEN if ok else RED))
        elif sub == "3":
            tags = engine.list_tags()
            if not tags:
                print(c(t("tag_none_found"), YELLOW))
            else:
                for idx, t_name in enumerate(tags, start=1):
                    print(f"  [{idx}] {t_name}")
                t_sel = input(f"\n{BOLD}{t('tag_delete_prompt')}{RESET}").strip()
                target_tag = ""
                if t_sel.isdigit() and 1 <= int(t_sel) <= len(tags):
                    target_tag = tags[int(t_sel) - 1]
                elif t_sel in tags:
                    target_tag = t_sel
                if target_tag:
                    rem_yn = input(t("tag_delete_remote_confirm")).strip().lower()
                    ok, msg = engine.delete_tag(target_tag, remote=(rem_yn == "y"))
                    print(c(msg, GREEN if ok else RED))
        elif sub == "4":
            ok, msg = engine.push_all_tags()
            print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_remote(self, engine: GitEngine):
        """远程仓库设置子菜单"""
        current_url = engine.get_remote_url()
        print(c(f"🌐 {t('remote_title')}", BOLD + CYAN))
        if current_url:
            print(f"  {t('remote_origin_label', url=c(current_url, GREEN))}\n")
        else:
            print(f"  {c(t('remote_none'), YELLOW)}\n")

        print(f" {t('remote_opt_view')}")
        print(f" {t('remote_opt_set')}")
        print(f" {t('remote_opt_test')}")
        print(f" {t('back_to_main')}")
        print()

        sub = input(f"{BOLD}{t('remote_prompt')}{RESET}").strip()
        if sub == "1":
            remotes = engine.list_remotes()
            if remotes:
                for r in remotes:
                    print(f"  {BOLD}{r['name']}{RESET} \t{r['url']} ({r['type']})")
            else:
                print(c(t("remote_none"), YELLOW))
        elif sub == "2":
            new_url = input(t("remote_set_prompt")).strip()
            if new_url:
                ok, msg = engine.set_remote_origin(new_url)
                print(c(msg, GREEN if ok else RED))
        elif sub == "3":
            print(t("remote_testing"))
            ok, msg = engine.test_remote_connection()
            print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_multi_sync(self):
        """多仓库巡检与同步"""
        self._handle_multi_repo_view()

    def _action_gitignore(self, engine: GitEngine):
        """.gitignore 快速编辑器"""
        while True:
            print(c(f"🚫 {t('gitignore_title')}", BOLD + CYAN))
            content = engine.get_gitignore_content()
            if content:
                print(c(t("gitignore_current_label"), BOLD))
                for line in content.splitlines()[:30]:
                    print(f"  {c(line, DIM)}")
                if len(content.splitlines()) > 30:
                    print(c(f"  ... ({len(content.splitlines())} lines total)", DIM))
            else:
                print(c(t("gitignore_empty_file"), YELLOW))
            print()
            pattern = input(f"{BOLD}{t('gitignore_add_prompt')}{RESET}").strip()
            if not pattern or pattern.lower() == "b":
                break
            ok, msg = engine.append_to_gitignore(pattern)
            print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 设置菜单
    # ─────────────────────────────────────────────────────────

    def _menu_manage_features(self):
        """设置主菜单"""
        while True:
            print()
            print(c("══════════════════════════════════════════", YELLOW))
            print(c(f"  🛠️  {t('settings_title')}", BOLD + YELLOW))
            print(c("══════════════════════════════════════════", YELLOW))
            print(f" {t('settings_opt_presets')}")
            print(f" {t('settings_opt_add_custom')}")
            print(f" {t('settings_opt_remove_custom')}")
            print(f" {t('settings_opt_lang')}")
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
        """语言切换"""
        print()
        print(c(t("lang_switch_title"), BOLD + CYAN))
        print(f"  {t('lang_opt_en')}")
        print(f"  {t('lang_opt_zh')}")
        print(f"  {t('back_to_main')}")
        print()

        prompt_str = "Choose language [1/2, b to cancel]: " if get_language() == "en" else "请选择语言 [1/2, b 返回]: "
        choice = input(f"{BOLD}{prompt_str}{RESET}").strip()
        if choice == "1":
            self.config_mgr.set_language("en")
            print(c(t("lang_changed"), GREEN))
        elif choice == "2":
            self.config_mgr.set_language("zh")
            print(c(t("lang_changed"), GREEN))
        prompt_press_enter()

    def _menu_toggle_presets(self):
        """开关备选功能"""
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
        choice = input(f"{BOLD}Number [b to return]: {RESET}").strip()
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
    # 多仓库支持
    # ─────────────────────────────────────────────────────────

    def _handle_non_git_dir(self):
        repos = scan_multi_repos(self.target_dir)
        if repos:
            print(c(t("non_git_sub_found", count=len(repos)), CYAN))
            self._handle_multi_repo_view(repos)
        else:
            print(c("┏" + "━" * 58 + "┓", YELLOW))
            print(c("┃", YELLOW) + f"  {BOLD}{t('non_git_title')}{RESET}".ljust(66) + c("┃", YELLOW))
            print(c("┗" + "━" * 58 + "┛", YELLOW))
            print()
            print(f" {t('init_repo_opt')}")
            print(f" {t('clone_repo_opt')}")
            print(f" [q] {t('menu_quit')}")
            print()
            c_input = input(f"{BOLD}Select [1/2, q]: {RESET}").strip()
            if c_input == "1":
                res = run_git(["init"], cwd=self.target_dir)
                if res.success:
                    print(c("🎉 Init OK!", GREEN))
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
        if repos is None:
            repos = scan_multi_repos(self.target_dir)

        if not repos:
            print(c("No Git repositories found.", YELLOW))
            prompt_press_enter()
            return

        print()
        print(c(f"════════ {t('multi_repo_title', count=len(repos))} ════════", BOLD + CYAN))
        for idx, r in enumerate(repos, start=1):
            st_text = c(t("sync_up_to_date"), GREEN) if r["is_clean"] and r["ahead"] == 0 else c(t("dirty_status", count=r["total_changes"]), YELLOW)
            ahead_str = f" ↑{r['ahead']}" if r["ahead"] > 0 else ""
            behind_str = f" ↓{r['behind']}" if r["behind"] > 0 else ""
            print(f" [{idx}] {BOLD}{r['name']:<20}{RESET} {c(r['branch'], CYAN):<12} {st_text}{ahead_str}{behind_str}")

        print("\n" + t("multi_opt_enter"))
        print(t("multi_opt_all"))
        print(t("multi_opt_comma"))
        print(f"  {t('back_to_main')}")
        print()

        choice = input(f"{BOLD}Select option: {RESET}").strip()
        if choice.lower() in ["b", ""]:
            return
        elif choice.lower() == "a":
            print(c(f"\n🚀 {t('multi_syncing', count=len(repos))}", BOLD + CYAN))
            succ, fail = 0, 0
            for r in repos:
                print(f"\n▸ Repo: {BOLD}{r['name']}{RESET}")
                eng = GitEngine(r["path"])
                ok, logs = eng.one_click_sync()
                for l in logs:
                    print(f"  {l}")
                if ok:
                    succ += 1
                else:
                    fail += 1
            print(c(f"\n{t('multi_sync_summary', succ=succ, fail=fail)}", GREEN if fail == 0 else YELLOW))
            prompt_press_enter()
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(repos):
                sub_cli = FoolGitCLI(target_dir=repos[idx - 1]["path"])
                sub_cli._run_single_repo_menu()
            else:
                print(c(t("out_of_range", choice=choice), RED))
                prompt_press_enter()
        elif "," in choice:
            # Comma-separated selection: sync specific repos
            indices = []
            for part in choice.split(","):
                part = part.strip()
                if part.isdigit():
                    n = int(part)
                    if 1 <= n <= len(repos):
                        indices.append(n - 1)
            if not indices:
                print(c(t("invalid_choice"), RED))
                prompt_press_enter()
                return
            selected = [repos[i] for i in indices]
            print(c(f"\n🚀 {t('multi_syncing_selected', count=len(selected))}", BOLD + CYAN))
            succ, fail = 0, 0
            for r in selected:
                print(f"\n▸ Repo: {BOLD}{r['name']}{RESET}")
                eng = GitEngine(r["path"])
                ok, logs = eng.one_click_sync()
                for ln in logs:
                    print(f"  {ln}")
                if ok:
                    succ += 1
                else:
                    fail += 1
            print(c(f"\n{t('multi_sync_summary', succ=succ, fail=fail)}", GREEN if fail == 0 else YELLOW))
            prompt_press_enter()
