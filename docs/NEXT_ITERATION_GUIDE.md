# FoolGit 竞品深度对比、需求落差审计与下一迭代开发指南

> 本文档面向下一次迭代开发（Sprint C）编写，基于当前代码库实测状态（**5,300 行代码**，12 个 `unittest` 回归测试全通过），结合市面主流 Git 工具进行客观对比，给出精确可执行的工程规格书。

---

## 一、市面主流 Git 工具横向深度对比

### 1.1 竞品画像与核心定位对比表

| 维度 | **GitHub Desktop** | **SmartGit / SourceTree** | **Fork / Tower** | **Lazygit / gitui** | **VS Code + GitLens** | **FoolGit (本项目)** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **形态与技术栈** | Electron GUI（单桌面端） | Java JVM / Objective-C+Electron | 原生桌面 GUI（付费） | Go / Rust 终端 TUI | IDE 内置扩展 | **CLI (<0.2s) + 模块化 PyQt6 暗黑 GUI** |
| **目标人群** | 初学者 / GitHub 用户 | 企业发布管理 / 专职 Git 管理员 | 中高级个人开发者 / 团队 | Vim / Neovim 终端极客 | 编辑器重度用户 | **普通开发者 / AI 编程 / 学生 / 科研 / 厌恶复杂度人群** |
| **默认概念露出** | 较简洁，但仍需理解 Changes / History / Fetch / Publish | 极重（Stage/Index/HEAD/Rebase/Submodule/Bisect 全铺开） | 完整暴露分支图、Stashes、Reflog、Interactive Rebase | 5 分栏 + 50+ 单字母热键 + Hunk Stage | 杂糅行内 Blame、时间线、热力图等数十视图 | **0 黑话隐喻**（云存档、后悔药、临时储物柜、平行宇宙、时光机） |
| **日常保存步骤** | 填写 Summary → Commit to main → Push origin (2~3 步) | Stage → Commit → Pull → Push (4 步) | Stage → Commit → Pull → Push (4 步) | `Space` → `c` → `p` → `P` (4 步) | 暂存 → 输入 → 提交 → 同步 (3 步) | **1 步闭环**（同步前体检 → 智能摘要 → 自动 Pull/Commit/Push） |
| **防呆与安全护栏** | 仅提醒推送未跟踪仓库，无大文件/敏感文件/Auto-Locker | 弱默认保护，易误触发强操作 | 有部分确认框，仍依赖人脑判断 | 几乎无防呆，单键误触易 Reset | 无 `.env`/大文件专项提醒 | **内置体检（>=10MB / `.env` / 游离 HEAD）+ 一键加 `.gitignore` + Auto-Locker 拉取** |
| **冲突拯救体验** | 提供外部编辑器打开或简单 ours/theirs | 复杂三方 Merge 对比工具 | 交互式冲突解决器 | 终端内手工挑代码块 | IDE 内联 Accept Current/Incoming | **三键傻瓜急救**（保留我的 / 使用远程 / 中止合并） |
| **多仓库批量巡检** | ❌ 不支持（需手动切） | ✅ 支持但配置繁琐 | ⚠️ 支持多标签但不支持一键全同步 | ❌ 不支持 | ⚠️ Workspace 级且较卡顿 | **✅ 一键扫描并批量/按逗号序号同步多个仓库** |
| **双语纯净度** | 官方仅英文（中文靠社区魔改） | 英文为主 / 菜单繁杂 | 英文为主 | 英文为主 | 依赖插件质量，常混杂术语 | **✅ 100% 纯净 EN / ZH，热切换零混杂** |

### 1.2 客观优劣势诊断（竞品在哪些地方依然比我们强？）

为了指导下一轮有效迭代，必须直面竞品目前仍领先 FoolGit 的地方：

1. **GitHub Desktop 赢在「勾选单个文件保存」与「优雅登录鉴权引导」**：
   - 现状：FoolGit 的 `one_click_sync()` 固定执行 `git add -A`，用户无法在不删除文件的前提下「这次暂不提交某 1 个临时文件」。
   - 现状：FoolGit 加入了 `GIT_TERMINAL_PROMPT=0` 防卡死，但一旦鉴权失败（HTTPS 403 / SSH `Permission denied`），目前只把原始英文 git stderr 抛给用户，**缺少人话修复引导**。
2. **Lazygit / Fork 赢在「多仓库极速扫描」与「Reflog 终极救命」**：
   - 现状：FoolGit `scan_multi_repos()` 使用 `os.walk` 默认遍历所有子目录，遇到前端 `node_modules/`、Python `.venv/`、Rust `target/` 时会产生海量无效遍历，慢数十倍。
   - 现状：一旦新手真的用了 `discard_all` 或删除了有价值的分支，目前 FoolGit 还不能通过 `git reflog` 一键找回。
3. **Fork / GitHub Desktop 赢在「统一视觉弹窗质感」**：
   - 现状：FoolGit 主窗口与业务弹窗已实现暗黑风且拆分为 `foolgit_pkg/gui/`，但部分确认框仍直接调用系统原生 `QMessageBox`（在 macOS 上外观偏传统，与自绘 `#1C1D21` 风格不够一体）；且本轮拆包后尚未在含 PyQt6 环境中跑一轮离线 UI 视觉验收与 `foolgit.spec` 打包测试。

---

## 二、当前代码库架构与需求达成度审计

### 2.1 当前代码资产盘点（实测 5,300 LOC）

```text
FoolGit/
├── REQUIREMENTS.md                 需求总纲与 Sprint A/B 路线
├── docs/NEXT_ITERATION_GUIDE.md    本开发指导文档
├── tests/test_foolgit.py (240 LOC) 12 个自动化 unittest 用例（make test 全通过）
└── foolgit_pkg/
    ├── __init__.py       (5 LOC)   版本号与包元信息
    ├── presets.py        (34 LOC)  6 个出厂默认 + 7 个可扩展功能注册表
    ├── cli_entry.py      (88 LOC)  <0.2s 入口 + 一步子命令 (sync/pull/s/gui)
    ├── config.py         (193 LOC) ~/.foolgit/config.json + recent_repos + 自定义命令
    ├── core.py           (852 LOC) GitEngine 核心、porcelain=v2、体检、储物柜、时光机
    ├── i18n.py           (910 LOC) EN/ZH 纯净双语字典（360+ 键 100% 对等）
    ├── cli.py            (1,004 LOC) 编号交互 CLI + 具象隐喻文案
    └── gui/
        ├── __init__.py   (9 LOC)   导出统一接口
        ├── theme.py      (287 LOC) 暗黑 QSS、图标生成、弹窗/Diff 高亮复用工具
        ├── window.py     (690 LOC) 主窗体、后台线程锁、PR 按钮、Auto-Locker 挂载
        └── dialogs.py    (988 LOC) 11 个业务暗黑弹窗（含储物柜偷看、时光机对比）
```

### 2.2 需求达成与残留缺口矩阵

| 需求域 | 当前完成度 | 已落地能力 | 当前明确缺口（下一迭代必做） |
| :--- | :---: | :--- | :--- |
| **极简启动与日常主线** | 95% | 6 默认项 + `sync`/`pull`/`s` 一步直达 + Preview | 缺少「单次排除某文件后再同步」开关 |
| **防呆与新手保护** | 85% | 首次署名引导、大文件/`.env`/Detached HEAD 体检、Auto-Locker Pull、超時保护 | **缺少鉴权失败人话向导**；缺少 `reflog` 误删分支/丢弃恢复兜底 |
| **多仓库效率** | 75% | 递归扫描、序号/逗号批处理、`recent_repos` | **`scan_multi_repos` 未跳过 `node_modules/.venv/dist/build` 等巨型目录** |
| **CLI 与 i18n 纯净性** | 98% | 主流程与边缘分支全部 `t()` 化、360+ 键对称 | 需补齐新加入的交互向导词条 |
| **GUI 质感与打包分发** | 80% | `gui/` 四模块拆包完成、无字体警告 CSS、支持 PR 直达 | **确认框未统一自绘暗黑组件**；`scripts/build_macos.sh` 与 `foolgit.spec` 需按 `gui/` 包路径复测打包 |
| **代码体积与可维护性** | 80% | `gui.py` 已成功拆分；`core.py` 解耦良好 | `cli.py` (1,004 行) 与 `dialogs.py` (988 行) 后续可按需细化，暂可接受 |

---

## 三、下一迭代开发蓝图（Sprint C —— 精度打磨与超级护城河）

> **迭代目标**：在**绝不增加主界面/主菜单任何多余按钮**的前提下，补齐对比 GitHub Desktop 与 Lazygit 的最后几块拼图，并完成 macOS 打包验证。

### 任务 1：`scan_multi_repos()` 极速目录剪枝 (`core.py`)
- **痛点**：目前扫描工作目录会深入 `node_modules`、`.venv`、`dist` 等无用目录，耗时且卡顿。
- **开发规格**：
  - 在 `core.py` 定义 `_SCAN_SKIP_DIRS = {"node_modules", ".venv", "venv", "__pycache__", "build", "dist", ".pytest_cache", ".mypy_cache", "target", ".idea", ".vscode"}`。
  - 在 `scan_multi_repos()` 遍历 `dirs` 时就地过滤：`dirs[:] = [d for d in dirs if d not in _SCAN_SKIP_DIRS]`，避免递归进入，同时一旦发现 `.git` 立即停止继续向下探测该子仓库的更深子目录（除非需要 submodule，默认普通项目不嵌套）。
- **验收标准**：在包含大型 `node_modules/` 的目录测试中扫描耗时明显降低；`tests/test_foolgit.py` 新增跳过测试目录用例。

### 任务 2：可选「同步排除文件」防漏护栏 (`core.py` + `cli.py`)
- **痛点**：`one_click_sync()` 固定全量打包；新手偶尔只想排除临时测试文件。
- **开发规格**：
  - 为 `GitEngine.one_click_sync(custom_msg=None, exclude_paths: Optional[List[str]] = None)` 增加可选排除参数（若传入，先 `git add -A`，再对排除项执行 `git reset HEAD -- <path>`，保留在本地工作区不提交）。
  - **严格克制原则**：不把它做成 Lazygit 式复杂 Stage 界面！仅在 `cli.py` 风险确认后或当改动文件数 >= 2 时于 `_action_sync` 提供一句可选轻提示（直接回车仍 100% 默认全量同步）。
- **验收标准**：临时仓库测试 `one_click_sync("part", exclude_paths=["scratch.txt"])` 后，`scratch.txt` 仍在工作区保留为未提交状态。

### 任务 3：鉴权失败人话诊断助手 (`core.py` + `cli.py` + `gui/window.py`)
- **痛点**：开启 `GIT_TERMINAL_PROMPT=0` 后，未登录 HTTPS 或未配 SSH Key 时只输出冷冰冰的 `Authentication failed` / `Permission denied (publickey)`。
- **开发规格**：
  - 新增 `GitEngine.diagnose_remote_error(err_text: str) -> Optional[str]`：
    - 识别 `permission denied (publickey)` → 提示检查 SSH Key 或改用 HTTPS 仓库地址；
    - 识别 `could not read username` / `authentication failed` / `403` → 提示配置 GitHub Personal Access Token 或运行 `gh auth login` / macOS Keychain；
    - 识别 `could not resolve host` / `timed out` → 提示检查网络、代理或 VPN。
  - 在 `safe_pull()`、`one_click_sync()` push 失败及 `test_remote_connection()` 中附带人话建议行（全双语 `t()`）。

### 任务 4：Reflog「紧急找回」保险箱 (`core.py` + `cli.py` + `gui/dialogs.py`)
- **痛点**：吃错「彻底擦除（discard_all）」或误删含未合并提交的「平行宇宙分支」后，新手以为代码永远没了。
- **开发规格**：
  - 在 `core.py` 新增：
    - `list_recovery_points(limit: int = 8) -> List[Dict[str, str]]`（解析 `git reflog -n <limit> --date=relative --pretty=format:%h|%gd|%gs|%cr`）；
    - `recover_from_reflog(ref_hash: str, new_branch: str)`（调用 `create_branch_at_commit`，安全拉回新平行宇宙分支，永不破坏当前工作区）。
  - 放在 CLI/GUI **「后悔药（Undo Pills）」弹窗最底部**作为一个安静的救命入口，不占用主菜单位置。

### 任务 5：GUI 视觉统一与打包回归验证 (`gui/` + `foolgit.spec` + `scripts/`)
- **开发规格**：
  1. 在 `gui/theme.py` 增加 `confirm_dark_dialog(parent, title, message)`，统一替代弹窗中风格割裂的原生 `QMessageBox.question`，全部使用暗黑圆角样式 `#1C1D21`。
  2. 检查并在含 `PyQt6` 的环境中执行 `QT_QPA_PLATFORM=offscreen` 启动检查（验证 `foolgit_pkg.gui` 包导入、主窗体渲染、PR 按钮显隐、语言热切换、零 `qt.qpa.fonts` 警告）。
  3. 检查并更新 `foolgit.spec` / `scripts/build_macos.sh` 以确保 PyInstaller `--onedir` 正确打入拆分后的 `foolgit_pkg.gui` 子包及全部数据文件。

---

## 四、下一次会话直接开工清单（Checklist）

- [ ] **Step 1**：检查 `foolgit.spec` 与 `scripts/build_macos.sh` 是否兼容 `foolgit_pkg/gui/` 目录包结构。
- [ ] **Step 2**：在 `core.py` 实现目录剪枝、`exclude_paths`、`diagnose_remote_error` 与 `list_recovery_points`。
- [ ] **Step 3**：在 `i18n.py` 补全 EN/ZH 词条并保持 key 100% 对等。
- [ ] **Step 4**：在 `cli.py` 接入鉴权建议与 Reflog 紧急找回；在 `gui/dialogs.py` 与 `gui/theme.py` 统一暗黑确认框并接入紧急找回。
- [ ] **Step 5**：在 `tests/test_foolgit.py` 增加对应单测并运行 `make test` + PyQt6 offscreen 冒烟验收。
