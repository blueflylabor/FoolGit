"""
FoolGit 核心执行引擎
封装 Git 底层命令、状态检测、友好错误翻译以及多仓库扫描能力。
与 CLI/GUI 视图完全解耦。
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


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
        # 分支名
        branch_res = run_git(["branch", "--show-current"], cwd=self.repo_path)
        branch = branch_res.stdout if branch_res.success and branch_res.stdout else "HEAD (游离)"

        # 远程状态 (ahead / behind)
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

        # 文件变动
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

        # 远端 URL
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
        """安全拉取最新代码并给出通俗易懂的中文反馈"""
        info = self.get_info()
        branch = info["branch"]

        if not info["remote_url"]:
            return False, "⚠️ 当前仓库未配置远程仓库 (origin)，无需拉取。"

        res = run_git(["pull", "origin", branch], cwd=self.repo_path)
        if res.success:
            if "Already up to date" in res.stdout or "已经是最新" in res.stdout:
                return True, "✅ 代码已是最新，无需更新。"
            return True, f"✅ 成功拉取远程最新代码！\n{res.stdout}"

        # 错误翻译与防呆诊断
        err_msg = res.stderr or res.stdout
        if "conflict" in err_msg.lower() or "冲突" in err_msg:
            return False, "❌ 拉取失败：与本地代码产生冲突！建议先查看改动或使用【暂存保存】后再拉取。"
        if "couldn't find remote ref" in err_msg.lower():
            return False, f"⚠️ 远端尚未建立 [{branch}] 分支，可直接进行【一键保存并同步】以推送到远端。"
        return False, f"❌ 拉取遇到问题: {err_msg}"

    def one_click_sync(self, custom_msg: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        一键同步核心流程 (Pull ➔ Add -A ➔ Commit ➔ Push)
        返回: (是否完全成功, 步骤日志列表)
        """
        logs = []
        info = self.get_info()
        branch = info["branch"]

        if not info["remote_url"]:
            logs.append("⚠️ 未检测到远程仓库 (origin)，将仅在本地完成提交。")

        # 1. 安全 Pull
        if info["remote_url"]:
            logs.append("▸ 步骤 1/4: 检查并拉取远端更新...")
            pull_ok, pull_msg = self.safe_pull()
            logs.append(pull_msg)
            if not pull_ok and "未建立" not in pull_msg and "未配置" not in pull_msg:
                # 若拉取冲突则中止，防止脏提交
                return False, logs

        # 重新刷新状态
        info = self.get_info()

        # 2. 如果工作区是干净的，且没有超前提交，则无需操作
        if info["is_clean"] and info["ahead"] == 0:
            logs.append("✨ 工作区非常干净，代码已是最新，无需提交或推送！")
            return True, logs

        # 3. Add -A
        if not info["is_clean"]:
            logs.append("▸ 步骤 2/4: 记录所有文件改动 (git add -A)...")
            add_res = run_git(["add", "-A"], cwd=self.repo_path)
            if not add_res.success:
                logs.append(f"❌ 添加文件失败: {add_res.stderr}")
                return False, logs

            # 4. Commit
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_text = custom_msg.strip() if custom_msg and custom_msg.strip() else f"update: {now_str}"
            logs.append(f"▸ 步骤 3/4: 提交本地版本 [{commit_text}]...")
            commit_res = run_git(["commit", "-m", commit_text], cwd=self.repo_path)
            if not commit_res.success:
                logs.append(f"⚠️ 提交未产生新版本: {commit_res.stderr or commit_res.stdout}")
            else:
                logs.append("✅ 本地提交完成！")
        else:
            logs.append("▸ 本地代码无需新提交，检测到有已提交但未推送的内容。")

        # 5. Push
        if info["remote_url"]:
            logs.append(f"▸ 步骤 4/4: 推送改动到远端分支 [{branch}]...")
            push_res = run_git(["push", "-u", "origin", branch], cwd=self.repo_path)
            if push_res.success:
                logs.append("🎉 推送成功！本地代码已与远端完全同步！")
                return True, logs
            else:
                err_text = push_res.stderr or push_res.stdout
                if "rejected" in err_text:
                    logs.append("❌ 推送被拒绝：远端有更新的版本。请先执行【一键拉取最新代码】再试。")
                else:
                    logs.append(f"❌ 推送失败: {err_text}")
                return False, logs
        else:
            logs.append("🎉 本地已完成保存！(由于未配置远程仓库，已跳过推送)")
            return True, logs

    def undo_action(self, mode: str, target: Optional[str] = None) -> Tuple[bool, str]:
        """
        通俗易懂的后悔药体系
        mode:
          - 'discard_all': 丢弃全部未提交修改 (工作区彻底恢复干净)
          - 'discard_file': 丢弃单个指定文件的修改
          - 'uncommit': 撤回刚刚的 commit (回到暂存区，写的代码完全保留)
        """
        if mode == "discard_all":
            # 放弃未暂存与已暂存的所有更改
            res1 = run_git(["reset", "--hard", "HEAD"], cwd=self.repo_path)
            res2 = run_git(["clean", "-fd"], cwd=self.repo_path)
            if res1.success:
                return True, "✅ 已经丢弃所有未提交修改，工作区已恢复为上个版本的干净状态！"
            return False, f"❌ 操作失败: {res1.stderr}"

        elif mode == "discard_file":
            if not target:
                return False, "❌ 请提供要撤销修改的文件名。"
            res = run_git(["checkout", "HEAD", "--", target], cwd=self.repo_path)
            if res.success:
                return True, f"✅ 已经丢弃文件 [{target}] 的所有本地改动。"
            return False, f"❌ 撤销失败: {res.stderr}"

        elif mode == "uncommit":
            # 软回退上一个提交，保留写好的代码
            res = run_git(["reset", "--soft", "HEAD~1"], cwd=self.repo_path)
            if res.success:
                return True, "✅ 成功撤回上一次提交！你写的代码完整保留在工作区中，可以重新修改或再次提交。"
            return False, f"❌ 撤回失败 (可能当前仓库只有一次提交): {res.stderr}"

        return False, "未知操作类型"

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
            return True, f"✅ 已成功切换到分支 [{branch_name}]"
        return False, f"❌ 切换失败: {res.stderr or res.stdout}"

    def create_and_switch_branch(self, new_branch_name: str) -> Tuple[bool, str]:
        """新建并切换到新分支"""
        new_branch_name = new_branch_name.strip()
        if not new_branch_name:
            return False, "分支名称不能为空"
        res = run_git(["checkout", "-b", new_branch_name], cwd=self.repo_path)
        if res.success:
            return True, f"🎉 成功创建并切换到新分支 [{new_branch_name}]！"
        return False, f"❌ 创建分支失败: {res.stderr or res.stdout}"

    def stash_save(self, note: str = "") -> Tuple[bool, str]:
        """把当前未完成的代码存入暂存箱"""
        now = datetime.now().strftime("%H:%M:%S")
        msg = f"FoolGit 暂存: {note.strip() if note else now}"
        res = run_git(["stash", "save", "-u", msg], cwd=self.repo_path)
        if res.success:
            if "No local changes to save" in res.stdout:
                return True, "✨ 当前没有未保存的改动，暂存箱不需要存入。"
            return True, f"📦 代码已安全存入暂存箱！工作区已还原干净。"
        return False, f"❌ 暂存失败: {res.stderr}"

    def stash_pop(self) -> Tuple[bool, str]:
        """从暂存箱取回上一次保存的代码"""
        res = run_git(["stash", "pop"], cwd=self.repo_path)
        if res.success:
            return True, "📂 成功从暂存箱恢复上一次的代码改动！"
        if "No stash entries found" in (res.stderr or res.stdout):
            return False, "⚠️ 暂存箱里空空如也，没有可恢复的存盘。"
        return False, f"❌ 恢复暂存遇到冲突或错误: {res.stderr or res.stdout}"

    def get_recent_history(self, count: int = 10) -> List[str]:
        """获取最近简明提交流水线"""
        cmd = [
            "log",
            f"-n{count}",
            "--pretty=format:%h|%an|%ar|%s",
        ]
        res = run_git(cmd, cwd=self.repo_path)
        if res.success and res.stdout:
            return res.stdout.splitlines()
        return []

    def get_diff_stat(self) -> str:
        """获取简明改动差异统计"""
        res = run_git(["diff", "--stat"], cwd=self.repo_path)
        return res.stdout if res.success else ""


# ─────────────────────────────────────────────────────────────
# 多仓库扫描工具 (继承并现代化 gsyn 功能)
# ─────────────────────────────────────────────────────────────

def scan_multi_repos(base_dir: str = ".", max_depth: int = 3) -> List[Dict[str, Any]]:
    """递归扫描子目录下所有的 Git 仓库并获取其健康状态"""
    base_path = Path(base_dir).resolve()
    repo_dirs = []

    # 1. 检查 base_dir 本身
    if (base_path / ".git").is_dir():
        repo_dirs.append(base_path)

    # 2. 遍历子目录
    for root, dirs, _ in os.walk(base_path):
        rel_depth = len(Path(root).relative_to(base_path).parts)
        if rel_depth >= max_depth:
            dirs.clear()
            continue
        if ".git" in dirs:
            repo_dirs.append(Path(root))
            dirs.remove(".git")  # 避免深入 .git 内部

    # 去重
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
