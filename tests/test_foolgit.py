"""
FoolGit 自动化回归测试套件 (标准库 unittest，零第三方依赖)
覆盖 i18n 纯净性、ConfigManager、GitEngine 核心与安全护栏、CLI 入口。
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from foolgit_pkg.config import ConfigManager
from foolgit_pkg.core import GitEngine, parse_custom_git_args, run_git, scan_multi_repos, _SCAN_SKIP_DIRS
from foolgit_pkg.i18n import TRANSLATIONS, set_language, t
from foolgit_pkg.presets import ALL_PRESET_IDS, DEFAULT_ACTIVE_IDS, get_preset_info


class TestI18nAndPresets(unittest.TestCase):
    """测试双语词条完整性与预设清单"""

    def test_en_zh_key_parity(self):
        en_keys = set(TRANSLATIONS["en"].keys())
        zh_keys = set(TRANSLATIONS["zh"].keys())
        self.assertEqual(en_keys, zh_keys)
        self.assertGreaterEqual(len(en_keys), 350)

    def test_no_empty_translations(self):
        for lang in ("en", "zh"):
            for k, val in TRANSLATIONS[lang].items():
                self.assertTrue(isinstance(val, str) and val.strip(), f"Empty key {lang}.{k}")

    def test_preset_metadata_localized(self):
        self.assertEqual(len(DEFAULT_ACTIVE_IDS), 6)
        for pid in ALL_PRESET_IDS:
            for lang in ("en", "zh"):
                set_language(lang)
                meta = get_preset_info(pid)
                self.assertFalse(meta["name"].startswith("preset_"), f"Missing name for {pid}")


class TestConfigManager(unittest.TestCase):
    """测试持久化配置、预设开关、自定义命令与最近仓库"""

    def test_config_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            mgr = ConfigManager(cfg_path)
            self.assertEqual(mgr.get_language(), "en")
            self.assertEqual(mgr.get_active_preset_ids(), DEFAULT_ACTIVE_IDS)

            mgr.set_language("zh")
            self.assertEqual(mgr.get_language(), "zh")

            self.assertTrue(mgr.enable_preset("history"))
            self.assertIn("history", mgr.get_active_preset_ids())
            self.assertTrue(mgr.disable_preset("history"))
            self.assertNotIn("history", mgr.get_active_preset_ids())

            cid = mgr.add_custom_command("Status", 'git status -s', "Short status")
            self.assertEqual(len(mgr.get_custom_commands()), 1)
            self.assertTrue(mgr.remove_custom_command(cid))
            self.assertEqual(len(mgr.get_custom_commands()), 0)

            repo_dir = Path(tmp) / "myrepo"
            repo_dir.mkdir()
            mgr.add_recent_repo(str(repo_dir))
            self.assertEqual(mgr.get_recent_repos(), [str(repo_dir.resolve())])

            mgr.reset_to_defaults()
            self.assertEqual(mgr.get_language(), "en")
            self.assertEqual(mgr.get_active_preset_ids(), DEFAULT_ACTIVE_IDS)


class TestGitEngine(unittest.TestCase):
    """测试 GitEngine 核心操作、护栏、储物柜与时光机"""

    def setUp(self):
        set_language("en")
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.repo = self.root / "work"
        self.repo.mkdir()
        run_git(["init"], cwd=str(self.repo))
        run_git(["config", "user.email", "tester@example.com"], cwd=str(self.repo))
        run_git(["config", "user.name", "Tester"], cwd=str(self.repo))
        (self.repo / "main.py").write_text("print('v1')\n", encoding="utf-8")
        run_git(["add", "-A"], cwd=str(self.repo))
        run_git(["commit", "-m", "initial"], cwd=str(self.repo))
        self.engine = GitEngine(str(self.repo))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_parse_custom_git_args_quoted(self):
        args = parse_custom_git_args('git commit -m "hello world" --amend')
        self.assertEqual(args, ["commit", "-m", "hello world", "--amend"])

    def test_identity_check_and_set(self):
        ok, name, email = self.engine.check_git_identity()
        self.assertTrue(ok)
        self.assertEqual(name, "Tester")
        self.assertEqual(email, "tester@example.com")

        ok_set, _ = self.engine.set_git_identity("Alice", "alice@example.com")
        self.assertTrue(ok_set)
        ok2, name2, email2 = self.engine.check_git_identity()
        self.assertTrue(ok2)
        self.assertEqual((name2, email2), ("Alice", "alice@example.com"))

    def test_smart_msg_risks_and_gitignore(self):
        (self.repo / ".env").write_text("TOKEN=123\n", encoding="utf-8")
        (self.repo / "main.py").write_text("print('v2')\n", encoding="utf-8")
        msg = self.engine.generate_smart_commit_msg()
        self.assertIn("2 file(s)", msg)

        risks = self.engine.check_sync_risks()
        self.assertTrue(risks["has_risk"])
        self.assertIn(".env", risks["sensitive_files"])

        ok_ign, _ = self.engine.append_to_gitignore(".env")
        self.assertTrue(ok_ign)
        self.assertIn(".env", self.engine.get_gitignore_content())

    def test_locker_save_peek_apply_drop(self):
        (self.repo / "main.py").write_text("print('wip')\n", encoding="utf-8")
        ok, _ = self.engine.stash_save("wip feature")
        self.assertTrue(ok)
        stashes = self.engine.list_stashes()
        self.assertEqual(len(stashes), 1)
        diff_txt = self.engine.get_stash_diff(0, color=False)
        self.assertIn("wip", diff_txt)
        ok_app, _ = self.engine.stash_apply(0)
        self.assertTrue(ok_app)
        ok_drop, _ = self.engine.stash_drop(0)
        self.assertTrue(ok_drop)
        self.assertEqual(len(self.engine.list_stashes()), 0)

    def test_time_machine_compare_branch_and_revert(self):
        c1 = self.engine.get_recent_history(1)[0].split("|")[0]
        (self.repo / "main.py").write_text("print('v2')\n", encoding="utf-8")
        run_git(["commit", "-am", "second"], cwd=str(self.repo))
        c2 = self.engine.get_recent_history(1)[0].split("|")[0]

        (self.repo / "main.py").write_text("print('v3')\n", encoding="utf-8")
        cmp_diff = self.engine.diff_against_commit(c2, color=False)
        self.assertIn("+print('v3')", cmp_diff)
        run_git(["checkout", "--", "main.py"], cwd=str(self.repo))

        ok_rev, _ = self.engine.revert_commit(c2)
        self.assertTrue(ok_rev)
        self.assertEqual((self.repo / "main.py").read_text(encoding="utf-8"), "print('v1')\n")

        ok_br, _ = self.engine.create_branch_at_commit(c1, "tm-sandbox")
        self.assertTrue(ok_br)
        self.assertEqual(self.engine.get_info()["branch"], "tm-sandbox")

    def test_porcelain_rename_and_unmerged(self):
        # Test rename parsing (porcelain v2 '2 ' entry with tab)
        (self.repo / "renamed.py").write_text("print('v1')\n", encoding="utf-8")
        (self.repo / "main.py").unlink()
        run_git(["add", "-A"], cwd=str(self.repo))
        info = self.engine.get_info()
        self.assertEqual(info["branch"], self.engine.get_info()["branch"])
        self.assertGreaterEqual(info["total_changes"], 1)
        self.assertTrue(any("renamed.py" in f for f in info["staged"]), info)

        # Reset and verify conflict parsing (porcelain v2 'u ' entry)
        run_git(["reset", "--hard", "HEAD"], cwd=str(self.repo))
        curr = self.engine.get_info()["branch"]
        run_git(["checkout", "-b", "side"], cwd=str(self.repo))
        (self.repo / "main.py").write_text("side\n", encoding="utf-8")
        run_git(["commit", "-am", "side"], cwd=str(self.repo))
        run_git(["checkout", curr], cwd=str(self.repo))
        (self.repo / "main.py").write_text("ours\n", encoding="utf-8")
        run_git(["commit", "-am", "ours"], cwd=str(self.repo))
        run_git(["merge", "side"], cwd=str(self.repo))

        conflict_info = self.engine.get_info()
        self.assertIn("main.py", conflict_info["conflicts"])
        self.assertGreaterEqual(conflict_info["total_changes"], 1)
        ok_res, _ = self.engine.resolve_conflict("main.py", "ours")
        self.assertTrue(ok_res)

    def test_remote_web_and_pr_url_and_auto_locker_pull(self):
        bare = self.root / "remote.git"
        run_git(["init", "--bare", str(bare)], cwd=str(self.root))
        main_branch = self.engine.get_info()["branch"]
        run_git(["remote", "add", "origin", str(bare)], cwd=str(self.repo))
        run_git(["push", "-u", "origin", main_branch], cwd=str(self.repo))

        # Clone second copy and push upstream update to test auto_locker_pull
        other = self.root / "other"
        run_git(["clone", str(bare), str(other)], cwd=str(self.root))
        run_git(["config", "user.email", "o@e.com"], cwd=str(other))
        run_git(["config", "user.name", "Other"], cwd=str(other))
        (other / "main.py").write_text("print('remote')\n", encoding="utf-8")
        run_git(["commit", "-am", "remote change"], cwd=str(other))
        run_git(["push", "origin", main_branch], cwd=str(other))

        # Dirty untracked or modified non-conflicting change triggers auto_locker_pull cleanly
        (self.repo / "notes.txt").write_text("local note\n", encoding="utf-8")
        ok_al, _logs = self.engine.auto_locker_pull()
        self.assertTrue(ok_al)
        self.assertTrue((self.repo / "notes.txt").exists())

        # URL conversions
        self.engine.set_remote_origin("git@github.com:org/Repo.git")
        self.assertEqual(self.engine.get_remote_web_url(), "https://github.com/org/Repo")
        self.engine.create_and_switch_branch("feat-ui")
        self.assertEqual(
            self.engine.get_pr_compare_url(),
            "https://github.com/org/Repo/compare/feat-ui?expand=1",
        )


class TestCliEntry(unittest.TestCase):
    """测试 CLI 一键子命令与帮助"""

    def test_cli_help_and_version(self):
        repo_root = Path(__file__).resolve().parent.parent
        res = subprocess.run(
            [sys.executable, "-m", "foolgit_pkg.cli_entry", "-v"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("FoolGit version", res.stdout)

        res_s = subprocess.run(
            [sys.executable, "-m", "foolgit_pkg.cli_entry", "s"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_s.returncode, 0)


if __name__ == "__main__":
    unittest.main()


class TestSprintC(unittest.TestCase):
    """Sprint C 新功能回归测试"""

    def setUp(self):
        set_language("en")
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.repo = self.root / "work"
        self.repo.mkdir()
        run_git(["init"], cwd=str(self.repo))
        run_git(["config", "user.email", "t@e.com"], cwd=str(self.repo))
        run_git(["config", "user.name", "T"], cwd=str(self.repo))
        (self.repo / "main.py").write_text("v1\n", encoding="utf-8")
        run_git(["add", "-A"], cwd=str(self.repo))
        run_git(["commit", "-m", "init"], cwd=str(self.repo))
        self.engine = GitEngine(str(self.repo))

    def tearDown(self):
        self.tmp_dir.cleanup()

    # ── Task 1: scan_multi_repos 剪枝 ───────────────────────────────
    def test_scan_skip_dirs_defined(self):
        """_SCAN_SKIP_DIRS 必须包含 node_modules 和 .venv"""
        from foolgit_pkg.core import _SCAN_SKIP_DIRS
        self.assertIn("node_modules", _SCAN_SKIP_DIRS)
        self.assertIn(".venv", _SCAN_SKIP_DIRS)
        self.assertIn("__pycache__", _SCAN_SKIP_DIRS)

    def test_scan_skips_noise_directories(self):
        """scan_multi_repos 不应进入 node_modules 子仓库"""
        # 创建噪音目录内的 git 仓库（真实扫描应跳过）
        noise = self.root / "node_modules" / "some-pkg"
        noise.mkdir(parents=True)
        run_git(["init"], cwd=str(noise))
        repos = scan_multi_repos(str(self.root), max_depth=4)
        paths = [r["path"] for r in repos]
        self.assertFalse(any("node_modules" in p for p in paths),
                         f"node_modules repo found in results: {paths}")

    def test_scan_finds_real_repo(self):
        """scan_multi_repos 能正常找到真实仓库"""
        repos = scan_multi_repos(str(self.root), max_depth=3)
        paths = [r["path"] for r in repos]
        self.assertTrue(any(str(self.repo) in p or p == str(self.repo) for p in paths),
                        f"Real repo not found in {paths}")

    # ── Task 2: exclude_paths ──────────────────────────────────────
    def test_one_click_sync_exclude_paths(self):
        """sync 时 exclude_paths 对应文件不被提交，仍留在工作区"""
        (self.repo / "keep.py").write_text("temp\n", encoding="utf-8")
        (self.repo / "commit.py").write_text("real\n", encoding="utf-8")
        ok, logs = self.engine.one_click_sync("test exclude", exclude_paths=["keep.py"])
        self.assertTrue(ok, logs)
        # keep.py 仍在工作区（未暂存状态）
        self.assertTrue((self.repo / "keep.py").exists())
        status = run_git(["status", "--porcelain"], cwd=str(self.repo))
        self.assertIn("keep.py", status.stdout)

    # ── Task 3: diagnose_remote_error ──────────────────────────────
    def test_diagnose_ssh_error(self):
        msg = self.engine.diagnose_remote_error("Permission denied (publickey)")
        self.assertIsNotNone(msg)
        self.assertIn("SSH", msg)

    def test_diagnose_https_error(self):
        msg = self.engine.diagnose_remote_error("Authentication failed for 'https://github.com'")
        self.assertIsNotNone(msg)
        self.assertIn("Token", msg.replace("token", "Token"))

    def test_diagnose_network_error(self):
        msg = self.engine.diagnose_remote_error("Could not resolve host: github.com")
        self.assertIsNotNone(msg)
        self.assertTrue(
            any(w in msg.lower() for w in ("network", "internet", "connection", "host")),
            f"Expected network-related hint, got: {msg}"
        )

    def test_diagnose_no_error(self):
        msg = self.engine.diagnose_remote_error("")
        self.assertIsNone(msg)

    # ── Task 4: list_recovery_points / recover_from_reflog ─────────
    def test_list_recovery_points(self):
        """首次提交后 reflog 应至少有一条记录"""
        (self.repo / "main.py").write_text("v2\n", encoding="utf-8")
        run_git(["commit", "-am", "second"], cwd=str(self.repo))
        points = self.engine.list_recovery_points(5)
        self.assertGreaterEqual(len(points), 1)
        self.assertIn("hash", points[0])
        self.assertIn("action", points[0])

    def test_recover_from_reflog(self):
        """recover_from_reflog 能基于 reflog hash 创建新分支"""
        points = self.engine.list_recovery_points(3)
        self.assertTrue(points)
        ok, msg = self.engine.recover_from_reflog(points[0]["hash"], "recovered-branch")
        self.assertTrue(ok, msg)
        branches = [b["name"] for b in self.engine.list_branches()]
        self.assertIn("recovered-branch", branches)

    # ── i18n 新词条对等性 ───────────────────────────────────────────
    def test_sprint_c_i18n_parity(self):
        """Sprint C 新增的所有 i18n key 在 EN/ZH 两节均存在"""
        new_keys = [
            "diag_ssh_key", "diag_https_token", "diag_network",
            "sync_excluded_files", "sync_exclude_prompt",
            "reflog_title", "reflog_opt_recover", "reflog_prompt",
            "reflog_branch_prompt", "reflog_recover_ok",
            "recover_bad_args", "reflog_empty",
            "gui_dark_confirm_yes", "gui_dark_confirm_no",
        ]
        for key in new_keys:
            self.assertIn(key, TRANSLATIONS["en"], f"Missing EN key: {key}")
            self.assertIn(key, TRANSLATIONS["zh"], f"Missing ZH key: {key}")


if __name__ == "__main__":
    unittest.main()
