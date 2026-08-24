from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .gate import GateConfig, evaluate_event


def _host_output(host: str, decision: dict[str, Any]) -> dict[str, Any]:
    enforce = bool(decision.get("enforce"))
    reason = str(decision.get("continuation_reason", ""))

    if host == "codex":
        return {"decision": "block", "reason": reason} if enforce else {}
    if host == "antigravity-cli":
        return {"decision": "continue", "reason": reason} if enforce else {"decision": "allow"}
    return {"enforce": enforce, "reason": reason, "decision": decision}


def run_hook(host: str) -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise TypeError("hook input must be a JSON object")
        decision = evaluate_event(host, event, GateConfig.from_env()).to_dict()
        json.dump(_host_output(host, decision), sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")
        return 0
    except Exception as exc:  # fail open by design
        if host == "antigravity-cli":
            json.dump({"decision": "allow"}, sys.stdout)
        elif host == "codex":
            json.dump({}, sys.stdout)
        else:
            json.dump({"enforce": False, "reason": "", "error": type(exc).__name__}, sys.stdout)
        sys.stdout.write("\n")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mero Precision completion gate")
    parser.add_argument("--host", default="generic", choices=["generic", "codex", "antigravity-cli", "pi"])
    args = parser.parse_args()
    return run_hook(args.host)


if __name__ == "__main__":
    raise SystemExit(main())
