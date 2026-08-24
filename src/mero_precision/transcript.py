from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

_MAX_TRANSCRIPT_BYTES = 2_000_000


def read_transcript_tail(path_value: str | None) -> str:
    """Read a bounded transcript tail. Return an empty string on any error."""
    if not path_value:
        return ""

    try:
        path = Path(path_value).expanduser()
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - _MAX_TRANSCRIPT_BYTES))
            data = handle.read()
        return data.decode("utf-8", errors="replace")
    except (OSError, ValueError):
        return ""


def _content_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(filter(None, (_content_to_text(item) for item in value)))
    if isinstance(value, dict):
        for key in ("text", "content", "message", "prompt", "output", "result", "error"):
            if key in value:
                text = _content_to_text(value[key])
                if text:
                    return text
    return ""


def _walk_objects(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_objects(child)


def extract_messages(transcript_text: str) -> tuple[str, str, str]:
    """Extract the latest task and its best-effort evidence window.

    Transcript formats are host-owned and unstable. Verification evidence from
    an older user task must not satisfy the current task, so the returned text
    resets whenever a later user message is found. Parsing failure falls back
    to bounded plain text and never becomes a reason to block an agent.
    """
    latest_user = ""
    latest_assistant = ""
    all_text: list[str] = []
    latest_turn: list[str] = []
    saw_user = False

    if not transcript_text:
        return latest_user, latest_assistant, ""

    values: list[Any] = []
    stripped = transcript_text.strip()

    try:
        values.append(json.loads(stripped))
    except json.JSONDecodeError:
        for line in transcript_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                values.append(json.loads(line))
            except json.JSONDecodeError:
                all_text.append(line)
                if saw_user:
                    latest_turn.append(line)

    for value in values:
        for obj in _walk_objects(value):
            role = str(obj.get("role", obj.get("type", ""))).lower()
            text = _content_to_text(obj.get("content", obj.get("message", obj.get("text"))))

            if text:
                all_text.append(text)
                if role in {"user", "human", "input"}:
                    latest_user = text
                    latest_assistant = ""
                    latest_turn = [text]
                    saw_user = True
                elif role in {"assistant", "model", "ai"}:
                    latest_assistant = text
                    if saw_user:
                        latest_turn.append(text)
                elif saw_user:
                    latest_turn.append(text)

            for key in ("command", "output", "result", "error", "prompt"):
                extra = _content_to_text(obj.get(key))
                if extra and extra != text:
                    all_text.append(extra)
                    if saw_user:
                        latest_turn.append(extra)

    if saw_user and latest_turn:
        evidence = latest_turn
    elif all_text:
        evidence = all_text
    else:
        evidence = [transcript_text]

    return latest_user, latest_assistant, "\n".join(evidence)
