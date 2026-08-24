# Mero Precision

[![validate](https://github.com/zacmero/mero-precision/actions/workflows/validate.yml/badge.svg)](https://github.com/zacmero/mero-precision/actions/workflows/validate.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Maximum signal. Minimum semantic loss.**

Mero Precision is a precision-first communication and completion discipline for coding agents. It reduces semantic waste without asking the model to think less, speak in fragments, or flatten uncertainty.

The project has two layers:

1. An Agent Skill that controls technical communication.
2. Optional CLI adapters that observe task completion and selectively request another pass.

> **Status: v0.1.0 experimental.** The completion gate defaults to `observe` mode. It records what it would enforce, but it does not continue the agent automatically.

## Why this exists

Aggressive terseness can shorten output while damaging grammar, causality, scope, uncertainty, and execution order. Mero Precision takes a different approach:

```text
required reasoning depth
        ↓
semantic firewall
        ↓
precise rendering
        ↓
minimum useful prose
```

The core rule is simple:

> Compress the presentation, not the reasoning.

## What Mero Precision protects

- negation and scope;
- conditions and exceptions;
- ordering and dependencies;
- quantities, dates, thresholds, and units;
- uncertainty and confidence;
- correlation versus causation;
- exact technical terms, code, commands, paths, and errors;
- requested deliverables and verification obligations.

## Automatic modes

The base `session` mode applies to technical work. The skill loads additional references when the task requires them:

| Overlay | Applies to |
|---|---|
| `review` | Code and pull-request review |
| `commit` | Commit messages |
| `docs` | READMEs, runbooks, API docs, release notes |
| `spec` | Skills, prompts, AGENTS.md, protocols, requirements |
| `research` | Papers, experiments, evidence, architecture analysis |
| `incident` | Debugging, outages, postmortems, recovery |
| `memory` | Explicit persistent-context compression only |

The user does not need to select a mode. The agent classifies the output surface and reads the matching reference.

## Multi-host layout

This repository is structured as a native package for three CLI-oriented hosts:

| Host | Native surface | v0.1 status |
|---|---|---|
| Codex CLI | Agent Skill + `Stop` hook | Shadow gate implemented |
| Antigravity CLI | Plugin rule + skill + `Stop` hook | Shadow gate implemented |
| Pi Agent | Pi package + TypeScript extension + skill | Shadow gate implemented |

All three adapters call the same Python scoring engine. Host wrappers only translate lifecycle events and continuation responses.

## Install

### Antigravity CLI — full plugin

```bash
git clone https://github.com/zacmero/mero-precision.git
cd mero-precision
agy plugin install .
agy plugin enable mero-precision
agy plugin list
```

Keep the gate in shadow mode first:

```bash
export MERO_PRECISION_MODE=observe
```

Open `/hooks` inside AGY, then inspect `~/.local/state/mero-precision/events.jsonl` after a task.

### Pi Agent — skill plus lifecycle extension

```bash
pi install git:github.com/zacmero/mero-precision@main
pi list
```

Use `pi config` to inspect the installed resources. Add `-l` for a project-local installation.

### Codex CLI — full plugin

```bash
codex plugin marketplace add zacmero/mero-precision --ref main
codex plugin marketplace list
```

Open `/plugins` in Codex, select the **Mero Protocol** marketplace, install and enable `mero-precision`, then start a new session. Open `/hooks` to review and trust the command hook.

### Skill-only installation

Copy or link `skills/mero-precision/` into an Agent Skills directory used by your host. For Codex user scope:

```bash
git clone https://github.com/zacmero/mero-precision.git
mkdir -p ~/.agents/skills
ln -s "$(pwd)/mero-precision/skills/mero-precision" ~/.agents/skills/mero-precision
```

This activates the instruction layer without lifecycle enforcement.

## Completion gate modes

The hook is always registered when its adapter is installed. Its behavior is controlled by `MERO_PRECISION_MODE`:

| Mode | Behavior |
|---|---|
| `off` | Return immediately and do not log |
| `observe` | Score and log; never continue the agent |
| `selective` | Continue only when the score crosses the threshold and a concrete completion defect exists |

Default:

```bash
export MERO_PRECISION_MODE=observe
```

Enable selective enforcement after reviewing shadow data:

```bash
export MERO_PRECISION_MODE=selective
export MERO_PRECISION_THRESHOLD=6
export MERO_PRECISION_MAX_CONTINUATIONS=1
```

The gate fails open. A parser error cannot trap an agent in a loop. Decision logs contain hashes and scoring metadata, not transcript text.

## What the gate scores

The deterministic v0.1 gate scores five dimensions:

- task complexity;
- external-effect risk;
- verification debt;
- epistemic risk;
- unresolved failure state.

Complexity or risk alone never forces a continuation. The gate also requires an actionable defect, such as:

- code work with no successful verification;
- a failed verification command;
- explicit unfinished work;
- an execution error;
- active background work at stop time.

The gate does not use another model in v0.1.

## Benchmark doctrine

Mero Precision does **not** claim a token-saving percentage.

The benchmark separates three hypotheses:

1. Does Mero Precision improve output quality?
2. Does it improve verified task completion?
3. Does it reduce total task cost?

Output tokens are not total cost. Input, cached input, reasoning tokens, retries, tool turns, and enforcement turns must be reported separately when the host exposes them.

The canonical policy is in [`benchmark/POLICY.md`](benchmark/POLICY.md). It requires preregistered tasks, fresh sessions, fixed model settings, raw artifacts, paired comparisons, and explicit missing-data labels.

Run the complete repository check:

```bash
make check
```

The benchmark itself has no third-party Python dependency. Its explicit equivalent is:

```bash
python3 benchmark/scripts/validate.py \
  benchmark/examples/run-records.jsonl \
  --manifest benchmark/examples/task-manifest.json \
  --artifact-root benchmark/examples \
  --require-complete \
  --require-artifacts

python3 benchmark/scripts/analyze.py \
  benchmark/examples/run-records.jsonl \
  --manifest benchmark/examples/task-manifest.json \
  --output /tmp/mero-precision-report.md
```

## Repository map

```text
skills/mero-precision/       canonical Agent Skill
rules/precision-kernel.md    tiny always-on instruction kernel
src/mero_precision/          shared deterministic gate
adapters/                    host-specific wrappers and instructions
extensions/pi/               Pi lifecycle adapter
benchmark/                   policy, schemas, examples, analyzer
benchmark/experiments/       generated experiment directories
hooks/                       Codex plugin hook definition
hooks.json                   Antigravity plugin hook definition
```

## Design boundaries

Mero Precision is not intended to control fiction, poetry, lyrics, character dialogue, emotional correspondence, or brand voice unless explicitly requested.

The `memory` overlay never auto-triggers. Persistent context has a higher semantic cost than ordinary chat output.

## Roadmap

- Calibrate the deterministic score in shadow mode.
- Add host conformance fixtures from real transcripts.
- Measure false positives and false negatives.
- Run the four-arm benchmark.
- Consider an optional semantic critic only if deterministic enforcement is insufficient.
- Publish claims only after raw paired results support them.

## Acknowledgments

The project is independently authored. It is conceptually inspired by the routing discipline of Caveman and the complete-grammar, stable-terminology approach of SimpleEnglish. See [`NOTICE.md`](NOTICE.md).

## License

MIT. See [`LICENSE`](LICENSE).
