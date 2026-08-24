# Benchmark harness

The benchmark is deliberately small and inspectable. It uses JSON, JSONL, Python's standard library, and raw files.

## Five-minute setup

Create a pilot skeleton:

```bash
make benchmark-init EXPERIMENT=pilot-001 TASKS=12 REPLICATES=1 SEED=20260824
```

The equivalent direct command is:

```bash
python3 benchmark/scripts/init_experiment.py \
  benchmark/experiments/pilot-001 \
  --experiment-id pilot-001 \
  --tasks 12 \
  --replicates 1 \
  --seed 20260824
```

Then:

1. Replace every `REPLACE_ME` value in the manifest.
2. Write each prompt in `tasks/`.
3. Define deterministic acceptance checks before any run.
4. Commit the complete experiment directory.
5. Put that commit hash in every run record.
6. Run the fixed randomized arm order from `manifest.json`.
7. Preserve raw artifacts and append one JSON object per run.

Validate during collection:

```bash
python3 benchmark/scripts/validate.py \
  benchmark/experiments/pilot-001/run-records.jsonl \
  --manifest benchmark/experiments/pilot-001/manifest.json
```

Require the full matrix and artifact files at the end:

```bash
python3 benchmark/scripts/validate.py \
  benchmark/experiments/pilot-001/run-records.jsonl \
  --manifest benchmark/experiments/pilot-001/manifest.json \
  --artifact-root benchmark/experiments/pilot-001 \
  --require-complete \
  --require-artifacts
```

Generate the paired report:

```bash
python3 benchmark/scripts/analyze.py \
  benchmark/experiments/pilot-001/run-records.jsonl \
  --manifest benchmark/experiments/pilot-001/manifest.json \
  --output benchmark/experiments/pilot-001/report.md
```

Give the complete experiment directory and `ANALYST_PROMPT.md` to another agent for independent review. The agent must run validation before interpretation and must cite decisive run IDs and artifact paths.

## Arms

- `baseline`: no Mero Precision surface is visible.
- `kernel`: precision kernel plus an observe-only gate that cannot alter agent behavior.
- `skill`: kernel plus automatic skill and references; the gate remains observe-only.
- `selective`: skill plus selective completion enforcement.

Do not add or remove an arm after inspecting outcomes.

## Pilot versus claim-candidate

A pilot can use 12 diverse tasks with one run per arm. It calibrates the harness and cannot support public performance claims.

A claim-candidate uses at least 30 tasks and three replicates per arm as a design floor. The floor is not a substitute for interval precision or power analysis.

## Files

- `POLICY.md`: binding experiment policy.
- `RUBRIC.md`: blind semantic-review rubric.
- `RUNNER_SPEC.md`: minimal contract for an agent that implements host runners.
- `schemas/`: machine-readable record contracts.
- `examples/`: valid example data and artifacts.
- `scripts/init_experiment.py`: zero-dependency experiment scaffolder.
- `scripts/validate.py`: zero-dependency policy-aware validator.
- `scripts/analyze.py`: zero-dependency task-level paired summary.
- `ANALYST_PROMPT.md`: instructions for an independent analysis agent.
