# Optional bridge for sessions outside the vault

The normal V3 installation manages only the hook settings inside the vault. It cannot
see sessions in other project folders. [Issue #41](https://github.com/avenoxai/avenoxbeyin/issues/41)
reported this limit and the missing project origin. This bundled wrapper provides a
connection for explicitly chosen project folders; the default installation does not
change.

## Installation

After installing the V3 package that contains this file, you can install the bridge
automatically directly through `beyin.py` or inspect the configuration:

### 1. Automatic installation (`--install`)

```sh
# Automatic installation for Antigravity (hooks.json and GEMINI.md marker):
py -3 beyin.py bridge --harness antigravity --project-root "C:\MyProjects" --install

# For Claude Code:
python3 beyin.py bridge --harness claude --project-root "/absolute/path/to/MyProjects" --install

# For Codex:
python3 beyin.py bridge --harness codex --project-root "/absolute/path/to/MyProjects" --install

# For OpenCode (global plugin file):
python3 beyin.py bridge --harness opencode --project-root "/absolute/path/to/MyProjects" --install
```

On Windows, use `py -3` instead of `python3` and your real Windows paths. State is
found from the installed `.beyin-runtime.json` file; for special use it can be given
with `--state`. `--project-root` is repeatable and covers subfolders. Choose the
project roots you actually want, not the whole home directory or disk.

Automatic installation (`--install`):
- Automatically detects the relevant harness's global settings file and safely adds the bridge hooks:
  - Claude Code: `~/.claude/settings.json` (that directory if a custom `CLAUDE_CONFIG_DIR` is set).
  - Codex: `$CODEX_HOME/hooks.json` (default `~/.codex/hooks.json`).
  - Antigravity: `~/.gemini/config/hooks.json`.
  - OpenCode: `~/.config/opencode/plugins/beyin-v3-bridge.js` (`$XDG_CONFIG_HOME/opencode/plugins` if `XDG_CONFIG_HOME` is set). Because OpenCode's project plugin is loaded only inside the vault, the bridge writes a managed global plugin that forwards the four lifecycle events to `beyin_v3_bridge.py`. The Python path, the bridge command and the project roots are in the managed `beyin-v3-bridge.json` file in the folder above the plugin (`~/.config/opencode/beyin-v3-bridge.json`); the plugin reads this file on every event. A running OpenCode 2.2.6 service kept using the module it had previously imported even though the plugin file was rewritten in place; for this reason the roots are not held in the module. A reinstall that narrows the roots and `--uninstall` take effect from the next event without restarting the service. It is silent outside the vault and project roots; it carries no Companion data. If a user-owned file exists at either of the two paths, neither is written and the installation stops with an error. `--uninstall` deletes only the two managed files. Compare the path with the `config` line of the `opencode debug paths` output (present in 1.19.5 and 2.2.6); if the OpenCode service runs with a different `XDG_CONFIG_HOME`, install with the same value.
- **Automatic `.bak` backup**: before any existing configuration file is changed, a backup with the `.bak` extension is saved next to it (e.g. `hooks.json.bak`, `settings.json.bak`).
- **Antigravity `GEMINI.md` marker**: when `--harness antigravity --install` is run, in addition to the hook registration, an idempotent block (`<!-- beyin-v3-bridge:start --> ... <!-- beyin-v3-bridge:end -->`) that points to the vault location and the basic instructions is added or updated in `~/.gemini/config/GEMINI.md` in the user's home directory. If the file already exists, it is first backed up as `GEMINI.md.bak`.

Corrupt JSON or an unexpected hook list format is preserved; the installation stops
with an error. The Antigravity instruction also applies only to the chosen project
roots; it gives no instruction to automatically read or modify Companion files.

Global client settings are not within the rollback scope of a vault update.
The Antigravity harness name and receipt format are already supported in 3.11.0; this
change does not register a new harness or exclusion component. When you go back to
3.11.0, the existing bridge commands may work, but the new `bridge --install` /
`--uninstall` commands do not exist. If you also want to remove the global bridge,
run `python3 beyin.py bridge --harness antigravity --uninstall` before the rollback.
The OpenCode bridge came after 3.12.0; before going back to a version that does not
include it, run `python3 beyin.py bridge --harness opencode --uninstall`. Rollback
does not delete the global plugin: in every OpenCode session the plugin keeps calling
the old `beyin_v3_bridge.py` file in the vault, the old version rejects the
`--harness opencode` option, and the plugin silently returns empty (no context and no
records; the OpenCode session is not affected). Because `bridge --harness opencode --uninstall`
also does not exist in the old version, to remove it after a rollback delete, by hand,
first `~/.config/opencode/beyin-v3-bridge.json`, then
`~/.config/opencode/plugins/beyin-v3-bridge.js` (that directory instead of `~/.config`
if `XDG_CONFIG_HOME` is set); `.bak` backups are not loaded by OpenCode. A Beyin
update does not change these global files; if the release notes report a change in
the OpenCode bridge, rerun the `--install` command.

Pi does not use hook JSON. For the same scoped bridge, load the vault-owned extension with
`pi -e /absolute/path/to/MyBrain/.pi/extensions/beyin-v3.ts --beyin-project-root /absolute/path/to/MyProjects`.
Multiple roots, event selection and the context budget can also be set with Pi flags;
see the [Pi document](PI.md#explicit-bridge-from-another-project). This also uses the
same startup/metadata limit; the outside-project scope below applies to Pi as well.
`--print-config --harness pi` is not used. Before you `rollback` or `uninstall` to a
version without Pi support (3.12.0 and earlier), remove this `-e` path from your
personal Pi settings and aliases; once the extension file is deleted, Pi does not
recognize the `--beyin-project-root` flag and will not start.

### 2. Manual inspection and printing (`--print-config`)

If you only want to see the JSON configuration that would be generated, without writing files to disk, you can use `--print-config`:

```sh
python3 "/absolute/path/to/MyBrain/beyin.py" bridge --harness claude \
  --project-root "/absolute/path/to/MyProjects" --print-config
```

This mode does not change files. You can manually add the generated `hooks` event
groups to the existing event lists of the relevant global file.
For OpenCode the output is JSON, but instead of a hook group it carries the paths and
the contents to be generated of the managed plugin file and the settings file
(`plugin`, `content`, `settings`, `settings_content`); the files are still not written.
Back up the existing settings first. Do not replace the whole file with this output;
keep the other settings and hooks. Do not add the same bridge twice; choose a single
target Beyin for a project. The commands carry the absolute path of the current Python
and the installed script; on Windows PowerShell encoded arguments are used. When
moving to another computer, regenerate them there. Enable the hook feature of your
Codex version, complete the `/hooks` trust review and open a new session in the
client. The tool does not produce a trust hash or user approval.

The JSON format was compared on 21 September 2026 with the primary documents of
[Codex hooks](https://developers.openai.com/codex/hooks) and
[Claude hooks](https://code.claude.com/docs/en/hooks). The Antigravity format (named
hook, flat list for `PreInvocation` and `Stop`, the `conversationId` and
`workspacePaths` fields, the command running in the `hooks.json` folder) was taken
from the `hooks.json` document embedded in the Antigravity CLI 1.2.16 binary and was
tried in a real session on Windows 11 with the same version on 10 October 2026; the
document embedded in 1.2.3 (macOS) describes the same format. Live delivery was not
tried on macOS and Linux. A CLI simulation is not evidence of real Desktop hook
delivery; after installation, do the read-back below in each client.

## When the vault location changes

If you moved the vault to another folder or user account, first complete the
[steps for moving and renewing the state binding](MULTI-MACHINE.md#moving-the-vault-to-another-folder-or-account).
The vault installation and `--rebind-state` do not rewrite the bridge commands in the
global client settings. The global commands keep calling the old `beyin_v3_bridge.py`
and `--vault` path ([#618](https://github.com/avenoxai/avenoxbeyin/issues/618)).

- For every harness where you installed the bridge automatically, rerun the previous
  `bridge --install` command **in the new vault folder**. Keep in the same command all
  the `--project-root` roots you chose before, the custom `--event` list and the
  `--context-chars` budget; only the roots you pass again are covered, and if events
  and budget are not given, the defaults are used. Run it with the account the client
  uses and, if any, the custom `CLAUDE_CONFIG_DIR` / `CODEX_HOME`. The Beyin bridge
  handlers in the relevant global settings are refreshed, and unrelated settings are
  kept. The Antigravity `GEMINI.md` bridge marker is also updated with the new vault
  path.
- If you installed manually, generate the `--print-config` output from the new
  location with the same scope, event and budget options, and in the global settings
  replace only the old Beyin bridge handlers. Do not overwrite the whole file.
- For Claude, Codex and Antigravity, check that the registered commands match the
  `--print-config` output generated from the new vault path. Complete the required
  client hook trust review and open a new session. If the `SessionStart` context is
  on, also verify that the `Beyin CLI` path the bridge gives in an allowed project
  outside the vault shows the new vault.
  `hook_paths: ok` in `doctor` checks only the hooks inside the vault; it does not
  mean the global bridge points to the right place.

If you use Pi, point the `-e` extension path in your personal settings or alias to
the new vault; keep the project scope, event and budget choices. No hook JSON is
generated for Pi.

Global settings belong to the user and are not within the rollback scope of a vault update.

## Scope and separate budget

- `SessionStart`, `Stop`, `PreCompact`, `SessionEnd` are forwarded. `UserPromptSubmit`
  is never forwarded.
- In Claude and Codex, when `Stop` is selected, the installation also attaches a
  `PostToolUse` handler only to file-editing tools (`Edit|Write|apply_patch|MultiEdit|NotebookEdit`).
  This event is not queued, does not start synchronization and does not add context;
  it only writes a small edit marker in the runtime folder, named with the hash of
  this project and session. The path, tool input or transcript is not stored. Edits
  made with shell commands do not trigger this event; a note or task written with
  `beyin.py` from the Claude Code Bash tool opens the same marker (using Claude
  Code's `CLAUDE_CODE_SESSION_ID` value).
- The event set can be narrowed with `--event SessionStart --event SessionEnd`. If
  `Stop` is not selected, the `PostToolUse` handler is not installed either. A
  reinstall removes all the previous bridge handlers and writes the chosen set.
- Antigravity has no `PreCompact` and `SessionEnd`. The same limits as the vault
  adapter are used: `PreInvocation` counts as `SessionStart` only when
  `invocationNum: 0`, and `Stop` counts as `Stop` only when `fullyIdle: true`. Because
  the hook command runs in the `hooks.json` folder, the project is the first
  `workspacePaths` entry in the payload; it does not fall back to the process working
  directory. If one of the workspaces is the vault or another installed vault, the
  bridge stays silent and the events are left to that vault's local hooks.
- `--context-chars 1500` is the startup instruction limit (0-4000). `0` turns off
  injection. If the full instruction does not fit, empty output is returned instead of
  a truncated command.
- At startup, the project label, the receipt session ID, the absolute CLI path and a
  sourced-record instruction are given: after meaningful work, the result or lasting
  learning is first written to a vault note with `note-create`, then that note is
  cited with `receipt --ref`. The absolute CLI path is written once; subcommands start
  with it so that long paths do not consume the budget. The Companion, Last-Session,
  old receipts or the body of a personal note are not carried automatically into the
  external project. When needed, the agent calls `context` with an explicit project
  filter. A behavior deliberately narrower than the temporary wrapper in the issue was
  chosen at this point.
- The exception is the optional `preferences --project-context on` setting: when on,
  the newest receipt summary and date of the same project and the tasks whose date has
  arrived are added as a short block, and only a count comes from other projects. The
  gates and limits are in
  [the preferences document](PREFERENCES.md#project-aware-session-start).
- A local `auto_sync: false` / manual profile silences the bridge; `context_mode: off`
  silences the startup text. The global options do not change the local preferences
  file. The existing check interval is kept.
- The vault, its subfolders and other vaults that have their own `.beyin-runtime.json`
  file are skipped. Real paths are resolved; scope cannot be escaped through a
  symlink. If you attached a custom local hook without a separate vault installation,
  do not also attach the global bridge to the same project.
- Cwd precedence: the payload, `CLAUDE_PROJECT_DIR` for Claude, the process working
  directory (for Antigravity only the first `workspacePaths` entry).
  An invalid/disallowed cwd and a missing session ID create no record.
- In OpenCode, the cwd comes from the session directory (2.x `session.location.directory`,
  1.x `session.directory`; if the session cannot be read, the folder the plugin was
  loaded from, 2.x `ctx.location.directory`, 1.x factory `directory`); it does not
  fall back to the server process directory. If the folder is unknown, the plugin
  sends no event, and the bridge also does not record an OpenCode event without a
  cwd. The global plugin is loaded in every folder but the bridge returns `{}` outside
  the vault and project roots; vault sessions are recorded once by the local plugin.
- The queue stores only the event/harness/session hash, a bounded project label, the
  hash of the project path and the time. The full cwd, prompt and transcript are not
  stored. Folders with the same name are separated by hash. The project label is
  local metadata; do not use a folder name that contains a secret. `no_memory: true`
  and the internal job marker create no record.
- No Jev call, API key or new daemon is needed. The global startup does not start an
  automatic update check either. The existing local worker synchronization is used.

## Sourced record and verification

When the work is done, the agent creates a result source in the vault within its
current authority; it sends a receipt in the format below with the `session` the hook
provided:

```json
{"event_id":"unique-work-result","summary":"Result documented in the source.",
 "refs":["notes/project-result.md"],"session":"SESSION_HASH_FROM_HOOK"}
```

```sh
python3 "/absolute/path/to/MyBrain/beyin.py" receipt --harness claude --file receipt.json --json
python3 "/absolute/path/to/MyBrain/beyin.py" doctor --json
```

`refs` go to existing vault-relative sources. If there is no source yet, first write a
note with `note-create` (stdin JSON: `{"source": "knowledge/concepts/NAME.md", "text": "..."}`);
for a new concept, add the `knowledge/index.md` line with `note-read` / `note-edit`.
Do not copy external repo files or conversations merely because a hook ran.

The Stop reminder follows the same rule as a session inside the vault
([preferences document](PREFERENCES.md#receipt-reminder-at-stop)): in a session that
has an edit marker and no receipt written with the same `session` value after the
edits, the bridge blocks Stop once per session. The reminder gives the absolute CLI
path once and asks for the `note-create` step first, then `receipt --ref`; if the work
left nothing lasting, it is enough for the agent to say so in one sentence. If the
receipt declares a learning but no note was written under `knowledge/`, the same
one-time knowledge reminder comes. A read-only session, a second Stop carrying
`stop_hook_active`, a manual profile, `no_memory: true` and
`BEYIN_V3_NO_RECEIPT_REMINDER=1` are not blocked. In another project the same raw
session ID cannot see this marker. Because `UserPromptSubmit` is not received, the
`[kaydetme]` prompt marker is not read in the bridge. A checkpoint only shows that the
event was seen; it is not a work result or task completion. The `receipt-gaps.json.checkpoints`
field in `doctor --json` contains the project label and `project_id`. Because prompt
events are not received, complete receipt coverage of every turn is not claimed. If
the agent closes without writing a record, the worker does not invent a summary.

The vault's own Antigravity hook (`.agents/hooks.json`) also takes the project label
from the first `workspacePaths` entry by the same rule. In 3.9.0 and earlier,
Antigravity sessions inside the vault were labeled with the hook folder's name
(`.agents`). Because the session ID does not change, an ongoing session is not split;
the label and the `project_id` value are updated on the first new event, and old rows
that send no new event stay as `.agents`. A vault session whose first workspace is a
project outside the vault carries that project's `project_id` (this is also true for
the payload `cwd` field in Claude and Codex); with `--project-context on`, this
session's receipt summary can appear at the start of that project's session.

The isolated tests cover three harnesses, scope/double-trigger protections, project
origin, idempotence, the old checkpoint table migration, gap closure with a receipt,
and the execution, in an external cwd, of a command generated from a real installed
ZIP. Personal global settings are not changed in the tests. Additionally verify, by
opening a new session in a real client and using `doctor`, that the event was seen.

## Shutdown and rollback

To remove the bridge you can run the `--uninstall` command directly:

```sh
# Clean up the Antigravity bridge and the GEMINI.md marker:
py -3 beyin.py bridge --harness antigravity --uninstall

# For Claude Code:
python3 beyin.py bridge --harness claude --uninstall

# For Codex:
python3 beyin.py bridge --harness codex --uninstall
```

Automatic removal (`--uninstall`):
- Finds the relevant global settings file (`hooks.json` or `settings.json`) and deletes only the hook definitions related to `beyin_v3_bridge`; keeps all other user settings and custom hooks.
- Takes a `.bak` backup of the existing file before the change.
- For Antigravity, safely cleans the bridge block (`<!-- beyin-v3-bridge:start --> ... <!-- beyin-v3-bridge:end -->`) in `~/.gemini/config/GEMINI.md`; if the file contains no other text, it deletes the file too.
- For OpenCode, deletes first `~/.config/opencode/beyin-v3-bridge.json`, then `~/.config/opencode/plugins/beyin-v3-bridge.js`. Does not touch a file that does not carry the managed marker; user-owned global plugins are kept. Even if the running service keeps the old module in memory, it does not call the bridge without the settings file.

For manual removal, remove only the added bridge handlers from the global settings
and open a new session; keep the other handlers. For temporary silencing, the manual
profile can be used; it also stops the local automatic jobs.

An update refreshes the wrapper along with the other managed runtime files; global
settings stay user-owned. For this reason edit observation (`PostToolUse`) is not
added by itself to a previously installed bridge: after the update, rerun the same
`bridge --install` command. Because the command line does not change, if you go back
to an old version with the settings that contain this handler, the old bridge answers
the `PostToolUse` event with `{}`; the old `--uninstall` also removes the bridge
handlers in all events. **Before** you roll back or uninstall to an old version that
does not include the bridge, **remove the global handlers** (`--uninstall`). Leaving a
nonexistent script in a global hook produces a client error. When re-enabling,
generate the current JSON and complete the required trust review.
