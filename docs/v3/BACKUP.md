# Back up your vault

The source of truth for your notes, tasks, rules and receipts is the files in the
vault folder. A second folder on the same disk is not a backup against disk
failure. Keep at least one copy on a separate device or in a private repository
you trust, and keep a few older versions too. Syncing can also sync an
accidental deletion.

## Without Git: a dated folder or ZIP

1. Wait until the agents and your note editor have finished writing to the vault.
2. In your file manager, copy the vault folder to another disk or create a dated
   ZIP (e.g. `Beyin-2026-11-15.zip`). Check that hidden files are copied too.
   Do not overwrite the previous good copy.
3. `.beyin-note-write/` holds temporary write requests, locks and operation
   backups; do not include it in a portable note backup of a finished vault. Do
   not delete this directory while an operation is running, and do not treat the
   backup as complete while one is.
4. Do not sync the local state directory outside the vault between live
   machines. Besides the SQLite index, it also holds local queues, settings and
   client-specific information. If you need it for a full recovery, take **a
   separate, private copy** while all writers are stopped; do not delete the
   state as unnecessary. On a new machine, setup and `sync` re-index the source
   notes, but they do not recreate every local setting or operation.
   [Files that move or stay local](MULTI-MACHINE.md).
5. Extract the copy into a separate folder and verify it by reading a few notes,
   the companion archive and an attachment. Merely creating a backup does not
   prove it can be restored.

If you use a cloud folder, check the account's access and version-history
settings. `visibility: private` limits what a note contributes to context; it
does not prevent the note from being transferred to the cloud or to Git. The
backup contains the same private information.

## Private Git repository: with version history

If you do not know Git, the first path is enough. If you choose the Git path:

1. Create a **private** repository with your Git provider. Make the account,
   sharing and upload decisions yourself; do not push your real notes to a
   public repository.
2. If the vault has no Git, run `git init`. First review the
   [recommended `.gitignore`](MULTI-MACHINE.md#recommended-gitignore) rules; keep
   machine-specific setup and state files out of the sync.
3. Inspect the files with `git status --short`. Select only the files and folders
   you want to back up with `git add -- FILE_OR_FOLDER`; review the content with
   `git diff --cached --stat` and, if needed, `git diff --cached`. Do not add
   private tokens, keys or files that must not be shared.
4. Run `git commit -m "Vault backup"`. Add the remote address the new repository
   gave you with `git remote add origin PRIVATE_REPO_URL`. If `origin` already
   exists, first check that it is the right target; do not overwrite it.
5. See the branch name with `git branch --show-current`, then push that branch
   with `git push -u origin BRANCH_NAME`. Verify that the files and the latest
   commit are on the remote. Repeat the commit/push steps for later changes;
   they do not happen on their own.
6. Try a restore by cloning into a separate folder and opening sample notes. On a
   new machine, install Beyin separately; do not copy machine-specific setup
   files from the old machine. [Multi-machine guide](MULTI-MACHINE.md).

## What does doctor know?

`python beyin.py doctor --human` gives only information about the backup.
`backup.remote_configured` in the JSON says that the local Git configuration has
a non-empty remote address. That address may also point to a local folder;
reachability, last push, tracked files or recoverability are **not verified**.
For this reason `backup_verified` stays `false`. The remote address and
credentials are not put in the output; no network connection, push or file write
is made.

If Git is missing, there is no remote address or the check cannot be made, the
result is `unknown` or `unavailable`. This is not a claim that you have no
backup: a backup you made with other tools is not visible here. Overall health
status does not change, and no warning is added to session start. This first
version has no mute setting, no automatic backup and no `backup` command.
