#!/usr/bin/env python3
"""Validate repository structure, linked assets, and metadata consistency."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from repo_manifest import build_manifest, repo_root

POSITIVE_MATCH_CASES = [
    "how to use tokio",
    "value moved error",
    "E0382 in my trading system",
    "Cargo.toml workspace",
    "Rust web server with axum",
    "Send Sync trait",
]

NEGATIVE_MATCH_CASES = [
    "hello world",
    "write a haiku",
    "docker compose bug",
    "difference between tcp and udp",
]


def parse_links(markdown: str) -> list[str]:
    links = re.findall(r"!?[^\]]*\]\(([^)]+)\)", markdown)
    return links


def resolve_local_link(root: Path, source: Path, target: str) -> Path:
    if target.startswith("/"):
        return root / target.lstrip("/")
    return (source.parent / target).resolve()


def main() -> int:
    root = repo_root()
    manifest = build_manifest(root)
    errors: list[str] = []
    warnings: list[str] = []

    for asset, exists in manifest["assets"].items():
        if not exists:
            errors.append(f"missing required asset: {asset}")

    metadata_path = root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("version") != manifest["version"]:
        errors.append(
            f"metadata version {metadata.get('version')} does not match VERSION {manifest['version']}"
        )

    expected_stats = manifest["stats"]
    for key, expected in expected_stats.items():
        actual = metadata.get("stats", {}).get(key)
        if actual != expected:
            errors.append(f"metadata stats.{key}={actual!r} does not match manifest {expected!r}")

    if metadata.get("fork_repository") != manifest["repository"]["origin"]:
        errors.append(
            "metadata fork_repository does not match git remote origin "
            f"({metadata.get('fork_repository')!r} != {manifest['repository']['origin']!r})"
        )

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    for raw_link in parse_links(readme):
        if raw_link.startswith(("http://", "https://", "mailto:")) or raw_link.startswith("#"):
            continue
        target = raw_link.split("#", 1)[0]
        resolved = resolve_local_link(root, readme_path, target)
        if not resolved.exists():
            errors.append(f"README link points to missing file: {raw_link}")

    hooks_path = root / "hooks" / "hooks.json"
    hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
    matcher = hooks["hooks"]["UserPromptSubmit"][0]["matcher"]
    try:
        pattern = re.compile(matcher)
    except re.error as exc:
        errors.append(f"hook matcher does not compile: {exc}")
    else:
        for text in POSITIVE_MATCH_CASES:
            if not pattern.search(text):
                errors.append(f"hook matcher missed expected Rust prompt: {text!r}")
        for text in NEGATIVE_MATCH_CASES:
            if pattern.search(text):
                errors.append(f"hook matcher incorrectly matched non-Rust prompt: {text!r}")

    hook_script = root / ".claude" / "hooks" / "rust-skill-eval-hook.sh"
    if hook_script.exists() and not hook_script.stat().st_mode & 0o111:
        warnings.append("hook script exists but is not executable")

    if errors:
        print("Repository validation FAILED")
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print("Repository validation PASSED")

    for warning in warnings:
        print(f"WARN: {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
