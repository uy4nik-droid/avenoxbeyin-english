# Installation, update and rollback

`beyin.py` inside the vault is the single entry point. Run the commands in the vault folder. The examples below use `python3` for macOS/Linux; on Windows, write `py -3` instead. Python 3.11+ is required.

## First installation without Git

Download and unpack the `beyin-v3-X.Y.Z.zip` package from [the latest stable release page](https://github.com/uy4nik-droid/avenoxbeyin-english/releases/latest) (`X.Y.Z` is the version number on the page). The package and the minimum requirements are stated on the release page. GitHub's automatic source archive is different from the product package.

Pick or create a vault folder. Inside the unpacked package:

```sh
python3 scripts/install_v3.py --vault "/full/path/to/Beynim"
```

Windows example:

```powershell
py -3 scripts/install_v3.py --vault "C:\Notes\Beynim"
```

By default the runtime is installed in the operating system's local application data area, outside the vault. If you like, you can pass `--state "/separate/local/directory"` at install time; pick a directory reserved only for this application. The installed entry point and launchers remember this choice. No new account, Git, pip or service is installed.

For the first connection, open the vault in your AI client and start a new session. When hook definitions change, complete the client's required trust review; the updater does not create a trust record. When the `update` result has `trust_review_required: true`, `trust_review_files` says which hook files changed; the human output shows only those clients' steps (`.codex/hooks.json` → Codex `/hooks`, `.kiro/hooks/beyin-v3.json` → Kiro Agent Hooks panel or CLI `/hooks`, `.agents/hooks.json` → Antigravity folder trust, `.claude/settings.local.json` → a new session in Claude Code).

## Checking and updating

```sh
python3 beyin.py doctor
python3 beyin.py update --check
python3 beyin.py update
```

`doctor` shows local records, pending work and problems. A metadata report is not proof of real client delivery or that every note was interpreted correctly.

`update --check` examines the official stable release and verifies the package in a temporary area. It does not change the vault or the existing runtime files. If no package is given, network access is required. `update` applies the new version after the same verification. A second update to the same version is a no-op; numeric version order is used. A downgrade is not done by loading an older package; `rollback` is used to go back.

The default download source is the official GitHub stable release of the `uy4nik-droid/avenoxbeyin-english` repository. A preview, a moving development branch or a third-party package source is not selected automatically. If there is no stable release or no expected ZIP, it reports this as an error; it does not return a result as if a release existed.

With a local, previously downloaded ZIP, no network is needed:

```sh
python3 beyin.py update --check --package "/downloaded/beyin-v3-X.Y.Z.zip"
python3 beyin.py update --package "/downloaded/beyin-v3-X.Y.Z.zip"
```

Take a local package only from a source you trust: the checksum verifies integrity; it is not a substitute for an independent signature or trust in the source.

## Clickable launchers

The installer puts only the launcher for the relevant platform into the vault:

| Platform | Launcher |
| --- | --- |
| macOS | `Beyni Güncelle.command` |
| Windows | `Beyni Guncelle.cmd` |
| Linux | `Beyni Güncelle.desktop` and `Beyni Güncelle.sh` |

All of them call the installed `beyin.py update` command and contain no separate update logic. The operating system may ask for permission to open/run the file. A custom Python/runtime path is recorded at install time; if you moved Python afterwards, the installation needs to be reassessed.

## Interruption or problem

```sh
python3 beyin.py recover
python3 beyin.py rollback
```

`recover` reads the journal of an interrupted operation and completes the planned operation. An error message does not mean the operation was cancelled; some system files may have been written and the successful version stamp may not have been written yet.

`rollback` restores the backup of the last system operation. If you added the [optional global bridge](GLOBAL-BRIDGE.md) yourself, before doing `rollback` or `uninstall` to an older version that does not contain the bridge (V3.1.0 and earlier), remove the bridge handlers from the global settings; leaving a nonexistent script in a global hook produces a client error. If you added the Antigravity bridge, the same applies when going back to 3.9.0 and earlier: the bridge of those versions does not recognize `--harness antigravity`, so first remove the `beyin-v3-bridge` key in `~/.gemini/config/hooks.json`. If you used [Pi](PI.md), when going back to a version without Pi support (3.12.0 and earlier): `rollback` and `uninstall` remove the `.pi/extensions/beyin-v3.ts` file; first remove the path you added to your personal Pi settings or to the `pi -e ... --beyin-project-root ...` alias, otherwise Pi will not start, failing with `Unknown option: --beyin-project-root`. `--harness pi` receipts are written in the source with `harness: manual` and a `client: pi` field that older versions ignore; an older version reads them as manual receipts and `sync` stays healthy, and updating again preserves the Pi attribution. There is no separate exclusion name for Pi; the extension is excluded with the `adapters` group, and older versions recognize this name. In the first V2 migration, the previous version and the recognized old runners are also restored. Rolling back a clean V3 installation is reported as `uninstalled`; a nonexistent older version is not invented. User notes you added later are not deleted. This command is not an operation that undoes the whole vault history.

If there is a user change that came in between in a managed file, the operation stops with a conflict instead of overwriting it. In supported JSON settings, unrelated changes are preserved; a conflicting managed section needs review. If there is a locked/active writer, wait for it to finish and try again. Do not delete the lock/sentinel file of a lost operation haphazardly.

A line-ending difference alone does not count as a change: if `core.autocrlf` or an editor converted a managed file to CRLF, update, removal and rollback do not stop, and the file returns to the stock LF format when it is rewritten. The conflict message states the reason: `content differs` means a real edit, `deleted` means a deleted file.

## Full removal: check the remaining components

`python3 beyin.py rollback` or the installer's `--uninstall` option reverts the managed files
inside the vault. It deliberately **does not delete notes, receipts or the state folder
outside the vault**. Turn off the optional components that were additionally enabled, in this order:

1. First, record the full path of the state folder via `python3 beyin.py doctor` or
   `.beyin-runtime.json`; back up any data you want to keep. Once the vault is removed,
   this CLI and the runtime file may no longer exist.
2. For every active global bridge, run, for example,
   `python3 beyin.py bridge --harness codex --uninstall` with the current CLI inside the vault
   (repeat for every active harness name). Do this step before removing the vault adapter; if
   a vault script that is not in the global settings remains, the client may give an error at startup.
3. If Yakala is installed, run `python3 beyin.py yakala kaldir`. This removes the shortcut, the
   startup integration and the Yakala skill; cards, downloaded files and diagnostic records
   stay in place.
4. Then remove the vault installation with `python3 scripts/install_v3.py --vault "<vault>" --uninstall`,
   or, if you are going back to the previous version, run `python3 beyin.py rollback`.
5. Last, if there is a machine-local index/history you do not want to keep, verify the state
   path and the backup you recorded beforehand; delete the state folder as a **separate,
   explicit decision**. This operation cannot be undone; it is not part of the default removal.

If there is more than one harness or Yakala installation, repeat steps 2 and 3 for each active component.
If the bridge or Yakala was never installed, skip that step. Before removal, inspect with `beyin.py doctor`,
and after the operation, inspect the remaining files with `git status --short`; do not delete the user's settings wholesale.


## Going back to an older version from linked homepages

`homepage-create` pages that copy selected information depend on the current permissions of
their sources. An older reader that does not know about this link (including 3.12.0) may
count the copy as an independent note during `sync`. For this reason, if the target reader
does not carry the safe homepage rollback contract and linked-page markers are found inside the vault,
`rollback` **stops without changing the system files**. A retry of a half-finished rollback
and the `recover` path also repeat the check.

After deliberately moving the copied or derived copies out of the vault in the current version,
try again. Deleting only the link markers is not enough: if copied sensitive values remain,
an older reader may read them as ordinary notes. The command does not delete user notes, change
privacy metadata or break the link on its own. If there is unreadable Markdown, the operation
stops because safety cannot be verified. In vaults with no linked copies, rollback works
normally. This protection is for the supported `rollback`/`recover` flow; replacing the runtime
files by hand with an old version or reinstalling with an old installer is not considered a
safe way back.

## Moving the state directory

The state directory is outside the vault, under the local account, and its default location is
the operating system's application data area (`%LOCALAPPDATA%` on Windows). In some cases it
is necessary to leave this default and put the state somewhere else:

- If the client is installed as an **MSIX package**, Windows redirects the `%LOCALAPPDATA%`
  path to the package's container (`...\Packages\<package-identity>\LocalCache\Local\...`).
  Processes running inside and outside the package can read the same string and go to
  different directories; then half of the memory is left on one side and half on the other.
- The container path contains the package identity. If the application is reinstalled with a
  different identity or the container is reset, the pinned path becomes invalid.
- If `%LOCALAPPDATA%` is redirected to a folder synced with the cloud, the state must not be synced.

Moving is a supported operation: `install_v3.py --state` pins the new path. The database is
tied to the **vault root path**, not the state path; so moving the state for the same vault
does not invalidate the database. Moving the vault is a separate matter: the installer
explicitly pulls the binding to the new path with the old state and `--rebind-state` (in a
moved vault, `beyin.py update` stops until this step is done); for details see [MULTI-MACHINE](MULTI-MACHINE.md#moving-the-vault-to-another-folder-or-account).

### Steps

1. **Close the agent sessions.** A running worker may be writing to the state.

2. **Read the current path.** The `state` field in the `.beyin-runtime.json` file at the vault
   root is the pinned path. Do not edit this file by hand; the installer writes it.

3. **Pick the target.** A directory outside the vault, reserved only for this application, on a
   local fixed disk and without cloud syncing. Example: `F:\beyin-v3-state`.

4. **Copy the directory.** The whole content is moved: `memory.sqlite3`, `v3-install.json`,
   `hook-queue/`, `hook-done/`, `markdown-journal/`, preference and cache files.
   After copying, compare the file hashes.

5. **Do not copy the `update-journal.json` file.** If there is a journal left over from an
   interrupted update, it must not be moved to the new location. If `install_v3.py` sees a
   pending journal in the target state, it does not do a fresh installation; it calls `recover`
   and **continues the old operation**, targeting the old pin. The result returns
   `install_resumed: true` and `.beyin-runtime.json` does not point to the new path. If there
   is a journal in the old directory, first complete the operation there with
   `beyin.py recover`, then copy.

6. **Run the installer with the new path.** First inspect the plan:

   ```powershell
   py -3 scripts/install_v3.py --vault "C:\Notes\Beynim" --state "F:\beyin-v3-state" --plan
   ```

   If the plan is clean, run the same command without `--plan`. After creating the directory,
   the installer re-resolves it and pins the canonical path.

7. **Verify from both sides.** Run `py -3 beyin.py doctor --json` both from the agent shell
   (inside the package) and from a normal PowerShell window (outside the package); it should
   give the same result. The `state_location` field should show the `warnings` list empty and
   the `sibling_state_roots` list with a single entry (or empty). In the human-readable output
   that runs without `--json`, each warning is a line starting with `State location (info):`;
   there should be none.

8. **Delete the old directory only after this.** Wait until the verification passes.


### Recognizing a split state

A split does not present itself like a broken installation: both directories really exist
and both have a `v3-install.json`, because one was installed from inside the package and one
from outside. Looked at alone, both seem healthy; the difference is that which half a session
reads depends on whether the process is inside the package.

`doctor` reports this under `state_location`:

- `sibling_state_roots`: all the state roots installed for the same vault key, counted once
  by directory identity. If there is more than one, a `state_split` warning is given. Since
  plain writes inside the package are also redirected to the container, a real split is most
  reliably visible from **outside the package**.
- `pinned_in_package_container`: the pinned path passes through `Packages\...\LocalCache`.
- `pin_resolves_elsewhere`: this process resolves the pinned string to a different directory.
  The field is filled on every platform, and the warning is given only on Windows; on macOS
  and Linux a symlink goes to the same place for every process and causes no split.
- `pinned_state_empty`: no installation was found at the pinned root.
- `effective_state_differs`: this run reads a different state instead of the pinned root
  (for example, the source CLI was called with a different `--state`).

These are informational; they do not raise the `doctor` status. If you see a split, decide
which half is current (the `memory.sqlite3` dates and the receipt count help), move it with the
steps above; delete the other only after the step 7 verification has passed.

### Old installations pinned with a pre-redirection path

In an MSIX installation made with 3.4.0 and earlier (before the #114 fix), the pinned path may
have been written without the redirection being applied. This does not fix itself. To fix it,
run the installer containing #114 **from inside the package** (from the agent shell) again with
the current `--state` value; the pin returns to the redirected canonical path. In this case no
copying is needed, but the rule in step 5 applies: if there is a pending `update-journal.json`,
first run `beyin.py recover`, then inspect first with `--plan` as in step 6.

#### If `update` and `recover` both give `transaction target escapes root` (#139)

Viewed from inside the package, the state root may stay in its old spelling while the files
inside it can resolve under `Packages\<package>\LocalCache\...`. This happens when the root
itself also exists outside the package. The updater before this version counted the two
spellings as different directories and stopped the operation; `recover` and the installer that
delegates a pending journal to `recover` went through the same check, so all three were stuck.
Now, if it sits under the target root by name and there is no link (symlink, junction) in
between that leads outside the root, it is written; a link that goes outside the root is still
rejected.

A stuck vault cannot get past this wall with its own installed `recover`, because the
installed updater carries the old check. Download and unpack the package of the version that
contains the fix, then run the installer **from inside the package** (from the agent shell)
with the `state` value in `.beyin-runtime.json`:

```powershell
py -3 scripts/install_v3.py --vault "C:\Notes\Beynim" --state "<state in .beyin-runtime.json>"
```

The first run completes the pending operation (`install_resumed: true`). Run the same command
once more; this time the new version is installed and the vault gets the fixed updater. Then
verify with `beyin.py doctor`. Do not edit the pin file by hand.

## `invalid legacy skill hashes` (#73)

Some vaults installed from `main` after `cad7953` (#35), between 17 and 19 September 2026,
carry the `3.0.2` stamp but use a package verifier different from the official V3.0.2 tag.
This verifier rejects the new skill paths in the V3.1.0/V3.2.0 manifest; `update --check`
gives the same error. A migration done from the official V3.0.2 package does not represent
this special case.

The package format prepared for V3.2.1 is compatible with this old verifier; once it is
published as stable, a normal `update` is enough. Do not assume a fix that has not yet been
published is installed. To move to the current V3.2.0 right away:

1. From [the official V3.2.0 page](https://github.com/uy4nik-droid/avenoxbeyin-english/releases/tag/v3.2.0)
   download `beyin-v3-3.2.0.zip` and the `.sha256` file next to it. Before unpacking the ZIP
   and running the code inside it, compare the SHA-256 value. Use
   `shasum -a 256 beyin-v3-3.2.0.zip` for macOS/Linux and
   `Get-FileHash beyin-v3-3.2.0.zip -Algorithm SHA256` for Windows; the result must equal the
   first field of the official `.sha256` file.
2. Close the agent sessions. Unpack the ZIP into a separate folder outside the vault. Read the
   `state` path in the existing vault's `.beyin-runtime.json` file; if you used a custom state,
   do not create a new default state. Do not modify this file.
3. In the unpacked package folder, inspect the plan with the real vault and existing state paths:

   ```sh
   python3 scripts/install_v3.py --vault "/full/path/to/Beynim" --state "/existing/state" --plan
   ```

4. If the plan succeeds, run the same command without `--plan`. The installer verifies the
   package hashes, stops with a conflict on existing user edits, and creates the update
   journal/backup. If there is a conflict, do not overwrite the files; first inspect the
   change. Do not edit `.beyin-version` or the installed Python files by hand.
5. Check the result inside the vault with `python3 beyin.py doctor`. If the hook definitions
   changed, complete the Codex `/hooks`, Kiro Agent Hooks panel or CLI `/hooks` review and
   open a new session.
   Later updates again use the normal `update` command; if needed, `rollback` brings back the
   previous installation.

On Windows, use `py -3` for the Python commands. This path uses the installer of the verified
official package instead of calling the installed old package verifier; user notes and the
existing state directory are preserved.

## What changes?

The package updates only the managed engine files, the installed entry point/launchers, the three core skills and the client connections. A custom skill with the same name or a modified managed script is not silently overwritten. Unrelated user settings are preserved with the supported merge rules. Markdown notes, Companion texts and old daily/knowledge sources are not replaced by the package contents.

In the V2 migration, stock writers recognized by hash are replaced with reversible, inert entries. This way, an old command remaining in an already-open client does not restart the model compiler either. Customized runners and schedulers outside the project are assessed separately. [Migration guide](MIGRATION.md).

## Checks applied

The archive allow list, file SHA256, version and runtime schema are verified. The package Python files are compiled; the new code passes an init, sync, source search and receipt test in a separate synthetic vault. Real vault notes are not used for this test. The implementation has a local lock, a persistent journal with the previous/new file contents and modes, managed-file hash checks and a runtime database check before the version. The version stamp is written last.

These checks are not a distributed cloud lock or an atomic transaction for all external applications. Changes seen from another editor are preserved; real client behavior is verified separately. [Platform report](PLATFORM-TESTS.md).

## Component exclusion and updates

A user can exclude components they do not need (`skills/<name>`, `adapters/<name>`, `launchers`, `agents_block`, `harnesses/antigravity`) with `--exclude-component` at install time or with `beyin.py preferences --exclude-component <name>` at runtime (and turn them back on with `--include-component`).

- During `update` and `install`, managed and unmodified files belonging to excluded components are cleaned from disk and dropped from the manifest.
- Files modified by the user are never deleted or overwritten; they are preserved and reported in the operation summary.
- If the user removed the V3 regions in shared files (`AGENTS.md` or `.agents/hooks.json`) by hand, no conflict is produced.
- On rollback, the previous state is restored; the exclusion preferences in the `.beyin-exclusions.json` file are preserved.
- If the exclusion file cannot be read, the operating system error is preserved; an invalid JSON or UTF-8 error names the file. Read errors do not change the file.

## Package building for developers

At the repo root:

```sh
python3 scripts/build_v3_release.py --output "/tmp/beyin-v3-3.13.0.zip" --version 3.13.0
```

This command only builds a local ZIP; it does not publish to GitHub. The package contains `manifest.json`, the allowed installer/entry files, the runtime modules and the three skills. The manifest carries the version, schema/runtime schema, minimum Python, file hashes and recognized legacy hashes. Publishing the release and the final platform CI are separate operations.

## V3.1 version notifications

Update a V3.0.2 installation once with `python3 beyin.py update`. The new notification code runs after this first migration. On Windows, use `py -3`. Session opening does not wait for the network; the short-lived worker checks only the official GitHub metadata at most once a day. The result of the first check becomes visible in the next session or `doctor` call. The same version is not shown again at every prompt. Notes and prompts are not sent for this check, and no model call or automatic installation is made.

`update --check --metadata-only` reads only the version information: it does not download the ZIP, does not run package code and does not write the vault/runtime/cache. The full `update --check` continues to run the existing package verification and the temporary synthetic installation. A metadata result is not proof that the package can be installed. A network error does not mean "you are up to date"; doctor shows the last successful check date and the status.

`preferences --update-notifications off/on` manages the notifications and the automatic version network access; it does not change the memory synchronization preference. `BEYIN_UPDATES_OFF=1` takes precedence over this preference. `update --dismiss X.Y.Z` silences only that version's session notification; doctor continues to show the version. The preference and cache are in the state directory outside the vault; since no field was added to the old preference schema, rollback to an older version is safe. When internet access is off, `update --package /path/package.zip` can be used.

In an online ZIP download, the GitHub asset SHA-256 and, if present, the official checksum file are verified before any package code is run. The cache is not the source of the package to be installed; the installation reads the official metadata again. A checksum is not an independent publisher signature. `context --no-sync` creates no version check, worker or notification record.

## Release for the maintainer

`VERSION` and `docs/v3/releases/X.Y.Z.md` define the same version. The `Verified V3 release package` workflow builds the ZIP once; six OS/Python combinations verify this same ZIP with a clean installation, migration from the published real V3.0.2 and V3.1.0 packages and the `cad7953` intermediate installation, no-op, rollback and interruption/recover. PR runs do not publish.

A manual `workflow_dispatch` with `publish=true` on main, if the tests are green, first uploads the same bytes as a draft, then publishes it as stable/latest and downloads the published asset again to verify it. An existing release is not overwritten; a new version number is needed. The optional global bridge (#41) entered the package with V3.2.0; installation and update do not change the global settings ([GLOBAL-BRIDGE.md](GLOBAL-BRIDGE.md)).
