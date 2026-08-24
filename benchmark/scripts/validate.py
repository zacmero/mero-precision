#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from validation_core import (
    SETTING_FIELDS,
    load_json,
    load_records,
    validate_manifest,
    validate_record,
)


def validate_against_manifest(records: list[dict[str, Any]], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    arms = manifest["arms"]
    settings = manifest["settings"]
    tasks = {task["task_id"]: task for task in manifest["tasks"]}
    arm_orders = manifest["arm_orders"]
    exclusion_codes = {rule["code"] for rule in manifest["exclusion_rules"]}

    included_cells: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    run_ids: Counter[str] = Counter()
    commits: set[str] = set()

    for record in records:
        line = record.get("_line", "?")
        prefix = f"line {line}"
        run_ids[str(record.get("run_id"))] += 1
        if record.get("experiment_id") != manifest["experiment_id"]:
            errors.append(f"{prefix}: experiment_id does not match manifest")
        task = tasks.get(record.get("task_id"))
        if task is None:
            errors.append(f"{prefix}: unknown task_id {record.get('task_id')!r}")
            continue
        if record.get("arm") not in arms:
            errors.append(f"{prefix}: arm is not enabled by manifest")
        replicate = record.get("replicate")
        if not isinstance(replicate, int) or replicate > task["replicates"]:
            errors.append(f"{prefix}: replicate exceeds manifest")
            continue
        key = f"{task['task_id']}:r{replicate}"
        order = arm_orders.get(key, [])
        if record.get("arm") in order:
            expected_index = order.index(record["arm"]) + 1
            if record.get("order_index") != expected_index:
                errors.append(f"{prefix}: order_index must be {expected_index} from manifest arm order")
        for field in SETTING_FIELDS:
            expected = task.get(field, settings.get(field))
            if record.get(field) != expected:
                errors.append(f"{prefix}: {field}={record.get(field)!r} does not match manifest value {expected!r}")
        if record.get("fixture_commit") != task.get("fixture_commit"):
            errors.append(f"{prefix}: fixture_commit does not match task manifest")
        expected_implementation = None if record.get("arm") == "baseline" else manifest.get("implementation_commit")
        if record.get("implementation_commit") != expected_implementation:
            errors.append(f"{prefix}: implementation_commit does not match the manifest arm contract")
        commit = record.get("preregistration_commit")
        if isinstance(commit, str):
            commits.add(commit)
        exclusion = record.get("exclusion", {})
        if exclusion.get("excluded"):
            if exclusion.get("code") not in exclusion_codes:
                errors.append(f"{prefix}: exclusion code is not preregistered")
        else:
            included_cells[(task["task_id"], replicate, record["arm"])].append(record)

    for run_id, count in run_ids.items():
        if count > 1:
            errors.append(f"duplicate run_id {run_id!r}")
    if len(commits) > 1:
        errors.append(f"run records use multiple preregistration commits: {', '.join(sorted(commits))}")
    for cell, cell_records in included_cells.items():
        if len(cell_records) > 1:
            errors.append(f"multiple included records for cell {cell}")
    return errors


def validate_artifacts(records: list[dict[str, Any]], root: Path) -> list[str]:
    errors: list[str] = []
    resolved_root = root.resolve()
    for record in records:
        line = record.get("_line", "?")
        for field, value in record.get("artifacts", {}).items():
            if value is None:
                if record.get("status") == "completed" and field in {"prompt", "response", "usage", "checks", "environment"}:
                    errors.append(f"line {line}: completed run requires artifacts.{field}")
                continue
            if not isinstance(value, str):
                errors.append(f"line {line}: artifacts.{field} must be a path string or null")
                continue
            path = (resolved_root / value).resolve()
            try:
                path.relative_to(resolved_root)
            except ValueError:
                errors.append(f"line {line}: artifact path escapes root: {value}")
                continue
            if not path.is_file():
                errors.append(f"line {line}: artifact file does not exist: {value}")
    return errors


def expected_cells(manifest: dict[str, Any]) -> set[tuple[str, int, str]]:
    return {
        (task["task_id"], replicate, arm)
        for task in manifest["tasks"]
        for replicate in range(1, task["replicates"] + 1)
        for arm in manifest["arms"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Mero Precision JSONL run records")
    parser.add_argument("path", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-artifacts", action="store_true")
    args = parser.parse_args()

    records, errors = load_records(args.path)
    if not records:
        errors.append("no records found")

    for record in records:
        errors.extend(validate_record(record))

    manifest = None
    if args.manifest:
        try:
            manifest = load_json(args.manifest)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"manifest: {exc}")
        else:
            errors.extend(validate_manifest(manifest, args.manifest.parent))
            errors.extend(validate_against_manifest(records, manifest))

    if args.require_artifacts:
        root = args.artifact_root or args.path.parent
        errors.extend(validate_artifacts(records, root))

    if args.require_complete:
        if manifest is None:
            errors.append("--require-complete requires --manifest")
        else:
            included = {
                (r["task_id"], r["replicate"], r["arm"])
                for r in records
                if not r.get("exclusion", {}).get("excluded", False)
            }
            missing = sorted(expected_cells(manifest) - included)
            for cell in missing:
                errors.append(f"missing included run for cell {cell}")

    if errors:
        for error in sorted(set(errors)):
            print(error)
        return 1

    included_count = sum(not r.get("exclusion", {}).get("excluded", False) for r in records)
    excluded_count = len(records) - included_count
    print(f"valid: {len(records)} records ({included_count} included, {excluded_count} excluded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
