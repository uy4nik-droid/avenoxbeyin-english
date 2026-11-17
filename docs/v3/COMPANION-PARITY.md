# V2 → V3 personality and continuity review

Review date: 2026-09-17. Baselines compared: V2 `2e074cc`, published
V3.0.2 `55cd4e8`. The "personality/performance declined" feedback relayed by the user
is a user observation. The causes below are verified from the code; neither a subjective
personality score nor a quality gain for all models has been measured.

## Where did the loss occur?

| Behavior | V2 | V3.0.2 | This fix |
| --- | --- | --- | --- |
| Identity setup | Personalized CLAUDE and Companion templates | The ZIP installer installed only the technical AGENTS/CLAUDE block; Core and relationship files were not created | A shared thinking-partner protocol and starter notes owned by the user, created once |
| Session opening | Core reading instruction and a deterministic relationship bridge; upper limit 16,000 characters | 5,000 characters total; Core/Soul not in the priority set; duplicated JSON metadata consumed the budget | Core/Soul, corrections, the latest outcome, active topic bodies, the latest Journal and the knowledge map are carried as short source sections |
| "Do you know me, where did we leave off?" | The relationship sources were present at opening | An empty search result if the words in the query do not overlap with a note | Deterministic companion context for relationship questions; the general search contract is preserved |
| Journal and Threads selection | The latest Journal entry; but Threads was only title/status and 12 lines | Journal clipped from the end of the file; a new entry could be lost if it was at the top; closed topics consumed the budget | The newest-dated Journal, the active Threads body; the clipping is explicit and shown with the file path |
| Learning from the relationship | Core/Journal/Threads/Last-Session/Kurallar were explicitly the agent's responsibility | The beyin skill mostly described task/receipt operations | A concrete writing protocol for explicit user corrections, rationale, open next steps and meaningful observations |
| Knowledge distillation | The model compiler produced concepts, links and the knowledge index | The compiler was retired; a receipt index was produced, and the synthesis instruction was too short | A concept/link/index update flow for the active agent; no separate model call |

Sources: `scripts/install_v3.py`, `template/CLAUDE.md`,
`template/.claude/hooks/session-start.sh`, `template/.claude/scripts/compile.py`,
`template/.claude/scripts/beyin_v3_hook.py`, `template/.agents/skills/beyin/SKILL.md`.

[Issue #27](https://github.com/avenoxai/avenoxbeyin/issues/27) directly reported that the
relationship sources were not selected with an empty SessionStart query. The earlier #29 fix
prioritized four files but did not complete Core/Soul and the missing setup/learning protocol.
[Issue #21](https://github.com/avenoxai/avenoxbeyin/issues/21) shows that V2 lost the Threads
body: V2's faulty line filter was not restored. Windows hook failures may also have
contributed to the perceived forgetfulness; those were fixed separately in V3.0.2. The new
[#32](https://github.com/avenoxai/avenoxbeyin/issues/32) report describes a V3.0.1
installation; it was not assumed to reproduce in V3.0.2.

## Installation and data protection

`beyin_v3_companion.py` is included in the package. A clean installer creates the missing
starter notes once. In a managed update from V2 or V3, the new worker does the same check on
its first run. The existing Companion/Echo directory is used first, or if there is none, the
single local Core/Soul directory; if there is more than one identity candidate, no choice is
invented. Archive and symlink directories are not discovered as an identity. If the user has a
Soul file, no rival Core is created.

The starter notes are not added to the package manifest's managed files. Personal changes
remain after an update and after rollback/uninstall. Notes the user deleted after they were
initialized once are not recreated. The initialization marker lives only in the external local
runtime state. Learning and relationship writes are done by the active agent; the worker does
not invent user history.

The Normal 5,000 and Economy 2,000 character limits and saved preferences are preserved. It is
not claimed that the whole file will fit in less context: a read marker is added to a clipped
source. Private/untrusted records and records that changed after indexing are excluded from
automatic context. `no_memory` events inject no context and are not written to the queue.

Budget sharing ([#45](https://github.com/avenoxai/avenoxbeyin/issues/45)): `Kurallar.md`
and `Last-Session.md` get a base share before the equal split; when the rules file does not
fit, not only the end but the beginning and end come together, and the marker in between says
how many characters were skipped and that the file needs to be read. The cut is at a line
boundary; no half rule comes through. After the knowledge map and related sources take their
share, the leftover budget is given back to the clipped companion sections; the limit is never
exceeded.

If room is tight at opening, the full general/project rules (the rationales may need to be
dropped), the topmost dated handoff card and a short view of all open topics are set aside
first. The rules' base share belongs to the category; the general and project files split the
same share. Identity, style, Journal, knowledge map, receipt and query results use the
remaining space. If this core does not fit either, identity, Journal and the other optional
sources first drop to a short head; the handoff file keeps its topmost card and at least its
base share, and the short view of topics gets the rest. If this remainder is less than what the
old proportional split gave the topics, each source first gets that proportional share
(limited to its protected part or its base share); the leftover space goes in order to the
remaining rules, the topmost handoff card and the short view of topics. So however long the
rules grow, the handoff card and the topic steps do not fall below what the old split showed.
If the rules themselves do not fit, the bounded shares and explicit clipping markers apply; it
is not said that rules of arbitrary length will fit fully into every finite budget. The source
files are not modified in this process.
This core is a floor, not a ceiling: the remaining space is first shared among all sources. So
the older handoff cards of parallel sessions and all the topic cards come through as long as
they fit; the topmost card always comes whole and first, and a cut handoff detail ends with the
`[truncated: read source]` marker. Topic cards come either whole or in their short view; the
space the whole card cannot use returns to the other sources.

When finding the boundaries of topic and handoff cards, a code fence closes only with the same
marker, at least the length of the opening, followed only by whitespace. A line with sample
text after the marker does not close the fence; headings inside it are not counted as a new
topic or an old handoff card.

Each of the `###` headings in `Threads.md` is preserved in the short view. If the
`**Status:**` / `**Durum:**` and `**Next step:**` / `**Next:**` / `**Sonraki adım:**` / `**Sıradaki adım:**` paragraphs exist, they
are taken verbatim together with their continuation lines; the same fields
without bold (`Status:`, `Durum:`, `Next:`, `Sonraki adım:` ...) are also recognized. The first status and next-step field is the current card;
later dated history paragraphs do not enlarge this short view. A detail paragraph is separated
by a blank line. In the old free-text format, the first sentence and the sentences that
indicate pending work/reminders are selected verbatim.
If space narrows, one pending-step sentence is chosen from this old format; in budgets so small
that even the headings cannot fit, it is not guaranteed that all headings will be visible.
This selection is not a semantic summary; it is not guaranteed to find an unlabeled or
differently worded next step. The short view points to the source for detail and unlabeled
steps. Closed topics and example headings in code fences are not part of this view.
Example status/next-step fields and pending-work sentences inside code fences are also not
taken into the short view; when the space suffices and the full topic card is shown, the code
examples are preserved verbatim.
When the short view does not fit either, all headings are preserved; the space is given to the
topics in file order in slices of at least 80 characters, the later ones come with only their
headings, and the section ends with the `[Thread overview clipped; read source]` marker. With
hundreds of topics, meaningless fragments of one or two characters per heading are not
produced. If the headings would take almost all of the space and leave status for fewer topics,
the topics come in file order with their full short views, followed by the headings that fit
and the same marker; so as the space grows, the number of visible next steps does not decrease.

An `@path` reference in `CLAUDE.md` does not prove that file was successfully loaded in the
current client session ([#610](https://github.com/avenoxai/avenoxbeyin/issues/610)).
For example, Claude Code's [`claudeMdExcludes`](https://code.claude.com/docs/en/settings-reference#claudemdexcludes)
setting can exclude the instruction file that contains the reference. For this reason, on
startup, resume, post-compaction and continuity questions, the companion sources are shown
under the normal source verification, privacy and budget rules; their bodies are not dropped
just because a reference was found. If the client also loads the same file separately,
duplication can occur; losing the rules by trusting an unverified load is avoided. The opening
does not produce a `Loaded in full` claim; `companion_rules_opening` in `doctor` likewise does
not return an `imported: true` or unclipped result by looking at the file reference; it reports
the real companion share. This fix adds no new setting or opt-out and does not mean that a real
Claude Code load was verified.

On Claude/Codex opening, regeneration is repeated with a shrinking budget until it fits the
client's UTF-16/UTF-8 measure. The hook's own notices are also deducted from the character
budget; the final safety cut is not trusted not to lose the companion sources.

Before this sharing, companion files are read from the source-verified snapshot with an upper
limit of 200,000 characters ([#374](https://github.com/avenoxai/avenoxbeyin/issues/374)).
A file that stays shorter than its share leaves the remainder to the longer files; so the rule
clipping and the numbers in the `rules X-Y (n of N)` marker are computed over the file's full
text. Previously the share was split equally, and a `Kurallar.md` exceeding about 40,000
characters lost its beginning in this layer: the summary at the beginning of the file never
reached the opening, and the marker counted the rules from the truncated text. A `Kurallar.md`
that exceeds the upper limit is now kept with its beginning and end in this layer too;
`Journal.md` continues to be kept by its end, since the newest entries are at the bottom.

Scoped rules (#333, [#375](https://github.com/avenoxai/avenoxbeyin/issues/375)): a correction
that belongs to a single project or area is written to `projects/<project>/Kurallar.md`; at
most a one-line pointer tagged `[kapsam: <project>]` remains in the global `Kurallar.md`. The
tag takes the form `[kapsam: ...]` or `[scope: ...]` (`kapsam: name` without square brackets is
also recognized), accepts several names separated by commas; `genel`, `global`, `all` and
`herkes` are the same as an untagged rule. The tag can sit on any line of a list item that
opens at the start of a line with `-`, `*`, `+`, `1.` or `1)`; the item continues until a blank
line or a heading. Name comparison ignores differences in case and Turkish characters. The hook
filters out other projects' tagged items only when an active `project` name arrives in the hook
input; then it also adds the first `Kurallar.md` found (or `rules.md` if there is none) from a
folder carrying exactly this name under `projects/`, `Projeler/` and `projeler/` at the vault
root. Symbolic links and paths leaving the vault are not read; the file must be an indexed
source that is not `private`. Claude Code does not send a `project` field in the hook input:
there the tagged rules also enter the opening and the project file does not come automatically.
This is why the pointer line tells the agent when to open the file. Finding the active project
through `cwd` is a separate matter ([#288](https://github.com/avenoxai/avenoxbeyin/issues/288)).

## Knowledge map and optional `INDEKS.md` (#595)

The knowledge map at opening is by default the `knowledge/index.md` file: the article list the
compiler maintains. As the knowledge base grows, this list is cut within the map's share (at
most 1,500 characters when the companion sources fit, at most 600 when clipped) and the lines
at the bottom become invisible. [#595](https://github.com/avenoxai/avenoxbeyin/issues/595)
proposed instead a short routing card the author maintains by hand: each line says what the
note is and when to open it; the contents do not enter the opening.

This is optional. If `INDEKS.md` exists in the `knowledge/` folder itself (the Turkish
spellings `İNDEKS.md`, `İndeks.md`, `Indeks.md` and `indeks.md` are also recognized), this card
replaces the article list as the opening map; the label becomes `[Knowledge map: knowledge/INDEKS.md]`.
The share and clipping rules are the same: a long card is also cut and the cut is marked. If
there is no card, nothing changes. Recommended format:

```markdown
# Knowledge base: when to open

42 articles; their contents do not enter the opening, open the relevant article only when the topic comes up.

| Topic | When to open |
| --- | --- |
| [[concepts/musteri-notlari\|Customer notes]] | When a contract clause or a delivery date is discussed |
| [[concepts/arac-listesi\|Tool list]] | When choosing a new tool |
```

The card is read at every opening, so it must be kept short: each line a single note and a
single "when to open" sentence. The compiler (`compile.py`) does not write or delete the card;
the lines are written or maintained by the agent.

The card passes through the same gates as the other companion sources: it must be an indexed
source that has not changed since the last sync and is neither `private` nor `untrusted`. If
one of these conditions does not hold, the opening shows `knowledge/index.md` with the old
behavior; the card's text never leaks into the opening. In an opening that carries no
question, the card takes the place of the article list: the related sources section below adds
back neither the list nor the card. In an opening that carries a question, the list can come as
a related source if it matches the question. A map shown in full, with or without a card, is
not repeated in related sources.

Only the card at the root of `knowledge/` enters the opening. `INDEKS.md` files in other
folders are ordinary notes: if the question matches them they come as related sources; they are
not added to the opening on their own. `Threads.md` itself carries the opening view of the open
topics; in this version there is no card, no draft-generating script and no `doctor` check for
topic files in a separate folder.

## Size limit and archiving (#96)

[Issue #96](https://github.com/avenoxai/avenoxbeyin/issues/96) reported that in a
five-week-old vault `Last-Session.md` had grown to about 94,000 and `Threads.md` to about
57,000 characters. The context budget was clipping these files, but the clipping marker sent
the agent to read the whole file, and the growth was visible in no output. The root cause was
in the instruction: it said "update", with no format or limit given. In clients that count
every message as a separate task, the update was appended as a new dated paragraph every turn.

The fix has four parts:

- **Instruction.** One handoff card is opened per session in `Last-Session.md`
  (`## YYYY-MM-DD HH:MM · <label> · <session_id[:8]>`), and the session updates only its own
  card in place; other sessions' cards are not overwritten. In `Threads.md` the topic is
  updated in place. The continuity check is done not on every reply but when a meaningful
  piece of work is finished. The agent does not touch the `## Previous`/`## Önceki` section;
  old cards are moved only by the command below.
- **Measurable limit.** The default limit is 3,000 characters for `Last-Session.md` and 8,000
  for `Threads.md`. Counting is by Unicode character; it is not a byte or UTF-16 unit, so a
  file heavy with Turkish or emoji does not look larger than it is. `preferences
  --last-session-chars N --threads-chars N` changes the limit between 1,000 and 200,000, and
  `0` turns it off. The setting is written not to the `.beyin-preferences.json` file in the
  vault but to `companion-limits.json` in the runtime folder. Because older versions reject
  an unknown preference field, this choice does not break the hooks after a rollback; in
  return, the setting is machine-specific. A corrupt limit file is not silently overwritten;
  the defaults are used.
- **Visibility.** If the limit is exceeded, the first line of the companion context is a single
  `Memory hygiene:` warning. The warning writes the file name, the real size and the limit, and
  tells the agent not to read the file from start to finish and to run `companion-compact`. The
  warning is inside the context budget. If `Last-Session.md` exceeds the limit while the
  parallel-session notice is on, the warning says not to archive other sessions' fresh cards
  just to remove the warning. It shows a `--last-session-chars` suggestion, rounded to 1,000
  characters, that would fit the existing file (at most 200,000); this is not an automatic
  setting change, a session-count calculation or a guarantee against future growth. For a
  larger file, a coordinated review is suggested. `doctor` reports the size of all companion
  files under `companion_hygiene`; in `--human` output, each file that exceeds the limit shows
  as a line. This is not a synchronization failure and does not change the `doctor` status.
  `Kurallar.md`, `Core.md`/`Soul.md` and `Journal.md` accumulate on purpose; their sizes are
  shown for information only and no limit is applied to them. The hook reads `Kurallar.md`
  directly and, when it does not fit, gives its beginning and end together with the skipped
  rule range (#45, #196). `doctor` also gives, under `companion_rules_opening`, the current
  character share (`share`) of the Claude Code opening's rule text by the hook's own
  calculation; the number is not a fixed ceiling, and a shorter rules file can make room for
  optional detail. The share varies with the current size of the other companion files and
  with the receipt. If the rules are being clipped, a single line shows in `--human` output.
  It is informational, does not change the `doctor` status and writes no file (#374). Also, if
  `Kurallar.md` is clipped at opening, a `Memory hygiene: Kurallar.md opens clipped (fit ceiling X of Y chars)...`
  warning appears at the top of the session-start context (#461).
- **Lossless archiving.** `python3 beyin.py companion-compact` is an explicit command; no hook,
  worker or scheduler runs it on its own. Only in a file exceeding the limit does it first move
  the body of the `## Previous`/`## Önceki` (Last-Session) or `## Closed`/`## Kapanan`/`## Kapalı`
  (Threads) section, then the oldest dated entries until the file comes down to the limit. A
  dated entry is a heading, paragraph or list item that has an ISO date (`2026-10-12`) or a
  written date (`12 Ekim 2026`, `12 October 2026`; for a range, the last day: `4→5 Ekim 2026`)
  in its first characters, and it lasts until the next entry or an undated heading. A dated
  heading opens a card: the dated lines and subheadings inside it up to the next heading of the
  same or a higher level belong to that card; the card either stays or is moved as a whole,
  without being split (#118). The newest entry of the handoff card
  and of each topic heading stays in place. In Threads, dated lines directly under the
  `## Active`/`## Open`/`## Aktif`/`## Açık`/`## Acik` section are not moved, because they may be a topic
  themselves. The moved lines are appended verbatim and in order to the
  `Arşiv/<File>-YYYY-MM.md` file in the companion folder. The archive is marked
  `visibility: private`; it does not enter automatic context and ordinary search, and is
  opened directly when needed. A single line pointing to the archive path remains in the live
  file. Frontmatter, code blocks, CRLF line endings and the undated structure are preserved.
  If there is no dated entry to move, or the file still exceeds the limit after moving, the
  command backs up the remaining full text of the file to the same monthly archive
  (`backup: written`). The same text is searched for by SHA-256 digest in this month's archive
  and the previous 12 months' archives (at most 8 MiB read in total); if found, it is not
  rewritten, and the report gives `backup: exists` and the real archive path. The first backup
  of the month is always the full text. If the file changed only slightly within the same month
  (#596), the new backup is written as a delta backup against the latest full backup in that
  monthly file (`backup_format: delta`); if the delta is at most half the text. The delta does
  not depend on another month or another delta; each monthly file is restored on its own. Each
  record is verified by length and SHA-256; `scripts/restore_v3_compact_backup.py` in the repo
  lists verified versions and writes the selected one to a new file outside the vault. An
  archive that is missing, changed, unreadable, symlinked or outside these limits does not count
  as proof of a backup; the command safely writes a new backup. It does not delete old copies.
  A move re-run after an interruption recognizes the earlier record by the same bounded scan and
  does not append the text a second time; a record outside the window causes only an extra
  copy, not a loss of text. If the live file changes during the scan, the old backup is not
  accepted and `conflict` is returned. The command returns `needs_rewrite`; only after that does
  the agent rewrite the file within the limit, so summarizing is never the only copy of any text
  (#168). If the live file changes after the archive is written, the archive reverts to its old
  bytes and `conflict` is reported. `--dry-run` shows the plan without writing anything. The
  command makes no model call and, when finished, runs `sync` to index the new sizes.
- **Decision ledger.** Decision lines in the moved text (`**Karar:**`, `**Karar (Ad):**`,
  `**Karar 2 (Ad):**`, `**Decision:**`; may be a list item; those inside code blocks do not
  count) are additionally appended verbatim to the `Kararlar.md` file in the companion folder,
  with the title of the card they came from and the archive path. The same line is not added a
  second time; the file grows only by appending. `Kararlar.md` is a `visibility: internal`
  note and, unlike the archive, enters search and context; so a decision whose card went to the
  archive stays visible. A decision remaining in the live card is not copied. The report gives
  the count `decisions_added` (`decisions_planned` in `--dry-run`).

`tests/v3_companion_hygiene_test.py` builds the two shapes from #96 with synthetic data (dated
paragraphs added at the top and an unpruned `## Previous Sessions`; dozens of dated updates per
topic and a closed section). It tests that the warning comes as a single line at every budget,
does not come for a file at the limit, a single extra entry is caught in the next session,
counting is by character, the `doctor` report, validation of the setting, and that archiving is
lossless line by line, ordered, repeatable and safe against concurrent edits.

## Verification

`tests/v3_companion_test.py` tests, with synthetic data, a clean ZIP installation, the same
context in three clients, the Normal/Economy/lower-limit budgets, a relationship question, the
wrong identity/archive distinction, private/untrusted/changed sources, a large Journal and a
Journal with the new entry on top, the knowledge map, update/rollback protection and the
one-time initialization behavior.

The first eight regression scenarios were run on `v3.0.2`, published with the same file:
7 failed, 1 passed. After the fix all eight passed. The last extended companion suite passed
13/13. The old version's failures made visible in particular the missing Core/identity, the
context lost at 2,000 characters, the empty relationship query and the no-memory violation.

The local full suite passed 199/199, and the V3 suite within it 152/152. The frozen semantic
contract was kept at development 10/10 and holdout 6/6. The migration to the local `3.0.3`
candidate ZIP with the old updater installed from the real V3.0.2 code, the initialization of
missing notes in the first worker, the identity read-back from the hook and the preservation of
personal notes during rollback to 3.0.2 passed. This candidate package is a test version; it is
not a claim of a published release.

```sh
python3 -m unittest discover -s tests -p 'v3_companion_test.py'
python3 -m unittest discover -s tests -p 'v3_*test.py'
python3 scripts/evaluate_v3.py
# To run the same regressions on an extracted old checkout:
BEYIN_TEST_REPO=/path/to/v3.0.2 python3 tests/v3_companion_test.py
```

These are tests of the source transfer, installation and protection contracts. No blind user
comparison of personality quality was done on new live model conversations. The application of
the learning protocol depends on the active agent following instructions; existing memory data
is not automatically rewritten retroactively.

The decision ledger does not widen the privacy and trust boundary of the source card: no
decision is copied from private, untrusted or rejected sources. The new `Kararlar.md` is open
to local search (`visibility: internal`) and closed to the remote advisor
(`remote_allowed: false`). An existing ledger must also carry `remote_allowed: false` or
`visibility: private`; for a corrupt or unsuitable ledger, the cards are not moved and an
attention warning is returned. If the same line appears in different cards, each card's
decision is kept separately; retrying the same card adds no new copy.

For a Kurallar.md that does not pass source verification, doctor reports the opening
measurement as `stale`; check again after `beyin.py sync`. This diagnosis is read-only, does
not show the excluded rule text and does not move the rules to the archive.
