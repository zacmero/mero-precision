# Security policy

Mero Precision hooks execute with the permissions of the local coding-agent process. Review the repository before installation.

## v0.1 safety posture

- The completion gate defaults to observe-only.
- The gate never executes project commands.
- The gate stores hashes and decision metadata, not transcript content.
- The gate fails open on internal errors.
- Selective mode allows one continuation by default.
- This is a completion aid, not a security boundary.

Do not rely on Mero Precision to block destructive commands, protect secrets, or enforce sandbox policy. Use a dedicated pre-tool security control for those purposes.

## Reporting

Open a private GitHub security advisory for vulnerabilities that could expose transcript content, create unbounded continuation loops, or execute unintended commands.
