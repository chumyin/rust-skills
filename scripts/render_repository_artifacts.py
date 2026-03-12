#!/usr/bin/env python3
"""Render generated repository artifacts from the manifest."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from repo_manifest import build_manifest, repo_root

CANONICAL_REPOSITORY = "https://github.com/ZhangHanDong/rust-skills"
FORK_LINEAGE = [
    "https://github.com/actionbook/rust-skills",
    "https://github.com/patricka3125/rust-skills",
]
DESCRIPTION = "Comprehensive Rust learning and development skills for Claude"
AUTHOR = "ZhangHanDong"
LICENSE = "MIT"


def latest_commit_date(root: Path) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or "1970-01-01"


def render_metadata(root: Path | None = None) -> str:
    root = root or repo_root()
    manifest = build_manifest(root)
    skills = manifest["skills"]
    stats = manifest["stats"]
    layer1_skills = [name for name in skills["meta"] if re.match(r"m0[1-7]-", name)]
    layer2_skills = [name for name in skills["meta"] if re.match(r"m(09|1[0-5])-", name)]
    payload = {
        "name": "rust-skills",
        "version": manifest["version"],
        "description": DESCRIPTION,
        "author": AUTHOR,
        "license": LICENSE,
        "repository": CANONICAL_REPOSITORY,
        "fork_repository": manifest["repository"]["origin"],
        "fork_lineage": FORK_LINEAGE,
        "stats": {
            "skill_entrypoints": stats["skill_entrypoints"],
            "skill_directories": stats["skill_directories"],
            "meta_skills": stats["meta_skills"],
            "domain_skills": stats["domain_skills"],
            "core_skills": stats["core_skills"],
            "supporting_skills": stats["supporting_skills"],
            "experimental_skills": stats["experimental_skills"],
            "total_skills": stats["skill_entrypoints"],
            "unsafe_rules": stats["unsafe_rules"],
            "coding_guidelines": {
                "p_rules": 80,
                "g_rules_compressed": True,
            },
            "agents": stats["agents"],
            "commands": stats["commands"],
            "template_files": stats["template_files"],
        },
        "skills": {
            "core": skills["core"],
            "layer1_language_mechanics": layer1_skills,
            "layer2_design_choices": layer2_skills,
            "layer3_domain_constraints": skills["domain"],
            "supporting": skills["supporting"],
            "experimental": skills["experimental"],
        },
        "agents": manifest["agents"],
        "commands": manifest["commands"],
        "compatibility": {
            "claude_code_min_version": "1.0.0",
            "rust_version_coverage": "1.0.0 - 1.85.0",
        },
        "last_updated": latest_commit_date(root),
        "quality_checks": {
            "repository_validation": "python3 scripts/validate_repo.py",
            "hook_matcher_tests": "python3 tests/hook-matcher-test.py",
            "trigger_self_check": "bash test-triggers.sh --self-check",
            "ci_ready": True,
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_capabilities_summary(root: Path | None = None) -> str:
    root = root or repo_root()
    manifest = build_manifest(root)
    stats = manifest["stats"]
    skills = manifest["skills"]
    assets = manifest["assets"]

    asset_lines = "\n".join(
        f"| `{path}` | {'present' if exists else 'missing'} |"
        for path, exists in assets.items()
    )
    command_lines = "\n".join(f"- `{command}`" for command in manifest["commands"])
    agent_lines = "\n".join(f"- `{agent}`" for agent in manifest["agents"])
    core_lines = ", ".join(f"`{name}`" for name in skills["core"])
    meta_lines = ", ".join(f"`{name}`" for name in skills["meta"])
    domain_lines = ", ".join(f"`{name}`" for name in skills["domain"])
    supporting_lines = ", ".join(f"`{name}`" for name in skills["supporting"])

    return f"""# Rust-Skills Capabilities Summary

> Generated from `scripts/render_repository_artifacts.py`. Do not edit by hand.

## Overview

| Metric | Count |
|--------|-------|
| Total Skill Entrypoints | {stats["skill_entrypoints"]} |
| Background Agents | {stats["agents"]} |
| Slash Commands | {stats["commands"]} |
| Unsafe Rules | {stats["unsafe_rules"]} |
| Template Files | {stats["template_files"]} |

## Skill Topology

- Root router entrypoint: `rust-guru` via the repository root `SKILL.md`
- Core skills: {core_lines}
- Meta skills: {meta_lines}
- Domain skills: {domain_lines}
- Supporting skills: {supporting_lines}

## Hook Routing

The repository uses a Rust-targeted lexical matcher in `hooks/hooks.json` to trigger the forced evaluation hook. The matcher is validated against positive and negative prompt samples by `tests/hook-matcher-test.py`, and the local hook asset is verified by `test-triggers.sh --self-check`.

## Commands

{command_lines}

## Agents

{agent_lines}

## Distribution Assets

| Asset | Status |
|-------|--------|
{asset_lines}

## Validation Commands

- `python3 scripts/validate_repo.py`
- `python3 tests/hook-matcher-test.py`
- `bash test-triggers.sh --self-check`
- `bash tests/validation/validate-skills.sh`
- `bash scripts/quality-check.sh`

## Repository Lineage

- Canonical upstream reference: `{CANONICAL_REPOSITORY}`
- Active fork origin: `{manifest["repository"]["origin"]}`
"""


def write_artifacts(root: Path | None = None) -> None:
    root = root or repo_root()
    (root / "metadata.json").write_text(render_metadata(root), encoding="utf-8")
    (root / "docs" / "capabilities-summary.md").write_text(
        render_capabilities_summary(root), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write generated artifacts to disk.",
    )
    parser.add_argument(
        "--artifact",
        choices=("metadata", "capabilities", "all"),
        default="all",
        help="Print a single artifact or all artifacts to stdout when not writing.",
    )
    args = parser.parse_args()

    root = repo_root()
    if args.write:
        write_artifacts(root)
        return 0

    outputs = []
    if args.artifact in {"metadata", "all"}:
        outputs.append(render_metadata(root))
    if args.artifact in {"capabilities", "all"}:
        outputs.append(render_capabilities_summary(root))
    print("\n".join(output.rstrip() for output in outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
