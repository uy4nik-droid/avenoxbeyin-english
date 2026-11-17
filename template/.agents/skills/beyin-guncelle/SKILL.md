---
name: beyin-guncelle
description: Updates the Beyin installation to a new official release, checks the version, or rolls back a failed upgrade. Triggers - "update my brain", "is there a new version", "brain version", "rollback", "undo the update", "beynimi güncelle", "yeni sürüm var mı", "beyin sürümü", "güncellemeyi geri al", "/beyin-guncelle". Do not use for - fault diagnosis (beyin-doktor), taking notes (beyin).
---

# Update the brain

The only update tool is the `beyin.py` file in the vault root. Use `python3` on macOS/Linux and `py -3` on Windows. Do not update the user's vault with your own curl/copy/git-pull chain.

- If the user only asks about the version, run `python3 beyin.py update --check --metadata-only`; do not install anything.
- If the user wants the update, run `python3 beyin.py update`. This request is authorization for a routine local update; do not ask for permission a second time. The official stable release is the default; a preview or custom package is used only if the user chose it.
- If the user wants to go back, run `python3 beyin.py rollback`; then verify the result with `doctor`.
- For requests to silence or enable starter skills, adapters or launchers, run `python3 beyin.py preferences --exclude-component <name>` or `--include-component <name>` (the setting is written to the `.beyin-exclusions.json` file and applied on the next update or install). On update, excluded files that are unmodified are cleaned up; ones the user has modified are kept.

A no-op on the same version is success. Success is reported only from a read-back of the version and health. If there is a half-finished operation, a download error, a broken package or a local file conflict, keep the existing information; do not change the version stamp by hand. Do not force your way past a conflict or bulk-restore personal notes from a backup. If there is no new release or no access, do not say 'updated'.

The updater checks the package source, its integrity and the system files it may change. Notes, user skills and personal settings are not update text. If a new/changed hook definition requires a trust review, explain this in the way that fits the client; do not fabricate a trust record. State the required restart and the single user step, if any.

In the result message, state the previous→new version, the verification result and any step still open. Do not share tokens, local user paths, dumps of personal settings or raw logs.

Before V3.1, if `--metadata-only` is not recognized, fall back to the existing `update --check` command. The version notice is on by default and is a daily GitHub metadata check; it sends no notes. Apply a request to turn it off/on with `preferences --update-notifications off/on`. To silence a single release use `update --dismiss X.Y.Z`. A metadata-only result is not proof that the package can be installed.
