# Pi Agent adapter

The root `package.json` declares both the Mero Precision skill and the Pi extension.

## Install from GitHub

```bash
pi install git:github.com/zacmero/mero-precision@main
pi list
```

Use `pi config` to inspect or disable the installed skill and extension. Start a new Pi session after installation.

For a project-local installation, add `-l`:

```bash
pi install git:github.com/zacmero/mero-precision@main -l
```

The extension listens for the latest user input and assistant turn. At `agent_settled`, it calls the shared Python gate.

In `observe` mode, the extension records the decision as a non-context session entry.

In `selective` mode, it queues one hidden follow-up message when the gate identifies a concrete completion defect.

## Requirements

- Pi Agent;
- Node.js 20 or later;
- Python 3.11 or later.

## Official contract

- https://pi.dev/docs/latest/skills
- https://pi.dev/docs/latest/extensions
- https://pi.dev/docs/latest/packages

## Fixture

`fixtures/normalized-agent-settled.json` tests the payload produced by the TypeScript extension before it calls the shared gate.
