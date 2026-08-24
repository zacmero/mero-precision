# Specification overlay

A specification is an executable contract for a human or agent.

## Rules

1. Write one independently executable instruction per sentence.
2. Put each condition before the instruction it controls.
3. Use `must` for requirements.
4. Use `can` for capability or permission.
5. Use `may`, `might`, or explicit probability for uncertainty.
6. Use `should` only for a real recommendation, and give its rationale.
7. Use one stable term for each state, component, and operation.
8. Define ambiguous terms before using them as requirements.
9. Give pronouns explicit referents when more than one referent is possible.
10. State precedence when rules can conflict.
11. Separate intended, claimed, observed, and verified state when the distinction affects behavior.
12. Do not permit a state mutation before its required verification.
13. State stop conditions and failure behavior.
14. Do not use examples as hidden requirements.
15. Preserve exact machine names, fields, enums, paths, and commands.

A model can read `should` as optional. Do not use it when failure to comply is an error.
