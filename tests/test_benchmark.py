from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmark/scripts/analyze.py"
spec = importlib.util.spec_from_file_location("mero_benchmark_analyze", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BenchmarkTests(unittest.TestCase):
    def test_example_report_has_all_arms(self) -> None:
        records = module.read_records(ROOT / "benchmark/examples/run-records.jsonl")
        manifest = module.read_manifest(ROOT / "benchmark/examples/task-manifest.json")
        report = module.render(records, manifest)
        self.assertIn("| kernel |", report)
        self.assertIn("| skill |", report)
        self.assertIn("| selective |", report)
        self.assertIn("Absolute task success", report)
        self.assertIn("Pilot status: exploratory only", report)

    def test_bootstrap_single_value_is_exact(self) -> None:
        self.assertEqual(module.bootstrap_ci([3.0]), (3.0, 3.0))

    def test_task_level_deltas_average_replicates_before_inference(self) -> None:
        records = [
            {"task_id": "a", "replicate": 1, "arm": "baseline", "quality": {"deterministic_score": 0.1}},
            {"task_id": "a", "replicate": 1, "arm": "skill", "quality": {"deterministic_score": 0.3}},
            {"task_id": "a", "replicate": 2, "arm": "baseline", "quality": {"deterministic_score": 0.2}},
            {"task_id": "a", "replicate": 2, "arm": "skill", "quality": {"deterministic_score": 0.6}},
            {"task_id": "b", "replicate": 1, "arm": "baseline", "quality": {"deterministic_score": 0.5}},
            {"task_id": "b", "replicate": 1, "arm": "skill", "quality": {"deterministic_score": 0.6}},
        ]
        deltas, paired_runs = module.task_level_deltas(records, "skill", "deterministic_score")
        self.assertEqual(paired_runs, 3)
        self.assertEqual(len(deltas), 2)
        self.assertAlmostEqual(deltas[0], 0.3)
        self.assertAlmostEqual(deltas[1], 0.1)

    def test_excluded_records_remain_visible_in_policy_audit(self) -> None:
        records = module.read_records(ROOT / "benchmark/examples/run-records.jsonl")
        excluded = copy.deepcopy(records[0])
        excluded["run_id"] = "excluded-example"
        excluded["exclusion"] = {
            "excluded": True,
            "code": "HOST_CRASH_BEFORE_MODEL",
            "reason": "Synthetic exclusion",
        }
        lines = module.policy_audit([*records, excluded], None)
        text = "\n".join(lines)
        self.assertIn("Excluded records retained: **1**", text)
        self.assertIn("HOST_CRASH_BEFORE_MODEL=1", text)

    def test_experiment_scaffolder_creates_randomized_orders(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "experiment"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "benchmark/scripts/init_experiment.py"),
                    str(target),
                    "--experiment-id",
                    "test-001",
                    "--tasks",
                    "4",
                    "--replicates",
                    "2",
                    "--seed",
                    "42",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["tasks"]), 4)
            self.assertEqual(len(manifest["arm_orders"]), 8)
            for order in manifest["arm_orders"].values():
                self.assertEqual(set(order), set(manifest["arms"]))
            self.assertTrue((target / "tasks/task-01.md").is_file())


if __name__ == "__main__":
    unittest.main()
