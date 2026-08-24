#!/usr/bin/env bash
set -euo pipefail

owner="${1:-zacmero}"
repo="${2:-mero-precision}"
full_name="${owner}/${repo}"

if ! command -v gh >/dev/null 2>&1; then
  printf 'error: GitHub CLI (gh) is required\n' >&2
  exit 1
fi

gh auth status >/dev/null

if gh repo view "$full_name" >/dev/null 2>&1; then
  printf 'error: repository already exists: %s\n' "$full_name" >&2
  exit 1
fi

if [ "$(git branch --show-current)" != "main" ]; then
  printf 'error: publish from the main branch\n' >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  printf 'error: working tree must be clean\n' >&2
  exit 1
fi

gh repo create "$full_name" \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "Maximum signal. Minimum semantic loss for coding agents."

gh repo edit "$full_name" \
  --add-topic agent-skills \
  --add-topic coding-agents \
  --add-topic codex \
  --add-topic antigravity \
  --add-topic pi-agent \
  --add-topic prompt-engineering \
  --add-topic benchmarks

printf 'published: https://github.com/%s\n' "$full_name"
