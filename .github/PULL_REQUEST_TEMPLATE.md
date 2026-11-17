## Change and rationale

<!-- The concrete problem, the previous and new behavior, why the existing solution falls short.
Limit the change to a single purpose; keep unrelated edits separate. -->

Related record: <!-- Fixes #N for a fully resolved bug; Refs #N for partial work. -->
Base commit: <!-- git merge-base HEAD origin/main -->
<!-- For large work, link the dependent PRs, the dependency order and, if any, the RFC/ADR or design issue. -->

## Verification

<!-- Write the commands you ran, the environment and the real results.
For a bug fix, if possible show the regression that fails before the fix (RED) and passes after.
For a behavior-preserving refactor, compare the API, CLI/JSON, file format and related characterization tests before/after.
If you could not write a test, explain why and the alternative verification; if it was not run, explain the limit of that.
For small documentation changes an appropriate check is enough; do not count a test you did not run as passed. -->

| Command / scenario | Environment | Result |
| --- | --- | --- |
| | | |

## Related contracts

<!-- Fill in only the relevant lines or write not applicable.
If a public API, CLI, hook, state or data format changes, explain the compatibility/migration and, if any, the deprecation approach.
For a risky architecture/security/distribution change, link the alternatives, the relevant reviewer, the test and the upgrade/rollback plan.
These details are not required for pure documentation and small fixes. -->

- Privacy, sensitive folders, untrusted external content and protection of user files:
- Context budget and read-only paths not writing:
- Installed package, source copies and Python stdlib dependencies:
- Windows, macOS and Linux differences:
- If installation, schema or a persistent setting changed, update/rollback verification:
- If a public interface or file format changed, compatibility/transition for existing users:

## Known limits and contributions

<!-- What is out of scope, tests/platforms not run, and who contributed.
If user-visible behavior changed, mention the related documentation update, or the reason if it is missing.
Do not include tokens, keys or real private vault data. -->
