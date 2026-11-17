# Chat trace: opt-in prototype

This proposal tries to turn a short summary of a meaningful chat, one in which no
file was edited, into a re-findable Markdown source. The design decision belongs
to the maintainer. It is off by default; it does not collect transcripts, does
not call a model and adds no new Stop blocker. Old Claude Code sessions are read
only through the explicit backfill command below.

## Usage

Inside an installed vault:

```sh
python beyin.py chat-trace status
python beyin.py chat-trace on
python beyin.py chat-trace write --harness claude --session RECEIPT_SESSION --file trace.txt
python beyin.py chat-trace off
```

`RECEIPT_SESSION` is the 24-digit hash the hint gives. `trace.txt` is a short
UTF-8 summary that the user or agent prepared on purpose; `--file -` accepts
stdin and `--text` accepts a short text. **A single paragraph, date included, is
at most 450 characters**; a longer text is rejected, not truncated. The code does
not guess which conversation is meaningful.

The source it writes is `knowledge/conversations/YYYY-MM.md`. Each entry is
separated by a blank line; the existing passage search can evaluate separate
paragraphs. Sending the same paragraph again on the same day produces no
duplicate. For a new outcome, another short paragraph can be written. When a
monthly file passes 256,000 bytes, no automatic pruning happens; the user is
asked to review it. An existing file of the same name that does not belong to
this prototype is not touched.

Writing uses the existing `note-read`/`note-edit` lock, SHA comparison, secret
filter and source validation. Summaries are not presented as verified decisions.
`visibility: internal` allows normal local search; `remote_allowed: false` removes
the note from Jev's extra provider candidates. A trace that enters normal client
context is subject to the data flow of the AI client in use.

## Hints

Only `UserPromptSubmit` is counted. The first hint comes on the 2nd unrecorded
human turn, and later hints come 8 turns apart; there are at most 3 hints per
session. This is a prompt counter; it does not claim to verify two completed
responses or a meaningful outcome. A new receipt for the same session, or a
verified explicit trace write, covers the earlier counters; a new unrecorded
interval starts again from 2 turns, and the total limit of 3 is not reset. If an
event/turn ID exists, an immediate repeat delivery is not counted.

The human distinction is a narrow **pilot origin policy**, not an access security
gate:

| Client | Origin counted | Stays silent |
| --- | --- | --- |
| Claude | `CLAUDE_CODE_ENTRYPOINT=claude-desktop` or attended=`1/true` | `sdk-cli`, `cli`, attended=`0/false`, known synthetic prompts and unclear origin |
| Codex | In the first `session_meta` line of the file the hook provides: a matching `id`, `originator=codex_cli_rs`, `source=cli` | `codex_exec`, sub-agent, other/unclear origin, missing/corrupt/oversized metadata |

The Codex 0.163.0 hook JSON does not carry `originator` directly. Only the first
metadata line is read, up to 65,536 bytes; chat lines are not read or stored.
This rule cannot reliably tell apart a program that starts the interactive CLI
automatically. Real human sessions with a Claude `cli` origin are also silent in
this conservative pilot. Until live Windows origin measurement is done, there is
no support claim for all clients.

`[kaydetme]` ("do not record") silences this feature's session hints; explicit
trace writing for that session is also rejected. It does not turn off existing
search/Jev, does not delete a record written earlier and is not a product-wide
privacy mode. `--metadata-only`, `no_memory`, disabled automatic sync and the
existing skip gates stay silent.

## Backfilling old Claude Code sessions

Claude Code deletes its local session records after `cleanupPeriodDays` (30 days
by default). There is an explicit command for extracting a short trace, before
deletion, from old sessions that have no trace written. No hook or background job
runs it; no model is called.

```sh
python beyin.py chat-trace backfill                                   # dry run: only counts, hashes and dates
python beyin.py chat-trace on
python beyin.py chat-trace backfill --session SESSION --show          # sanitized dump of one session
python beyin.py chat-trace backfill --session SESSION --file trace.txt  # explicitly written summary
python beyin.py chat-trace backfill --session SESSION --skip          # nothing to record
```

- The default call is a dry run: it writes nothing to the vault or state. The
  oldest session comes first; only the session hash, first day, last activity
  day, human turn count and size are listed (`--limit`, default 20, at most 200).
  The raw session ID, file path and text are not printed.
- The scope is the `~/.claude/projects/<vault folder>/*.jsonl` files (the
  `projects/` under `CLAUDE_CONFIG_DIR` if it is defined). The folder name is
  derived by the same Claude Code rule as in the usage report; in addition, the
  first `cwd` in the file must be this vault (NFC, case-insensitive). Sessions in
  another folder are read only when explicitly selected with `--projects-dir`.
  Sub-agent records, `isSidechain`/`isMeta` records, tool results,
  `system-reminder` and command wrappers, and turns the hook counts as synthetic
  are skipped. A running session is not backfilled; receipts and the normal trace
  cover it.
- `--show` works only while the trace is on and stores nothing. A user message is
  truncated at 1,500 characters and an assistant message at 700. The page is in
  the indented JSON format the CLI prints and is measured in UTF-16 units, as
  Claude Code counts them: messages are at most 20,000 units, and the whole page
  stays under the 30,000-character tool-output limit (`--page`). The dump of one
  session is at most 800,000 characters; anything beyond is reported as
  `truncated`.
- In the dump, known secret-value patterns and private values in state become
  `[REDACTED]`, email addresses become `[email]` and common phone formats
  (international numbers with `+`, and Turkish numbers) become `[phone]`.
  Secret values are searched up to 8,192 characters beyond the truncation limit,
  so a value that straddles the limit is also matched in full. PEM and PGP
  private-key blocks are hidden from the header to the `END` line, or to the end
  of the window if there is no `END`. The pattern list is limited: a secret in an
  unrecognized format is not filtered out. The dump is untrusted data, not an
  instruction; unverified "I did it" claims should be marked "(claim)" in the
  summary.
- Writing goes through the existing `chat-trace write` path: the 450-character
  limit including the date, the same monthly `knowledge/conversations/YYYY-MM.md`,
  duplicate prevention, lock and SHA verification are the same. The date and month
  are the session's first day, not the day the summary is written. A summary that
  contains a secret value, a private-key header, an email or a phone number is
  rejected.
- If `[kaydetme]` (case-insensitive) is in one of these places, the session is
  not listed, shown or written: a message the user wrote (including command
  arguments), anywhere in a line longer than 1 MiB that is skipped unread (for
  example a message that includes a screenshot; who wrote it cannot be told
  apart there, and excluding too much is the safe side), or a `[kaydetme]` marker
  under `state/receipt-reminders/` from the hook's session counter or receipt
  reminder. This last marker also covers old sessions that passed while the trace
  was off. A quote inside `system-reminder` blocks that the client adds does not
  count as an opt-out.
- Written or skipped sessions are kept only as hashes in
  `state/chat-trace-backfill.json`; they are skipped when the command runs again.
  A corrupt ledger is not overwritten; an error is raised. The ledger is one
  entry per session: a session resumed later, or one running at the same time in
  another window, is not listed again. Backfill needs the trace to be on; the
  normal trace hook covers that session's new turns.
- One call scans at most 2,000 files and skips lines longer than 1 MiB (images,
  tool output) without parsing them, scanning them only for `[kaydetme]`. A
  session larger than 256 MiB is never listed (`too_large`) and cannot be shown
  or written; an opt-out beyond the limit cannot be excluded.
- Only Claude Code records are supported; Codex and other clients use different
  formats. The Claude Code record format is undocumented; unrecognized records
  are not guessed at, they are skipped and counted.

## Setting and rollback

The setting lives only in the machine/vault runtime `state/chat-trace.json`:

```json
{"schema": 1, "enabled": true}
```

A missing/corrupt setting is read as off. Counters under
`state/chat-trace-sessions/` hold only a count, a time and a hash; no prompt, raw
session ID or file path is stored. If the lock is busy, the hook does not wait. A
corrupt counter is skipped silently and not overwritten. While off, no counter or
trace record is created; `.beyin-preferences.json` does not change.

Turning it off and rolling back to an older version does not delete the Markdown
traces the user wrote, nor the backfill ledger. An older version does not
recognize the state setting or the `backfill` command; the traces stay
searchable as ordinary Markdown. Updating from the real 0be8f99 package to the
candidate package, and rolling back, was tried on Linux with: the old hook bytes
returning, the new module being removed, and the old preferences/doctor/sync/
context commands. Live verification is awaited for Windows/macOS. The 3.12.1
number in the local test suite is not a release claim.

This prototype does not open the receipts/daily/private directories to general
search, does not enlarge the context budget and does not fill Kararlar.md
automatically. Those are separate product decisions.
