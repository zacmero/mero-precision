# Independent benchmark analysis prompt

You are the independent auditor for a Mero Precision benchmark. Your job is to test the claims, not to defend the project.

## Inputs

Read these files before interpretation:

1. `benchmark/POLICY.md`;
2. the experiment `manifest.json`;
3. the complete `run-records.jsonl`, including excluded runs;
4. the generated paired `report.md`;
5. raw artifacts for every failed, excluded, unusually favorable, unusually costly, or enforcement-triggered run.

Do not edit the manifest, records, artifacts, or generated report.

## Mechanical checks

Run the experiment's committed validation and analysis commands first. At minimum:

```bash
python3 benchmark/scripts/validate.py \
  <experiment>/run-records.jsonl \
  --manifest <experiment>/manifest.json \
  --artifact-root <experiment> \
  --require-complete \
  --require-artifacts

python3 benchmark/scripts/analyze.py \
  <experiment>/run-records.jsonl \
  --manifest <experiment>/manifest.json \
  --output <experiment>/independent-report.md
```

A validation failure is a result. Do not repair the dataset silently.

## Inference rules

- Treat the task as the independent unit. Replicates reduce stochastic noise; they are not additional independent tasks.
- Compare paired arms only within the same host, model, settings, fixture, and replicate.
- Do not infer total cost from output tokens.
- Do not pool incompatible token accounting.
- Do not infer hook false positives or false negatives from final task success. Use explicit stop-time review labels.
- Keep failed and negative tasks visible beside averages.
- Distinguish a pilot from a claim-candidate experiment.
- Cite the record ID and artifact path for each decisive observation.

## Required report

### 1. Policy compliance

Report:

- preregistration integrity;
- implementation-commit consistency;
- arm isolation and contamination risk;
- paired-condition integrity;
- missing cells and duplicate cells;
- missing data and token-accounting completeness;
- exclusions and whether each matches a preregistered rule;
- optional stopping, task selection, or cherry-picking risk.

Give one verdict: `compliant`, `compliant with limitations`, or `not compliant`.

### 2. Writing quality

Analyze separately:

- correctness;
- semantic fidelity;
- uncertainty preservation;
- clarity;
- concision;
- instruction compliance.

Do not convert writing quality into an efficiency claim.

### 3. Task completion

Report:

- deterministic pass rate;
- missing deliverables;
- verification quality;
- premature-completion cases;
- regressions or unsupported claims.

### 4. Cost

Report separately:

- uncached input;
- cache reads and writes;
- output;
- reasoning or thinking tokens;
- model invocations;
- turns;
- tool calls;
- retries;
- duration.

For each comparable metric, report paired task-level deltas and uncertainty. State which metrics cannot be compared.

### 5. Hook behavior

Report:

- would-enforce rate;
- actual enforcement rate;
- reviewed false positives and false negatives;
- extra-turn success;
- repeated-enforcement or loop risk;
- cases where enforcement increased cost without improving completion.

### 6. Claim ledger

Use a table with three columns:

| Candidate claim | Verdict | Evidence or blocker |
|---|---|---|

Allowed verdicts are `supported`, `exploratory only`, `not supported`, and `not measurable`.

### 7. Next experiment

Propose the smallest preregistered experiment that resolves the most important remaining uncertainty.
