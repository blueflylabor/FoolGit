"""
FoolGit 核心执行引擎
封装 Git 底层命令、状态检测、多语言友好反馈以及多仓库扫描能力。
与 CLI/GUI 视图完全解耦。
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .i18n import t


class GitResult:
    """Git 命令执行结果"""
    def __init__(self, code: int, stdout: str, stderr: str, cmd: str = ""):
        self.code = code
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.cmd = cmd

    @property
    def success(self) -> bool:
        return self.code == 0

    @property
    def output(self) -> str:
        return self.stdout if self.stdout else self.stderr


def run_git(args: List[str], cwd: str = ".") -> GitResult:
    """在指定目录安全执行 git 命令并捕获输出"""
    full_cmd = ["git"] + args
    try:
        proc = subprocess.run(
            full_cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return GitResult(proc.returncode, proc.stdout, proc.stderr, " ".join(full_cmd))
    except Exception as e:
        return GitResult(-1, "", str(e), " ".join(full_cmd))


def is_git_repo(path: str = ".") -> bool:
    """检测指定路径是否处于 Git 仓库工作区内"""
    res = run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return res.success and res.stdout.strip() == "true"


def get_repo_root(path: str = ".") -> Optional[Path]:
    """获取 Git 仓库根目录"""
    res = run_git(["rev-parse", "--show-toplevel"], cwd=path)
    if res.success and res.stdout:
        return Path(res.stdout.strip())
    return None


class GitEngine:
    """单一仓库操作管理器"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = str(get_repo_root(repo_path) or Path(repo_path).resolve())

    def get_info(self) -> Dict[str, Any]:
        """获取仓库当前详细健康状况与状态指标"""
        branch_res = run_git(["branch", "--show-current"], cwd=self.repo_path)
        branch = branch_res.stdout if branch_res.success and branch_res.stdout else "HEAD"

        ahead = 0
        behind = 0
        has_upstream = False
        rev_res = run_git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"], cwd=self.repo_path)
        if rev_res.success:
            parts = rev_res.stdout.split()
            if len(parts) == 2:
                ahead = int(parts[0])
                behind = int(parts[1])
                has_upstream = True

        status_res = run_git(["status", "--porcelain"], cwd=self.repo_path)
        modified_files = []
        untracked_files = []
        staged_files = []

        if status_res.success and status_res.stdout:
            for line in status_res.stdout.splitlines():
                if len(line) < 3:
                    continue
                index_st = line[0]
                work_st = line[1]
                fname = line[3:].strip()
                if index_st == "?" and work_st == "?":
                    untracked_files.append(fname)
                else:
                    if index_st in ["M", "A", "D", "R"]:
                        staged_files.append(fname)
                    if work_st in ["M", "D"]:
                        modified_files.append(fname)

        total_changes = len(modified_files) + len(untracked_files) + len(staged_files)

        remote_res = run_git(["remote", "get-url", "origin"], cwd=self.repo_path)
        remote_url = remote_res.stdout if remote_res.success else ""

        repo_name = Path(self.repo_path).name

        return {
            "name": repo_name,
            "path": self.repo_path,
            "branch": branch,
            "has_upstream": has_upstream,
            "ahead": ahead,
            "behind": behind,
            "is_clean": total_changes == 0,
            "total_changes": total_changes,
            "modified": modified_files,
            "untracked": untracked_files,
            "staged": staged_files,
            "remote_url": remote_url,
        }

    def safe_pull(self) -> Tuple[bool, str]:
        """安全拉取最新代码并给出通俗多语言反馈"""
        info = self.get_info()
        branch = info["branch"]

        if not info["remote_url"]:
            return False, f"⚠️ {t('pull_no_remote')}"

        res = run_git(["pull", "origin", branch], cwd=self.repo_path)
        if res.success:
            if "Already up to date" in res.stdout or "已经是最新" in res.stdout:
                return True, f"✅ {t('pull_up_to_date')}"
            return True, f"✅ {t('pull_success')}\n{res.stdout}"

        err_msg = res.stderr or res.stdout
        if "conflict" in err_msg.lower() or "冲突" in err_msg:
            return False, f"❌ {t('pull_conflict')}"
        if "couldn't find remote ref" in err_msg.lower():
            return False, f"⚠️ {t('pull_no_ref', branch=branch)}"
        return False, f"❌ {t('pull_error', error=err_msg)}"

    def one_click_sync(self, custom_msg: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        一键同步核心流程 (Pull ➔ Add -A ➔ Commit ➔ Push)
        所有步骤日志纯净本地化
        """
        logs = []
        info = self.get_info()
        branch = info["branch"]

        if not info["remote_url"]:
            logs.append(f"⚠️ {t('sync_step_no_remote')}")

        # 1. 安全 Pull
        if info["remote_url"]:
            logs.append(f"▸ {t('sync_step_pull')}")
            pull_ok, pull_msg = self.safe_pull()
            logs.append(pull_msg)
            if not pull_ok and "未建立" not in pull_msg and "does not exist" not in pull_msg:
                return False, logs

        info = self.get_info()

        # 2. 如果工作区是干净的，且没有超前提交，则无需操作
        if info["is_clean"] and info["ahead"] == 0:
            logs.append(f"✨ {t('sync_clean_nothing')}")
            return True, logs

        # 3. Add -A
        if not info["is_clean"]:
            logs.append(f"▸ {t('sync_step_add')}")
            add_res = run_git(["add", "-A"], cwd=self.repo_path)
            if not add_res.success:
                logs.append(f"❌ {t('sync_add_failed', error=add_res.stderr)}")
                return False, logs

            # 4. Commit
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_text = custom_msg.strip() if custom_msg and custom_msg.strip() else f"update: {now_str}"
            logs.append(f"▸ {t('sync_step_commit', msg=commit_text)}")
            commit_res = run_git(["commit", "-m", commit_text], cwd=self.repo_path)
            if not commit_res.success:
                logs.append(f"⚠️ {t('sync_commit_no_new', error=commit_res.stderr or commit_res.stdout)}")
            else:
                logs.append(f"✅ {t('sync_commit_success')}")
        else:
            logs.append(f"▸ {t('sync_already_committed')}")

        # 5. Push
        if info["remote_url"]:
            logs.append(f"▸ {t('sync_step_push', branch=branch)}")
            push_res = run_git(["push", "-u", "origin", branch], cwd=self.repo_path)
            if push_res.success:
                logs.append(f"🎉 {t('sync_push_success')}")
                return True, logs
            else:
                err_text = push_res.stderr or push_res.stdout
                if "rejected" in err_text:
                    logs.append(f"❌ {t('sync_push_rejected')}")
                else:
                    logs.append(f"❌ {t('sync_push_failed', error=err_text)}")
                return False, logs
        else:
            logs.append(f"🎉 {t('sync_local_done')}")
            return True, logs

    def undo_action(self, mode: str, target: Optional[str] = None) -> Tuple[bool, str]:
        """通俗多语言后悔药体系"""
        if mode == "discard_all":
            res1 = run_git(["reset", "--hard", "HEAD"], cwd=self.repo_path)
            res2 = run_git(["clean", "-fd"], cwd=self.repo_path)
            if res1.success:
                return True, f"✅ {t('discard_all_success')}"
            return False, f"❌ {res1.stderr}"

        elif mode == "discard_file":
            if not target:
                return False, "Target file required."
            res = run_git(["checkout", "HEAD", "--", target], cwd=self.repo_path)
            if res.success:
                return True, f"✅ {t('discard_file_success', target=target)}"
            return False, f"❌ {res.stderr}"

        elif mode == "uncommit":
            res = run_git(["reset", "--soft", "HEAD~1"], cwd=self.repo_path)
            if res.success:
                return True, f"✅ {t('uncommit_success')}"
            return False, f"❌ {t('uncommit_failed', error=res.stderr)}"

        return False, "Unknown undo action"

    def list_branches(self) -> List[Dict[str, Any]]:
        """获取所有本地分支及当前选中标记"""
        res = run_git(["branch", "--list"], cwd=self.repo_path)
        branches = []
        if res.success and res.stdout:
            for line in res.stdout.splitlines():
                line = line.strip()
                is_current = line.startswith("*")
                name = line.lstrip("* ").strip()
                branches.append({"name": name, "is_current": is_current})
        return branches

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        """切换到已有分支"""
        res = run_git(["checkout", branch_name], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('switch_success', branch=branch_name)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def create_and_switch_branch(self, new_branch_name: str) -> Tuple[bool, str]:
        """新建并切换到新分支"""
        new_branch_name = new_branch_name.strip()
        if not new_branch_name:
            return False, "Branch name cannot be empty."
        res = run_git(["checkout", "-b", new_branch_name], cwd=self.repo_path)
        if res.success:
            return True, f"🎉 {t('create_branch_success', branch=new_branch_name)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def stash_save(self, note: str = "") -> Tuple[bool, str]:
        """把当前未完成的代码存入暂存箱"""
        now = datetime.now().strftime("%H:%M:%S")
        msg = f"FoolGit: {note.strip() if note else now}"
        res = run_git(["stash", "save", "-u", msg], cwd=self.repo_path)
        if res.success:
            if "No local changes to save" in res.stdout:
                return True, f"✨ {t('stash_clean_nothing')}"
            return True, f"📦 {t('stash_saved')}"
        return False, f"❌ {res.stderr}"

    def stash_pop(self) -> Tuple[bool, str]:
        """从暂存箱取回上一次保存的代码"""
        res = run_git(["stash", "pop"], cwd=self.repo_path)
        if res.success:
            return True, f"📂 {t('stash_popped')}"
        if "No stash entries found" in (res.stderr or res.stdout):
            return False, f"⚠️ {t('stash_empty')}"
        return False, f"❌ {res.stderr or res.stdout}"

    def get_recent_history(self, count: int = 10) -> List[str]:
        """获取最近简明提交流水线"""
        cmd = ["log", f"-n{count}", "--pretty=format:%h|%an|%ar|%s"]
        res = run_git(cmd, cwd=self.repo_path)
        if res.success and res.stdout:
            return res.stdout.splitlines()
        return []

    def get_diff_stat(self) -> str:
        """获取简明改动差异统计"""
        res = run_git(["diff", "--stat"], cwd=self.repo_path)
        return res.stdout if res.success else ""


def scan_multi_repos(base_dir: str = ".", max_depth: int = 3) -> List[Dict[str, Any]]:
    """递归扫描子目录下所有的 Git 仓库并获取其健康状态"""
    base_path = Path(base_dir).resolve()
    repo_dirs = []

    if (base_path / ".git").is_dir():
        repo_dirs.append(base_path)

    for root, dirs, _ in os.walk(base_path):
        rel_depth = len(Path(root).relative_to(base_path).parts)
        if rel_depth >= max_depth:
            dirs.clear()
            continue
        if ".git" in dirs:
            repo_dirs.append(Path(root))
            dirs.remove(".git")

    seen = set()
    results = []
    for rdir in repo_dirs:
        str_path = str(rdir)
        if str_path in seen:
            continue
        seen.add(str_path)
        engine = GitEngine(str_path)
        info = engine.get_info()
        results.append(info)

    return results
