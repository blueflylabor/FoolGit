"""
FoolGit 国际化 (i18n) 模块
严格分离语言：英文模式下 100% 纯英文，中文模式下 100% 纯中文，严禁中英文混杂。
"""

from typing import Dict, Any

DEFAULT_LANG = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ─────────────────────────────────────────────────────────────
    # 英文 (Pure English - Zero Chinese)
    # ─────────────────────────────────────────────────────────────
    "en": {
        # App & Header
        "app_title": "FoolGit v1.0.0 ── Simple & Foolproof Git Assistant",
        "repo_label": "Repo",
        "branch_label": "Branch",
        "status_label": "Status",
        "clean_status": "✨ Clean, nothing to commit",
        "dirty_status": "✎ {count} file(s) changed",
        "sync_up_to_date": " (Synced with remote ✓)",
        "sync_ahead": " (↑ {count} commit(s) ahead)",
        "sync_behind": " (↓ {count} update(s) behind)",
        "sync_diverged": " (↑ ahead {ahead} / ↓ behind {behind})",
        "no_upstream": " (No remote tracking)",
        "press_enter_to_continue": "Press Enter to return to main menu...",
        "goodbye": "👋 Goodbye!",
        "invalid_choice": "⚠️ Invalid option. Please enter a valid number, + or q.",
        "out_of_range": "⚠️ Number [{choice}] is out of range.",
        "prompt_choice": "👉 Please select an option [Default: 1, q: Quit]: ",
        "menu_quit": "Quit",

        # Settings Menu
        "settings_title": "FoolGit Settings & Feature Store",
        "settings_btn": "Settings",
        "settings_opt_presets": "[1] Feature Library (Enable or disable built-in features)",
        "settings_opt_add_custom": "[2] Add Custom Git Command (Extend your shortcuts)",
        "settings_opt_remove_custom": "[3] Remove a Custom Command",
        "settings_opt_lang": "[4] Interface Language (Current: English)",
        "settings_opt_reset": "[5] Reset to Factory Defaults (Restore 6 core actions)",
        "back_to_main": "[b] Back to main menu",
        "select_setting": "Select a setting [1/2/3/4/5, b to return]: ",
        "reset_confirm": "Are you sure you want to restore factory defaults? (y/n): ",
        "reset_done": "Reset to factory defaults completed successfully!",

        # Language Switcher
        "lang_name_current": "English",
        "lang_switch_title": "Select Interface Language:",
        "lang_opt_en": "[1] English",
        "lang_opt_zh": "[2] Simplified Chinese",
        "lang_changed": "Language updated to: English",
        "lang_toggle_btn": "Language: English",

        # Feature Store
        "feature_store_title": "Feature Library (Enter number to toggle on/off):",
        "feature_enabled": "[Enabled ✓]",
        "feature_disabled": "[Disabled ✗]",
        "feature_toggle_hint": "Tip: Enter a number to toggle, or 'b' to go back",
        "feature_toggle_prompt": "Select feature to toggle [b to return]: ",
        "feature_turned_on": "Enabled and added to main menu: {name}",
        "feature_turned_off": "Removed from main menu: {name}",

        # Custom Commands
        "add_custom_title": "Add Custom Git Command to Main Menu:",
        "custom_name_prompt": "1. Display name (e.g. Push All Tags): ",
        "custom_cmd_prompt": "2. Actual Git command (e.g. git push origin --tags): ",
        "custom_desc_prompt": "3. Optional description: ",
        "custom_added": "Custom command [{name}] added! It now appears on the main menu.",
        "remove_custom_title": "Select custom command to remove:",
        "remove_custom_empty": "No custom commands found.",
        "custom_removed": "Removed command [{name}]",
        "custom_tag": "Custom",

        # Action: Sync (One-Click Sync)
        "sync_banner": "One-Click Sync & Save",
        "sync_tip": "Automatically pulls remote ➔ records changes ➔ commits ➔ pushes to remote.",
        "commit_prompt": "Enter commit message (Press Enter for auto timestamp): ",
        "syncing": "Safely syncing, please wait...",
        "sync_step_no_remote": "No remote repository (origin) configured. Saving locally only.",
        "sync_step_pull": "Step 1/4: Checking and pulling remote updates...",
        "sync_clean_nothing": "Working tree is completely clean and up-to-date. No commit needed!",
        "sync_step_add": "Step 2/4: Staging all modified files (git add -A)...",
        "sync_add_failed": "Failed to add files: {error}",
        "sync_step_commit": "Step 3/4: Creating local commit [{msg}]...",
        "sync_commit_no_new": "Commit generated no changes: {error}",
        "sync_commit_success": "Local commit created successfully!",
        "sync_already_committed": "No new local edits to commit. Pushing existing local commits...",
        "sync_step_push": "Step 4/4: Pushing changes to remote branch [{branch}]...",
        "sync_push_success": "Synced successfully! Your code is now fully in sync with remote!",
        "sync_push_rejected": "Push rejected: remote has newer commits. Please run 'Pull' first.",
        "sync_push_failed": "Push failed: {error}",
        "sync_local_done": "Local changes saved successfully! (Push skipped: no remote origin)",

        # Action: Pull
        "pulling": "Checking and pulling latest remote code...",
        "pull_no_remote": "No remote repository (origin) configured for this repo.",
        "pull_up_to_date": "Code is already up to date.",
        "pull_success": "Successfully pulled latest updates from remote!",
        "pull_conflict": "Pull failed: merge conflicts detected with local code! Please check files or use Stash.",
        "pull_no_ref": "Remote branch [{branch}] does not exist yet. You can use 'One-Click Sync' to push it.",
        "pull_error": "Pull encountered an issue: {error}",

        # Action: Status & Diff
        "status_title": "Changes & Status Overview:",
        "work_dir": "Working directory: {path}",
        "clean_workspace": "Working tree clean, no pending changes found.",
        "staged_files": "Staged files ready to commit:",
        "modified_files": "Modified files (unstaged):",
        "untracked_files": "Untracked files (new):",
        "diff_stat_title": "Line changes statistics:",
        "diff_title": "Inspecting code diff (git diff):",
        "no_diff": "No modified code differences in working tree.",

        # Action: Undo
        "undo_title": "Undo / Discard Changes Menu:",
        "undo_opt_all": "Discard ALL uncommitted changes (Restore clean workspace)",
        "undo_opt_commit": "Undo the last commit (Keep your edited code in workspace)",
        "undo_opt_file": "Discard changes in a specific file",
        "undo_prompt": "Select undo level [1/2/3, b to return]: ",
        "discard_all_confirm": "Are you sure you want to discard ALL uncommitted work? This cannot be undone! (type y to confirm): ",
        "discard_all_success": "All uncommitted changes discarded. Working tree restored to clean state!",
        "discard_file_success": "Discarded local changes in [{target}].",
        "discard_file_prompt": "Enter file path to discard changes: ",
        "uncommit_success": "Last commit undone! Your code remains intact in the workspace.",
        "uncommit_failed": "Failed to undo commit (this may be the initial commit): {error}",
        "cancelled": "Operation cancelled.",

        # Action: Branch
        "branch_title": "Branch Management:",
        "local_branches": "Local branches:",
        "current_branch_mark": "(current)",
        "branch_opt_switch": "[Enter number] Switch to corresponding branch",
        "branch_opt_new": "[n] Create & switch to a new branch",
        "branch_prompt": "Select branch or enter option: ",
        "new_branch_prompt": "Enter new branch name (e.g. dev, feat-auth): ",
        "switch_success": "Switched to branch [{branch}] successfully.",
        "create_branch_success": "Created and switched to new branch [{branch}]!",

        # Action: Stash
        "stash_title": "Stash Management:",
        "stash_opt_save": "Stash changes (Temporarily package unfinished work & clean workspace)",
        "stash_opt_pop": "Restore stash (Pop and re-apply latest stashed work)",
        "stash_prompt": "Select option: ",
        "stash_note_prompt": "Optional note for stash (Press Enter for auto timestamp): ",
        "stash_clean_nothing": "No local changes to save. Stash not needed.",
        "stash_saved": "Code safely saved to stash! Working tree is clean.",
        "stash_popped": "Successfully restored stashed code changes!",
        "stash_empty": "Stash box is empty. No stashed changes found.",

        # Action: History & Clean & Tag & Remote
        "history_title": "Recent 10 Commits Summary:",
        "no_history": "No commit history found.",
        "clean_confirm": "Are you sure you want to delete all untracked files/directories? (type y to confirm): ",
        "clean_success": "Cleaned untracked files successfully!",
        "tag_name_prompt": "Enter new release tag name (e.g. v1.0.0): ",
        "tag_msg_prompt": "Optional tag message (Press Enter to use tag name): ",
        "tag_push_prompt": "Push this tag to remote repository? (y/n) [Default: y]: ",
        "tag_created": "Created local tag [{tag}] successfully!",
        "tag_pushed": "Tag [{tag}] pushed to remote successfully!",
        "remote_title": "Remote Repositories:",
        "remote_none": "No remote repository configured.",

        # Multi-repo & non-git
        "non_git_title": "Current directory is not a Git repository",
        "non_git_sub_found": "Not a Git repo, but found {count} Git project(s) in subdirectories:",
        "init_repo_opt": "[1] Initialize a new Git repository here (git init)",
        "clone_repo_opt": "[2] Clone a remote repository here (git clone)",
        "clone_url_prompt": "Enter remote Git repository URL: ",
        "multi_repo_title": "Multi-Repository Dashboard ({count} repos)",
        "multi_opt_enter": "[Enter number] Open dedicated menu for that repo",
        "multi_opt_all": "[a] One-click sync ALL repositories in batch",
        "multi_syncing": "Syncing {count} repositories in batch...",
        "multi_sync_summary": "Batch sync completed: {succ} succeeded, {fail} failed.",

        # Presets metadata
        "preset_sync_name": "One-Click Sync",
        "preset_sync_tag": "Recommended",
        "preset_sync_desc": "Auto pull ➔ record changes ➔ commit ➔ push to remote",

        "preset_pull_name": "Pull Latest Code",
        "preset_pull_tag": "Common",
        "preset_pull_desc": "Safely fetch and merge latest remote updates",

        "preset_status_name": "View Changes & Status",
        "preset_status_tag": "Status",
        "preset_status_desc": "Overview of changed files, staged files and sync status",

        "preset_undo_name": "Undo / Discard Changes",
        "preset_undo_tag": "Safety",
        "preset_undo_desc": "Discard unwanted edits or undo the last commit",

        "preset_branch_name": "Switch or Create Branch",
        "preset_branch_tag": "Branch",
        "preset_branch_desc": "Switch branch by number or create a new branch",

        "preset_stash_name": "Stash / Restore Edits",
        "preset_stash_tag": "Stash",
        "preset_stash_desc": "Temporarily stash unfinished work and restore anytime",

        "preset_history_name": "View Recent Commit History",
        "preset_history_tag": "Extra",
        "preset_history_desc": "Clean timeline of recent 10 commits with author",

        "preset_diff_name": "View Code Differences (Diff)",
        "preset_diff_tag": "Extra",
        "preset_diff_desc": "Line-by-line inspection of changes",

        "preset_clean_name": "Clean Untracked Files",
        "preset_clean_tag": "Extra",
        "preset_clean_desc": "Remove untracked junk or generated files",

        "preset_tag_name": "Release Tag Management",
        "preset_tag_tag": "Extra",
        "preset_tag_desc": "Tag current commit (e.g. v1.0.0) and push to remote",

        "preset_remote_name": "View Remote Repositories",
        "preset_remote_tag": "Extra",
        "preset_remote_desc": "Inspect origin URLs and remote configuration",

        "preset_multi_sync_name": "Multi-Repository Sync",
        "preset_multi_sync_tag": "Batch",
        "preset_multi_sync_desc": "Scan and sync multiple Git repositories in batch",

        # GUI Specific labels
        "gui_quick_actions": "Quick Actions",
        "gui_tools": "Tools & Settings",
        "gui_terminal_ready": "FoolGit Ready. Click 'One-Click Sync' to commit & push.",
        "gui_commit_placeholder": "Commit message (leave blank for auto timestamp)...",
    },

    # ─────────────────────────────────────────────────────────────
    # 简体中文 (Pure Chinese - Zero English clutter)
    # ─────────────────────────────────────────────────────────────
    "zh": {
        # App & Header
        "app_title": "FoolGit v1.0.0 ── 傻瓜式 Git 助理",
        "repo_label": "仓库",
        "branch_label": "分支",
        "status_label": "状态",
        "clean_status": "✨ 干净无修改",
        "dirty_status": "✎ {count} 个文件有改动",
        "sync_up_to_date": " (与远端同步 ✓)",
        "sync_ahead": " (↑待推送 {count} 个提交)",
        "sync_behind": " (↓待拉取 {count} 个更新)",
        "sync_diverged": " (↑超前{ahead} / ↓落后{behind})",
        "no_upstream": " (未关联远端)",
        "press_enter_to_continue": "按回车键返回主菜单...",
        "goodbye": "👋 再见！",
        "invalid_choice": "⚠️ 输入无效，请输入数字序号、+ 或 q。",
        "out_of_range": "⚠️ 编号 [{choice}] 不在菜单范围内，请重新选择。",
        "prompt_choice": "👉 请选择操作编号 [直接回车默认: 1, q: 退出]: ",
        "menu_quit": "退出",

        # Settings Menu
        "settings_title": "FoolGit 功能库与个性化设置",
        "settings_btn": "个性化设置",
        "settings_opt_presets": "[1] 预设功能库开关 (从官方功能池自由勾选追加或移除)",
        "settings_opt_add_custom": "[2] 添加我的自定义 Git 命令 (自由扩展专属快捷命令)",
        "settings_opt_remove_custom": "[3] 删除我的自定义 Git 命令",
        "settings_opt_lang": "[4] 切换界面语言 (当前: 简体中文)",
        "settings_opt_reset": "[5] 恢复出厂设置 (重置为默认6大傻瓜功能)",
        "back_to_main": "[b] 返回主菜单",
        "select_setting": "请选择设置项 [1/2/3/4/5, b 返回]: ",
        "reset_confirm": "确定要重置回出厂默认设置吗？(y/n): ",
        "reset_done": "已恢复出厂默认设置！",

        # Language Switcher
        "lang_name_current": "简体中文",
        "lang_switch_title": "选择界面语言:",
        "lang_opt_en": "[1] 英文 (English)",
        "lang_opt_zh": "[2] 简体中文 (Chinese)",
        "lang_changed": "语言设置已更新为: 简体中文",
        "lang_toggle_btn": "语言: 简体中文",

        # Feature Store
        "feature_store_title": "官方功能库清单 (输入序号切换开启/停用):",
        "feature_enabled": "[已开启 ✓]",
        "feature_disabled": "[已停用 ✗]",
        "feature_toggle_hint": "提示: 输入数字序号直接切换对应功能状态，输入 b 返回",
        "feature_toggle_prompt": "请选择要切换的功能编号 [b 返回]: ",
        "feature_turned_on": "已开启并加入主菜单: {name}",
        "feature_turned_off": "已从主菜单移除: {name}",

        # Custom Commands
        "add_custom_title": "添加自定义命令到主菜单:",
        "custom_name_prompt": "1. 请输入菜单显示的名称 (例如: 推送全部标签): ",
        "custom_cmd_prompt": "2. 请输入实际执行的 Git 命令 (例如: git push origin --tags): ",
        "custom_desc_prompt": "3. 可选输入一句话功能说明: ",
        "custom_added": "成功添加自定义命令 [{name}]！它已出现在主菜单中。",
        "remove_custom_title": "请选择要删除的自定义命令:",
        "remove_custom_empty": "当前暂无自定义命令。",
        "custom_removed": "已删除命令 [{name}]",
        "custom_tag": "自定",

        # Action: Sync (一键保存并同步)
        "sync_banner": "一键保存并同步",
        "sync_tip": "自动拉取远端 ➔ 记录改动 ➔ 提交版本 ➔ 推送到远端。",
        "commit_prompt": "请输入提交说明 (直接回车自动生成带时间记录): ",
        "syncing": "正在安全同步中，请稍候...",
        "sync_step_no_remote": "未检测到远程仓库 (origin)，将仅在本地完成提交。",
        "sync_step_pull": "步骤 1/4: 检查并拉取远端更新...",
        "sync_clean_nothing": "工作区非常干净，代码已是最新，无需提交或推送！",
        "sync_step_add": "步骤 2/4: 记录所有文件改动 (git add -A)...",
        "sync_add_failed": "添加文件失败: {error}",
        "sync_step_commit": "步骤 3/4: 提交本地版本 [{msg}]...",
        "sync_commit_no_new": "提交未产生新版本: {error}",
        "sync_commit_success": "本地提交完成！",
        "sync_already_committed": "本地代码无需新提交，检测到有已提交但未推送的内容。",
        "sync_step_push": "步骤 4/4: 推送改动到远端分支 [{branch}]...",
        "sync_push_success": "推送成功！本地代码已与远端完全同步！",
        "sync_push_rejected": "推送被拒绝：远端有更新的版本。请先执行【拉取最新代码】再试。",
        "sync_push_failed": "推送失败: {error}",
        "sync_local_done": "本地已完成保存！(由于未配置远程仓库，已跳过推送)",

        # Action: Pull
        "pulling": "正在检查并拉取远程代码...",
        "pull_no_remote": "当前仓库未配置远程仓库 (origin)，无需拉取。",
        "pull_up_to_date": "代码已是最新，无需更新。",
        "pull_success": "成功拉取远程最新代码！",
        "pull_conflict": "拉取失败：与本地代码产生冲突！建议先查看改动或使用【暂存保存】后再拉取。",
        "pull_no_ref": "远端尚未建立 [{branch}] 分支，可直接进行【一键保存并同步】以推送到远端。",
        "pull_error": "拉取遇到问题: {error}",

        # Action: Status & Diff
        "status_title": "代码改动详情清单:",
        "work_dir": "工作目录: {path}",
        "clean_workspace": "工作区非常干净，没有发现任何待保存的改动。",
        "staged_files": "已暂存待提交的文件:",
        "modified_files": "已修改但未暂存的文件:",
        "untracked_files": "新建且未跟踪的文件:",
        "diff_stat_title": "代码行数增删统计:",
        "diff_title": "正在查看具体代码差异 (diff):",
        "no_diff": "当前工作区没有已修改的代码差异。",

        # Action: Undo
        "undo_title": "后悔药 / 撤销改动菜单:",
        "undo_opt_all": "放弃全部未提交的代码修改 (工作区彻底还原干净)",
        "undo_opt_commit": "撤回上一次提交 commit (代码依然保留在工作区)",
        "undo_opt_file": "放弃单个指定文件的修改",
        "undo_prompt": "请选择后悔药级别 [1/2/3, b 返回]: ",
        "discard_all_confirm": "确定要彻底放弃所有未提交的代码吗？该操作不可逆！(输入 y 确认): ",
        "discard_all_success": "已经丢弃所有未提交修改，工作区已恢复为干净状态！",
        "discard_file_success": "已经丢弃文件 [{target}] 的所有本地改动。",
        "discard_file_prompt": "请输入要丢弃修改的文件路径: ",
        "uncommit_success": "成功撤回上一次提交！代码完整保留在工作区中。",
        "uncommit_failed": "撤回失败 (可能当前仓库只有一次提交): {error}",
        "cancelled": "已取消操作。",

        # Action: Branch
        "branch_title": "分支管理菜单:",
        "local_branches": "本地分支列表:",
        "current_branch_mark": "(当前分支)",
        "branch_opt_switch": "[输入数字] 切换到对应分支",
        "branch_opt_new": "[n] 新建并切换到新分支",
        "branch_prompt": "请选择或输入操作: ",
        "new_branch_prompt": "请输入新分支名称 (如: dev, feat-auth): ",
        "switch_success": "已成功切换到分支 [{branch}]。",
        "create_branch_success": "成功创建并切换到新分支 [{branch}]！",

        # Action: Stash
        "stash_title": "代码暂存箱管理 (Stash):",
        "stash_opt_save": "暂存存盘 (临时打包未写完的代码，工作区还原干净)",
        "stash_opt_pop": "取回恢复 (从暂存箱取回上一次保存的代码)",
        "stash_prompt": "请选择操作: ",
        "stash_note_prompt": "可选输入暂存备注 (直接回车默认时间): ",
        "stash_clean_nothing": "当前没有未保存的改动，暂存箱不需要存入。",
        "stash_saved": "代码已安全存入暂存箱！工作区已还原干净。",
        "stash_popped": "成功从暂存箱恢复上一次的代码改动！",
        "stash_empty": "暂存箱里空空如也，没有可恢复的存盘。",

        # Action: History & Clean & Tag & Remote
        "history_title": "最近 10 次提交简明历史:",
        "no_history": "暂无提交历史。",
        "clean_confirm": "确定要清理所有未跟踪的文件与临时生成目录吗？(输入 y 确认): ",
        "clean_success": "清理完成！工作区已移除所有未跟踪文件。",
        "tag_name_prompt": "请输入新版本标签名称 (如 v1.0.0): ",
        "tag_msg_prompt": "可选输入版本说明 (直接回车默认与标签同名): ",
        "tag_push_prompt": "是否同步将该标签推送到远程仓库？(y/n) [默认 y]: ",
        "tag_created": "成功创建本地标签 [{tag}]！",
        "tag_pushed": "标签 [{tag}] 已成功推送到远程仓库！",
        "remote_title": "关联的远程仓库地址:",
        "remote_none": "当前仓库尚未配置远程仓库 (origin)。",

        # Multi-repo & non-git
        "non_git_title": "当前目录不是 Git 仓库，且子目录下未找到项目",
        "non_git_sub_found": "当前目录不是 Git 仓库，但在此目录下发现了 {count} 个 Git 子项目：",
        "init_repo_opt": "[1] 在当前目录初始化新建一个 Git 仓库 (git init)",
        "clone_repo_opt": "[2] 克隆一个远程仓库到这里 (git clone)",
        "clone_url_prompt": "请输入远程 Git 仓库 URL: ",
        "multi_repo_title": "多仓库巡检列表 (共 {count} 个)",
        "multi_opt_enter": "[输入序号] 进入该子仓库的独立傻瓜面板",
        "multi_opt_all": "[a] 全部一键批量同步 (Pull ➔ Commit ➔ Push)",
        "multi_syncing": "开始对全部 {count} 个仓库执行批量同步...",
        "multi_sync_summary": "批量同步结束: 成功 {succ} 个，失败 {fail} 个。",

        # Presets metadata
        "preset_sync_name": "一键保存并同步",
        "preset_sync_tag": "推荐",
        "preset_sync_desc": "自动拉取 ➔ 保存改动 ➔ 提交 ➔ 推送远端",

        "preset_pull_name": "一键拉取最新代码",
        "preset_pull_tag": "常用",
        "preset_pull_desc": "从远程仓库下载最新更新并安全合并",

        "preset_status_name": "查看代码改动详情",
        "preset_status_tag": "状态",
        "preset_status_desc": "清晰展示当前分支、改动文件清单及超前/落后状态",

        "preset_undo_name": "后悔药 / 撤销改动",
        "preset_undo_tag": "安全",
        "preset_undo_desc": "一键撤销写乱的代码、丢弃修改或撤回上次提交",

        "preset_branch_name": "切换或新建分支",
        "preset_branch_tag": "分支",
        "preset_branch_desc": "直接按编号秒切分支，或一键输入新名称创建分支",

        "preset_stash_name": "暂存保存 / 恢复改动",
        "preset_stash_tag": "储藏",
        "preset_stash_desc": "临时封存没写完的代码，随时一键恢复",

        "preset_history_name": "查看简明提交历史",
        "preset_history_tag": "扩展",
        "preset_history_desc": "按时间倒序列出最近的 10 次提交与作者",

        "preset_diff_name": "查看具体代码差异",
        "preset_diff_tag": "扩展",
        "preset_diff_desc": "逐行对比改动代码的高亮变化 (diff)",

        "preset_clean_name": "清理未跟踪垃圾文件",
        "preset_clean_tag": "扩展",
        "preset_clean_desc": "一键清理本地新建但未加入 git 的临时文件和空目录",

        "preset_tag_name": "版本标签 (Release Tag)",
        "preset_tag_tag": "扩展",
        "preset_tag_desc": "打上版本标记 (如 v1.0.0) 并可一键推送到远程",

        "preset_remote_name": "查看远程仓库地址",
        "preset_remote_tag": "扩展",
        "preset_remote_desc": "查看当前绑定的 GitHub/GitLab 远程仓库链接",

        "preset_multi_sync_name": "多仓库批量巡检与同步",
        "preset_multi_sync_tag": "批量",
        "preset_multi_sync_desc": "扫描子目录下所有 Git 项目并进行批量一键同步",

        # GUI Specific labels
        "gui_quick_actions": "日常快捷操作",
        "gui_tools": "工具与设置",
        "gui_terminal_ready": "FoolGit 就绪。点击「一键保存并同步」即可提交并推送到远端。",
        "gui_commit_placeholder": "输入提交说明 (留空将自动记录时间)...",
    }
}

_CURRENT_LANG = DEFAULT_LANG


def set_language(lang: str) -> None:
    """设置全局当前语言 ('en' 或 'zh')"""
    global _CURRENT_LANG
    if lang in TRANSLATIONS:
        _CURRENT_LANG = lang
    else:
        _CURRENT_LANG = DEFAULT_LANG


def get_language() -> str:
    """获取当前语言代码 ('en' 或 'zh')"""
    return _CURRENT_LANG


def t(key: str, **kwargs) -> str:
    """国际化翻译函数"""
    lang_dict = TRANSLATIONS.get(_CURRENT_LANG, TRANSLATIONS[DEFAULT_LANG])
    text = lang_dict.get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
