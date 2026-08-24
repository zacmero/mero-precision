#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"


def load_json(relative: str, errors: list[str]) -> dict:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {relative}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"JSON root must be an object: {relative}")
        return {}
    return value


def main() -> int:
    errors: list[str] = []

    required = [
        "README.md",
        "LICENSE",
        "NOTICE.md",
        "CITATION.cff",
        "Makefile",
        "plugin.json",
        "hooks.json",
        ".codex-plugin/plugin.json",
        "hooks/codex-hooks.json",
        "rules/precision-kernel.md",
        "skills/mero-precision/SKILL.md",
        "package.json",
        "pyproject.toml",
        "benchmark/POLICY.md",
        "benchmark/RUBRIC.md",
        "benchmark/RUNNER_SPEC.md",
        "benchmark/ANALYST_PROMPT.md",
        "benchmark/scripts/init_experiment.py",
        "benchmark/scripts/validate.py",
        "benchmark/scripts/analyze.py",
        "scripts/publish_github.sh",
        "benchmark/schemas/task-manifest.schema.json",
        "benchmark/schemas/run-record.schema.json",
        "benchmark/examples/task-manifest.json",
        "benchmark/examples/run-records.jsonl",
        "adapters/codex-cli/fixtures/stop.json",
        "adapters/antigravity-cli/fixtures/stop.json",
        "adapters/pi-agent/fixtures/normalized-agent-settled.json",
        "extensions/pi/index.ts",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    json_files = (
        "plugin.json",
        "hooks.json",
        ".codex-plugin/plugin.json",
        "hooks/codex-hooks.json",
        "package.json",
        "benchmark/schemas/task-manifest.schema.json",
        "benchmark/schemas/run-record.schema.json",
        "benchmark/examples/task-manifest.json",
        "adapters/codex-cli/fixtures/stop.json",
        "adapters/antigravity-cli/fixtures/stop.json",
        "adapters/pi-agent/fixtures/normalized-agent-settled.json",
    )
    parsed = {relative: load_json(relative, errors) for relative in json_files}

    skill_path = ROOT / "skills/mero-precision/SKILL.md"
    try:
        skill = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read skill: {exc}")
        skill = ""
    if not skill.startswith("---\n") or "\nname: mero-precision\n" not in skill:
        errors.append("skill frontmatter is missing or malformed")
    version_match = re.search(r'(?m)^  version: "([^"]+)"$', skill)
    if not version_match or version_match.group(1) != VERSION:
        errors.append(f"skill metadata version must be {VERSION}")

    for reference in ("review", "commit", "docs", "spec", "research", "incident", "memory"):
        if not (ROOT / f"skills/mero-precision/references/{reference}.md").is_file():
            errors.append(f"missing skill reference: {reference}.md")

    package = parsed.get("package.json", {})
    codex_plugin = parsed.get(".codex-plugin/plugin.json", {})
    if package.get("name") != "mero-precision" or package.get("version") != VERSION:
        errors.append("package.json name or version is inconsistent")
    if codex_plugin.get("name") != "mero-precision" or codex_plugin.get("version") != VERSION:
        errors.append("Codex plugin name or version is inconsistent")
    if parsed.get("plugin.json", {}).get("name") != "mero-precision":
        errors.append("Antigravity plugin name is inconsistent")

    try:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"invalid pyproject.toml: {exc}")
    else:
        project = pyproject.get("project", {})
        if project.get("name") != "mero-precision" or project.get("version") != VERSION:
            errors.append("pyproject.toml name or version is inconsistent")

    if errors:
        for error in errors:
            print(error)
        return 1

    print("repository structure valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
