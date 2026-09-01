from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mero_precision.gate import GateConfig, evaluate_event


class GateTests(unittest.TestCase):
    def config(self, mode: str = "observe", threshold: int = 6) -> GateConfig:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        return GateConfig(mode=mode, threshold=threshold, max_continuations=1, state_dir=Path(self.temp.name))  # type: ignore[arg-type]

    def test_small_explanation_does_not_enforce(self) -> None:
        decision = evaluate_event(
            "generic",
            {"conversation_id": "a", "prompt": "Explain what this function returns.", "last_assistant_message": "It returns the cached user."},
            self.config("selective"),
        )
        self.assertFalse(decision.would_enforce)
        self.assertFalse(decision.enforce)

    def test_code_change_without_verification_would_enforce(self) -> None:
        decision = evaluate_event(
            "generic",
            {
                "conversation_id": "b",
                "prompt": "Fix the authentication function in the repository and update the tests.",
                "last_assistant_message": "Implemented the fix.",
            },
            self.config("observe", threshold=3),
        )
        self.assertTrue(decision.would_enforce)
        self.assertFalse(decision.enforce)
        self.assertIn("code work has no recorded verification", decision.actionable_reasons)

    def test_selective_mode_enforces_once(self) -> None:
        config = self.config("selective", threshold=3)
        event = {
            "conversation_id": "c",
            "prompt": "Fix the database migration code and update the tests.",
            "last_assistant_message": "Implemented the migration fix.",
        }
        first = evaluate_event("generic", event, config)
        second = evaluate_event("generic", event, config)
        self.assertTrue(first.enforce)
        self.assertFalse(second.enforce)
        self.assertEqual(second.continuation_count, 1)

    def test_successful_verification_removes_verification_debt(self) -> None:
        decision = evaluate_event(
            "generic",
            {
                "conversation_id": "d",
                "prompt": "Fix the null guard in the code.",
                "last_assistant_message": "Fixed the guard and verified it.",
                "transcript_text": "pytest\n12 passed\nexit code 0",
            },
            self.config("selective"),
        )
        self.assertEqual(decision.components["verification_debt"], 0)
        self.assertFalse(decision.enforce)

    def test_old_task_verification_does_not_verify_latest_task(self) -> None:
        transcript = "\n".join(
            [
                json.dumps({"role": "user", "content": "Fix the old function in the code."}),
                json.dumps({"role": "assistant", "content": "Done."}),
                json.dumps({"command": "pytest", "output": "12 passed; exit code 0"}),
                json.dumps({"role": "user", "content": "Fix the new function in the code."}),
                json.dumps({"role": "assistant", "content": "Implemented the new fix."}),
            ]
        )
        decision = evaluate_event(
            "generic",
            {"conversation_id": "latest-task", "transcript_text": transcript},
            self.config("observe", threshold=3),
        )
        self.assertEqual(decision.components["verification_debt"], 2)
        self.assertIn("code work has no recorded verification", decision.actionable_reasons)

    def test_background_work_is_actionable(self) -> None:
        decision = evaluate_event(
            "generic",
            {
                "conversation_id": "e",
                "prompt": "Run the benchmark and summarize it.",
                "last_assistant_message": "The benchmark started.",
                "fully_idle": False,
            },
            self.config("selective", threshold=2),
        )
        self.assertTrue(decision.enforce)
        self.assertIn("Background work is still active", decision.continuation_reason)

    def test_log_does_not_store_prompt_or_raw_session_id(self) -> None:
        config = self.config("observe", threshold=3)
        prompt = "Fix SECRET_PROJECT_NAME in the authentication code."
        session_id = "private-session-identifier"
        evaluate_event(
            "generic",
            {
                "conversation_id": session_id,
                "prompt": prompt,
                "last_assistant_message": "Implemented the fix.",
            },
            config,
        )
        log = (config.state_dir / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(prompt, log)
        self.assertNotIn("SECRET_PROJECT_NAME", log)
        self.assertNotIn(session_id, log)

    def test_project_disabled_via_marker_file(self) -> None:
        with tempfile.TemporaryDirectory() as project_dir:
            marker = Path(project_dir) / ".mero-precision-hook-ignore"
            marker.touch()

            config = self.config("selective", threshold=3)
            event = {
                "conversation_id": "opt-out",
                "workspacePaths": [project_dir],
                "prompt": "Fix the database migration code and update the tests.",
                "last_assistant_message": "Implemented the migration fix.",
            }
            decision = evaluate_event("generic", event, config)
            self.assertFalse(decision.enforce)
            self.assertEqual(decision.mode, "off")

    def test_project_disabled_via_json_config(self) -> None:
        with tempfile.TemporaryDirectory() as project_dir:
            cfg = Path(project_dir) / ".mero-precision.json"
            cfg.write_text('{"disabled": true}', encoding="utf-8")

            config = self.config("selective", threshold=3)
            event = {
                "conversation_id": "opt-out-json",
                "workspacePaths": [project_dir],
                "prompt": "Fix the database migration code and update the tests.",
                "last_assistant_message": "Implemented the migration fix.",
            }
            decision = evaluate_event("generic", event, config)
            self.assertFalse(decision.enforce)
            self.assertEqual(decision.mode, "off")

    def test_bun_and_mise_test_commands_recognized(self) -> None:
        test_cases = [
            "bun test\n3 passed\nexit code 0",
            "bun run test\n5 passed\nexit code 0",
            "mise run test\n10 passed\nexit status 0",
            "mise exec -- bun test\n4 passed\nexit code 0",
            "rtk bun test\n6 passed\nexit code 0",
            "rtk test\nall tests passed\nexit code 0",
        ]
        for transcript in test_cases:
            decision = evaluate_event(
                "generic",
                {
                    "conversation_id": "test-runner",
                    "prompt": "Fix the authentication helper and update tests.",
                    "last_assistant_message": "Implemented fix and verified.",
                    "transcript_text": transcript,
                },
                self.config("selective"),
            )
            self.assertEqual(decision.components["verification_debt"], 0, f"Failed for: {transcript}")
            self.assertFalse(decision.enforce)

    def test_project_name_recorded_in_decision(self) -> None:
        event = {
            "conversation_id": "proj-meta",
            "workspacePaths": ["/home/user/projects/my-awesome-app"],
            "prompt": "Explain what this function returns.",
            "last_assistant_message": "It returns a string.",
        }
        decision = evaluate_event("generic", event, self.config("observe"))
        self.assertEqual(decision.project_name, "my-awesome-app")
        self.assertEqual(decision.to_dict()["project_name"], "my-awesome-app")


if __name__ == "__main__":
    unittest.main()

