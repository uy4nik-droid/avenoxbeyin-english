# Avenox Second Brain V3: agent install guide

This file is the canonical install recipe for carrying out the following user request:

> Set up my second brain in this folder. If there is an existing installation, update it
> and keep my notes. Do the necessary download and setup steps yourself. At the end,
> let's verify it together by saving a sample piece of information and reading it back
> in a new session.

The user does not have to download a ZIP, unpack an archive or look for an install
command. The agent does these. Only the client's normal folder, workspace or hook trust
review belongs to the user.

## Non-negotiable rules

1. The install target is the current vault/workspace folder in which the user made this request.
2. Do not delete, move, rename or overwrite user notes, and do not clobber them with `git reset`.
3. First detect any existing V1, V2 or V3 installation. The official installer and the
   official updater apply the backup, conflict and rollback rules; do not skip these
   checks by hand.
4. Use only the latest stable GitHub release package of the `uy4nik-droid/avenoxbeyin-english`
   repository. Do not use Source code archives or third-party packages.
5. Do not spill raw notes, credentials, private paths or secret values into terminal
   output, into the chat or to external services.
6. Do not claim success before the installation is complete. Check the installer or
   updater exit code, the version stamp and the result of `beyin.py doctor`. Also read
   the `companion` and `skills.conflicts` fields in the installer output; if you see
   `needs_attention`, do not complete the related step without asking the user.

## 1. Find the target and Python

- The vault path is the current workspace root. Use the absolute, canonical path.
- Look for Python 3.11 or newer:
  - macOS/Linux: `python3` first, then `python`
  - Windows: `py -3` first, then `python`
- Actually run the interpreter you found and check its version.
- If there is no suitable Python, treat the user's install request as authorization and
  install a stable Python 3 release with the operating system's official package manager.
  If administrator permission or an operating-system confirmation is required, ask the
  user for approval, briefly and clearly, only at that point. Do not use random download
  sites.

Obsidian is for opening notes; no Obsidian plugin is needed during installation. Git,
pip, Node, Mem0, an API key or an always-running server are not needed.

## 2. Download the official package to a temporary location and verify it

First find out the tag of the latest stable release. The first way is the GitHub API:

`https://api.github.com/repos/uy4nik-droid/avenoxbeyin-english/releases/latest`

Use the `tag_name` field in the response; `draft` and `prerelease` must be false. For
unauthenticated requests the API applies an hourly limit per IP. If it returns HTTP 403
or 429, do not push the API and do not guess the version; as the second way, read the
redirect of this address:

`https://github.com/uy4nik-droid/avenoxbeyin-english/releases/latest`

This address redirects to `https://github.com/uy4nik-droid/avenoxbeyin-english/releases/tag/vX.Y.Z`;
the tag is the last path segment.

The release must carry a stable `vMAJOR.MINOR.PATCH` tag. If the tag is `vX.Y.Z`, the
required assets are:

- `beyin-v3-X.Y.Z.zip`
- `beyin-v3-X.Y.Z.zip.sha256`

Do not pin the version, and do not mistake the `X.Y.Z` placeholder in these lines for a
real version: derive the names from the real tag. The download addresses are the
`browser_download_url` fields in the API response; if you used the redirect path, the
same addresses follow this pattern:

`https://github.com/uy4nik-droid/avenoxbeyin-english/releases/download/vX.Y.Z/beyin-v3-X.Y.Z.zip`
`https://github.com/uy4nik-droid/avenoxbeyin-english/releases/download/vX.Y.Z/beyin-v3-X.Y.Z.zip.sha256`

Download both over HTTPS into the operating system's temporary folder. Compare the first
field in the SHA-256 file with the local SHA-256 of the ZIP. If they do not match, stop,
do not unpack the archive and report the problem.

When unpacking the ZIP into a temporary folder, check that the destination of every
member stays inside this temporary folder. Reject an archive that contains an absolute
path, an escape with `..` or a symbolic link. The package root must contain
`manifest.json` and `scripts/install_v3.py`.

## 3. Apply the installation or update

First look at the `.beyin-version` file in the vault root and branch according to it.

### 3a. If `.beyin-version` is missing, or V1 or V2 exists: the official installer

With the same Python interpreter you found:

```text
<python> <temp-package>/scripts/install_v3.py --vault <absolute-vault-path>
```

For an old V1/V2 installation, first run the same command with `--plan` appended; this
changes nothing and shows what would be written and what would be retired. If the user
has modified an old runner by hand, the installer returns exit code 1 with the message
`Customized legacy runner requires review <path>`. Do not delete or overwrite that file;
summarize its contents briefly, get the user's explicit approval, and only then use
`--accept-customized-legacy <vault-relative-path>` for that single file. There is no
bulk migration. Details:
`https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/MIGRATION.md`

### 3b. If `.beyin-version` already starts with `3.`: the installed updater

For an existing V3 installation, the preferred way is the `beyin.py` updater inside the
vault. In the vault root, run it with the ZIP you downloaded and verified:

```text
<python> beyin.py update --check --package <downloaded-zip>
<python> beyin.py update --package <downloaded-zip>
```

If the result is `updated`, the version has changed; if it is `noop`, the vault is
already up to date; both are success. This way does not needlessly force a new client
trust review, and if necessary it can be fully rolled back with
`<python> beyin.py rollback`. It also works without `--package` when there is network
access; a network error (for example `http_403`) does not mean "up to date". If the
`update` command is not recognized in a very old V3 package, fall back to path 3a. The
output of `beyin.py --help` does not list the `update`, `rollback` and `recover`
commands; they are handled separately in the entry script and they work. Do not fall
back to 3a just because you did not see the command in the `--help` list.

### Applies to both paths

If the vault has `.beyin-runtime.json`, the installer and updater preserve its external
local state location. On a new installation, state is written outside the vault, to the
appropriate local application-data directory for macOS, Linux or Windows. Do not move
the state into iCloud, OneDrive, Dropbox or the vault.

If a managed file has been modified by hand, both paths fail with the error
`Reinstall conflict: managed file changed <path>` and return exit code 1. Do not
overwrite the user's file. Report the conflicting file and why it cannot continue
automatically, briefly. For an interrupted official V3 operation, first use the
`beyin.py recover` path in the existing vault; do not re-copy before it has failed. Do
not update an installed vault with your own chain of curl, copy or `git pull`.

## 4. Verify the installation

Run these checks in the vault root:

```text
<python> beyin.py doctor --human
<python> beyin.py preferences --human
```

In addition, check that these files exist: `.beyin-version`,
`.agents/skills/beyin/SKILL.md`, `.agents/skills/beyin-doktor/SKILL.md`,
`.agents/skills/beyin-guncelle/SKILL.md` and `.agents/skills/beyin-kontrol/SKILL.md`.
After installation, delete the temporary ZIP and the unpack folder; do not touch user
notes. The installation adds a managed section marked `<!-- beyin-v3:start -->` to the
`AGENTS.md` file in the vault root; existing content is preserved. If `CLAUDE.md` does
not exist, it is created with only the `@AGENTS.md` import line. The section is not added
a second time to a `CLAUDE.md` that already imports `AGENTS.md`; the same section is added
to a `CLAUDE.md` that does not import it. In the summary you give the user, say what was
added.
If you are using a package that includes Kiro support, also check the files
`.kiro/hooks/beyin-v3.json` and `.kiro/skills/beyin/SKILL.md`; these files may be absent
in older packages.

The installation leaves only the update shortcut of the relevant platform in the vault
root: on macOS `Beyni Güncelle.command`, on Windows `Beyni Guncelle.cmd`, on Linux
`Beyni Güncelle.sh` and the `Beyni Güncelle.desktop` that calls it. All of them call the
installed `beyin.py update` command and contain no separate update logic. In the future
the user can update by telling the agent "update my brain" or with this shortcut.

Show the user the `/hooks` review in Codex, and the normal workspace/folder trust in
Claude Code and Antigravity. Do not make up a trust hash or bypass the approval. There is
no extra trust step for OpenCode; the plugin loads when OpenCode is opened in the vault
folder. There is no extra trust step for OMP either; the `.omp/hooks/pre/beyin-v3.ts`
hook loads when OMP is opened in the vault folder. If Hermes Agent is used, the installer
writes the plugin files into the vault, but for the connection, the steps
`hermes plugins enable beyin-v3` and a restart belong to the user; the steps are in
`https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/HERMES.md`.
If Kiro IDE 1.x or the V3 CLI is used, open the vault, review the Beyin definitions in
the Agent Hooks panel or on the CLI `/hooks` screen, and start a new session.
If Pi is used, open Pi in the vault folder, show the user the `.pi/extensions/beyin-v3.ts`
file, leave Pi's project trust question to the user and start a new session; do not
write to the `~/.pi/agent/trust.json` file by hand. In projects outside the vault, Pi
connects only with an explicit `--beyin-project-root` scope (`docs/v3/PI.md`).
Then ask for a new client session to be opened. If the Codex Desktop automatic hook
context does not appear, this is not a claim of installation success; direct refresh with
the installed `beyin.py context` and `sync` commands can be used.

## 5. Get to know the user and do a real read-back

After installation, read the `.agents/skills/beyin/SKILL.md` file. Ask the user at most
three short getting-to-know-you questions. Save the answers to a source Markdown note:
identity and form-of-address information is written to the `Core.md` file in the
companion folder. Only the official installer creates this folder. On path 3b (updating
from an older V3) the folder is not created immediately; it is also not created when the
`companion` field in the installer output returns `needs_attention`. In both cases, do
not open a new identity folder: look for an existing `Core.md` or `Soul.md` in the vault,
and if there is more than one candidate, ask the user which one to use. New semantic
notes, on the other hand, are created only under `notes/` or `knowledge/` with
`<python> beyin.py note-create --file NOTE_JSON`; if the folder does not exist, it is
created. Then sync with `<python> beyin.py sync`, and in a separate command read the same
information back with `<python> beyin.py context "<the topic you are looking for>"` and
tell the user the `source` path it returns. Opening and reading the file directly does
not count as a read-back. Do not write made-up profile information.

Finally, ask the user to open a new session and ask about the saved sample information.
Do not say "memory across sessions is verified" until this new-session read-back has been
done.

The default consumption profile is Normal. If the user wishes, via the beyin skill they
can say "switch to economy mode", "set the check interval to 30 minutes" or "turn off
automatic checks". Local checks do not call a model, and no timer that wakes a closed
application is installed.

## Optional Jev advisor

Jev is not part of the installation and is off by default. After installation, the output
of `<python> beyin.py jev status --human` should show "Jev: off" and "Key: not set";
do nothing else. Do not turn it on, ask for an API key or bring up the subject
unless the user explicitly asks.

If the user asks, apply the Jev section in the installed `.agents/skills/beyin/SKILL.md`
and the steps in
`https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/JEV.md`
(the installed package has no `docs/` folder). The key lives in the `TYPESAFE_API_KEY`
environment variable; it is not written to Markdown, to version control or to a command
argument. The `jev` command does not accept or print the key. If `env_file` is going to be
used, an absolute path is required. Per rule 5, do not ask for the key in the chat and do
not print it into the chat; the user puts it into their own shell environment themselves.
Measure first with `jev shadow`, then do `jev on`. While `jev on` is active, the agent's
`context ... --jev`, `jev-answer` and `jev-review` calls also send data to the provider:
`context --jev` sends the query and, for every allowed candidate, the title and an excerpt
of the text. `auto_context` is a separate and additional opt-in: when
`jev on --enable auto_context` is turned on, on every turn the prompt text and, for up to
8 candidate notes, the title and the first 600 characters go to the provider. `private`
notes are not sent by any path; from V3.2.0 onward, records with `remote_allowed: false`
and `sensitivity: sensitive` are not sent either. Tell the user these things before
turning them on. When the mode is not `off` and there is no key, the command warns and the
calls fall back to the local result. To turn it off: `<python> beyin.py jev off`; in an
emergency, the `BEYIN_JEV_DISABLE=1` environment variable stops the calls without changing
the saved mode.

Local option that needs no key: if the user explicitly asks, for a separately installed
`laya-serve` (`LAYA_HOST=127.0.0.1 LAYA_PORT=8765`) run
`<python> beyin.py jev shadow --provider laya`, then `jev status --check`. Do not install
Laya, PyTorch or model weights into Beyin's environment. Laya runs only in shadow mode:
because it measured much weaker than Jev, its scores are recorded for measurement only
and change no result; `jev on --provider laya` is rejected with `laya_shadow_only`, and
`jev status` shows the mode as `shadow (only)`. The same sending rules
apply; `private`, `remote_allowed: false` and `sensitivity: sensitive` records do not go
to Laya either. Returning to Jev: `jev on --provider typesafe`.

## Manual fallback

If the agent's network or file permission is genuinely insufficient, direct the user to
this page:

`https://avenox.lol/ikincibeyin`

The V3 ZIP button on the page leads to the latest stable official release package on
GitHub and to the SHA-256 file; the same packages are also available directly on the
`https://github.com/uy4nik-droid/avenoxbeyin-english/releases/latest` page. After a manual
installation, verify that the version is current with `<python> beyin.py update --check`
in the vault root. This path is the last resort that takes the place of automatic
installation; it is not the first choice.
