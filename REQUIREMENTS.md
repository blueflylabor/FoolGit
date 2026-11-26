# FoolGit Product Strategy, Competitive Differentiation & Roadmap

> **Core Positioning**: Compete with both **heavy enterprise GUIs** (SmartGit, SourceTree, GitKraken) and **hotkey-dense TUIs** (Lazygit, gitui) by doing the **exact opposite** — **radical simplicity, zero Git jargon, 1-click daily workflow, and built-in safety guardrails**.

---

## 1. Competitive Differentiation Matrix: Lazygit vs. SmartGit vs. FoolGit

| Dimension | **Lazygit** (and `gitui` / `tig` TUIs) | **SmartGit** (and `SourceTree` / `GitKraken`) | **FoolGit** (Our Moat) |
| :--- | :--- | :--- | :--- |
| **Target User** | Vim/Neovim power users who already master Git internals | Enterprise release managers & full-time Git admins | **Everyday devs, AI/vibe-coders, students, researchers, beginners** |
| **Learning Curve** | **High** — 50+ single-letter hotkeys across 5 split panes (`a`, `c`, `P`, `x`, `s`, `r`...) | **High** — 40+ toolbar buttons, 6 docked panels, deep right-click menus | **Near Zero** — 1 Hero Action + 5–6 essential cards; numbered CLI (`[1..6]`) |
| **Git Jargon** | Exposes raw Git (`Stage`, `Hunk`, `Rebase`, `Squash`, `Fixup`, `Reflog`) | Exposes raw Git (`Index`, `HEAD`, `Fast-forward`, `Cherry-pick`, `Submodule`) | **Zero Jargon** — "Save & Sync", "Undo / Restore", "Keep My Version / Use Remote" |
| **Daily Save Flow** | Multi-step (`Space` stage → `c` commit → `p` pull → `P` push) | Multi-step (`Stage All` → `Commit` → `Pull` → `Push`) | **1-Click Pipeline** (`Pull → Add → Smart Commit → Push`) |
| **Safety Guardrails** | Minimal — easy to trigger destructive reset/rebase with one wrong key | Weak defaults — easy to commit `.env` / large binaries or get stuck in detached HEAD | **Built-in Guardrails** — warns on large files (`>=10 MB`), `.env`/keys, detached HEAD + 1-click `.gitignore` |
| **Conflict Handling** | Manual hunk/line editor inside TUI | Complex 3-way merge viewer | **3-Button Rescue** — "Keep My Version", "Use Remote Version", or "Abort Merge" |
| **Startup & Footprint** | Fast Go binary (~10ms), terminal-only | Heavy Java JVM / Electron (slow startup, high RAM) | **< 0.2s CLI startup** (`porcelain=v2` single-call) + lightweight dark PyQt6 GUI |
| **Bilingual Purity** | English-centric / partial community translations | English-centric / cluttered menus | **100% Pure EN / ZH** hot-switchable, zero mixed-language strings |

### Key Strategic Insight
- **Lazygit wins on speed**, but loses 80% of developers because it requires memorizing TUI keybindings and Git internals.
- **SmartGit wins on completeness**, but loses 90% of users to cognitive overload and multi-step friction.
- **FoolGit wins the underserved majority**: people who want **Git to behave like Cloud Save with a Safety Net** — fast like a CLI tool, clean like a modern dark app, and safe enough that you can't accidentally break your repo.

---

## 2. Core Design Principles

1. **Choose, Don't Type (能点选，不打字)**
   - Numbered menus in CLI; clickable cards, commit chips, and lists in GUI.
2. **Progressive Disclosure (渐进式暴露)**
   - Factory default = **6 essential actions** (`sync`, `pull`, `status`, `undo`, `branch`, `stash`).
   - Power features (`history`, `diff`, `clean`, `tag`, `remote`, `multi_sync`, `gitignore`) live in the Feature Library (`Settings`) and are opt-in.
3. **100% Pure Bilingual Separation (纯净双语)**
   - English (default) and Simplified Chinese (`zh`), switchable on the fly, zero mixed-language strings.
4. **Safety First (防呆护栏)**
   - Never silently destroy uncommitted work.
   - Warn before committing sensitive/large files or on detached HEAD.
   - Surface merge conflicts immediately with plain recovery actions.
5. **Programmer-Grade Minimalism (极简暗黑美学)**
   - Dark charcoal palette (`#121316` / `#1C1D21`), emerald primary (`#10B981`), crimson danger (`#EF4444`), zero visual clutter.

---

## 3. Completed Milestones (Phases 1–4)

### Phase 1 — Core Simplicity & Purity ✅
- [x] `GitEngine` decoupled from UI (`porcelain=v2` fast status, < 0.2s CLI startup)
- [x] Factory 6-preset default + Feature Library toggle + Custom Git commands
- [x] 100% pure EN/ZH `i18n.py` + persistent `.foolgit/config.json`
- [x] Dark PyQt6 GUI with zero font-alias warnings & live language switching

### Phase 2 — Full Preset Parity & Daily Ergonomics ✅
- [x] Dedicated dark dialogs for Undo (per-file discard, uncommit, amend), Stash (list/apply/drop), Clean (preview), Tag, Remote, Diff (color-coded), History (click-to-inspect), Branch Manager, `.gitignore` Editor, and Multi-Repo Batch Sync.
- [x] Conventional Commit quick chips (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).

### Phase 3 — Anti-SmartGit Safety & Intelligence ✅
- [x] **Smart Commit Message Generator**: Auto-summarize changed files (`update: 3 files (gui.py, core.py, +1 more)`) + `✨ Auto` chip in GUI.
- [x] **Pre-Sync Risk Guardrails**: Detect large files (`>=10 MB`), sensitive/junk files (`.env`, `.pem`, `.key`, `.DS_Store`), and detached HEAD before committing, with 1-click "Add Sensitive Files to .gitignore & Sync".
- [x] **Zero-Jargon Conflict Rescue**: Per-file "Keep My Version" (`--ours`) and "Use Remote Version" (`--theirs`) + "Abort Merge" in both CLI and GUI.
- [x] **Quick Repo Switcher & Short Commit Hash**: Switch folder directly in GUI header; show `repo · 7-char-oid`.

### Phase 4 — Visual Polish & Ergonomics ✅
- [x] **Minimalist Timeline**: 1-column commit dot (`●`) + branch/tag decoration in History Viewer.
- [x] **One-Click Web Link**: Convert `origin` SSH/HTTPS URL and open repository in browser (`🌐 Open Web`).
- [x] **Keyboard & Async Ergonomics**: Press `Enter` in commit field to sync, busy-state button lock, 100% localized non-Git init prompt.

---

## 4. Next-Iteration Development Roadmap (Phases 5–6)

> **Goal for Next Iteration**: Combine Lazygit's *instantaneous project flow* with FoolGit's *zero-friction safety*, without adding a single complex pane.

### Phase 5 — Zero-Friction Daily Flow (Next Sprint 🎯)
1. **Recent Repositories History (`recent_repos` in `config.json`)**
   - *Why*: Lazygit's `recent repos` makes multi-project switching effortless. Right now FoolGit GUI requires browsing folders every time.
   - *Spec*: Persist the last 5–8 opened repo paths in `ConfigManager`; add a quick dropdown/submenu in GUI (`Switch Repo` menu) and CLI (`[r] Recent Repos`).
2. **Pre-Sync Action Preview Pill ("What will happen?")**
   - *Why*: Builds trust without SmartGit's noisy staging pane.
   - *Spec*: Display a subtle 1-line summary under the Sync button (e.g. `Will pull origin/main → commit 3 files → push` or `Nothing to commit · Up to date`).
3. **CLI One-Shot Fast Subcommands (`./foolgit sync`, `./foolgit s`, `./foolgit gui`)**
   - *Why*: Power users occasionally want `./foolgit sync "fix typo"` without entering the interactive menu, while keeping `./foolgit` interactive by default.
   - *Spec*: Extend `cli_entry.py` with optional `sync [msg]`, `pull`, `status`/`s`, `gui` subcommands while preserving < 0.2s startup.
4. **Non-Blocking Remote Freshness Check (`git fetch --dry-run` / lightweight check)**
   - *Why*: Warn users *before* they edit stale code (`↓ 2 updates waiting on remote`), without blocking UI startup.
   - *Spec*: Optional background check on GUI launch / refresh button.
5. **Safe "Time Machine" Restore Point (Revert / Checkout Commit safely)**
   - *Why*: Beginners often ask "How do I go back to yesterday's version?" without understanding `git revert` vs `git reset --hard`.
   - *Spec*: In History Viewer, add a plain `"Restore a copy of this commit"` (`git revert` or create branch at commit) option with clear non-destructive explanation.

### Phase 6 — Collaboration & Distribution (Future)
1. **One-Click Pull Request / Compare Link**
   - When on a non-default branch (e.g. `feat-login` != `main`/`master`), offer `"🔀 Create PR in Browser"` (`https://github.com/user/repo/compare/feat-login?expand=1`).
2. **macOS `.app` Bundle & Homebrew Tap**
   - Package cleanly (`--onedir` + `.app` wrapper / Homebrew formula) so non-technical users can install via `brew install foolgit` without Gatekeeper `--onefile` lag.
3. **Automated Test Suite (`pytest` / `unittest`)**
   - Formalize the temporary-repo integration tests and i18n parity checks into `tests/` with `make test` so every future PR/commit stays regression-free.
