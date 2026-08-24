# Contributing

Contributions are welcome when they preserve the project's central invariant:

> Brevity must not change meaning.

## Before proposing a change

1. State the failure mode that the change addresses.
2. Separate writing quality, task completion, and token cost.
3. Add a deterministic test when the behavior is deterministic.
4. Add a benchmark task when the claim is empirical.
5. Preserve raw benchmark artifacts.
6. Do not add public performance claims without paired evidence.

## Adapter changes

For host-specific work:

- cite the current official host contract in the adapter README;
- keep host wrappers thin;
- translate into the shared gate event model;
- default new enforcement paths to `observe`;
- fail open on parsing, logging, or configuration errors;
- add a fixture for the host payload.

## Benchmark changes

Read `benchmark/POLICY.md` before editing the harness. A benchmark pull request must not:

- remove failed runs without a preregistered exclusion reason;
- mix model versions in one paired comparison;
- infer total cost from output tokens;
- use the treatment output to modify acceptance checks;
- publish only favorable task subsets.

## Development

```bash
make check
```

The benchmark policy is intentionally zero-dependency. Do not add an analysis dependency unless the same result cannot be implemented clearly with the Python standard library.
