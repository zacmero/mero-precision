# Adapter contract

Each adapter must perform four operations:

1. Read the host lifecycle payload.
2. Supply the latest task, assistant response, and verification evidence when available.
3. Call the shared gate.
4. Translate `enforce` into the host's native continuation action.

## Required behavior

- Register the lifecycle gate continuously.
- Default to `observe` mode.
- Never invoke a model evaluator implicitly.
- Never execute project verification commands from the hook.
- Fail open on parser, timeout, state, or logging errors.
- Limit continuation attempts.
- Inject a targeted reason, not a generic “review your work” prompt.
- Keep host-specific code thin.

## Host translation

| Host | Allow stop | Continue |
|---|---|---|
| Codex CLI | `{}` | `{"decision":"block","reason":"..."}` |
| Antigravity CLI | non-`continue` decision | `{"decision":"continue","reason":"..."}` |
| Pi Agent | no follow-up | hidden `followUp` message with `triggerTurn: true` |

## Transcript caution

Transcript formats are host-owned and can change. An adapter must treat transcript parsing as best-effort. A parsing failure must reduce enforcement confidence, not create a block.
