# Architecture

## Layers

```text
precision kernel
    always-on, very small
          │
          ▼
Agent Skill
    progressively loaded
          │
          ▼
mode references
    loaded by task surface
          │
          ▼
completion gate
    deterministic, always registered
          │
          ├── observe: log only
          └── selective: targeted continuation
```

## Shared gate

Host adapters normalize their lifecycle data into a common event:

```json
{
  "conversation_id": "host session id",
  "prompt": "latest user task",
  "last_assistant_message": "latest answer",
  "transcript_text": "best-effort tool and verification evidence",
  "fully_idle": true
}
```

The shared gate returns a score, components, concrete defects, and a continuation decision.

## Why deterministic first

A model-based critic can detect semantic failures that regular expressions cannot. It also adds input tokens, output tokens, latency, variance, and another failure mode.

Version 0.1 starts with deterministic signals because they are:

- cheap;
- inspectable;
- reproducible;
- easy to calibrate in shadow mode;
- suitable for missing verification and explicit incompleteness.

A future semantic critic must be an independently benchmarked optional layer.

## Continuation safety

- Default mode is `observe`.
- Selective mode requires both a threshold score and an actionable defect.
- Complexity or risk alone cannot continue a task.
- The default maximum is one continuation per task key.
- Codex's native `stop_hook_active` signal suppresses repeat continuation.
- State-write failure disables continuation for that event.
- Parser and logging errors fail open.

## Privacy

The event log stores scores, reasons, hashes, and host metadata. It does not store prompt, assistant, or transcript content.
