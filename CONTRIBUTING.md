# Contributing to Avenoxbeyin

Every contribution is valuable, including bug reports, documentation fixes, tests, code reviews and new ideas. This guide is a shared starting point for human contributors and for people who work with AI agents.

**Core approach:** Produce solutions that are not just working code, but genuinely needed, understandable, verifiable and maintainable in the long run.

## 1. Before you start

- Review the [README](README.md) and the relevant [V3 docs](docs/v3/README.md); check whether a similar [issue](https://github.com/avenoxai/avenoxbeyin/issues), [PR](https://github.com/avenoxai/avenoxbeyin/pulls) or existing solution already exists.
- For a bug fix, explain how the problem is reproduced; for a feature proposal, explain which need it meets.
- For new dependencies, major architectural changes and broad features, **discuss it on an issue first**. Avoid uncoordinated parallel PRs on the same topic.
- **One PR, one topic:** Do not mix unrelated refactoring or formatting changes into the same PR. For small documentation and test fixes, opening an issue beforehand is not required. Split large work into small PRs that state their dependencies and can be verified on their own; link PRs that wait on each other and overlapping parallel work in the related issue.

## 2. The project's core principles

| Principle | Expectation |
| --- | --- |
| **Local-first** | The default flow must stay local; user notes and sensitive data must not be sent out without permission. |
| **Markdown source** | User notes are the source of truth; the index and cache must not replace them. |
| **Few dependencies** | Core V3 must run on the **Python 3.11+ standard library**; no new required package, account, API key or background service may be added. |
| **Data and compatibility** | Installation, update, migration and rollback must protect user data and existing behavior. |
| **Privacy and trust** | Private notes, untrusted content, file paths and context boundaries must be protected. |
| **Client consistency** | The shared core behaviors of the supported AI clients must not be broken. |

Before proposing a change, ask: **Can this be solved more simply with the existing structure? Should it be in the core, or optional? What is the long-term maintenance cost?**

Technical contracts: [Runtime](docs/v3/RUNTIME.md) · [Markdown](docs/v3/MARKDOWN.md) · [Update](docs/v3/UPDATE.md).

## 3. Code, tests and compatibility

- Follow the existing code layout; do not add duplicate modules, needless abstractions or dependencies.
- Before a refactor, identify the behavior to be preserved and its points of use. If user-visible behavior changes, update the tests and the docs.
- Support a bug claim with the version/commit (`main@<sha>`), reproduction steps and **real output**. A static analysis or AI agent finding alone is not verification.
- For behavior fixes, a regression test is expected that fails without the fix (`RED`) and passes after it. If it is technically not possible, explain the reason and the alternative verification in the PR; whether to accept the exception is up to the maintainer's judgment.
- In semantic tests, do not change the [fixed fixtures and holdout expectations](docs/v3/SEMANTIC-TEST-CONTRACT.md) merely to raise the score. Use synthetic data and temporary directories instead of a real user vault.

### Review according to the risk of the change

The same weight of process is not applied to every contribution:

| Change | Expected preparation |
| --- | --- |
| **Documentation, tests or a small, isolated fix** | A narrow scope and the relevant verification are enough; an RFC or a comprehensive architecture report is not needed just for a small fix. |
| **Behavior-preserving refactor** | First identify the contracts to preserve, such as external imports/CLI/JSON, file format and test patch points; run characterization and regression tests before/after with the same inputs. |
| **Architecture, security, state, installer or release change** | Before coding, discuss on an issue, in a short RFC/ADR or design summary, the options, risks, out-of-scope items, dependencies, the relevant expert/maintainer review and an applicable upgrade/rollback test plan. |

**Backward compatibility:** Preserve the existing public API/CLI, user data, configuration, file paths, hooks and package contracts as far as possible. If a truly incompatible change is needed, explain in advance the affected users, the transition/migration path, the need for an appropriate deprecation/compatibility layer and the limits of going back; do not start unnecessary deprecation for an internal refactor. When needed, split the compatibility layer first and the internal move afterwards into separate PRs.

The `--human` output of the installed `beyin.py` entry is written as UTF-8 when redirected to a pipe or a file; the encoding of an interactive terminal is preserved.

**Core V3 checks** (at the repo root):

```bash
python -m unittest discover -s tests -p "v3_*test.py"
python scripts/evaluate_v3.py
```

On Windows, use `py -3` instead of `python` if needed. V3 test discovery uses the `tests/v3_*test.py` pattern. In tests that spawn subprocesses, use `tests/v3_package_helpers.inherited_env()`; otherwise `BEYIN_V3_SKIP` coming from an agent environment can misleadingly make tests look successful.

| Area of change | Additional check |
| --- | --- |
| Windows engine/adapter | `python tests/scripts_test_windows.py` and `python tests/antigravity_test.py` |
| POSIX engine/graph | `python3 tests/scripts_test.py` |
| Windows installation | `pwsh -NoProfile -File tests/Test-Preflight.ps1` and the related installation tests |
| Package/update | [Update contract](docs/v3/UPDATE.md) and [release workflow](.github/workflows/release.yml) |

GitHub Actions runs some jobs only when the relevant files change. **A workflow not being triggered does not mean the test passed.** In the PR, state only the commands you actually ran, the environment and the results.

**Rollback:** In PRs that add a persistent setting, a new client name or an installation component, going back to the previous version must be tested. Old `validate()` versions may reject unknown keys **and values outside the supported range**. New persistent settings should be kept in a separate file under `state/` instead of `.beyin-preferences.json`.

## 4. Developing with AI agents

You may use AI tools; however, **the contributor is responsible for the correctness of the code, the tests and the explanations.** An agent's statement is not test or review evidence.

Recommended workflow:

1. **Review:** Have the agent review the related issue, the existing code, the tests and this guide.
2. **Bound it:** Make clear the problem to be solved and the work that is out of scope.
3. **Audit:** Review the generated changes; weed out unrelated refactors, needless abstractions, invented APIs and weakened tests.
4. **Verify:** Actually run the tests; explain the risks, the gaps and the unverified claims in the PR.

Do not get results by loosening tests, do not modify user files without permission, and do not treat an issue as permission for a broad rewrite. Repository settings, authorization, merge and release decisions are the maintainer's responsibility.

## 5. Issues and Pull Requests

**Bug report:** Share the version/commit, operating system, Python version, client, expected/actual behavior, reproduction steps and error output cleaned of sensitive information. You can use the [bug template](.github/ISSUE_TEMPLATE/bug_report.md).

**Feature proposal:** Describe the use case, existing alternatives, possible side effects and maintenance cost. The [feature template](.github/ISSUE_TEMPLATE/feature_request.md) can be used.

**PR:** There is no mandatory convention for the fork/branch name. In the [PR template](.github/PULL_REQUEST_TEMPLATE.md), state what changed and why, the previous/new behavior, the tests applied and their real results. Explain privacy, user data, client/platform differences, platforms not tried and, if needed, installation/rollback risks.

- **`Fixes #N`:** If the issue is fully resolved; the issue closes automatically when merged.
- **`Refs #N`:** For partial work or related discussion.

Take review feedback into account. **Green CI alone is not merge approval; merging to `main` does not automatically mean a release either.**

## 6. Maintainer review and maintenance process

Instead of placing extra obligations on contributors, this section explains how PRs are evaluated:

- Open PRs and issues are reviewed in maintenance rounds. Each PR is evaluated in a separate `git worktree`; claims are verified on current `main` with a real installation, file or database row. Mock data alone is not proof; the `RED` stage of a regression is also checked.
- Contributor commits are not rewritten (no rebase/squash/force-push). Necessary small maintainer fixes are added as separate commits and explained in the PR. PRs are taken with a **merge commit**, preserving authorship.
- Several PRs are tried together in a combined tree in the same round; conflicts are resolved, and the Python **3.11 and 3.14** tests and `scripts/evaluate_v3.py` are run. PRs are merged in order, and the final `main` is compared with the tree that was tested.
- CI runs on Linux, macOS and Windows; for first-time contributors, fork-originated CI runs start after approval. Reproducible bugs without a PR can be fixed by the maintainer and credited to the reporter with `Reported-by`. A status note is written on design and proposal issues. Product direction, merge and publication decisions belong to the maintainer.
- For critical modules it is helpful for reviewers who know the area to take part in the process. If contribution volume requires it, controls such as `CODEOWNERS` or branch rulesets may be evaluated separately; enabling them is the repo administrator's decision, and this guide alone does not create a new merge blocker.

## 7. Privacy and security

Do not include real notes, chat records, personal file paths, private workspaces, tokens or API keys in issues, PRs, test fixtures or logs. Use synthetic data and clean sensitive information out of shared output.

Instead of detailing a serious security vulnerability in a public issue, prefer GitHub's private security reporting channel **if it is available**, or private contact with the maintainer. Enabling the private channel is the maintainer's decision.

---

The goal is not to limit development speed needlessly, but to protect contribution quality and long-term maintainability as the project grows.

**A small but reliable contribution is more valuable than a large feature that is hard to maintain.**
