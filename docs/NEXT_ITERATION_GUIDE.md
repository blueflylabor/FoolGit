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
| **防呆与安全护栏** | 仅提醒推送未跟踪仓库，无大文件/敏感文件/Auto-Locker | 弱默认保护，易误触发强操作 | 有部分确认框，仍依赖人脑判断 | 几乎无防呆，单键误触易 Reset | 无 `.env`/大文件专项提醒 | **内置体检（>10MB / `.env` / 游离 HEAD）+ 一键加 `.gitignore` + Auto-Locker 拉取** |
| **冲突拯救体验** | 提供外部编辑器打开或简单 ours/theirs | 复杂三方 Merge 对比工具 | 交互式冲突解决器 | 终端内手工挑代码块 | IDE 内联 Accept Current/Incoming | **三键傻瓜急救**（保留我的 / 使用远程 / 中止合并） |
| **多仓库批量巡检** | ❌ 不支持（需手动切） | ✅ 支持但配置繁琐 | ⚠️ 支持多标签但不支持一键全同步 | ❌ 不支持 | ⚠️ Workspace 级且较卡顿 | **✅ 一键扫描并批量/按逗号序号同步多个仓库** |
| **双语纯净度** | 官方仅英文（中文靠社区魔改） | 英文为主 / 菜单繁杂 | 英文为主 | 英文为主 | 依赖插件质量，常混杂术语 | **✅ 100% 纯净 EN / ZH，热切换零混杂** |

### 1.2 客观优劣势诊断（竞品在哪些地方依然比我们强？）

...（此处保持原文内容）

---

## 二、当前代码库架构与需求达成度审计

...（保持原文内容）

---

## 三、下一迭代开发蓝图（Sprint C —— 精度打磨与超级护城河）

...（保持原文内容）

---

## 四、下一次会话直接开工清单（Checklist）

...（保持原文内容）
