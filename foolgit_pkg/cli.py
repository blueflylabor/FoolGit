"""
FoolGit 终端交互 UI (CLI)
提供极简、直观、低心智负担的菜单选择体验。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from .core import GitEngine, is_git_repo, scan_multi_repos, run_git
from .config import ConfigManager
from .presets import PRESET_LIBRARY, DEFAULT_ACTIVE_IDS

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


def clear_screen():
    """轻量清屏或隔断"""
    # 保持终端历史，仅输出清爽分隔
    print("\n" + "─" * 60 + "\n")


def prompt_press_enter():
    """等待用户敲回车继续"""
    try:
        input(f"\n{c('按回车键返回主菜单...', DIM)}")
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
            print(f"\n{c('已安全退出 FoolGit。', YELLOW)}")
            sys.exit(0)

    # ─────────────────────────────────────────────────────────
    # 单仓库主界面与流程
    # ─────────────────────────────────────────────────────────

    def _render_header(self, info: Dict[str, Any]):
        """渲染顶部直观健康卡片"""
        repo_name = info["name"]
        branch = info["branch"]
        clean_status = c("✨ 干净无修改", GREEN) if info["is_clean"] else c(f"✎ {info['total_changes']} 个文件有改动", YELLOW)

        sync_status = ""
        if info["has_upstream"]:
            if info["ahead"] > 0 and info["behind"] > 0:
                sync_status = c(f" (↑超前{info['ahead']} / ↓落后{info['behind']})", MAGENTA)
            elif info["ahead"] > 0:
                sync_status = c(f" (↑待推送 {info['ahead']} 个提交)", CYAN)
            elif info["behind"] > 0:
                sync_status = c(f" (↓待拉取 {info['behind']} 个更新)", BLUE)
            else:
                sync_status = c(" (与远端同步 ✓)", GREEN)
        else:
            sync_status = c(" (未关联远端)", GRAY)

        print(c("┏" + "━" * 58 + "┓", CYAN))
        print(c("┃", CYAN) + f"  {BOLD}FoolGit v1.0.0{RESET} ── 傻瓜式 Git 助理" + " " * 23 + c("┃", CYAN))
        header_line = f"  📁 仓库: {c(repo_name, BOLD)}   🌿 分支: {c(branch, GREEN)}"
        print(c("┃", CYAN) + header_line.ljust(66) + c("┃", CYAN))
        status_line = f"  ⚡ 状态: {clean_status}{sync_status}"
        print(c("┃", CYAN) + status_line.ljust(72) + c("┃", CYAN))
        print(c("┗" + "━" * 58 + "┛", CYAN))
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
            # 1. 预设功能
            for pid in active_ids:
                if pid in PRESET_LIBRARY:
                    meta = PRESET_LIBRARY[pid]
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
                    "tag": "自定",
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
            print(f" {c('[+]', BOLD + YELLOW)} {BOLD}🛠️  功能库与个性化设置{RESET} {c('(自选添加功能/命令)', GRAY)}")
            print(f" {c('[q]', BOLD + RED)} {BOLD}退出{RESET}")
            print()

            # 用户输入
            choice = input(f"{BOLD}👉 请选择操作编号{RESET} {c('[直接回车默认: 1, q: 退出]: ', DIM)}").strip()

            if choice.lower() in ["q", "quit", "exit"]:
                print(c("👋 再见！", GREEN))
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
                    print(c(f"⚠️ 编号 [{choice}] 不在菜单范围内，请重新选择。", RED))
                    prompt_press_enter()
            else:
                print(c("⚠️ 输入无效，请输入数字序号、+ 或 q。", RED))
                prompt_press_enter()

    def _dispatch_action(self, engine: GitEngine, item: Dict[str, Any]):
        """执行具体选项对应的操作"""
        itype = item["type"]
        item_id = item["id"]

        print()
        if itype == "custom":
            # 自定义命令直接执行
            raw_cmd = item["raw_cmd"]
            print(c(f"🚀 正在执行自定义命令: {raw_cmd}", BOLD + CYAN))
            res = run_git(raw_cmd.replace("git ", "").split(), cwd=engine.repo_path)
            if res.stdout:
                print(res.stdout)
            if res.stderr:
                print(c(res.stderr, YELLOW if res.success else RED))
            if res.success:
                print(c("✅ 执行完成！", GREEN))
            else:
                print(c("❌ 执行失败，请检查命令语法或仓库状态。", RED))
            prompt_press_enter()
            return

        # 预设命令分发
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
            print(c(f"功能 [{item_id}] 暂未实现或配置有误。", RED))
            prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 核心动作实现
    # ─────────────────────────────────────────────────────────

    def _action_sync(self, engine: GitEngine):
        """一键保存并同步"""
        print(c("══════════════════════════════════════════", CYAN))
        print(c("  🚀 一键保存并同步", BOLD + GREEN))
        print(c("══════════════════════════════════════════", CYAN))
        print("💡 提示：将自动拉取远端 ➔ 记录改动 ➔ 提交版本 ➔ 推送到远端。")
        
        custom_msg = input(f"{BOLD}请输入提交说明{RESET} {c('(直接回车自动生成带时间记录): ', DIM)}").strip()

        print("\n正在安全同步中，请稍候...")
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
        print(c("⬇️  正在检查并拉取远程代码...", BOLD + CYAN))
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
        print(c("🔍 代码改动详情清单:", BOLD + CYAN))
        print(f"工作目录: {c(info['path'], DIM)}")
        print()

        if info["is_clean"]:
            print(c("✨ 工作区非常干净，没有发现任何待保存的改动。", GREEN))
        else:
            if info["staged"]:
                print(c("● 已暂存待提交的文件:", GREEN))
                for f in info["staged"]:
                    print(f"  {c('+', GREEN)} {f}")
            if info["modified"]:
                print(c("● 已修改但未暂存的文件:", YELLOW))
                for f in info["modified"]:
                    print(f"  {c('M', YELLOW)} {f}")
            if info["untracked"]:
                print(c("● 新建且未跟踪的文件:", CYAN))
                for f in info["untracked"]:
                    print(f"  {c('?', CYAN)} {f}")

        stat = engine.get_diff_stat()
        if stat:
            print(f"\n{c('● 代码行数增删统计:', BOLD)}")
            print(stat)

        prompt_press_enter()

    def _action_undo(self, engine: GitEngine):
        """后悔药子菜单"""
        print(c("💊 后悔药 / 撤销改动菜单:", BOLD + MAGENTA))
        print(" [1] 放弃全部未提交的代码修改 (工作区彻底还原干净)")
        print(" [2] 撤回上一次提交 commit (代码依然保留在工作区)")
        print(" [3] 放弃单个指定文件的修改")
        print(" [b] 返回上一层")
        print()

        sub = input(f"{BOLD}请选择后悔药级别 [1/2/3, b 返回]: {RESET}").strip()
        if sub == "1":
            confirm = input(c("⚠️ 确定要彻底放弃所有未提交的代码吗？该操作不可逆！(输入 y 确认): ", RED)).strip().lower()
            if confirm == "y":
                ok, msg = engine.undo_action("discard_all")
                print(c(msg, GREEN if ok else RED))
            else:
                print(c("已取消操作。", YELLOW))
        elif sub == "2":
            ok, msg = engine.undo_action("uncommit")
            print(c(msg, GREEN if ok else RED))
        elif sub == "3":
            fname = input("请输入要丢弃修改的文件路径: ").strip()
            if fname:
                ok, msg = engine.undo_action("discard_file", target=fname)
                print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_branch(self, engine: GitEngine):
        """分支管理子菜单"""
        branches = engine.list_branches()
        print(c("🌿 分支管理菜单:", BOLD + CYAN))
        print("本地分支列表:")
        for idx, b in enumerate(branches, start=1):
            curr_mark = c("★ (当前)", GREEN) if b["is_current"] else ""
            print(f"  [{idx}] {b['name']} {curr_mark}")

        print("\n快捷操作:")
        print("  [直接输入数字] 切换到对应的分支")
        print("  [n] 新建并切换到新分支")
        print("  [b] 返回上一层")
        print()

        sub = input(f"{BOLD}请选择或输入操作: {RESET}").strip()
        if sub.lower() == "b":
            return
        if sub.lower() == "n":
            new_b = input("请输入新分支名称 (如: dev, feat-auth): ").strip()
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
                print(c("序号超出范围！", RED))
        prompt_press_enter()

    def _action_stash(self, engine: GitEngine):
        """暂存管理子菜单"""
        print(c("📦 代码暂存箱管理 (Stash):", BOLD + CYAN))
        print(" [1] 暂存存盘 (临时打包未写完的代码，工作区还原干净)")
        print(" [2] 取回恢复 (从暂存箱取回上一次保存的代码)")
        print(" [b] 返回上一层")
        print()

        sub = input(f"{BOLD}请选择操作: {RESET}").strip()
        if sub == "1":
            note = input("可选输入暂存备注 (直接回车默认时间): ").strip()
            ok, msg = engine.stash_save(note)
            print(c(msg, GREEN if ok else RED))
        elif sub == "2":
            ok, msg = engine.stash_pop()
            print(c(msg, GREEN if ok else RED))
        prompt_press_enter()

    def _action_history(self, engine: GitEngine):
        """提交历史"""
        hist = engine.get_recent_history(10)
        print(c("📜 最近 10 次提交简明历史:", BOLD + CYAN))
        if not hist:
            print("暂无提交历史。")
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
        print(c("🔍 正在查看具体代码差异 (diff):", BOLD + CYAN))
        res = run_git(["diff", "--color=always"], cwd=engine.repo_path)
        if res.stdout:
            print(res.stdout)
        else:
            print(c("当前工作区没有已修改的代码差异。", GREEN))
        prompt_press_enter()

    def _action_clean(self, engine: GitEngine):
        """清理未跟踪文件"""
        confirm = input(c("⚠️ 确定要清理所有未跟踪的文件/临时生成目录吗？(输入 y 确认): ", RED)).strip().lower()
        if confirm == "y":
            res = run_git(["clean", "-fd"], cwd=engine.repo_path)
            if res.success:
                print(c("✅ 清理完成！工作区已移除未跟踪文件。", GREEN))
            else:
                print(c(f"❌ 清理失败: {res.stderr}", RED))
        prompt_press_enter()

    def _action_tag(self, engine: GitEngine):
        """打标签"""
        tag_name = input("请输入新版本标签名称 (如 v1.0.0): ").strip()
        if not tag_name:
            return
        tag_msg = input("可选输入版本说明 (直接回车默认与标签同名): ").strip() or tag_name
        res = run_git(["tag", "-a", tag_name, "-m", tag_msg], cwd=engine.repo_path)
        if res.success:
            print(c(f"✅ 成功打上本地标签 [{tag_name}]！", GREEN))
            push_yn = input("是否同步将该标签推送到远程仓库？(y/n) [默认 y]: ").strip().lower()
            if push_yn != "n":
                pres = run_git(["push", "origin", tag_name], cwd=engine.repo_path)
                if pres.success:
                    print(c(f"🎉 标签 [{tag_name}] 已成功推送到远程仓库！", GREEN))
                else:
                    print(c(f"⚠️ 标签本地创建成功，但推送到远程失败: {pres.stderr}", YELLOW))
        else:
            print(c(f"❌ 创建标签失败: {res.stderr}", RED))
        prompt_press_enter()

    def _action_remote(self, engine: GitEngine):
        """查看远程仓库"""
        res = run_git(["remote", "-v"], cwd=engine.repo_path)
        print(c("🌐 关联的远程仓库地址:", BOLD + CYAN))
        if res.stdout:
            print(res.stdout)
        else:
            print(c("当前仓库尚未配置远程仓库 (origin)。", YELLOW))
        prompt_press_enter()

    def _action_multi_sync(self):
        """多仓库巡检与同步"""
        self._handle_multi_repo_view()

    # ─────────────────────────────────────────────────────────
    # 功能库管理与个性化设置菜单
    # ─────────────────────────────────────────────────────────

    def _menu_manage_features(self):
        """功能库管理主菜单"""
        while True:
            print()
            print(c("══════════════════════════════════════════", YELLOW))
            print(c("  🛠️  FoolGit 功能库与个性化设置", BOLD + YELLOW))
            print(c("══════════════════════════════════════════", YELLOW))
            print(" [1] 🧩 预设功能库开关 (从官方功能池自由勾选追加/移除)")
            print(" [2] ➕ 添加我的自定义 Git 命令 (自由扩展专属快捷命令)")
            print(" [3] ➖ 删除我的自定义 Git 命令")
            print(" [4] 🔄 恢复出厂设置 (重置为默认6大傻瓜功能)")
            print(" [b] 返回主菜单")
            print()

            sub = input(f"{BOLD}请选择设置项 [1/2/3/4, b 返回]: {RESET}").strip()
            if sub.lower() in ["b", ""]:
                break
            elif sub == "1":
                self._menu_toggle_presets()
            elif sub == "2":
                self._menu_add_custom_cmd()
            elif sub == "3":
                self._menu_remove_custom_cmd()
            elif sub == "4":
                conf = input(c("⚠️ 确定要重置回出厂默认设置吗？(y/n): ", RED)).strip().lower()
                if conf == "y":
                    self.config_mgr.reset_to_defaults()
                    print(c("✅ 已恢复出厂默认设置！", GREEN))
                    prompt_press_enter()

    def _menu_toggle_presets(self):
        """开启或关闭官方备选功能"""
        while True:
            active_ids = self.config_mgr.get_active_preset_ids()
            all_keys = list(PRESET_LIBRARY.keys())

            print()
            print(c("📋 官方功能库清单 (输入序号切换开启/停用):", BOLD + CYAN))
            for idx, pid in enumerate(all_keys, start=1):
                meta = PRESET_LIBRARY[pid]
                is_on = pid in active_ids
                status_badge = c("[已开启 ✓]", GREEN) if is_on else c("[已停用 ✗]", GRAY)
                print(f"  [{idx}] {status_badge} {BOLD}{meta['name']}{RESET} ── {c(meta['short_desc'], DIM)}")

            print(f"\n{c('提示: 输入数字序号直接切换对应功能状态，输入 b 返回', DIM)}")
            choice = input(f"{BOLD}请选择要切换的功能编号 [b 返回]: {RESET}").strip()

            if choice.lower() in ["b", ""]:
                break

            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(all_keys):
                    target_id = all_keys[num - 1]
                    if target_id in active_ids:
                        self.config_mgr.disable_preset(target_id)
                        print(c(f"已从主菜单移除: {PRESET_LIBRARY[target_id]['name']}", YELLOW))
                    else:
                        self.config_mgr.enable_preset(target_id)
                        print(c(f"已开启并加入主菜单: {PRESET_LIBRARY[target_id]['name']}", GREEN))
                else:
                    print(c("序号超出范围！", RED))

    def _menu_add_custom_cmd(self):
        """添加自定义命令"""
        print()
        print(c("➕ 添加自定义命令到主菜单:", BOLD + GREEN))
        name = input("1. 请输入菜单显示的名称 (例如: 推送全部标签): ").strip()
        if not name:
            print(c("名称不能为空！", RED))
            prompt_press_enter()
            return
        cmd = input("2. 请输入实际执行的 Git 命令 (例如: git push origin --tags): ").strip()
        if not cmd:
            print(c("命令不能为空！", RED))
            prompt_press_enter()
            return
        desc = input("3. 可选输入一句话功能说明: ").strip()

        cid = self.config_mgr.add_custom_command(name, cmd, desc)
        print(c(f"🎉 成功添加自定义命令 [{name}]！它已出现在主菜单中。", GREEN))
        prompt_press_enter()

    def _menu_remove_custom_cmd(self):
        """删除自定义命令"""
        cmds = self.config_mgr.get_custom_commands()
        if not cmds:
            print(c("当前暂无自定义命令。", YELLOW))
            prompt_press_enter()
            return
        print()
        print(c("➖ 请选择要删除的自定义命令:", BOLD + RED))
        for idx, item in enumerate(cmds, start=1):
            print(f"  [{idx}] {item['name']} ({item['cmd']})")
        choice = input(f"{BOLD}请输入编号 [b 返回]: {RESET}").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(cmds):
                item = cmds[idx - 1]
                self.config_mgr.remove_custom_command(item["id"])
                print(c(f"✅ 已删除命令 [{item['name']}]", GREEN))
            else:
                print(c("序号超出范围！", RED))
        prompt_press_enter()

    # ─────────────────────────────────────────────────────────
    # 多仓库巡检与非 Git 目录引导 (继承 gsyn)
    # ─────────────────────────────────────────────────────────

    def _handle_non_git_dir(self):
        """非 Git 目录下的智能响应"""
        repos = scan_multi_repos(self.target_dir)
        if repos:
            print(c(f"💡 当前目录不是 Git 仓库，但在此目录下发现了 {len(repos)} 个 Git 子项目：", CYAN))
            self._handle_multi_repo_view(repos)
        else:
            print(c("┏" + "━" * 58 + "┓", YELLOW))
            print(c("┃", YELLOW) + f"  {BOLD}当前目录不是 Git 仓库，且子目录下未找到项目{RESET}".ljust(58) + c("┃", YELLOW))
            print(c("┗" + "━" * 58 + "┛", YELLOW))
            print()
            print("您可以:")
            print(" [1] 在当前目录初始化新建一个 Git 仓库 (git init)")
            print(" [2] 克隆一个远程仓库到这里 (git clone)")
            print(" [q] 退出")
            print()
            c_input = input(f"{BOLD}请选择 [1/2, q 退出]: {RESET}").strip()
            if c_input == "1":
                res = run_git(["init"], cwd=self.target_dir)
                if res.success:
                    print(c("🎉 成功在当前目录初始化 Git 仓库！", GREEN))
                    prompt_press_enter()
                    self._run_single_repo_menu()
                else:
                    print(c(f"初始化失败: {res.stderr}", RED))
            elif c_input == "2":
                url = input("请输入远程 Git 仓库 URL: ").strip()
                if url:
                    print(f"正在克隆 {url} ...")
                    cres = run_git(["clone", url], cwd=self.target_dir)
                    if cres.success:
                        print(c("🎉 克隆成功！", GREEN))
                    else:
                        print(c(f"❌ 克隆失败: {cres.stderr}", RED))
                prompt_press_enter()

    def _handle_multi_repo_view(self, repos: Optional[List[Dict[str, Any]]] = None):
        """多仓库巡检与批量同步界面"""
        if repos is None:
            repos = scan_multi_repos(self.target_dir)

        if not repos:
            print(c("未找到任何 Git 子仓库。", YELLOW))
            prompt_press_enter()
            return

        print()
        print(c(f"════════════════ 多仓库巡检列表 (共 {len(repos)} 个) ════════════════", BOLD + CYAN))
        for idx, r in enumerate(repos, start=1):
            st_text = c("已同步 ✓", GREEN) if r["is_clean"] and r["ahead"] == 0 else c("待同步 ✎", YELLOW)
            ahead_str = f" ↑{r['ahead']}" if r["ahead"] > 0 else ""
            behind_str = f" ↓{r['behind']}" if r["behind"] > 0 else ""
            print(f" [{idx}] {BOLD}{r['name']:<20}{RESET} {c(r['branch'], CYAN):<12} {st_text}{ahead_str}{behind_str}")

        print("\n操作选项:")
        print("  [输入序号] 进入该子仓库的独立傻瓜面板")
        print("  [a] 全部一键批量同步 (Pull ➔ Commit ➔ Push)")
        print("  [b] 返回")
        print()

        choice = input(f"{BOLD}请选择操作: {RESET}").strip()
        if choice.lower() == "a":
            print(c(f"\n🚀 开始对全部 {len(repos)} 个仓库执行批量同步...", BOLD + CYAN))
            succ, fail = 0, 0
            for r in repos:
                print(f"\n▸ 同步仓库: {BOLD}{r['name']}{RESET} ({r['path']})")
                eng = GitEngine(r["path"])
                ok, logs = eng.one_click_sync()
                for l in logs:
                    print(f"  {l}")
                if ok:
                    succ += 1
                else:
                    fail += 1
            print(c(f"\n批量同步结束: 成功 {succ} 个，失败 {fail} 个", GREEN if fail == 0 else YELLOW))
            prompt_press_enter()
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(repos):
                # 切换目标目录并打开单仓库菜单
                sub_cli = FoolGitCLI(target_dir=repos[idx - 1]["path"])
                sub_cli._run_single_repo_menu()
            else:
                print(c("序号超出范围！", RED))
                prompt_press_enter()
