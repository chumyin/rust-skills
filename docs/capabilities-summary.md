# Rust-Skills Capabilities Summary

> Generated from `scripts/render_repository_artifacts.py`. Do not edit by hand.

## Overview

| Metric | Count |
|--------|-------|
| Total Skill Entrypoints | 40 |
| Background Agents | 11 |
| Slash Commands | 21 |
| Unsafe Rules | 47 |
| Template Files | 9 |

## Skill Topology

- Root router entrypoint: `rust-guru` via the repository root `SKILL.md`
- Core skills: `coding-guidelines`, `rust-guru`, `rust-learner`, `unsafe-checker`
- Meta skills: `m01-ownership`, `m02-resource`, `m03-mutability`, `m04-zero-cost`, `m05-type-driven`, `m06-error-handling`, `m07-concurrency`, `m09-domain`, `m10-performance`, `m11-ecosystem`, `m12-lifecycle`, `m13-domain-error`, `m14-mental-model`, `m15-anti-pattern`
- Domain skills: `domain-cli`, `domain-cloud-native`, `domain-embedded`, `domain-fintech`, `domain-iot`, `domain-ml`, `domain-web`
- Supporting skills: `core-actionbook`, `core-agent-browser`, `core-dynamic-skills`, `core-fix-skill-docs`, `rmcp-mcp`, `rust-call-graph`, `rust-code-navigator`, `rust-daily`, `rust-deps-visualizer`, `rust-refactor-helper`, `rust-skill-creator`, `rust-symbol-analyzer`, `rust-trait-explorer`, `rust-unit-test`

## Hook Routing

The repository uses a Rust-targeted lexical matcher in `hooks/hooks.json` to trigger the forced evaluation hook. The matcher is validated against positive and negative prompt samples by `tests/hook-matcher-test.py`, and the local hook asset is verified by `test-triggers.sh --self-check`.

## Commands

- `achievement`
- `ai-daily`
- `audit`
- `cache-clean`
- `cache-status`
- `clean-crate-skills`
- `crate-info`
- `create-llms-for-skills`
- `create-llms-from-source`
- `create-skills-via-llms`
- `docs`
- `fix-skill-docs`
- `guideline`
- `rust-daily`
- `rust-features`
- `rust-review`
- `skill-index`
- `sync-crate-skills`
- `unsafe-check`
- `unsafe-review`
- `update-crate-skill`

## Agents

- `browser-fetcher`
- `clippy-researcher`
- `crate-researcher`
- `docs-cache`
- `docs-researcher`
- `layer1-analyzer`
- `layer2-analyzer`
- `layer3-analyzer`
- `rust-changelog`
- `rust-daily-reporter`
- `std-docs-researcher`

## Distribution Assets

| Asset | Status |
|-------|--------|
| `LICENSE` | present |
| `.claude/settings.example.json` | present |
| `.claude/hooks/rust-skill-eval-hook.sh` | present |
| `.codex/INSTALL.md` | present |
| `.opencode/INSTALL.md` | present |
| `hooks/hooks.json` | present |
| `README.md` | present |

## Validation Commands

- `python3 scripts/validate_repo.py`
- `python3 tests/hook-matcher-test.py`
- `bash test-triggers.sh --self-check`
- `bash tests/validation/validate-skills.sh`
- `bash scripts/quality-check.sh`

## Repository Lineage

- Canonical upstream reference: `https://github.com/ZhangHanDong/rust-skills`
- Active fork origin: `https://github.com/chumyin/rust-skills`
