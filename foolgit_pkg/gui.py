"""
FoolGit 极简图形化交互界面 (GUI) - PyQt6 版本
高质感黑灰极简程序员科技风 (Dark/Gray Minimalist Aesthetic)
纯净多语言支持，彻底杜绝中英文混杂。
动态渲染全部官方预设与自定义命令，拥有全套专属暗色弹窗。
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTextEdit, QFrame, QDialog, QCheckBox, QMessageBox, QInputDialog,
    QScrollArea, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter

from .core import GitEngine, is_git_repo, run_git, scan_multi_repos
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
    font-family: Helvetica, Arial, sans-serif;
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

/* 后悔药/危险按钮 (Danger Accent) */
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
    font-family: Menlo, Monaco, Courier, monospace;
    font-size: 11.5px;
    line-height: 1.4;
    padding: 8px;
}

/* 列表控件 */
QListWidget {
    background-color: #0A0A0C;
    border: 1px solid #2B2C32;
    border-radius: 8px;
    color: #E4E7EB;
    padding: 4px;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 5px;
}
QListWidget::item:selected {
    background-color: #27282D;
    color: #FFFFFF;
}
QListWidget::item:hover {
    background-color: #1F2024;
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
        self.setWindowIcon(self._create_app_icon())
        self.resize(560, 820)
        self.setMinimumSize(500, 700)

        # 检查是否为 Git 仓库
        if not is_git_repo(self.target_dir):
            self._handle_non_git_repo()

        self._setup_ui()
        self.refresh_status()
        self._render_quick_actions()

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

        self.btn_switch_repo = QPushButton(t("gui_switch_repo_btn"))
        self.btn_switch_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_switch_repo.setStyleSheet(
            "QPushButton { padding: 3px 8px; font-size: 11px; color: #9CA3AF; border-color: #2E3038; }"
        )
        self.btn_switch_repo.clicked.connect(self._action_switch_repo)
        repo_row.addWidget(self.btn_switch_repo)

        repo_row.addStretch()

        self.branch_combo = QComboBox()
        self.branch_combo.setMinimumWidth(140)
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
        # 1.5 冲突急救横幅 (Conflict Rescue Banner - 默认隐藏)
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
        sync_layout.addWidget(self.txt_commit)

        # Conventional Commit 快捷标签 (Chips)
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

        root_layout.addWidget(sync_card)

        # ─────────────────────────────────────────────────────
        # 3. 动态快捷操作区 (Dynamic Quick Actions Grid)
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

        self.btn_refresh = QPushButton("🔄 " + ("Refresh" if get_language() == "en" else "刷新状态"))
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
    # 动态渲染快捷操作卡片
    # ─────────────────────────────────────────────────────────

    def _render_quick_actions(self):
        """动态构建与渲染所有已启用的功能卡片和自定义命令"""
        # 清除现有按钮
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
                icon, name, handler, style_id = preset_handlers[pid]
                items.append((icon, name, handler, style_id))

        for c_cmd in custom_cmds:
            cmd_text = c_cmd["cmd"]
            def make_handler(cmd):
                return lambda: self._run_custom_command(cmd)
            items.append(("⚡", c_cmd["name"], make_handler(cmd_text), None))

        for idx, (icon, name, handler, style_id) in enumerate(items):
            btn = QPushButton(f"{icon}  {name}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if style_id:
                btn.setObjectName(style_id)
            btn.clicked.connect(handler)
            row = idx // 2
            col = idx % 2
            self.grid_layout.addWidget(btn, row, col)

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
        oid_suffix = f"  ·  {info['commit_oid']}" if info.get("commit_oid") else ""
        self.lbl_repo_name.setText(f"📁 {info['name']}{oid_suffix}")

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

        # 检测合并冲突并显示/隐藏急救横幅
        conflicts = self.engine.get_conflict_files()
        if conflicts:
            self.lbl_conflict_text.setText(f"⚠️  {t('conflict_title')} ({len(conflicts)})")
            self.conflict_banner.show()
        else:
            self.conflict_banner.hide()

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

    def _create_app_icon(self) -> QIcon:
        """生成极简暗黑科技风应用图标"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#10B981"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
        painter.setPen(QColor("#121316"))
        painter.setFont(QFont("Helvetica", 30, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
        painter.end()
        return QIcon(pixmap)

    def _apply_commit_prefix(self, prefix: str):
        """将 Conventional Commit 前缀填充到提交输入框"""
        current = self.txt_commit.text().strip()
        known_prefixes = ("feat:", "fix:", "docs:", "chore:", "refactor:")
        for kp in known_prefixes:
            if current.startswith(kp):
                current = current[len(kp):].lstrip()
                break
        new_text = f"{prefix}: {current}" if current else f"{prefix}: "
        self.txt_commit.setText(new_text)
        self.txt_commit.setFocus()

    def _fill_smart_commit_msg(self):
        """一键生成并填充可读的改动摘要作为提交说明"""
        msg = self.engine.generate_smart_commit_msg()
        self.txt_commit.setText(msg)
        self.txt_commit.setFocus()

    def _action_switch_repo(self):
        """在界面内直接切换工作的 Git 仓库目录"""
        chosen_dir = QFileDialog.getExistingDirectory(
            self, t("gui_switch_repo_btn"), str(Path(self.target_dir).resolve())
        )
        if not chosen_dir:
            return
        self.target_dir = chosen_dir
        if not is_git_repo(self.target_dir):
            self._handle_non_git_repo()
        self.engine = GitEngine(self.target_dir)
        self.refresh_status()
        self.log(f"> 📁 {self.engine.repo_path}")

    def apply_language(self, lang: str):
        """应用语言并刷新所有控件文字 (100% 纯净无混杂)"""
        self.config_mgr.set_language(lang)
        self.btn_lang.setText(t("lang_toggle_btn"))
        self.btn_switch_repo.setText(t("gui_switch_repo_btn"))
        self.lbl_sync_title.setText(t("sync_banner"))
        self.lbl_sync_tip.setText(t("sync_tip"))
        self.txt_commit.setPlaceholderText(t("gui_commit_placeholder"))
        for chip_btn, i18n_key in self._commit_chips:
            chip_btn.setText(t(i18n_key))
        self.btn_auto_msg.setText(t("gui_auto_msg_chip"))
        self.btn_conflict_rescue.setText("🚑  " + t("gui_conflict_rescue"))
        self.btn_sync.setText("🚀  " + t("preset_sync_name"))
        self.lbl_act_section.setText(t("gui_quick_actions").upper())
        self.btn_refresh.setText("🔄 " + ("Refresh" if get_language() == "en" else "刷新状态"))
        self.btn_settings.setText("⚙️ " + t("settings_btn"))
        self._render_quick_actions()
        self.refresh_status()

    def _toggle_language(self):
        """中英文即时无感热切换"""
        new_lang = "zh" if get_language() == "en" else "en"
        self.apply_language(new_lang)
        self.log(f"> {t('lang_changed')}")

    # ─────────────────────────────────────────────────────────
    # 业务动作与专属暗黑弹窗
    # ─────────────────────────────────────────────────────────

    def _action_sync(self):
        """触发一键保存并同步（含同步前安全体检）"""
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
            reply = QMessageBox.warning(
                self,
                t("gui_risk_confirm_title"),
                "\n".join(lines),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.log(f"> {t('cancelled')}")
                return

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
        """极简后悔药弹窗（支持全部撤销、撤销提交、按文件丢弃）"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("undo_title").replace(":", ""))
        dialog.setFixedSize(450, 440)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("undo_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #EF4444;")
        d_layout.addWidget(title)

        btn_all = QPushButton("⚠️  " + t("undo_opt_all"))
        btn_all.setObjectName("UndoButton")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_all)

        btn_uncommit = QPushButton("↩️  " + t("undo_opt_commit"))
        btn_uncommit.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_uncommit)

        btn_amend = QPushButton("✏️  " + t("undo_opt_amend"))
        btn_amend.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_amend)

        # 按文件丢弃
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #2B2C32;")
        d_layout.addWidget(sep)

        lbl_file = QLabel(t("gui_select_file_hint"))
        lbl_file.setProperty("class", "Muted")
        d_layout.addWidget(lbl_file)

        discard_list = QListWidget()
        discardable = self.engine.get_discardable_files()
        if not discardable:
            item = QListWidgetItem(t("discard_file_no_changes"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            discard_list.addItem(item)
        else:
            for f in discardable:
                item = QListWidgetItem(f"[{f['status']}]  {f['path']}")
                item.setData(Qt.ItemDataRole.UserRole, f["path"])
                if f["status"] == "M":
                    item.setForeground(QColor("#FBBF24"))
                elif f["status"] == "A":
                    item.setForeground(QColor("#34D399"))
                else:
                    item.setForeground(QColor("#38BDF8"))
                discard_list.addItem(item)

        d_layout.addWidget(discard_list, stretch=1)

        btn_discard_file = QPushButton("🗑️  " + t("gui_discard_selected_btn"))
        btn_discard_file.setObjectName("UndoButton")
        btn_discard_file.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_discard_file.setEnabled(len(discardable) > 0)
        d_layout.addWidget(btn_discard_file)

        def do_all():
            reply = QMessageBox.question(
                dialog, "Confirm", t("discard_all_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                dialog.accept()
                ok, msg = self.engine.undo_action("discard_all")
                self.log(f"> {msg}")
                self.refresh_status()

        def do_uncommit():
            dialog.accept()
            ok, msg = self.engine.undo_action("uncommit")
            self.log(f"> {msg}")
            self.refresh_status()

        def do_discard_file():
            curr = discard_list.currentItem()
            if not curr:
                return
            target_path = curr.data(Qt.ItemDataRole.UserRole)
            if not target_path:
                return
            reply = QMessageBox.question(
                dialog, "Confirm", t("discard_file_confirm", target=target_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                dialog.accept()
                ok, msg = self.engine.undo_action("discard_file", target=target_path)
                self.log(f"> {msg}")
                self.refresh_status()

        def do_amend():
            new_msg, ok_input = QInputDialog.getText(
                dialog, t("gui_amend_commit"), t("gui_amend_prompt")
            )
            if ok_input and new_msg.strip():
                dialog.accept()
                ok, msg = self.engine.amend_commit_message(new_msg.strip())
                self.log(f"> {msg}")
                self.refresh_status()

        btn_all.clicked.connect(do_all)
        btn_uncommit.clicked.connect(do_uncommit)
        btn_amend.clicked.connect(do_amend)
        btn_discard_file.clicked.connect(do_discard_file)
        dialog.exec()

    def _action_stash_dialog(self):
        """暂存箱弹窗（含存盘、恢复与条目列表管理）"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("stash_title").replace(":", ""))
        dialog.setFixedSize(460, 440)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel(t("stash_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        top_btns = QHBoxLayout()
        btn_save = QPushButton("📦  " + t("stash_opt_save").split("(")[0].strip())
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        top_btns.addWidget(btn_save)

        btn_pop = QPushButton("📂  " + t("stash_opt_pop").split("(")[0].strip())
        btn_pop.setCursor(Qt.CursorShape.PointingHandCursor)
        top_btns.addWidget(btn_pop)
        d_layout.addLayout(top_btns)

        lbl_list = QLabel(t("gui_stash_list_label"))
        lbl_list.setProperty("class", "Muted")
        d_layout.addWidget(lbl_list)

        stash_list = QListWidget()
        d_layout.addWidget(stash_list, stretch=1)

        entry_btns = QHBoxLayout()
        btn_apply = QPushButton("📂  " + t("gui_stash_apply_btn"))
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        entry_btns.addWidget(btn_apply)

        btn_drop = QPushButton("🗑️  " + t("gui_stash_drop_btn"))
        btn_drop.setObjectName("UndoButton")
        btn_drop.setCursor(Qt.CursorShape.PointingHandCursor)
        entry_btns.addWidget(btn_drop)
        d_layout.addLayout(entry_btns)

        def refresh_stashes():
            stash_list.clear()
            entries = self.engine.list_stashes()
            if not entries:
                item = QListWidgetItem(t("stash_list_empty"))
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                stash_list.addItem(item)
                btn_apply.setEnabled(False)
                btn_drop.setEnabled(False)
            else:
                for idx, entry in enumerate(entries):
                    item = QListWidgetItem(f"[{entry['ref']}]  {entry['desc']}")
                    item.setData(Qt.ItemDataRole.UserRole, idx)
                    stash_list.addItem(item)
                stash_list.setCurrentRow(0)
                btn_apply.setEnabled(True)
                btn_drop.setEnabled(True)

        def do_save():
            note, ok_in = QInputDialog.getText(dialog, "Stash", t("stash_note_prompt"))
            if not ok_in:
                return
            ok, msg = self.engine.stash_save(note.strip())
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_stashes()

        def do_pop():
            ok, msg = self.engine.stash_pop()
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_stashes()

        def do_apply():
            curr = stash_list.currentItem()
            if not curr:
                return
            idx = curr.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                return
            ok, msg = self.engine.stash_apply(int(idx))
            self.log(f"> {msg}")
            self.refresh_status()

        def do_drop():
            curr = stash_list.currentItem()
            if not curr:
                return
            idx = curr.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                return
            ok, msg = self.engine.stash_drop(int(idx))
            self.log(f"> {msg}")
            refresh_stashes()

        btn_save.clicked.connect(do_save)
        btn_pop.clicked.connect(do_pop)
        btn_apply.clicked.connect(do_apply)
        btn_drop.clicked.connect(do_drop)
        refresh_stashes()
        dialog.exec()

    def _action_branch_dialog(self):
        """分支管理弹窗（查看、切换、新建、删除分支）"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_branch_manager"))
        dialog.setFixedSize(440, 440)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("🌿  " + t("gui_branch_manager"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        lbl = QLabel(t("gui_branch_list_label"))
        lbl.setProperty("class", "Muted")
        d_layout.addWidget(lbl)

        branch_list = QListWidget()
        d_layout.addWidget(branch_list, stretch=1)

        def refresh_branches():
            branch_list.clear()
            for b in self.engine.list_branches():
                suffix = f"  {t('current_branch_mark')}" if b["is_current"] else ""
                item = QListWidgetItem(f"{b['name']}{suffix}")
                item.setData(Qt.ItemDataRole.UserRole, b["name"])
                if b["is_current"]:
                    item.setForeground(QColor("#10B981"))
                branch_list.addItem(item)

        btn_row = QHBoxLayout()
        btn_switch = QPushButton("🔀  " + t("gui_branch_switch_btn"))
        btn_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_switch)

        btn_delete = QPushButton("🗑️  " + t("gui_branch_delete_btn"))
        btn_delete.setObjectName("UndoButton")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_delete)
        d_layout.addLayout(btn_row)

        create_row = QHBoxLayout()
        txt_new_branch = QLineEdit()
        txt_new_branch.setPlaceholderText(t("gui_new_branch_placeholder"))
        create_row.addWidget(txt_new_branch, stretch=1)

        btn_create = QPushButton("➕  " + t("gui_branch_create_btn"))
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        create_row.addWidget(btn_create)
        d_layout.addLayout(create_row)

        def do_switch():
            curr = branch_list.currentItem()
            if not curr:
                return
            b_name = curr.data(Qt.ItemDataRole.UserRole)
            ok, msg = self.engine.switch_branch(b_name)
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_branches()

        def do_delete():
            curr = branch_list.currentItem()
            if not curr:
                return
            b_name = curr.data(Qt.ItemDataRole.UserRole)
            reply = QMessageBox.question(
                dialog, "Confirm", t("branch_delete_confirm", branch=b_name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            ok, msg = self.engine.delete_branch(b_name, force=(reply == QMessageBox.StandardButton.Yes))
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_branches()

        def do_create():
            new_name = txt_new_branch.text().strip()
            if not new_name:
                return
            ok, msg = self.engine.create_and_switch_branch(new_name)
            self.log(f"> {msg}")
            if ok:
                txt_new_branch.clear()
            self.refresh_status()
            refresh_branches()

        btn_switch.clicked.connect(do_switch)
        btn_delete.clicked.connect(do_delete)
        btn_create.clicked.connect(do_create)
        refresh_branches()
        dialog.exec()

    def _action_gitignore_dialog(self):
        """.gitignore 快速编辑弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_gitignore_editor"))
        dialog.setFixedSize(460, 440)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("🚫  " + t("gui_gitignore_editor"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        lbl = QLabel(t("gui_gitignore_content_label"))
        lbl.setProperty("class", "Muted")
        d_layout.addWidget(lbl)

        txt_content = QTextEdit()
        txt_content.setReadOnly(True)
        txt_content.setObjectName("LogConsole")
        d_layout.addWidget(txt_content, stretch=1)

        def refresh_content():
            content = self.engine.get_gitignore_content()
            txt_content.setPlainText(content if content else t("gitignore_empty_file"))

        add_row = QHBoxLayout()
        txt_pattern = QLineEdit()
        txt_pattern.setPlaceholderText(t("gui_gitignore_pattern_placeholder"))
        add_row.addWidget(txt_pattern, stretch=1)

        btn_add = QPushButton("➕  " + t("gui_gitignore_add_btn"))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        add_row.addWidget(btn_add)
        d_layout.addLayout(add_row)

        def do_add():
            pattern = txt_pattern.text().strip()
            if not pattern:
                return
            ok, msg = self.engine.append_to_gitignore(pattern)
            self.log(f"> {msg}")
            if ok:
                txt_pattern.clear()
            refresh_content()
            self.refresh_status()

        btn_add.clicked.connect(do_add)
        refresh_content()
        dialog.exec()

    def _action_conflict_dialog(self):
        """合并冲突急救弹窗（保留本地 / 使用远程 / 中止合并）"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_conflict_rescue"))
        dialog.setFixedSize(480, 420)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("🚑  " + t("gui_conflict_rescue"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #EF4444;")
        d_layout.addWidget(title)

        lbl = QLabel(t("conflict_files_label"))
        lbl.setProperty("class", "Muted")
        d_layout.addWidget(lbl)

        conflict_list = QListWidget()
        d_layout.addWidget(conflict_list, stretch=1)

        resolve_row = QHBoxLayout()
        btn_ours = QPushButton("🛡️  " + t("gui_conflict_keep_mine"))
        btn_ours.setCursor(Qt.CursorShape.PointingHandCursor)
        resolve_row.addWidget(btn_ours)

        btn_theirs = QPushButton("☁️  " + t("gui_conflict_use_remote"))
        btn_theirs.setCursor(Qt.CursorShape.PointingHandCursor)
        resolve_row.addWidget(btn_theirs)
        d_layout.addLayout(resolve_row)

        btn_abort = QPushButton("↩️  " + t("conflict_opt_abort").replace("[a] ", ""))
        btn_abort.setObjectName("UndoButton")
        btn_abort.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_abort)

        def refresh_conflicts():
            conflict_list.clear()
            files = self.engine.get_conflict_files()
            for f in files:
                item = QListWidgetItem(f"⚠️  {f}")
                item.setData(Qt.ItemDataRole.UserRole, f)
                item.setForeground(QColor("#FCA5A5"))
                conflict_list.addItem(item)
            if files:
                conflict_list.setCurrentRow(0)
            btn_ours.setEnabled(bool(files))
            btn_theirs.setEnabled(bool(files))
            if not files:
                dialog.accept()

        def do_resolve(strategy: str):
            curr = conflict_list.currentItem()
            if not curr:
                return
            fpath = curr.data(Qt.ItemDataRole.UserRole)
            if not fpath:
                return
            ok, msg = self.engine.resolve_conflict(fpath, strategy)
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_conflicts()

        def do_abort():
            dialog.accept()
            ok, msg = self.engine.abort_merge()
            self.log(f"> {msg}")
            self.refresh_status()

        btn_ours.clicked.connect(lambda: do_resolve("ours"))
        btn_theirs.clicked.connect(lambda: do_resolve("theirs"))
        btn_abort.clicked.connect(do_abort)
        refresh_conflicts()
        dialog.exec()

    def _action_clean_dialog(self):
        """清理未跟踪垃圾文件弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_clean_manager"))
        dialog.setFixedSize(480, 420)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("clean_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        preview = self.engine.clean_preview()
        if not preview:
            lbl_clean = QLabel("✨  " + t("clean_nothing"))
            lbl_clean.setStyleSheet("color: #10B981; font-size: 13px; font-weight: 600; padding: 30px 0;")
            d_layout.addWidget(lbl_clean, alignment=Qt.AlignmentFlag.AlignCenter)
            btn_close = QPushButton("OK")
            btn_close.clicked.connect(dialog.accept)
            d_layout.addWidget(btn_close)
        else:
            lbl_hint = QLabel(t("clean_preview_title"))
            lbl_hint.setProperty("class", "Muted")
            d_layout.addWidget(lbl_hint)

            clean_list = QListWidget()
            for p in preview:
                clean_list.addItem(f"🗑️  {p}")
            d_layout.addWidget(clean_list, stretch=1)

            btn_clean = QPushButton("🔥  " + t("gui_clean_now_btn"))
            btn_clean.setObjectName("UndoButton")
            btn_clean.setCursor(Qt.CursorShape.PointingHandCursor)

            def do_clean():
                dialog.accept()
                ok, msg = self.engine.clean_execute()
                self.log(f"> {msg}")
                self.refresh_status()

            btn_clean.clicked.connect(do_clean)
            d_layout.addWidget(btn_clean)

        dialog.exec()

    def _action_tag_dialog(self):
        """版本标签管理弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_tag_manager"))
        dialog.setFixedSize(500, 520)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("tag_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        # 新建标签输入行
        create_box = QFrame()
        create_box.setProperty("class", "CardFrame")
        c_layout = QVBoxLayout(create_box)
        c_layout.setContentsMargins(12, 10, 12, 10)
        c_layout.setSpacing(8)

        txt_tag = QLineEdit()
        txt_tag.setPlaceholderText(t("tag_name_prompt"))
        c_layout.addWidget(txt_tag)

        txt_msg = QLineEdit()
        txt_msg.setPlaceholderText(t("tag_msg_prompt"))
        c_layout.addWidget(txt_msg)

        cb_push = QCheckBox(t("tag_push_prompt").split("?")[0] + "?")
        cb_push.setChecked(True)
        c_layout.addWidget(cb_push)

        btn_create = QPushButton("🏷️  " + t("gui_new_tag_btn"))
        btn_create.setStyleSheet("background-color: #10B981; color: #FFFFFF;")
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        c_layout.addWidget(btn_create)

        d_layout.addWidget(create_box)

        # 标签列表
        lbl_list = QLabel(t("tag_opt_list"))
        lbl_list.setProperty("class", "SectionTitle")
        d_layout.addWidget(lbl_list)

        tag_list = QListWidget()
        def reload_tags():
            tag_list.clear()
            tags = self.engine.list_tags()
            if not tags:
                tag_list.addItem(t("tag_none_found"))
            else:
                for tg in tags:
                    tag_list.addItem(f"🏷️  {tg}")

        reload_tags()
        d_layout.addWidget(tag_list, stretch=1)

        # 底部操作行
        bot_row = QHBoxLayout()
        btn_del = QPushButton("❌  " + t("gui_delete_tag_btn"))
        btn_del.setObjectName("UndoButton")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        bot_row.addWidget(btn_del)

        btn_push_all = QPushButton("🚀  " + t("gui_push_tags_btn"))
        btn_push_all.setCursor(Qt.CursorShape.PointingHandCursor)
        bot_row.addWidget(btn_push_all)

        d_layout.addLayout(bot_row)

        def do_create():
            name = txt_tag.text().strip()
            if not name:
                return
            msg = txt_msg.text().strip()
            ok, res_msg = self.engine.create_tag(name, msg, push=cb_push.isChecked())
            self.log(f"> {res_msg}")
            txt_tag.clear()
            txt_msg.clear()
            reload_tags()

        def do_delete():
            curr = tag_list.currentItem()
            if not curr:
                return
            tname = curr.text().replace("🏷️", "").strip()
            if not tname or tname == t("tag_none_found"):
                return
            remote_yn = QMessageBox.question(
                dialog, "Delete Remote", t("tag_delete_remote_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            ok, res_msg = self.engine.delete_tag(tname, remote=(remote_yn == QMessageBox.StandardButton.Yes))
            self.log(f"> {res_msg}")
            reload_tags()

        def do_push_all():
            ok, res_msg = self.engine.push_all_tags()
            self.log(f"> {res_msg}")

        btn_create.clicked.connect(do_create)
        btn_del.clicked.connect(do_delete)
        btn_push_all.clicked.connect(do_push_all)

        dialog.exec()

    def _action_remote_dialog(self):
        """远程仓库设置弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_remote_manager"))
        dialog.setFixedSize(520, 440)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("remote_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        curr_url = self.engine.get_remote_url()
        lbl_curr = QLabel(t("remote_origin_label", url=curr_url if curr_url else t("remote_none")))
        lbl_curr.setProperty("class", "Muted")
        lbl_curr.setWordWrap(True)
        d_layout.addWidget(lbl_curr)

        # 编辑 URL
        box = QFrame()
        box.setProperty("class", "CardFrame")
        b_layout = QVBoxLayout(box)
        b_layout.setContentsMargins(12, 10, 12, 10)
        b_layout.setSpacing(8)

        lbl_edit = QLabel(t("remote_set_prompt"))
        lbl_edit.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        b_layout.addWidget(lbl_edit)

        txt_url = QLineEdit()
        txt_url.setText(curr_url)
        txt_url.setPlaceholderText("https://github.com/user/repo.git")
        b_layout.addWidget(txt_url)

        btn_save = QPushButton("💾  " + t("gui_set_origin_btn"))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        b_layout.addWidget(btn_save)

        d_layout.addWidget(box)

        # 连通性测试卡片
        test_box = QFrame()
        test_box.setProperty("class", "CardFrame")
        t_layout = QHBoxLayout(test_box)
        t_layout.setContentsMargins(12, 10, 12, 10)

        btn_test = QPushButton("⚡  " + t("gui_test_conn_btn"))
        btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
        t_layout.addWidget(btn_test)

        lbl_test_result = QLabel("")
        lbl_test_result.setWordWrap(True)
        t_layout.addWidget(lbl_test_result, stretch=1)

        d_layout.addWidget(test_box)

        # 所有 remotes 文本框
        lbl_all = QLabel(t("remote_opt_view"))
        lbl_all.setProperty("class", "SectionTitle")
        d_layout.addWidget(lbl_all)

        txt_all = QTextEdit()
        txt_all.setObjectName("LogConsole")
        txt_all.setReadOnly(True)
        txt_all.setFixedHeight(80)
        remotes = self.engine.list_remotes()
        if remotes:
            for r in remotes:
                txt_all.append(f"{r['name']}\t{r['url']} ({r['type']})")
        else:
            txt_all.append(t("remote_none"))
        d_layout.addWidget(txt_all)

        def do_save():
            new_u = txt_url.text().strip()
            if not new_u:
                return
            ok, msg = self.engine.set_remote_origin(new_u)
            self.log(f"> {msg}")
            lbl_curr.setText(t("remote_origin_label", url=new_u))
            self.refresh_status()

        def do_test():
            lbl_test_result.setStyleSheet("color: #FBBF24;")
            lbl_test_result.setText("Testing connection...")
            ok, msg = self.engine.test_remote_connection()
            if ok:
                lbl_test_result.setStyleSheet("color: #34D399; font-weight: bold;")
                lbl_test_result.setText("✓ Connected successfully!")
            else:
                lbl_test_result.setStyleSheet("color: #EF4444;")
                lbl_test_result.setText("✗ " + msg)
            self.log(f"> {msg}")

        btn_save.clicked.connect(do_save)
        btn_test.clicked.connect(do_test)

        dialog.exec()

    def _action_diff_dialog(self):
        """代码差异对比弹窗 (高亮绿/红 diff)"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_diff_viewer"))
        dialog.resize(720, 540)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(18, 16, 18, 16)
        d_layout.setSpacing(10)

        top_row = QHBoxLayout()
        lbl_t = QLabel(t("diff_menu_title"))
        lbl_t.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        top_row.addWidget(lbl_t)

        top_row.addStretch()

        combo_mode = QComboBox()
        combo_mode.addItem(t("gui_diff_mode_unstaged"), False)
        combo_mode.addItem(t("gui_diff_mode_staged"), True)
        top_row.addWidget(combo_mode)

        combo_files = QComboBox()
        combo_files.addItem(t("gui_diff_select_file"), "")
        info = self.engine.get_info()
        for f in list(dict.fromkeys(info["modified"] + info["staged"])):
            combo_files.addItem(f, f)
        top_row.addWidget(combo_files)

        d_layout.addLayout(top_row)

        txt_diff = QTextEdit()
        txt_diff.setObjectName("LogConsole")
        txt_diff.setReadOnly(True)
        txt_diff.setFont(QFont("Menlo", 12))
        d_layout.addWidget(txt_diff, stretch=1)

        def update_diff():
            staged = combo_mode.currentData()
            fpath = combo_files.currentData()
            raw = self.engine.get_diff(staged=staged, file_path=fpath if fpath else None, color=False)
            txt_diff.clear()
            if not raw:
                txt_diff.append(f"<span style='color: #10B981;'>{t('no_diff')}</span>")
                return

            for line in raw.splitlines():
                safe_l = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if safe_l.startswith("+++") or safe_l.startswith("---"):
                    txt_diff.append(f"<span style='color: #9CA3AF; font-weight: bold;'>{safe_l}</span>")
                elif safe_l.startswith("+"):
                    txt_diff.append(f"<span style='color: #34D399;'>{safe_l}</span>")
                elif safe_l.startswith("-"):
                    txt_diff.append(f"<span style='color: #F87171;'>{safe_l}</span>")
                elif safe_l.startswith("@@"):
                    txt_diff.append(f"<span style='color: #38BDF8;'>{safe_l}</span>")
                else:
                    txt_diff.append(f"<span style='color: #D1D5DB;'>{safe_l}</span>")

        combo_mode.currentIndexChanged.connect(update_diff)
        combo_files.currentIndexChanged.connect(update_diff)
        update_diff()

        dialog.exec()

    def _action_history_dialog(self):
        """提交历史及详情流水线弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_history_viewer"))
        dialog.resize(740, 560)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(18, 16, 18, 16)
        d_layout.setSpacing(10)

        title = QLabel(t("history_menu_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        hist = self.engine.get_recent_history(25)

        list_commits = QListWidget()
        list_commits.setFixedHeight(180)

        commit_map = {}
        for item in hist:
            parts = item.split("|")
            if len(parts) >= 4:
                h, author, when, msg = parts[0], parts[1], parts[2], parts[3]
                display_text = f"{h}  ─  {msg}  ({when} by {author})"
                commit_map[display_text] = h
                list_commits.addItem(display_text)
            else:
                list_commits.addItem(item)

        d_layout.addWidget(list_commits)

        lbl_det = QLabel(t("gui_history_viewer"))
        lbl_det.setProperty("class", "SectionTitle")
        d_layout.addWidget(lbl_det)

        txt_detail = QTextEdit()
        txt_detail.setObjectName("LogConsole")
        txt_detail.setReadOnly(True)
        txt_detail.setFont(QFont("Menlo", 11))
        d_layout.addWidget(txt_detail, stretch=1)

        def on_commit_selected():
            curr = list_commits.currentItem()
            if not curr:
                return
            h = commit_map.get(curr.text())
            if not h:
                return
            detail = self.engine.get_commit_detail(h)
            txt_detail.clear()
            for line in detail.splitlines():
                safe_l = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if safe_l.startswith("+"):
                    txt_detail.append(f"<span style='color: #34D399;'>{safe_l}</span>")
                elif safe_l.startswith("-"):
                    txt_detail.append(f"<span style='color: #F87171;'>{safe_l}</span>")
                elif safe_l.startswith("commit "):
                    txt_detail.append(f"<span style='color: #FBBF24; font-weight: bold;'>{safe_l}</span>")
                else:
                    txt_detail.append(f"<span style='color: #D1D5DB;'>{safe_l}</span>")

        list_commits.itemSelectionChanged.connect(on_commit_selected)
        if list_commits.count() > 0:
            list_commits.setCurrentRow(0)

        dialog.exec()

    def _action_multi_sync_dialog(self):
        """多仓库扫描与批量同步弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("gui_multi_sync"))
        dialog.resize(620, 500)
        dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")

        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        repos = scan_multi_repos(self.target_dir)

        title = QLabel(t("multi_repo_title", count=len(repos)))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        list_repos = QListWidget()
        for r in repos:
            clean_str = "✨ Clean" if r["is_clean"] else f"✎ {r['total_changes']} changed"
            sync_str = f"↑{r['ahead']} ↓{r['behind']}" if r["has_upstream"] else "Local only"
            list_repos.addItem(f"📁 {r['name']} [{r['branch']}]  ──  {clean_str}  ({sync_str})\n   {r['path']}")

        d_layout.addWidget(list_repos, stretch=1)

        btn_sync_all = QPushButton("🚀  " + t("multi_opt_all"))
        btn_sync_all.setObjectName("SyncButton")
        btn_sync_all.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_sync_all)

        def do_sync_all():
            btn_sync_all.setEnabled(False)
            self.log(f"\n> ─── {t('multi_syncing', count=len(repos))} ───")
            succ = 0
            fail = 0
            for r in repos:
                self.log(f"> Syncing: {r['name']} ({r['branch']})...")
                sub_engine = GitEngine(r["path"])
                ok, logs = sub_engine.one_click_sync()
                if ok:
                    succ += 1
                    self.log(f"  ✓ {r['name']} synced.")
                else:
                    fail += 1
                    self.log(f"  ✗ {r['name']} sync error.")
            self.log(f"> {t('multi_sync_summary', succ=succ, fail=fail)}")
            self.refresh_status()
            dialog.accept()

        btn_sync_all.clicked.connect(do_sync_all)
        dialog.exec()

    def _run_custom_command(self, raw_cmd: str):
        """执行自定义 Git 命令并实时回显日志"""
        self.log(f"\n> ─── 🚀 Running: {raw_cmd} ───")
        args = raw_cmd.replace("git ", "").split()
        def job():
            res = run_git(args, cwd=self.engine.repo_path)
            lines = []
            if res.stdout:
                lines.append(res.stdout)
            if res.stderr:
                lines.append(res.stderr)
            lines.append("✓ Done" if res.success else "✗ Failed")
            return res.success, lines
        self._run_in_background(job)

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
        dialog.setFixedSize(480, 560)
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
                    self._render_quick_actions()
                    self.refresh_status()
                return on_state_changed

            cb.stateChanged.connect(make_handler(pid, cb))
            scroll_layout.addWidget(cb)

        scroll.setWidget(scroll_widget)
        d_layout.addWidget(scroll)

        # 添加自定义命令按钮
        btn_add_cmd = QPushButton("➕ " + t("settings_opt_add_custom"))
        btn_add_cmd.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_add_cmd():
            name_text, ok1 = QInputDialog.getText(dialog, "Custom Command", t("custom_name_prompt"))
            if not ok1 or not name_text.strip():
                return
            cmd_text, ok2 = QInputDialog.getText(dialog, "Custom Command", t("custom_cmd_prompt"))
            if not ok2 or not cmd_text.strip():
                return
            desc_text, _ = QInputDialog.getText(dialog, "Custom Command", t("custom_desc_prompt"))
            self.config_mgr.add_custom_command(name_text.strip(), cmd_text.strip(), desc_text.strip() if desc_text else "")
            self._render_quick_actions()
            self.log(f"> {t('custom_added', name=name_text)}")

        btn_add_cmd.clicked.connect(do_add_cmd)
        d_layout.addWidget(btn_add_cmd)

        # 删除自定义命令按钮
        btn_rm_cmd = QPushButton("🗑️ " + t("settings_opt_remove_custom"))
        btn_rm_cmd.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_rm_cmd():
            cmds = self.config_mgr.get_custom_commands()
            if not cmds:
                QMessageBox.information(dialog, t("settings_title"), t("remove_custom_empty"))
                return
            labels = [f"{c['name']} ({c['cmd']})" for c in cmds]
            chosen_label, ok_sel = QInputDialog.getItem(
                dialog, t("settings_opt_remove_custom"), t("remove_custom_title"), labels, 0, False
            )
            if ok_sel and chosen_label:
                idx = labels.index(chosen_label)
                target_cmd = cmds[idx]
                self.config_mgr.remove_custom_command(target_cmd["id"])
                self._render_quick_actions()
                self.log(f"> {t('custom_removed', name=target_cmd['name'])}")

        btn_rm_cmd.clicked.connect(do_rm_cmd)
        d_layout.addWidget(btn_rm_cmd)

        # 重置按钮
        btn_reset = QPushButton(t("settings_opt_reset"))
        btn_reset.setStyleSheet("color: #EF4444; border-color: #4D2529;")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_reset():
            reply = QMessageBox.question(dialog, "Reset", t("reset_confirm"))
            if reply == QMessageBox.StandardButton.Yes:
                self.config_mgr.reset_to_defaults()
                dialog.accept()
                self._render_quick_actions()
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
                QMessageBox.information(self, "Success", "Git repository initialized successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to initialize: {res.stderr}")


def launch_gui(target_dir: str = "."):
    """启动 PyQt6 极简图形应用"""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 12))
    app.setStyleSheet(DARK_QSS)

    window = FoolGitMainWindow(target_dir=target_dir)
    window.show()
    sys.exit(app.exec())
