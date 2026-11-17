---
name: beyin-doktor
description: Checks whether the Beyin vault actually works - source freshness, hook/worker status, skill conflicts, update problems. Triggers - "brain doctor", "is my brain working", "memory is broken", "vault health check", "hook isn't working", "beyin doktor", "beyin çalışıyor mu", "hafıza bozuk", "kasa sağlık kontrolü", "hook çalışmıyor", "/beyin-doktor". Do not use for - version upgrades (beyin-guncelle), taking notes (beyin).
---

# Brain doctor

Work with `beyin.py` in the vault root. macOS/Linux: `python3 beyin.py doctor`; Windows: `py -3 beyin.py doctor`. Do not copy old Bash hook lists or another user's paths.

Read the version, pending/failed jobs, last sync, source conflicts and skill status in the output. Even if the command exits 0, do not interpret an empty lifecycle history as 'client connection verified'. Explain the fault and the smallest fix without dumping error logs or private notes into the chat.

If a source change is not indexed, run `python3 beyin.py sync`; if skill files differ, reconcile them in a controlled way with `python3 beyin.py skill-sync`. If both sides changed, keep the files and say which version should be chosen. If an update was left half-finished, use the `beyin-guncelle` path; do not turn the health indicator green by deleting the runtime database or user files.

When the client connection needs to be verified, use a test note that contains no private data. In a new real session, asking for the information in this note from hook context alone is stronger evidence than checking that the file exists. In Codex check the correct project and `/hooks` trust; in Claude a new project session; for headless Antigravity use the `--add-dir VAULT` binding; in Kiro IDE/CLI V3 the vault folder and the `.kiro/hooks/beyin-v3.json` file; in OpenCode that it was opened in the vault folder and the `.opencode/plugins/beyin-v3.js` file; in OMP that it was opened in the vault folder and the `.omp/hooks/pre/beyin-v3.ts` file. In Pi check `.pi/extensions/beyin-v3.ts`, project trust and a new session; in an external project use only the bridge scoped with an explicit `--beyin-project-root` (`docs/v3/PI.md` is the product document). Do not write trust hashes, and do not count a result obtained through bypass as evidence of a normal install.

The `companion_hygiene` section shows the character counts of the companion files. If Last-Session.md or Threads.md is in `over_limit`, that is a memory hygiene finding, not a sync failure: show the plan with `python3 beyin.py companion-compact --dry-run`, and if it looks right run `companion-compact`. The command moves old sections word for word under `Arşiv/` and deletes no text. Kurallar.md, Core.md and Journal.md accumulate on purpose; their sizes are reported for information only.

`state_storage` shows the size of the local index outside the vault, its free pages, its event record count and leftover old temporary files; it is informational. If `compact_suggested: true`, tell the user the two numbers and show the plan with `python3 beyin.py state-compact --dry-run`; if it looks right run `state-compact`. The command deletes only event records past their retention period and old temporary files, then shrinks the index with VACUUM; it does not touch vault files. Do not delete the `memory.sqlite3` file by hand.

`companion_rules_opening` gives, by the hook's own calculation, how much of Kurallar.md the Claude Code opening shows in full. If `status: clipped`, the rule text (`chars`) exceeds the `share` characters the opening can show in full with these settings, and the rules in between are skipped in every session; this is not a fault. Tell the user the two numbers and suggest shortening the rules and moving long reasoning and detail to a separate note (e.g. `Kurallar-Detay.md`). Do not rewrite Kurallar.md on your own.

The `instruction_references` section lists, with file and line, the `[[wikilink]]` and `[text](path)` links in AGENTS.md, CLAUDE.md, the companion Kurallar.md and the skill folders that have no match inside the vault; code blocks do not count. This is informational and does not set the status to `needs_attention`: tell the user which instruction points to a note that no longer exists, suggest fixing the link if the target moved, and do not invent a note on your own.

`scheduled_check` shows the last `scheduled-check` run of a scheduler the user set up themselves. `never_run` is not a fault; if the user wants an audit or notification even while the clients are closed, suggest the scheduler example in `docs/v3/PREFERENCES.md`, and do not create a job on your own. If you see `error` or an `age_hours` larger than expected, say that the scheduler is not running.

The records in `validity.ignored_rejections` say `validity: rejected` but their `kind` is not inference or preference, so the claim is still in current context. If the user really rejected this claim, add `kind: inference` (or `preference`) to the source; if not, remove the `validity` field. Do not delete the source.

`validity.rejected_dependents` lists current notes that link to a rejected inference with a `[[wikilink]]` or `[text](path)`; `ambiguous_rejected_links` additionally shows the link when one of several notes with the same file name was rejected. This is informational and does not set the status to `needs_attention`: the link may be explaining the reason for the rejection. Tell the user which note relies on a rejected claim; if the note still treats that claim as true, suggest fixing it or linking it to a new note with `supersedes`. Do not change or reject the note on your own.

`review.due` shows that a note's own `review_at` date has arrived: a time to reconsider an idea, not a fault. Tell the user which notes are waiting; suggest moving the date forward, turning the note into a task or retiring it, and leave the decision to them. `review.invalid` lists values that are not real dates; ask the user for the correct date, do not guess.

The `inbox` section is filled only if the user turned on `--inbox-report on`: the number of notes waiting in the inbox folders and the age of the oldest note. For a folder with `attention`, tell the user how many notes have been waiting and for how long, and suggest processing them; do not move, classify or delete notes on your own. If the list is empty or the inbox lives under another name, suggest that the user give the folder name with `--inbox-folder`; do not guess the name.

Tell the user three things: the part that works, the unverified/broken part, and the single next fix if there is one. Give a short, concrete result instead of raw JSON. If the user's existing approval covers the safe fix, do not ask for approval again unnecessarily.

V3.1: `updates` in `doctor` shows the latest version check; a network error does not prove you are up to date. For a version question alone use `beyin.py update --check --metadata-only`. Route update requests to the beyin-guncelle skill.
