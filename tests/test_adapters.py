from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def run_process(self, command: list[str], fixture: Path, mode: str, threshold: int = 3) -> dict:
        with tempfile.TemporaryDirectory() as state_dir:
            env = {
                **os.environ,
                "MERO_PRECISION_MODE": mode,
                "MERO_PRECISION_THRESHOLD": str(threshold),
                "MERO_PRECISION_STATE_DIR": state_dir,
            }
            result = subprocess.run(
                command,
                input=fixture.read_text(encoding="utf-8"),
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT,
                check=True,
            )
        return json.loads(result.stdout)

    def test_codex_wrapper_observes_without_blocking(self) -> None:
        output = self.run_process(
            [sys.executable, str(ROOT / "adapters/codex-cli/stop_gate.py")],
            ROOT / "adapters/codex-cli/fixtures/stop.json",
            "observe",
        )
        self.assertEqual(output, {})

    def test_codex_wrapper_can_request_continuation(self) -> None:
        output = self.run_process(
            [sys.executable, str(ROOT / "adapters/codex-cli/stop_gate.py")],
            ROOT / "adapters/codex-cli/fixtures/stop.json",
            "selective",
        )
        self.assertEqual(output.get("decision"), "block")
        self.assertIn("verification", output.get("reason", ""))

    def test_antigravity_wrapper_observes_without_continuing(self) -> None:
        output = self.run_process(
            [sys.executable, str(ROOT / "adapters/antigravity-cli/stop_gate.py")],
            ROOT / "adapters/antigravity-cli/fixtures/stop.json",
            "observe",
        )
        self.assertEqual(output, {"decision": "allow"})

    def test_antigravity_wrapper_can_continue(self) -> None:
        output = self.run_process(
            [sys.executable, str(ROOT / "adapters/antigravity-cli/stop_gate.py")],
            ROOT / "adapters/antigravity-cli/fixtures/stop.json",
            "selective",
        )
        self.assertEqual(output.get("decision"), "continue")
        self.assertIn("verification", output.get("reason", ""))

    def test_pi_normalized_payload_can_request_follow_up(self) -> None:
        fixture = ROOT / "adapters/pi-agent/fixtures/normalized-agent-settled.json"
        env_command = [sys.executable, "-m", "mero_precision.cli", "--host", "pi"]
        with tempfile.TemporaryDirectory() as state_dir:
            env = {
                **os.environ,
                "PYTHONPATH": str(ROOT / "src"),
                "MERO_PRECISION_MODE": "selective",
                "MERO_PRECISION_THRESHOLD": "3",
                "MERO_PRECISION_STATE_DIR": state_dir,
            }
            result = subprocess.run(
                env_command,
                input=fixture.read_text(encoding="utf-8"),
                capture_output=True,
                text=True,
                env=env,
                cwd=ROOT,
                check=True,
            )
        output = json.loads(result.stdout)
        self.assertTrue(output.get("enforce"))
        self.assertIn("verification", output.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
