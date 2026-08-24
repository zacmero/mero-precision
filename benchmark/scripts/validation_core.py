#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ARMS = {"baseline", "kernel", "skill", "selective"}
STATUSES = {"completed", "timeout", "error", "refusal", "malformed"}
MODES = {"off", "observe", "selective"}
REVIEW_LABELS = {None, "true_positive", "false_positive", "true_negative", "false_negative"}
HEX_COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
PLACEHOLDER = "REPLACE_ME"

REQUIRED_RECORD_FIELDS = {
    "schema_version",
    "experiment_id",
    "manifest_path",
    "preregistration_commit",
    "run_id",
    "task_id",
    "arm",
    "replicate",
    "order_index",
    "host",
    "host_version",
    "provider",
    "model",
    "effort",
    "temperature",
    "permission_mode",
    "tool_profile",
    "environment_id",
    "timeout_seconds",
    "fixture_commit",
    "implementation_commit",
    "started_at",
    "ended_at",
    "duration_ms",
    "status",
    "tokens",
    "model_invocations",
    "turns",
    "tool_calls",
    "retries",
    "quality",
    "enforcement",
    "artifacts",
    "exclusion",
}

TOKEN_FIELDS = ("complete", "source", "input", "cache_read", "cache_write", "output", "reasoning", "total")
ARTIFACT_FIELDS = ("prompt", "response", "transcript", "usage", "diff", "checks", "gate_events", "environment")
SETTING_FIELDS = (
    "host",
    "host_version",
    "provider",
    "model",
    "effort",
    "temperature",
    "permission_mode",
    "tool_profile",
    "environment_id",
    "timeout_seconds",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def load_records(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: record must be an object")
                continue
            record["_line"] = line_number
            records.append(record)
    return records, errors


def valid_iso8601(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_manifest(manifest: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "experiment_id",
        "stage",
        "implementation_commit",
        "random_seed",
        "arms",
        "primary_outcomes",
        "analysis_command",
        "exclusion_rules",
        "settings",
        "arm_orders",
        "tasks",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        return [f"manifest: missing fields: {', '.join(missing)}"]

    if manifest["schema_version"] != "1.0":
        errors.append("manifest: schema_version must be 1.0")
    if not HEX_COMMIT_RE.fullmatch(str(manifest.get("implementation_commit", ""))):
        errors.append("manifest: implementation_commit must be a 7-40 character lowercase hex commit")
    if manifest["stage"] not in {"pilot", "claim-candidate"}:
        errors.append("manifest: invalid stage")

    arms = manifest.get("arms")
    if not isinstance(arms, list) or len(arms) < 2 or len(set(arms)) != len(arms) or any(a not in ARMS for a in arms):
        errors.append("manifest: arms must be a unique list of supported arms")
    elif "baseline" not in arms:
        errors.append("manifest: arms must include baseline")

    settings = manifest.get("settings")
    if not isinstance(settings, dict):
        errors.append("manifest: settings must be an object")
        settings = {}
    for field in SETTING_FIELDS:
        if field not in settings:
            errors.append(f"manifest: settings.{field} is required")
    for path, value in walk_values(manifest):
        if isinstance(value, str) and PLACEHOLDER in value:
            errors.append(f"manifest: unresolved placeholder at {path}")

    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("manifest: tasks must be a non-empty list")
        return errors

    task_ids: set[str] = set()
    arm_orders = manifest.get("arm_orders") if isinstance(manifest.get("arm_orders"), dict) else {}
    exclusion_codes: set[str] = set()
    for rule in manifest.get("exclusion_rules", []):
        if not isinstance(rule, dict) or not isinstance(rule.get("code"), str):
            errors.append("manifest: each exclusion rule needs a code and description")
            continue
        code = rule["code"]
        if code in exclusion_codes:
            errors.append(f"manifest: duplicate exclusion code {code}")
        exclusion_codes.add(code)

    for index, task in enumerate(tasks, 1):
        if not isinstance(task, dict):
            errors.append(f"manifest: task {index} must be an object")
            continue
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"manifest: task {index} has no task_id")
            continue
        if task_id in task_ids:
            errors.append(f"manifest: duplicate task_id {task_id}")
        task_ids.add(task_id)
        replicates = task.get("replicates")
        if not isinstance(replicates, int) or replicates < 1:
            errors.append(f"manifest: {task_id}.replicates must be positive")
            continue
        prompt_path = task.get("prompt_path")
        if not isinstance(prompt_path, str) or not prompt_path:
            errors.append(f"manifest: {task_id}.prompt_path is required")
        elif not (root / prompt_path).is_file():
            errors.append(f"manifest: prompt file does not exist: {prompt_path}")
        if not task.get("deliverables"):
            errors.append(f"manifest: {task_id} needs at least one deliverable")
        if not task.get("acceptance_checks"):
            errors.append(f"manifest: {task_id} needs at least one acceptance check")
        for replicate in range(1, replicates + 1):
            key = f"{task_id}:r{replicate}"
            order = arm_orders.get(key)
            if not isinstance(order, list) or set(order) != set(arms) or len(order) != len(arms):
                errors.append(f"manifest: arm_orders.{key} must be a permutation of arms")

    expected_order_keys = {
        f"{task['task_id']}:r{replicate}"
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("task_id"), str) and isinstance(task.get("replicates"), int)
        for replicate in range(1, task["replicates"] + 1)
    }
    extra_order_keys = set(arm_orders) - expected_order_keys
    if extra_order_keys:
        errors.append(f"manifest: unknown arm order keys: {', '.join(sorted(extra_order_keys))}")
    return errors


def walk_values(value: Any, path: str = "root"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_values(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_values(child, f"{path}[{index}]")
    else:
        yield path, value


def validate_record(record: dict[str, Any]) -> list[str]:
    line = record.get("_line", "?")
    prefix = f"line {line}"
    errors: list[str] = []
    missing = sorted(REQUIRED_RECORD_FIELDS - record.keys())
    if missing:
        return [f"{prefix}: missing fields: {', '.join(missing)}"]

    if record["schema_version"] != "1.0":
        errors.append(f"{prefix}: schema_version must be 1.0")
    if record["arm"] not in ARMS:
        errors.append(f"{prefix}: invalid arm {record['arm']!r}")
    if record["status"] not in STATUSES:
        errors.append(f"{prefix}: invalid status {record['status']!r}")
    if not isinstance(record["replicate"], int) or record["replicate"] < 1:
        errors.append(f"{prefix}: replicate must be a positive integer")
    if not isinstance(record["order_index"], int) or record["order_index"] < 1:
        errors.append(f"{prefix}: order_index must be a positive integer")
    if not isinstance(record["duration_ms"], int) or record["duration_ms"] < 0:
        errors.append(f"{prefix}: duration_ms must be a non-negative integer")
    if not isinstance(record["timeout_seconds"], int) or record["timeout_seconds"] < 1:
        errors.append(f"{prefix}: timeout_seconds must be positive")
    if not HEX_COMMIT_RE.fullmatch(str(record["preregistration_commit"])):
        errors.append(f"{prefix}: preregistration_commit must be a 7-40 character lowercase hex commit")
    if not valid_iso8601(record["started_at"]) or not valid_iso8601(record["ended_at"]):
        errors.append(f"{prefix}: started_at and ended_at must be ISO-8601 timestamps")

    for field in ("model_invocations", "turns"):
        if not isinstance(record[field], int) or record[field] < 0:
            errors.append(f"{prefix}: {field} must be a non-negative integer")
    for field in ("tool_calls", "retries"):
        if record[field] is not None and (not isinstance(record[field], int) or record[field] < 0):
            errors.append(f"{prefix}: {field} must be null or a non-negative integer")
    if record["status"] == "completed" and record["model_invocations"] < 1:
        errors.append(f"{prefix}: completed runs need at least one model invocation")

    tokens = record["tokens"]
    if not isinstance(tokens, dict):
        errors.append(f"{prefix}: tokens must be an object")
    else:
        for field in TOKEN_FIELDS:
            if field not in tokens:
                errors.append(f"{prefix}: tokens.{field} is required")
        if tokens.get("complete"):
            missing_values = [field for field in ("input", "cache_read", "cache_write", "output", "reasoning", "total") if tokens.get(field) is None]
            if missing_values:
                errors.append(f"{prefix}: complete token accounting has null fields: {', '.join(missing_values)}")
        for field in ("input", "cache_read", "cache_write", "output", "reasoning", "total"):
            value = tokens.get(field)
            if value is not None and (not isinstance(value, int) or value < 0):
                errors.append(f"{prefix}: tokens.{field} must be null or a non-negative integer")

    quality = record["quality"]
    if not isinstance(quality, dict):
        errors.append(f"{prefix}: quality must be an object")
    else:
        if not isinstance(quality.get("task_success"), bool):
            errors.append(f"{prefix}: quality.task_success must be boolean")
        score = quality.get("deterministic_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            errors.append(f"{prefix}: quality.deterministic_score must be in [0, 1]")
        semantic = quality.get("semantic_score")
        if semantic is not None and (not isinstance(semantic, (int, float)) or isinstance(semantic, bool) or not 0 <= semantic <= 1):
            errors.append(f"{prefix}: quality.semantic_score must be null or in [0, 1]")
        if record["status"] != "completed" and quality.get("task_success") is True:
            errors.append(f"{prefix}: non-completed run cannot have task_success=true")

    enforcement = record["enforcement"]
    if not isinstance(enforcement, dict):
        errors.append(f"{prefix}: enforcement must be an object")
    else:
        if enforcement.get("mode") not in MODES:
            errors.append(f"{prefix}: invalid enforcement.mode")
        if enforcement.get("review_label") not in REVIEW_LABELS:
            errors.append(f"{prefix}: invalid enforcement.review_label")
        if enforcement.get("triggered") and enforcement.get("mode") != "selective":
            errors.append(f"{prefix}: enforcement can trigger only in selective mode")

    expected_mode = {"baseline": "off", "kernel": "observe", "skill": "observe", "selective": "selective"}.get(record["arm"])
    if isinstance(enforcement, dict) and enforcement.get("mode") != expected_mode:
        errors.append(f"{prefix}: arm {record['arm']} requires enforcement.mode={expected_mode}")

    if record["arm"] == "baseline" and record["implementation_commit"] is not None:
        errors.append(f"{prefix}: baseline implementation_commit must be null")
    if record["arm"] != "baseline":
        implementation_commit = record["implementation_commit"]
        if not isinstance(implementation_commit, str):
            errors.append(f"{prefix}: treatment arm requires implementation_commit")
        elif not HEX_COMMIT_RE.fullmatch(implementation_commit):
            errors.append(f"{prefix}: implementation_commit must be a 7-40 character lowercase hex commit")

    artifacts = record["artifacts"]
    if not isinstance(artifacts, dict):
        errors.append(f"{prefix}: artifacts must be an object")
    else:
        for field in ARTIFACT_FIELDS:
            if field not in artifacts:
                errors.append(f"{prefix}: artifacts.{field} is required")

    exclusion = record["exclusion"]
    if not isinstance(exclusion, dict):
        errors.append(f"{prefix}: exclusion must be an object")
    else:
        if not isinstance(exclusion.get("excluded"), bool):
            errors.append(f"{prefix}: exclusion.excluded must be boolean")
        if exclusion.get("excluded") and not exclusion.get("code"):
            errors.append(f"{prefix}: excluded run requires exclusion.code")
        if not exclusion.get("excluded") and (exclusion.get("code") is not None or exclusion.get("reason") is not None):
            errors.append(f"{prefix}: included run must have null exclusion code and reason")

    return errors
