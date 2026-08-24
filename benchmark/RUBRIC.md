# Blind semantic-review rubric

Reviewers must not see arm names. Randomize response order and assign opaque response IDs.

Score each dimension from 0 to 4.

## Correctness

- **4**: Correct, complete, and consistent with available evidence.
- **3**: Correct with a minor omission that does not change the conclusion.
- **2**: Mixed correctness or one material unsupported claim.
- **1**: Major errors, but some useful content remains.
- **0**: Fundamentally incorrect or non-responsive.

## Semantic fidelity

- **4**: Preserves negation, scope, uncertainty, causality, chronology, conditions, and terminology.
- **3**: One minor distinction is weakened without changing the practical result.
- **2**: One material distinction is lost or overstated.
- **1**: Several material distinctions are lost.
- **0**: Compression reverses or substantially changes the meaning.

## Clarity

- **4**: Easy to understand in one pass; structure matches the task.
- **3**: Clear with minor friction.
- **2**: Understandable after rereading.
- **1**: Ambiguous or structurally confusing.
- **0**: Not usable.

## Concision

- **4**: No removable prose without information loss.
- **3**: Small amount of removable prose.
- **2**: Noticeable repetition or unnecessary framing.
- **1**: Excessively verbose or telegraphic enough to impede reading.
- **0**: Length or compression makes the answer unusable.

## Instruction compliance

- **4**: Satisfies every requested deliverable and format constraint.
- **3**: One non-material formatting miss.
- **2**: One requested component is incomplete.
- **1**: Several requested components are missing.
- **0**: Does not perform the requested task.

## Recording

Record:

- opaque response ID;
- reviewer or judge ID;
- judge model and version, when applicable;
- all five scores;
- one factual note for every score below 4;
- pairwise preference and reason, when comparing two outputs.

Normalize a composite score only after preregistering its weights. Do not invent weights after viewing results.
