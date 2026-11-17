# V3 source and distribution boundaries

This inventory is a preparation record for
[#501](https://github.com/avenoxai/avenoxbeyin/issues/501). The base examined is
`0be8f9961e3bef7a312735cd7461c66ecdca760a` (V3.12.0). The paths and symbols below
show the current behavior in this source; the proposed split boundaries are not an
accepted new architecture. The single source for the contribution flow and test rules
is [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Entry points and responsibilities

| Source | Current responsibility / call surface | Boundary to preserve before splitting |
| --- | --- | --- |
| [`scripts/beyin_entry.py`](../../scripts/beyin_entry.py) | The installed `beyin.py`; `main`, `load_cli`, `human_result` | CLI JSON/stdout, human output and old Windows code page behavior; the installed CLI is loaded dynamically. |
| [`scripts/beyin_v3.py`](../../scripts/beyin_v3.py) | CLI dispatch, state resolution, `hook_reconcile`; becomes `beyin_v3_cli.py` on install | It is not the same source file as the runtime core, despite the same name. Commands, arguments, exit codes and hook reconciliation must be preserved. |
| [`scripts/install_v3.py`](../../scripts/install_v3.py) | `install` / `_install`: managed files, client hook/skill setup, migration and update journal | Runs independently of the ZIP; user regions, exclusions, ownership of old installs and rollback must be preserved. |
| [`beyin_v3.py`](../../template/.claude/scripts/beyin_v3.py) | `MemoryStore`, state and retrieval/context operations | The SQLite/Markdown boundary, public symbols, context budget and privacy/trust filters. |
| [`beyin_v3_sync.py`](../../template/.claude/scripts/beyin_v3_sync.py) | `SyncEngine`, `parse`, `render`, `atomic`; scanning/signature, receipt, task and note operations | Uses the core, index, hygiene, projections, preferences, secrets and notes modules. The parser, scanning and receipt separations are candidates; transaction ownership must stay single. |
| [`beyin_v3_yakala.py`](../../template/.claude/scripts/beyin_v3_yakala.py) | URL/transport safety, card/attachment storage, extractors, platform capture, popup, listener and `install` | The single-file listener outside the vault must be able to run; modules cannot be moved before the distribution decision below is made. |
| [`beyin_v3_projections.py`](../../template/.claude/scripts/beyin_v3_projections.py) | Receipt views, coverage/gaps, quarantine and knowledge freshness | Ownership of derived views, the reality of the source and receipt isolation. |
| [`beyin_v3_hygiene.py`](../../template/.claude/scripts/beyin_v3_hygiene.py) | Boundary, file size, inbox/knowledge checks and task reports | Read-only check paths; a second settings authority must not be created alongside the existing preferences/exclusions modules. |
| [`beyin_v3_hook.py`](../../template/.claude/scripts/beyin_v3_hook.py) | Hook protocol, context/receipt reminder, queue | Latency budget, fail-open and no-memory behavior; the existing separation from `beyin_v3_hook_done.py`. |

`beyin_v3_notes.py`, `beyin_v3_passage.py`, `beyin_v3_index.py`,
`beyin_v3_references.py`, `beyin_v3_preferences.py`, `beyin_v3_exclusions.py`
and the client adapters already carry separate responsibilities. New helpers should
use them without copying them. Similar `default_state` or atomic-write code should not
be unified without examining independent execution and trust boundaries.

## Distribution chain

1. [`build_v3_release.py:build`](../../scripts/build_v3_release.py) puts the three
   entry scripts, the flat `template/.claude/scripts/beyin_v3*.py` files and the
   three base skills into the ZIP. The schema-1 manifest carries the SHA-256 of each
   file.
2. [`beyin_v3_update.py:allowed`](../../template/.claude/scripts/beyin_v3_update.py)
   restricts runtime names with `beyin_v3(?:_[a-z]+)*.py`. Matching the build glob is
   not by itself updater compatibility; a subpackage or an arbitrary helper file may
   be rejected by the old updater.
3. The installer installs the runtime into `.claude/scripts/`, the development CLI as
   `beyin_v3_cli.py`, and the entry script into the vault root as `beyin.py`. The
   user's Markdown sources are not mixed with this managed runtime.
4. On the macOS, Linux and Windows paths, Yakala `install()` copies only its own
   script under `state/yakala/` (`shutil.copy2(script, runner)`). Importing a sibling
   module from the vault does not guarantee that module will be next to this copy.
   Although `listen_mac` / `_hand_over` can switch to the current vault copy, the
   starting path must be able to open on its own. For this reason `beyin_v3_docx.py`
   is loaded optionally; if it is not next to the copy, the DOCX card is left to agent
   review.

For Yakala, the decision between a **generated single-file bootstrap** and an **atomic
runtime package** is open. The decision must cover the old shortcut, the vault not
being found, multiple vaults, offline use, interrupted installation, upgrade and
rollback. This document does not choose one of these options. Moving to a `src/`
source package is also not a file move to be made before the old updater → ZIP →
installer chain is proven.

## Evidence before moving and temporary outputs

- `tests/v3_signature_contract_test.py` and `tests/v3_adjacent_import_test.py`
  protect the public signature and sibling-module loading contracts. Merely
  re-exporting may not keep the global resolution inside the helper the same for old
  `patch.object(original_module, ...)` calls; the relevant patch point must be tested
  separately.
- [`tests/v3_yakala_standalone_cli_test.py`](../../tests/v3_yakala_standalone_cli_test.py)
  runs only the copied single file in isolated Python processes: offline text capture
  → listing → processing → finishing, and read-only help/empty listing when there is
  no vault. It is not evidence for the GUI, the listener, native platform acceptance
  or the distribution architecture decision.
- The existing discovery is `python -m unittest discover -s tests -p "v3_*test.py"`;
  moving tests into a subdirectory may change discovery. The V3, release and Jev
  workflow path filters should also be evaluated together with the file move.
- Besides source-based tests, a real ZIP install, upgrade from an old version,
  rollback and recovery are needed; the Windows/macOS/Linux result is stated
  separately.
- Temporary local agent outputs can be kept under `.agent-work/` at the root and are
  ignored by Git. This ignore rule does not delete existing tracked files.
- `tests/fixtures/v3/`, frozen evaluation inputs, decision-quality evidence and
  historical reports are not moved/deleted in this PR. No bulk cleanup should be done
  without a separate per-file inventory, reference and reproducibility check.

This preparation record does not mean the runtime refactor is complete, a new
distribution design is approved or platform tests have been run.
