# Public architecture review

Scope: main 2e074cc, read-only code review. No real model or installer was run.

## Strengths
- A shared script/hook store; the Codex renderer provides absolute paths, protection of unrelated hooks and atomic writes: template/.claude/scripts/render_codex_hooks.py:44,66,118; scripts/upgrade.sh:448.
- The Codex transcript adapter takes user/assistant messages instead of tool/reasoning: template/.claude/scripts/flush.py:127.
- The compiler uses temporary staging, an output allowlist, symlink/deletion rejection, a source hash check and per-file atomic promotion: template/.claude/scripts/compile.py:325,443,509,637.

## Findings
1. The Codex adapter is not an independent model engine; the default summary/compile requires the Claude CLI. flush.py:485; compile.py:631.
2. A failed flush is not put into a persistent retry queue; finally deletes the hook input. hooks/session-end.sh:49; flush.py:763,849.
3. There is no Claude/Codex Stop checkpoint. Dedup is only 60 seconds; there is no transcript cursor, and there is a limit of the last 30 messages/15,000 characters. render_codex_hooks.py:15; flush.py:32,210,312. New content can be suppressed or old content repeated.
4. Daily creation and append are not protected by a single lock across sessions. An exists/write_text race can make the first daily content be lost. flush.py:520,730. The state is inside the vault: hooks/lib.sh:12.
5. The compiler's whole output set is not a transaction; a partial success can remain during promotion. compile.py:533. The window for a concurrent edit between the CAS check and the copy is also open.
6. The Last-Session/Threads update depends on agent discipline; the session-end mtime check can mistake another session's write for success. template/CLAUDE.md:33; hooks/session-end.sh:36.
7. Upgrade snapshot + finalize gate is positive, but there is no automatic rollback for an in-place cp. scripts/upgrade.sh:149,347,782. git add -u -- . can pull concurrent tracked changes outside the allowlist into the commit: 787-803.

## Test evidence and gaps
PYTHONDONTWRITEBYTECODE=1 python3 tests/scripts_test.py: 36/36 passed, 7.048 seconds, exit 0. A temporary vault/model stub was used. The repo was not changed.
The existing green suite does not refute the issues above: there is no specific regression evidence for a new transcript suffix within 60 seconds, replay of the same transcript after 60 seconds, the first-daily-creation race between different sessions, automatic retry after a flush failure, an error/rollback in the second promotion copy, a tracked edit outside the allowlist during upgrade, and the real Desktop lifecycle. These scenarios must be added to the new shared runtime acceptance gates.
