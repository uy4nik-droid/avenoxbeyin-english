# Shared runtime parity review

Scope: public main 2e074cc was compared with the local .claude/hooks/vault_runtime/engine.py and scripts/VAULT-AUTOMATION.md. Only these two local files were read; no live runtime, service, model or installer was run. No account, private record or credential content was read. Because the local compiler implementation is outside the permitted scope, its staging safety has not been verified.

## Result
The local engine is a foundation that could cover the important gaps of the public lifecycle with a persistent spool/SQLite, a single writer, journal recovery, a transcript cursor, structured receipts and revision checks. But copying it one-to-one does not achieve parity: platform dependencies, parser regressions, a conflict result not turning into a failed job, and paths pinned to a private vault must be separated out. The public compiler's safety layer must be preserved; the local projection engine is not a compiler that replaces it.

## Public features that must not be lost
- Compiler isolated staging; symlink, deletion, output allowlist and source-change checks. Public template/.claude/scripts/compile.py:325,384,443,471,637. The local engine does not call a model; safe_path only rejects escape outside the root, and is not equivalent to the compiler manifest policy that rejects all symlinks (engine.py:246).
- Per-file atomic promotion, fsync and hash-based ingestion. Public compile.py:509,851. The local journal can complete this; atomicity of the whole compile set must be designed separately.
- Recursion guard, a tool-less summary runner, the compiler's restricted tool list and timeout. Public flush.py:383; compile.py:553. Compiler isolation must not be replaced by prompt discipline alone.
- Codex event_msg item_completed variants: public flush.py:139; local normalize reads only user_message/agent_message (engine.py:103). Support for the public variants must be preserved and tested with a golden fixture.
- The public platform locking adapter, Windows installer/PowerShell hook support. Locally there are direct fcntl, os.uname and a macOS default state directory (engine.py:7,121,180). Moving to the public version requires a platform adapter.
- The renderer's protection of unrelated hooks and idempotent wiring; upgrade snapshot, preserved private settings, finalize gate and the latest version stamp. Public render_codex_hooks.py:66,118; scripts/upgrade.sh:347,496,782,820. These must not be skipped when the journal runtime is installed.

## What to take from the local engine and what to fix
- To take: the small metadata spool (168-175), external runtime/single writer (121-157), commit-before-effect journal and recovery (221-265), incremental cursor (267-312), event retry/dead-letter (518-549), task expected revision (555-576), per-source projection and the evidence-kind boundary.
- A conflict is not success: receipt() writes receipt-session meta and deletes the pending entry without checking the false result of owned_write() (340-369); run() makes this succeeded (537-539). When a source receipt or daily entry is preserved and rejected, the event must be conflict/retry, and the gap must not be closed.
- Idempotent effects instead of an exactly-once claim: a fixed event_id must be kept, and a repeated event must be rejected if its payload is not the same. The current enqueue writes to the same spool name, and the DB INSERT OR IGNORE keeps the first payload (168-173,528). A collision/mutated retry must produce an explicit error.
- A single writer provides only a local OS lock. The documents correctly say there is no distributed SQLite (VAULT-AUTOMATION.md:59-61); a revision/conflict resolution is needed for remote concurrent edits.
- The receipt gap heuristic is not verified completion: it uses the assistant text length (engine.py:302). The structured receipt must be canonical, and the heuristic should only produce a visible warning.

## 8 acceptance criteria for Codex / Claude parity
1. The same source task, receipt schema and deterministic projection: the same fixture result must be identical except for the harness name; the model runner requirement must be independent of the harness.
2. Separate real cold-session lifecycle delivery in CLI and Desktop: SessionStart, prompt, Stop, PreCompact, SessionEnd; SessionEnd only enqueues within the time limit. A config hash or fixture does not replace real delivery (document:65).
3. When the same event is delivered again, a single source receipt/daily marker; the same event_id with different content is an explicit conflict. A new transcript suffix must not be lost within 60 seconds.
4. Crash injection: when the process is interrupted and restarted after the spool, after the DB commit, before/after the file replace and during the second projection, there must be no loss/duplicate; a failed event must appear as retry/dead_letter.
5. Parser golden fixture parity: Claude text blocks; Codex user_message, agent_message and item_completed; malformed/partial JSONL, truncate/rotation, long transcript and opt-out; reasoning/tool text must not be carried into notes.
6. Concurrency: when two harnesses work on the same task revision and daily, a single writer, the expected revision conflict and a preserved manual edit; a false owned_write must never become succeeded/gap-cleared.
7. Compiler safety regressions: the public staging allowlist, symlink/deletion rejection, live-source hash, runner timeout/no recursive hook; a recoverable transaction for multi-file promotion. The actual local compiler must not be declared equivalent without a separate review.
8. Clean install/upgrade/rollback on macOS and Windows: unrelated config/skills are preserved; old handlers are inert; trust is verified interactively; canonical source records are not lost; changes outside the allowlist are not committed.

## Migration risks and order
- First the layout/runtime config abstraction: local private names/paths are not carried into the public product; only the necessary algorithms are ported.
- An explicit schema migration and an old log hash import are needed between the public .state JSON and the new SQLite cursor/receipt journal. Otherwise daily may be compiled again or retroactive records may be skipped.
- The old daily auto-summary and the new structured receipt are not left open at the same time. A cutover boundary and an event watermark are recorded; enqueue is verified first, then the old handler is made inert.
- The body of the public personal memory files is preserved; generated view adoption is done with a snapshot and hash comparison. The user's text is not reinterpreted as a receipt.
- Compiler schedule/model/budget are left as a separate policy. The local document preserves a separate model compiler (VAULT-AUTOMATION.md:51); staging equivalence for this code is not yet evidence.
- The public upgrade snapshot is positive but rollback is not automatic; the new install must provide a journal + explicit resume/rollback. The broad scope of git add -u -- . must be removed (scripts/upgrade.sh:802).

## Evidence limit
The public model-stub suite passed 36/36; it does not cover these parity criteria on its own. No test was run for the local engine in this round; the findings are a read-only static review. In particular, new regression tests are needed for a conflict false result turning into a receipt success state and for parser variant loss.

## Coordinator's independent synthetic verification addendum
Evidence the other review agents reported to the coordinator: the local receipt owned_write gives succeeded on a conflict; because the public PR20 health parser expects JSONL, the compiler's pretty JSON error record can show 0 errors, and an AttributeError can occur on a warning entry. This sub-review did not rerun these. Neither bug should be carried over as is: the receipt state transition must depend on the result of all effects; health must explicitly handle valid JSON/JSONL variants with a single-version schema, and a corrupt or unknown record cannot count as healthy.
