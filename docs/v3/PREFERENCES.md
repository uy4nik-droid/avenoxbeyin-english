# Automatic check and context preferences

The user setting is in `.beyin-preferences.json`; it is not a managed release file. The installer, updater and rollback do not change this file. If the file does not exist, the existing normal behavior is kept. The shared Python application reads the same settings on Windows, macOS and Linux; there is no new service or model dependency.

Use `python3 beyin.py preferences --profile economical` for economical use, `--profile normal` for normal and `--profile manual` for manual use. If no argument is given, the settings are read. The agent applies them through the beyin skill. `--human` gives readable output.

Fields: `auto_sync` boolean; `interval_minutes` 0–1440 (0 means every event); `context_mode` turn/session/off; `context_chars` 1000–12000. The character limit applies to the whole of the additional hook context; it is not a token quota. Numeric and unknown fields are validated, and a faulty file is not silently overwritten.

Economical profile: auto_sync=true, interval_minutes=15, context_mode=session, context_chars=2000. Manual: auto_sync=false and context_mode=off. To change just one field of the existing settings, for example `preferences --interval-minutes 30`; choosing a profile resets the automatic check and context fields to that profile, and keeps the independent secret filter preference. Changing the interval does not turn on a check that is off.

## Daily receipt layout

`python3 beyin.py preferences --daily-layout flat` writes the daily receipt views
to the path `daily/YYYY-MM-DD.md`. The default `v3` keeps the existing
`daily/v3/YYYY-MM-DD.md` layout; to go back, use `--daily-layout v3`. The preference
is applied with the next `sync`. The setting is in the `.beyin-daily-layout.json`
file in the vault root; if you sync the vault with Git, sync this file too. It is not
machine-specific, and profile changes do not affect it.
A separate file keeps compatibility with the strict `.beyin-preferences.json` schema
of older versions; older engines do not apply this preference, so update all machines
that write to the same vault.
The ownership of flat views is kept in a separate `receipt_flat_views` table; a
`rollback` to 3.11.0 leaves no paths in the old engine's view table that it does not
recognize. The old engine uses the `daily/v3/` layout and keeps the existing flat views.
After updating again, the preference is applied again. If the Obsidian daily notes
plugin opens the flat view, text written there also counts as a manually edited view and
is archived on recovery.

If the flat target has a non-generated human daily note that the engine does not track,
the file is kept, no view is written and no conflict arises. Receipts stay in
`knowledge/v3/outcomes.md`; receipts that reference a human daily note are not hidden
from context. When the layout changes, the old tracked view is removed only if it is
identical to the bytes last written.
A manually edited view is kept, and `sync` and `doctor` give a visible warning.
`python3 beyin.py sync --recover-views` archives this edit losslessly in the `.archive/`
next to it and regenerates the view or removes the old view. This command also does not
touch an untracked human daily note.

`preferences --human` shows the active layout and the target path pattern. If the flat
target is a symbolic link, the target file is not touched; `sync` keeps processing the
other notes with a source warning. After the state is rebuilt, views left in the old
layout with `generated: true` and `kind: receipt-index` are also found. If their bytes
are identical to the content that would be generated in the new layout, they are
retired; if they do not match, they are kept because they may have been changed by hand,
and are archived losslessly only with `--recover-views`. A flat file name alone is not
proof of ownership; if the state and the generated header are both lost, it counts as a
human note.

The identity evidence of a receipt that is excluded from context because it rests on a
generated view stays in `receipts/<event-id-sha256>.md.view-provenance.json`. The receipt
Markdown does not change; the marker carries no summary text or note content. When the
state is deleted and rebuilt, or when moving to another machine, this receipt stays
excluded; **new-identity** receipts that rest on a human note that later uses the same
old daily path can become visible. When syncing `receipts/`, sync these JSON files too and
do not delete them, to preserve the historical evidence. A corrupt marker is not silently
repaired; the receipt concerned is kept out, a warning is given and existing views are
kept. If the marker cannot be written or the POSIX directory `fsync` fails, the last copy
of the view is not deleted either; fix the problem and run `sync` again.
On Windows there is no directory `fsync` with Python's standard API; file `fsync` and
atomic replacement are applied. Older engines cannot read the new JSON markers; even if
the file format does not break them, update all machines for this exclusion guarantee
after state loss. SQLite exclusion rows left from the previous version are moved to
these markers during the first `sync`. If, before the update, the evidence of both the
state and the old view is already lost, the history cannot be safely recovered; an old
state or vault backup is needed. To avoid hiding human daily notes by mistake, historical
ownership is not made up from the file name alone.

### Obsidian graph and receipt files

Each receipt is written under the name `receipts/<event-id-sha256>.md`. This name is the
receipt's identity: repeating the same submission, recovering a half-finished write,
matching a copy coming from another machine, and older versions all work with this name.
For this reason Beyin does not rename receipt files; renaming them by hand too, a file
whose name does not match is not read as a receipt.

The `daily/v3/` and `knowledge/v3/outcomes.md` views link to the receipt in the form
`[[receipts/<hash>.md|<event_id>]]`; in the reading view the event id appears instead of
the hash. For a receipt whose summary is hidden (bound to a private, untrusted, unreadable
or index-excluded source) the event id is not shown either; the link stays only with the
hash name, because the id the agent chose often says the same thing as the summary.
`recap` does not show the event id either.

The Obsidian graph labels nodes with the file name; the `aliases` or `title` property
does not change the label in the core graph. For this reason receipt nodes appear in the
graph with their hash name, and `outcomes`, which links to every receipt, becomes a large
hub node. Beyin does not touch the `.obsidian/` settings; taking receipts out of the
graph is the user's choice in Obsidian:

- To hide them only from the graph, type `-path:"receipts/"` into Filters > Search files
  in the Graph view settings (gear icon). To hide the generated views too, use
  `-path:"receipts/" -path:"daily/v3/" -path:"knowledge/v3/"`. `path:` searches inside the
  path; another folder whose name ends with `receipts` is also hidden. Search and the file
  explorer do not change.
- To take them out of the graph and search together, add `receipts/` to the Settings >
  Files and links > Excluded files list (and `daily/v3/` and `knowledge/v3/` too if you
  like). Obsidian does not show files matching these patterns in Graph view, Search and
  unlinked mentions, and de-emphasizes them in Quick Switcher and link suggestions.

These settings affect only Obsidian; `sync`, `recap`, `context` and the session opening
context stay the same. In the flat layout the views are in the same `daily/` folder as
human daily notes; if you exclude the `daily/` folder, your own daily notes are hidden too.

## Memory file limits

`Last-Session.md` is limited to 3,000 characters by default and `Threads.md` to 8,000.
`python3 beyin.py preferences --last-session-chars 4000 --threads-chars 12000` changes
the limits between 1,000 and 200,000, and `0` turns off the limit concerned. These two
fields are kept not in the vault preference file but in `companion-limits.json` in the
runtime folder: since older versions reject an unknown preference field, rollback stays
safe, while the setting is machine-specific. A profile change does not reset the limits.
A faulty value or a corrupt limits file prevents any setting from being saved. The
warning at the start of a session when the limit is exceeded, the `doctor` report and
the lossless `companion-compact` command are described in [the companion review](COMPANION-PARITY.md).

## Memory context at session start

The memory context at the start of a session (and continuity questions like "where did we leave off")
carries the `Core`, `Kurallar`, `Last-Session`, `Threads` and `Journal` files together. Since the limits of
the two handoff files alone are 3,000 + 8,000 characters, the 12,000 ceiling can be tight.
`python3 beyin.py preferences --companion-context-chars 24000` gives this opening context a
separate budget between 1,000 and 24,000; `0` uses the `context_chars` value again. The
context in other turns stays limited by `context_chars`. The setting is kept not in the vault
preference file but in `companion-context.json` in the runtime folder: since older versions reject
an unknown field or an out-of-range value in the preference file, rollback stays safe. A corrupt file
returns the opening to the `context_chars` limit and is not overwritten on its own.

The client's own limit comes before this budget. In Claude Code, when the hook's `additionalContext`
text exceeds 10,000 characters, it writes the text to a file in the session folder and gives the model
only the file path and a preview of the first ~2,000 characters; there is no setting that raises this limit.
With a full companion only `Core` and `Kurallar` fit into the preview; `Last-Session`, `Threads` and
`Journal` drop out of the automatic context (#175). For this reason, in Claude Code sessions both the opening
and the turn context are produced with at most 9,500 characters (even if `context_chars` is 12,000); the
`preferences` output says this with `client_context_notice`. By default Codex also moves hook context that exceeds
10,000 UTF-8 bytes (about 2,500 tokens of 4 bytes) to a file and gives the model only a head and tail preview;
the middle is dropped (`codex-rs/hooks/src/output_spill.rs`). Since Turkish letters take 2 bytes, in Codex sessions
the context is produced with the same 9,500-character budget, and if the text exceeds 10,000 bytes the budget is
reduced proportionally and regenerated; sections are not cut from the end. Codex's per-hook `additionalContextLimit`
setting is in `.codex/hooks.json`, and since changing this file lowers hook trust, Beyin does not use it. No such
limit was measured for Antigravity, OpenCode, Hermes and OMP.

If the memory files are being trimmed at the opening, an unrelated note selected without a query is not added; the remaining
budget goes back to the trimmed files. If the files fit completely, a recent note of at most 1,500 characters can be added.

`doctor` reports under `companion_rules_opening` how many characters of `Kurallar.md` arrive in full within this budget;
if the rules are trimmed, the `--human` output reports this in a single line (#374). The number changes with the size of the other
companion files and with the receipt. In a sample vault carrying Core 544, Last-Session 1,743, Threads 543 characters and one
receipt, the default 5,000-character opening shows about 1,550-1,750 and 8,000 about 3,050-3,300 characters; with rules of
~50 characters per line this is between 30 and 60 rules.

## Opt-in secret filter

The command `python3 beyin.py preferences --secret-filter on` replaces common access-key formats with `[REDACTED]` before writing, in the receipt summary, the note-create and task-create body, and the `title`, `next_action`, `completion_criterion` and `facts` fields of these commands and of task-update changes. It is off by default; a profile change does not change this independent preference. To turn it off, use `--secret-filter off`.

Prefixed environment variable assignments like `TYPESAFE_API_KEY=...`, `OPENAI_API_KEY=...`, `MY_SECRET=...`, `DB_PASSWORD=...`, `AWS_SECRET_ACCESS_KEY=...` and `PRIVATE_KEY=...` are also recognized; `export`, `set`, `$env:`, `os.environ["..."] = ...` and quoted forms are supported. Windows `setx` and `[Environment]::SetEnvironmentVariable` and fish `set -x` commands, which have no `=` or `:` between the name and the value, are also recognized; in these commands an unquoted value must contain at least one digit, so that the next word in plain text is not redacted. The recognized secret name must be at the end of the variable: configuration names such as `PUBLIC_API_KEY_NAME`, `API_KEY_COUNT` and `SSH_PRIVATE_KEY_PATH` are therefore not redacted. Hugging Face tokenizer fields (`pad_token`, `eos_token`, `bos_token`, `unk_token`, `sep_token`, `cls_token`, `mask_token`) are not counted as secrets. In a name containing a Turkish letter (`KİŞİSEL_API_KEY=...`), the value is redacted and the Turkish part of the name is kept. The existing value length and format limits apply; not every environment variable or short password is detected as a secret.

Additional fixed secret values can be written, one value per line, to the `secret-patterns.txt` file in the runtime folder outside the vault. The file runs no regex; comment lines start with `#`. The matched texts or values are not written to the health record, only the total number of matches is shown in the `doctor` result. This measure reduces accidental persistent writes; it is not a full DLP tool or a tool for cleaning notes already written.

The interval is limited, by the local SQLite record, atomically across clients, from the most recent automatic start. The check does not run unless the next event arrives. In a new session there is always a fresh check; on a recorded worker failure, a retry. If the record cannot be written (another client holds the lock, the cadence file is read-only or the disk is full), the automatic check of that turn is skipped: the hook produces no error, the turn context comes from the previous index, and a warning says the reason — in the case of an interval skip the "interval preference" line, in the case of a write refusal a line saying the record could not be written and pointing to `doctor`. Only the lock and the write refusal are skipped; real errors such as a corrupt cadence table stay visible. If the runtime folder as a whole cannot be written, the hook tries to write to the event queue before reaching this point; that is a separate hook behavior and this rule does not cover it. This low-level check calls no model. Even when automatic context is off, explicit note/task/receipt and context commands work. An operation started before turning it off can complete; metadata that was already pending is kept. The explicit `--drain-queue` maintenance command processes this queue.

If turn context is requested during a check held back by the interval, a short refresh warning is given instead of presenting old records as current. In economical mode, context is not added again in later messages; the beyin skill refreshes the sources directly when information is needed.

Custom V2 cron/LaunchAgent/Task Scheduler jobs or the 15-minute paid agent automations that the user set up separately are not turned off by these preferences. The job concerned must first be identified and managed separately. V3 does not run Luna/Sonnet on its own.

This change is a local candidate; it is not automatically added to the published v3.0.0 package. Until a new package is published, it should not be announced to users as an existing version feature.

## Project-aware session start

The command `python3 beyin.py preferences --project-context on` makes [the global bridge](GLOBAL-BRIDGE.md) add a short block about that project to the start of a session opened in a project outside the vault. It is off by default; when off, the bridge's output does not change. Sessions inside the vault are not affected. When on:

- The newest receipt summary bound to the same `project_id` (the hash of the folder path) is added as a single line, at most 600 characters. If the receipt's source file has been deleted, or the receipt or a source in `refs` is `private` or untrusted, that receipt is skipped and the previous one is looked at.
- That project's due tasks (`due_at` today or earlier by local date, status `active` or `waiting`) are listed with title and next step. If the task has an explicit `project_id`, only the same canonical folder identity matches; with a different or invalid identity there is no fallback to the name. If this field is absent, the old behavior is kept: the `project` field matches the folder name (case-insensitive), and two folders with the same name see the same tasks. The CLI/web does not derive a folder identity from the display name. This partial protection does not exist when reverting to an older version; for use that needs identity separation, use `--project-context off` before rolling back.
- Tasks go through the same gates as normal context: `private` and untrusted records, superseded tasks and sources that changed after being indexed do not enter.
- The titles of other projects' tasks or of projectless tasks are not given, only a count is written: `(N due tasks outside this project)`.
- The block is limited to what remains of the bridge's `--context-chars` budget and to at most 1,200 characters. If there are tasks, the receipt summary does not exceed half of this area. Lines are added whole; tasks that do not fit are counted with `(+N tasks did not fit)`.
- The block is built with a read-only SQLite read; there is no model call and no write. If the read fails, only this block drops, and the bridge's start instruction is given exactly as is.
- Since older versions reject an unknown preference field, the setting is kept not in `.beyin-preferences.json` but in `project-context.json` in the runtime folder; it is machine-specific and rollback-safe. To turn it off, `--project-context off`.

## Protection of sensitive folders

Folders whose name contains a word that signals sensitivity, such as `Kasa`, `Şifreler`, `Müşteriler`, `Özel`, `Private`, are not included in the main memory scan. The same rule applies in subfolders as well; Turkish letters, upper/lower case, and a leading emoji or numbers make no difference. These files are not deleted or modified.

Even if an index left from an older version has not been synchronized yet, sources in these folders are not shown in the automatic memory context. Receipt summaries bound to these sources are also removed from the automatic opening context. If you want a visible memory record, you must keep the file outside the sensitive folder. `visibility: private` can additionally be used for personal notes; the folder name alone does not change the file's operating system and Git permissions.

## Opt-in hygiene signals

There are three signals and all three are off by default; unless turned on, the hook output and the `doctor` report do not change:

```bash
python3 beyin.py preferences --word-cap-warning on --max-words 800
python3 beyin.py preferences --folder-questions on
python3 beyin.py preferences --promotion on
```

- `--word-cap-warning`: after Claude or Codex writes a note (PostToolUse), if the note exceeds the cap, it gives a one-line split signal. This is a signal; the file is not split or moved. The cap is set between 10 and 100000 with `--max-words` (default 500). Codex's `apply_patch` edits are also measured. This signal is not shown in Antigravity, OpenCode, OMP and Hermes.
- `--folder-questions`: at session start, adds at most three questions for top-level folders that have been quiet for more than 14 days. Only the folder itself and its direct contents are looked at; the vault is not scanned. The same folder is asked once until it becomes active again.
- `--promotion`: writes the in-vault paths of edited notes to the `touch-log.tsv` file in the runtime folder; `doctor` produces a hot and cold folder report from them. The decision to move is always yours.

The companion folder, vault-class names (`Kasa`, `Şifreler`, `Müşteriler`, `Özel`, `Private`, including spellings with an emoji or number prefix), archive, template and code folders are exempt from all of these signals. Since older versions reject an unknown preference field, the settings are kept not in `.beyin-preferences.json` but in `hygiene.json` in the runtime folder; it is machine-specific, a profile change does not touch them, and they are rollback-safe. To turn off, give the same option with `off`.


### Inbox report

```bash
python3 beyin.py preferences --inbox-report on --inbox-max-items 10 --inbox-max-days 7
```

It is off by default. When on, `doctor` counts the Markdown notes in top-level folders whose name contains the word `inbox` or the phrase `gelen kutusu` (`📥 000-Inbox`, `00_INBOX`, `Gelen Kutusu`) and shows the age of the oldest note (the `inbox` field). The age is taken from the note's frontmatter `created` date; if there is no date or it is not a real date, it falls back to the file modification time (clone and sync clients can reset this time). If your inbox sits under another name, give the top-level folder name yourself; the list replaces name recognition, and upper/lower case and Unicode spelling make no difference:

```bash
python3 beyin.py preferences --inbox-folder "Capture" --inbox-folder "📥 Notes"
python3 beyin.py preferences --inbox-folder ""   # empty the list, go back to name recognition
```

A folder that is in the list but not found in the vault is shown with `error: not_found`. A folder whose note count reaches the `--inbox-max-items` value or whose oldest note reaches `--inbox-max-days` days is marked `attention`; this is only a signal and does not change the `doctor` status. No note is moved, classified or any agent started; the decision to process is yours. An unreadable folder is not counted as empty, it is listed with `error`. Companion and vault-class folders are exempt; dot folders and symbolic links are not counted. Since older versions reject an unknown `hygiene.json` key, the setting is kept in a separate `inbox-report.json` file in the runtime folder; rollback does not turn off the other hygiene signals. To turn off, `--inbox-report off`.

## Scheduled health check and notification

Automatic checks run on a client event; if no client is opened, a problem that `doctor` sees (sync conflict, stale hook path, skill/instruction conflict, task and validity problems) stays invisible until the next session (#267). `beyin.py scheduled-check` closes this with an operating system scheduler that you set up: it first runs `sync`, then `doctor`, and writes the result to the `scheduled-check.json` file in the runtime folder. `doctor` shows the last run with its age in the `scheduled_check` field (`never_run` if it was never set up); this field is informational and does not change the status. The command calls no model, installs no service, repairs nothing; Beyin does not install a scheduler.

Exit code: `0` healthy, `4` attention needed, `1` the check itself could not complete, `3` another check is still running. `2` is argparse's usage error (a misspelled command, an option that does not exist in an older version); it does not mean "attention". The lock is the operating system's file lock: the lock of a crashed run is released with it, so there is no stale lock to wait for.

When the result needs attention, a line is written to the `scheduled-notice.json` file in the runtime folder and is said once, as a single line, at the opening of the next agent session. This channel always works; with or without `--notify`.

If you add `--notify` (off by default), an operating system notification is also shown at the same moments. There is no extra dependency: on Windows a Windows PowerShell 5.1 toast (these types do not exist in `pwsh` 7), on macOS `osascript`, on Linux `notify-send` (if absent the notification is silently skipped, the line at session opening still appears). It cannot be known that the notification was actually seen (`osascript` returns success even in Focus mode, a Windows toast can silently drop); so the notification is an additional channel and does not replace the session line.

- Only on a state change: once on the transition from healthy to attention, once when it is fixed (`Beyin: issues resolved, vault is healthy.`). It does not repeat every night while the problem persists; it reminds once every seven days. If the check itself cannot complete, the notification does not change and `doctor` shows `error`.
- The text consists of fixed patterns and numbers; it writes no note name, path or project name: `Beyin: sync conflict (2), hook warning (1) - details: beyin.py doctor`. The text is passed to the notification tool as an argument, not through a shell; every subprocess has a timeout.
- The session line is said once by the first session that opens; if the problem is fixed, an unsaid line is withdrawn.
- All the state (last run, last said time, pending line) is in separate files in the machine-specific runtime folder, not written to the vault or `.beyin-preferences.json`; rollback therefore does not break and each machine reports its own health. `doctor` reads from these files only the fields it knows and writes to none; the session opening reads only the small line file and does no vault scan.

A notification reaches the screen only from a scheduler that runs in the user session. The examples below therefore run in the user session; replace the paths with your own vault.

**Windows** (Task Scheduler, "run only when user is logged on": a task with no `/RU` given is set up this way; if "whether user is logged on or not" is chosen, the toast does not reach the screen). In PowerShell, `--%` passes the rest of the line to `schtasks` as is; without it, Windows PowerShell 5.1 breaks the `\"` escapes inside `/TR` and the vault path is split off from the `/TR` value. In `cmd.exe`, `--%` is not written:

```powershell
schtasks --% /Create /TN "Beyin saglik" /SC DAILY /ST 20:00 /TR "py -3 \"C:\Users\YOU\Beynim\beyin.py\" scheduled-check --notify"
```

**macOS** (LaunchAgent). `/usr/bin/python3` is 3.9 on macOS; Beyin needs 3.11 and above. Find the path that is 3.11+ with `python3 --version` (Homebrew: `/opt/homebrew/bin/python3`, python.org: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`). If the vault is under iCloud Drive, Documents or Desktop, macOS closes these folders to background processes; add this `python3` to System Settings › Privacy & Security › Full Disk Access. Because the notification comes through `osascript`, it appears in Notification Center under the name "Script Editor"; it may ask for permission on the first notification. `~/Library/LaunchAgents/com.avenox.beyin-saglik.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.avenox.beyin-saglik</string>
  <key>ProgramArguments</key><array>
    <string>/opt/homebrew/bin/python3</string>
    <string>/Users/you/Beynim/beyin.py</string>
    <string>scheduled-check</string><string>--notify</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/Users/you/Library/Logs/beyin-saglik.log</string>
  <key>StandardErrorPath</key><string>/Users/you/Library/Logs/beyin-saglik.log</string>
</dict></plist>
```

```sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.avenox.beyin-saglik.plist
```

**Linux** (systemd user timer; output is read with `journalctl --user -u beyin-saglik`). Beyin needs Python 3.11 and above; the distribution's `/usr/bin/python3` may be older. Check with `/usr/bin/python3 --version`, and if it is older, write the path that is 3.11+ into `ExecStart` (e.g. the output of `command -v python3.11`). `~/.config/systemd/user/beyin-saglik.service`:

```ini
[Unit]
Description=Beyin health check

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/you/Beynim/beyin.py scheduled-check --notify
SuccessExitStatus=4
```

`~/.config/systemd/user/beyin-saglik.timer`:

```ini
[Timer]
OnCalendar=*-*-* 20:00
Persistent=true

[Install]
WantedBy=timers.target
```

```sh
systemctl --user enable --now beyin-saglik.timer
```

Plain `cron` runs outside the user session; the notification does not reach the screen but the record and the line at session opening still work. Do not throw the output away to `/dev/null`, redirect it to a log file (`>> ~/beyin-saglik.log 2>&1`); on macOS, Full Disk Access is needed for cron too.

To remove it, delete the scheduler task; there is no setting to turn off on the Beyin side.

Where and how it was verified:

| Platform | On a real desktop | Only by test |
|---|---|---|
| Windows 11 (PowerShell 5.1) | `scheduled-check --notify` from Task Scheduler: the notification landed in Notification Center, but did not come as a popup on screen while a full-screen video was open (Windows keeps notifications only in the center at that time; the command still returned 0). At session opening the line was said once | Lock conflict, state transitions, argument literal (with a real `powershell.exe`) |
| macOS | Not tried | `osascript` argv format, with a fake notification tool |
| Linux | Not tried | `notify-send` argv format and being skipped when absent |

## Parallel session notification

When multiple sessions are open in the same vault, agents can touch the shared git index, shared temporary files or the same note. The card side is solved with the companion protocol; this notification is for shared things outside the card (#170). It is off by default:

```bash
python3 beyin.py preferences --parallel-sessions on
```

- When on, at every real user prompt (UserPromptSubmit; SessionStart in Hermes, OpenCode and Antigravity, which send the first prompt as SessionStart) the session writes its own marker. If there is another session that was active in the last 45 minutes and has not yet been announced in this session, a single line is added to the top of the context: `[Parallel session] 2 more session(s) open in this vault: #3f9a1c2b (3 min ago), #e5f6a7b8 (14 min ago). Re-read from disk before touching the same file; run git status before committing.`
- The identity is the first 8 characters of that session's `Receipt session=` value; it is found from the title of the other session's Last-Session card. At most two sessions are written by name in the line, the rest are counted. The same session is announced once in a session; a session opened later is announced once on the next prompt. Synthetic turns like subagent notifications neither write a marker nor get a line.
- The marker is a `session-markers/<sha256(harness + "\0" + session_id)>.json` file in the runtime folder and carries only `schema, harness, session, first_at, last_at, announced`: the prompt text and the working folder are not written. Since the runtime folder is per vault and machine-specific, sessions in another vault or on another machine are not counted.
- SessionEnd deletes its own marker (no ghost session remains after `/clear`). On every write, markers older than 24 hours are deleted and at most 128 markers are kept. An unreadable marker is ignored; a marker error does not bring the hook down, only the line drops.
- Since older versions reject an unknown preference field, the setting is kept not in `.beyin-preferences.json` but in `parallel-sessions.json` in the runtime folder; it is rollback-safe. When off, the hook output does not change and no marker is written. When on, `doctor` writes the number of active markers, read-only. To turn off, `--parallel-sessions off`.

## Preventing context repetition within a session (`--context-dedupe`)

When `context_mode: turn` is on, the hook does a lexical search on every user prompt. In long and focused sessions, passing the same notes to the model again and again with every message needlessly fills the context window (#363). When in-session de-duplication is enabled:

```bash
python3 beyin.py preferences --context-dedupe on
```

- The hook keeps the records it already delivered in this session (`id`, `source_sha256` and text window) in a `session-delivery/<sha256(harness + "\0" + session_id)>.json` file in the runtime folder. The session identity itself is not written.
- The message context is passage-based: another section of a long note (same `id`, different window) counts as new and is delivered; the same window counts as a repeat even if it has been shortened. The budget of the held-back records goes to the new records.
- If a note coming up in the search result was delivered before and the file has not changed on disk, it is filtered; only new or updated notes are delivered to the model in the message.
- The last receipt block added after the notes is also tracked with the same ledger; only the sha256 value of the receipt text is kept in the ledger. The same receipt is given once in a session; it is given again when a new receipt is written or the receipt file changes, and after compaction. A receipt not shown because it did not fit the budget is not counted as delivered.
- If no new note is left in a prompt, the hook returns empty additional context (`{}`); unnecessary token consumption and distraction are avoided. If all the matching notes are held back but the last receipt is new for this session, only the receipt is given. In a prompt where no note matches, no receipt is added either, just as when dedupe is off.
- **Compaction:** When the model compacts the context (`PreCompact` or the Claude Code `SessionStart` event with `source: compact`), the delivery ledger is reset automatically, because old notes drop out of the window.
- `SessionEnd` clears the session's delivery ledger. If the file is edited on disk, the note counts as new because `source_sha256` changes, and it is delivered again.
- A prompt where everything counts as a repeat does not delete the continuity anchor (`topic-refs`); a short follow-up message after compaction does not lose the topic.
- The ledger keeps at most 512 records per session and 8 windows per record (the oldest drops). On every write, ledgers older than 24 hours are deleted and at most 128 ledgers are kept.
- For rollback safety, the setting is kept not in `.beyin-preferences.json` but in `context-dedupe.json` in the runtime folder (off by default). To turn off, `--context-dedupe off`.

## Receipt reminder at Stop

The installation binds the PostToolUse hook, for Claude and Codex, only to tools that edit files (`Edit|Write|apply_patch|MultiEdit|NotebookEdit`). When this event arrives, the hook writes a small edit marker, named with the hash of the session identity, to the runtime folder outside the vault; the transcript is not read. Shell commands do not trigger this event; Bash is not added to the matcher so as not to start a hook process on every command. Instead, in Claude Code, if there are no editor edits in the turn, the Stop hook reads only the last 2 MB of that session's own transcript file and stops at the user message at the start of the turn (#212). If a vault Markdown file that a Bash or PowerShell command in the turn explicitly names (a quoted path, a plain path, or a glob such as `*.md` in the last segment) was changed while that command was running (between the call and the result record), the same edit marker is opened with that command's time. A note that the command only read and that another session or editor changes later is not written to this session. The command text is not written anywhere; only a timestamp is kept. A path given via a variable, a script that computes its own path, a command that writes in the background, moves and deletions are not seen; dot folders and receipt views that sync rewrites are not counted. Commands of Task subagents (their transcripts are in a separate file) and commands before an interruption, compaction or slash command record in the same turn are also not seen. In Codex, shell commands are not read. `note-create`, `note-edit`, `task-create` and `task-update` run from the Bash tool know the session through `CLAUDE_CODE_SESSION_ID`: they open the edit marker themselves and leave a small flag; that session's next Stop queues this write, with its write time, as `PostToolUse` metadata marked `observed: cli`, so that the receipt scope also counts this turn as an edited turn. At Stop, if there is no receipt written after the edits in the runtime record with the same client and the same `session` value, the hook blocks Stop once per session and reminds with the command `python3 beyin.py receipt --harness claude --session <value> --event-id ... --summary ... --ref ...` (`--harness codex` for Codex, `py -3` on Windows; JSON alternative `--file RECEIPT_JSON`) together with the `Receipt session=<value>` information. If this value is not written with `--session` or in the `session` field of the receipt JSON, the receipt does not close this checkpoint. New edits made after the receipt open a new window.

The Stop event is queued before the reminder. If the runtime record cannot be read, the flow is not stopped. A second Stop carrying `stop_hook_active`, the manual profile (`auto_sync: false`) and a `--metadata-only` hook call make no reminder; they do not spend the one-time allowance either. For an external project session, the global bridge gives the same one-time reminder with its own edit observation and the absolute CLI path ([global bridge](GLOBAL-BRIDGE.md#sourced-record-and-verification)). The user can turn off the reminder in this session by writing `[kaydetme]` in a user message; `BEYIN_V3_NO_RECEIPT_REMINDER=1` turns the feature off entirely.

In the receipt summary, a lasting learning is declared on a separate line, at the start of the line: `Öğrenilen: <one sentence>` (or `Ders:`, `Kalıcı öğrenim:`, `Learned:`, `Lesson:`, `Lessons learned:`, `Learning:`; plural forms such as `Öğrenilenler:` and `Learnings:` count too). If there is no learning, the reason is stated on the same line: `Öğrenilen: yok (rutin kontrol)`. Answers such as `yok`, `hiçbiri`, `bulunmadı`, `none` and an empty label do not count as a learning declaration. In a session where files were edited, a bare `Öğrenilen: yok` answer without a reason is questioned once; an empty label is not questioned because it can be a list heading. A parenthesized explanation at the end of the answer (`Öğrenilen: yok (rutin kontrol)`) also does not change the answer; text after the parenthesis counts as a declaration. The label is read only on its own line; expressions inside text such as `machine learning:` are not declarations. If the receipt declares a learning but no note was written under `knowledge/`, `🧠 500-Knowledge/` or `500-Knowledge/` in the session, or there is no such note in refs, the Stop hook reminds the agent once per session to distill the learning under `knowledge/concepts/`. `knowledge/index.md`, `knowledge/log.md` and `knowledge/v3/` do not count as distillation; these can also be changed by the compiler, git or sync. A receipt written in answer to the receipt reminder is checked not at the Stop carrying `stop_hook_active` but at the next Stop. If no lasting concept is needed, it is enough for the agent to say so in one sentence; the hook does not block a second time. Learnings that have not yet become a lasting note can be recorded with `python3 beyin.py learn --session SESSION --candidate "Learning" --source notes/source.md --scope PROJECT` in the `learning-state.jsonl` ledger in the runtime; `learn --list` lists active candidates. If `--scope` is not given, the scope is global. The session value must be the value the hook gave. A candidate recorded after the start of this edit window satisfies both the knowledge distillation reminder and the bare `yok` query; an old candidate is not valid in later windows. In an answer with a reasoned `yok`, an empty label and other receipts that need no reminder, the folder is not scanned. The ledger is a local intermediate record; it does no automatic distillation.

To make silent stagnation visible, the `beyin.py doctor` command writes how many days ago the last knowledge distillation was done and how many receipts have been recorded since that date. The actual output is ASCII, like the other doctor lines: `Last knowledge distillation: 3 days ago (12 receipts since then)`; if there is no concept note at all `Last knowledge distillation: no concept note distilled yet (N receipts in total)`; if the measurement fails `Last knowledge distillation: not measurable (<error>)`. The same folders as the Stop reminder are counted: Markdown notes under `knowledge/`, `🧠 500-Knowledge/` and `500-Knowledge/`. For this reason a hand-edited `🧠 500-Knowledge/` note also counts as distillation and resets the counter; in 3.9.0 and earlier doctor looked only at the `knowledge/` folder. Doctor does not count a note with `generated: true` in its frontmatter; the Stop reminder does not make this distinction. The date is read from the note's frontmatter `updated` or `modified` field, if absent from the file time, because git checkout and iCloud restore reset the file time. `knowledge/index.md`, `knowledge/log.md` and `knowledge/v3/` are not counted, and only the first 4 KB of each note is read.

If, outside the managed block, a V2 phrase that leaves the `knowledge/` folder to the compiler (such as `derleyici yönetir`, `derleyici yazar`, `elle düzenlemeyin`, `compiler-managed`) remains in `AGENTS.md` or `CLAUDE.md`, doctor writes a `Instruction conflict: ...` line and sets the status to `needs_attention`. This phrase leads the agent to avoid writing knowledge notes; removing the line turns off the warning.

## Turn-start context: passage-level strict search

The context the hook adds on every message (`context_mode: turn`) comes from strict search. This search does not score the whole note as a single set of words; it splits the note into Markdown blocks and, from each source, delivers the block that best matches the question, together with its heading path (#83). If the answer is in the middle of a long note, the block carrying the answer comes, not the first characters of the note; a long session archive that contains almost every word also cannot come to the front on every question. There is no model call and no new dependency.

- Splitting: headings (except those inside code blocks) open a section, blank lines separate paragraphs, blocks exceeding about 900 characters are split at a sentence boundary into windows overlapping by 200 characters. Frontmatter is not read; the title, alias and `facts` fields are added to each block's search words.
- Acceptance and ranking: a block requires at least two shared words. The weight is computed with the existing relative idf family, multiplied by the question coverage (`shared words / question words`, the denominator at most 4), and if it falls under `strict_floor` the block is eliminated. Acceptance is done with block frequency, and the ranking of accepted sources with source frequency; a note split into many sections does not make its own words look common. A long message written in a chatty mood is not eliminated because of its length. If a project is selected, the project words do not count as a match.
- The gates are the same: visibility, trust, project, freshness and supersede rules pass through the same `_eligible()` function as the note-level path; the budget and citation contract is the same `pack_context`.
- An empty result is an answer. The old note-level path is returned to only when there is a real error or when the index is being built for the first time.

The index is derived data and is kept in the runtime folder outside the vault as `passages.json` (JSON, 0600 permission, atomic write, 64 MB limit; no pickle). Only changed records are reprocessed; if the tokenizer changes, the cache is rebuilt on its own. The first build runs at most about 1 second in each turn and resumes where it left off; until it is complete, those turns use the old path, so that a large vault does not exceed the hook time.

### `retrieval.json`

The optional `retrieval.json` in the runtime folder (see QUICKSTART for its location) carries two settings:

```json
{"strict_floor": 0.2, "strict_exclude": ["📦 900-Archive/", "Arsiv/Oturumlar/"]}
```

- `strict_floor`: a number between 0 and 2, default 0.20. Raising it reduces wrong additions, and also lowers the rate of finding the answer.
- `strict_exclude`: at most 64 path prefixes relative to the vault root. `daily/` and `receipts/` are always excluded; the list is added to these. The comparison is insensitive to upper/lower case and Unicode form (NFC/NFD), and the `\` separator is also accepted. It is suitable for archive or session dump folders. This setting eliminates results in the strict search paths, including the note-level fallback search. It does not apply to the companion source selection at the `context_mode: session` opening and does not block an explicit non-strict history search. To keep an archive folder out of the index entirely, `--index-exclude-dir`, described below, should be preferred.
- `unscoped_min_shared` (1 or 2, default 1) and `unscoped_dominant_weight` (greater than 0, at most 1; default 1): add two optional rules only to the explicit `beyin.py context` search that runs without `--project`. Both are off by default; details in the section below.
- If the file is corrupt or a value is invalid, the defaults are used; the hook does not break.

This setting is machine-specific and does not enter the `.beyin-preferences.json` schema: we did not want the hook to stop because of a preference field it does not recognize when an older version is reverted to. Older versions ignore keys they do not read in this file.

### Projectless explicit search: two optional rules (#532)

When `beyin.py context "<question>"` runs without a project, results are ranked with BM25 and a note sharing a single word with the question also enters the result. In a vault that keeps most of its notes in a single project (course notes, an old archive), these two things can happen: that project fills the top five of every question with its volume, and a question outside the vault brings an unrelated note because of a single shared word. Two rules for these are turned on with `retrieval.json`:

```json
{"unscoped_min_shared": 2, "unscoped_dominant_weight": 0.25}
```

- `unscoped_min_shared: 2`: a multi-word question must share at least two words with the note (the same gate as in the hook's strict path). A note coming with a single shared word is eliminated; if no note remains, the result is `records: []` and `abstained: true`. An exact name match (#354) or a word naming the note's own project is enough alone ("how is the backgammon game going" reaches the backgammon notes). A one-word question keeps working with one shared word; a typo correction counts in place of the word it corrected, it does not count as a second word.
- `unscoped_dominant_weight`: if a single project holds more than half of the eligible records (the index has at least 20 records), the BM25 weight of that project's records is multiplied by this coefficient. The record is not deleted, it only moves down. Name match, due task and closed task corrections are not scaled. If the project's name, or the name of the folder mapped to it in `.beyin-projects.json`, appears in the question, the reduction is not applied. The record's project comes first from its own `project` field, otherwise from the `.beyin-projects.json` folder mapping; the same logic as `--project`.
- What they do not affect: queries given `--project`, the hook context on every message (strict path), the companion selection at session opening, Jev candidate pools and the `--jev` path.

Why off: the gain depends on the vault's structure. In the measurement that brought the contribution (698 notes, 83% of the notes in a single course project), the two rules together raised top-1 from 14 to 16 on 20 English questions and lowered top-3 from 18 to 17; they returned an empty result on 4 of the 4 questions outside the vault (0 before), and finding the note that was read afterwards in the top five fell from 8 to 7. When the fixed fixtures in the repository are asked through the same projectless explicit search path:

| Measurement (projectless explicit `context`) | off (default) | `unscoped_min_shared: 2` | `unscoped_dominant_weight: 0.25` |
|---|---|---|---|
| Search benchmark, 32 questions, no project: top-1 / top-3 | 30 / 32 | 30 / 32 | 30 / 32 |
| Same benchmark, when the top folder is counted as a project (`knowledge` 57%): top-1 / top-3 | 30 / 32 | 30 / 32 | 21 / 26 |
| Passage corpus, 42 short questions, answers in the 71% project: in the top five | 41 | 41 | 24 |
| Same corpus, project 80%: in the top five, short / long question | 41 / 38 | 41 / 38 | 10 / 0 |
| Decision fixture, 22 expected notes: found / extra delivered | 19 / 43 | 18 / 32 | 19 / 43 |
| Passage corpus noise, 15 casual / 15 agent commands: returned a result | 12 / 13 | 5 / 4 | 12 / 13 |
| Scenario fixture, 12 answered questions: in the top five | 12 | 12 | 12 |

The reduction lowers the hit rate at every coefficient (0.25 to 0.9 were tried) when the answers are inside the dominant project; raising the threshold only moves the boundary. The two-word rule reduces noise noticeably but leaves a question that finds the right note with a single shared word ("revert it the same way") empty. For this reason both are explicitly chosen settings. If most of the notes in your vault are in a single project and your projectless questions are generally not about that project, try turning them on; measure before and after with your own questions.

### Measurement and the default `strict_floor`

`python3 scripts/evaluate_v3_passages.py` measures the two paths from the hook's delivery path (`context_for(strict=True)` and `render_context`) at 2000 and 5000 budgets. The default corpus is synthetic and deterministic; `--vault DIR --questions FILE` does the same measurement read-only on your own vault. `answerable` means the labeled note is delivered and the answer sentence appears verbatim in the delivered text; noise is in how many of the control messages with no counterpart a record was added.

Synthetic corpus (152 notes, 42 questions, two question formats; 15 casual, 15 agent commands and 10 common-word controls), `strict_floor` 0.20:

| | note-level 2000 | passage 2000 | note-level 5000 | passage 5000 |
|---|---|---|---|---|
| short question, answerable | 19/42 | 32/42 | 24/42 | 33/42 |
| long chat message, answerable | 17/42 | 27/42 | 20/42 | 28/42 |
| noise: casual / agent command | 0/15, 0/15 | 0/15, 1/15 | 0/15, 0/15 | 0/15, 1/15 |

A real vault (1,285 notes; 88 labeled questions, each in short, filler-word and long chat form, 264 queries in total; 20 casual, 40 agent commands and 20 control messages built from the vault's most frequent words), hook path:

| | note-level | 0.15 | 0.20 | 0.25 | 0.20 and archive exclusion |
|---|---|---|---|---|---|
| answerable, 2000 | 28/264 | 141/264 | 130/264 | 124/264 | 138/264 |
| answerable, 5000 | 60/264 | 178/264 | 160/264 | 147/264 | 167/264 |
| long chat message, 5000 | 1/88 | 39/88 | 39/88 | 39/88 | 42/88 |
| noise: casual | 4/20 | 5/20 | 1/20 | 0/20 | 2/20 |
| noise: agent command | 16/40 | 23/40 | 13/40 | 8/40 | 12/40 |
| noise: the vault's frequent words | 0/20 | 19/20 | 16/20 | 5/20 | 16/20 |

The default 0.20 was chosen by this rule: the lowest threshold that does not raise the casual and agent-command noise above today's note-level path. 0.15 brings the answer slightly more often but exceeds today's path in both noise types; 0.25 is quieter and brings fewer answers. The cost is clear: only in messages built from the vault's most frequent words does the passage path often add a block (16/20 at 0.20, 0/20 at note level). If this seems too much to you, make `strict_floor` 0.25.

In the same vault, the first index build is about 3 seconds (split over several turns), the cache is 9.1 MB (5.5 MB when the archive is excluded). Under heavy load (load average around 40 on 10 cores) the median time per query is 1.8 seconds at note level and 0.5 seconds on the passage path; about 0.3 seconds of both is the source freshness check. It was measured on a single vault and a Turkish-heavy corpus; measure on your own vault and tune the threshold accordingly.

## Folder names excluded from the index (`index.json`)

If there is a code repository embedded inside the vault, the documents of other projects that repository carries (such as `3rdparty/SDL2/README.md`, `SECURITY.md`) enter the index like your notes and can come ahead of real notes in search. You say which folder names will never enter the index:

```bash
python3 beyin.py preferences --index-exclude-dir 3rdparty --index-exclude-dir target
python3 beyin.py preferences --index-include-dir target   # remove from the list
python3 beyin.py sync
```

- The list holds folder **names**, not paths: when you write `3rdparty`, `3rdparty` folders at every depth of the vault are not scanned. The match is made on the whole path segment (`3rdparty-notes` or `my3rdparty` are not affected), upper/lower case and Unicode form (NFC/NFD) make no difference, and the Turkish `İ/i/I/ı` count as the same letter. At most 64 names.
- Beyin on its own skips only `node_modules`, `receipts`, `__pycache__`, folders starting with a dot and symbolic links; writing these names in the list is allowed but changes nothing. Names like `vendor`, `external`, `third_party` are **not skipped automatically**: a `Vendor` that is an embedded code tree in one vault is the folder of supplier notes in another vault, and we did not want notes to silently drop out of search with an update. Instead, `doctor` shows the indexed folders that carry one of these names and contain upstream documents like `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, with their count (`Index scope (info): ...`) and writes the command to run. The decision is yours.
- `notes`, `knowledge`, `tasks` and the companion folder cannot be put in the list: `note-create` and `task-create` read back what they wrote from the index, and the session-start memory context also takes the companion files from the index. The command rejects these names with the reason. For the same reason, `note-create` and `task-create` reject a new source that would fall under a name in the list before writing the file.
- The active list is visible everywhere: `index_exclusions` in the `sync` output (`excluded_dirs`, the number of folders skipped in this scan `pruned` and the first 20 paths `pruned_dirs`), and the `Folder names excluded from the index` line in the `doctor` and `preferences` output. If you have no list, these outputs do not change.
- When a name is added, the next `sync` deletes the records in those folders from the index (the `deleted` count, `delete` events) and search does not bring them; the files are not touched. When the name is removed from the list, the next `sync` indexes the same files again. Skipped folders are never listed or read, so a large tree adds no load to `sync` time either.
- The setting is machine-specific and sits in the `index.json` file in the runtime folder (`{"schema": 1, "excluded_dirs": ["3rdparty"]}`); it does not enter the `.beyin-preferences.json` schema. The path of the runtime folder is in the `state_location.effective_state` field of the `python3 beyin.py doctor --json` output (see QUICKSTART for default locations). You can also write the file by hand; the rules are the same.
- If the file is corrupt, a symbolic link, exceeds 64 KB, or contains a single invalid entry (path separator, `.`/`..`, empty name, protected name, unknown key), **none** of the list is applied: `sync` does not break, everything is indexed, and the reason appears in the `index_exclusions.error` field of the `sync` output and in the `index.json is invalid (...)` line in `doctor`. A visible error was preferred over a half-applied list.
- If `doctor` cannot read the index query or its records, it does not count this section as empty and healthy: it reports `index_exclusions.status: unavailable` and only the error type. The human output says `Index scope could not be checked (...)`; this does not mean the `index.json` file is invalid or the list was not applied. Other doctor checks continue; this info line alone does not change the overall status or the exit code. The Markdown index table not yet existing before the first sync is not counted as an error.
- This is not a privacy boundary. When reverting to a version that does not recognize this setting (3.9.0 and earlier), the file is ignored and those folders are indexed again; when updated again, the list is applied from where it left off. What reliably keeps a source out of context is the `visibility: private` field. Since the frontmatter of a file that is not in the index is not read, its visibility cannot be known either. So every file under a folder in the list is treated like a private source when it is given as a source to a receipt: `recap` does not show its path, only counts; the session-start context and the project bridge do not show that receipt either. When the folder is removed from the list and reindexed, the decision returns to the note's own `visibility` field.
- A note sitting in a folder in the list does not take part in the other rules either, because it is not in the index: if it retires another note with `supersedes`, that old note counts as current again, and if it carries `validity: rejected`, it no longer blocks the same claim being proposed again. Before putting a folder in the list, check whether it contains such notes.
- The difference from `strict_exclude` in `retrieval.json`: that one eliminates results in strict search; the files are still scanned, indexed and can be found in an explicit non-strict search. `index.json` cuts the scan itself.
- The opt-in word cap signal also skips folders in the list. The inbox report, the closed task report and the knowledge distillation date look at files on disk, not the index; this list does not change them.

## Component and skill exclusion (muting)

The user can mute starter skills, adapters, launchers or hooks that they do not need:

- `python3 beyin.py preferences --exclude-component skills/beyin-doktor`
- `python3 beyin.py preferences --include-component skills/beyin-doktor`

Components that can be excluded:
`agents_block`, `adapters`, `adapters/hermes`, `adapters/kiro`, `adapters/omp`, `adapters/opencode`, `harnesses/antigravity`, `launchers`, `skills`, `skills/beyin`, `skills/beyin-doktor`, `skills/beyin-guncelle`.

The `adapters` group also covers the Pi extension (`.pi/extensions/beyin-v3.ts`). There is no separate name for Pi: `.beyin-exclusions.json` travels with the vault and 3.12.0 and earlier stop the update when they see an unknown name.

The `beyin-kontrol` skill runs only when the user explicitly asks and does not write without approval; it has no exclusion name of its own, and `skills` removes the four starter skills together. A new name was not added, for rollback compatibility, because it would break the `.beyin-exclusions.json` validation of older versions.

Exclusion preferences are stored in the independent `.beyin-exclusions.json` file in the vault root (it does not change the `.beyin-preferences.json` file; so rollback to older versions stays 3.4.0-compatible). When the preference is saved, it is applied at the next install or update (`update` or `install`). Unmodified excluded files are cleaned up, while files the user changed are kept without a conflict. The `doctor` output shows both the applied exclusions and the pending changes.

## Hermes platform preference (`hermes-platforms.json`)

In the Hermes Agent integration, no receipt reminder or end-of-session checkpoint is produced for channels counted as unattended (bot) by default (`a2a`, `cron`, `telegram`, `discord`, `slack`, `whatsapp`, `signal`, `matrix`, `email`, `sms`, `webhook`).

For those who use Hermes as a personal interactive assistant over a channel like Slack, this channel can be marked as attended:

```bash
# Count Slack as attended/with a human:
python3 beyin.py preferences --hermes-attended-platform slack

# Count a custom bot channel as unattended:
python3 beyin.py preferences --hermes-unattended-platform custom-bot

# Go back to the defaults:
python3 beyin.py preferences --hermes-reset-platforms
```

The setting is kept in the `hermes-platforms.json` file in the runtime folder (`{"schema": 1, "attended": ["slack"], "unattended": []}`); it does not enter the `.beyin-preferences.json` schema and is rollback-safe.
