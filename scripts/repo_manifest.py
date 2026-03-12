#!/usr/bin/env python3
"""Build a deterministic manifest for the rust-skills repository."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

CORE_SKILLS = {
    "rust-guru",
    "rust-learner",
    "coding-guidelines",
    "unsafe-checker",
}

EXPERIMENTAL_SKILLS = {"meta-cognition-parallel"}

REQUIRED_ASSETS = (
    "LICENSE",
    ".claude/settings.example.json",
    ".claude/hooks/rust-skill-eval-hook.sh",
    ".codex/INSTALL.md",
    ".opencode/INSTALL.md",
    "hooks/hooks.json",
    "README.md",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def git_remote_url(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def normalize_remote(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("git@github.com:"):
        return "https://github.com/" + url.removeprefix("git@github.com:").removesuffix(
            ".git"
        )
    if url.startswith("https://github.com/") and url.endswith(".git"):
        return url[:-4]
    return url


def build_manifest(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    skill_files = [root / "SKILL.md", *sorted((root / "skills").rglob("SKILL.md"))]
    skill_names: list[str] = []
    skill_entries: list[dict[str, object]] = []

    for skill_file in skill_files:
        frontmatter = parse_frontmatter(skill_file)
        if skill_file == root / "SKILL.md":
            name = frontmatter.get("name", "rust-guru")
        else:
            name = frontmatter.get("name", skill_file.parent.name)
        skill_names.append(name)
        skill_entries.append(
            {
                "name": name,
                "path": str(skill_file.relative_to(root)),
                "has_description": "description" in frontmatter,
                "user_invocable": frontmatter.get("user-invocable") != "false",
            }
        )

    meta_skills = sorted(name for name in skill_names if re.fullmatch(r"m\d{2}-[\w-]+", name))
    domain_skills = sorted(name for name in skill_names if name.startswith("domain-"))
    core_skills = sorted(name for name in skill_names if name in CORE_SKILLS)
    experimental_skills = sorted(name for name in skill_names if name in EXPERIMENTAL_SKILLS)
    supporting_skills = sorted(
        set(skill_names) - set(meta_skills) - set(domain_skills) - set(core_skills) - set(experimental_skills)
    )

    commands = sorted(path.stem for path in (root / "commands").glob("*.md"))
    agents = sorted(path.stem for path in (root / "agents").glob("*.md"))
    unsafe_rules = sorted(
        path.stem
        for path in (root / "skills" / "unsafe-checker" / "rules").glob("*.md")
        if not path.name.startswith("_")
    )
    template_files = sorted(
        str(path.relative_to(root))
        for path in (root / "templates").rglob("*")
        if path.is_file()
    )
    assets = {
        path: (root / path).exists()
        for path in REQUIRED_ASSETS
    }

    return {
        "version": read_text(root / "VERSION").strip(),
        "repository": {
            "origin": normalize_remote(git_remote_url(root)),
        },
        "stats": {
            "skill_entrypoints": len(skill_files),
            "skill_directories": len([path for path in (root / "skills").iterdir() if path.is_dir()]),
            "core_skills": len(core_skills),
            "meta_skills": len(meta_skills),
            "domain_skills": len(domain_skills),
            "supporting_skills": len(supporting_skills),
            "experimental_skills": len(experimental_skills),
            "commands": len(commands),
            "agents": len(agents),
            "unsafe_rules": len(unsafe_rules),
            "template_files": len(template_files),
        },
        "skills": {
            "core": core_skills,
            "meta": meta_skills,
            "domain": domain_skills,
            "supporting": supporting_skills,
            "experimental": experimental_skills,
        },
        "commands": commands,
        "agents": agents,
        "assets": assets,
        "skill_entries": skill_entries,
        "template_files": template_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the generated manifest.",
    )
    args = parser.parse_args()

    manifest = build_manifest()
    indent = 2 if args.pretty else None
    print(json.dumps(manifest, indent=indent, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
