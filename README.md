# 💡 FoolGit (Simple & Foolproof Git Assistant / 傻瓜式定制 Git 助理)

> **极简、防呆、纯选择题交互。** 专为日常高频 Git 操作定制，告别繁琐冗长指令与臃肿 GUI 软件。
> **Modern Programmer Dark/Gray Theme, PyQt6 & Terminal CLI, Pure English / Pure Chinese.**

---

## 🌟 设计哲学 (Philosophy)

对于绝大多数日常开发者和初学者来说：
1. **默认出厂极简**：日常 90% 的场景无非是「一键同步保存」、「拉取更新」、「看改动」、「撤销误改」和「切分支」。出厂只展示最核心的 6 个原子操作。
2. **纯净多语言 (Zero Mixed Language)**：出厂默认英文（English），支持切换为简体中文（Chinese）。**英文模式下 100% 纯英文，中文模式下 100% 纯中文，严禁中英混杂**。语言偏好自动持久化保存。
3. **现代程序员暗色质感 (Dark/Gray Modern Aesthetic)**：
   - GUI 基于 **PyQt6** 打造，采用深灰黑客科技风（Charcoal `#121316` + Card `#1C1D21` + 翡翠绿高亮）。
   - 告别传统臃肿的拓扑树状图，打造如 Raycast / Linear / VS Code 般精致的轻量操作面板。
4. **扩展自由自选**：在「功能库」中一键勾选追加（如查看历史、Diff、清理垃圾文件、Release标签），或者添加专属自定义 Git 命令。

---

## 🚀 快速上手 (Quick Start)

### 1. 运行 GUI 现代化桌面版 (PyQt6)
```bash
# 直接运行 GUI
./foolgit-gui

# 或者通过 foolgit 参数启动
./foolgit --gui
```
> 点击右上角 `Language` 按钮即可即时在英文与中文之间无感热切换。

### 2. 运行 CLI 终端版
```bash
./foolgit
```

### 3. 配置全局快捷命令 (推荐)
```bash
# 终端版命令 (输入 foolgit 即可使用)
sudo ln -sf $(pwd)/foolgit /usr/local/bin/foolgit

# 桌面 GUI 命令 (输入 foolgit-gui 即可弹出窗口)
sudo ln -sf $(pwd)/foolgit-gui /usr/local/bin/foolgit-gui
```

---

## 🎨 界面视觉与功能区

- **顶部状态卡片 (Header)**：当前仓库名称、分支秒切下拉菜单（支持 `+` 一键新建分支）、状态指示胶囊（干净 / 有修改 / 超前落后指示）、右上角语言切换。
- **核心大动作 (Hero Section)**：**`🚀 One-Click Sync`**，支持可选填写提交信息（留空自动带时间记录），一键完成 `Pull ➔ Add ➔ Commit ➔ Push`。
- **日常快捷操作 (Quick Actions)**：
  - `⬇️ Pull Latest`（一键拉取最新代码）
  - `🔍 View Changes`（查看代码改动详情）
  - `💊 Undo / Discard`（后悔药：放弃未提交修改 / 撤回上次 commit）
  - `📦 Stash / Restore`（暂存未完成代码 / 一键恢复）
- **工具与设置 (Tools & Settings)**：
  - `📜 History`（最近 10 次提交流水线）
  - `🔍 Diff`（代码行级增删高亮对比）
  - `⚙️ Settings`（功能库勾选开关与自定义 Git 命令管理）
- **极简深色控制台 (Terminal Console)**：实时展示 Git 步骤与反馈，异步非阻塞执行，界面丝滑流畅。

---

## 🌐 语言设置与配置持久化

- **默认语言**：英文 (`en`)
- **可选语言**：简体中文 (`zh`)
- **CLI 切换**：在主菜单输入 `+` ➔ 选择 `[4] Interface Language` 即可切换。
- **GUI 切换**：点击右上角语言按钮一键即时切换。
- 配置文件持久化保存在 `~/.foolgit/config.json`（若不可写会自动安全降级）。
