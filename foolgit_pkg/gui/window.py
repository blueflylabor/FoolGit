"""
FoolGit PyQt6 极简桌面主窗体与异步工作线程模块
"""

import os
import sys
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QGridLayout,
    QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMainWindow,
    QMenu, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget
)

from ..config import ConfigManager
from ..core import GitEngine, is_git_repo, parse_custom_git_args, run_git
from ..i18n import get_language, t
from .dialogs import DialogsMixin
from .theme import DARK_QSS, create_app_icon


class GitTaskThread(QThread):
    """异步执行 Git 操作的后台工作线程"""
    finished_signal = pyqtSignal(bool, list)

    def __init__(self, target_func):
        super().__init__()
        self.target_func = target_func

    def run(self):
        result = self.target_func()
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], list):
            self.finished_signal.emit(result[0], result[1])
        elif isinstance(result, tuple) and len(result) == 2:
            self.finished_signal.emit(result[0], [result[1]])
        else:
            self.finished_signal.emit(True, [])


class FoolGitMainWindow(QMainWindow, DialogsMixin):
    """FoolGit PyQt6 现代化主窗体"""

    def __init__(self, target_dir: str = "."):
        super().__init__()
        self.target_dir = target_dir
        self.config_mgr = ConfigManager()
        self.engine = GitEngine(self.target_dir)

        self.setWindowTitle("FoolGit")
        self.setWindowIcon(create_app_icon())
        self.resize(580, 820)
        self.setMinimumSize(520, 700)

        if not is_git_repo(self.target_dir):
            self._handle_non_git_repo()

        self._setup_ui()
        self.config_mgr.add_recent_repo(self.engine.repo_path)
        self.refresh_status()
        self._render_quick_actions()
        QTimer.singleShot(500, self._check_remote_freshness_async)

    def _setup_ui(self):
        """构建整体界面布局"""
        main_widget = QWidget(self)
        main_widget.setObjectName("MainWidget")
        self.setCentralWidget(main_widget)

        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(12)

        # ─────────────────────────────────────────────────────
        # 1. 顶部 Header 卡片
        # ─────────────────────────────────────────────────────
        header_card = QFrame()
        header_card.setProperty("class", "CardFrame")
        h_card_layout = QVBoxLayout(header_card)
        h_card_layout.setContentsMargins(16, 14, 16, 14)
        h_card_layout.setSpacing(10)

        top_row = QHBoxLayout()
        self.lbl_logo = QLabel("⚡ FoolGit")
        self.lbl_logo.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        self.lbl_logo.setStyleSheet("color: #FFFFFF;")
        top_row.addWidget(self.lbl_logo)

        self.lbl_ver = QLabel("v1.0.0")
        self.lbl_ver.setStyleSheet(
            "background-color: #27282D; color: #8C8F99; padding: 2px 6px; border-radius: 4px; font-size: 10px;"
        )
        top_row.addWidget(self.lbl_ver)
        top_row.addStretch()

        self.btn_lang = QPushButton(t("lang_toggle_btn"))
        self.btn_lang.setObjectName("LangButton")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_language)
        top_row.addWidget(self.btn_lang)
        h_card_layout.addLayout(top_row)

        # Row 2: Repo, Switch, Open Web, Create PR, Branch controls
        repo_row = QHBoxLayout()
        self.lbl_repo_name = QLabel("📁 ...")
        self.lbl_repo_name.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        repo_row.addWidget(self.lbl_repo_name)

        self.btn_switch_repo = QPushButton(t("gui_switch_repo_btn"))
        self.btn_switch_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_switch_repo.setStyleSheet(
            "QPushButton { padding: 3px 8px; font-size: 11px; color: #9CA3AF; border-color: #2E3038; }"
        )
        self.btn_switch_repo.clicked.connect(self._action_switch_repo)
        repo_row.addWidget(self.btn_switch_repo)

        self.btn_open_web = QPushButton(t("gui_open_remote_web"))
        self.btn_open_web.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_web.setStyleSheet(
            "QPushButton { padding: 3px 8px; font-size: 11px; color: #60A5FA; border-color: #2563EB; }"
        )
        self.btn_open_web.clicked.connect(self._action_open_web)
        repo_row.addWidget(self.btn_open_web)

        self.btn_create_pr = QPushButton(t("gui_create_pr_btn"))
        self.btn_create_pr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create_pr.setStyleSheet(
            "QPushButton { padding: 3px 8px; font-size: 11px; color: #34D399; border-color: #1E4636; }"
        )
        self.btn_create_pr.clicked.connect(self._action_create_pr)
        self.btn_create_pr.hide()
        repo_row.addWidget(self.btn_create_pr)

        repo_row.addStretch()

        self.branch_combo = QComboBox()
        self.branch_combo.setMinimumWidth(130)
        self.branch_combo.currentTextChanged.connect(self._on_branch_changed)
        repo_row.addWidget(self.branch_combo)

        btn_new_branch = QPushButton("+")
        btn_new_branch.setFixedWidth(30)
        btn_new_branch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_branch.clicked.connect(self._action_new_branch)
        repo_row.addWidget(btn_new_branch)
        h_card_layout.addLayout(repo_row)

        # Row 3: Status Badge
        self.lbl_status_pill = QLabel("...")
        self.lbl_status_pill.setObjectName("StatusPill")
        self.lbl_status_pill.setStyleSheet("background-color: #172B23; color: #10B981; border: 1px solid #1E4636;")
        h_card_layout.addWidget(self.lbl_status_pill, alignment=Qt.AlignmentFlag.AlignLeft)
        root_layout.addWidget(header_card)

        # ─────────────────────────────────────────────────────
        # 1.5 冲突急救横幅 (默认隐藏)
        # ─────────────────────────────────────────────────────
        self.conflict_banner = QFrame()
        self.conflict_banner.setStyleSheet(
            "QFrame { background-color: #2A1517; border: 1px solid #7F1D1D; border-radius: 10px; }"
        )
        cb_layout = QHBoxLayout(self.conflict_banner)
        cb_layout.setContentsMargins(14, 10, 14, 10)
        cb_layout.setSpacing(10)

        self.lbl_conflict_text = QLabel("⚠️  " + t("conflict_title"))
        self.lbl_conflict_text.setStyleSheet("color: #FCA5A5; font-weight: 700; font-size: 12px; border: none;")
        cb_layout.addWidget(self.lbl_conflict_text, stretch=1)

        self.btn_conflict_rescue = QPushButton("🚑  " + t("gui_conflict_rescue"))
        self.btn_conflict_rescue.setObjectName("UndoButton")
        self.btn_conflict_rescue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_conflict_rescue.clicked.connect(self._action_conflict_dialog)
        cb_layout.addWidget(self.btn_conflict_rescue)

        self.conflict_banner.hide()
        root_layout.addWidget(self.conflict_banner)

        # ─────────────────────────────────────────────────────
        # 2. 核心大动作: One-Click Sync & Save (Hero Card)
        # ─────────────────────────────────────────────────────
        sync_card = QFrame()
        sync_card.setProperty("class", "CardFrame")
        sync_layout = QVBoxLayout(sync_card)
        sync_layout.setContentsMargins(16, 14, 16, 14)
        sync_layout.setSpacing(8)

        self.lbl_sync_title = QLabel(t("sync_banner"))
        self.lbl_sync_title.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        self.lbl_sync_title.setStyleSheet("color: #10B981;")
        sync_layout.addWidget(self.lbl_sync_title)

        self.lbl_sync_tip = QLabel(t("sync_tip"))
        self.lbl_sync_tip.setProperty("class", "Muted")
        self.lbl_sync_tip.setWordWrap(True)
        sync_layout.addWidget(self.lbl_sync_tip)

        self.txt_commit = QLineEdit()
        self.txt_commit.setPlaceholderText(t("gui_commit_placeholder"))
        self.txt_commit.returnPressed.connect(self._action_sync)
        sync_layout.addWidget(self.txt_commit)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        self._commit_chips = []
        chip_defs = [
            ("feat", "gui_commit_chip_feat"),
            ("fix", "gui_commit_chip_fix"),
            ("docs", "gui_commit_chip_docs"),
            ("chore", "gui_commit_chip_chore"),
            ("refactor", "gui_commit_chip_refactor"),
        ]
        for prefix, i18n_key in chip_defs:
            chip_btn = QPushButton(t(i18n_key))
            chip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            chip_btn.setStyleSheet(
                "QPushButton { background-color: #202227; color: #9CA3AF; border: 1px solid #2E3038; "
                "border-radius: 6px; padding: 3px 9px; font-size: 11px; font-weight: 600; }"
                "QPushButton:hover { background-color: #2A2D34; color: #10B981; border-color: #10B981; }"
            )
            chip_btn.clicked.connect(lambda _checked=False, p=prefix: self._apply_commit_prefix(p))
            chips_row.addWidget(chip_btn)
            self._commit_chips.append((chip_btn, i18n_key))
        chips_row.addStretch()

        self.btn_auto_msg = QPushButton(t("gui_auto_msg_chip"))
        self.btn_auto_msg.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_auto_msg.setStyleSheet(
            "QPushButton { background-color: #172B23; color: #34D399; border: 1px solid #1E4636; "
            "border-radius: 6px; padding: 3px 10px; font-size: 11px; font-weight: 700; }"
            "QPushButton:hover { background-color: #1E3A2F; color: #6EE7B7; }"
        )
        self.btn_auto_msg.clicked.connect(self._fill_smart_commit_msg)
        chips_row.addWidget(self.btn_auto_msg)
        sync_layout.addLayout(chips_row)

        self.btn_sync = QPushButton("🚀  " + t("preset_sync_name"))
        self.btn_sync.setObjectName("SyncButton")
        self.btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sync.clicked.connect(self._action_sync)
        sync_layout.addWidget(self.btn_sync)

        self.lbl_sync_preview = QLabel("")
        self.lbl_sync_preview.setProperty("class", "Muted")
        self.lbl_sync_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sync_layout.addWidget(self.lbl_sync_preview)
        root_layout.addWidget(sync_card)

        # ─────────────────────────────────────────────────────
        # 3. 动态快捷操作区
        # ─────────────────────────────────────────────────────
        actions_card = QFrame()
        actions_card.setProperty("class", "CardFrame")
        self.act_layout = QVBoxLayout(actions_card)
        self.act_layout.setContentsMargins(16, 12, 16, 14)
        self.act_layout.setSpacing(10)

        self.lbl_act_section = QLabel(t("gui_quick_actions").upper())
        self.lbl_act_section.setProperty("class", "SectionTitle")
        self.act_layout.addWidget(self.lbl_act_section)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(8)
        self.act_layout.addWidget(self.grid_widget)
        root_layout.addWidget(actions_card)

        # ─────────────────────────────────────────────────────
        # 4. 工具栏 (Refresh, Settings)
        # ─────────────────────────────────────────────────────
        tools_row = QHBoxLayout()
        tools_row.setSpacing(8)

        self.btn_refresh = QPushButton(t("gui_refresh_btn"))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_status)
        tools_row.addWidget(self.btn_refresh)

        self.btn_settings = QPushButton("⚙️ " + t("settings_btn"))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("color: #60A5FA; border-color: #2563EB;")
        self.btn_settings.clicked.connect(self._open_settings_dialog)
        tools_row.addWidget(self.btn_settings)
        root_layout.addLayout(tools_row)

        # ─────────────────────────────────────────────────────
        # 5. 控制台日志框
        # ─────────────────────────────────────────────────────
        term_frame = QFrame()
        term_frame.setProperty("class", "TerminalFrame")
        term_layout = QVBoxLayout(term_frame)
        term_layout.setContentsMargins(8, 8, 8, 8)

        self.txt_console = QTextEdit()
        self.txt_console.setObjectName("LogConsole")
        self.txt_console.setReadOnly(True)
        self.txt_console.append(f"> {t('gui_terminal_ready')}")
        term_layout.addWidget(self.txt_console)
        root_layout.addWidget(term_frame, stretch=1)

    def _render_quick_actions(self):
        """动态构建与渲染所有已启用的功能卡片和自定义命令"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        active_ids = [pid for pid in self.config_mgr.get_active_preset_ids() if pid != "sync"]
        custom_cmds = self.config_mgr.get_custom_commands()

        preset_handlers = {
            "pull": ("⬇️", t("preset_pull_name"), self._action_pull, None),
            "status": ("🔍", t("preset_status_name"), self._action_status, None),
            "undo": ("💊", t("preset_undo_name"), self._action_undo_dialog, "UndoButton"),
            "branch": ("🌿", t("preset_branch_name"), self._action_branch_dialog, None),
            "stash": ("📦", t("preset_stash_name"), self._action_stash_dialog, None),
            "history": ("📜", t("preset_history_name"), self._action_history_dialog, None),
            "diff": ("🔍", t("preset_diff_name"), self._action_diff_dialog, None),
            "clean": ("🧹", t("preset_clean_name"), self._action_clean_dialog, None),
            "tag": ("🏷️", t("preset_tag_name"), self._action_tag_dialog, None),
            "remote": ("🌐", t("preset_remote_name"), self._action_remote_dialog, None),
            "multi_sync": ("🔄", t("preset_multi_sync_name"), self._action_multi_sync_dialog, None),
            "gitignore": ("🚫", t("preset_gitignore_name"), self._action_gitignore_dialog, None),
        }

        items = []
        for pid in active_ids:
            if pid in preset_handlers:
                items.append(preset_handlers[pid])

        for c_cmd in custom_cmds:
            cmd_text = c_cmd["cmd"]
            items.append(("⚡", c_cmd["name"], lambda _c=False, cmd=cmd_text: self._run_custom_command(cmd), None))

        for idx, (icon, name, handler, style_id) in enumerate(items):
            btn = QPushButton(f"{icon}  {name}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if style_id:
                btn.setObjectName(style_id)
            btn.clicked.connect(handler)
            self.grid_layout.addWidget(btn, idx // 2, idx % 2)

    def log(self, text: str):
        """向控制台追加日志并滚到底部"""
        self.txt_console.append(text)
        self.txt_console.verticalScrollBar().setValue(
            self.txt_console.verticalScrollBar().maximum()
        )

    def refresh_status(self):
        """刷新仓库健康状态、分支、预览与 PR 按钮状态"""
        info = self.engine.get_info()
        oid_suffix = f"  ·  {info['commit_oid']}" if info.get("commit_oid") else ""
        self.lbl_repo_name.setText(f"📁 {info['name']}{oid_suffix}")

        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()
        for b in self.engine.list_branches():
            self.branch_combo.addItem(b["name"])
        self.branch_combo.setCurrentText(info["branch"])
        self.branch_combo.blockSignals(False)

        if info["is_clean"]:
            status_text = t("clean_status")
            self.lbl_status_pill.setStyleSheet(
                "background-color: #12281F; color: #34D399; border: 1px solid #1A4736; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px;"
            )
        else:
            status_text = t("dirty_status", count=info["total_changes"])
            self.lbl_status_pill.setStyleSheet(
                "background-color: #2A2111; color: #FBBF24; border: 1px solid #4C3916; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px;"
            )

        if info["has_upstream"]:
            if info["ahead"] > 0 and info["behind"] > 0:
                status_text += f" (↑{info['ahead']} / ↓{info['behind']})"
            elif info["ahead"] > 0:
                status_text += f" (↑{info['ahead']})"
            elif info["behind"] > 0:
                status_text += f" (↓{info['behind']})"
            else:
                status_text += " (✓)"

        self.lbl_status_pill.setText(status_text)
        self.lbl_sync_preview.setText(self.engine.get_sync_preview())

        pr_url = self.engine.get_pr_compare_url()
        if pr_url:
            self.btn_create_pr.show()
        else:
            self.btn_create_pr.hide()

        conflicts = self.engine.get_conflict_files()
        if conflicts:
            self.lbl_conflict_text.setText(f"⚠️  {t('conflict_title')} ({len(conflicts)})")
            self.conflict_banner.show()
        else:
            self.conflict_banner.hide()

    def _run_in_background(self, task_func, on_finished=None):
        """后台异步运行任务，锁定同步按钮防连点"""
        self.btn_sync.setEnabled(False)
        self.btn_sync.setText(t("gui_syncing_btn"))
        self.btn_refresh.setEnabled(False)
        self.worker = GitTaskThread(task_func)

        def handle_done(ok, logs):
            for l in logs:
                self.log(l)
            self.btn_sync.setEnabled(True)
            self.btn_sync.setText("🚀  " + t("preset_sync_name"))
            self.btn_refresh.setEnabled(True)
            if on_finished:
                on_finished(ok)
            self.refresh_status()

        self.worker.finished_signal.connect(handle_done)
        self.worker.start()

    def _apply_commit_prefix(self, prefix: str):
        """将 Conventional Commit 前缀填充到提交输入框"""
        current = self.txt_commit.text().strip()
        for kp in ("feat:", "fix:", "docs:", "chore:", "refactor:"):
            if current.startswith(kp):
                current = current[len(kp):].lstrip()
                break
        self.txt_commit.setText(f"{prefix}: {current}" if current else f"{prefix}: ")
        self.txt_commit.setFocus()

    def _fill_smart_commit_msg(self):
        """一键生成并填充可读的改动摘要作为提交说明"""
        self.txt_commit.setText(self.engine.generate_smart_commit_msg())
        self.txt_commit.setFocus()

    def _switch_to_repo_path(self, chosen_dir: str):
        """切换到指定 Git 仓库目录并记录到最近列表"""
        self.target_dir = chosen_dir
        if not is_git_repo(self.target_dir):
            self._handle_non_git_repo()
        self.engine = GitEngine(self.target_dir)
        self.config_mgr.add_recent_repo(self.engine.repo_path)
        self.refresh_status()
        self.log(f"> 📁 {self.engine.repo_path}")
        QTimer.singleShot(200, self._check_remote_freshness_async)

    def _action_switch_repo(self):
        """弹出最近仓库快速切换菜单 + 浏览文件夹"""
        recent = self.config_mgr.get_recent_repos()
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1C1D21; color: #E5E7EB; border: 1px solid #2E3038; border-radius: 6px; padding: 4px; }"
            "QMenu::item { padding: 6px 14px; border-radius: 4px; }"
            "QMenu::item:selected { background-color: #2A2D34; color: #10B981; }"
        )
        if recent:
            header_act = menu.addAction(t("gui_recent_section"))
            header_act.setEnabled(False)
            for rp in recent:
                act = menu.addAction(f"📁  {Path(rp).name}  ({rp})")
                act.triggered.connect(lambda _checked=False, p=rp: self._switch_to_repo_path(p))
            menu.addSeparator()

        browse_act = menu.addAction("🔍  " + t("gui_browse_folder"))

        def do_browse():
            chosen_dir = QFileDialog.getExistingDirectory(
                self, t("gui_switch_repo_btn"), str(Path(self.target_dir).resolve())
            )
            if chosen_dir:
                self._switch_to_repo_path(chosen_dir)

        browse_act.triggered.connect(do_browse)
        menu.exec(self.btn_switch_repo.mapToGlobal(self.btn_switch_repo.rect().bottomLeft()))

    def _check_remote_freshness_async(self):
        """后台非阻塞检查远端是否有新提交"""
        def fetch_job():
            ok, behind = self.engine.fetch_remote_status()
            return ok, [str(behind)]

        self._fetch_worker = GitTaskThread(fetch_job)
        self._fetch_worker.finished_signal.connect(lambda ok, _logs: self.refresh_status() if ok else None)
        self._fetch_worker.start()

    def _action_open_web(self):
        """在默认浏览器中打开远程仓库网页"""
        web_url = self.engine.get_remote_web_url()
        if not web_url:
            QMessageBox.information(self, "FoolGit", t("gui_no_web_remote"))
            return
        webbrowser.open(web_url)
        self.log(f"> 🌐 {web_url}")

    def _action_create_pr(self):
        """在浏览器中打开一键发起 PR / Compare 页面"""
        pr_url = self.engine.get_pr_compare_url()
        if pr_url:
            webbrowser.open(pr_url)
            self.log(f"> 🔀 {pr_url}")

    def apply_language(self, lang: str):
        """应用语言并刷新所有控件文字 (100% 纯净无混杂)"""
        self.config_mgr.set_language(lang)
        self.btn_lang.setText(t("lang_toggle_btn"))
        self.btn_switch_repo.setText(t("gui_switch_repo_btn"))
        self.btn_open_web.setText(t("gui_open_remote_web"))
        self.btn_create_pr.setText(t("gui_create_pr_btn"))
        self.lbl_sync_title.setText(t("sync_banner"))
        self.lbl_sync_tip.setText(t("sync_tip"))
        self.txt_commit.setPlaceholderText(t("gui_commit_placeholder"))
        for chip_btn, i18n_key in self._commit_chips:
            chip_btn.setText(t(i18n_key))
        self.btn_auto_msg.setText(t("gui_auto_msg_chip"))
        self.btn_conflict_rescue.setText("🚑  " + t("gui_conflict_rescue"))
        self.btn_sync.setText("🚀  " + t("preset_sync_name"))
        self.lbl_act_section.setText(t("gui_quick_actions").upper())
        self.btn_refresh.setText(t("gui_refresh_btn"))
        self.btn_settings.setText("⚙️ " + t("settings_btn"))
        self._render_quick_actions()
        self.refresh_status()

    def _toggle_language(self):
        """中英文即时无感热切换"""
        self.apply_language("zh" if get_language() == "en" else "en")
        self.log(f"> {t('lang_changed')}")

    def _ensure_identity_gui(self) -> bool:
        """同步前检测 Git 署名，缺失时用通俗弹窗引导设置"""
        has_id, _, _ = self.engine.check_git_identity()
        if has_id:
            return True
        name, ok1 = QInputDialog.getText(self, t("identity_missing_title"), t("identity_name_prompt"))
        if not ok1 or not name.strip():
            return False
        email, ok2 = QInputDialog.getText(self, t("identity_missing_title"), t("identity_email_prompt"))
        if not ok2 or not email.strip():
            return False
        ok_save, msg = self.engine.set_git_identity(name, email)
        self.log(f"> {msg}")
        return ok_save

    def _action_sync(self):
        """触发一键保存并同步（含身份检查 + 安全体检）"""
        if not self._ensure_identity_gui():
            self.log(f"> {t('identity_skipped')}")
            return

        risks = self.engine.check_sync_risks()
        if risks["has_risk"]:
            lines = [t("risk_warning_title"), ""]
            if risks["detached_head"]:
                lines.append("• " + t("risk_detached_head"))
            if risks["sensitive_files"]:
                lines.append("• " + t("risk_sensitive_files") + " " + ", ".join(risks["sensitive_files"]))
            if risks["large_files"]:
                lf_str = ", ".join(f"{name} ({mb}MB)" for name, mb in risks["large_files"])
                lines.append("• " + t("risk_large_files") + " " + lf_str)
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle(t("gui_risk_confirm_title"))
            msg_box.setText("\n".join(lines))
            btn_ignore_sync = None
            if risks["sensitive_files"] and not risks["detached_head"]:
                btn_ignore_sync = msg_box.addButton(t("gui_risk_ignore_btn"), QMessageBox.ButtonRole.AcceptRole)
            btn_yes = msg_box.addButton(QMessageBox.StandardButton.Yes)
            btn_no = msg_box.addButton(QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(btn_no)
            msg_box.exec()

            clicked = msg_box.clickedButton()
            if clicked == btn_ignore_sync and btn_ignore_sync is not None:
                for sf in risks["sensitive_files"]:
                    _, ign_msg = self.engine.append_to_gitignore(sf)
                    self.log(f"> {ign_msg}")
                self.refresh_status()
            elif clicked != btn_yes:
                self.log(f"> {t('cancelled')}")
                return

        user_msg = self.txt_commit.text().strip()
        self.log(f"\n> ─── {t('sync_banner')} ───")
        self.log(f"> {t('syncing')}")

        def job():
            return self.engine.one_click_sync(user_msg if user_msg else None)

        self._run_in_background(job, lambda ok: self.txt_commit.clear() if ok else None)

    def _action_pull(self):
        """拉取远程更新（阻塞时提示 Auto-Locker 自动暂存拉取）"""
        self.log(f"\n> ─── {t('preset_pull_name')} ───")

        def job():
            ok, msg = self.engine.safe_pull()
            return ok, [msg]

        def on_pull_done(ok):
            if not ok:
                last_text = self.txt_console.toPlainText().splitlines()[-1] if self.txt_console.toPlainText() else ""
                if self.engine.is_pull_blocked_by_local_changes(last_text):
                    reply = QMessageBox.question(
                        self, "FoolGit",
                        t("pull_blocked_local") + "\n\n" + t("pull_auto_locker_prompt"),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self._run_in_background(self.engine.auto_locker_pull)

        self._run_in_background(job, on_pull_done)

    def _action_status(self):
        """查看详细变动清单"""
        info = self.engine.get_info()
        self.log(f"\n> ─── {t('status_title')} ───")
        if info["is_clean"]:
            self.log(f"  {t('clean_workspace')}")
        else:
            for f in info["staged"]:
                self.log(f"  [+] {f}")
            for f in info["modified"]:
                self.log(f"  [M] {f}")
            for f in info["untracked"]:
                self.log(f"  [?] {f}")
            for f in info.get("conflicts", []):
                self.log(f"  [!] {f}")
            stat = self.engine.get_diff_stat()
            if stat:
                self.log("\n" + stat)

    def _run_custom_command(self, raw_cmd: str):
        """安全解析并执行自定义 Git 命令"""
        self.log(f"\n> ─── {t('custom_running', cmd=raw_cmd)} ───")
        args = parse_custom_git_args(raw_cmd)

        def job():
            res = run_git(args, cwd=self.engine.repo_path)
            lines = []
            if res.stdout:
                lines.append(res.stdout)
            if res.stderr:
                lines.append(res.stderr)
            lines.append(t("custom_ok") if res.success else t("custom_failed"))
            return res.success, lines

        self._run_in_background(job)

    def _on_branch_changed(self, branch_name: str):
        """切换平行宇宙分支"""
        if not branch_name:
            return
        _, msg = self.engine.switch_branch(branch_name)
        self.log(f"> {msg}")
        self.refresh_status()

    def _action_new_branch(self):
        """快速新建分支"""
        text, ok = QInputDialog.getText(self, t("gui_branch_create_btn"), t("new_branch_prompt"))
        if ok and text.strip():
            _, b_msg = self.engine.create_and_switch_branch(text.strip())
            self.log(f"> {b_msg}")
            self.refresh_status()

    def _handle_non_git_repo(self):
        """非 Git 目录初始化提示"""
        reply = QMessageBox.question(
            self, "FoolGit", t("non_git_gui_prompt"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            res = run_git(["init"], cwd=self.target_dir)
            if res.success:
                QMessageBox.information(self, "FoolGit", t("non_git_init_ok"))
            else:
                QMessageBox.critical(self, "FoolGit", t("non_git_init_fail", error=res.stderr))


def launch_gui(target_dir: str = "."):
    """启动 PyQt6 极简图形应用"""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 12))
    app.setStyleSheet(DARK_QSS)

    window = FoolGitMainWindow(target_dir=target_dir)
    window.show()
    sys.exit(app.exec())
