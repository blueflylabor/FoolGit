# 💡 FoolGit (傻瓜式定制 Git 助理)

[English Documentation](README.md) | [简体中文说明](README_zh.md)

> **极简、防呆、纯选择题交互。** 专为日常高频 Git 操作定制，告别繁琐冗长指令与臃肿 GUI 软件。
> **现代程序员黑灰极简风格，PyQt6 桌面版 + 交互式终端 CLI，纯净多语言支持。**

---

## 🌟 设计哲学

对于绝大多数日常开发者和初学者来说：
1. **默认出厂极简**：日常 90% 的场景无非是「一键同步保存」、「拉取更新」、「看改动」、「撤销误改」和「切分支」。出厂只展示最核心的 6 个原子操作。
2. **纯净多语言 (Zero Mixed Language)**：出厂默认英文（English），支持切换为简体中文（Chinese）。**英文模式下 100% 纯英文，中文模式下 100% 纯中文，严禁中英混杂**。语言偏好自动持久化保存。
3. **现代程序员暗色质感 (Dark/Gray Modern Aesthetic)**：
   - GUI 基于 **PyQt6** 打造，采用深灰黑客科技风（Charcoal `#121316` + Card `#1C1D21` + 翡翠绿高亮）。
   - 告别传统臃肿的拓扑树状图，打造如 Raycast / Linear / VS Code 般精致的轻量操作面板。
4. **扩展自由自选**：在「功能库」中一键勾选追加（如查看历史、Diff、清理垃圾文件、Release标签），或者添加专属自定义 Git 命令。

---

## 🚀 快速安装与部署

### 方式一：一键自动化安装脚本 (macOS & Linux 推荐)
在项目根目录下直接运行：
```bash
./install.sh
```
安装脚本会自动：
- 检查系统环境并赋予执行权限。
- 全局链接命令 `foolgit`（CLI 版）与 `foolgit-gui`（PyQt6 桌面版）。
- 在 macOS 上自动生成 `FoolGit.app`，可通过 Spotlight、Launchpad 或 Raycast 随时唤醒！

如需卸载，直接运行：
```bash
./uninstall.sh
```

### 方式二：标准 Python 包安装 (pip)
```bash
# 基础 CLI 版本
pip install -e .

# 包含 PyQt6 GUI 桌面版
pip install -e ".[gui]"
```

### 方式三：手动软链接
```bash
sudo ln -sf $(pwd)/foolgit /usr/local/bin/foolgit
sudo ln -sf $(pwd)/foolgit-gui /usr/local/bin/foolgit-gui
```

---

## 📦 跨平台编译与打包 (Compilation & Packaging)

项目提供了为各大平台独立打包二进制可执行文件与安装包的脚本，使用者**无需预先安装 Python 或任何库**即可原生运行！

---

### ⚡ 1. 独立构建纯净终端 CLI 二进制程序 (重点推荐)
CLI 版完全不依赖任何 GUI 或 Qt 库，编译耗时仅需数秒，产物极小（**约 7 MB**）：

```bash
# 专属 CLI 构建脚本
./scripts/build_cli.sh

# 或使用 Makefile
make cli
```
**生成产物**：
- `dist/foolgit`（单文件独立二进制可执行程序）

**如何将编译产物安装到系统**：
```bash
sudo cp dist/foolgit /usr/local/bin/
# 或安装到当前用户目录:
cp dist/foolgit ~/.local/bin/
```

Windows 下对应：
```cmd
scripts\build_cli.bat
```
生成 `dist\foolgit.exe`。

---

### 🍎 2. macOS 桌面端 GUI 与 DMG 打包
执行：
```bash
./scripts/build_macos.sh
# 或使用 Makefile: make gui
# 或使用通用构建器: python3 scripts/build.py --all
```
构建脚本将自动在 `dist/` 目录下生成：
1. **`dist/foolgit`**：单文件原生终端可执行程序。
2. **`dist/FoolGit.app`**：完整的 macOS 应用 Bundle（可直接双击运行或拖入 `/Applications`）。
3. **`dist/FoolGit-1.0.0-macOS.dmg`**：标准 macOS 拖拽安装镜像包！

---

### 🐧 3. Linux 平台编译打包
```bash
./scripts/build_linux.sh
```
生成：
- `dist/foolgit`（终端独立二进制）
- `dist/foolgit-gui`（GUI 独立二进制）
- `dist/foolgit.desktop`（系统应用菜单图标）

---

### 🪟 4. Windows 平台编译打包
```cmd
scripts\build_windows.bat
```
生成：
- `dist\foolgit.exe`
- `dist\foolgit-gui.exe`

---

### 🧰 5. 开发者 Makefile 常用指令
```bash
make cli       # 独立构建轻量 CLI 二进制程序 (~7MB)
make gui       # 构建 macOS GUI 应用包及 DMG 镜像
make all       # 同时构建 CLI 与 GUI
make install   # 执行系统安装 (install.sh)
make uninstall # 执行系统卸载 (uninstall.sh)
make clean     # 清理 dist/ 与 build/ 缓存
```

---

## 🎨 界面视觉与核心功能

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
