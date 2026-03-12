# Forced Eval Hook

> How rust-skills forces Rust-specific routing before the assistant answers.

## Purpose

The forced evaluation hook exists to prevent a generic assistant from jumping straight to an implementation answer when a Rust question really needs routing first.

The intended sequence is:

1. Detect that the prompt is Rust-related.
2. Ask the assistant to evaluate relevant skills.
3. Activate the matching skills.
4. Answer with the routed context loaded.

This hook is especially important for cases where a surface fix is technically valid but architecturally wrong, such as ownership or concurrency issues inside a domain-specific system.

## Repository Assets

The hook implementation in this fork is split across two files:

- `hooks/hooks.json`
  Defines the Rust-targeted matcher and points to the local hook script.
- `.claude/hooks/rust-skill-eval-hook.sh`
  Emits the routing instructions that tell the assistant to evaluate and activate relevant skills before answering.

The repository also includes `.claude/settings.example.json` for related runtime permissions used by browser-backed skills.

## Current Flow

```text
User prompt
    ↓
Rust-targeted matcher in hooks/hooks.json
    ↓
Forced evaluation hook script
    ↓
Assistant evaluates matching rust-skills
    ↓
Assistant activates selected skills
    ↓
Assistant answers with routed context
```

## Matcher Design

The matcher in this fork is intentionally narrow.

It looks for Rust-specific signals such as:

- Rust tooling: `Cargo.toml`, `cargo`, `rustc`, `docs.rs`, `crates.io`
- Compiler signals: `E0xxx`, `value moved`, `cannot borrow`
- Core concepts: `ownership`, `lifetime`, `unsafe`, `Send`, `Sync`
- Common ecosystem cues: `tokio`, `serde`, `axum`, `clippy`

It intentionally does **not** use catch-all fragments like `.*`. Earlier versions effectively matched arbitrary prompts, which made the hook fire outside Rust scope and reduced trust in the routing layer.

## Hook Script Contract

The hook script should stay simple and stable:

- tell the assistant to evaluate relevant Rust skills
- require YES/NO reasoning per skill
- require activation before answering
- avoid duplicating the entire routing table already maintained by the skill files

The script in this fork is written to be short, legible, and easy to validate in CI.

## Validation

This fork validates the hook in three layers:

1. `tests/hook-matcher-test.py`
   Checks positive and negative matcher cases.
2. `test-triggers.sh --self-check`
   Verifies that the matcher file and hook script are present and executable.
3. `python3 scripts/validate_repo.py`
   Fails if the hook assets are missing or the matcher drifts out of the validated shape.

These checks run locally and in GitHub Actions CI.

## Operational Notes

- Plugin-style installs can use the repository-local hook asset directly.
- Skills-only installs do not automatically enable hook-based routing.
- The hook is only one layer of control; the `rust-guru` router and the skill descriptions still carry the main routing logic.

## Maintenance Guidance

If the matcher changes, update the tests in `tests/hook-matcher-test.py` in the same change.

If the hook script wording changes, keep the message focused on:

- evaluate
- activate
- answer

Do not turn the hook script into a second copy of the entire documentation set. That duplication is what causes drift.
