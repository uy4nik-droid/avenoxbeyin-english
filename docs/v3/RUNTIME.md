# V3 local memory foundation

This module is an opt-in foundation, not a replacement installer or lifecycle migration. Existing hooks and the isolated compiler are unchanged. It makes no model calls and imports no remote provider. It must be given an existing synthetic or explicitly authorized vault and a runtime directory outside that vault.

`template/.claude/scripts/beyin_v3.py` exposes `MemoryStore(state_dir, vault_root)`. SQLite records and receipts persist in `state_dir/memory.sqlite3`; the runtime directory is private to the local account. Each operation owns and closes its connection. Write operations use `BEGIN IMMEDIATE` transactions; this is local process coordination, not distributed cloud synchronization.

The database records the resolved vault root it was created for (`metadata.vault_root`) and refuses any other root with `runtime belongs to another vault`, so two vaults never share one index. Nothing rebinds it implicitly. For a moved vault, `install_v3.py --state <state> --rebind-state` moves the binding after verifying that the recorded folder is gone or is the same folder, or provably uses another state root, and that the vault carries this state's installation pin; it copies the database to `memory-before-rebind.sqlite3` first. See [MULTI-MACHINE.md](MULTI-MACHINE.md#moving-the-vault-to-another-folder-or-account).

## Hook acknowledgement retention

Every processed hook event is first acknowledged as a private `state/hook-done/<sha256>.json` marker. These recent markers prevent duplicate work without needing to read the database when the same event is immediately replayed.

On successful queue drains, `beyin_v3_hook_done.py` migrates markers older than seven days into the local `memory.sqlite3` table `hook_done_ledger` (at most 256 per run). Its row stores only the event hash, harness and lifecycle event name, not prompt or session text. The SQLite transaction commits **before** the JSON is removed: if a worker crashes between those steps, both copies are harmless and `doctor` counts the event once. A failed migration never deletes its marker. When no old markers are found, the scan is limited to once per day.

Newly delivered events are checked against both the live markers and this ledger. `doctor` combines recent JSON and archived lifecycle metadata so migration does not reset previously observed clients or inflate `acknowledged_events`. This is local-only and requires no extra service or dependency.

The ledger intentionally **retains event hashes indefinitely**, because removing old hashes would allow very late event-ID replays. This change bounds the number of individual JSON files during ordinary use; it does not promise bounded SQLite storage or a measured speed-up. A state reset, backup or restore should keep `memory.sqlite3` and `hook-done/` together.

## Event retention and state size

Every real record change stores a full snapshot in the `events` table, so a vault that is edited daily, or reindexed by an upgrade, grew `memory.sqlite3` without bound before #585. Only `history` reads old snapshots; the receipt-view quarantine stores `MAX(sequence)` as a cutoff, and sync, receipts, `doctor` and the usage report never read old rows. `beyin_v3_retention.py` therefore keeps:

- the newest event of every record that still exists, which is exactly what a fresh sync of the same vault writes, so `history` of a current record is never empty;
- at most the 10 newest events of each record, and only for 30 days; a deleted record keeps its trail, ending in its `delete` event, for that window;
- the newest row of the table, so `MAX(sequence)` never moves back. `AUTOINCREMENT` never reuses a sequence number.

The table has no time column and gets none, because a release before this one reads the same database after a rollback. Age comes from sequence marks in `metadata`: at most once a day the current `MAX(sequence)` is saved with the time, and an event at or below a mark saved 30 days ago is at least that old. Events written before the first mark count as new for one full window, so an upgraded vault loses nothing older for 30 days except snapshots beyond a record's newest 10.

The background queue worker prunes at most 500 rows per successful drain on the same SQLite writer lock, after acknowledgement and hook-done compaction, and never in a worker started by a `SessionStart` or `UserPromptSubmit` hook, which may wait for it. Once the backlog is gone it checks at most once a day. It never reads the vault. In the same run it removes leftover temp files older than one day from the state root, `hook-queue/` and `receipt-reminders/`, matching only the temp names this runtime writes there (`hook-health.json.<hex>.tmp`, `.index-xxxxxxxx` and the like). The hook's own atomic writer now removes its temp file when the replace fails. On POSIX, the same run and `state-compact` also delete Jev score entries (`<state>/.cache/jev/<sha256>.json`) whose file modification time and valid JSON `created_at` are older than one day, the longest `cache_ttl` Jev accepts. Directory-descriptor-relative operations prevent a concurrent symlink swap from redirecting deletion. Cleanup and this version's Jev cache publisher share a nonblocking directory lock; a busy or unsupported lock skips cleanup (and skips cache publication for that call, without discarding the returned score). Windows cleanup is disabled until equivalent reparse-point-safe deletion is available. `state-compact --dry-run` and `doctor` count safely sweepable entries as `expired_jev_cache`; zero can also mean unsupported or busy, not an empty cache. Malformed old entries cannot be cache hits and may be removed; files larger than 1 MiB are conservatively retained. Older runtime versions do not participate in the publication lock: do not run an old cache writer concurrently with cleanup.

Deleted rows become free pages that SQLite reuses, so the file stops growing; it does not shrink by itself. A database created by this release uses incremental auto-vacuum and the worker returns at most 1024 free pages per run. A full `VACUUM` rewrites the whole file under an exclusive lock, so it runs only from the explicit command `python3 beyin.py state-compact` (Windows: `py -3 beyin.py state-compact`; `--dry-run` reports what would go without writing). The command prunes everything due now, removes stale temp files, switches an older file to incremental auto-vacuum and runs `VACUUM`; a busy index is reported and left as it was. `doctor` reports `state_storage` (index size, free bytes, event count, auto-vacuum mode, stale temp files) as information only and suggests the command when at least 64 MiB and a quarter of the file are free pages. Neither path touches the vault, the receipts or `hook_done_ledger`.

## Records and source references

`ingest(record)` requires `id`, `text`, and `source`. The source must be an existing relative file resolving inside the vault. Traversal and escaping symlinks are rejected. Records preserve all supplied structured fields, including `facts`, `kind`, `project`, `status`, `visibility`, `updated_at`, and `supersedes`. Facts default to an empty mapping, revision to 1, visibility to internal, and supersedes to an empty list. When `updated_at` is absent or blank it is filled from the first of `updated`, `modified`, `last_modified`, `date_modified` whose value is a string beginning with an ISO date; other values are ignored and file modification time is never used, because synchronized vaults rewrite it. The alias stays in the record and the source file is not rewritten.

Ingesting the exact same record is idempotent. Reusing an existing ID for different content fails. `update_task(id, expected_revision, changes)` performs a locked revision comparison and increments the revision; it does not permit changing the record ID or directly setting its revision. These updates affect the local record store, not source Markdown files. They do not claim external verification or completion.

`submit_receipt(event_id, summary, refs, harness)` requires existing source references. Replaying the same semantic payload, including from the other harness, returns the original receipt. Changing summary or references under an existing event ID fails. First-writer harness attribution is retained. Receipts are stored locally and do not automatically append to daily notes or project views.

The Claude/Codex Stop learning reminder treats knowledge references as citations, not proof that a note was updated. Its filesystem evidence accepts either a distilled Markdown note cited in the receipt's `refs` with modification time at or after the edit window began, or a PostToolUse editor write of such a note (Claude file path, Codex apply_patch header) in the same window, since that write precedes the hook that opens the window. The editor check examines all parsed paths in the hook's bounded input payload, rather than only the first five. File symlinks are rejected, and resolved paths must remain inside the vault and within the existing distillation roots, outside generated-file exclusions; the mtime check also requires the cited path itself to name a distilled note. An unrelated recent note elsewhere in the vault no longer satisfies the receipt's learning claim, and citing an older note alone does not suppress the reminder. Candidates staged for this session in the current edit window can also satisfy the separate candidate-ledger check. Filesystem evidence remains a time heuristic, not content-hash verification, proof of authorship or a semantic check that the declared learning was saved; a sync tool can change modification times without changing content.

## Retrieval and harness parity

`retrieve(query, project=None, audience='internal', statuses=None, limit=5, budget_chars=8000)` returns records, source citations, abstention, truncation, omitted count, and a visible character budget. Retrieval uses normalized Turkish/English lexical tokens, conservative query stopwords and removal of the explicitly selected project token. It has no embeddings, natural-language reasoning, or inferred task completion.

Turkish is agglutinative, so every token is reduced to one canonical stem by a small suffix stripper before scoring, on the query side and the document side alike. It peels an ordered longest-match table of nominal suffixes to a fixpoint, refuses to touch words shorter than five characters, keeps a stem floor of three characters for plurals and four or five for the rest, and gates each suffix on the preceding sound plus a weak vowel-harmony check. That is why `farkı` finds a note about `fark` and `notlar` finds a note about `not`. Consonant softening is handled for p/b and k/ğ: a stem ending in a vowel plus `b` or `g` (soft g is folded to `g`) is written back with `p` or `k`, so `kitabı`, `örneği` and `temizliği` meet `kitap`, `örnek` and `temizlik`. Known limits: it is a heuristic with no lexicon, so it does not model t/d or nk/ng softening (`ümit`/`ümidi`, `renk`/`rengi` stay apart; d would merge past tense stems such as `denedi` into `denetim`), vowel loss or doubling (`kayıt`/`kaydı`, `hak`/`hakkı`), and it cannot strip suffixes off three-letter roots other than plurals (`ev`/`evden`), it over-peels some words into non-words that only have to be consistent (`araba` and `arabanın` both become `arab`), and it merges a small number of English words that happen to end in a Turkish suffix (`quota`/`quote`, `viola`/`violin`); measured over 198k dictionary words, 4.5 percent land in a merged group, while `table`/`tab`, `handle`/`hand`, `golden`/`gol`, `garden`/`gar` and `state`/`sta` stay apart. Verb inflection is out of scope. Stems replace tokens, they are never added alongside them, so a score still counts matched query words and `STRICT_MIN_SHARED` keeps its meaning. Nothing is stored: tokens are computed per query, so an existing vault needs no reindex after upgrading.

Filters apply before scoring. Public sees public; internal sees internal and public; private is explicit. Untrusted records never enter context. Project filtering is exact. Supersession is resolved over every trusted record, not only the eligible ones: a `supersedes` value names a note by its explicit id, by vault path (with or without `.md`) or `[[link]]`, or by its file name when exactly one note has it, never by substring. A value that resolves to nothing, to several notes or to the note itself retires nothing; sync reports it as `supersedes_issues` and doctor as `supersedes`, without degrading either. Untrusted notes cannot retire another note. Without explicit statuses every route drops notes whose status starts with a retired word (`superseded`, `retired`, `archived`, `deprecated`, `obsolete`, `replaced`, `arşiv`, `eski`, `emekli`, `geçersiz`); any other status stays deliverable. Explicit status filters select exactly the requested first words, case and Turkish letters folded; a note without a status counts as active, a task without one does not. Non-strict matches (`retrieve`, `candidates`, the `context` command) are ranked by Okapi BM25 over stem counts (`k1` 1.5, `b` 0.75) with timestamp as a tie-breaker, so a long hub note that mentions every query word once no longer outranks the note that is about them; records with no shared term keep timestamp order. Strict matches keep the calibrated weight and thresholds described below. Unknown queries abstain. Structured facts and citations are preserved; oversized text may be clipped with an explicit marker and text_truncated flag when the metadata fits, otherwise the record is omitted; the budget measures serialized record/citation characters, not tokenizer tokens or the entire response envelope.

The explicit `context` command adds `unmatched_terms`: sorted, deduplicated query words (case/diacritic folded, matched using the engine's stemming, excluding stopwords) absent from the **delivered** records' text, titles, fact values and aliases. This additive lexical diagnostic does not change ranking, admission, budgets or `abstained`. It is not proof that a topic is missing from the vault: clipping, the result limit, scope/privacy filters and synonyms can all leave a term unmatched. Hidden, stale and unselected records are not inspected for this field; with no delivered records, all non-stopword query tokens are unmatched. It is also computed after optional Jev selection; automatic hook context is unchanged.

Supersession is stateless: the current trusted index determines each match, with no persisted target binding. A new same-basename note can therefore make a formerly unique name reference ambiguous and let its old target return to context; one added at the vault root matches a bare value as an exact path, so it is retired in the old target's place without any report. Prefer an explicit id or full vault-relative path to avoid this collision. Explicit `sync` and `doctor` human output shows a bounded warning for ineffective references; JSON fields, command statuses and per-turn hook behavior are unchanged. See [Supersedes references](MARKDOWN.md#supersedes-references) for the repair steps and limits.

The per-turn hook asks for strict context (`context_for(..., strict=True)`), which ranks Markdown passages instead of whole notes (`beyin_v3_passage.py`, #83). Each record's text is split into heading-aware blocks (oversized blocks become overlapping windows of about 900 characters), a block is admitted with the same relative-idf weight family scaled by query coverage, and the best block per source is delivered with its heading path through the same `pack_context` budget and citation contract. Admission uses block frequency, ranking among admitted sources uses source frequency, and the coverage denominator is capped at four terms so a long conversational prompt is not rejected for its length. Frontmatter is never read (records carry the Markdown body), `daily/` and `receipts/` are always excluded, supersession, visibility, trust, project and freshness gates are the same `_eligible()` gates as the note-level path, and explicit project words do not count as matches. The derived index lives in the runtime directory as JSON (`passages.json`, 0600), re-tokenised only for changed records; a cold build runs in one-second steps and meanwhile, like any real error, falls back to the note-level path. An empty passage result is an answer, not a fallback. `retrieval.json` in the runtime directory may set `strict_floor` (default 0.20) and extra `strict_exclude` prefixes; see PREFERENCES.md. The same file can opt the unscoped explicit `context` command (no `--project`) into two-word admission (`unscoped_min_shared: 2`) and dominant-project demotion (`unscoped_dominant_weight`, BM25 part only); both are off by default because they cost recall on the frozen fixtures (#532). `scripts/evaluate_v3_passages.py` measures both paths on a deterministic synthetic corpus or, read-only, on your own vault.

Both clients call `shared_context(store, harness, query, **kwargs)` or `store.context_for(harness, query, **kwargs)`. Codex and Claude use exactly the same retrieval implementation and normalized output. `codex_context` and `claude_context` are convenience wrappers.

`optional_provider()` returns None by default without imports or calls. An enabled provider requires an explicitly supplied factory; integrations must call this intentionally. The local store never depends on the provider's existence or state.

## Validation boundary

The frozen semantic contract and an independent test lane own acceptance. The implementation does not read holdout scenarios or hardcode fixture IDs. Small synthetic lexical gates cannot establish broad language understanding. Real lifecycle delivery, user-facing approval, installer migration, compiler execution and multi-machine reconciliation remain outside this foundation. Existing compiler staging, output allowlists, source hashes and restricted model execution must remain intact if a later migration integrates this store.

## Vault binding and source freshness

Each database is bound to the canonical vault root. Reusing a runtime for a different vault fails rather than mixing contexts. Ingest captures a source SHA256; retrieval excludes missing or changed sources and returns `stale_count` for eligible records. Explicit revision updates refresh the source snapshot; this is not automatic external verification. This foundation's indexed records are authoritative for its state API, not a replacement for canonical Markdown task synchronization. A project-only query lists eligible records in that scope; an unscoped query without meaningful terms abstains.

## Transactional history

Record ingestion and revision updates append an immutable snapshot event inside the same SQLite transaction as the record projection. `history(record_id, audience="internal")` returns committed `{sequence,event_type,record_id,revision,record}` entries in global monotonic sequence order; event types are `ingest` and `update`, and Markdown synchronization adds `delete` when a source is removed or no longer validates. Duplicate ingestion, rejected revisions and validation failures create no events. History is empty when the current record is outside the audience or untrusted, or its source hash is stale; a deleted record is judged by the snapshot in its final `delete` event. Individual events outside the audience are omitted. Snapshots past the retention described in "Event retention and state size" are gone; the newest snapshot of a current record always stays. The CLI `history` command synchronizes first. Returned JSON objects are fresh copies. Receipts retain their separate idempotency table.

Initialization adds the events table to existing foundation databases. Prior mutations remain explicitly unrecorded prehistory; the module does not invent baseline events for old rows. This is a local audit history, not a distributed log or a complete event-replay migration tool.

Supply a dedicated application runtime directory. Initialization sets that exact directory to account-private permissions; never pass a general home, cache, or shared parent directory. Its parent permissions are not modified.

## Managed paths and unmanaged user layer

V3 writes exclusively to its explicit managed vault files:
- Entry point and metadata: `beyin.py`, `.beyin-runtime.json`, `.beyin-version`.
- Scripts: `.claude/scripts/beyin_v3*.py`.
- Managed starter skills: `.agents/skills/{beyin,beyin-doktor,beyin-guncelle,beyin-kontrol}/`, `.claude/skills/...`, and `.kiro/skills/...`. A same-named skill the user already has is left as it is; a rollback removes the folders of a skill the update added.
- Platform launchers: `Beyni Guncelle.cmd`, `Beyni Güncelle.sh`, `Beyni Guncelle.command`, `Beyni Güncelle.desktop`.
- Adapter shims: `.claude/hermes-plugin/`, `.claude/scripts/beyin_v3_kiro.py`, `.opencode/plugins/`, `.omp/hooks/`, `.pi/extensions/beyin-v3.ts`.
- Harness hook declarations: `.claude/settings.local.json`, `.codex/hooks.json`, `.codex/config.toml`, `.agents/hooks.json`, `.kiro/hooks/beyin-v3.json`.
- Companion instruction blocks: `AGENTS.md`, `CLAUDE.md`.

All other paths belong to the user. In particular, `.brain/` and `custom/` directories are reserved as an untouched, unmanaged user layer. Installer, updater, and `doctor` checks never treat files under `.brain/` or `custom/` as conflicts or unmanaged system intrusions.

## Managing project folder scopes

Folders in `.beyin-projects.json` that cannot be found produce a warning and a doctor
diagnosis; queries for the other projects continue. The missing-folder mapping is kept as a
scope boundary so that stale `--no-sync` index rows are not opened to other projects as
shared notes.

A single bad entry, such as a path that leaves the vault, an absolute path or one containing
`.`, an empty project name, or a folder assigned to two projects, no longer stops every open
project call. The entry is skipped with a stderr warning, the vault folder it might point to
is not opened to any project, and `shared_unscoped` is treated as off until the entry is
fixed. File-level errors such as broken JSON or an unknown key still stop open project calls.
Reading does not change the file.

`project-scope list` only reads. `project-scope add --folder "Projeler/Deneme" --project deneme`,
`project-scope remove --folder "Projeler/Deneme"` and `project-scope prune` explicitly edit the
scope file. `prune` now removes folder entries that can no longer be found and invalid paths.
A broken or symlinked configuration is not overwritten; repair the file first.

`--shared-unscoped on|off` can be used only with `add`. A call with no action is treated as
`list`; if the flag is given with no action, `list`, `remove` or `prune`, the command returns
an explicit error and exit code 1 without changing any scope or runtime file. To change the
setting while keeping the existing mapping, run `add` again with the same folder and project
name:

```sh
python3 beyin.py project-scope add --folder "Projeler/Deneme" --project deneme --shared-unscoped on
```

On Windows, use `py -3` instead of `python3`. Pass `off` to turn it off; if you leave out the
flag, the existing value is kept, and a new file defaults to `false`. The `add` output also
shows the saved `shared_unscoped` value. `on` includes eligible notes that are not assigned to
any project in all open project queries, including the external project bridge; it does not
open notes that belong to another project or are `private`. To see only the current value, use
`project-scope list` without the flag.

## Workspaces, link checking and MOC

`workspace`, `lint` and `moc` run only when called explicitly; SessionStart, `sync` and
`doctor` do not run them. `workspace list`, `workspace inspect`, `workspace plan`,
`workspace provision --dry-run` and `lint` are read-only and do not create state.

- Workspace metadata (name, kind, lifecycle, rules file, note roots, provision status) lives
  in the `.beyin-workspaces.json` file at the vault root. Folder bindings stay in the
  `folders` map in `.beyin-projects.json`, and the format of that file does not change. An
  older version reads the scope file as before and ignores the registry file; after
  `rollback`, project scopes keep working. A workspace's sources are derived from the
  `folders` map on every read: a change made with `project-scope add/remove` is visible
  immediately. Projects with no registry entry are listed with `registered: false`. A registry
  file written with a newer schema version, or a corrupt one, is not modified.
- `workspace disconnect` removes only a binding that still points to that workspace; it does
  not touch the folder or notes on disk. `archive` does not change scope; it only hides the
  workspace from the list.
- `workspace provision <id>` writes a `provision.status: pending` record before the first
  file, then creates the folders and templates (an existing file is kept), binds the folders
  and verifies them. The project folder lives under the vault's own project folder
  (`🏰 300-Projects/<id>` in the template, otherwise `projects/<id>`). Even when `--source` is
  given, this folder, which holds the rule and MOC templates, and the note root are also bound
  to the workspace (`bindings` in the `plan` output); verification also checks that the
  template files fall into this workspace within the retrieval scope.
  If an error occurs, only this attempt's own changes are rolled back: the files it created
  and that are unchanged, folders left empty, bindings that still point to this workspace, and
  its own record. Other changes made in the meantime are kept. If something cannot be rolled
  back, the `reconciliation` object in the error output says what remains, and the record
  stays as `provision.status: failed`; the same `workspace provision <id>` command completes
  the record from where it stopped.
- `lint [--folder <folder>]` reports broken wikilinks, missing headings or attachments, and
  orphan notes with no incoming links. Partial paths (`[[folder/note]]`) and attachments are
  resolved like Obsidian does, by name and path ending; code blocks and inline code are not
  counted. Notes in sensitive folders, archive folders (such as `📦 900-Archive` or
  `Arşiv`), `visibility: private` notes and installation folders are not scanned; a link to
  such a note also appears as broken. Exception: a link given by full vault path to a plain
  `.md` receipt file at the top level of the root `receipts/` folder resolves; the receipt
  body is not read and a `#heading` section is not verified. Receipt files do not enter the
  scan or the MOC list; a bare name or a nonexistent receipt still counts as broken. Counts
  are always returned in full; lists carry at most 100 entries, and the rest is counted in the
  `truncated` field (use a narrower `--folder` for all of them). `folder_counts` counts the
  findings before truncation by the direct parent folder of the source file (`.` is the vault
  root); the broken-link count is the number of links, not of target files. The first 100
  folders with the most findings are listed, with ties broken by path order; the counts of the
  remaining folders and findings are kept in the `folder_counts_remaining` field. When
  `--folder` is used, this breakdown also covers only the selected scan area. This summary
  does not change the exclusion policy: it adds no new exemption for files that are left out
  of the index or generated.
- `moc [--folder knowledge] [--file MOC.md]` writes only to a plain `.md` file in the target
  folder. Names of instruction, companion or rules files such as `CLAUDE.md`, `AGENTS.md` and
  `Kurallar.md` are not accepted. If the file does not exist, it creates it. If it exists, it
  regenerates only the part between a single `<!-- beyin-moc:start -->` and
  `<!-- beyin-moc:end -->` pair, and only when the file carries exactly that pair; it does not
  touch a file without markers. Add the marker pair by hand where the index should appear. A
  MOC lists only notes that its own readers can also see: the note's project scope (the
  `project` field or the `.beyin-projects.json` folder) must equal the scope of the MOC file,
  its visibility must not be narrower than the MOC's (a `visibility: public` MOC lists only
  public notes), and it must not be `trust: untrusted` or a rejected inference. In a nested
  scope, run a separate `moc --folder <folder>` for each project folder; skipped notes appear
  in the `skipped` counts in the output. `moc` must be run again when the scope file changes.
  If nothing changed, the file is not written.
  Because Obsidian does not use the Beyin lock, the file is compared again (content digest,
  mtime, size, inode) after the new text is ready and just before the rename; if it changed,
  nothing is written and the command asks to be run again. On macOS and Linux the old file is
  held open during the rename, and an in-place edit saved in the meantime is noticed and put
  back; for an editor that first empties the file and then writes, the command waits (up to
  0.2 s) until the file stops changing before putting it back. The remaining limit: if an
  editor replaces the file with a new file in exactly that microsecond-scale gap, the operating
  system cannot lock against it.

## Receipt view conflict and recovery

`daily/v3/YYYY-MM-DD.md` and `knowledge/v3/outcomes.md` are generated from the immutable
receipt sources. If a view has been edited by hand or there is no local tracking history, the
existing bytes are preserved and a `kind: receipt_view` warning stays visible
(`sync.status: degraded`). Healthy source context, lifecycle records and writing new receipts
continue; real source conflicts continue to block context and history. The `receipt`,
`task-update`, `context` and `recap` JSON outputs report the relevant diagnosis under
`source_sync.warnings`. `history` keeps its JSON list format and writes the warning to stderr.

A CRLF/CR/LF difference alone does not count as a manual edit. New receipt summaries use LF;
old source files and index summaries are not rewritten. A receipt source with CRLF line endings
is indexed with the trailing CR, as 3.12.0 read it, so after `rollback` the older version's
byte comparison sees the same line. Generated views use LF for old summaries too. A previous
view whose ownership is proven moves to LF on the first sync; the tracked hash belongs to the
raw bytes written, and later LF records are not rewritten. A view can be updated if it is
identical to the current deterministic output apart from line endings. If an old view with
mixed line endings is stale, the receipt links it contains select only the subset to be
regenerated: the hash of the regenerated **raw bytes** must equal the recorded old hash, and
the current text must differ only in line endings. A link or heading alone does not give
permission to write. The view written by versions 3.10-3.12 is regenerated in those versions'
format (hash-named link, unhidden summary) only for comparison; if the evidence matches, it is
replaced with the current format. If this evidence cannot be established because of a time
zone, another generator format or missing history, the view is preserved; use the explicit
recovery command below. The same check applies when removing a tracked view that belongs to
the old daily layout.

The view that tracked or existing receipts would generate is not indexed as a source note,
even if its heading is deleted. Fixed links to the same file are also excluded. View records
that were wrongly indexed earlier, and the history events belonging to them, are hidden from
automatic context; the bytes of audit events are not changed. A real note that later appears
in the view's place can be indexed again. Even if the local state is lost entirely, the
provenance information saved next to the recovery archive and the archive digest are used to
recognise the same fixed link that still exists. If this side record is deleted or corrupted,
or a link changes both place and content, the old provenance cannot be proven again; inspect
those files by hand.

Explicit recovery command: `python3 beyin.py sync --recover-views` (Windows: `py -3 beyin.py sync --recover-views`).
The conflicting bytes are durably written as a separate file for each attempt inside
`.archive/` next to the view, and then the view is regenerated. If recovery fails, the source
and the tracking record are kept; symlink archive targets are not accepted. The command does
not delete receipt sources or the runtime database. Move any user additions in the archive to
suitable knowledge notes. If there is a fixed link, a small `.provenance.json` record is also
stored next to the archive; keep this record together with the archive.
On POSIX, before the original view is changed, the archive file, the archive directory and the
parent directory pass `fsync` barriers; a barrier error stops the recovery. This order is not
an absolute durability guarantee against power loss or a remote file system. On Windows,
directory `fsync` is not supported, so the same durability claim is not made.

### Errors when resolving learning candidates

In an explicit `learn --resolve distilled|discarded` request, if checking for the candidate
ledger or reading, locking or writing the existing ledger fails with an I/O error, the command
exits with 1. The JSON error carries the fixed message `learning candidate resolution failed`
instead of a private file path or ledger content. Successful resolution, a request that
completes without error but matches nothing, and a missing ledger keep their existing results
and exit code 0 behavior. The existing rewrite step runs even when no match is found; an I/O
error in this step also exits with 1. The receipt's automatic candidate tracking remains
optional; a resolution failure does not roll back or fail the persisted receipt. The ledger
format and the write/retry behavior do not change.

An explicit `learn --list` request likewise exits with 1 and the fixed message
`learning candidate listing failed`, with no private path or content, when checking or reading
the existing candidate ledger fails with an I/O error. A ledger that does not exist or is not a
regular file stays an empty list. Successful filtering, skipping of malformed lines, and the
existing best-effort behavior of the hook candidate checks do not change.

## Memory audit read errors

An explicit `beyin.py audit` fails with exit 1 and `audit source scan failed` when a
candidate note cannot be read or directory enumeration reports an I/O error. It
does not return partial findings as a complete audit or call the memory balanced.
The error includes no raw filesystem message or source contents. Check local file
and directory access, then rerun the audit. User notes are not modified.

Healthy report fields, excluded directories, private/untrusted/generated/retired
note filtering, and the existing skip behavior for invalid frontmatter are
unchanged. The lower-level `scan_audit_candidates` helper keeps its best-effort
default; the explicit audit uses its keyword-only `strict=True` option.
