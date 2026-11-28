# FoolGit Product Strategy, Software Engineering Analysis & Roadmap

> **Core Positioning**: Compete with both **heavy enterprise GUIs** (SmartGit, SourceTree, GitKraken) and **hotkey-dense TUIs** (Lazygit, gitui) by doing the **exact opposite** — **radical simplicity, zero Git jargon, 1-click daily workflow, and built-in safety guardrails**.

---

## 1. Competitive Differentiation Matrix: Lazygit vs. SmartGit vs. FoolGit

| Dimension | **Lazygit** (and `gitui` / `tig` TUIs) | **SmartGit** (and `SourceTree` / `GitKraken`) | **FoolGit** (Our Moat) |
| :--- | :--- | :--- | :--- |
| **Target User** | Vim/Neovim power users who already master Git internals | Enterprise release managers & full-time Git admins | **Everyday devs, AI/vibe-coders, students, researchers, beginners** |
| **Learning Curve** | **High** — 50+ single-letter hotkeys across 5 split panes (`a`, `c`, `P`, `x`, `s`, `r`...) | **High** — 40+ toolbar buttons, 6 docked panels, deep right-click menus | **Near Zero** — 1 Hero Action + 5–6 essential cards; numbered CLI (`[1..6]`) |
| **Git Jargon** | Exposes raw Git (`Stage`, `Hunk`, `Rebase`, `Squash`, `Fixup`, `Reflog`) | Exposes raw Git (`Index`, `HEAD`, `Fast-forward`, `Cherry-pick`, `Submodule`) | **Zero Jargon** — "Cloud Save", "Undo Pills", "Temporary Locker", "Parallel Worlds", "Time Machine" |
| **Daily Save Flow** | Multi-step (`Space` stage → `c` commit → `p` pull → `P` push) | Multi-step (`Stage All` → `Commit` → `Pull` → `Push`) | **1-Click Pipeline** (`Pull → Add → Smart Commit → Push`) |
| **Safety Guardrails** | Minimal — easy to trigger destructive reset/rebase with one wrong key | Weak defaults — easy to commit `.env` / large binaries or get stuck in detached HEAD | **Built-in Guardrails** — warns on large files (`>=10 MB`), `.env`/keys, detached HEAD + 1-click `.gitignore` |
| **Conflict Handling** | Manual hunk/line editor inside TUI | Complex 3-way merge viewer | **3-Button Rescue** — "Keep My Version", "Use Remote Version", or "Abort Merge" |
| **Startup & Footprint** | Fast Go binary (~10ms), terminal-only | Heavy Java JVM / Electron (slow startup, high RAM) | **< 0.2s CLI startup** (`porcelain=v2` single-call) + lightweight dark PyQt6 GUI |
| **Bilingual Purity** | English-centric / partial community translations | English-centric / cluttered menus | **100% Pure EN / ZH** hot-switchable, zero mixed-language strings |

---

## 2. Core Design Principles

1. **Choose, Don't Type (能点选，不打字)** — Numbered menus in CLI; clickable cards, commit chips, and lists in GUI.
2. **Progressive Disclosure (渐进式暴露)** — Factory default = **6 essential actions** (`sync`, `pull`, `status`, `undo`, `branch`, `stash`); extra tools stay in Settings until enabled.
3. **Concrete Human Metaphors (超具象人话隐喻)** — *Undo Pills* (后悔药), *Temporary Locker* (临时储物柜), *Parallel Worlds* (平行宇宙), *Time Machine* (时光机).
4. **100% Pure Bilingual Separation (纯净双语)** — English (default) and Simplified Chinese (`zh`), zero mixed-language strings.
5. **Safety First (防呆护栏)** — Never silently destroy uncommitted work; warn on sensitive/large files; surface merge conflicts with plain recovery choices.

---

## 3. Software Engineering & Architecture Analysis

### 3.1 Current Codebase Architecture (~4,834 LOC)

```text
foolgit_pkg/
├── __init__.py     (5 LOC)    Package metadata
├── presets.py      (34 LOC)   Official 6-default + 7-extra preset registry
├── cli_entry.py    (87 LOC)   Fast CLI entrypoint + one-shot subcommands (sync/pull/s/gui)
├── config.py       (193 LOC)  JSON persistence (~/.foolgit/config.json), recent_repos, presets
├── core.py         (745 LOC)  Decoupled GitEngine (porcelain=v2, safety checks, Time Machine)
├── i18n.py         (846 LOC)  338-key pure EN/ZH translation dictionary
├── cli.py          (975 LOC)  Interactive numbered-menu CLI + concrete metaphors
└── gui.py          (1,949 LOC) PyQt6 dark desktop UI + 10+ modal dialogs
```

### 3.2 Engineering Quality Assessment (SDLC Stages)

| SDLC Stage | Current Maturity | Observations |
| :--- | :--- | :--- |
| **Requirements & Domain Model** | **Strong** | Clear Anti-SmartGit / Anti-Lazygit positioning; concrete user-facing metaphors aligned across core, CLI, and i18n. |
| **Architecture & Decoupling** | **Good (CLI/Core), Needs Refactor (GUI)** | `GitEngine` (`core.py`) is cleanly decoupled from `cli.py` and `gui.py`. However, `gui.py` (1,949 LOC) is monolithic. |
| **Reliability & Edge Cases** | **Moderate** | Works smoothly on happy paths, but lacks subprocess timeouts, `GIT_TERMINAL_PROMPT=0`, Git identity onboarding, and `porcelain=v2` `u` (unmerged) / `2` (rename) edge-case handling. |
| **Testing & QA Automation** | **Weak (Gap)** | **No `tests/` directory or `make test` target**; verification relies on ad-hoc scripts. |
| **Packaging & Distribution** | **Moderate** | Fast Python CLI launcher (`./foolgit`, ~0.17s) works well; GUI requires matching PyQt6 Python env; macOS `.app` / Homebrew tap not yet finalized. |

---

## 4. Identified Gaps & Technical Debt (Actionable Audit)

> Concrete weaknesses found in the current codebase to guide the next engineering sprint:

### A. Reliability & Git Edge-Case Gaps (`core.py` / `cli.py`)
1. **No Subprocess Timeout / Non-Interactive Guard**: `run_git()` has no `timeout` and does not set `GIT_TERMINAL_PROMPT=0` — broken SSH/HTTPS auth or slow networks can hang the CLI/GUI indefinitely.
2. **Missing First-Run Git Identity Check**: If a beginner has never run `git config user.name` / `user.email`, `one_click_sync` fails with a cryptic `Author identity unknown` error instead of guiding them to set their name & email once.
3. **Pull Blocked by Local Edits**: When `safe_pull()` fails because local modified files would be overwritten, beginners are stuck. We need an **"Auto-Locker Pull"** flow (automatically lock WIP → Pull → restore WIP).
4. **Custom Command Argument Splitting**: `cli.py` (and `gui.py`) parses custom commands with `.replace("git ", "").split()`, which breaks quoted arguments like `git commit -m "hello world"` (`shlex.split` needed).
5. **`porcelain=v2` Unmerged (`u `) & Rename (`2 `) Lines**: `get_info()` does not count `u ` (unmerged conflict) lines in `total_changes` and does not split `\t` on `2 ` rename entries.

### B. i18n Purity Gaps (`cli.py` / `cli_entry.py`)
1. **Remaining Hardcoded English**: `cli.py` lines ~887–904 (`Init failed`, `Cloning ...`, `No Git repositories found.`, `Select option:`, `Number [b to return]:`) and `cli_entry.py` (`Current directory is not a Git repository.`) are not yet wrapped in `t()`.

### C. Testing & Maintainability Gaps
1. **No Automated Test Suite (`tests/`)**: Need `unittest` / `pytest` covering `core.py` (temp-repo workflows), `config.py`, `i18n.py` (EN/ZH key parity + no hardcoded leak checks), and `cli_entry.py` one-shot commands.
2. **Monolithic `gui.py` (1,949 LOC)**: Before the upcoming **GUI Beautification** sprint, `gui.py` should be split into `gui/theme.py`, `gui/dialogs.py`, and `gui/main_window.py`.

---

## 5. Completed Milestones (Phases 1–5) ✅

- **Phase 1**: Core engine (`porcelain=v2`), 6-preset default + Feature Library, 100% pure EN/ZH `i18n.py`, dark PyQt6 GUI.
- **Phase 2**: Full preset parity across CLI & GUI (Undo, Stash, Clean, Tag, Remote, Diff, History, Branch, `.gitignore`, Multi-Repo).
- **Phase 3**: Smart commit summary (`✨ Auto`), pre-sync risk guardrails (`>=10 MB`, `.env`/keys, detached HEAD), zero-jargon Conflict Rescue (`Keep My Version` / `Use Remote Version` / `Abort`).
- **Phase 4**: One-click Open Web (`🌐`), Enter-to-sync, busy-state lock, decorated history timeline.
- **Phase 5**: `recent_repos` history, sync action preview (`get_sync_preview`), CLI one-shot subcommands (`sync`, `pull`, `s`, `gui`), async remote fetch, Time Machine (`revert_commit` / `create_branch_at_commit`), and concrete beginner metaphors (*Undo Pills*, *Temporary Locker*, *Parallel Worlds*, *Time Machine*).

---

## 6. Next-Iteration Development Backlog (Prioritized)

### Sprint A — CLI & Core Hardening (Completed ✅)
1. [x] **Subprocess Safety (`core.py`)**: Added network/local timeouts + `GIT_TERMINAL_PROMPT=0` env guard; fixed `porcelain=v2` `u ` & `2 ` parsing; switched custom commands to `shlex.split()` via `parse_custom_git_args()`.
2. [x] **First-Run Identity Onboarding (`core.py` + `cli.py` + `gui`)**: Detects missing `user.name`/`user.email` before sync/commit and guides setup in plain language.
3. [x] **Auto-Locker Pull Rescue (`core.py` + `cli.py` + `gui`)**: Detects pull blocked by local edits and offers 1-key **"Lock WIP → Pull → Restore WIP"** (`auto_locker_pull()`).
4. [x] **100% i18n Cleanup (`cli.py` + `cli_entry.py` + `gui`)**: Replaced all remaining hardcoded English strings in non-git, multi-repo, remote test, and one-shot CLI flows with `t()`.
5. [x] **Automated Test Suite (`tests/test_foolgit.py` + `Makefile`)**: Added stdlib `unittest` suite wired to `make test`.

### Sprint B — GUI Modularization, Beautification & Distribution
1. [x] **Modularize `gui.py`** into `foolgit_pkg/gui/` (`theme.py`, `dialogs.py`, `window.py`, `__init__.py`), sharing `create_dark_dialog` & `render_diff_html` helpers and dark scrollbars.
2. [x] **Visual & Metaphor Parity**: Aligned GUI dialogs with CLI metaphors (*Undo Pills*, *Temporary Locker* with live diff peek, *Parallel Worlds*, *Time Machine* with Compare/Branch/Revert) and added one-click `🔀 Create PR` (`get_pr_compare_url()`).
3. [ ] **Distribution**: macOS `.app` (`--onedir`) & Homebrew formula tap for zero-config installation.
