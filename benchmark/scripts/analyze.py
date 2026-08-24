#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

METRICS = {
    "task_success": "Task success",
    "deterministic_score": "Deterministic score",
    "semantic_score": "Semantic score",
    "total_tokens": "Total tokens",
    "input_tokens": "Input tokens",
    "cache_read_tokens": "Cache-read tokens",
    "cache_write_tokens": "Cache-write tokens",
    "output_tokens": "Output tokens",
    "reasoning_tokens": "Reasoning tokens",
    "model_invocations": "Model invocations",
    "turns": "Turns",
    "tool_calls": "Tool calls",
    "retries": "Retries",
    "duration_ms": "Duration (ms)",
}

DEFAULT_METRICS = [
    "task_success",
    "deterministic_score",
    "semantic_score",
    "total_tokens",
    "input_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "model_invocations",
    "turns",
    "tool_calls",
    "retries",
    "duration_ms",
]

STRATUM_FIELDS = (
    "experiment_id",
    "host",
    "host_version",
    "provider",
    "model",
    "effort",
    "temperature",
    "permission_mode",
    "tool_profile",
    "environment_id",
)


def read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"line {line_number}: record must be an object")
            records.append(record)
    return records


def read_manifest(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def bootstrap_ci(values: list[float], seed: int = 0, samples: int = 5000) -> tuple[float, float] | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0], values[0]

    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        draw = [rng.choice(values) for _ in values]
        means.append(statistics.fmean(draw))
    means.sort()
    low = means[math.floor(0.025 * (samples - 1))]
    high = means[math.ceil(0.975 * (samples - 1))]
    return low, high


def stable_seed(*parts: str) -> int:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def metric(record: dict[str, Any], name: str) -> float | None:
    quality = record.get("quality", {})
    tokens = record.get("tokens", {})
    if name == "task_success":
        return 1.0 if quality.get("task_success") else 0.0
    if name == "deterministic_score":
        value = quality.get("deterministic_score")
    elif name == "semantic_score":
        value = quality.get("semantic_score")
    elif name == "duration_ms":
        value = record.get("duration_ms")
    elif name in {"model_invocations", "turns", "tool_calls", "retries"}:
        value = record.get(name)
    elif name == "total_tokens":
        if not tokens.get("complete"):
            return None
        value = tokens.get("total")
    elif name == "input_tokens":
        value = tokens.get("input")
    elif name == "cache_read_tokens":
        value = tokens.get("cache_read")
    elif name == "cache_write_tokens":
        value = tokens.get("cache_write")
    elif name == "output_tokens":
        value = tokens.get("output")
    elif name == "reasoning_tokens":
        value = tokens.get("reasoning")
    else:
        raise ValueError(name)
    return float(value) if value is not None else None


def fmt(value: float | None, digits: int = 2) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def stratum_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(record.get(field) for field in STRATUM_FIELDS)


def stratum_label(key: tuple[Any, ...]) -> str:
    values = dict(zip(STRATUM_FIELDS, key, strict=True))
    effort = values["effort"] if values["effort"] is not None else "default"
    temperature = values["temperature"] if values["temperature"] is not None else "default"
    return (
        f"{values['experiment_id']} · {values['host']} {values['host_version']} · "
        f"{values['provider']}/{values['model']} · effort={effort} · temperature={temperature} · "
        f"permissions={values['permission_mode']} · tools={values['tool_profile']} · env={values['environment_id']}"
    )


def cell_map(records: list[dict[str, Any]]) -> dict[tuple[str, int, str], dict[str, Any]]:
    result: dict[tuple[str, int, str], dict[str, Any]] = {}
    for record in records:
        key = (record["task_id"], record["replicate"], record["arm"])
        result.setdefault(key, record)
    return result


def task_level_deltas(
    records: list[dict[str, Any]],
    arm: str,
    metric_name: str,
) -> tuple[list[float], int]:
    by_cell = cell_map(records)
    tasks = sorted({record["task_id"] for record in records})
    task_deltas: list[float] = []
    paired_runs = 0

    for task_id in tasks:
        replicate_ids = sorted({record["replicate"] for record in records if record["task_id"] == task_id})
        replicate_deltas: list[float] = []
        for replicate in replicate_ids:
            baseline = by_cell.get((task_id, replicate, "baseline"))
            treatment = by_cell.get((task_id, replicate, arm))
            if baseline is None or treatment is None:
                continue
            baseline_value = metric(baseline, metric_name)
            treatment_value = metric(treatment, metric_name)
            if baseline_value is None or treatment_value is None:
                continue
            replicate_deltas.append(treatment_value - baseline_value)
            paired_runs += 1
        if replicate_deltas:
            task_deltas.append(statistics.fmean(replicate_deltas))

    return task_deltas, paired_runs


def absolute_task_success(records: list[dict[str, Any]], arm: str) -> tuple[int, int, float | None]:
    arm_records = [record for record in records if record["arm"] == arm]
    if not arm_records:
        return 0, 0, None
    successes = sum(bool(record.get("quality", {}).get("task_success")) for record in arm_records)
    return successes, len(arm_records), successes / len(arm_records)


def expected_cells(manifest: dict[str, Any]) -> set[tuple[str, int, str]]:
    return {
        (task["task_id"], replicate, arm)
        for task in manifest.get("tasks", [])
        for replicate in range(1, int(task.get("replicates", 0)) + 1)
        for arm in manifest.get("arms", [])
    }


def policy_audit(records: list[dict[str, Any]], manifest: dict[str, Any] | None) -> list[str]:
    included = [record for record in records if not record.get("exclusion", {}).get("excluded", False)]
    excluded = [record for record in records if record.get("exclusion", {}).get("excluded", False)]
    lines = [
        "## Policy audit",
        "",
        f"- Raw records: **{len(records)}**.",
        f"- Included records: **{len(included)}**.",
        f"- Excluded records retained: **{len(excluded)}**.",
    ]

    experiments = sorted({str(record.get("experiment_id")) for record in records})
    commits = sorted({str(record.get("preregistration_commit")) for record in records if record.get("preregistration_commit")})
    implementation_commits = sorted(
        {str(record.get("implementation_commit")) for record in records if record.get("implementation_commit")}
    )
    strata = {stratum_key(record) for record in included}
    lines.append(f"- Experiment IDs: **{len(experiments)}** ({', '.join(experiments) or 'none'}).")
    lines.append(f"- Preregistration commits: **{len(commits)}** ({', '.join(commits) or 'none'}).")
    lines.append(
        f"- Mero Precision implementation commits: **{len(implementation_commits)}** "
        f"({', '.join(implementation_commits) or 'none'})."
    )
    lines.append(f"- Host/model/settings strata: **{len(strata)}**. Results below are not pooled across strata.")

    incomplete_tokens = [record for record in included if not record.get("tokens", {}).get("complete")]
    lines.append(f"- Included runs with incomplete total-token accounting: **{len(incomplete_tokens)}**.")

    duplicate_cells = Counter((r["task_id"], r["replicate"], r["arm"]) for r in included)
    duplicate_count = sum(count - 1 for count in duplicate_cells.values() if count > 1)
    lines.append(f"- Duplicate included task/replicate/arm cells: **{duplicate_count}**.")

    if manifest is None:
        lines.append("- No manifest supplied. Missing cells, preregistered arm order, and design-stage checks are not verified here.")
    else:
        actual = set(duplicate_cells)
        missing = expected_cells(manifest) - actual
        lines.append(f"- Missing preregistered cells: **{len(missing)}**.")
        task_count = len(manifest.get("tasks", []))
        replicate_floor = min((int(task.get("replicates", 0)) for task in manifest.get("tasks", [])), default=0)
        stage = manifest.get("stage", "unknown")
        lines.append(f"- Design stage: **{stage}**; tasks: **{task_count}**; minimum replicates per task: **{replicate_floor}**.")
        if stage == "pilot":
            lines.append("- Pilot status: exploratory only. The policy forbids public performance claims from this stage.")
        elif stage == "claim-candidate":
            if task_count < 30 or replicate_floor < 3:
                lines.append("- Claim-candidate floor is not met: fewer than 30 tasks or fewer than three replicates.")
            else:
                lines.append("- Numeric claim-candidate floor is met. This does not establish adequate power or claim readiness.")

    if excluded:
        exclusion_counts = Counter(str(record.get("exclusion", {}).get("code")) for record in excluded)
        detail = ", ".join(f"{code}={count}" for code, count in sorted(exclusion_counts.items()))
        lines.append(f"- Exclusion codes: {detail}.")

    lines.extend([
        "",
        "Run `benchmark/scripts/validate.py` with the manifest before interpreting effects. This report does not certify preregistration integrity.",
        "",
    ])
    return lines


def ordered_metrics(manifest: dict[str, Any] | None) -> list[str]:
    primary = [name for name in (manifest or {}).get("primary_outcomes", []) if name in METRICS]
    return primary + [name for name in DEFAULT_METRICS if name not in primary]


def render_stratum(records: list[dict[str, Any]], key: tuple[Any, ...], metrics: list[str], arms: list[str]) -> list[str]:
    lines = [
        f"## Stratum: {stratum_label(key)}",
        "",
        "Positive deltas mean that treatment is higher than baseline. Lower is usually better for tokens, turns, retries, tool calls, invocations, and duration.",
        "",
    ]

    for metric_name in metrics:
        rows: list[str] = []
        for arm in arms:
            task_deltas, paired_runs = task_level_deltas(records, arm, metric_name)
            if not task_deltas:
                continue
            mean = statistics.fmean(task_deltas)
            median = statistics.median(task_deltas)
            ci = bootstrap_ci(task_deltas, seed=stable_seed(str(key), arm, metric_name))
            ci_text = "—" if ci is None else f"[{fmt(ci[0])}, {fmt(ci[1])}]"
            rows.append(f"| {arm} | {len(task_deltas)} | {paired_runs} | {fmt(mean)} | {fmt(median)} | {ci_text} |")
        if not rows:
            continue
        lines.extend([
            f"### {METRICS[metric_name]}",
            "",
            "| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |",
            "|---|---:|---:|---:|---:|---:|",
            *rows,
            "",
        ])

    lines.extend([
        "### Absolute task success",
        "",
        "| Arm | Successful runs | Included runs | Rate |",
        "|---|---:|---:|---:|",
    ])
    for arm in ("baseline", *arms):
        successes, count, rate = absolute_task_success(records, arm)
        rate_text = "—" if rate is None else f"{rate:.1%}"
        lines.append(f"| {arm} | {successes} | {count} | {rate_text} |")
    lines.append("")
    return lines


def hook_summary(records: list[dict[str, Any]]) -> list[str]:
    included = [record for record in records if not record.get("exclusion", {}).get("excluded", False)]
    labels = Counter(
        record.get("enforcement", {}).get("review_label")
        for record in included
        if record.get("enforcement", {}).get("review_label") is not None
    )
    would = sum(bool(record.get("enforcement", {}).get("would_enforce")) for record in included)
    triggered = [record for record in included if record.get("enforcement", {}).get("triggered")]
    extra_reviewed = [
        record.get("enforcement", {}).get("extra_turn_success")
        for record in triggered
        if record.get("enforcement", {}).get("extra_turn_success") is not None
    ]

    fp = labels["false_positive"]
    tn = labels["true_negative"]
    fn = labels["false_negative"]
    tp = labels["true_positive"]
    fpr = fp / (fp + tn) if fp + tn else None
    fnr = fn / (fn + tp) if fn + tp else None
    extra_rate = sum(bool(value) for value in extra_reviewed) / len(extra_reviewed) if extra_reviewed else None

    return [
        "## Hook calibration",
        "",
        f"- Would enforce: **{would}** included runs.",
        f"- Actually triggered: **{len(triggered)}** included runs.",
        f"- Reviewed labels: TP={tp}, FP={fp}, TN={tn}, FN={fn}.",
        f"- False-positive rate: **{'—' if fpr is None else f'{fpr:.1%}'}**.",
        f"- False-negative rate: **{'—' if fnr is None else f'{fnr:.1%}'}**.",
        f"- Reviewed extra-turn success rate: **{'—' if extra_rate is None else f'{extra_rate:.1%}'}**.",
        "",
        "False-positive and false-negative rates use explicit stop-time review labels. They are not inferred from final task success.",
        "",
    ]


def render(records: list[dict[str, Any]], manifest: dict[str, Any] | None = None) -> str:
    included = [record for record in records if not record.get("exclusion", {}).get("excluded", False)]
    arms_source = (manifest or {}).get("arms") or sorted({record.get("arm") for record in included})
    arms = [arm for arm in ("kernel", "skill", "selective") if arm in arms_source]

    lines = [
        "# Mero Precision paired benchmark report",
        "",
        "This report keeps writing quality, task completion, and task cost separate. Confidence intervals resample tasks, not replicates.",
        "",
    ]
    lines.extend(policy_audit(records, manifest))

    by_stratum: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in included:
        by_stratum[stratum_key(record)].append(record)

    metrics = ordered_metrics(manifest)
    for key in sorted(by_stratum, key=lambda item: tuple(str(value) for value in item)):
        lines.extend(render_stratum(by_stratum[key], key, metrics, arms))

    lines.extend(hook_summary(records))
    lines.extend([
        "## Interpretation boundary",
        "",
        "This output is descriptive. Inspect raw artifacts and apply `benchmark/ANALYST_PROMPT.md` before making a claim.",
        "",
        "A shorter output does not establish lower total task cost. A favorable average does not erase failed or excluded tasks.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a task-level paired Mero Precision benchmark summary")
    parser.add_argument("path", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = render(read_records(args.path), read_manifest(args.manifest))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
