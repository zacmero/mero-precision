# Memory overlay

Load this overlay only when the user explicitly requests persistent-memory work.

Persistent context has a higher semantic cost than ordinary output.

## Rules

1. Preserve source, timestamp, confidence, and temporal scope.
2. Preserve contradictions and later reinterpretations.
3. Do not convert an inference into a fact.
4. Do not convert a past preference into a permanent preference.
5. Do not overwrite history to make the current summary cleaner.
6. Deduplicate repeated statements only when their meaning is identical.
7. Preserve rationale when it affects future decisions.
8. Preserve identifiers, dates, quantities, and project names exactly.
9. Mark unknown or disputed claims explicitly.
10. Back up the original before destructive compression.
11. Prefer structured fields over telegraphic fragments.
12. Do not auto-trigger this overlay.

Compression can remove repetition. It must not remove provenance or evolution.
