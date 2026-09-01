# Mero Precision paired benchmark report

This report keeps writing quality, task completion, and task cost separate. Confidence intervals resample tasks, not replicates.

## Policy audit

- Raw records: **0**.
- Included records: **0**.
- Excluded records retained: **0**.
- Experiment IDs: **0** (none).
- Preregistration commits: **0** (none).
- Mero Precision implementation commits: **0** (none).
- Host/model/settings strata: **0**. Results below are not pooled across strata.
- Included runs with incomplete total-token accounting: **0**.
- Duplicate included task/replicate/arm cells: **0**.
- Missing preregistered cells: **48**.
- Design stage: **pilot**; tasks: **12**; minimum replicates per task: **1**.
- Pilot status: exploratory only. The policy forbids public performance claims from this stage.

Run `benchmark/scripts/validate.py` with the manifest before interpreting effects. This report does not certify preregistration integrity.

## Hook calibration

- Would enforce: **0** included runs.
- Actually triggered: **0** included runs.
- Reviewed labels: TP=0, FP=0, TN=0, FN=0.
- False-positive rate: **—**.
- False-negative rate: **—**.
- Reviewed extra-turn success rate: **—**.

False-positive and false-negative rates use explicit stop-time review labels. They are not inferred from final task success.

## Interpretation boundary

This output is descriptive. Inspect raw artifacts and apply `benchmark/ANALYST_PROMPT.md` before making a claim.

A shorter output does not establish lower total task cost. A favorable average does not erase failed or excluded tasks.
