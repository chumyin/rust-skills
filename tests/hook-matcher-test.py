#!/usr/bin/env python3
"""Executable tests for the Rust hook matcher."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS_PATH = ROOT / "hooks" / "hooks.json"
MATCHER = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))["hooks"]["UserPromptSubmit"][0]["matcher"]
PATTERN = re.compile(MATCHER)

POSITIVE_CASES = [
    ("how to use tokio", "tokio"),
    ("value moved error", "value moved"),
    ("E0382 in my trading system", "E0382"),
    ("Cargo.toml workspace members", "Cargo.toml"),
    ("Rust web server with axum", "Rust"),
    ("Need Send Sync trait bounds", "Send"),
]

NEGATIVE_CASES = [
    "hello world",
    "write a haiku",
    "docker compose bug",
    "difference between tcp and udp",
]


def main() -> int:
    print("=== Hook Matcher Tests ===")
    print(f"Matcher loaded from: {HOOKS_PATH}\n")

    failed = 0

    for text, expected in POSITIVE_CASES:
        match = PATTERN.search(text)
        if match is None:
            failed += 1
            print(f"FAIL: expected Rust prompt to match: {text!r}")
            continue
        print(f"PASS: {text!r} -> matched {match.group()!r}")
        if expected.lower() not in match.group().lower():
            failed += 1
            print(f"FAIL: expected match fragment {expected!r}, got {match.group()!r}")

    for text in NEGATIVE_CASES:
        match = PATTERN.search(text)
        if match is not None:
            failed += 1
            print(f"FAIL: expected non-Rust prompt to miss: {text!r} -> {match.group()!r}")
        else:
            print(f"PASS: {text!r} -> no match")

    print(f"\nSummary: {len(POSITIVE_CASES) + len(NEGATIVE_CASES) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
