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
        "undo_title": "Undo Pills (Pick How Far Back to Go):",
        "undo_opt_all": "Wipe ALL unsaved edits (Reset desk to last snapshot)",
        "undo_opt_commit": "Unpack last snapshot (Cancel snapshot, KEEP your edited files)",
        "undo_opt_file": "Wipe edits in JUST ONE file (Keep everything else)",
        "undo_opt_amend": "Rename last snapshot message (Fix typo in last note)",
        "undo_prompt": "Pick an undo pill [1/2/3/4, b to return]: ",
        "discard_all_confirm": "Are you sure you want to discard ALL uncommitted work? This cannot be undone! (type y to confirm): ",
        "discard_all_success": "All uncommitted changes discarded. Working tree restored to clean state!",
        "discard_file_success": "Discarded local changes in [{target}].",
        "discard_file_prompt": "Enter file path to discard changes: ",
        "discard_file_no_changes": "No modified, staged, or untracked files to discard.",
        "discard_file_select_prompt": "Enter file number to discard [b to return]: ",
        "discard_file_confirm": "Discard all changes in [{target}]? (y/n): ",
        "uncommit_success": "Last commit undone! Your code remains intact in the workspace.",
        "uncommit_failed": "Failed to undo commit (this may be the initial commit): {error}",
        "cancelled": "Operation cancelled.",

        # Action: Branch
        "branch_title": "Parallel Worlds (Branches):",
        "local_branches": "Your parallel worlds:",
        "current_branch_mark": "(you are here)",
        "branch_opt_switch": "[Enter number] Jump into that parallel world",
        "branch_opt_new": "[n] Spin off a brand-new parallel world (safe sandbox)",
        "branch_opt_delete": "[d] Delete a parallel world",
        "branch_delete_prompt": "Enter branch name to delete: ",
        "branch_delete_confirm": "Force delete branch [{branch}]? (y/n) [Default: n]: ",
        "branch_delete_success": "Branch [{branch}] deleted successfully.",
        "branch_delete_failed": "Failed to delete branch: {error}",
        "branch_cannot_delete_current": "Cannot delete current branch [{branch}]. Switch to another branch first.",
        "branch_prompt": "Select branch or enter option: ",
        "new_branch_prompt": "Enter new branch name (e.g. dev, feat-auth): ",
        "switch_success": "Switched to branch [{branch}] successfully.",
        "create_branch_success": "Created and switched to new branch [{branch}]!",

        # Action: Stash
        "stash_title": "Temporary Locker (Pause WIP Without Losing It):",
        "stash_opt_save": "Lock current WIP in locker (Clean desk for an urgent task)",
        "stash_opt_pop": "Take out latest WIP from locker (Resume where you left off)",
        "stash_opt_list": "Open locker list (Peek inside, restore, or throw away)",
        "stash_prompt": "Select locker action: ",
        "stash_note_prompt": "Optional label for this locker item (Enter for auto time): ",
        "stash_clean_nothing": "Desk is already clean — nothing to put in locker.",
        "stash_saved": "WIP safely locked away! Your desk is clean now.",
        "stash_popped": "Took out your WIP from the locker and put it back on your desk!",
        "stash_empty": "Your temporary locker is empty.",
        "stash_applied": "Copied [{ref}] back to your desk (kept a backup in locker).",
        "stash_dropped": "Threw away locker item [{ref}].",
        "stash_list_title": "Items Inside Temporary Locker:",
        "stash_list_empty": "Locker is empty.",
        "stash_list_prompt": "Enter item number to inspect/manage, or 'b' to return: ",
        "stash_entry_opt_peek": "[p] Peek inside (see what files & lines were saved)",
        "stash_entry_opt_apply": "[a] Restore to desk (keep backup in locker)",
        "stash_entry_opt_drop": "[d] Throw away this locker item",
        "stash_entry_opt_back": "[b] Back to locker list",
        "stash_entry_prompt": "Action [p/a/d/b]: ",

        # Action: History & Clean & Tag & Remote & Diff
        "history_title": "Time Machine (Snapshot Album):",
        "history_menu_title": "Time Machine (Snapshot Album):",
        "no_history": "No snapshots recorded yet.",
        "history_prompt_inspect": "Enter snapshot number [1-{count}] to inspect or time-travel, or Enter to return: ",
        "history_commit_detail_title": "Snapshot [{commit}]:",
        "history_cli_action_prompt": "Time Machine: [b] Branch from here (safe copy), [c] Compare with now, [r] Safe undo, or Enter: ",
        "history_cli_compare_title": "Changes between snapshot [{commit}] and your current desk:",
        "history_cli_compare_clean": "Your current desk is identical to snapshot [{commit}]!",
        "sync_preview_label": "Next step",

        # Hardening, Onboarding, Auto-Locker Pull & CLI Purity
        "git_timeout_error": "Git command timed out after {seconds}s (check network or auth).",
        "identity_missing_title": "First-Time Snapshot Author Setup:",
        "identity_missing_desc": "Git needs your name & email to label your snapshots.",
        "identity_name_prompt": "Your name (e.g. Alice): ",
        "identity_email_prompt": "Your email (e.g. alice@example.com): ",
        "identity_invalid": "Name and email cannot be empty.",
        "identity_saved": "Author identity saved ({name} <{email}>)!",
        "identity_skipped": "Skipped author setup. Commit may fail without Git identity.",
        "pull_blocked_local": "Local unsaved edits would be overwritten by incoming updates.",
        "pull_auto_locker_prompt": "Use Auto-Locker? [l] Lock WIP → Pull → Restore WIP, or Enter to cancel: ",
        "pull_auto_locker_step_save": "Step 1/3: Locking local WIP into Temporary Locker...",
        "pull_auto_locker_step_pull": "Step 2/3: Downloading cloud updates...",
        "pull_auto_locker_step_pop": "Step 3/3: Restoring your WIP from Temporary Locker...",
        "pull_auto_locker_pop_conflict": "Cloud updates downloaded cleanly, but your restored WIP conflicts with incoming edits. Use Conflict Rescue!",
        "not_git_error": "❌ Current directory is not a Git repository.",
        "custom_running": "🚀 Running: {cmd}",
        "custom_ok": "✅ OK",
        "custom_failed": "❌ Failed",
        "feature_not_found": "Feature [{id}] not found.",
        "select_option_prompt": "Select option: ",
        "select_number_back_prompt": "Number [b to return]: ",
        "non_git_select_prompt": "Select [1/2, q]: ",
        "init_ok_msg": "🎉 Repository initialized! Opening FoolGit...",
        "init_fail_msg": "❌ Init failed: {error}",
        "cloning_msg": "Cloning {url} ...",
        "clone_ok_msg": "🎉 Cloned successfully!",
        "clone_fail_msg": "❌ Clone failed: {error}",
        "no_repos_found": "No Git repositories found in subdirectories.",
        "gui_refresh_btn": "🔄 Refresh",
        "gui_create_pr_btn": "🔀 Create PR",
        "conflict_banner_cli": "[!] Conflict Rescue ({count} conflicted file(s) waiting!)",
        "conflict_files_status": "Conflicted files (need rescue):",
        "risk_ignore_continue_prompt": "[i] Add sensitive files to .gitignore & sync, [y] Continue anyway, or [n] Cancel [Default: n]: ",
        "commit_smart_hint": "Auto summary if Enter: {msg}",
        "commit_prefix_hint": "Quick prefixes: [1] feat:  [2] fix:  [3] docs:  [4] chore:  (or type note directly)",
        "commit_prefix_note_prompt": "Enter brief note after '{prefix} ' (Enter to use auto): ",
        "pr_available_hint": "🔀 Create PR / Compare link: {url}",
        "pr_open_prompt": "Open PR page in browser now? (y/n) [Default: n]: ",
        "pr_not_feature_branch": "Switch to a non-main parallel world branch first to open a PR link.",
        "opened_in_browser": "🌐 Opened in browser: {url}",
        "history_more_lines": "  ... ({total} lines total)",

        "clean_title": "Clean Untracked Junk Files:",
        "clean_preview_title": "The following untracked files/folders will be permanently deleted:",
        "clean_confirm": "Are you sure you want to delete these untracked files/directories? (type y to confirm): ",
        "clean_success": "Cleaned untracked files successfully!",
        "clean_nothing": "No untracked files to clean. Working tree is tidy!",

        "tag_title": "Release Tag Management:",
        "tag_opt_list": "[1] List existing tags",
        "tag_opt_create": "[2] Create a new tag (with optional push)",
        "tag_opt_delete": "[3] Delete a tag (local / remote)",
        "tag_opt_push_all": "[4] Push all local tags to remote",
        "tag_prompt": "Select tag action [1/2/3/4, b to return]: ",
        "tag_name_prompt": "Enter new release tag name (e.g. v1.0.0): ",
        "tag_msg_prompt": "Optional tag message (Press Enter to use tag name): ",
        "tag_push_prompt": "Push this tag to remote repository? (y/n) [Default: y]: ",
        "tag_created": "Created local tag [{tag}] successfully!",
        "tag_pushed": "Tag [{tag}] pushed to remote successfully!",
        "tag_deleted": "Tag [{tag}] deleted successfully.",
        "tag_none_found": "No tags found in repository.",
        "tag_delete_prompt": "Enter tag name to delete: ",
        "tag_delete_remote_confirm": "Also delete tag from remote repository? (y/n) [Default: n]: ",
        "tag_push_all_success": "All tags pushed to remote successfully!",
        "tag_push_all_failed": "Failed to push tags: {error}",

        "remote_title": "Remote Repositories:",
        "remote_none": "No remote repository configured.",
        "remote_origin_label": "Current Remote (origin): {url}",
        "remote_opt_view": "[1] View remote URLs",
        "remote_opt_set": "[2] Set or update 'origin' URL",
        "remote_opt_test": "[3] Test connection to remote repository",
        "remote_opt_open_web": "[4] Open repository in browser",
        "remote_opt_open_pr": "[5] Create PR / Compare branch in browser",
        "remote_prompt": "Select remote action [1/2/3/4/5, b to return]: ",
        "remote_set_prompt": "Enter new remote URL for 'origin': ",
        "remote_set_success": "Remote origin URL updated to: {url}",
        "remote_test_success": "Connection to remote repository verified successfully!",
        "remote_test_failed": "Connection failed: {error}",
        "remote_testing": "Testing connection to remote repository...",

        "diff_menu_title": "Inspect Code Differences (Diff):",
        "diff_opt_unstaged": "[1] View unstaged changes (working tree edits)",
        "diff_opt_staged": "[2] View staged changes (ready to commit)",
        "diff_opt_file": "[3] View diff for a specific file",
        "diff_prompt": "Select diff mode [1/2/3, b to return]: ",
        "diff_file_prompt": "Select file number to view diff [b to return]: ",
        "diff_no_modified_files": "No modified files found.",

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

        "preset_gitignore_name": ".gitignore Quick Editor",
        "preset_gitignore_tag": "Extra",
        "preset_gitignore_desc": "View and add patterns to .gitignore without opening an editor",

        # Amend commit
        "amend_title": "Edit Last Commit Message:",
        "amend_prompt": "Enter new commit message: ",
        "amend_success": "Last commit message updated to: [{msg}]",
        "amend_empty_msg": "Commit message cannot be empty.",

        # Conflict rescue
        "conflict_title": "Merge Conflict Detected:",
        "conflict_files_label": "Files with conflicts:",
        "conflict_opt_abort": "[a] Abort merge (restore to pre-merge state)",
        "conflict_opt_ours": "[m] Keep MY local version for a file",
        "conflict_opt_theirs": "[r] Use REMOTE version for a file",
        "conflict_opt_back": "[b] Back (resolve manually in your editor)",
        "conflict_prompt": "Action [m/r/a/b]: ",
        "conflict_select_file_prompt": "Select file number: ",
        "conflict_resolved_ours": "Kept your local version for [{file}] and marked resolved.",
        "conflict_resolved_theirs": "Applied remote version for [{file}] and marked resolved.",
        "merge_abort_success": "Merge aborted. Repository restored to pre-merge state.",

        # Pre-sync safety guardrails
        "risk_warning_title": "Safety Check Before Sync:",
        "risk_detached_head": "Detached HEAD: You are not on any branch! Please switch or create a branch first.",
        "risk_sensitive_files": "Sensitive/junk files detected (consider adding to .gitignore):",
        "risk_large_files": "Large files (>=10 MB) detected:",
        "risk_continue_prompt": "Continue syncing anyway? (y/n) [Default: n]: ",
        "gui_auto_msg_chip": "✨ Auto",
        "gui_switch_repo_btn": "📁 Switch Repo",
        "gui_conflict_keep_mine": "Keep My Version",
        "gui_conflict_use_remote": "Use Remote Version",
        "gui_risk_confirm_title": "Pre-Sync Safety Warning",
        "gui_risk_ignore_btn": "Add Sensitive Files to .gitignore && Sync",
        "gui_open_remote_web": "🌐 Open Web",
        "gui_no_web_remote": "No GitHub/GitLab/Gitee web URL found for origin.",
        "gui_syncing_btn": "⏳  Syncing...",
        "non_git_gui_prompt": "Current directory is not a Git repository. Initialize one here?",
        "non_git_init_ok": "Git repository initialized successfully!",
        "non_git_init_fail": "Failed to initialize: {error}",

        # Phase 5: Recent repos, Sync preview, Time Machine
        "recent_repos_opt": "[r] Recent Repositories",
        "recent_repos_title": "Recent Repositories:",
        "recent_repos_empty": "No recent repositories recorded yet.",
        "recent_repos_prompt": "Select repo number to switch, or 'b' to return: ",
        "gui_browse_folder": "Browse Folder...",
        "gui_recent_section": "Recent Repositories",
        "sync_preview_clean": "Working tree clean · Up to date",
        "sync_preview_pull": "Pull origin/{branch}",
        "sync_preview_commit": "Commit {count} file(s)",
        "sync_preview_push": "Push to {branch}",
        "sync_preview_local_only": "Local save only",
        "time_machine_revert_btn": "↩️ Revert This Commit (Safe Undo)",
        "time_machine_branch_btn": "🌿 Branch from Here (Safe Copy)",
        "time_machine_branch_prompt": "New branch name from [{commit}]: ",
        "time_machine_revert_confirm": "Create a safe reverse commit to undo [{commit}]?",
        "time_machine_revert_ok": "Safely reverted commit [{commit}] with a new undo commit!",
        "time_machine_revert_fail": "Could not auto-revert cleanly: {error}",
        "time_machine_branch_ok": "Created safe branch [{branch}] from commit [{commit}]!",
        "history_cli_action_prompt": "Action: [r] Revert commit, [b] Branch from commit, or Enter to return: ",

        # Gitignore editor
        "gitignore_title": ".gitignore Quick Editor:",
        "gitignore_current_label": "Current .gitignore contents:",
        "gitignore_empty_file": "(empty — no .gitignore file found)",
        "gitignore_add_prompt": "Enter pattern to add (e.g. *.log, node_modules/, .env): ",
        "gitignore_added": "Added [{pattern}] to .gitignore",
        "gitignore_already_exists": "Pattern [{pattern}] already exists in .gitignore",
        "gitignore_empty_pattern": "Pattern cannot be empty.",

        # Multi-repo comma selection
        "multi_opt_comma": "[1,3,5] Select specific repos by number (comma-separated)",
        "multi_syncing_selected": "Syncing {count} selected repositories...",

        # GUI Specific labels
        "gui_quick_actions": "Quick Actions",
        "gui_tools": "Tools & Settings",
        "gui_terminal_ready": "FoolGit Ready. Click 'One-Click Sync' to commit & push.",
        "gui_commit_placeholder": "Commit message (leave blank for auto timestamp)...",
        "gui_tag_manager": "Tag Manager",
        "gui_remote_manager": "Remote Settings",
        "gui_clean_manager": "Clean Junk Files",
        "gui_diff_viewer": "Diff Viewer",
        "gui_history_viewer": "Commit History",
        "gui_multi_sync": "Batch Multi-Sync",
        "gui_test_conn_btn": "Test Connection",
        "gui_set_origin_btn": "Save Origin URL",
        "gui_new_tag_btn": "New Tag",
        "gui_delete_tag_btn": "Delete Tag",
        "gui_push_tags_btn": "Push All Tags",
        "gui_clean_now_btn": "Clean Files Now",
        "gui_clean_preview_label": "Files to be removed:",
        "gui_diff_mode_unstaged": "Unstaged Changes",
        "gui_diff_mode_staged": "Staged Changes",
        "gui_diff_select_file": "All Files",
        "gui_discard_selected_btn": "Discard Selected File",
        "gui_select_file_hint": "Select a file to discard its changes:",

        # GUI new features
        "gui_stash_manager": "Stash Manager",
        "gui_gitignore_editor": ".gitignore Editor",
        "gui_branch_manager": "Branch Manager",
        "gui_amend_commit": "Edit Last Commit",
        "gui_conflict_rescue": "Conflict Rescue",
        "gui_stash_list_label": "Saved stash entries:",
        "gui_stash_apply_btn": "Apply Selected",
        "gui_stash_drop_btn": "Delete Selected",
        "gui_amend_prompt": "Enter new commit message:",
        "gui_amend_btn": "Save New Message",
        "gui_gitignore_content_label": "Current .gitignore:",
        "gui_gitignore_add_btn": "Add Pattern",
        "gui_gitignore_pattern_placeholder": "e.g. *.log, node_modules/, .env",
        "gui_branch_list_label": "Local branches:",
        "gui_branch_switch_btn": "Switch to Selected",
        "gui_branch_create_btn": "Create New Branch",
        "gui_branch_delete_btn": "Delete Branch",
        "gui_new_branch_placeholder": "New branch name...",
        "gui_commit_chip_feat": "feat:",
        "gui_commit_chip_fix": "fix:",
        "gui_commit_chip_docs": "docs:",
        "gui_commit_chip_chore": "chore:",
        "gui_commit_chip_refactor": "refactor:",

        # Sprint C: diagnose_remote_error
        "diag_ssh_key": (
            "Tip: SSH key not found or not authorized. "
            "Check your SSH agent (`ssh-add ~/.ssh/id_rsa`) or switch to an HTTPS remote URL."
        ),
        "diag_https_token": (
            "Tip: HTTPS authentication failed. Create a GitHub/GitLab Personal Access Token "
            "and store it in your OS keychain, or run `gh auth login`."
        ),
        "diag_network": (
            "Tip: Cannot reach the remote host. "
            "Check your internet connection, proxy settings, or VPN status."
        ),

        # Sprint C: sync exclude_paths
        "sync_excluded_files": "Excluded from this commit (kept on desk): {files}",

        # Sprint C: Reflog recovery
        "reflog_title": "Emergency Recovery — Lost Commit Finder:",
        "reflog_opt_recover": "[Enter number] Recover — create a safe new branch from that point",
        "reflog_prompt": "Select recovery point [b to return]: ",
        "reflog_branch_prompt": "New branch name for recovery: ",
        "reflog_recover_ok": "Recovery branch [{branch}] created from [{hash}]! Switch to it now.",
        "recover_bad_args": "Recovery hash and branch name are required.",
        "reflog_empty": "No reflog entries found (fresh repo or git reflog disabled).",

        # Sprint C: GUI dark confirm dialog
        "gui_dark_confirm_yes": "Confirm",
        "gui_dark_confirm_no": "Cancel",

        # Sprint C: sync exclude prompt
        "sync_exclude_prompt": "Exclude any file from this commit? Enter path or leave blank: ",
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
        "undo_title": "后悔药（选一颗吃下去）：",
        "undo_opt_all": "🧼 擦掉还没保存的修改（桌面彻底还原到上次快照）",
        "undo_opt_commit": "⏪ 拆掉刚才拍的快照（取消提交，但改动的文件全保留）",
        "undo_opt_file": "📄 只擦掉某一个文件的改动（其余文件不受影响）",
        "undo_opt_amend": "✏️ 给刚才的快照改个名字（修改上次提交说明）",
        "undo_prompt": "请选择要吃的后悔药 [1/2/3/4, b 返回]: ",
        "discard_all_confirm": "确定要彻底放弃所有未提交的代码吗？该操作不可逆！(输入 y 确认): ",
        "discard_all_success": "已经丢弃所有未提交修改，工作区已恢复为干净状态！",
        "discard_file_success": "已经丢弃文件 [{target}] 的所有本地改动。",
        "discard_file_prompt": "请输入要丢弃修改的文件路径: ",
        "discard_file_no_changes": "当前没有已修改、已暂存或未跟踪的文件。",
        "discard_file_select_prompt": "请输入要丢弃修改的文件编号 [b 返回]: ",
        "discard_file_confirm": "确定放弃 [{target}] 的所有改动吗？(y/n): ",
        "uncommit_success": "成功撤回上一次提交！代码完整保留在工作区中。",
        "uncommit_failed": "撤回失败 (可能当前仓库只有一次提交): {error}",
        "cancelled": "已取消操作。",

        # Action: Branch
        "branch_title": "平行宇宙（分支沙盒管理）：",
        "local_branches": "你当前拥有的平行宇宙:",
        "current_branch_mark": "(当前所在)",
        "branch_opt_switch": "[输入数字] 穿越到对应平行宇宙",
        "branch_opt_new": "[n] 裂变一个新平行宇宙（互不干扰的安全实验区）",
        "branch_opt_delete": "[d] 销毁某个平行宇宙",
        "branch_delete_prompt": "请输入要删除的分支名称: ",
        "branch_delete_confirm": "是否强制删除分支 [{branch}]？(y/n) [默认 n]: ",
        "branch_delete_success": "分支 [{branch}] 已成功删除。",
        "branch_delete_failed": "删除分支失败: {error}",
        "branch_cannot_delete_current": "无法删除当前分支 [{branch}]，请先切换到其他分支。",
        "branch_prompt": "请选择或输入操作: ",
        "new_branch_prompt": "请输入新分支名称 (如: dev, feat-auth): ",
        "switch_success": "已成功切换到分支 [{branch}]。",
        "create_branch_success": "成功创建并切换到新分支 [{branch}]！",

        # Action: Stash
        "stash_title": "临时储物柜（先锁起来去忙急事，稍后原样取回）：",
        "stash_opt_save": "🔒 锁进储物柜（把没写完的改动存进去，桌面瞬间变干净）",
        "stash_opt_pop": "🔓 取出上次锁的东西（把刚才存的改动原样拿回桌面）",
        "stash_opt_list": "🧳 看看柜子里存了啥（偷看内容、取回或扔掉）",
        "stash_prompt": "请选择储物柜操作: ",
        "stash_note_prompt": "可选给这条存档贴个标签 (直接回车默认时间): ",
        "stash_clean_nothing": "桌面本来就是干净的，不需要往储物柜里存东西。",
        "stash_saved": "改动已安全锁进临时储物柜！桌面已还原干净。",
        "stash_popped": "已从储物柜取出改动并放回你的桌面！",
        "stash_empty": "临时储物柜里空空如也。",
        "stash_applied": "已将 [{ref}] 复制放回桌面（储物柜里仍保留一份备份）。",
        "stash_dropped": "已扔掉储物柜条目 [{ref}]。",
        "stash_list_title": "临时储物柜里的存档清单:",
        "stash_list_empty": "储物柜里没有任何存档。",
        "stash_list_prompt": "输入编号查看/操作，或输入 b 返回: ",
        "stash_entry_opt_peek": "[p] 偷看一眼（看看里面到底存了哪些改动）",
        "stash_entry_opt_apply": "[a] 拿回桌面（储物柜里保留备份）",
        "stash_entry_opt_drop": "[d] 扔掉这条存档",
        "stash_entry_opt_back": "[b] 返回储物柜清单",
        "stash_entry_prompt": "请选择操作 [p/a/d/b]: ",

        # Action: History & Clean & Tag & Remote & Diff
        "history_title": "时光机（历史快照相册）：",
        "history_menu_title": "时光机（历史快照相册）：",
        "no_history": "还没有拍过任何快照。",
        "history_prompt_inspect": "输入快照编号 [1-{count}] 查看详情或穿越，直接回车返回: ",
        "history_commit_detail_title": "快照详情 [{commit}]:",
        "history_cli_action_prompt": "时光机: [b] 穿越并开新宇宙(安全副本), [c] 对比现在桌面, [r] 安全抵消这次改动, 回车返回: ",
        "history_cli_compare_title": "快照 [{commit}] 与你当前桌面的差异:",
        "history_cli_compare_clean": "你当前的桌面和快照 [{commit}] 完全一模一样！",
        "sync_preview_label": "下一步预览",

        # Hardening, Onboarding, Auto-Locker Pull & CLI Purity
        "git_timeout_error": "Git 命令执行超时（超过 {seconds} 秒，请检查网络或认证状态）。",
        "identity_missing_title": "首次拍照署名设置（仅需一次）:",
        "identity_missing_desc": "拍照存档前，需要告诉 Git 你的名字和邮箱。",
        "identity_name_prompt": "请输入你的署名 (例如 Alice): ",
        "identity_email_prompt": "请输入你的邮箱 (例如 alice@example.com): ",
        "identity_invalid": "署名和邮箱不能为空。",
        "identity_saved": "署名身份已保存 ({name} <{email}>)！",
        "identity_skipped": "已跳过署名设置，未设置署名时可能无法提交快照。",
        "pull_blocked_local": "本地有未保存改动会与云端更新冲突，拉取被安全拦截。",
        "pull_auto_locker_prompt": "开启自动储物柜拉取？输入 [l] 锁进储物柜 → 拉取 → 取出恢复，回车取消: ",
        "pull_auto_locker_step_save": "第 1/3 步：正在把本地未保存改动锁进临时储物柜...",
        "pull_auto_locker_step_pull": "第 2/3 步：正在从云端下载最新更新...",
        "pull_auto_locker_step_pop": "第 3/3 步：正在从储物柜取回你的改动...",
        "pull_auto_locker_pop_conflict": "云端更新已下载，但取回本地改动时与新代码产生重叠，请使用冲突急救！",
        "not_git_error": "❌ 当前目录不是 Git 仓库。",
        "custom_running": "🚀 正在执行: {cmd}",
        "custom_ok": "✅ 执行成功",
        "custom_failed": "❌ 执行失败",
        "feature_not_found": "未找到功能项 [{id}]。",
        "select_option_prompt": "请选择操作: ",
        "select_number_back_prompt": "请输入编号 [b 返回]: ",
        "non_git_select_prompt": "请选择 [1/2, q 退出]: ",
        "init_ok_msg": "🎉 仓库初始化成功！正在进入面板...",
        "init_fail_msg": "❌ 初始化失败: {error}",
        "cloning_msg": "正在克隆 {url} ...",
        "clone_ok_msg": "🎉 克隆成功！",
        "clone_fail_msg": "❌ 克隆失败: {error}",
        "no_repos_found": "当前及子目录下未发现任何 Git 仓库。",
        "gui_refresh_btn": "🔄 刷新状态",
        "gui_create_pr_btn": "🔀 发起 PR",
        "conflict_banner_cli": "[!] 冲突急救（发现 {count} 个冲突文件等待处理！）",
        "conflict_files_status": "存在冲突待解决的文件:",
        "risk_ignore_continue_prompt": "[i] 将敏感文件加入 .gitignore 并同步，[y] 强制继续，或 [n] 取消 [默认 n]: ",
        "commit_smart_hint": "直接回车将使用智能摘要: {msg}",
        "commit_prefix_hint": "快捷标签: [1] feat:  [2] fix:  [3] docs:  [4] chore:  (也可直接输入说明)",
        "commit_prefix_note_prompt": "请输入 '{prefix} ' 后的说明 (直接回车自动补全): ",
        "pr_available_hint": "🔀 发起 PR / 分支对比链接: {url}",
        "pr_open_prompt": "立即在浏览器中打开发起 PR 页面？(y/n) [默认 n]: ",
        "pr_not_feature_branch": "当前处于主分支，请先切换到功能分支后再发起 PR。",
        "opened_in_browser": "🌐 已在默认浏览器打开: {url}",
        "history_more_lines": "  ... (共 {total} 行)",

        "clean_title": "清理未跟踪垃圾文件:",
        "clean_preview_title": "以下未跟踪的文件或目录将被彻底删除:",
        "clean_confirm": "确定要清理所有未跟踪的文件与临时生成目录吗？(输入 y 确认): ",
        "clean_success": "清理完成！工作区已移除所有未跟踪文件。",
        "clean_nothing": "当前没有未跟踪的垃圾文件，工作区很干净！",

        "tag_title": "版本标签管理 (Release Tag):",
        "tag_opt_list": "[1] 查看已有的全部版本标签",
        "tag_opt_create": "[2] 打新版本标签 (可选同步推送远端)",
        "tag_opt_delete": "[3] 删除指定的标签 (本地 / 远端)",
        "tag_opt_push_all": "[4] 推送所有本地标签到远端 (git push --tags)",
        "tag_prompt": "请选择标签操作 [1/2/3/4, b 返回]: ",
        "tag_name_prompt": "请输入新版本标签名称 (如 v1.0.0): ",
        "tag_msg_prompt": "可选输入版本说明 (直接回车默认与标签同名): ",
        "tag_push_prompt": "是否同步将该标签推送到远程仓库？(y/n) [默认 y]: ",
        "tag_created": "成功创建本地标签 [{tag}]！",
        "tag_pushed": "标签 [{tag}] 已成功推送到远程仓库！",
        "tag_deleted": "标签 [{tag}] 删除成功。",
        "tag_none_found": "当前仓库暂无任何版本标签。",
        "tag_delete_prompt": "请输入要删除的标签名: ",
        "tag_delete_remote_confirm": "是否同时从远端仓库删除该标签？(y/n) [默认 n]: ",
        "tag_push_all_success": "所有本地标签已成功推送到远程仓库！",
        "tag_push_all_failed": "推送标签失败: {error}",

        "remote_title": "关联的远程仓库地址:",
        "remote_none": "当前仓库尚未配置远程仓库 (origin)。",
        "remote_origin_label": "当前远程仓库 (origin): {url}",
        "remote_opt_view": "[1] 查看当前远程仓库配置",
        "remote_opt_set": "[2] 设置或修改 origin 仓库地址",
        "remote_opt_test": "[3] 测试远程仓库网络连通性",
        "remote_opt_open_web": "[4] 在浏览器中打开远程仓库网页",
        "remote_opt_open_pr": "[5] 在浏览器中发起 PR / 对比分支",
        "remote_prompt": "请选择远程操作 [1/2/3/4/5, b 返回]: ",
        "remote_set_prompt": "请输入新的远程仓库 origin 地址: ",
        "remote_set_success": "远程 origin 地址已更新为: {url}",
        "remote_test_success": "远程仓库连接测试成功！网络与权限均正常。",
        "remote_test_failed": "远程仓库连接失败: {error}",
        "remote_testing": "正在测试远程仓库连通性，请稍候...",

        "diff_menu_title": "查看代码差异 (Diff):",
        "diff_opt_unstaged": "[1] 查看工作区未暂存的修改",
        "diff_opt_staged": "[2] 查看已暂存待提交的修改 (--staged)",
        "diff_opt_file": "[3] 查看指定单个文件的代码差异",
        "diff_prompt": "请选择差异对比模式 [1/2/3, b 返回]: ",
        "diff_file_prompt": "请选择要查看差异的文件编号 [b 返回]: ",
        "diff_no_modified_files": "当前没有已修改的文件。",

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

        "preset_gitignore_name": ".gitignore 快速编辑",
        "preset_gitignore_tag": "扩展",
        "preset_gitignore_desc": "快速查看并追加常用的 .gitignore 忽略规则",

        # Amend commit
        "amend_title": "修改上一次提交的说明文字:",
        "amend_prompt": "请输入新的提交说明: ",
        "amend_success": "上一次提交说明已成功修改为: [{msg}]",
        "amend_empty_msg": "提交说明不能为空。",

        # Conflict rescue
        "conflict_title": "检测到 Merge 冲突:",
        "conflict_files_label": "存在冲突的文件:",
        "conflict_opt_abort": "[a] 中止合并 (还原到合并前的干净状态)",
        "conflict_opt_ours": "[m] 为指定文件「保留我的本地版本」",
        "conflict_opt_theirs": "[r] 为指定文件「使用远程版本」",
        "conflict_opt_back": "[b] 返回 (手动在编辑器中解决冲突)",
        "conflict_prompt": "请选择操作 [m/r/a/b]: ",
        "conflict_select_file_prompt": "请输入文件编号: ",
        "conflict_resolved_ours": "已为 [{file}] 保留你的本地版本并标记为已解决。",
        "conflict_resolved_theirs": "已为 [{file}] 应用远程版本并标记为已解决。",
        "merge_abort_success": "合并已中止，仓库已恢复到合并前状态。",

        # Pre-sync safety guardrails
        "risk_warning_title": "同步前安全体检提醒:",
        "risk_detached_head": "游离状态 (Detached HEAD)：当前未处于任何分支，请先切换或新建分支！",
        "risk_sensitive_files": "检测到敏感或系统垃圾文件（建议加入 .gitignore）：",
        "risk_large_files": "检测到超大文件 (>=10 MB)：",
        "risk_continue_prompt": "是否仍要继续同步？(y/n) [默认 n]: ",
        "gui_auto_msg_chip": "✨ 智能摘要",
        "gui_switch_repo_btn": "📁 切换仓库",
        "gui_conflict_keep_mine": "保留我的版本",
        "gui_conflict_use_remote": "使用远程版本",
        "gui_risk_confirm_title": "同步前安全提醒",
        "gui_risk_ignore_btn": "将敏感文件加入 .gitignore 并同步",
        "gui_open_remote_web": "🌐 打开网页",
        "gui_no_web_remote": "未检测到可用的 GitHub/GitLab/Gitee 网页地址。",
        "gui_syncing_btn": "⏳  正在同步...",
        "non_git_gui_prompt": "当前目录不是 Git 仓库，是否立即在此初始化？",
        "non_git_init_ok": "Git 仓库初始化成功！",
        "non_git_init_fail": "初始化失败: {error}",

        # Phase 5: Recent repos, Sync preview, Time Machine
        "recent_repos_opt": "[r] 最近打开的仓库",
        "recent_repos_title": "最近使用过的仓库列表:",
        "recent_repos_empty": "暂无最近打开的仓库记录。",
        "recent_repos_prompt": "输入编号切换仓库，或输入 b 返回: ",
        "gui_browse_folder": "浏览选择文件夹...",
        "gui_recent_section": "最近打开的仓库",
        "sync_preview_clean": "工作区干净 · 已与远端同步",
        "sync_preview_pull": "拉取 origin/{branch}",
        "sync_preview_commit": "提交 {count} 个改动文件",
        "sync_preview_push": "推送至 {branch}",
        "sync_preview_local_only": "仅本地保存",
        "time_machine_revert_btn": "↩️ 安全撤销此提交 (生成反向提交)",
        "time_machine_branch_btn": "🌿 从此版本拉出新分支 (安全副本)",
        "time_machine_branch_prompt": "基于提交 [{commit}] 创建新分支名称: ",
        "time_machine_revert_confirm": "确定要生成一个反向提交来安全撤销 [{commit}] 吗？（不会破坏历史）",
        "time_machine_revert_ok": "已通过新提交安全撤销 [{commit}]！",
        "time_machine_revert_fail": "无法自动无冲突撤销: {error}",
        "time_machine_branch_ok": "已从提交 [{commit}] 安全创建并切换到分支 [{branch}]！",
        "history_cli_action_prompt": "操作: [r] 安全撤销此提交, [b] 从此版本建分支, 或直接回车返回: ",

        # Gitignore editor
        "gitignore_title": ".gitignore 快速编辑:",
        "gitignore_current_label": "当前 .gitignore 文件内容:",
        "gitignore_empty_file": "(空文件 — 未找到 .gitignore)",
        "gitignore_add_prompt": "请输入要添加的规则 (如 *.log、node_modules/、.env): ",
        "gitignore_added": "已将 [{pattern}] 添加到 .gitignore",
        "gitignore_already_exists": "规则 [{pattern}] 已存在于 .gitignore 中",
        "gitignore_empty_pattern": "规则不能为空。",

        # Multi-repo comma selection
        "multi_opt_comma": "[1,3,5] 按编号选择多个仓库 (用逗号分隔)",
        "multi_syncing_selected": "正在同步已选中的 {count} 个仓库...",

        # GUI Specific labels
        "gui_quick_actions": "日常快捷操作",
        "gui_tools": "工具与设置",
        "gui_terminal_ready": "FoolGit 就绪。点击「一键保存并同步」即可提交并推送到远端。",
        "gui_commit_placeholder": "输入提交说明 (留空将自动记录时间)...",
        "gui_tag_manager": "标签管理",
        "gui_remote_manager": "远程仓库设置",
        "gui_clean_manager": "清理垃圾文件",
        "gui_diff_viewer": "代码差异对比",
        "gui_history_viewer": "提交历史明细",
        "gui_multi_sync": "多仓库批量同步",
        "gui_test_conn_btn": "测试连通性",
        "gui_set_origin_btn": "保存 Origin 地址",
        "gui_new_tag_btn": "新建标签",
        "gui_delete_tag_btn": "删除标签",
        "gui_push_tags_btn": "推送全部标签",
        "gui_clean_now_btn": "立即清理文件",
        "gui_clean_preview_label": "将要删除的文件/文件夹:",
        "gui_diff_mode_unstaged": "工作区修改",
        "gui_diff_mode_staged": "暂存区修改",
        "gui_diff_select_file": "全部文件",
        "gui_discard_selected_btn": "丢弃选中文件修改",
        "gui_select_file_hint": "选择要丢弃修改的文件:",

        # GUI new features
        "gui_stash_manager": "暂存箱管理",
        "gui_gitignore_editor": ".gitignore 编辑",
        "gui_branch_manager": "分支管理器",
        "gui_amend_commit": "修改上次提交",
        "gui_conflict_rescue": "冲突急救",
        "gui_stash_list_label": "已保存的暂存条目:",
        "gui_stash_apply_btn": "应用选中条目",
        "gui_stash_drop_btn": "删除选中条目",
        "gui_amend_prompt": "请输入新的提交说明文字:",
        "gui_amend_btn": "保存新说明",
        "gui_gitignore_content_label": "当前 .gitignore 文件:",
        "gui_gitignore_add_btn": "添加规则",
        "gui_gitignore_pattern_placeholder": "如 *.log、node_modules/、.env",
        "gui_branch_list_label": "本地分支列表:",
        "gui_branch_switch_btn": "切换到选中分支",
        "gui_branch_create_btn": "新建并切换分支",
        "gui_branch_delete_btn": "删除选中分支",
        "gui_new_branch_placeholder": "输入新分支名称...",
        "gui_commit_chip_feat": "功能:",
        "gui_commit_chip_fix": "修复:",
        "gui_commit_chip_docs": "文档:",
        "gui_commit_chip_chore": "杂项:",
        "gui_commit_chip_refactor": "重构:",

        # Sprint C: diagnose_remote_error
        "diag_ssh_key": (
            "提示：SSH 密钥未找到或未被授权。"
            "请检查 SSH agent（`ssh-add ~/.ssh/id_rsa`）或改用 HTTPS 仓库地址。"
        ),
        "diag_https_token": (
            "提示：HTTPS 鉴权失败。请在 GitHub/GitLab 创建 Personal Access Token "
            "并存入系统钥匙串，或运行 `gh auth login`。"
        ),
        "diag_network": (
            "提示：无法连接到远端服务器。"
            "请检查网络连接、代理设置或 VPN 是否正常。"
        ),

        # Sprint C: sync exclude_paths
        "sync_excluded_files": "本次未提交（保留在桌面）：{files}",

        # Sprint C: Reflog recovery
        "reflog_title": "紧急找回 — 丢失快照保险箱:",
        "reflog_opt_recover": "[输入序号] 找回 — 从该节点安全拉出新分支",
        "reflog_prompt": "请选择要找回的节点 [b 返回]: ",
        "reflog_branch_prompt": "请输入找回新分支名称: ",
        "reflog_recover_ok": "找回分支 [{branch}] 已从 [{hash}] 成功创建！可立即切换过去查看。",
        "recover_bad_args": "找回需要提供快照哈希与新分支名。",
        "reflog_empty": "未找到任何 reflog 记录（全新仓库或 reflog 已被清空）。",

        # Sprint C: GUI dark confirm dialog
        "gui_dark_confirm_yes": "确定",
        "gui_dark_confirm_no": "取消",

        # Sprint C: sync exclude prompt
        "sync_exclude_prompt": "是否本次排除某个文件不提交？输入路径或直接回车: ",
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
