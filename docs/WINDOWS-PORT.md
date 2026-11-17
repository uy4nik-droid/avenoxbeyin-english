# Native Windows port: what changed, and why

This document explains why the `SETUP-WINDOWS.md` path exists and where it
diverges from upstream. Every item rests on a measured observation; the things
that were not measured are listed separately at the end.

## The one-line `beyin.md` entry now picks the right lane

Having a native Windows engine was not enough on its own. The public entry file,
`docs/beyin-v2.md`, went straight into `/tmp`, Bash and the `SETUP.md` flow
without telling platforms apart, so the single line the from-scratch viewer
copied might never reach the Windows installer.

Before writing anything to the target vault, the entry gate now picks one of three lanes:

| Environment | Path chosen | Limit |
| --- | --- | --- |
| macOS / Linux | Existing `SETUP.md` | The macOS flow was not changed |
| Native Windows | Fresh temp clone -> `SETUP-WINDOWS.md` -> `install.ps1` | Clean install only |
| WSL | `SETUP.md`, entirely inside the same WSL distribution | Vault on the Linux filesystem; a mixed Windows Obsidian runtime is not verified |

This split is pinned at the repo level by `tests/entrypoint_test.py`. The working
behavior of the native Windows installer is measured separately by the preflight,
clean-install and engine tests in Windows CI.

## Why there is a separate path

Upstream's own README marks Windows as a gap:

> | Windows | **not tested**, WSL recommended | The Linux path is valid inside WSL. There is no install path for native Windows. |

`docs/SPEC-V2.md` lists portability as a goal: *"Portable. macOS + Linux
for all shell code. Windows: documented as WSL-recommended, not silently
broken."* This port fills that gap; it does not change the WSL path.

**macOS and Linux behavior is unchanged.** The POSIX hook configuration stays in
`template/.claude/settings.json`; the Windows installer replaces it only in the
vault it installs, using `scripts/settings.windows.json`. The same pattern
applies to the diagnostic skill: the POSIX `beyin-doktor` stays in the template,
and the installer replaces it in the vault it installs with
`scripts/skill.beyin-doktor.windows.md`. `upgrade.sh`, for its part, copies the
new shared lock module `_portalock.py` together with the two engine scripts.

## Do not run `scripts/upgrade.sh` on Windows

`upgrade.sh` is a POSIX upgrader and manages the existing `.sh` hook names.
There is not yet a path that safely recognizes and converts a vault with
PowerShell hooks; automatically trying the wrong path could wire the same event
twice. For that reason native Windows support is for clean installs only for now;
upgrading an existing vault is explicitly out of scope.

## Layers that break

| Layer | Upstream (POSIX) | On Windows | Counterpart in this repo |
|---|---|---|---|
| File locking | `fcntl.flock` | no such module, dies on import | `_portalock.py` (`msvcrt.locking`) |
| Detached process | `start_new_session=True` | ignored | `DETACHED_PROCESS \| CREATE_NEW_PROCESS_GROUP` |
| Hooks | `hooks/*.sh` (bash) | no bash | `hooks/*.ps1` + `pwsh.exe` |
| Hook registration | `"$CLAUDE_PROJECT_DIR/.../x.sh"` | `.ps1` does not run directly | shell-less `pwsh.exe` + `args` exec-form |
| Output encoding | UTF-8 | OEM code page | `lib.ps1` pins it to UTF-8 |
| Line endings | LF | Git converts to CRLF | `.gitattributes` pins LF |
| Symlink test | works | `WinError 1314` | explicitly skipped with `skipUnless` |
| Diagnostic skill | `beyin-doktor` looks for `.sh`, symlinks and `command -v python3` | none of the three exist, permanent red in a healthy vault | `scripts/skill.beyin-doktor.windows.md` (the installer swaps it in) |

## Three measured Windows traps

**1. `[Console]::OutputEncoding` is the OEM code page.** On a Turkish machine
that is cp857. This system produces Turkish context from start to finish, and the
memory folder's name contains an emoji. Measurement: under cp857, "Türkçe"
turns into bytes that are not valid UTF-8, and 🔮 becomes a plain `?` with no way
back. `lib.ps1` pins this in **one place**; setting it per hook is how a hook gets
forgotten.

**2. `WindowsApps\python3.exe` exists even when Python is not installed.** It is
a shortcut that opens the Microsoft Store. `Get-Command` finds it, and running it
does nothing. A hook that only checks for existence takes it for Python, says it
"started" the engine, and the summarizer never runs. That is why both `lib.ps1`
and `install.ps1` verify Python by **running** it, and use `Get-Command -All`,
because the stub can sit in front of the real installation.

**3. PowerShell 5.1 strips embedded double quotes.** When passing arguments to
native commands, `print("X")` reaches Python as `print(X)` and raises a
`NameError`. Measurement: a probe containing quotes made the gate say "no Python"
on a machine that had Python. The probes now contain no quotes at all.

## Why `install.ps1` does not carry `#requires -Version 7.0`

If it did, the user the gate is aimed at, someone without pwsh 7, would see a bare
PowerShell version error instead of our message. The preflight is written in a
5.1-compatible subset; once the gate is passed, the script relaunches itself
under `pwsh`.

The gate verifies all four dependencies (pwsh 7, Python 3, git, claude) by
**running** them, and if even one is missing it stops **without writing anything
to disk**. This matches upstream's own rule: *"an honest v1 beats a half-installed v2."*

## The hooks are a translation, not a copy

The PowerShell hooks were translated from bash line by line. Each function names
the `.sh` line it corresponds to in its comment. The session key is
**byte-identical** to bash's (the SHA-256 of the UTF-8 `session_id`, lowercase
hex), the state file names and the flat layout are the same, the counter lock is
still `mkdir`-based, and the 16,000-character context budget and the order of
progressive truncation are the same.

Three deliberate differences: the UTF-8 pinning above, verifying Python by running
it, and writing a failed flush persistently to `flush_last_error` (upstream's
`python3-missing` marker and warning are kept as well).

One platform difference: `lib.sh` shells out to `python3` for SHA-256 and JSON
escaping; in PowerShell both are native, so **the hook layer needs no Python at
all.** Python is needed only for the engine.

## Verification

```
python tests/scripts_test_windows.py     Ran 25 tests, OK (skipped=1)
pwsh -File tests/Test-Preflight.ps1      TAMAM: 6 test gecti
pwsh -File tests/Test-CleanInstall.ps1   TAMAM: 18 kontrol gecti
```

`Test-CleanInstall.ps1` installs a vault from scratch, drives the real
`SessionEnd` hook with a real payload, and expects the detached engine to write
under `daily/`. The only thing stubbed is `claude`; the installation, the hooks,
the detaching and the engine are real.

## What we do not claim

- **This port was not tested on a physical viewer's Windows machine.** It was
  measured with CI and contributor verification on Windows 11 + PowerShell 7 +
  Python 3, and it is not official Microsoft/Anthropic support.
- **The symlink security test cannot be set up on Windows.** Because the attack
  cannot be staged (`WinError 1314`), it is skipped with `skipUnless`; on that
  surface we do not have upstream's assurance. Note: the junction and hardlink
  variants were measured and `compile.py` rejects both (`staging-escape`,
  `staging-special`), so the defense is not single-layered.
- **`MAX_PATH` was not measured on a stock machine.** Long path support is off by
  default on Windows. The longest path in a real measured vault was 131
  characters, well within the 260 limit; `install.ps1` still warns if the vault
  path is deep.
- **`upgrade.sh` line numbers** belong to the upstream version of that day.
