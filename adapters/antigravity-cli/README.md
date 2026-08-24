# Antigravity CLI adapter

The repository root is an Antigravity CLI plugin:

```text
plugin.json
hooks.json
rules/
skills/
```

The always-on rule loads the compact precision kernel. The Agent Skill remains progressively loaded. The `Stop` hook always runs, but the shared gate defaults to observe-only.

When selective mode finds a concrete completion defect, the hook returns:

```json
{
  "decision": "continue",
  "reason": "Run the missing verification before stopping."
}
```

Any non-`continue` decision allows termination.

## Install

```bash
git clone https://github.com/zacmero/mero-precision.git
cd mero-precision
agy plugin install .
agy plugin enable mero-precision
agy plugin list
```

Antigravity stages installed CLI plugins under:

```text
~/.gemini/antigravity-cli/plugins/<plugin-name>/
```

The bundled hook resolves the default staged path. Set `MERO_PRECISION_PLUGIN_ROOT` only when the plugin lives elsewhere.

Keep the first runs in shadow mode:

```bash
export MERO_PRECISION_MODE=observe
```

Inside AGY, inspect loaded hooks:

```text
/hooks
```

After one task, inspect the shadow decision log:

```bash
tail -n 5 ~/.local/state/mero-precision/events.jsonl
```

## Official contract

- https://antigravity.google/docs/cli/plugins/
- https://antigravity.google/docs/hooks/

Hook paths and payloads remain host-owned. Keep the gate in `observe` mode until the installed CLI passes its adapter fixture.

## Fixture

`fixtures/stop.json` follows the documented Stop-event shape and is used by `make check`. It contains no real transcript data.
