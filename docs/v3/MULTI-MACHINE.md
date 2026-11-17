# Using Beyin on more than one machine

Beyin is local-first: there is no cross-machine sync code, and Beyin does not install git
([UPDATE](UPDATE.md)). If you sync the same vault on two computers (e.g. work and home)
with a tool like git, this document explains which files to sync and how the two machines
should work on the same day ([#112](https://github.com/avenoxai/avenoxbeyin/issues/112)).

Each machine installs and updates Beyin itself. The runtime (SQLite database) is outside the vault,
machine-specific and not synced; each machine builds it itself from the Markdown in the vault.

## Doctor: machine files tracked in Git

`python3 beyin.py doctor` (and the `--human` view) reports, read-only, in the
`tracked_machine_files` field whether a fixed list of installation paths is tracked in the
Git index: the runtime pin, `Beyni Guncelle.cmd`, known hook/adapter files, the Codex
setting and retired runner paths. This is not a scan of all managed files or of user scripts;
the contents of the checked installation files are not read, and Git tracking or settings
are not changed.
If there is no Git / it is not a repository, `skipped`; on access, timeout, unsupported Git or
sparse checkout/index conditions, `unavailable` is reported and it is not counted as a clean result.
The check makes no network access. The warning is informational; it does not change doctor's overall
status or the failure policy of the scheduled check. During the transition, keep each machine's own
backup; this document is not an instruction to untrack automatically or to copy another machine's files.

## What is synced

| Path | Goes into Git? | Why |
|---|---|---|
| Notes and companion files | yes | Markdown is the source of truth. |
| `.beyin-daily-layout.json` | yes | `preferences --daily-layout flat\|v3` chooses the vault's shared view path. Machines that write to the same vault must use the same preference and an engine version that supports this option. |
| `.beyin-workspaces.json` | yes | The metadata of the `workspace` commands (name, type, lifecycle, provision state). Folder links stay in `.beyin-projects.json`; the two must be synced together. |
| `🔮 850-Companion/Arşiv/` | yes | `companion-compact` takes text out of the live file and moves it to the archive, leaving a single marker line in its place. If the archive stays on one machine, the other machine sees a marker with nothing inside. `visibility: private` in the archive means it does not enter automatic context; it does not mean outside git. |
| `receipts/` | yes | The receipt file does not change after it is written and its name is the digest of the `event_id` (`beyin_v3_sync.py` `receipt()`). The other machine takes the new receipt into its own database at the next `sync` (`_scan_receipts()`). |
| `receipts/*.md.view-provenance.json` | yes | Records, with the immutable event identity, that a receipt was excluded because it rests on a generated view. When the state is rebuilt, the old receipt stays excluded; new human receipts resting on the same daily path are not blocked. It carries no content; these files must not be deleted. |
| `.presence/` | only if `parallel-sessions` is on | Short-lived JSON markers for open sessions. They carry the session identity and timestamps; they carry no prompt text or working folder. Git or cloud sync carries this metadata too. |
| `knowledge/conversations/` | only if chat trace is on and a summary was written | Markdown summaries produced from the user/agent conversation; they are synced like note text and can carry content. |
| `daily/v3/`, `knowledge/v3/` | no | These views are produced from the receipts in the local database (`beyin_v3_projections.py` `project_receipts()`). If the receipts are synced, they come out the same on two machines in the same time zone; the file name is the machine's local day, so machines in different time zones can put the same receipt on different days. If they are put into Git, the file coming from the other machine counts as hand-edited (`manual receipt view edit preserved`) and that view is no longer updated. |
| `AGENTS.md`, `CLAUDE.md` | yes | The user's own instructions are also in these files. Since 3.7.0, the Beyin block carries no machine path (`python3 beyin.py sync`), and is the same on every machine that installs the same version. If the block of the machine that updated first reaches the other through git, the other machine's update counts it as its own block and gives no conflict. |
| Installation files | no | Some carry this machine's paths (`.beyin-runtime.json`, hook files, Hermes and OMP plugins); the rest belongs to the version installed on this machine. If the files of the machine that updated first pass to the other through git, they do not agree with that machine's installation record; reinstalling stops with a `Reinstall conflict: managed file changed` error. |

When `--daily-layout flat` is chosen, the generated daily notes are in `daily/YYYY-MM-DD.md`.
Since human daily notes can be found here too, do not leave the whole `daily/` folder out of Git;
separate only the generated files. The local day and time zone rule is the same in both layouts.
Details in [the daily receipt layout](PREFERENCES.md#daily-receipt-layout).

### Privacy choice

Git and cloud sync work by file path inside the vault; `visibility: private`
prevents entering automatic context, it does not take the file out of Git or OneDrive/iCloud/Dropbox.
Before pushing to a shared repository, check these paths with `git status --short`.

If you do not need the cross-device open-session warning, you can add this to your `.gitignore` file:

```gitignore
.presence/
```

This choice prevents open sessions on other devices from being seen. If you want to keep
conversation summaries local, also add this:

```gitignore
knowledge/conversations/
```

This second choice prevents new summaries from being added to Git; it does not stop
tracking files that are already tracked. If you use cloud sync, set the equivalent exclusion
separately in that service. If you want to use summaries or presence markers on another device,
do not add these lines.

## Recommended `.gitignore`

```gitignore
# Beyin installation: each machine installs and updates Beyin itself
.beyin-runtime.json
.beyin-version
beyin.py
Beyni Guncelle.cmd
.claude/settings.local.json
.claude/scripts/
.claude/hermes-plugin/
.claude/skills/beyin/
.claude/skills/beyin-doktor/
.claude/skills/beyin-guncelle/
.claude/skills/beyin-kontrol/
.agents/hooks.json
.agents/skills/beyin/
.agents/skills/beyin-doktor/
.agents/skills/beyin-guncelle/
.agents/skills/beyin-kontrol/
.codex/config.toml
.codex/hooks.json
.kiro/hooks/beyin-v3.json
.kiro/skills/beyin/
.kiro/skills/beyin-doktor/
.kiro/skills/beyin-guncelle/
.kiro/skills/beyin-kontrol/
.opencode/plugins/beyin-v3.js
.omp/hooks/pre/beyin-v3.ts
# companion-compact cross-process lock; persistent but not user data
**/.beyin-compact.lock
# Local lock, requests and full-byte backups of note writers on the same machine
.beyin-note-write/
# Views generated from the local database: each machine generates its own
daily/v3/
knowledge/v3/
```

Check: right after installation or an update, `git status --short` should be empty.

### If there are user scripts in the same folder

The `.claude/scripts/` line above excludes the whole folder; if your own sync script is
also there, it prevents adding it to Git. Before applying the list as is, separate the
user files in the folder. For example, if you only want to sync your file `my-sync.py`,
replace the `.claude/scripts/` line with these two lines:

```gitignore
.claude/scripts/*
!.claude/scripts/my-sync.py
```

Here, since the folder itself is not excluded, the second line can re-include that file.
If there is another rule that excludes a parent folder, examine that too;
`git check-ignore -v -- .claude/scripts/my-sync.py` shows which rule matched. A match
starting with `!` is an include rule; verify with `git status --short` that the file can be added.
Replace the example file name with your own file; do not add managed engine files to this exception.
Excluding only the `beyin_v3*.py` pattern does not cover all installation files: for example
the retired `compile.py` and `flush.py` shells left from old installations can also be managed.

### Untracking previously tracked installation files

Adding to `.gitignore` does not untrack files Git already tracks. `git rm --cached`
leaves the selected file in this working copy, but once the deletion record is committed, **on
other clones the next pull can delete that tracked file**. If there is a local change, Git may
instead stop the pull; in both cases do not continue without checking the installation.

1. **Before** sharing the change and pulling on other machines, on each machine back up that
   machine's vault and the state folder outside the vault to a separate place. Backups must not
   go into Git or the shared sync folder. Do not replace files that carry machine-specific paths
   with another machine's copy.
2. Check the tracked files with a targeted command such as
   `git ls-files -- .beyin-runtime.json .claude/settings.local.json .codex/hooks.json`;
   this example is not a full list. Compare the list above with your own installation, keep
   user scripts and custom hook entries. Untrack only the installation files you selected with
   `git rm --cached -- FILE`; do not untrack the whole vault in bulk. Examine the staged diff before the commit.
3. After the pull on each machine, restore the deleted machine files **from that machine's own backup**
   or run the installer of the verified Beyin package again on this machine.
   Since `beyin.py` may also have been deleted, you can use the `scripts/install_v3.py` entry point in the package;
   give it the existing vault path and this machine's existing state path.
   Copying another machine's `v3-install.json` record is not the supported path for this transition.
   If there is no local state record or the installer reports a conflict, do not get past it by overwriting files; examine the
   [move limits](#moving-the-vault-to-another-folder-or-account) below.
4. On this machine run `python3 beyin.py doctor`; on Windows use `py -3 beyin.py doctor`.
   Examine the active state and `hook_paths` findings, verify that custom hook entries are preserved
   and that there is no unexpected deletion/change in the `git status --short` output.

This transition separates Git file tracking; it does not mean doctor finds all tracked
machine files automatically ([#539](https://github.com/avenoxai/avenoxbeyin/issues/539)).

If `.beyin-runtime.json` still came from another operating system (a `C:\...` path on Windows,
a `/...` path on macOS or Linux), it is not an absolute path on this machine. `beyin.py` then uses
this machine's default state directory; every command says this in a single line on stderr
(stdout and `--json` output do not change) and `doctor` shows it as `pinned_state_not_absolute`.
The hook files of such a vault also carry the other machine's paths; `doctor` lists them under `hook_paths`,
and on this machine installation fixes both together. The installer also does not count such a path as a changed file, it rewrites
it with this machine's path ([#249](https://github.com/avenoxai/avenoxbeyin/issues/249)). Since the
`beyin.py` of 3.8.1 and earlier cannot read this path, `beyin.py update` does not work; run the installer of the new package
once (`python3 scripts/install_v3.py --vault "<vault>"`; if you used a custom state on this machine, give it with `--state`),
then add the file to `.gitignore`.

Default state paths coming from the same or a different operating system (Windows, Linux, macOS) or another user account
(`AppData/Local/beyin-v3/<vault-hash>`, `.local/state/beyin-v3/<vault-hash>`
or `Library/Application Support/beyin-v3/<vault-hash>`) count as foreign pins; the CLI and lifecycle hook fall back to this
machine's and user's local default state directory. Custom `--state` directories are not affected by this
heuristic mapping; on a moved vault, additionally verify the pin and the active state with `doctor`.

`companion-compact` leaves its lock file persistent in the companion folder. Not deleting
the file prevents a new inode from being opened at the same path while the lock is held on POSIX.
The lock coordinates only processes that see the same shared file system; separate working copies
replicated by synchronization tools and NFS/SMB setups that offer no lock semantics are outside this guarantee.

- **3.6.0 and earlier:** In those versions the block carried this machine's absolute command path. Until both machines
  move to 3.7.0, keep `AGENTS.md` (and `CLAUDE.md` too if it carries the block itself) in `.gitignore`;
  once both are updated you can remove the line.
- Your own skills, `.claude/settings.json` or other client settings are not on this list;
  whether to sync them is your decision.

## Recommended `.gitattributes`

```gitattributes
# Receipt files are compared byte by byte: line endings are not converted
receipts/** -text
# Companion files in card and record layout: the additions of both machines stay together
**/Last-Session.md merge=union
**/Journal.md merge=union
**/Arşiv/*.md merge=union
```

**`receipts/** -text`:** Git for Windows' default `core.autocrlf=true` can convert synced
receipt sources to CRLF. The current engine accepts a line-ending-only difference as the same
receipt; older clients may report a conflict because of byte comparison.
This line prevents unnecessary byte changes and old-client problems; `eol=lf` can also be used.

**`merge=union`:** Git keeps the lines of both sides and produces no conflict. It deletes no lines but
can leave duplicates. So it is suitable only for files where only new records are added:
`Last-Session.md` with a card per session, `Journal.md` and the archive. `Threads.md`, `Kurallar.md`
and `Core.md` are deliberately not on the list. In these files a piece of information has a single current form;
if two machines change the same line, a visible conflict is better than two
contradictory lines silently left side by side.

The order of cards merged with union may not be by time, and the blank line between two cards can
collapse. `companion-compact` orders cards not by their position but by the date and time in the heading,
and keeps the newest.

## Working on two machines on the same day

- **Last-Session:** each session opens its own card and edits only that
  ([companion protocol](COMPANION-PARITY.md)). The cards of the two machines are merged with union.
- **Threads, Kurallar, Core:** the section concerned is edited in place. If Git gives a conflict, choose
  the current one by hand.
- **Git steps:** `pull` before starting work; when done, `commit`, `pull --rebase`,
  `push`. If multiple sessions are open in the same vault, do not run git commands from multiple
  sessions at the same time; push from one session or once at the end of the day.
- **Parallel sessions and cross-device awareness:** with `preferences --parallel-sessions on` on, the agent
  gets a one-line warning on its first prompt if there is another session active in the last 45 minutes
  in the same vault ([PREFERENCES.md](PREFERENCES.md#parallel-session-notification)). Sessions are
  synchronized with light `.presence/<session_id[:24]>.json` files in the vault root and machine-local runtime markers;
  when the session closes (`SessionEnd`) the file is cleanly deleted, and markers older than 45 minutes
  are dropped automatically ([#205](https://github.com/avenoxai/avenoxbeyin/issues/205)).
- **Opening a session before a conflict is resolved:** when `pull --rebase` stops at a conflict,
  the markers `<<<<<<<`, `=======`, `>>>>>>>` remain in the file. `sync` does not index a file that
  carries these three markers in order (receipt included) and returns `degraded` with an `unresolved git conflict markers`
  warning; until the file is resolved it drops out of context ([#205](https://github.com/avenoxai/avenoxbeyin/issues/205)).
  Markers inside code blocks are counted too: a conflict example quoted in a note also gives the warning. First resolve the conflict (`git status` must be clean), then
  open a session.
- **Conflict copies of file sync services:** services such as iCloud, Dropbox, Syncthing, Google Drive
  leave the two sides of a conflict as two files ([#205](https://github.com/avenoxai/avenoxbeyin/issues/205)).
  `sync` moves, deletes or renames no file; you decide which side is right.
  - A copy carrying the service's own stamp (`Note (… conflicted copy …).md`, `Note (Case Conflict).md`,
    `Note.sync-conflict-20261006-120000-ABCDEF7.md`) is not taken into the index; it returns `degraded`
    with a `file sync conflict copy` warning. The original note is indexed normally.
  - A numbered name (`Note 2.md`, `Note (1).md`) is only listed when `Note.md` exists in the same folder:
    in the `sync_copy_candidates` field the two files and whether their contents are the same (`same_content`)
    are visible, both stay in the index and the sync status does not change. A real note named like this
    (`Season 2.md`) does not drop out; rename it to take it off the list. If the copy also carries the note's `id`,
    the two files additionally drop out of context with a `duplicate source id` conflict.
  - Anything appended to the `<digest>.md` name under `receipts/` (`<digest> 2.md`, `<digest> (conflicted copy).md`)
    is a receipt copy: it is not indexed, it is visible with a `file sync copy of a receipt` warning. Receipts are
    append-only; compare the copy with the original and delete it.
- **Keep the receipt `event_id` unique across machines:** the agent chooses the `event_id` and the file
  name is its digest. If two machines give the same name to the same topic on the same day (`shared-topic-2026-09-27`),
  two different receipts fall onto the same file and `pull --rebase` stops with `CONFLICT (add/add)`.
  If the conflict is resolved by choosing one side's file, the other machine's database keeps its own summary;
  `sync` gives no warning and the views of the two machines silently diverge. To prevent this, append
  the first 8 characters of the `Receipt session=` value, as in the card heading, to the end of the `event_id`:
  `shared-topic-2026-09-27-3f9a1c2b`.

## Multiple agents on the same machine

When Claude Code and Codex edit human-written notes in the same vault, they use `note-read` and `note-edit`
instead of writing files directly. Last-Session.md, Threads.md,
Journal.md and project notes are included in this flow. For tasks, revision-checked
`task-update` is used, and for receipts and generated views their own V3 commands.

```text
python3 beyin.py note-read "project/Threads.md"
python3 beyin.py note-edit --file request.json
```

To get only the SHA-256 value of an existing note, you can use `note-read "project/Threads.md" --sha-only`. This option keeps the `source`, `exists`, `sha256` fields in the JSON output; it does not send the `content` field. File reading and source validations do not change. For a missing source `exists: false`, `sha256: null` is returned; it can also be used together with `--must-exist`. This option does not make old edits safe without reading the current content; after a conflict, re-read the target text.

On Windows use `py -3` instead of `python3`. `note-read` gives, as JSON, `source`,
`exists`, `sha256`, `content`; if the file does not exist `exists: false`, the last two fields
are `null` and the exit is 0, so the note can be created with `note-edit`. If the
file must exist, add `--must-exist`: a missing file gives `error` (`FileNotFoundError`)
and exit 1. `source` is the real spelling on disk of the existing
file and parent folders; if the request was made with an upper/lower case or Windows
short-name alias, it can differ from the input. In the next request
use this returned path. The managed, hidden and excluded source
rules are re-checked for the canonical path. `content` preserves the text read, including UTF-8 BOM
and CRLF; the hash is the SHA-256 digest of the raw bytes. Build the request from this
read, do not convert line endings:

```json
{"source":"project/Threads.md","expected_sha256":"64-hex-digit-hash-from-the-read","edits":[{"old":"old text that occurs exactly once","new":"new text"}]}
```

Each `old` must be non-empty text and must occur exactly once at the moment it is applied;
multiple edits are applied in order. On an existing file the full `content` is not given.
On a new file use `expected_sha256: null` and `content`, do not give `edits`.
If `secret-filter` is on, a result containing a secret is rejected before the write and the backup;
the text is not silently changed. An edit that removes a secret written earlier is accepted.
`--file -` (default) reads the JSON from stdin. The output is always JSON:
`written` or `unchanged` exit 0, `conflict` exit 2, `error` exit 1.
Command usage errors such as a missing source argument, a missing `--file` value and an unknown option
give `usage_error` and exit 64; for `note-read` / `note-edit`
these are JSON on stdout too. The error object is written in UTF-8; Turkish characters
appear as they are instead of as `\u` escapes. `--help` shows the usual help text.
On a conflict, re-read and rebuild the targeted edit while preserving the other agent's text.
Do not just refresh the hash and rewrite the old text; do not bypass the protection with a direct file write.
A file check, directory fsync, sync or database error after the atomic replacement completes
gives `conflict` / exit 2 and `write_occurred: true`.
This result also carries the canonical `source`, the `written_sha256` digest of the written bytes,
the `backup` path if any, and the `cause` error type. The write has happened; since another editor may have
changed it afterwards, this hash is not a guarantee of current content. First re-read with `note-read` and
run `sync`; do not blindly repeat the same edit. In this case a success notification and a session marker
are not produced.

Managed views are not read or edited as human notes. Even if the file's
`generated` / `kind` headers have been deleted from outside, if there is a current `receipt_views`
record the command is rejected before the write; the canonical file path is checked.
The file name alone or the history of a retired view is not a reason for rejection:
ordinary human notes at the same `daily/DAY.md` path can be used.
If the ownership database cannot be read, an error is returned before the write starts.

The lock and the base64 JSON backups of the previous bytes are under `.beyin-note-write/`
inside the vault. Since MSIX apps can virtualize AppData,
even the same `.beyin-runtime.json` state path can reach a different folder in two clients.
A lock inside the vault is not affected by this divergence. Add the `.gitignore` line above;
the tool also creates a `.gitignore` containing `*` in this local folder.
Keep request files here too with a unique name and delete your own request when the job is done.
Backups can carry sensitive note text and must stay outside sync and Git;
there is no automatic backup cleanup. `writer.lock` is persistent, do not delete it while there are open writers.

The OS lock waits at most 15 seconds and is released when the process exits. `note-create`
also takes the same lock for the existence check, the source write and the index read-back;
clients using different state roots also cannot silently overwrite the same new note.
Replaying, with `sync`, a journal left from a failed `note-create` operation is also
covered by this lock. If the lock is held by another writer, this `sync` skips and preserves
that journal record without waiting; the `sync` of the writer holding the lock or a later
`sync` completes it. This situation is not counted as a conflict and the hook context does not drop. So
the lock of another writer is not waited for while a database transaction is open.
Under the lock
the hash check, the unique target check, the full-byte backup, the write to a temporary file and the atomic
replacement are done; immediately before and after the replacement the source is re-read.
On POSIX the parent directory of the source file is fsynced after the replacement; if this step
fails, a written-but-unverified result is returned. On Windows no directory fsync is done with this stdlib
API; the platform's rename and file flush behavior applies.
A successful write updates the relevant V3 index. If there is a Claude Code session identity,
the receipt reminder window is opened; no automatic receipt is sent.

The protection is cooperative. Obsidian, companion writers and direct file
tools do not take this lock; the before/after check cannot prevent all outside races.
Do not edit the same note concurrently with these tools. The lock gives no guarantee for multi-file operations or for
git working copies on separate machines. Exclude the `.beyin-note-write/`
folder from cloud sync too. The source path must be a vault-relative visible
Markdown file; managed sources, configuration, hidden paths, symlink and
junction paths are rejected.

## Moving the vault to another folder or account

The hook files inside the vault carry the absolute paths of the installation (Python, `beyin_v3_hook.py`, `--vault`,
`--state`). When an installed vault is moved to another folder or to another Windows account
(`C:\Users\<old>\...`), every lifecycle hook fails with a generic error. `doctor` shows this as
`hook_paths: stale` and `needs_attention`; each line gives the file, the event and the old
path (`hook_script_missing`, `other_vault`, `python_missing`) ([#204](https://github.com/avenoxai/avenoxbeyin/issues/204)).

The fix is to run the installer again on this machine with the new vault path. Give the old state folder
(or a copy of it) with `--state`; the installation record is there, and the installer regenerates the managed in-vault
files that carry paths. The index in the state (`memory.sqlite3`) is also tied to the vault path it was built for
and does not open for a vault at another path. If the vault was moved, `--rebind-state`
explicitly pulls this binding to the new path ([#593](https://github.com/avenoxai/avenoxbeyin/issues/593)):

```text
py -3 scripts/install_v3.py --vault "C:\Users\<new>\Beynim" --state "<old state folder or a copy of it>" --rebind-state
```

On macOS and Linux the same command has the form `python3 scripts/install_v3.py --vault "/new/path/Beynim" --state
"<old state folder>" --rebind-state`. The old state path is in the `state` field of the
`.beyin-runtime.json` file in the vault.

**If you set up the global bridge, refresh it separately:** `--rebind-state` does not change the global client settings
or the old vault path in those settings. In the new vault folder, run again the previous `bridge --install` command
for every harness for which you set up the bridge; keep all
`--project-root`, custom `--event` and `--context-chars` choices.
`hook_paths: ok` in the `doctor` output does not prove that the global bridge uses the new path; this check looks only at the hooks inside the vault.
[Verifying the global bridge after a move](GLOBAL-BRIDGE.md#when-the-vault-location-changes).

If the flag is not given and the index is tied to another path, the installer stops without changing any file,
shows the old and new path and suggests the flag. On a moved vault `beyin.py update` also
stops with the same error; `doctor` and `sync` add a `hint` explaining this step to the
`runtime belongs to another vault` error. When the flag is given, the installer applies these rules:

- If the recorded old path no longer exists or is another name for the same folder (for example a name that differs
  only in letter case or a link left at the old path), the binding is pulled to the new path.
- If there is still a folder at the old path and its `.beyin-runtime.json` file points to this state
  or cannot be read, the installer refuses: this may be a copy, not a move, and two vaults would
  share the same state. If the old folder is a leftover no longer used, move it aside or rename it. If you
  will keep both copies, set up the new one with a **copy** of the state folder; the old
  vault keeps working with its own state.
- The `.beyin-runtime.json` in the vault must be the same file that this state's installation record wrote;
  otherwise the installer refuses. Another vault's state cannot be bound this way.
- If the recorded path is not an absolute path on this machine (state coming from another operating system), the installer
  refuses.

The old path appearing to be missing does not by itself prove a move: a removed disk or a
network folder that is not connected at the moment also appears missing. Give the flag only if you really moved the vault. Even
with a wrong binding the records of two vaults do not get mixed: the index stays tied to a single path and the other vault's
commands stop with `runtime belongs to another vault`.

Before changing the binding the installer finishes all conflict checks, writes a full copy of the index
to the state folder as `memory-before-rebind.sqlite3` (later copies with a `.1`, `.2`
suffix, the older one is not deleted) and changes the binding within a single SQLite transaction. The records, event
history and the `hook_done` record are preserved; the result appears in the `rebound` field (`from`, `to`, `backup`).
`--plan --rebind-state` does the same checks, shows the binding that would change in the `rebind` field and
writes nothing. If `doctor` and `sync` are healthy, you can delete the backup copy yourself; since it can carry sensitive
note text, it must stay outside sync and Git.

`beyin.py rollback` reverts the file changes of this installation, it does not revert the index binding:
the binding shows where the vault is. The reverted hook files again point to the old path
(`doctor`: `hook_paths: stale`); run the installer of the version you returned to again at the new path with the same `--state`.
Since the binding already points to this path, no flag is needed.

If the old state does not exist, the installer protects the installation files it finds without a record (like `.beyin-runtime.json`)
with `Unmanaged file conflict` and stops. If the hook files came from another machine through git, the old Beyin entries
inside them, even if they are in Windows' PowerShell `-EncodedCommand` form,
are recognized at installation as Beyin's own entries and replaced with the new ones; no
non-working copy is left next to them.

## How it was verified

Windows 11, Git 2.55 (`core.autocrlf=true`), Python 3.13, `main` @ db1f23d. A local bare
repository and two vaults; Beyin was installed in each with a separate `--state`.

- With the `.gitignore` above, on the second machine `git status` stayed empty after installation
  (`AGENTS.md` was in `.gitignore` as in the temporary note; `CLAUDE.md` was in git and did not change).
- When a managed script was changed as if it came from another version, reinstalling on that machine
  gave a `Reinstall conflict: managed file changed` error.
- A's receipt entered the database and the daily view on B after `sync`. B's receipt passed
  to A. `daily/v3/<day>.md` and `knowledge/v3/outcomes.md` came out byte for byte the same on the two machines.
- When `receipts/** -text` was removed: the receipt on B turned to CRLF, the views diverged,
  and resubmitting the same receipt gave `event id collision`.
- Two machines at the same time added a card to Last-Session, a record to Journal and changed the same Threads line:
  `pull --rebase` merged Last-Session and Journal preserving both records,
  and stopped with a conflict on Threads.
- While Threads was stopped with conflict markers: the first SessionStart left the file out as a changed source;
  the SessionStart after `sync` had the markers in its context. `sync` returned `warnings: []`,
  `doctor` showed nothing.
- Two vaults wrote receipts with the same `event_id` and different summaries: both fell on the same `receipts/<digest>.md`,
  `pull --rebase` stopped with an add/add conflict. After A's file was chosen and the rebase continued, on B `sync`
  returned `conflicts: []`; B's `recap` and `daily/v3` output kept showing B's summary.

## Line endings: `core.autocrlf=true` and receipts

This check was added for [#205](https://github.com/avenoxai/avenoxbeyin/issues/205).
Git for Windows' default `core.autocrlf=true` can check out receipt files not pinned by `.gitattributes`
as CRLF. The current engine writes new digests with LF, accepts a
CRLF/CR/LF difference as the same receipt and does not rewrite the old source file.
The last CR that 3.12.0 and earlier left in the index when reading CRLF output is also counted as the same receipt.
Real changes to the summary, refs or links are still conflicts. In older clients
a line-ending difference can lead to an `event id collision` error.

If `core.autocrlf=true` in a Git repository and there is no `-text` or `eol=lf` for `receipts/`,
`doctor` reports `receipt_line_endings.warning`. This information does not change the status and
does not touch the files. To prevent byte changes and old-client problems you can add `receipts/** -text` or
`receipts/** eol=lf` to the vault's `.gitattributes` file.
Check: `git check-attr text eol -- receipts/x.md`.

For old sources whose line endings changed there is no need to delete the local database;
refresh the comparison with `python3 beyin.py sync --full`. If the raw hash of an old view cannot be
safely regenerated from the receipts, the file is kept. In this case use the
[archiving view recovery](RUNTIME.md#receipt-view-conflict-and-recovery)
command; do not delete the source receipts.

This tolerance exists only in the current engine. `rollback` does not revert the local database and
3.12.0 or earlier still does byte comparison: an old source whose line endings changed
gives `receipt_divergence` again there, and a receipt submitted with a CRLF summary file gets
`event id collision` when resubmitted with the same file. If you will stay on the old version,
the old fix applies: move the `memory.sqlite3` file in the state folder to a backup,
run `python3 beyin.py sync` and then `python3 beyin.py sync --recover-views`;
give the summary with LF line endings on resubmission.

Presence sync is off by default. It is turned on on each device with `preferences --parallel-sessions on`.
The local `<state>/parallel-presence-device.json` file holds a random device identity;
even if two devices use the same user and state path, it does not delete the other's open record.
Do not sync this identity file with the vault. `doctor` does not create an identity or presence file.

## Offline mutation queue (optional, this machine only)

The `mutation-queue` command keeps a local queue in this machine's state folder. It does no cross-device
transport, device authorization, approval protocol or automatic sync; these are open design work under
[#205](https://github.com/avenoxai/avenoxbeyin/issues/205).

**It is off by default.** It is turned on separately on each machine:

```
python3 beyin.py mutation-queue --enable     # --disable to turn off; queued records are kept
python3 beyin.py mutation-queue              # status: enabled, pending/conflicting/failed counts
```

The switch is in the `<state>/mutation-queue-settings.json` file, no field is added to `.beyin-preferences.json`:
since older versions reject an unknown preference field, rollback stays safe. A corrupt
switch file counts as off and is not overwritten. While the queue is off, `--enqueue` and
`--replay` give an error and no queue, identity or lock file is opened; `doctor` shows only
`mutation_queue: {"enabled": false}`.

Commands:

- `--enqueue --file x.json`: `{"action", "source", "payload", "mutation_id"?}`. The actions are
  `note_create`, `note_update`, `task_create`, `task_update`, `receipt`. The payload is validated
  before entering the queue (a full SHA-256 `expected_hash` for `note_update`, an integer
  `expected_revision` for `task_update`). The optional `mutation_id` reduces resubmission of the same mutation
  to a single record; if the same identity arrives with a different mutation it is rejected. Like normal writes it checks
  the state's vault binding: a state bound to another vault is rejected with `runtime belongs to another vault`,
  an unbound state is bound to this vault. The record carries a digest of this binding (not the path);
  `--replay` marks a record bound to another vault `failed` without writing anything. Records that entered the queue
  before this field was added are applied to the state's own vault as before.
- `--list [--status pending|applied|conflict|failed|dismissed]`, `--replay`, `--clear-applied`
  (deletes applied and dismissed records), `--retry <id>` (makes a reviewed `conflict`/`failed`
  record `pending` again), `--dismiss <id>`.

The queue is in `<state>/mutation-queue.jsonl`, the identity in `<state>/device.json`. Since the state is always
outside the vault, neither is synced with the vault. The identity is a random 32-digit hexadecimal
value (uuid4); it contains no user name, machine name or path, is not written to any vault file
and is not shown in `doctor` output. If a presence identity exists, it is adopted on first use and pinned in
`device.json`. Queue writes, replay and cleanup share the common local lock inside the state;
if the lock times out, the waiting call gets a retryable `writer busy` error.
The queue file is rewritten atomically; on Windows a brief sharing violation is retried for a short time
as in other state writes. A corrupt queue line is reported and the file is left
as it is.

Replay rules:

- `note_update` uses the normal note writer; if the source's full SHA-256 does not match, the original
  does not change and a uniquely named `.sync-conflict-*.md` copy created for this purpose is opened
  (`sync` shows it as a warning, does not index it). Metadata that is not given is preserved
  (`visibility`, `project` included). The explicit secret filter applies to both the update and the copy.
- `note_create` and `task_create` do not rewrite if the same content is already on disk; they count it as applied.
  `receipt` follows the engine's own idempotency rule for the same `event_id`.
- On a `task_update` conflict no copy is opened; the record stays as `conflict` for review.

If the index sync at the end of replay does not complete, the applied mutations stay `applied`;
they are not queued again. `source_sync` in the JSON output reports, in the `degraded` / `conflict` case,
at most 20 warnings and 20 conflicts with the total counts; in the exception case the `error` status and error type.
The human output warns too. This diagnosis is not saved to the queue file. `status: succeeded`,
the `applied` / `failed` counts and the exit code are the application result of the queue; they do not show that
the index is fully up to date. To see the problem and refresh the index, run `python3 beyin.py sync`;
when there are no pending records, `--replay` does not sync again.

**Interruption and reconciliation.** The result of each mutation is written to the queue before moving to the next. If the process
dies after applying a mutation but before writing this confirmation, the record stays `pending`. The next
`--replay` checks, before rewriting, whether the target already carries this mutation:

- `task_update`: on a revision conflict `sync` runs first (a half-finished source write in the engine's write log is
  completed), then if the task's revision is greater than `expected_revision` and every requested
  field has the same value, the record becomes `applied` and `reconciled: true`. The revision
  is not incremented a second time.
- `note_update`: if the existing note is byte for byte the same as the content this update would produce, the record becomes
  `applied` and `reconciled: true`; no conflict copy is opened.

If the target does not carry the mutation (for example another writer updated the task with a different value)
the record stays `conflict` and review is needed. This is not a distributed, exactly-once operation;
another writer that independently made the same change is also counted as applied.
