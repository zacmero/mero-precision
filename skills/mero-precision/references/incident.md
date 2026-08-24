# Incident overlay

Write for operators who need an accurate state model under pressure.

## State discipline

Keep these states distinct:

- intended state;
- claimed state;
- observed state;
- verified state;
- unknown state.

An exception does not prove that an external action failed. Treat an uncertain external effect as `unknown` until reconciliation establishes the result.

## Rules

1. Use exact timestamps and time zones.
2. Preserve exact errors and commands.
3. State impact with measured scope when available.
4. Put recovery instructions in execution order.
5. State prerequisites before each irreversible step.
6. Do not claim recovery before external verification.
7. Separate trigger, contributing conditions, and root cause.
8. Separate mitigation from permanent correction.
9. Record failed verification attempts.
10. State what remains unknown.
11. Avoid blame language.
12. Do not compress away concurrency, retry, idempotency, or ordering details.
