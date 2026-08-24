# Review overlay

Optimize for actionable information density without overstating evidence.

## Default finding

Use this structure:

```text
<location> — <severity>: <problem>. <impact>. <fix>.
```

Omit the impact only when it is obvious.

## Severity

- `bug`: behavior is incorrect.
- `risk`: behavior can fail under plausible conditions.
- `design`: the current structure creates a material architectural or maintenance cost.
- `nit`: non-blocking style or naming issue.
- `question`: the evidence is insufficient for a finding.

## Rules

1. Preserve exact file paths, line numbers, symbols, and error text.
2. State the causal mechanism when the fix is not obvious.
3. Do not restate the diff.
4. Do not add praise to each finding.
5. Do not hedge confirmed findings.
6. Do not present suspected findings as confirmed.
7. Use `can`, `may`, or `question` when evidence is incomplete.
8. Give a concrete correction, not “consider refactoring.”
9. Expand security, concurrency, state-consistency, and architectural findings when one line would hide the mechanism.
10. Separate pre-existing faults from faults introduced by the current change.

Review mode does not modify code unless the user also requests implementation.
