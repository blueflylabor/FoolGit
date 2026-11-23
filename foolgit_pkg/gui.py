"""
FoolGit 极简图形化交互界面 (GUI) - PyQt6 版本
高质感黑灰极简程序员科技风 (Dark/Gray Minimalist Aesthetic)
纯净多语言支持，彻底杜绝中英文混杂。
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTextEdit, QFrame, QDialog, QCheckBox, QMessageBox, QInputDialog,
    QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

from .core import GitEngine, is_git_repo, run_git
from .config import ConfigManager
from .presets import get_preset_info, ALL_PRESET_IDS
from .i18n import t, set_language, get_language

# ─────────────────────────────────────────────────────────────
# 极简黑灰程序员 QSS 样式表 (Dark/Charcoal Modern Theme)
# ─────────────────────────────────────────────────────────────
DARK_QSS = """
QMainWindow, QWidget#MainWidget {
    background-color: #121316;
    color: #F3F4F6;
    font-family: -apple-system, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
}

QFrame.CardFrame {
    background-color: #1C1D21;
    border: 1px solid #2B2C32;
    border-radius: 10px;
}

QFrame.TerminalFrame {
    background-color: #0A0A0C;
    border: 1px solid #222328;
    border-radius: 8px;
}

QLabel {
    color: #F3F4F6;
    font-size: 13px;
}

QLabel.Muted {
    color: #8C8F99;
    font-size: 11px;
}

QLabel.SectionTitle {
    color: #8C8F99;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* 按钮基础样式 */
QPushButton {
    background-color: #27282D;
    color: #E4E7EB;
    border: 1px solid #36373E;
    border-radius: 7px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #32333A;
    border-color: #4A4B54;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #1F2024;
}

/* 一键同步按钮 (Emerald Accent) */
QPushButton#SyncButton {
    background-color: #10B981;
    color: #FFFFFF;
    border: 1px solid #059669;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 20px;
    border-radius: 8px;
}

QPushButton#SyncButton:hover {
    background-color: #059669;
    border-color: #047857;
}

QPushButton#SyncButton:pressed {
    background-color: #047857;
}

/* 后悔药按钮 (Danger Accent) */
QPushButton#UndoButton {
    background-color: #2A1D20;
    color: #F87171;
    border: 1px solid #4D2529;
}

QPushButton#UndoButton:hover {
    background-color: #3B2227;
    border-color: #6E3036;
    color: #FCA5A5;
}

/* 语言切换标签按钮 */
QPushButton#LangButton {
    background-color: #1E2024;
    color: #9CA3AF;
    border: 1px solid #2E3036;
    padding: 4px 10px;
    font-size: 11px;
    border-radius: 6px;
}

QPushButton#LangButton:hover {
    background-color: #2A2C33;
    color: #FFFFFF;
    border-color: #3F424A;
}

/* 输入框 */
QLineEdit {
    background-color: #121316;
    border: 1px solid #2D2E35;
    border-radius: 7px;
    padding: 9px 12px;
    color: #F3F4F6;
    font-size: 13px;
    selection-background-color: #2563EB;
}

QLineEdit:focus {
    border: 1px solid #3B82F6;
    background-color: #16171B;
}

/* 下拉菜单 */
QComboBox {
    background-color: #222328;
    color: #E4E7EB;
    border: 1px solid #32333A;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
}

QComboBox:hover {
    border-color: #44454E;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1C1D21;
    color: #E4E7EB;
    border: 1px solid #32333A;
    selection-background-color: #2B2C32;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

/* 控制台日志窗口 */
QTextEdit#LogConsole {
    background-color: #0A0A0C;
    color: #A7F3D0;
    border: none;
    font-family: "SF Mono", Menlo, Monaco, "Courier New", monospace;
    font-size: 11.5px;
    line-height: 1.4;
    padding: 8px;
}

/* 状态胶囊 */
QLabel#StatusPill {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}
"""


class GitTaskThread(QThread):
    """异步执行 Git 操作的后台工作线程"""
    finished_signal = pyqtSignal(bool, list)
    single_msg_signal = pyqtSignal(str)

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


class FoolGitMainWindow(QMainWindow):
    """FoolGit PyQt6 现代化主窗体"""

    def __init__(self, target_dir: str = "."):
        super().__init__()
        self.target_dir = target_dir
        self.config_mgr = ConfigManager()
        self.engine = GitEngine(self.target_dir)

        self.setWindowTitle("FoolGit")
        self.resize(540, 750)
        self.setMinimumSize(480, 640)

        # 检查是否为 Git 仓库
        if not is_git_repo(self.target_dir):
            self._handle_non_git_repo()

        self._setup_ui()
        self.refresh_status()

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

        # Row 1: Logo, Version, Language Switcher
        top_row = QHBoxLayout()
        self.lbl_logo = QLabel("⚡ FoolGit")
        self.lbl_logo.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        self.lbl_logo.setStyleSheet("color: #FFFFFF;")
        top_row.addWidget(self.lbl_logo)

        self.lbl_ver = QLabel("v1.0.0")
        self.lbl_ver.setStyleSheet("background-color: #27282D; color: #8C8F99; padding: 2px 6px; border-radius: 4px; font-size: 10px;")
        top_row.addWidget(self.lbl_ver)

        top_row.addStretch()

        # 语言切换按钮 (100% 纯净显示)
        self.btn_lang = QPushButton(t("lang_toggle_btn"))
        self.btn_lang.setObjectName("LangButton")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_language)
        top_row.addWidget(self.btn_lang)

        h_card_layout.addLayout(top_row)

        # Row 2: Repo & Branch controls
        repo_row = QHBoxLayout()
        self.lbl_repo_name = QLabel("📁 ...")
        self.lbl_repo_name.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        repo_row.addWidget(self.lbl_repo_name)

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
        self.lbl_status_pill = QLabel("Checking status...")
        self.lbl_status_pill.setObjectName("StatusPill")
        self.lbl_status_pill.setStyleSheet("background-color: #172B23; color: #10B981; border: 1px solid #1E4636;")
        h_card_layout.addWidget(self.lbl_status_pill, alignment=Qt.AlignmentFlag.AlignLeft)

        root_layout.addWidget(header_card)

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
        sync_layout.addWidget(self.txt_commit)

        self.btn_sync = QPushButton("🚀  " + t("preset_sync_name"))
        self.btn_sync.setObjectName("SyncButton")
        self.btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sync.clicked.connect(self._action_sync)
        sync_layout.addWidget(self.btn_sync)

        root_layout.addWidget(sync_card)

        # ─────────────────────────────────────────────────────
        # 3. 常用高频快捷操作 (2x2 Grid)
        # ─────────────────────────────────────────────────────
        actions_card = QFrame()
        actions_card.setProperty("class", "CardFrame")
        act_layout = QVBoxLayout(actions_card)
        act_layout.setContentsMargins(16, 12, 16, 14)
        act_layout.setSpacing(10)

        self.lbl_act_section = QLabel(t("gui_quick_actions").upper())
        self.lbl_act_section.setProperty("class", "SectionTitle")
        act_layout.addWidget(self.lbl_act_section)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        self.btn_pull = QPushButton("⬇️  " + t("preset_pull_name"))
        self.btn_pull.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pull.clicked.connect(self._action_pull)
        grid_layout.addWidget(self.btn_pull, 0, 0)

        self.btn_status = QPushButton("🔍  " + t("preset_status_name"))
        self.btn_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_status.clicked.connect(self._action_status)
        grid_layout.addWidget(self.btn_status, 0, 1)

        self.btn_undo = QPushButton("💊  " + t("preset_undo_name"))
        self.btn_undo.setObjectName("UndoButton")
        self.btn_undo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_undo.clicked.connect(self._action_undo_dialog)
        grid_layout.addWidget(self.btn_undo, 1, 0)

        self.btn_stash = QPushButton("📦  " + t("preset_stash_name"))
        self.btn_stash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stash.clicked.connect(self._action_stash_dialog)
        grid_layout.addWidget(self.btn_stash, 1, 1)

        act_layout.addLayout(grid_layout)
        root_layout.addWidget(actions_card)

        # ─────────────────────────────────────────────────────
        # 4. 工具栏 (History, Diff, Settings)
        # ─────────────────────────────────────────────────────
        tools_row = QHBoxLayout()
        tools_row.setSpacing(8)

        self.btn_history = QPushButton("📜 " + t("preset_history_name"))
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_history.clicked.connect(self._action_history)
        tools_row.addWidget(self.btn_history)

        self.btn_diff = QPushButton("🔍 " + t("preset_diff_name"))
        self.btn_diff.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_diff.clicked.connect(self._action_diff)
        tools_row.addWidget(self.btn_diff)

        self.btn_settings = QPushButton("⚙️ " + t("settings_btn"))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("color: #60A5FA; border-color: #2563EB;")
        self.btn_settings.clicked.connect(self._open_settings_dialog)
        tools_row.addWidget(self.btn_settings)

        root_layout.addLayout(tools_row)

        # ─────────────────────────────────────────────────────
        # 5. 黑客风控制台日志框 (Terminal Output Box)
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

    # ─────────────────────────────────────────────────────────
    # 状态刷新与异步工作流
    # ─────────────────────────────────────────────────────────

    def log(self, text: str):
        """向黑客终端追加日志"""
        self.txt_console.append(text)
        self.txt_console.verticalScrollBar().setValue(
            self.txt_console.verticalScrollBar().maximum()
        )

    def refresh_status(self):
        """刷新仓库健康状态和分支"""
        info = self.engine.get_info()
        self.lbl_repo_name.setText(f"📁 {info['name']}")

        # 刷新分支列表 (静音 signal 避免触发切分支)
        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()
        branches = self.engine.list_branches()
        for b in branches:
            self.branch_combo.addItem(b["name"])
        self.branch_combo.setCurrentText(info["branch"])
        self.branch_combo.blockSignals(False)

        # 状态胶囊更新
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

    def _run_in_background(self, task_func, on_finished=None):
        """后台异步运行任务，保证主界面丝滑不假死"""
        self.worker = GitTaskThread(task_func)

        def handle_done(ok, logs):
            for l in logs:
                self.log(l)
            if on_finished:
                on_finished(ok)
            self.refresh_status()

        self.worker.finished_signal.connect(handle_done)
        self.worker.start()

    # ─────────────────────────────────────────────────────────
    # 语言热切换 (100% 纯净无混杂)
    # ─────────────────────────────────────────────────────────

    def apply_language(self, lang: str):
        """应用语言并刷新所有控件文字 (100% 纯净无混杂)"""
        self.config_mgr.set_language(lang)
        self.btn_lang.setText(t("lang_toggle_btn"))
        self.lbl_sync_title.setText(t("sync_banner"))
        self.lbl_sync_tip.setText(t("sync_tip"))
        self.txt_commit.setPlaceholderText(t("gui_commit_placeholder"))
        self.btn_sync.setText("🚀  " + t("preset_sync_name"))
        self.lbl_act_section.setText(t("gui_quick_actions").upper())
        self.btn_pull.setText("⬇️  " + t("preset_pull_name"))
        self.btn_status.setText("🔍  " + t("preset_status_name"))
        self.btn_undo.setText("💊  " + t("preset_undo_name"))
        self.btn_stash.setText("📦  " + t("preset_stash_name"))
        self.btn_history.setText("📜 " + t("preset_history_name"))
        self.btn_diff.setText("🔍 " + t("preset_diff_name"))
        self.btn_settings.setText("⚙️ " + t("settings_btn"))
        self.refresh_status()

    def _toggle_language(self):
        """中英文即时无感热切换"""
        new_lang = "zh" if get_language() == "en" else "en"
        self.apply_language(new_lang)
        self.log(f"> {t('lang_changed')}")

    # ─────────────────────────────────────────────────────────
    # 业务动作
    # ─────────────────────────────────────────────────────────

    def _action_sync(self):
        """触发一键保存并同步"""
        user_msg = self.txt_commit.text().strip()

        self.log(f"\n> ─── {t('sync_banner')} ───")
        self.log(f"> {t('syncing')}")

        def job():
            return self.engine.one_click_sync(user_msg if user_msg else None)

        def on_done(ok):
            if ok:
                self.txt_commit.clear()

        self._run_in_background(job, on_done)

    def _action_pull(self):
        """拉取远程更新"""
        self.log(f"\n> ─── {t('preset_pull_name')} ───")

        def job():
            ok, msg = self.engine.safe_pull()
            return ok, [msg]

        self._run_in_background(job)

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
            stat = self.engine.get_diff_stat()
            if stat:
                self.log("\n" + stat)

    def _action_undo_dialog(self):
        """极简后悔药弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("undo_title").replace(":", ""))
        dialog.setFixedWidth(380)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("undo_title"))
        title.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #EF4444;")
        d_layout.addWidget(title)

        btn_all = QPushButton(t("undo_opt_all"))
        btn_all.setObjectName("UndoButton")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_all)

        btn_uncommit = QPushButton(t("undo_opt_commit"))
        btn_uncommit.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_uncommit)

        def do_all():
            dialog.accept()
            reply = QMessageBox.question(
                self,
                "Confirm",
                t("discard_all_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                ok, msg = self.engine.undo_action("discard_all")
                self.log(f"> {msg}")
                self.refresh_status()

        def do_uncommit():
            dialog.accept()
            ok, msg = self.engine.undo_action("uncommit")
            self.log(f"> {msg}")
            self.refresh_status()

        btn_all.clicked.connect(do_all)
        btn_uncommit.clicked.connect(do_uncommit)
        dialog.exec()

    def _action_stash_dialog(self):
        """暂存箱弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("stash_title").replace(":", ""))
        dialog.setFixedWidth(380)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("stash_title"))
        title.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        d_layout.addWidget(title)

        btn_save = QPushButton(t("stash_opt_save"))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_save)

        btn_pop = QPushButton(t("stash_opt_pop"))
        btn_pop.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_pop)

        def do_save():
            dialog.accept()
            ok, msg = self.engine.stash_save()
            self.log(f"> {msg}")
            self.refresh_status()

        def do_pop():
            dialog.accept()
            ok, msg = self.engine.stash_pop()
            self.log(f"> {msg}")
            self.refresh_status()

        btn_save.clicked.connect(do_save)
        btn_pop.clicked.connect(do_pop)
        dialog.exec()

    def _action_history(self):
        """查看最近 10 次提交"""
        hist = self.engine.get_recent_history(10)
        self.log(f"\n> ─── {t('history_title')} ───")
        if not hist:
            self.log(f"  {t('no_history')}")
        else:
            for item in hist:
                parts = item.split("|")
                if len(parts) >= 4:
                    self.log(f"  {parts[0]} - {parts[3]} ({parts[2]} by {parts[1]})")
                else:
                    self.log(f"  {item}")

    def _action_diff(self):
        """查看 Diff 代码改动"""
        res = run_git(["diff"], cwd=self.engine.repo_path)
        self.log(f"\n> ─── {t('diff_title')} ───")
        if res.stdout:
            self.log(res.stdout)
        else:
            self.log(f"  {t('no_diff')}")

    def _on_branch_changed(self, branch_name: str):
        """切换分支"""
        if not branch_name:
            return
        ok, msg = self.engine.switch_branch(branch_name)
        self.log(f"> {msg}")
        self.refresh_status()

    def _action_new_branch(self):
        """新建分支"""
        text, ok = QInputDialog.getText(self, "New Branch", t("new_branch_prompt"))
        if ok and text.strip():
            b_ok, b_msg = self.engine.create_and_switch_branch(text.strip())
            self.log(f"> {b_msg}")
            self.refresh_status()

    def _open_settings_dialog(self):
        """功能库开关与个性化定制窗口"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("settings_title"))
        dialog.setFixedSize(460, 520)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("settings_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        hint = QLabel(t("feature_toggle_hint"))
        hint.setProperty("class", "Muted")
        d_layout.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #2B2C32; background-color: #121316; border-radius: 8px; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #121316;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)

        active_ids = self.config_mgr.get_active_preset_ids()

        for pid in ALL_PRESET_IDS:
            meta = get_preset_info(pid)
            cb = QCheckBox(f"{meta['name']} ── {meta['short_desc']}")
            cb.setStyleSheet("QCheckBox { color: #E4E7EB; font-size: 12px; padding: 4px; } QCheckBox:hover { color: #FFFFFF; }")
            cb.setChecked(pid in active_ids)

            def make_handler(target_id, target_cb):
                def on_state_changed():
                    if target_cb.isChecked():
                        self.config_mgr.enable_preset(target_id)
                    else:
                        self.config_mgr.disable_preset(target_id)
                    self.refresh_status()
                return on_state_changed

            cb.stateChanged.connect(make_handler(pid, cb))
            scroll_layout.addWidget(cb)

        scroll.setWidget(scroll_widget)
        d_layout.addWidget(scroll)

        # 重置按钮
        btn_reset = QPushButton(t("settings_opt_reset"))
        btn_reset.setStyleSheet("color: #EF4444; border-color: #4D2529;")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_reset():
            reply = QMessageBox.question(dialog, "Reset", t("reset_confirm"))
            if reply == QMessageBox.StandardButton.Yes:
                self.config_mgr.reset_to_defaults()
                dialog.accept()
                self.refresh_status()
                self.log(f"> {t('reset_done')}")

        btn_reset.clicked.connect(do_reset)
        d_layout.addWidget(btn_reset)

        dialog.exec()

    def _handle_non_git_repo(self):
        """非 Git 目录初始化提示"""
        reply = QMessageBox.question(
            self,
            "FoolGit",
            "Current directory is not a Git repository. Initialize one here?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            res = run_git(["init"], cwd=self.target_dir)
            if res.success:
                QMessageBox.showinfo("Success", "Git repository initialized successfully!")
            else:
                QMessageBox.critical("Error", f"Failed to initialize: {res.stderr}")


def launch_gui(target_dir: str = "."):
    """启动 PyQt6 极简图形应用"""
    # 解决部分高分屏缩放问题
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    window = FoolGitMainWindow(target_dir=target_dir)
    window.show()
    sys.exit(app.exec())
