# Commit overlay

Write commit messages that preserve intent and non-obvious rationale.

## Subject

Use Conventional Commits when the repository does not define another convention:

```text
<type>(<scope>): <imperative summary>
```

- Use an imperative verb.
- Prefer 50 characters or fewer.
- Do not exceed 72 characters.
- Do not add a trailing period.
- Match repository capitalization conventions.

Supported default types:

`feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`.

## Body

Omit the body when the subject fully explains the change.

Include a body for:

- non-obvious rationale;
- breaking changes;
- security fixes;
- data migrations;
- compatibility constraints;
- reverts;
- issue references that affect future maintenance.

Explain why the change exists. Do not narrate every modified file.

Preserve exact issue identifiers and required trailers.

Do not add AI attribution unless the repository explicitly requires it.
