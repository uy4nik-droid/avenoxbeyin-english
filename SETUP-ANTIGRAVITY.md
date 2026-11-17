# Installing Avenox Beyin v2.3 with Antigravity

Apply this file inside Google Antigravity, at the root of the cloned `avenoxbeyin` repo.
The main setup contract is in `SETUP.md`; read it from start to finish and apply it as
written, using only the Antigravity differences below.

## Binding differences

1. Run the setup in English and do not change the interview, reversibility, placeholder and
   verification rules in `SETUP.md`.
2. In the prerequisites, look for `agy` instead of `claude`. Do not write to disk until
   `python3 -V` and `agy --version` have actually finished with zero. Do not ask for an
   API key; use the user's existing Antigravity session.
3. On native Windows, do not run the Bash path. Follow the native Windows flow in
   `SETUP-WINDOWS.md` and call the installer with `-Harness Antigravity`.
4. On macOS, Linux or WSL, apply the `SETUP.md` MODE A flow. In PHASE 2 both
   `render_codex_hooks.py` and `render_antigravity_hooks.py` must run.
5. For an existing v1, v2.0, v2.1 or v2.2 vault on macOS, Linux or WSL, use the
   `scripts/upgrade.sh` v2.3 upgrade. On native Windows, upgrading an existing vault is
   still unsupported; a from-scratch `install.ps1 -Harness Antigravity` installation is
   supported.
6. In the final report, verify the `avenox-beyin` entry in `.agents/hooks.json`, the
   absolute commands and the value `.beyin-version = 2.3.0`.

## Behavior limit

The Antigravity `PreInvocation` event adds the memory context as a temporary system
message on the first model call. `Stop` is every completed execution loop, not an exit
from the application. For this reason the adapter processes only the last user-assistant
exchange, keeps one digest per conversation and does not write the same turn to the daily
log a second time. Summarizing and compiling use the current `agy -p` session; there is no
direct Gemini API key or second copy of the engine.

After installation, open Antigravity directly at the vault root. After the first real
conversation, expect `daily/YYYY-MM-DD.md` to be created; if it is not, run
`beyin doktor` and report the last engine error in the `.claude/scripts/.state/health.json`
file.
