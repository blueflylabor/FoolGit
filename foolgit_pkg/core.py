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


def get_repo_root(path: str = ".") -> Optional[Path]:
    """获取 Git 仓库根目录"""
    res = run_git(["rev-parse", "--show-toplevel"], cwd=path)
    if res.success and res.stdout:
        return Path(res.stdout.strip())
    return None


def is_git_repo(path: str = ".") -> bool:
    """检测指定路径是否处于 Git 仓库工作区内 (复用 show-toplevel 减少一次进程调用)"""
    return get_repo_root(path) is not None


class GitEngine:
    """单一仓库操作管理器"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = str(get_repo_root(repo_path) or Path(repo_path).resolve())
        self._cached_remote_url: Optional[str] = None

    def get_remote_url(self) -> str:
        """按需获取远程 origin 地址并缓存，避免每次渲染都调用"""
        if self._cached_remote_url is None:
            remote_res = run_git(["remote", "get-url", "origin"], cwd=self.repo_path)
            self._cached_remote_url = remote_res.stdout if remote_res.success else ""
        return self._cached_remote_url

    def get_remote_web_url(self) -> str:
        """将 SSH/HTTPS 的 origin 地址转换为可直接在浏览器打开的网页链接"""
        raw = self.get_remote_url().strip()
        if not raw:
            return ""
        url = raw
        if url.startswith("git@") and ":" in url:
            host_part, path_part = url[4:].split(":", 1)
            url = f"https://{host_part}/{path_part}"
        elif url.startswith("ssh://git@"):
            url = "https://" + url[len("ssh://git@"):]
        if url.endswith(".git"):
            url = url[:-4]
        return url if url.startswith("http://") or url.startswith("https://") else ""

    def get_info(self) -> Dict[str, Any]:
        """获取仓库当前详细健康状况与状态指标 (使用 porcelain=v2 单次高效解析)"""
        status_res = run_git(["status", "--porcelain=v2", "--branch"], cwd=self.repo_path)

        branch = "HEAD"
        commit_oid = ""
        ahead = 0
        behind = 0
        has_upstream = False
        modified_files = []
        untracked_files = []
        staged_files = []

        if status_res.success and status_res.stdout:
            for line in status_res.stdout.splitlines():
                if line.startswith("# branch.oid "):
                    oid = line[13:].strip()
                    if oid and oid != "(initial)":
                        commit_oid = oid[:7]
                elif line.startswith("# branch.head "):
                    branch = line[14:].strip()
                elif line.startswith("# branch.upstream "):
                    has_upstream = True
                elif line.startswith("# branch.ab "):
                    parts = line[12:].split()
                    for p in parts:
                        if p.startswith("+"):
                            ahead = int(p[1:])
                        elif p.startswith("-"):
                            behind = int(p[1:])
                elif line.startswith("1 ") or line.startswith("2 "):
                    # 1 <XY> ... <path>
                    parts = line.split(maxsplit=8)
                    if len(parts) >= 9:
                        xy = parts[1]
                        fname = parts[8]
                        if xy[0] != ".":
                            staged_files.append(fname)
                        if xy[1] != ".":
                            modified_files.append(fname)
                elif line.startswith("? "):
                    untracked_files.append(line[2:].strip())

        total_changes = len(modified_files) + len(untracked_files) + len(staged_files)
        repo_name = Path(self.repo_path).name

        return {
            "name": repo_name,
            "path": self.repo_path,
            "branch": branch,
            "commit_oid": commit_oid,
            "has_upstream": has_upstream,
            "ahead": ahead,
            "behind": behind,
            "is_clean": total_changes == 0,
            "total_changes": total_changes,
            "modified": modified_files,
            "untracked": untracked_files,
            "staged": staged_files,
            "remote_url": "origin" if has_upstream else self.get_remote_url(),
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
            commit_text = custom_msg.strip() if custom_msg and custom_msg.strip() else self.generate_smart_commit_msg()
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
            target_path = Path(self.repo_path) / target
            if target_path.exists():
                # 检测是否为未跟踪文件
                check = run_git(["ls-files", "--error-unmatch", target], cwd=self.repo_path)
                if not check.success:
                    try:
                        if target_path.is_file() or target_path.is_symlink():
                            target_path.unlink()
                        elif target_path.is_dir():
                            import shutil
                            shutil.rmtree(target_path)
                        return True, f"✅ {t('discard_file_success', target=target)}"
                    except Exception as e:
                        return False, f"❌ {str(e)}"

            # 已跟踪文件：先取消暂存再还原工作区
            run_git(["reset", "HEAD", "--", target], cwd=self.repo_path)
            res = run_git(["checkout", "HEAD", "--", target], cwd=self.repo_path)
            if res.success:
                return True, f"✅ {t('discard_file_success', target=target)}"
            return False, f"❌ {res.stderr or res.stdout}"

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

    def list_stashes(self) -> List[Dict[str, str]]:
        """列出所有暂存条目（索引 + 描述）"""
        res = run_git(["stash", "list", "--pretty=format:%gd|%s"], cwd=self.repo_path)
        stashes = []
        if res.success and res.stdout:
            for line in res.stdout.splitlines():
                if "|" in line:
                    ref, desc = line.split("|", 1)
                    stashes.append({"ref": ref.strip(), "desc": desc.strip()})
                else:
                    stashes.append({"ref": line.strip(), "desc": line.strip()})
        return stashes

    def stash_apply(self, index: int = 0) -> Tuple[bool, str]:
        """应用指定索引的暂存条目（不删除）"""
        ref = f"stash@{{{index}}}"
        res = run_git(["stash", "apply", ref], cwd=self.repo_path)
        if res.success:
            return True, f"📂 {t('stash_applied', ref=ref)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def stash_drop(self, index: int = 0) -> Tuple[bool, str]:
        """删除指定索引的暂存条目"""
        ref = f"stash@{{{index}}}"
        res = run_git(["stash", "drop", ref], cwd=self.repo_path)
        if res.success:
            return True, f"🗑️ {t('stash_dropped', ref=ref)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def amend_commit_message(self, new_msg: str) -> Tuple[bool, str]:
        """修改上一次提交的说明（amend）"""
        new_msg = new_msg.strip()
        if not new_msg:
            return False, t("amend_empty_msg")
        res = run_git(["commit", "--amend", "-m", new_msg], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('amend_success', msg=new_msg)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def get_conflict_files(self) -> List[str]:
        """获取当前 merge 冲突文件列表"""
        res = run_git(["diff", "--name-only", "--diff-filter=U"], cwd=self.repo_path)
        if res.success and res.stdout:
            return [f.strip() for f in res.stdout.splitlines() if f.strip()]
        return []

    def abort_merge(self) -> Tuple[bool, str]:
        """中止当前 merge，恢复到 merge 前状态"""
        res = run_git(["merge", "--abort"], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('merge_abort_success')}"
        return False, f"❌ {res.stderr or res.stdout}"

    def resolve_conflict(self, file_path: str, strategy: str = "ours") -> Tuple[bool, str]:
        """用通俗策略解决单文件冲突: 'ours' (保留本地) 或 'theirs' (使用远端)"""
        if strategy not in ("ours", "theirs"):
            return False, "Invalid conflict resolution strategy."
        flag = "--ours" if strategy == "ours" else "--theirs"
        res = run_git(["checkout", flag, "--", file_path], cwd=self.repo_path)
        if not res.success:
            return False, f"❌ {res.stderr or res.stdout}"
        add_res = run_git(["add", "--", file_path], cwd=self.repo_path)
        if add_res.success:
            key = "conflict_resolved_ours" if strategy == "ours" else "conflict_resolved_theirs"
            return True, f"✅ {t(key, file=file_path)}"
        return False, f"❌ {add_res.stderr or add_res.stdout}"

    def generate_smart_commit_msg(self) -> str:
        """根据当前改动文件自动生成简洁可读的提交说明"""
        info = self.get_info()
        changed = list(dict.fromkeys(info["staged"] + info["modified"] + info["untracked"]))
        if not changed:
            return f"update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        names = [Path(p).name for p in changed[:2]]
        suffix = f", +{len(changed) - 2}" if len(changed) > 2 else ""
        return f"update: {len(changed)} file(s) ({', '.join(names)}{suffix})"

    def check_sync_risks(self, large_mb: int = 10) -> Dict[str, Any]:
        """同步前安全巡检：检测游离 HEAD、超大文件与敏感文件"""
        info = self.get_info()
        detached_head = info["branch"] in ("HEAD", "(detached)")
        changed = list(dict.fromkeys(info["modified"] + info["untracked"] + info["staged"]))
        large_files: List[Tuple[str, float]] = []
        sensitive_files: List[str] = []
        sensitive_names = {".env", ".ds_store", "id_rsa", "id_ed25519"}
        sensitive_exts = {".pem", ".key", ".p12", ".pfx"}
        threshold = large_mb * 1024 * 1024

        for rel in changed:
            full = Path(self.repo_path) / rel
            if not full.exists() or not full.is_file():
                continue
            fname_lower = full.name.lower()
            if fname_lower in sensitive_names or fname_lower.startswith(".env.") or full.suffix.lower() in sensitive_exts:
                sensitive_files.append(rel)
            try:
                size = full.stat().st_size
                if size >= threshold:
                    large_files.append((rel, round(size / (1024 * 1024), 1)))
            except OSError:
                pass

        return {
            "detached_head": detached_head,
            "large_files": large_files,
            "sensitive_files": sensitive_files,
            "has_risk": detached_head or bool(large_files) or bool(sensitive_files),
        }

    def get_gitignore_content(self) -> str:
        """读取仓库根目录的 .gitignore 文件内容"""
        path = Path(self.repo_path) / ".gitignore"
        if path.exists():
            try:
                return path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                return str(e)
        return ""

    def append_to_gitignore(self, pattern: str) -> Tuple[bool, str]:
        """追加一行 pattern 到 .gitignore（若不存在则创建）"""
        pattern = pattern.strip()
        if not pattern:
            return False, t("gitignore_empty_pattern")
        path = Path(self.repo_path) / ".gitignore"
        try:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if pattern in existing.splitlines():
                return True, f"ℹ️ {t('gitignore_already_exists', pattern=pattern)}"
            with open(path, "a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write(pattern + "\n")
            return True, f"✅ {t('gitignore_added', pattern=pattern)}"
        except Exception as e:
            return False, f"❌ {str(e)}"

    def get_recent_history(self, count: int = 10) -> List[str]:
        """获取最近简明提交流水线（含分支/标签装饰）"""
        cmd = ["log", f"-n{count}", "--pretty=format:%h|%an|%ar|%s|%d"]
        res = run_git(cmd, cwd=self.repo_path)
        if res.success and res.stdout:
            return res.stdout.splitlines()
        return []

    def get_diff_stat(self) -> str:
        """获取简明改动差异统计"""
        res = run_git(["diff", "--stat"], cwd=self.repo_path)
        return res.stdout if res.success else ""

    def delete_branch(self, branch_name: str, force: bool = False) -> Tuple[bool, str]:
        """删除指定本地分支"""
        info = self.get_info()
        if branch_name == info["branch"]:
            return False, f"⚠️ {t('branch_cannot_delete_current', branch=branch_name)}"
        flag = "-D" if force else "-d"
        res = run_git(["branch", flag, branch_name], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('branch_delete_success', branch=branch_name)}"
        return False, f"❌ {t('branch_delete_failed', error=res.stderr or res.stdout)}"

    def clean_preview(self) -> List[str]:
        """预览将被清理的未跟踪文件或文件夹"""
        res = run_git(["clean", "-nd"], cwd=self.repo_path)
        items = []
        if res.success and res.stdout:
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                if "Would remove " in line:
                    items.append(line.split("Would remove ", 1)[1].strip())
                elif "remove " in line:
                    items.append(line.split("remove ", 1)[1].strip())
                else:
                    items.append(line)
        return items

    def clean_execute(self) -> Tuple[bool, str]:
        """彻底清理所有未跟踪的文件与目录"""
        res = run_git(["clean", "-fd"], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('clean_success')}"
        return False, f"❌ {res.stderr or res.stdout}"

    def list_tags(self) -> List[str]:
        """获取所有版本标签列表（按创建时间倒序）"""
        res = run_git(["tag", "-l", "--sort=-creatordate"], cwd=self.repo_path)
        if res.success and res.stdout:
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return []

    def create_tag(self, name: str, msg: str = "", push: bool = False) -> Tuple[bool, str]:
        """创建新版本标签（可选推送远端）"""
        name = name.strip()
        if not name:
            return False, "Tag name cannot be empty."
        msg_text = msg.strip() if msg and msg.strip() else name
        res = run_git(["tag", "-a", name, "-m", msg_text], cwd=self.repo_path)
        if not res.success:
            return False, f"❌ {res.stderr or res.stdout}"
        if push:
            pres = run_git(["push", "origin", name], cwd=self.repo_path)
            if not pres.success:
                return True, f"✅ {t('tag_created', tag=name)}\n⚠️ {t('tag_push_all_failed', error=pres.stderr or pres.stdout)}"
            return True, f"🎉 {t('tag_created', tag=name)} & {t('tag_pushed', tag=name)}"
        return True, f"✅ {t('tag_created', tag=name)}"

    def delete_tag(self, name: str, remote: bool = False) -> Tuple[bool, str]:
        """删除本地标签（可选同时从远端删除）"""
        name = name.strip()
        if not name:
            return False, "Tag name cannot be empty."
        res = run_git(["tag", "-d", name], cwd=self.repo_path)
        if not res.success:
            return False, f"❌ {res.stderr or res.stdout}"
        if remote:
            pres = run_git(["push", "origin", "--delete", name], cwd=self.repo_path)
            if not pres.success:
                return True, f"✅ {t('tag_deleted', tag=name)}\n⚠️ Remote delete failed: {pres.stderr or pres.stdout}"
        return True, f"✅ {t('tag_deleted', tag=name)}"

    def push_all_tags(self) -> Tuple[bool, str]:
        """一键推送所有本地标签到远端"""
        res = run_git(["push", "origin", "--tags"], cwd=self.repo_path)
        if res.success:
            return True, f"🎉 {t('tag_push_all_success')}"
        return False, f"❌ {t('tag_push_all_failed', error=res.stderr or res.stdout)}"

    def list_remotes(self) -> List[Dict[str, str]]:
        """获取所有已配置的远程仓库信息"""
        res = run_git(["remote", "-v"], cwd=self.repo_path)
        remotes = []
        if res.success and res.stdout:
            for line in res.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 3:
                    remotes.append({
                        "name": parts[0],
                        "url": parts[1],
                        "type": parts[2].strip("()")
                    })
        return remotes

    def set_remote_origin(self, url: str) -> Tuple[bool, str]:
        """设置或更新 origin 远程仓库地址"""
        url = url.strip()
        if not url:
            return False, "Remote URL cannot be empty."
        remotes_res = run_git(["remote"], cwd=self.repo_path)
        has_origin = "origin" in remotes_res.stdout.split()
        if has_origin:
            res = run_git(["remote", "set-url", "origin", url], cwd=self.repo_path)
        else:
            res = run_git(["remote", "add", "origin", url], cwd=self.repo_path)

        if res.success:
            self._cached_remote_url = url
            return True, f"✅ {t('remote_set_success', url=url)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def test_remote_connection(self) -> Tuple[bool, str]:
        """轻量探测远端网络连通性与读写鉴权"""
        info = self.get_info()
        if not info["remote_url"]:
            return False, f"⚠️ {t('pull_no_remote')}"
        res = run_git(["ls-remote", "--exit-code", "-h", "origin"], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('remote_test_success')}"
        return False, f"❌ {t('remote_test_failed', error=res.stderr or res.stdout)}"

    def get_diff(self, staged: bool = False, file_path: Optional[str] = None, color: bool = False) -> str:
        """获取工作区或暂存区的代码修改差异 (diff)"""
        cmd = ["diff"]
        if color:
            cmd.append("--color=always")
        if staged:
            cmd.append("--staged")
        if file_path:
            cmd.extend(["--", file_path])
        res = run_git(cmd, cwd=self.repo_path)
        return res.stdout if res.success else ""

    def get_commit_detail(self, commit_hash: str) -> str:
        """获取具体某次提交的详细改动与元数据"""
        res = run_git(["show", "--stat", "-p", commit_hash.strip()], cwd=self.repo_path)
        return res.stdout if res.success else res.stderr

    def get_sync_preview(self) -> str:
        """生成同步前的一句话动作预览，让用户心里有底"""
        info = self.get_info()
        branch = info["branch"]
        has_remote = bool(info["remote_url"])
        changes = info["total_changes"]
        ahead = info["ahead"]

        if info["is_clean"] and ahead == 0 and info["behind"] == 0:
            return t("sync_preview_clean")

        steps = []
        if has_remote:
            steps.append(t("sync_preview_pull", branch=branch))
        if changes > 0:
            steps.append(t("sync_preview_commit", count=changes))
        if has_remote and (changes > 0 or ahead > 0):
            steps.append(t("sync_preview_push", branch=branch))
        elif not has_remote and changes > 0:
            steps.append(t("sync_preview_local_only"))

        if not steps:
            return t("sync_preview_clean")
        return " → ".join(steps)

    def fetch_remote_status(self) -> Tuple[bool, int]:
        """后台轻量探测远端更新数量（不修改工作区）"""
        info = self.get_info()
        if not info["remote_url"]:
            return False, 0
        res = run_git(["fetch", "origin", "--quiet"], cwd=self.repo_path)
        if not res.success:
            return False, 0
        updated = self.get_info()
        return True, updated["behind"]

    def revert_commit(self, commit_hash: str) -> Tuple[bool, str]:
        """安全回退指定提交（生成反向新提交，不抹除历史）"""
        commit_hash = commit_hash.strip()
        if not commit_hash:
            return False, "Commit hash required."
        res = run_git(["revert", "--no-edit", commit_hash], cwd=self.repo_path)
        if res.success:
            return True, f"✅ {t('time_machine_revert_ok', commit=commit_hash)}"
        # 若 revert 产生冲突，自动中止保持工作区干净
        run_git(["revert", "--abort"], cwd=self.repo_path)
        return False, f"❌ {t('time_machine_revert_fail', error=res.stderr or res.stdout)}"

    def create_branch_at_commit(self, commit_hash: str, branch_name: str) -> Tuple[bool, str]:
        """基于历史某次提交创建并切换到新分支（安全时光机副本）"""
        commit_hash = commit_hash.strip()
        branch_name = branch_name.strip()
        if not commit_hash or not branch_name:
            return False, "Commit hash and branch name are required."
        res = run_git(["checkout", "-b", branch_name, commit_hash], cwd=self.repo_path)
        if res.success:
            return True, f"🎉 {t('time_machine_branch_ok', branch=branch_name, commit=commit_hash)}"
        return False, f"❌ {res.stderr or res.stdout}"

    def get_discardable_files(self) -> List[Dict[str, str]]:
        """获取所有可丢弃改动的文件清单及状态 (用于序号选择丢弃)"""
        info = self.get_info()
        files = []
        seen = set()
        for f in info["modified"]:
            if f not in seen:
                files.append({"path": f, "status": "M"})
                seen.add(f)
        for f in info["staged"]:
            if f not in seen:
                files.append({"path": f, "status": "A"})
                seen.add(f)
        for f in info["untracked"]:
            if f not in seen:
                files.append({"path": f, "status": "?"})
                seen.add(f)
        return files


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
