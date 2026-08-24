# Mero Precision benchmark policy

This policy exists to prevent a writing-quality project from manufacturing an efficiency claim.

## 1. Separate the hypotheses

Every experiment must report these outcomes separately:

1. **Writing quality**: precision, clarity, semantic fidelity, and readability.
2. **Task completion**: requested deliverables, verification, and acceptance checks.
3. **Task cost**: input, cached input, output, reasoning, retries, turns, tool calls, model invocations, and duration.

A shorter answer is not necessarily a cheaper task. A cheaper task is not necessarily a successful task.

## 2. Preregister before measured runs

Before the first measured run, commit:

- the task manifest;
- the exact Mero Precision implementation commit;
- all prompts;
- the arm definitions;
- the model and host settings;
- the acceptance checks;
- the exclusion rules;
- the primary outcomes;
- the analysis command;
- the randomized arm order and seed.

Record that commit hash in every run record. The manifest does not contain its own commit hash because a file cannot truthfully contain the hash of the commit that contains it.

Do not edit task wording, checks, outcomes, or exclusion rules after reading treatment results. Start a new experiment ID when a correction is necessary.

Fix the run count before collection. Do not stop early because an effect looks favorable or continue only because it does not.

## 3. Select tasks before outcomes

Select tasks for the target workload, not for likely token savings.

A balanced corpus must include tasks with different:

- sizes;
- output lengths;
- verification requirements;
- technical domains;
- risk levels;
- likely benefits from compression.

Do not build a public benchmark only from verbose documentation tasks.

Do not count prompt paraphrases, cosmetic variants, or repeated seeds on the same underlying problem as independent tasks. Treat them as replicates.

## 4. Freeze paired conditions

Within a task and replicate, every arm must use:

- the same host and host version;
- the same provider and exact model identifier;
- the same reasoning or effort setting;
- the same temperature and sampling settings when configurable;
- the same permission mode;
- the same tool profile;
- the same environment image or identifier;
- the same repository commit or fixture snapshot;
- the same timeout;
- a fresh conversation;
- an isolated worktree or clean environment.

Do not compare different model versions as if the skill caused the difference.

## 5. Isolate the arms

The four canonical arms are:

- `baseline`: no precision kernel, skill, references, or completion hook;
- `kernel`: precision kernel plus the gate in observe mode;
- `skill`: kernel plus automatic skill and references, with the gate in observe mode;
- `selective`: skill plus selective completion enforcement.

The baseline environment must not expose Mero Precision through another skill directory, repository instruction, plugin cache, global rule, or inherited configuration.

Use separate temporary homes, plugin directories, or explicit host profiles when necessary. Record the tool and configuration profile for every run.

## 6. Randomize arm order

Randomize arm order within each task and replicate using the committed seed.

Record the actual order. Do not always run the baseline first.

## 7. Preserve raw evidence

Each run must retain:

- exact prompt;
- raw host output;
- transcript or event stream when available;
- tool-call log;
- provider or host usage payload;
- final response;
- repository diff;
- acceptance-check output;
- gate events;
- timing data;
- environment metadata.

Raw artifacts are canonical. Summaries are derived.

Do not rewrite or clean transcripts before analysis.

## 8. Record all runs

Record timeouts, tool failures, refusals, malformed output, and crashes.

Exclude a run only when a preregistered rule applies. Keep excluded records in the dataset with:

- `excluded: true`;
- a stable exclusion code;
- a factual explanation.

Never remove an unfavorable run because it looks anomalous.

## 9. Token accounting

Report these fields separately when the host exposes them:

- uncached input tokens;
- cache-read tokens;
- cache-write tokens;
- output tokens;
- reasoning or thinking tokens;
- total provider-counted tokens;
- number of model invocations.

Set `tokens.complete` to `false` when any material category is unavailable.

When accounting is incomplete:

- label the metric `partial`;
- do not call it total cost;
- do not infer missing reasoning tokens;
- do not compare provider billing from incompatible accounting systems.

Output-token reduction can be reported as output-token reduction only.

## 10. Quality measurement

Prefer deterministic acceptance checks:

- tests;
- build results;
- lint rules tied to the task;
- schema validation;
- file and symbol assertions;
- exact requested deliverable checks.

Do not create acceptance checks after seeing the generated solution.

For semantic quality, use blind review:

- hide arm labels;
- randomize answer order;
- use the committed rubric in `benchmark/RUBRIC.md`;
- separate correctness, semantic fidelity, clarity, and concision;
- record judge identity and model when an LLM judge is used;
- report same-family judge bias as a limitation.

An LLM judge cannot replace deterministic task checks.

## 11. Calibrate the hook before efficacy testing

In `observe` mode, record:

- score;
- would-enforce decision;
- concrete reason;
- actual task completeness;
- a reviewed label: true positive, false positive, true negative, or false negative.

Do not enable selective enforcement until the false-positive rate is acceptable for the target workload.

Report:

- enforcement rate;
- false-positive rate;
- false-negative rate;
- extra-turn success rate;
- repeated-enforcement rate.

Do not infer false-positive or false-negative labels from final task success. A reviewer must label the stop-time decision.

## 12. Use the task as the unit of inference

Replicates reduce stochastic noise. They do not turn one task into several independent tasks.

Calling tasks independent is a design claim. When tasks share the same underlying defect, fixture, or generated template, treat that relationship as clustering and disclose it.

For confidence intervals:

1. compute paired treatment-minus-baseline deltas within each task and replicate;
2. average replicate deltas within each task;
3. resample tasks, not individual runs.

Report both the number of paired runs and the number of independent tasks.

## 13. Primary comparisons

Use paired comparisons against `baseline` within each host, model, and settings stratum.

Report:

- independent tasks;
- complete paired runs;
- mean task-level delta;
- median task-level delta;
- 95% task-bootstrap interval;
- task success count and rate;
- missing-data count;
- exclusion count.

Do not aggregate across hosts or models without presenting each stratum separately.

Treat unregistered secondary metrics as exploratory.

## 14. Pilot and claim-candidate stages

A pilot can use 12 diverse tasks and one replicate per arm. It validates adapters, records, checks, and likely variance. It cannot support a public performance claim.

A claim-candidate experiment should use at least 30 preregistered tasks and three replicates per arm as a design floor. This floor is not proof of adequate statistical power. The public report must also justify precision using observed variance, interval width, or a power analysis.

Do not call an experiment claim-ready merely because it meets the numeric floor.

## 15. Claim gates

A public token-efficiency claim requires all of the following:

- a preregistered claim-candidate design;
- complete token accounting for the claimed metric;
- no material task-success regression;
- raw records and artifacts published;
- task-level paired confidence interval reported;
- unfavorable tasks retained;
- limitations stated next to the claim;
- evidence from more than one task category;
- no unresolved arm contamination.

A completion-quality claim requires deterministic checks or blinded review on the full preregistered task set.

A writing-quality claim must not be described as a token-saving claim.

## 16. Independent analysis

The analysis agent receives:

- this policy;
- the preregistration commit;
- the task manifest;
- all run records, including exclusions;
- raw artifact paths;
- the generated paired report;
- `benchmark/ANALYST_PROMPT.md`.

The analysis agent must identify policy violations before interpreting effects.

The project owner can disagree with the analysis, but must not alter raw records to resolve the disagreement.
