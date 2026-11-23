"""
FoolGit 极简图形化交互界面 (GUI)
基于原生 Tkinter 构建，零外部依赖，极速秒开。
保持与 CLI 相同的傻瓜式、低心智负担理念。
"""

import os
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any, List

from .core import GitEngine, is_git_repo, scan_multi_repos, run_git
from .config import ConfigManager
from .presets import get_preset_info, ALL_PRESET_IDS
from .i18n import t, set_language, get_language

# 极简现代配色方案 (Modern Clean Palette)
BG_MAIN = "#F8FAFC"       # 浅灰白主背景
BG_CARD = "#FFFFFF"       # 纯白卡片
FG_TITLE = "#0F172A"      # 主文字
FG_MUTED = "#64748B"      # 次级文字
BORDER_COLOR = "#E2E8F0"  # 边框浅色

COLOR_PRIMARY = "#2563EB" # 经典科技蓝
COLOR_SUCCESS = "#10B981" # 翡翠绿 (一键同步)
COLOR_WARN = "#F59E0B"    # 琥珀黄 (待推送/改动)
COLOR_DANGER = "#EF4444"  # 珊瑚红 (后悔药/撤销)
COLOR_PURPLE = "#8B5CF6"  # 紫色


class FoolGitGUI:
    """FoolGit 极简桌面图形窗口"""

    def __init__(self, target_dir: str = "."):
        self.target_dir = target_dir
        self.config_mgr = ConfigManager()
        self.engine = GitEngine(self.target_dir)

        self.root = tk.Tk()
        self.root.title("FoolGit")
        self.root.geometry("540x720")
        self.root.minsize(480, 600)
        self.root.configure(bg=BG_MAIN)

        # 检查是否为有效 Git 仓库
        if not is_git_repo(self.target_dir):
            self._prompt_init_or_clone()

        self._init_styles()
        self._build_ui()
        self.refresh_status()

    def _init_styles(self):
        """配置 ttk 样式"""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", background=BG_MAIN, font=("Helvetica", 11))
        style.configure("Card.TFrame", background=BG_CARD, relief="flat")
        style.configure("TLabel", background=BG_CARD, foreground=FG_TITLE)
        style.configure("Muted.TLabel", background=BG_CARD, foreground=FG_MUTED, font=("Helvetica", 10))
        style.configure("Header.TLabel", background=BG_CARD, foreground=FG_TITLE, font=("Helvetica", 14, "bold"))
        style.configure("Pill.TLabel", background="#E2E8F0", foreground=FG_TITLE, font=("Helvetica", 10, "bold"), padding=4)

    def _build_ui(self):
        """组装界面布局"""
        # 主可滚动/容器卡片
        container = tk.Frame(self.root, bg=BG_MAIN, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        # 1. 顶部状态栏与语言切换卡片
        top_card = tk.Frame(container, bg=BG_CARD, padx=14, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_card.pack(fill=tk.X, pady=(0, 12))

        # 顶部第一行: App 标头 + 语言切换按钮
        header_row = tk.Frame(top_card, bg=BG_CARD)
        header_row.pack(fill=tk.X)

        self.lbl_app_name = tk.Label(header_row, text="FoolGit", font=("Helvetica", 16, "bold"), fg=COLOR_PRIMARY, bg=BG_CARD)
        self.lbl_app_name.pack(side=tk.LEFT)

        self.lbl_version_badge = tk.Label(header_row, text="v1.0.0", font=("Helvetica", 9), fg=FG_MUTED, bg="#F1F5F9", padx=6, pady=2)
        self.lbl_version_badge.pack(side=tk.LEFT, padx=6)

        # 语言切换按钮
        self.btn_lang = tk.Button(
            header_row,
            text="🌐 " + ("中文" if get_language() == "en" else "English"),
            font=("Helvetica", 10),
            bg="#F1F5F9",
            fg=FG_TITLE,
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self._toggle_language
        )
        self.btn_lang.pack(side=tk.RIGHT)

        # 仓库与分支信息行
        repo_row = tk.Frame(top_card, bg=BG_CARD)
        repo_row.pack(fill=tk.X, pady=(8, 4))

        self.lbl_repo_name = tk.Label(repo_row, text="📁 ...", font=("Helvetica", 11, "bold"), fg=FG_TITLE, bg=BG_CARD)
        self.lbl_repo_name.pack(side=tk.LEFT)

        # 分支下拉选择
        self.branch_var = tk.StringVar(value="...")
        self.branch_combo = ttk.Combobox(repo_row, textvariable=self.branch_var, state="readonly", width=14)
        self.branch_combo.pack(side=tk.LEFT, padx=8)
        self.branch_combo.bind("<<ComboboxSelected>>", self._on_branch_selected)

        # 新建分支小按钮
        btn_new_branch = tk.Button(repo_row, text="+", font=("Helvetica", 10, "bold"), bg="#F1F5F9", fg=COLOR_PRIMARY, relief="flat", cursor="hand2", command=self._action_new_branch, width=2)
        btn_new_branch.pack(side=tk.LEFT)

        # 状态指示胶囊
        self.lbl_status_pill = tk.Label(
            top_card,
            text="Checking status...",
            font=("Helvetica", 10),
            bg="#ECFDF5",
            fg=COLOR_SUCCESS,
            padx=8,
            pady=4,
            relief="flat"
        )
        self.lbl_status_pill.pack(anchor="w", pady=(4, 0))

        # 2. 核心大动作: 一键保存并同步 (Hero Action)
        sync_card = tk.Frame(container, bg=BG_CARD, padx=14, pady=14, highlightbackground=BORDER_COLOR, highlightthickness=1)
        sync_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_sync_title = tk.Label(sync_card, text=t("sync_banner"), font=("Helvetica", 13, "bold"), fg=COLOR_SUCCESS, bg=BG_CARD)
        self.lbl_sync_title.pack(anchor="w")

        self.lbl_sync_tip = tk.Label(sync_card, text=t("sync_tip"), font=("Helvetica", 9), fg=FG_MUTED, bg=BG_CARD, wraplength=480, justify="left")
        self.lbl_sync_tip.pack(anchor="w", pady=(2, 8))

        # 提交信息输入框
        commit_box_frame = tk.Frame(sync_card, bg=BG_CARD)
        commit_box_frame.pack(fill=tk.X, pady=(0, 8))

        self.txt_commit_msg = tk.Entry(commit_box_frame, font=("Helvetica", 11), bg="#F8FAFC", fg=FG_TITLE, relief="solid", bd=1)
        self.txt_commit_msg.pack(fill=tk.X, ipady=4)
        self.txt_commit_msg.insert(0, "")

        # 大一键同步按钮
        self.btn_sync = tk.Button(
            sync_card,
            text="🚀  " + t("preset_sync_name"),
            font=("Helvetica", 12, "bold"),
            bg=COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self._action_sync
        )
        self.btn_sync.pack(fill=tk.X)

        # 3. 常用高频快捷卡片区 (2x2 Grid)
        actions_card = tk.Frame(container, bg=BG_CARD, padx=14, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        actions_card.pack(fill=tk.X, pady=(0, 12))

        self.lbl_quick_title = tk.Label(actions_card, text="⚡ Quick Actions / 常用操作", font=("Helvetica", 11, "bold"), fg=FG_TITLE, bg=BG_CARD)
        self.lbl_quick_title.pack(anchor="w", pady=(0, 8))

        grid_frame = tk.Frame(actions_card, bg=BG_CARD)
        grid_frame.pack(fill=tk.X)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # 4 个日常核心按钮
        self.btn_pull = tk.Button(grid_frame, text="⬇️  " + t("preset_pull_name"), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=self._action_pull)
        self.btn_pull.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))

        self.btn_status = tk.Button(grid_frame, text="🔍  " + t("preset_status_name"), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=self._action_status)
        self.btn_status.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 6))

        self.btn_undo = tk.Button(grid_frame, text="💊  " + t("preset_undo_name"), font=("Helvetica", 10), bg="#FEE2E2", fg=COLOR_DANGER, relief="flat", cursor="hand2", pady=8, command=self._action_undo_dialog)
        self.btn_undo.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=0)

        self.btn_stash = tk.Button(grid_frame, text="📦  " + t("preset_stash_name"), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=self._action_stash_dialog)
        self.btn_stash.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=0)

        # 4. 自选扩展动作与设置栏
        bottom_bar = tk.Frame(container, bg=BG_MAIN)
        bottom_bar.pack(fill=tk.X, pady=(0, 8))

        self.btn_history = tk.Button(bottom_bar, text="📜 " + t("preset_history_name"), font=("Helvetica", 9), bg=BG_CARD, fg=FG_MUTED, relief="flat", cursor="hand2", padx=8, pady=4, command=self._action_history)
        self.btn_history.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_diff = tk.Button(bottom_bar, text="🔍 Diff", font=("Helvetica", 9), bg=BG_CARD, fg=FG_MUTED, relief="flat", cursor="hand2", padx=8, pady=4, command=self._action_diff)
        self.btn_diff.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_settings = tk.Button(bottom_bar, text="⚙️ " + t("settings_title").replace("🛠️  ", ""), font=("Helvetica", 9), bg=BG_CARD, fg=COLOR_PRIMARY, relief="flat", cursor="hand2", padx=8, pady=4, command=self._open_settings_dialog)
        self.btn_settings.pack(side=tk.RIGHT)

        # 5. 底部操作日志反馈控制台
        log_card = tk.Frame(container, bg="#1E293B", padx=10, pady=8)
        log_card.pack(fill=tk.BOTH, expand=True)

        self.txt_log = tk.Text(log_card, bg="#1E293B", fg="#E2E8F0", font=("Menlo", 10), relief="flat", wrap="word", height=6)
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        self._append_log("FoolGit Ready. Click 'One-Click Sync' to commit & push.")

    # ─────────────────────────────────────────────────────────
    # 状态刷新与异步执行器
    # ─────────────────────────────────────────────────────────

    def _append_log(self, text: str):
        """向底部控制台追加日志"""
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

    def refresh_status(self):
        """刷新仓库健康状态和分支列表"""
        info = self.engine.get_info()
        self.lbl_repo_name.config(text=f"📁 {info['name']}")

        # 刷新分支列表
        branches = self.engine.list_branches()
        branch_names = [b["name"] for b in branches]
        self.branch_combo["values"] = branch_names
        self.branch_var.set(info["branch"])

        # 状态胶囊更新
        if info["is_clean"]:
            status_text = t("clean_status")
            badge_bg = "#ECFDF5"
            badge_fg = COLOR_SUCCESS
        else:
            status_text = t("dirty_status", count=info["total_changes"])
            badge_bg = "#FEF3C7"
            badge_fg = COLOR_WARN

        if info["has_upstream"]:
            if info["ahead"] > 0 and info["behind"] > 0:
                status_text += f" (↑{info['ahead']} / ↓{info['behind']})"
            elif info["ahead"] > 0:
                status_text += f" (↑{info['ahead']})"
            elif info["behind"] > 0:
                status_text += f" (↓{info['behind']})"
            else:
                status_text += " (✓)"

        self.lbl_status_pill.config(text=status_text, bg=badge_bg, fg=badge_fg)

    def _run_async(self, func, on_done=None):
        """在后台线程执行耗时 Git 命令，防止界面卡顿"""
        def worker():
            try:
                func()
            finally:
                if on_done:
                    self.root.after(0, on_done)
                self.root.after(0, self.refresh_status)

        t_thread = threading.Thread(target=worker, daemon=True)
        t_thread.start()

    # ─────────────────────────────────────────────────────────
    # 界面交互与 Git 动作
    # ─────────────────────────────────────────────────────────

    def _toggle_language(self):
        """一键切换当前语言并热重载界面文字"""
        new_lang = "zh" if get_language() == "en" else "en"
        self.config_mgr.set_language(new_lang)

        # 刷新所有控件文字
        self.btn_lang.config(text="🌐 " + ("中文" if new_lang == "en" else "English"))
        self.lbl_sync_title.config(text=t("sync_banner"))
        self.lbl_sync_tip.config(text=t("sync_tip"))
        self.btn_sync.config(text="🚀  " + t("preset_sync_name"))
        self.btn_pull.config(text="⬇️  " + t("preset_pull_name"))
        self.btn_status.config(text="🔍  " + t("preset_status_name"))
        self.btn_undo.config(text="💊  " + t("preset_undo_name"))
        self.btn_stash.config(text="📦  " + t("preset_stash_name"))
        self.btn_history.config(text="📜 " + t("preset_history_name"))
        self.btn_settings.config(text="⚙️ " + t("settings_title").replace("🛠️  ", ""))
        self.refresh_status()
        self._append_log(f"Language switched to: {new_lang.upper()}")

    def _action_sync(self):
        """一键同步按钮触发"""
        user_msg = self.txt_commit_msg.get().strip()

        def job():
            self._append_log("--- " + t("sync_banner") + " ---")
            self._append_log(t("syncing"))
            ok, logs = self.engine.one_click_sync(user_msg if user_msg else None)
            for l in logs:
                self._append_log(l)
            if ok:
                self.txt_commit_msg.delete(0, tk.END)

        self._run_async(job)

    def _action_pull(self):
        """拉取最新代码"""
        def job():
            self._append_log("--- " + t("preset_pull_name") + " ---")
            ok, msg = self.engine.safe_pull()
            self._append_log(msg)

        self._run_async(job)

    def _action_status(self):
        """查看改动详情"""
        info = self.engine.get_info()
        self._append_log(f"--- {t('status_title')} ---")
        if info["is_clean"]:
            self._append_log(t("clean_workspace"))
        else:
            for f in info["staged"]:
                self._append_log(f"  [+] {f}")
            for f in info["modified"]:
                self._append_log(f"  [M] {f}")
            for f in info["untracked"]:
                self._append_log(f"  [?] {f}")
            stat = self.engine.get_diff_stat()
            if stat:
                self._append_log(stat)

    def _action_undo_dialog(self):
        """后悔药弹窗选择"""
        win = tk.Toplevel(self.root)
        win.title(t("undo_title"))
        win.geometry("380x240")
        win.configure(bg=BG_CARD)
        win.transient(self.root)

        tk.Label(win, text=t("undo_title"), font=("Helvetica", 12, "bold"), fg=COLOR_DANGER, bg=BG_CARD).pack(pady=(16, 12))

        def do_discard_all():
            win.destroy()
            if messagebox.askyesno("Confirm", t("discard_all_confirm")):
                ok, msg = self.engine.undo_action("discard_all")
                self._append_log(msg)
                self.refresh_status()

        def do_uncommit():
            win.destroy()
            ok, msg = self.engine.undo_action("uncommit")
            self._append_log(msg)
            self.refresh_status()

        tk.Button(win, text=t("undo_opt_all").strip(), font=("Helvetica", 10), bg="#FEE2E2", fg=COLOR_DANGER, relief="flat", cursor="hand2", pady=8, command=do_discard_all).pack(fill=tk.X, padx=20, pady=4)
        tk.Button(win, text=t("undo_opt_commit").strip(), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=do_uncommit).pack(fill=tk.X, padx=20, pady=4)

    def _action_stash_dialog(self):
        """暂存箱弹窗选择"""
        win = tk.Toplevel(self.root)
        win.title(t("stash_title"))
        win.geometry("360x200")
        win.configure(bg=BG_CARD)
        win.transient(self.root)

        tk.Label(win, text=t("stash_title"), font=("Helvetica", 12, "bold"), fg=FG_TITLE, bg=BG_CARD).pack(pady=(16, 12))

        def do_save():
            win.destroy()
            ok, msg = self.engine.stash_save()
            self._append_log(msg)
            self.refresh_status()

        def do_pop():
            win.destroy()
            ok, msg = self.engine.stash_pop()
            self._append_log(msg)
            self.refresh_status()

        tk.Button(win, text=t("stash_opt_save").strip(), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=do_save).pack(fill=tk.X, padx=20, pady=4)
        tk.Button(win, text=t("stash_opt_pop").strip(), font=("Helvetica", 10), bg="#F1F5F9", fg=FG_TITLE, relief="flat", cursor="hand2", pady=8, command=do_pop).pack(fill=tk.X, padx=20, pady=4)

    def _action_history(self):
        """查看最近 10 次提交"""
        hist = self.engine.get_recent_history(10)
        self._append_log(f"--- {t('history_title')} ---")
        if not hist:
            self._append_log(t("no_history"))
        else:
            for item in hist:
                parts = item.split("|")
                if len(parts) >= 4:
                    self._append_log(f"{parts[0]} - {parts[3]} ({parts[2]} by {parts[1]})")
                else:
                    self._append_log(item)

    def _action_diff(self):
        """查看改动代码 diff"""
        res = run_git(["diff"], cwd=self.engine.repo_path)
        self._append_log(f"--- {t('diff_title')} ---")
        if res.stdout:
            self._append_log(res.stdout)
        else:
            self._append_log(t("no_diff"))

    def _on_branch_selected(self, event):
        """下拉选择分支后快速切换"""
        target_branch = self.branch_var.get()
        if target_branch:
            ok, msg = self.engine.switch_branch(target_branch)
            self._append_log(msg)
            self.refresh_status()

    def _action_new_branch(self):
        """新建分支输入弹窗"""
        name = simpledialog.askstring("New Branch", t("new_branch_prompt"), parent=self.root)
        if name:
            ok, msg = self.engine.create_and_switch_branch(name)
            self._append_log(msg)
            self.refresh_status()

    def _open_settings_dialog(self):
        """功能库开关与自定义命令设置窗口"""
        win = tk.Toplevel(self.root)
        win.title(t("settings_title"))
        win.geometry("440x480")
        win.configure(bg=BG_CARD)
        win.transient(self.root)

        tk.Label(win, text=t("settings_title"), font=("Helvetica", 12, "bold"), fg=FG_TITLE, bg=BG_CARD).pack(pady=(16, 8))

        # 功能开关列表容器
        frame_list = tk.Frame(win, bg=BG_CARD, padx=16)
        frame_list.pack(fill=tk.BOTH, expand=True)

        active_ids = self.config_mgr.get_active_preset_ids()
        check_vars = {}

        for pid in ALL_PRESET_IDS:
            meta = get_preset_info(pid)
            var = tk.BooleanVar(value=pid in active_ids)
            check_vars[pid] = var

            def make_toggle(target_id, target_var):
                def on_toggle():
                    if target_var.get():
                        self.config_mgr.enable_preset(target_id)
                    else:
                        self.config_mgr.disable_preset(target_id)
                    self.refresh_status()
                return on_toggle

            cb = tk.Checkbutton(
                frame_list,
                text=f"{meta['name']} ({meta['short_desc']})",
                variable=var,
                bg=BG_CARD,
                fg=FG_TITLE,
                anchor="w",
                font=("Helvetica", 10),
                command=make_toggle(pid, var)
            )
            cb.pack(fill=tk.X, pady=2)

        # 底部重置按钮
        def do_reset():
            if messagebox.askyesno("Reset", t("reset_confirm")):
                self.config_mgr.reset_to_defaults()
                win.destroy()
                self.refresh_status()
                self._append_log(t("reset_done"))

        tk.Button(win, text=t("settings_opt_reset"), font=("Helvetica", 10), bg="#F1F5F9", fg=COLOR_DANGER, relief="flat", cursor="hand2", command=do_reset).pack(fill=tk.X, padx=20, pady=12)

    def _prompt_init_or_clone(self):
        """非 Git 目录下的提示引导"""
        if messagebox.askyesno("FoolGit", "Current directory is not a Git repository. Initialize one?"):
            res = run_git(["init"], cwd=self.target_dir)
            if res.success:
                messagebox.showinfo("Success", "Git repository initialized successfully!")
            else:
                messagebox.showerror("Error", f"Init failed: {res.stderr}")

    def start(self):
        """启动 GUI 事件循环"""
        self.root.mainloop()


def launch_gui(target_dir: str = "."):
    """GUI 启动便捷函数"""
    app = FoolGitGUI(target_dir=target_dir)
    app.start()
