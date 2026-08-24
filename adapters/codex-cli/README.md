# Codex CLI adapter

The Codex adapter bundles the canonical Agent Skill and a native `Stop` hook.

Codex runs the hook whenever a turn attempts to stop. When selective mode finds a concrete completion defect, the wrapper returns:

```json
{
  "decision": "block",
  "reason": "Run the missing verification before stopping."
}
```

For `Stop`, this asks Codex to continue. It does not reject the completed turn.

## Full plugin installation

Add this repository as a Codex marketplace source:

```bash
codex plugin marketplace add zacmero/mero-precision --ref main
codex plugin marketplace list
```

Then launch Codex and open:

```text
/plugins
```

Select the **Mero Protocol** marketplace, install `mero-precision`, and enable it. Start a new Codex session after installation.

The first time the command hook is discovered, open:

```text
/hooks
```

Review and trust the exact Mero Precision hook definition. Codex skips untrusted command hooks.

## Skill-only installation

For the instruction layer without the completion hook:

```bash
git clone https://github.com/zacmero/mero-precision.git
mkdir -p ~/.agents/skills
ln -s "$(pwd)/mero-precision/skills/mero-precision" ~/.agents/skills/mero-precision
```

Codex follows symlinked skill folders. Restart Codex only if the skill does not appear automatically.

## Default behavior

```bash
export MERO_PRECISION_MODE=observe
```

Review `~/.local/state/mero-precision/events.jsonl` before enabling enforcement.

## Official contract

- https://developers.openai.com/codex/hooks/
- https://developers.openai.com/codex/skills/
- https://developers.openai.com/plugins/build/plugins

The adapter treats the transcript as best-effort because Codex documents its transcript format as unstable.

## Fixture

`fixtures/stop.json` is a synthetic Stop payload for local adapter tests. Run `make check` to verify observe and selective translations.
