# Repository Hardening Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Stabilize the fork so installation assets, routing hooks, tests, validation scripts, and repository metadata are internally consistent and verifiable.

**Architecture:** Keep the existing skill content model, but harden the repository around it. Replace brittle hand-maintained checks with deterministic validation, tighten hook routing to Rust-specific prompts, and ensure all README-linked distribution assets are present in the repository.

**Tech Stack:** Markdown, shell, Python 3, GitHub Actions

---

### Task 1: Establish a single source of truth for repository validation

**Files:**
- Create: `scripts/repo_manifest.py`
- Create: `scripts/validate_repo.py`
- Modify: `scripts/quality-check.sh`
- Modify: `tests/validation/validate-skills.sh`

**Step 1: Write failing validation expectations**

- Re-run the current validation scripts and capture the known failures:
  - wrong `skills/rust-guru` path assumption
  - missing `tools:` assumptions for agents
  - early exit in `quality-check.sh`

**Step 2: Implement deterministic repository inspection**

- Add a Python manifest generator that computes:
  - skill entrypoint counts
  - command counts
  - agent counts
  - unsafe rule counts
  - required distribution assets

**Step 3: Rewire shell validators to current repository reality**

- Make shell scripts call the new validation logic and report all failures without aborting after the first one.

**Step 4: Verify validation behavior**

- Run:
  - `python3 scripts/validate_repo.py`
  - `bash scripts/quality-check.sh`
  - `bash tests/validation/validate-skills.sh`

### Task 2: Repair the hook system and its tests

**Files:**
- Modify: `hooks/hooks.json`
- Create or modify: `.claude/hooks/rust-skill-eval-hook.sh`
- Modify: `tests/hook-matcher-test.py`
- Modify: `test-triggers.sh`

**Step 1: Confirm failing baseline**

- Re-run:
  - `python3 tests/hook-matcher-test.py`
  - `bash test-triggers.sh`

**Step 2: Tighten matcher semantics**

- Remove catch-all patterns and empty-alternative behavior.
- Keep Rust-specific lexical coverage while ensuring non-Rust prompts do not match.

**Step 3: Restore executable distribution assets**

- Add the missing hook script and make the README-referenced path real.

**Step 4: Rebuild tests**

- Turn `tests/hook-matcher-test.py` into a real executable test with positive and negative cases.
- Make `test-triggers.sh` syntactically valid and safe when `claude` is unavailable.

**Step 5: Verify**

- Run:
  - `python3 tests/hook-matcher-test.py`
  - `bash test-triggers.sh --self-check`

### Task 3: Restore distribution integrity

**Files:**
- Create: `LICENSE`
- Create: `.claude/settings.example.json`
- Modify: `README.md`
- Modify: `metadata.json`
- Modify: `docs/capabilities-summary.md`

**Step 1: Repair README-linked assets**

- Ensure every local file linked from the README exists or remove the link.

**Step 2: Align metadata with repository reality**

- Update maintained counts and repository identity fields using the manifest output.

**Step 3: Reduce misleading claims**

- Clearly distinguish:
  - supported assets
  - optional/manual flows
  - current platform support assumptions

**Step 4: Verify**

- Run:
  - `python3 scripts/validate_repo.py`
  - `rg -n "README-zh|README-ja|settings.example|rust-skill-eval-hook|License" README.md`

### Task 4: Add CI for regression protection

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Define minimum checks**

- Python syntax checks
- Hook matcher test
- Repository validation
- Quality check

**Step 2: Verify locally**

- Run the same commands the workflow will run.

### Task 5: Final verification and delivery

**Files:**
- Review only

**Step 1: Run full verification**

- `python3 scripts/validate_repo.py`
- `python3 tests/hook-matcher-test.py`
- `bash test-triggers.sh --self-check`
- `bash tests/validation/validate-skills.sh`
- `bash scripts/quality-check.sh`

**Step 2: Inspect git isolation**

- `git status --short`
- `git diff --cached --name-only`
- `git diff --cached`

**Step 3: Commit and push**

- Create focused commits for:
  - validation and hook repair
  - distribution assets and docs
  - CI
