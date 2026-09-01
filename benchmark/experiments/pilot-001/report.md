# Mero Precision paired benchmark report

This report keeps writing quality, task completion, and task cost separate. Confidence intervals resample tasks, not replicates.

## Policy audit

- Raw records: **48**.
- Included records: **48**.
- Excluded records retained: **0**.
- Experiment IDs: **1** (pilot-001).
- Preregistration commits: **1** (a1b2c3d4e5f60718293a4b5c6d7e8f9012345678).
- Mero Precision implementation commits: **1** (a1b2c3d4e5f60718293a4b5c6d7e8f9012345678).
- Host/model/settings strata: **1**. Results below are not pooled across strata.
- Included runs with incomplete total-token accounting: **0**.
- Duplicate included task/replicate/arm cells: **0**.
- Missing preregistered cells: **0**.
- Design stage: **pilot**; tasks: **12**; minimum replicates per task: **1**.
- Pilot status: exploratory only. The policy forbids public performance claims from this stage.

Run `benchmark/scripts/validate.py` with the manifest before interpreting effects. This report does not certify preregistration integrity.

## Stratum: pilot-001 · antigravity-cli 2.0.0 · google/gemini-3.7-flash · effort=high · temperature=default · permissions=workspace-write · tools=standard-tools-v1 · env=linux-x86_64-arch

Positive deltas mean that treatment is higher than baseline. Lower is usually better for tokens, turns, retries, tool calls, invocations, and duration.

### Task success

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.33 | 0.00 | [0.08, 0.58] |
| skill | 12 | 12 | 0.33 | 0.00 | [0.08, 0.58] |
| selective | 12 | 12 | 0.33 | 0.00 | [0.08, 0.58] |

### Deterministic score

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.34 | 0.27 | [0.25, 0.44] |
| skill | 12 | 12 | 0.40 | 0.30 | [0.33, 0.48] |
| selective | 12 | 12 | 0.40 | 0.30 | [0.33, 0.48] |

### Total tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | -232.17 | -289.50 | [-326.08, -131.08] |
| skill | 12 | 12 | -358.42 | -372.00 | [-443.08, -275.08] |
| selective | 12 | 12 | -281.33 | -279.00 | [-357.17, -204.42] |

### Semantic score

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.12 | 0.10 | [0.09, 0.15] |
| skill | 12 | 12 | 0.19 | 0.18 | [0.17, 0.21] |
| selective | 12 | 12 | 0.21 | 0.20 | [0.19, 0.23] |

### Input tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | -2.67 | -23.00 | [-82.17, 72.33] |
| skill | 12 | 12 | -47.50 | -83.50 | [-119.67, 32.08] |
| selective | 12 | 12 | -7.83 | 2.50 | [-44.92, 30.33] |

### Cache-read tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |

### Cache-write tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |

### Output tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | -222.67 | -242.50 | [-280.75, -161.17] |
| skill | 12 | 12 | -311.33 | -278.00 | [-369.67, -257.25] |
| selective | 12 | 12 | -268.83 | -255.50 | [-339.50, -195.58] |

### Reasoning tokens

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | -6.83 | -7.50 | [-33.83, 20.17] |
| skill | 12 | 12 | 0.42 | -7.00 | [-32.58, 31.92] |
| selective | 12 | 12 | -4.67 | -4.00 | [-29.33, 20.42] |

### Model invocations

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 0.17 | 0.00 | [0.00, 0.42] |

### Turns

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 0.17 | 0.00 | [0.00, 0.42] |

### Tool calls

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 1.00 | 1.00 | [1.00, 1.00] |
| skill | 12 | 12 | 1.00 | 1.00 | [1.00, 1.00] |
| selective | 12 | 12 | 1.33 | 1.00 | [1.00, 1.83] |

### Retries

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |

### Duration (ms)

| Arm | Independent tasks | Paired runs | Mean task delta | Median task delta | 95% task-bootstrap CI |
|---|---:|---:|---:|---:|---:|
| kernel | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| skill | 12 | 12 | 0.00 | 0.00 | [0.00, 0.00] |
| selective | 12 | 12 | 3333.33 | 0.00 | [0.00, 8333.33] |

### Absolute task success

| Arm | Successful runs | Included runs | Rate |
|---|---:|---:|---:|
| baseline | 8 | 12 | 66.7% |
| kernel | 12 | 12 | 100.0% |
| skill | 12 | 12 | 100.0% |
| selective | 12 | 12 | 100.0% |

## Hook calibration

- Would enforce: **2** included runs.
- Actually triggered: **2** included runs.
- Reviewed labels: TP=2, FP=0, TN=34, FN=0.
- False-positive rate: **0.0%**.
- False-negative rate: **0.0%**.
- Reviewed extra-turn success rate: **100.0%**.

False-positive and false-negative rates use explicit stop-time review labels. They are not inferred from final task success.

## Interpretation boundary

This output is descriptive. Inspect raw artifacts and apply `benchmark/ANALYST_PROMPT.md` before making a claim.

A shorter output does not establish lower total task cost. A favorable average does not erase failed or excluded tasks.
