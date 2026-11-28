"""
FoolGit 专属暗黑弹窗集合 (DialogsMixin)
与 CLI 具象隐喻完全一致：后悔药、临时储物柜（含偷看）、平行宇宙、时光机（含对比/分支/安全回退）等。
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QInputDialog, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QScrollArea,
    QTextEdit, QLineEdit, QVBoxLayout, QWidget
)

from ..core import GitEngine, scan_multi_repos
from ..i18n import t
from ..presets import ALL_PRESET_IDS, get_preset_info
from .theme import create_dark_dialog, render_diff_html


class DialogsMixin:
    """FoolGit 主窗口所有业务弹窗 Mixin"""

    def _action_undo_dialog(self):
        """后悔药弹窗（擦掉修改、拆掉快照、按文件擦除、快照改名）"""
        dialog = create_dark_dialog(self, t("undo_title").replace(":", ""), 460, 460)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("💊  " + t("undo_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #EF4444;")
        d_layout.addWidget(title)

        btn_all = QPushButton(t("undo_opt_all"))
        btn_all.setObjectName("UndoButton")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_all)

        btn_uncommit = QPushButton(t("undo_opt_commit"))
        btn_uncommit.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_uncommit)

        btn_amend = QPushButton(t("undo_opt_amend"))
        btn_amend.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_amend)

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
                dialog, "FoolGit", t("discard_all_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                dialog.accept()
                _, msg = self.engine.undo_action("discard_all")
                self.log(f"> {msg}")
                self.refresh_status()

        def do_uncommit():
            dialog.accept()
            _, msg = self.engine.undo_action("uncommit")
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
                dialog, "FoolGit", t("discard_file_confirm", target=target_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                dialog.accept()
                _, msg = self.engine.undo_action("discard_file", target=target_path)
                self.log(f"> {msg}")
                self.refresh_status()

        def do_amend():
            new_msg, ok_input = QInputDialog.getText(
                dialog, t("gui_amend_commit"), t("gui_amend_prompt")
            )
            if ok_input and new_msg.strip():
                dialog.accept()
                _, msg = self.engine.amend_commit_message(new_msg.strip())
                self.log(f"> {msg}")
                self.refresh_status()

        btn_all.clicked.connect(do_all)
        btn_uncommit.clicked.connect(do_uncommit)
        btn_amend.clicked.connect(do_amend)
        btn_discard_file.clicked.connect(do_discard_file)
        dialog.exec()

    def _action_stash_dialog(self):
        """临时储物柜弹窗（锁存、取出、列表、偷看内容、恢复与删除）"""
        dialog = create_dark_dialog(self, t("stash_title").replace(":", ""), 520, 520, fixed=False)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("📦  " + t("stash_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        top_btns = QHBoxLayout()
        btn_save = QPushButton(t("stash_opt_save").split("（")[0].split("(")[0].strip())
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        top_btns.addWidget(btn_save)

        btn_pop = QPushButton(t("stash_opt_pop").split("（")[0].split("(")[0].strip())
        btn_pop.setCursor(Qt.CursorShape.PointingHandCursor)
        top_btns.addWidget(btn_pop)
        d_layout.addLayout(top_btns)

        lbl_list = QLabel(t("gui_stash_list_label"))
        lbl_list.setProperty("class", "Muted")
        d_layout.addWidget(lbl_list)

        stash_list = QListWidget()
        stash_list.setFixedHeight(140)
        d_layout.addWidget(stash_list)

        txt_peek = QTextEdit()
        txt_peek.setObjectName("LogConsole")
        txt_peek.setReadOnly(True)
        txt_peek.setFont(QFont("Menlo", 11))
        d_layout.addWidget(txt_peek, stretch=1)

        entry_btns = QHBoxLayout()
        btn_apply = QPushButton("📂  " + t("gui_stash_apply_btn"))
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        entry_btns.addWidget(btn_apply)

        btn_drop = QPushButton("🗑️  " + t("gui_stash_drop_btn"))
        btn_drop.setObjectName("UndoButton")
        btn_drop.setCursor(Qt.CursorShape.PointingHandCursor)
        entry_btns.addWidget(btn_drop)
        d_layout.addLayout(entry_btns)

        def on_stash_selected():
            curr = stash_list.currentItem()
            if not curr:
                txt_peek.clear()
                return
            idx = curr.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                txt_peek.clear()
                return
            raw_diff = self.engine.get_stash_diff(int(idx), color=False)
            render_diff_html(txt_peek, raw_diff, t("no_diff"))

        def refresh_stashes():
            stash_list.clear()
            txt_peek.clear()
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
                on_stash_selected()

        def do_save():
            note, ok_in = QInputDialog.getText(dialog, "FoolGit", t("stash_note_prompt"))
            if not ok_in:
                return
            _, msg = self.engine.stash_save(note.strip())
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_stashes()

        def do_pop():
            _, msg = self.engine.stash_pop()
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_stashes()

        def do_apply():
            curr = stash_list.currentItem()
            if not curr or curr.data(Qt.ItemDataRole.UserRole) is None:
                return
            _, msg = self.engine.stash_apply(int(curr.data(Qt.ItemDataRole.UserRole)))
            self.log(f"> {msg}")
            self.refresh_status()

        def do_drop():
            curr = stash_list.currentItem()
            if not curr or curr.data(Qt.ItemDataRole.UserRole) is None:
                return
            _, msg = self.engine.stash_drop(int(curr.data(Qt.ItemDataRole.UserRole)))
            self.log(f"> {msg}")
            refresh_stashes()

        stash_list.itemSelectionChanged.connect(on_stash_selected)
        btn_save.clicked.connect(do_save)
        btn_pop.clicked.connect(do_pop)
        btn_apply.clicked.connect(do_apply)
        btn_drop.clicked.connect(do_drop)
        refresh_stashes()
        dialog.exec()

    def _action_branch_dialog(self):
        """平行宇宙（分支管理）弹窗"""
        dialog = create_dark_dialog(self, t("gui_branch_manager"), 450, 440)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(10)

        title = QLabel("🌿  " + t("branch_title").replace(":", ""))
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
            _, msg = self.engine.switch_branch(curr.data(Qt.ItemDataRole.UserRole))
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_branches()

        def do_delete():
            curr = branch_list.currentItem()
            if not curr:
                return
            b_name = curr.data(Qt.ItemDataRole.UserRole)
            reply = QMessageBox.question(
                dialog, "FoolGit", t("branch_delete_confirm", branch=b_name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            _, msg = self.engine.delete_branch(b_name, force=(reply == QMessageBox.StandardButton.Yes))
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
        dialog = create_dark_dialog(self, t("gui_gitignore_editor"), 460, 440)
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
        dialog = create_dark_dialog(self, t("gui_conflict_rescue"), 480, 420)
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
            if not curr or not curr.data(Qt.ItemDataRole.UserRole):
                return
            _, msg = self.engine.resolve_conflict(curr.data(Qt.ItemDataRole.UserRole), strategy)
            self.log(f"> {msg}")
            self.refresh_status()
            refresh_conflicts()

        def do_abort():
            dialog.accept()
            _, msg = self.engine.abort_merge()
            self.log(f"> {msg}")
            self.refresh_status()

        btn_ours.clicked.connect(lambda: do_resolve("ours"))
        btn_theirs.clicked.connect(lambda: do_resolve("theirs"))
        btn_abort.clicked.connect(do_abort)
        refresh_conflicts()
        dialog.exec()

    def _action_clean_dialog(self):
        """清理未跟踪垃圾文件弹窗"""
        dialog = create_dark_dialog(self, t("gui_clean_manager"), 480, 420)
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
                _, msg = self.engine.clean_execute()
                self.log(f"> {msg}")
                self.refresh_status()

            btn_clean.clicked.connect(do_clean)
            d_layout.addWidget(btn_clean)

        dialog.exec()

    def _action_tag_dialog(self):
        """版本标签管理弹窗"""
        dialog = create_dark_dialog(self, t("gui_tag_manager"), 500, 520)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        title = QLabel(t("tag_title"))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

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
            _, res_msg = self.engine.create_tag(name, txt_msg.text().strip(), push=cb_push.isChecked())
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
                dialog, "FoolGit", t("tag_delete_remote_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            _, res_msg = self.engine.delete_tag(tname, remote=(remote_yn == QMessageBox.StandardButton.Yes))
            self.log(f"> {res_msg}")
            reload_tags()

        def do_push_all():
            _, res_msg = self.engine.push_all_tags()
            self.log(f"> {res_msg}")

        btn_create.clicked.connect(do_create)
        btn_del.clicked.connect(do_delete)
        btn_push_all.clicked.connect(do_push_all)
        dialog.exec()

    def _action_remote_dialog(self):
        """远程仓库设置弹窗"""
        dialog = create_dark_dialog(self, t("gui_remote_manager"), 520, 440)
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
            _, msg = self.engine.set_remote_origin(new_u)
            self.log(f"> {msg}")
            lbl_curr.setText(t("remote_origin_label", url=new_u))
            self.refresh_status()

        def do_test():
            lbl_test_result.setStyleSheet("color: #FBBF24;")
            lbl_test_result.setText(t("remote_testing"))
            ok, msg = self.engine.test_remote_connection()
            lbl_test_result.setStyleSheet("color: #34D399; font-weight: bold;" if ok else "color: #EF4444;")
            lbl_test_result.setText(msg)
            self.log(f"> {msg}")

        btn_save.clicked.connect(do_save)
        btn_test.clicked.connect(do_test)
        dialog.exec()

    def _action_diff_dialog(self):
        """代码差异对比弹窗 (高亮绿/红 diff)"""
        dialog = create_dark_dialog(self, t("gui_diff_viewer"), 720, 540, fixed=False)
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
            raw = self.engine.get_diff(
                staged=combo_mode.currentData(),
                file_path=combo_files.currentData() or None,
                color=False,
            )
            render_diff_html(txt_diff, raw, t("no_diff"))

        combo_mode.currentIndexChanged.connect(update_diff)
        combo_files.currentIndexChanged.connect(update_diff)
        update_diff()
        dialog.exec()

    def _action_history_dialog(self):
        """时光机弹窗（历史快照相册 + 详情/对比当前桌面/拉新分支/安全抵消）"""
        dialog = create_dark_dialog(self, t("gui_history_viewer"), 760, 580, fixed=False)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(18, 16, 18, 16)
        d_layout.setSpacing(10)

        title = QLabel("📜  " + t("history_menu_title"))
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
                deco = f" {parts[4].strip()}" if len(parts) >= 5 and parts[4].strip() else ""
                display_text = f"● {h}{deco}  ─  {msg}  ({when} · {author})"
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

        def _selected_hash() -> Optional[str]:
            curr = list_commits.currentItem()
            return commit_map.get(curr.text()) if curr else None

        def on_commit_selected():
            h = _selected_hash()
            if not h:
                return
            render_diff_html(txt_detail, self.engine.get_commit_detail(h))

        list_commits.itemSelectionChanged.connect(on_commit_selected)
        if list_commits.count() > 0:
            list_commits.setCurrentRow(0)

        tm_row = QHBoxLayout()
        btn_compare_now = QPushButton("🔍  " + t("gui_diff_viewer"))
        btn_compare_now.setCursor(Qt.CursorShape.PointingHandCursor)
        tm_row.addWidget(btn_compare_now)

        btn_branch_here = QPushButton(t("time_machine_branch_btn"))
        btn_branch_here.setCursor(Qt.CursorShape.PointingHandCursor)
        tm_row.addWidget(btn_branch_here)

        btn_revert_commit = QPushButton(t("time_machine_revert_btn"))
        btn_revert_commit.setObjectName("UndoButton")
        btn_revert_commit.setCursor(Qt.CursorShape.PointingHandCursor)
        tm_row.addWidget(btn_revert_commit)
        d_layout.addLayout(tm_row)

        def do_compare_now():
            h = _selected_hash()
            if not h:
                return
            cmp_raw = self.engine.diff_against_commit(h, color=False)
            render_diff_html(txt_detail, cmp_raw, t("history_cli_compare_clean", commit=h))

        def do_branch_here():
            h = _selected_hash()
            if not h:
                return
            bname, ok_in = QInputDialog.getText(
                dialog, t("gui_history_viewer"), t("time_machine_branch_prompt", commit=h)
            )
            if ok_in and bname.strip():
                ok, msg = self.engine.create_branch_at_commit(h, bname.strip())
                self.log(f"> {msg}")
                self.refresh_status()
                if ok:
                    dialog.accept()

        def do_revert_commit():
            h = _selected_hash()
            if not h:
                return
            reply = QMessageBox.question(
                dialog, t("gui_history_viewer"),
                t("time_machine_revert_confirm", commit=h),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                ok, msg = self.engine.revert_commit(h)
                self.log(f"> {msg}")
                self.refresh_status()
                if ok:
                    dialog.accept()

        btn_compare_now.clicked.connect(do_compare_now)
        btn_branch_here.clicked.connect(do_branch_here)
        btn_revert_commit.clicked.connect(do_revert_commit)
        dialog.exec()

    def _action_multi_sync_dialog(self):
        """多仓库扫描与批量同步弹窗"""
        dialog = create_dark_dialog(self, t("gui_multi_sync"), 620, 500, fixed=False)
        d_layout = QVBoxLayout(dialog)
        d_layout.setContentsMargins(20, 18, 20, 18)
        d_layout.setSpacing(12)

        repos = scan_multi_repos(self.target_dir)
        title = QLabel(t("multi_repo_title", count=len(repos)))
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        d_layout.addWidget(title)

        list_repos = QListWidget()
        for r in repos:
            clean_str = t("clean_status") if r["is_clean"] else t("dirty_status", count=r["total_changes"])
            sync_str = f"↑{r['ahead']} ↓{r['behind']}" if r["has_upstream"] else t("no_upstream").strip()
            list_repos.addItem(f"📁 {r['name']} [{r['branch']}]  ──  {clean_str}  ({sync_str})\n   {r['path']}")
        d_layout.addWidget(list_repos, stretch=1)

        btn_sync_all = QPushButton("🚀  " + t("multi_opt_all"))
        btn_sync_all.setObjectName("SyncButton")
        btn_sync_all.setCursor(Qt.CursorShape.PointingHandCursor)
        d_layout.addWidget(btn_sync_all)

        def do_sync_all():
            btn_sync_all.setEnabled(False)
            self.log(f"\n> ─── {t('multi_syncing', count=len(repos))} ───")
            succ, fail = 0, 0
            for r in repos:
                sub_engine = GitEngine(r["path"])
                ok, _ = sub_engine.one_click_sync()
                if ok:
                    succ += 1
                    self.log(f"  ✓ {r['name']} ({r['branch']})")
                else:
                    fail += 1
                    self.log(f"  ✗ {r['name']} ({r['branch']})")
            self.log(f"> {t('multi_sync_summary', succ=succ, fail=fail)}")
            self.refresh_status()
            dialog.accept()

        btn_sync_all.clicked.connect(do_sync_all)
        dialog.exec()

    def _open_settings_dialog(self):
        """功能库开关与个性化定制窗口"""
        dialog = create_dark_dialog(self, t("settings_title"), 480, 560)
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

        btn_add_cmd = QPushButton("➕ " + t("settings_opt_add_custom"))
        btn_add_cmd.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_add_cmd():
            name_text, ok1 = QInputDialog.getText(dialog, t("settings_opt_add_custom"), t("custom_name_prompt"))
            if not ok1 or not name_text.strip():
                return
            cmd_text, ok2 = QInputDialog.getText(dialog, t("settings_opt_add_custom"), t("custom_cmd_prompt"))
            if not ok2 or not cmd_text.strip():
                return
            desc_text, _ = QInputDialog.getText(dialog, t("settings_opt_add_custom"), t("custom_desc_prompt"))
            self.config_mgr.add_custom_command(name_text.strip(), cmd_text.strip(), desc_text.strip() if desc_text else "")
            self._render_quick_actions()
            self.log(f"> {t('custom_added', name=name_text)}")

        btn_add_cmd.clicked.connect(do_add_cmd)
        d_layout.addWidget(btn_add_cmd)

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
                target_cmd = cmds[labels.index(chosen_label)]
                self.config_mgr.remove_custom_command(target_cmd["id"])
                self._render_quick_actions()
                self.log(f"> {t('custom_removed', name=target_cmd['name'])}")

        btn_rm_cmd.clicked.connect(do_rm_cmd)
        d_layout.addWidget(btn_rm_cmd)

        btn_reset = QPushButton(t("settings_opt_reset"))
        btn_reset.setStyleSheet("color: #EF4444; border-color: #4D2529;")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_reset():
            reply = QMessageBox.question(dialog, "FoolGit", t("reset_confirm"))
            if reply == QMessageBox.StandardButton.Yes:
                self.config_mgr.reset_to_defaults()
                dialog.accept()
                self._render_quick_actions()
                self.refresh_status()
                self.log(f"> {t('reset_done')}")

        btn_reset.clicked.connect(do_reset)
        d_layout.addWidget(btn_reset)
        dialog.exec()
