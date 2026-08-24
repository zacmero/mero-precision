# Benchmark runner implementation contract

This file is for an agent that implements a Codex, Pi, or Antigravity benchmark runner.

## Required input

The runner receives:

- `manifest.json`;
- one task ID;
- one replicate number;
- one arm;
- the preregistration commit;
- the exact Mero Precision implementation commit from the manifest;
- an output directory.

## Required procedure

1. Read the task and the preregistered arm order.
2. Create a fresh conversation and isolated workspace.
3. Expose only the selected arm's Mero Precision surfaces.
4. Apply the exact manifest settings.
5. Save the exact prompt before execution.
6. Run the host until completion or the fixed timeout.
7. Save raw output, transcript, usage payload, tool log, diff, gate events, and environment metadata.
8. Run only the preregistered acceptance checks.
9. Append one valid run record to `run-records.jsonl`.
10. Record failures instead of retrying silently.

## Arm isolation

- `baseline`: use a clean host profile with no Mero Precision rule, skill, plugin, or hook.
- `kernel`: expose only `rules/precision-kernel.md`; register the gate in `observe` mode.
- `skill`: expose the kernel and skill; keep the gate in `observe` mode.
- `selective`: expose the kernel and skill; set the gate to `selective`.

Do not keep the repository itself in a host skill-search path during the baseline run.

## Retry rule

A provider or transport retry must remain part of the same run and increment `retries`.

Do not discard and rerun a bad model outcome. Start a replacement run only when a preregistered exclusion rule applies, and retain the excluded record.

## Output contract

Use `benchmark/schemas/run-record.schema.json` and the example JSONL as the canonical shape.

The runner must not calculate public claims. Its job is evidence collection.
