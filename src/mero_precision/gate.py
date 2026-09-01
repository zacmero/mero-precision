from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from .transcript import extract_messages, read_transcript_tail

GateMode = Literal["off", "observe", "selective"]

_ACTION_RE = re.compile(
    r"\b(implement|build|create|write|add|change|modify|fix|debug|refactor|migrate|"
    r"deploy|release|commit|push|update|remove|delete|install|configure|review|"
    r"analyse|analyze|research|compare|design)\b",
    re.IGNORECASE,
)
_CODE_CHANGE_RE = re.compile(
    r"\b(implement|add|change|modify|fix|debug|refactor|migrate|update|remove|delete)\b"
    r".*\b(code|file|function|class|module|repository|repo|test|api|database|schema|"
    r"service|script|package|component|config(?:uration)?)\b",
    re.IGNORECASE | re.DOTALL,
)
_TEST_COMMAND_RE = re.compile(
    r"\b("
    r"pytest|python\s+-m\s+unittest|"
    r"npm\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|yarn\s+test|"
    r"bun\s+(?:run\s+)?test|bun\s+t\b|"
    r"cargo\s+test|go\s+test|mvn\s+test|gradle\s+test|dotnet\s+test|"
    r"make\s+test|npm\s+run\s+build|pnpm\s+build|cargo\s+check|"
    r"ruff\s+check|eslint|tsc\s+--noEmit|"
    r"vitest|jest|playwright\s+test|cypress\s+run|deno\s+test|"
    r"mise\s+(?:run\s+|exec\s+(?:--\s+)?)(?:[a-zA-Z0-9_-]+\s+)?(?:test|check|build)|"
    r"rtk\s+(?:[a-zA-Z0-9_-]+\s+)?(?:test|check|build)"
    r")\b",
    re.IGNORECASE,
)
_SUCCESS_RE = re.compile(
    r"\b(exit(?:ed)?\s+(?:code|status)\s*0|all\s+tests?\s+passed|tests?\s+passed|"
    r"passed\b|success(?:ful(?:ly)?)?|build\s+completed|0\s+failed)\b",
    re.IGNORECASE,
)
_FAILURE_RE = re.compile(
    r"\b(exit(?:ed)?\s+(?:code|status)\s*[1-9]\d*|tests?\s+failed|failed\b|"
    r"failure\b|traceback|exception|error:)\b",
    re.IGNORECASE,
)
_INCOMPLETE_RE = re.compile(
    r"\b(could\s+not|couldn't|unable\s+to|not\s+(?:yet\s+)?implemented|"
    r"not\s+(?:yet\s+)?complete|unfinished|still\s+need(?:s)?|remains?\s+to\s+be|"
    r"todo\b|tests?\s+(?:were\s+)?not\s+run|not\s+tested|untested)\b",
    re.IGNORECASE,
)
_RESEARCH_RE = re.compile(
    r"\b(research|paper|study|evidence|hypothesis|experiment|benchmark|architecture|"
    r"causal|correlation|mechanism)\b",
    re.IGNORECASE,
)
_HIGH_STAKES_RE = re.compile(
    r"\b(security|authentication|authorization|credential|secret|production|prod\b|"
    r"trading|broker|payment|charge|financial|medical|legal|migration|irreversible|"
    r"delete|drop\s+table|truncate|wipe|deploy|release)\b",
    re.IGNORECASE,
)
_CRITICAL_EFFECT_RE = re.compile(
    r"\b(trading|broker|payment|charge|production|prod\b|deploy|release|delete|"
    r"drop\s+table|truncate|wipe|irreversible|live\s+funds?)\b",
    re.IGNORECASE,
)
_REPO_EFFECT_RE = re.compile(r"\b(commit|push|merge|deploy|release|migration|database|infrastructure)\b", re.IGNORECASE)
_ENUM_RE = re.compile(r"(?m)^\s*(?:\d+[.)]|[-*])\s+")


@dataclass(slots=True)
class GateConfig:
    mode: GateMode = "observe"
    threshold: int = 6
    max_continuations: int = 1
    state_dir: Path = field(default_factory=lambda: _default_state_dir())

    @classmethod
    def from_env(cls) -> "GateConfig":
        raw_mode = os.getenv("MERO_PRECISION_MODE", "observe").strip().lower()
        mode: GateMode = raw_mode if raw_mode in {"off", "observe", "selective"} else "observe"  # type: ignore[assignment]
        return cls(
            mode=mode,
            threshold=_bounded_int("MERO_PRECISION_THRESHOLD", 6, 1, 14),
            max_continuations=_bounded_int("MERO_PRECISION_MAX_CONTINUATIONS", 1, 0, 3),
            state_dir=Path(os.getenv("MERO_PRECISION_STATE_DIR", _default_state_dir())).expanduser(),
        )


@dataclass(slots=True)
class GateDecision:
    schema_version: str
    timestamp: str
    host: str
    mode: GateMode
    project_name: str
    task_key: str
    score: int
    threshold: int
    components: dict[str, int]
    reasons: list[str]
    actionable_reasons: list[str]
    would_enforce: bool
    enforce: bool
    continuation_count: int
    continuation_reason: str
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _default_state_dir() -> str:
    if os.name == "nt" and os.getenv("LOCALAPPDATA"):
        return str(Path(os.environ["LOCALAPPDATA"]) / "mero-precision")
    if os.getenv("XDG_STATE_HOME"):
        return str(Path(os.environ["XDG_STATE_HOME"]) / "mero-precision")
    return str(Path.home() / ".local" / "state" / "mero-precision")


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(minimum, min(maximum, value))


def _event_value(event: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in event:
            return event[key]
    return default


def _task_key(host: str, event: dict[str, Any], prompt: str) -> str:
    session = str(_event_value(event, "session_id", "conversationId", "conversation_id", default="unknown"))
    session_digest = hashlib.sha256(session.encode("utf-8", errors="replace")).hexdigest()[:12]
    prompt_digest = hashlib.sha256(prompt[-8000:].encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{host}:{session_digest}:{prompt_digest}"


def _latest_test_status(text: str) -> tuple[bool, Literal["missing", "unknown", "passed", "failed"]]:
    matches = list(_TEST_COMMAND_RE.finditer(text))
    if not matches:
        return False, "missing"

    last = matches[-1].start()
    suffix = text[last:]
    success_positions = [match.start() for match in _SUCCESS_RE.finditer(suffix)]
    failure_positions = [match.start() for match in _FAILURE_RE.finditer(suffix)]
    last_success = max(success_positions, default=-1)
    last_failure = max(failure_positions, default=-1)

    if last_failure > last_success:
        return True, "failed"
    if last_success >= 0:
        return True, "passed"
    return True, "unknown"


def _score(prompt: str, assistant: str, transcript: str, event: dict[str, Any]) -> tuple[dict[str, int], list[str], list[str]]:
    joined = "\n".join(part for part in (prompt, assistant, transcript) if part)
    prompt_words = len(prompt.split())
    action = bool(_ACTION_RE.search(prompt))
    code_change = bool(_CODE_CHANGE_RE.search(prompt))
    enumerated = len(_ENUM_RE.findall(prompt))

    complexity = 0
    reasons: list[str] = []
    actionable: list[str] = []

    if action:
        complexity += 1
    if enumerated >= 2 or re.search(r"\b(both|as well as|and also|multiple files|point by point)\b", prompt, re.IGNORECASE):
        complexity += 1
    if prompt_words >= 220 or _RESEARCH_RE.search(prompt):
        complexity += 1
    complexity = min(3, complexity)
    if complexity:
        reasons.append(f"task complexity score {complexity}")

    external_effects = 0
    if code_change:
        external_effects = 1
    if action and _REPO_EFFECT_RE.search(prompt):
        external_effects = max(external_effects, 2)
    if action and _CRITICAL_EFFECT_RE.search(prompt):
        external_effects = 3
    if external_effects:
        reasons.append(f"external-effect score {external_effects}")

    test_seen, test_status = _latest_test_status(joined)
    verification_debt = 0
    if code_change:
        if test_status == "missing":
            verification_debt = 2
            actionable.append("code work has no recorded verification")
        elif test_status == "unknown":
            verification_debt = 1
            actionable.append("verification command has no recorded result")
        elif test_status == "failed":
            verification_debt = 3
            actionable.append("latest verification failed")
    if _INCOMPLETE_RE.search(assistant):
        verification_debt = max(verification_debt, 2)
    if verification_debt:
        reasons.append(f"verification-debt score {verification_debt}")

    epistemic_risk = 0
    if _RESEARCH_RE.search(prompt):
        epistemic_risk = 1
    if _HIGH_STAKES_RE.search(prompt):
        epistemic_risk = 2
    if epistemic_risk:
        reasons.append(f"epistemic-risk score {epistemic_risk}")

    failure_state = 0
    termination_reason = str(_event_value(event, "terminationReason", "termination_reason", default=""))
    error = str(event.get("error", "") or "")
    fully_idle = _event_value(event, "fullyIdle", "fully_idle", default=True)

    if _INCOMPLETE_RE.search(assistant):
        failure_state = max(failure_state, 2)
        actionable.append("assistant reports unfinished work")
    if termination_reason in {"error", "max_steps_exceeded"} or error:
        failure_state = max(failure_state, 2)
        actionable.append("execution stopped with an error or step limit")
    if fully_idle is False:
        failure_state = max(failure_state, 2)
        actionable.append("background work is still active")
    if failure_state:
        reasons.append(f"failure-state score {failure_state}")

    components = {
        "complexity": complexity,
        "external_effects": external_effects,
        "verification_debt": verification_debt,
        "epistemic_risk": epistemic_risk,
        "failure_state": failure_state,
    }
    return components, reasons, list(dict.fromkeys(actionable))


def _continuation_reason(actionable: list[str]) -> str:
    if "background work is still active" in actionable:
        return "Background work is still active. Wait for it to finish, inspect the result, and complete the task before stopping."
    if "latest verification failed" in actionable:
        return "The latest verification failed. Correct the failure and rerun the relevant checks before stopping."
    if "code work has no recorded verification" in actionable:
        return "The task changed or requested code, but no successful verification is recorded. Run the relevant focused checks and report the result before stopping."
    if "verification command has no recorded result" in actionable:
        return "A verification command ran, but its result is not recorded. Inspect the result and establish whether the task passed before stopping."
    if "assistant reports unfinished work" in actionable:
        return "The response reports unfinished work. Complete the remaining requested deliverable, or state the exact external blocker without claiming completion."
    if "execution stopped with an error or step limit" in actionable:
        return "The run is stopping because of an execution error or step limit. Inspect the failure, recover if safe, and complete the task before stopping."
    return "Run one final completion pass and correct the concrete unresolved task defect before stopping."


def _load_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {"tasks": {}}


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    Path(temp_name).replace(path)


def _append_log(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def _is_project_disabled(event: dict[str, Any] | None = None) -> bool:
    """Check if the current workspace or project opt-out file exists."""
    paths_to_check: list[Path] = []
    try:
        paths_to_check.append(Path.cwd())
    except Exception:
        pass
    if event:
        ws = _event_value(event, "workspacePaths", "workspace_paths", "cwd", "workspace", default=None)
        if isinstance(ws, list):
            for p in ws:
                if isinstance(p, str):
                    paths_to_check.append(Path(p))
        elif isinstance(ws, str):
            paths_to_check.append(Path(ws))

    for base in paths_to_check:
        try:
            resolved = base.resolve()
            for parent in [resolved, *resolved.parents]:
                if (
                    (parent / ".mero-precision-hook-ignore").exists()
                    or (parent / ".nomero").exists()
                    or (parent / ".mero-ignore").exists()
                ):
                    return True
                config_file = parent / ".mero-precision.json"
                if config_file.is_file():
                    try:
                        data = json.loads(config_file.read_text(encoding="utf-8"))
                        if (
                            data.get("hook_disabled") is True
                            or data.get("disabled") is True
                            or data.get("mode") == "off"
                        ):
                            return True
                    except Exception:
                        pass
                if (parent / ".git").exists():
                    break
        except Exception:
            continue
    return False


def _extract_project_name(event: dict[str, Any] | None = None) -> str:
    """Extract a safe project directory name for log attribution."""
    if event:
        ws = _event_value(event, "workspacePaths", "workspace_paths", "cwd", "workspace", default=None)
        if isinstance(ws, list) and ws:
            first = ws[0]
            if isinstance(first, str) and first.strip():
                return Path(first).name or "workspace"
        elif isinstance(ws, str) and ws.strip():
            return Path(ws).name or "workspace"
    try:
        return Path.cwd().name or "workspace"
    except Exception:
        return "unknown"


def evaluate_event(host: str, event: dict[str, Any], config: GateConfig | None = None) -> GateDecision:
    config = config or GateConfig.from_env()
    timestamp = datetime.now(timezone.utc).isoformat()
    project_name = _extract_project_name(event)

    if config.mode == "off" or _is_project_disabled(event):
        return GateDecision(
            schema_version="1.0",
            timestamp=timestamp,
            host=host,
            mode="off",
            project_name=project_name,
            task_key="off",
            score=0,
            threshold=config.threshold,
            components={},
            reasons=[],
            actionable_reasons=[],
            would_enforce=False,
            enforce=False,
            continuation_count=0,
            continuation_reason="",
        )

    transcript_path = _event_value(event, "transcript_path", "transcriptPath", default=None)
    raw_transcript = str(event.get("transcript_text", "") or "") or read_transcript_tail(transcript_path)
    extracted_user, extracted_assistant, flattened = extract_messages(raw_transcript)
    prompt = str(event.get("prompt", "") or extracted_user)
    assistant = str(
        _event_value(
            event,
            "last_assistant_message",
            "lastAssistantMessage",
            default=event.get("assistant", "") or extracted_assistant,
        )
        or ""
    )

    task_key = _task_key(host, event, prompt)
    components, reasons, actionable = _score(prompt, assistant, flattened, event)
    score = sum(components.values())
    would_enforce = score >= config.threshold and bool(actionable)

    state_path = config.state_dir / "state.json"
    log_path = config.state_dir / "events.jsonl"
    state = _load_state(state_path)
    tasks = state.setdefault("tasks", {})
    task_state = tasks.setdefault(task_key, {"continuation_count": 0, "reasons": []})
    continuation_count = int(task_state.get("continuation_count", 0))

    already_continued = bool(_event_value(event, "stop_hook_active", "stopHookActive", default=False))
    enforce = (
        config.mode == "selective"
        and would_enforce
        and continuation_count < config.max_continuations
        and not already_continued
    )
    reason = _continuation_reason(actionable) if would_enforce else ""

    if enforce:
        continuation_count += 1
        task_state["continuation_count"] = continuation_count
        task_state.setdefault("reasons", []).append(reason)
        task_state["updated_at"] = timestamp
        try:
            _write_json_atomic(state_path, state)
        except OSError:
            # Fail open. State failure must not create an unbounded loop.
            enforce = False

    decision = GateDecision(
        schema_version="1.0",
        timestamp=timestamp,
        host=host,
        mode=config.mode,
        project_name=project_name,
        task_key=task_key,
        score=score,
        threshold=config.threshold,
        components=components,
        reasons=reasons,
        actionable_reasons=actionable,
        would_enforce=would_enforce,
        enforce=enforce,
        continuation_count=continuation_count,
        continuation_reason=reason,
    )

    # Privacy default: log hashes and decisions, never transcript text.
    try:
        _append_log(log_path, decision.to_dict())
    except OSError:
        pass

    return decision
