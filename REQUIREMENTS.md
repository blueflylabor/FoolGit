# FoolGit Product Strategy & Requirements Analysis (Anti-SmartGit Design)

> **Core Positioning**: Compete with complex Git clients (SmartGit, SourceTree, GitKraken) by doing the **exact opposite** — **radical simplicity, zero Git jargon, and built-in safety guardrails**.

---

## 1. Why Complex Git Clients Fail 90% of Users

| Pain Point in SmartGit / SourceTree | FoolGit's Anti-SmartGit Solution |
| :--- | :--- |
| **40+ toolbar buttons & 6 docked panes** | **1 Hero Action ("One-Click Sync") + 5–6 basic cards**. Extra tools stay hidden in Feature Library until explicitly enabled. |
| **Cryptic Git terminology** (`Index`, `Stage`, `HEAD`, `Rebase`, `Fast-forward`, `Reflog`) | **Plain human language**: "Save & Sync", "Undo / Restore", "Stash Box", "Keep My Version / Use Remote Version". |
| **Multi-step daily workflow** (Stage → Commit → Pull → Resolve → Push) | **Single-button pipeline**: Pull → Add all → Commit (auto or smart message) → Push, with clear step-by-step logs. |
| **Fear of irreversible mistakes** | **Built-in guardrails**: Warn on large files (>10 MB) or sensitive files (`.env`, `.key`) before commit; confirm before destructive discards; offer "Undo Last Commit (Keep Code)". |
| **Intimidating 3-way merge conflict UI** | **3-button Conflict Rescue**: "Keep My Version", "Use Remote Version", or "Abort Merge". |
| **Slow, heavy Electron / Java JVM startup** | **Native < 0.2s CLI startup** (`porcelain=v2` single-call parsing) + lightweight dark PyQt6 GUI. |

---

## 2. Core Design Principles

1. **Choose, Don't Type (能点选，不打字)**
   - Numbered menus in CLI; clickable cards, chips, and lists in GUI.
2. **Progressive Disclosure (渐进式暴露)**
   - Factory default = **6 essential actions** (`sync`, `pull`, `status`, `undo`, `branch`, `stash`).
   - Power features (`history`, `diff`, `clean`, `tag`, `remote`, `multi_sync`, `gitignore`) live in the Feature Library (`Settings`) and are opt-in.
3. **100% Pure Bilingual Separation (纯净双语)**
   - English (default) and Simplified Chinese (`zh`), switchable on the fly, zero mixed-language strings.
4. **Safety First (防呆护栏)**
   - Never silently destroy uncommitted work.
   - Warn before committing sensitive/large files.
   - Surface merge conflicts immediately with plain recovery actions.
5. **Programmer-Grade Minimalism (极简暗黑美学)**
   - Dark charcoal palette (`#121316` / `#1C1D21`), emerald primary (`#10B981`), crimson danger (`#EF4444`), zero visual clutter.

---

## 3. Feature Architecture & Roadmap

### Phase 1 — Core Simplicity & Purity (Completed ✅)
- [x] `GitEngine` decoupled from UI (`porcelain=v2` fast status, < 0.2s CLI startup)
- [x] Factory 6-preset default + Feature Library toggle + Custom Git commands
- [x] 100% pure EN/ZH `i18n.py` + persistent `.foolgit/config.json`
- [x] Dark PyQt6 GUI with zero font-alias warnings & live language switching

### Phase 2 — Full Preset Parity & Daily Ergonomics (Completed ✅)
- [x] Dedicated dark dialogs for Undo (per-file discard, uncommit, amend), Stash (list/apply/drop), Clean (preview), Tag, Remote, Diff (color-coded), History (click-to-inspect), Branch Manager, `.gitignore` Editor, and Multi-Repo Batch Sync.
- [x] Conventional Commit quick chips (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).

### Phase 3 — Anti-SmartGit Safety & Intelligence (Current Iteration 🚀)
- [x] **Smart Commit Message Generator**: Auto-summarize changed files (`update: 3 files (gui.py, core.py, +1 more)`) instead of bare timestamps, with one-click `✨ Auto` chip in GUI.
- [x] **Pre-Sync Risk Guardrails**: Detect large files (>10 MB) or sensitive/junk files (`.env`, `.pem`, `.key`, `.DS_Store`) before committing and warn the user.
- [x] **Zero-Jargon Conflict Rescue**: Per-file "Keep My Version" (`--ours`) and "Use Remote Version" (`--theirs`) + "Abort Merge" in both CLI and GUI.
- [x] **Quick Repo Switcher in GUI**: Switch working repository folder directly from the header without restarting.
- [x] **Short Commit Hash Display**: Show current commit OID (`main @ 473e552`) in status & header.

### Phase 4 — Future Roadmap (Planned)
- [ ] **Visual Timeline Graph**: Minimalist 1-column commit dot graph in History Viewer (without SmartGit's noisy 10-column table).
- [ ] **GitHub / GitLab One-Click PR Link**: Detect remote URL and offer "Open Compare / Create PR in Browser".
- [ ] **macOS `.app` & Homebrew Tap**: Zero-config distribution for non-technical users.
