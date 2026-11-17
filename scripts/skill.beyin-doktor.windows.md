---
name: beyin-doktor
description: Health check for the brain. Reports hooks, scripts, memory files, daily logs, compile status and vault hygiene in a single table. Use when the user says "brain doctor", "doctor", "health check", "is the brain working", "is memory broken" (or in Turkish "beyin doktor", "doktor", "sağlık kontrolü", "beyin çalışıyor mu", "hafıza bozuk mu"), or when you suspect a memory mechanism is silently not working.
---

# Brain Doctor (Windows)

This skill audits the brain's mechanical layer: are the hooks firing, have the scripts run,
are the logs staying fresh, has the vault been polluted. The goal is to make silent failures visible.

**This vault is a native Windows install** (`SETUP-WINDOWS.md` + `scripts/install.ps1`). The engine
runs with `.ps1` hooks, not `.sh` hooks. The POSIX edition in the repo is for macOS and Linux;
do not run its commands here, they produce false reds. Differences:

| What the POSIX edition looks for | The reality on Windows |
| --- | --- |
| `.claude/hooks/*.sh` | `.claude\hooks\*.ps1` — `settings.json` calls them with `pwsh.exe` |
| execute permission (`chmod +x`) | Windows has no exec bit; the check is meaningless |
| `AGENTS.md`, `.agents/skills`, `.codex/hooks` symlinks | a Windows checkout does not preserve symlinks; `install.ps1` leaves **copies** |
| `command -v python3` | `python3.exe` is a Microsoft Store shortcut, not Python. The engine finds the real interpreter with `Get-BeyinPython` in `lib.ps1` |
| iCloud `* 2.md` conflict | OneDrive leaves `file (1).md` or `file-MACHINENAME.md` |

## How you work

1. Work in the vault root (the folder containing CLAUDE.md/AGENTS.md). All paths are relative; do not write absolute paths.
2. Run the checks below **in order with PowerShell 7 (`pwsh`)**. Use the commands exactly as
   written; do not guess. `pwsh` is a prerequisite of this install, so it is certainly present; Git Bash is not.
3. Do not try to squeeze multi-line blocks into a single line with `-Command`. Write the block to a temporary `.ps1`
   file and run it with `pwsh -NoProfile -ExecutionPolicy Bypass -File <file>`.
   Regexes containing backslashes break when passed inline, and the check then gives a false red.
4. Classify each check's output as 🟢 / 🟡 / 🔴.
5. Give the result in a single table and write one fix line for each 🔴.
6. At the very end, give a one-sentence verdict.

The checks are read-only. Do not fix anything on your own: report first, then fix if the user
asks.

## Checks

### 1. Are the hook files in place

```powershell
foreach ($h in 'session-start','prompt-counter','session-end','pre-compact') {
  $f = ".claude\hooks\$h.ps1"
  if (Test-Path $f) { "$h.ps1: ok" } else { "$h.ps1: FILE MISSING" }
}
```

🟢 all four `ok`. 🔴 missing.
Fix: copy the missing file from the repo (`template/.claude/hooks/`). Windows has no such thing as an
execute permission; do not look for `chmod`.

### 2. Are the hooks wired in settings.json

```powershell
$s = Get-Content .claude\settings.json -Raw
foreach ($h in 'session-start','prompt-counter','session-end','pre-compact') {
  if ($s -match [regex]::Escape("$h.ps1")) { "${h}: wired" } else { "${h}: NOT IN SETTINGS" }
}
```

🟢 all four wired. 🔴 if even one is missing, that hook never runs at all.
Fix: add the missing event to the `hooks` block in `.claude\settings.json` (SessionStart,
UserPromptSubmit, SessionEnd, PreCompact). The correct template is `scripts/settings.windows.json`;
the `command` field is `pwsh.exe` and the script path is given in `args` with `-File`. Then restart
Claude Code.

### 2b. Is pwsh.exe on the PATH

```powershell
$p = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if ($p) { "pwsh.exe: $($p.Source)" } else { "pwsh.exe: NOT ON PATH" }
```

A Windows-specific, silent failure: `settings.json` calls the hooks **by the bare name `pwsh.exe`**.
If it drops off the PATH, all four hooks fail without a sound and memory is not written.
🟢 found. 🔴 missing.
Fix: `winget install --id Microsoft.PowerShell --source winget`, or add the existing install's
folder back to the PATH. Then restart Claude Code.

### 3. Does every hook have the recursion guard

```powershell
Get-ChildItem .claude\hooks\*.ps1 | ForEach-Object {
  if (Select-String -LiteralPath $_.FullName -Pattern 'BEYIN_INVOKED_BY' -Quiet) {
    "$($_.Name): guard present"
  } else { "$($_.Name): NO GUARD" }
}
```

🟢 present in all (including `lib.ps1`). 🔴 missing. A hook without the guard fires again inside the
background `claude -p` call, which risks an infinite loop.
Fix: add `if ($env:BEYIN_INVOKED_BY) { exit 0 }` at the top of the file.

### 3b. Codex router, skill and hook links

Because a Windows checkout does not preserve symlinks, `install.ps1` leaves copies. The right question is not
"is it a symlink" but "is the copy current, and does `hooks.json` read an absolute path".

```powershell
if ((Get-FileHash AGENTS.md).Hash -eq (Get-FileHash CLAUDE.md).Hash) {
  'router: same content'
} else { 'router: SEPARATE/STALE' }
if (Test-Path .agents\skills\beyin-doktor\SKILL.md) { 'skills: copy in place' } else { 'skills: MISSING' }
$w = [ordered]@{ SessionStart='session-start.ps1'; UserPromptSubmit='prompt-counter.ps1'; PreCompact='pre-compact.ps1'; SessionEnd='session-end.ps1' }
$t = @{ SessionStart=15; UserPromptSubmit=5; PreCompact=10; SessionEnd=3 }
try {
  $d = Get-Content .codex\hooks.json -Raw | ConvertFrom-Json
  $ok = $true
  foreach ($e in $w.Keys) {
    $n = @(foreach ($m in @($d.hooks.$e)) { foreach ($h in @($m.hooks)) {
      if ($h.command -like "*$($w[$e])*" -and $h.command -match '[A-Za-z]:\\' -and $h.timeout -eq $t[$e]) { 1 }
    } }).Count
    if ($n -ne 1) { $ok = $false; "  $e count: $n (expected 1)" }
  }
  if ($ok) { 'codex: ok' } else { 'codex: BROKEN' }
} catch { 'codex: BROKEN/MISSING' }
```

🟢 all three lines same/in place/ok. 🟡 `router: SEPARATE/STALE`: `CLAUDE.md` was changed by hand after the install
and the copy has fallen behind. 🔴 `codex: BROKEN`: Codex is reading a relative or stale command.
Fix: for the router, `Copy-Item CLAUDE.md AGENTS.md -Force`. For the hooks,
`python .claude\scripts\render_codex_hooks.py --vault "$PWD" --platform windows`, then approve the
changed project hooks in Codex's `/hooks` screen. Do not write the trust hash by hand.

### 3c. Antigravity hook adapter

```powershell
try {
  $a = (Get-Content .agents\hooks.json -Raw | ConvertFrom-Json).'avenox-beyin'
  if (@($a.PreInvocation).Count -eq 1 -and @($a.Stop).Count -eq 1) { 'antigravity: ok' }
  else { 'antigravity: BROKEN' }
} catch { 'antigravity: BROKEN/MISSING' }
```

🟢 `ok`. 🔴 means Antigravity is not injecting memory or not carrying the last turn into the daily log.
Fix: `python .claude\scripts\render_antigravity_hooks.py --vault "$PWD" --platform windows`.

### 4. Python and the model CLI

**Do not use** `command -v python3`. On Windows `python3.exe` sits under `WindowsApps` as a
Microsoft Store shortcut even when Python is not installed: it is found but does not work. Ask the
engine's own resolver; it verifies the interpreter by running it.

```powershell
. .\.claude\hooks\lib.ps1
$py = Get-BeyinPython
if ($py) { "python: $py" } else { 'python: MISSING' }
$cli = Get-Command claude -ErrorAction SilentlyContinue
if ($cli) { "claude: $($cli.Source)" }
else {
  $agy = Get-Command agy -ErrorAction SilentlyContinue
  if ($agy) { "agy: $($agy.Source)" } else { 'model CLI: MISSING' }
}
```

🟢 Python found and `claude` or `agy` present. 🔴 without Python the engine does not run at all; if both
model CLIs are missing, the background summarizer stops.
Fix: `winget install --id Python.Python.3.13 --source winget`; for the model CLI,
`winget install --id Anthropic.ClaudeCode --source winget`. After installing, restart Claude Code
so the PATH is refreshed.

### 4b. Is the model CLI logged in

Being present is not enough. The background summarizer and compiler run through `claude -p`; if the CLI
is installed but logged out, every flush gets `Not logged in` and dies, and **no daily log is created anywhere**.
Being logged in to the desktop app does not cover the CLI; the two have separate credential stores.
`auth status` does not spend tokens.

```powershell
$cli = Get-Command claude -ErrorAction SilentlyContinue
if (-not $cli) { 'claude: MISSING' }
else {
  $raw = & $cli.Source auth status 2>$null
  try {
    $j = $raw | ConvertFrom-Json
    if ($j.loggedIn) { "session: logged in (method: $($j.authMethod))" } else { 'session: LOGGED OUT' }
  } catch { 'session: UNREADABLE' }
}
```

🟢 `session: logged in`. 🔴 `session: LOGGED OUT` or `UNREADABLE`: the engine looks like it is running but
memory is not written; this is the sneakiest failure.
Fix: **the user must run** `claude auth login` in a terminal **themselves** (it opens OAuth in the
browser). You, as the agent, cannot do this step, and do not try. Once login is done, verify with
`claude auth status`, then open and close a session and repeat check 6.

### 5. python3-missing marker

```powershell
if (Test-Path .claude\scripts\.state\python3-missing) {
  "marker PRESENT, date: " + (Get-Content .claude\scripts\.state\python3-missing -TotalCount 1)
} else { 'no marker' }
```

🟢 no marker. 🔴 marker present: the hooks could not find a working Python.
Fix: turn check 4 green, then delete the file:
`Remove-Item .claude\scripts\.state\python3-missing`.

### 6. Daily log freshness

```powershell
$f = Get-ChildItem daily\*.md -ErrorAction SilentlyContinue |
     Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $f) { 'daily: no logs at all' }
else { "daily: $($f.Name), written $([int]((Get-Date) - $f.LastWriteTime).TotalHours) hours ago" }
```

🟢 newer than 48 hours. 🟡 between 48 and 96 hours, or the vault was set up today and no session has
ended yet. 🔴 older than 96 hours.
Fix: end the session and start again, then repeat this check. If it is still empty, go back to checks
1, 2, 2b and 4; the fault is in the flush chain.

### 7. Compile status

```powershell
$f = '.claude\scripts\.state\compile-state.json'
if (Test-Path $f) {
  "state: updated $([int]((Get-Date) - (Get-Item $f).LastWriteTime).TotalHours) hours ago"
  $d = Get-Content $f -Raw | ConvertFrom-Json
  "last_run: $($d.last_run)"
  "last_status: $($d.last_status)"
  "ingested: $(@($d.ingested.PSObject.Properties).Count) logs"
} else { 'compile: no state file, no compile has run yet' }
```

🟢 `last_run` newer than 48 hours and `last_status` is `ok`. 🟡 no state, but the vault was just set up or
it is not yet 18:00 in the evening. 🔴 `last_status` starts with `fail:` or is older than 48 hours.
Fix: run one round by hand and look at the error (use check 4 for `$py`):
`& $py .claude\scripts\compile.py --dry-run`, then `& $py .claude\scripts\compile.py`.

### 8. Recent errors in the health records

`health.json` holds one JSON record per line (JSONL). Not every record is a failure: if the
`error` field starts with `warn:`, the engine **resolved the problem itself** (for example
`warn:summary-schema-retried` — the summary's first output did not match the schema, it was retried and it worked).
A check that counts warnings as errors produces a permanent red and trains the user to ignore the
doctor; tell the two apart.

```powershell
$f = '.claude\scripts\.state\health.json'
if (-not (Test-Path $f)) { 'health: no records' }
else {
  $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
  $err = 0; $warn = 0
  foreach ($line in Get-Content $f) {
    if (-not "$line".Trim()) { continue }
    try { $r = "$line" | ConvertFrom-Json } catch { continue }
    $yas = [int]((($now - $r.ts) / 3600))
    if ("$($r.error)" -like 'warn:*') { $tur = 'WARNING'; if ($yas -lt 48) { $warn++ } }
    else { $tur = 'ERROR'; if ($yas -lt 48) { $err++ } }
    "$tur | $($r.component) | $($r.error) | $yas hours ago"
  }
  "summary: $err errors, $warn warnings in the last 48 hours"
}
```

🟢 no records, or `0 errors` in the last 48 hours (warnings are fine). 🟡 warnings but no errors in the
last 48 hours: the engine recovered by itself; look into it if it keeps repeating. 🔴 at least one `ERROR` in the last 48 hours.
Fix: look at the `component` field. If it is `flush`, the transcript or the model CLI — check 4b
first; `claude-exit-1` almost always means a logged-out session. If it is `compile`, the model call
is the problem. After reading the record and fixing its cause you may delete the file
(`Remove-Item .claude\scripts\.state\health.json`); the script writes it again.

### 9. Knowledge index size

```powershell
if (Test-Path knowledge\index.md) { "index: $(@(Get-Content knowledge\index.md).Count) lines" }
else { 'index: FILE MISSING' }
```

Only the first 150 lines of the index enter the context at session start.
🟢 150 lines or fewer. 🟡 between 151 and 300 lines; the lower rows are no longer injected.
🔴 over 300 lines: time for a summary index.
Fix: group the index under theme headings, collapse old rows into a single summary row,
and leave the detail in the article. If the file is missing entirely, restore the seed file from the repo.

### 10. Cloud sync conflict files

OneDrive, not iCloud. OneDrive leaves the conflicting copy as `file-MACHINENAME.md` or `file (1).md`;
the `* 2.*` pattern can still show up in a vault that was moved over.

```powershell
$c = @(Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {
  $_.FullName -notlike '*\.git\*' -and (
    $_.Name -match ' 2\.' -or $_.Name -match ' \(\d+\)\.' -or $_.Name -match "-$env:COMPUTERNAME\."
  )
})
if ($c.Count -eq 0) { 'clean' } else { $c.FullName }
```

🟢 output is `clean`. 🔴 output present: sync kept two copies of the same file, and some of the memory files
may be in the wrong copy.
Fix: compare each listed file with its original
(`Compare-Object (Get-Content a.md) (Get-Content 'a (1).md')`), move the needed content into the
original, then delete the conflict copy. Do not delete without asking the user.

### 11. Git repository and uncommitted changes

```powershell
$null = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -eq 0) { "git: present, uncommitted: $(@(git status --porcelain).Count) files" }
else { 'git: NO REPO' }
```

🟢 repo present and fewer than 50 uncommitted files. 🟡 more than 50 piled up. 🔴 no repo, meaning
the memory has no history you can roll back to.
Fix: if there is no repo, `git init -b main`, then **`git config core.autocrlf false`** and a first
commit. This setting is required on Windows: otherwise a later checkout converts the `.py` and `.sh` files
to CRLF. If changes have piled up, commit.

### 12. Version file

```powershell
if (Test-Path .beyin-version) { "version: $(Get-Content .beyin-version -TotalCount 1)" }
else { 'version: FILE MISSING, v1 vault' }
```

🟢 `2.3.0`. 🟡 `2.2.0`, `2.1.0`, `2.0.0` or no file.
Fix: **do not run `scripts/upgrade.sh` on Windows** — it doubles every hook and stamps a version
onto an engine that cannot load (see `docs/WINDOWS-PORT.md`). There is no upgrade path on Windows:
set up a new vault and move the memory files over by hand.

### 13. Rules file

```powershell
$k = Get-ChildItem -Directory | Where-Object { $_.Name -like '*850-Companion' } |
     ForEach-Object { Join-Path $_.FullName 'Kurallar.md' }
if ($k -and (Test-Path -LiteralPath $k)) { "rules: present, $(@(Get-Content -LiteralPath $k).Count) lines" }
else { 'rules: MISSING' }
```

Do not type the emoji in the folder name into the command by hand; find it with a wildcard as above: the emoji
breaks when passed inline and the file appears "missing".

🟢 present. 🟡 missing: the user's corrections are not being made permanent.
Fix: copy the seed `Kurallar.md` file from the repo into the `850-Companion` folder.

### 14. Double-active hooks (settings.json + settings.local.json)

On Windows the command is `pwsh.exe` and the script path sits in `args`. A POSIX check that only looks
at the `command` field counts every event as `0` here and gives a false red; the one below combines the two.

```powershell
$ev = 'SessionStart','UserPromptSubmit','SessionEnd','PreCompact'
$v  = 'session-start.ps1','prompt-counter.ps1','session-end.ps1','pre-compact.ps1'
$n = @{}; foreach ($e in $ev) { $n[$e] = 0 }
foreach ($file in '.claude\settings.json', '.claude\settings.local.json') {
  if (-not (Test-Path $file)) { continue }
  try { $d = Get-Content $file -Raw | ConvertFrom-Json } catch { "${file}: CORRUPT JSON"; continue }
  foreach ($e in $ev) { foreach ($m in @($d.hooks.$e)) { foreach ($h in @($m.hooks)) {
    $blob = "$($h.command) $($h.args -join ' ')"
    if (@($v | Where-Object { $blob -like "*$_*" }).Count -gt 0) { $n[$e]++ }
  } } }
}
foreach ($e in $ev) { "${e}: $($n[$e])" }
```

🟢 the count for all four events is exactly `1`. 🔴 any of them `2` or more: on that event the
hooks run twice every time, so every prompt is counted twice and two flushes fire at the end of every
session. `0` means that event is not wired at all.
Fix: delete the brain hook entry in `.claude\settings.local.json`; do not touch unrelated
hooks or other keys such as `env` and `permissions`. The single wiring must stay
in `.claude\settings.json`.

### 15. Backup leftovers in the vault that may carry secrets

```powershell
$r = @(Get-ChildItem -Recurse -File -Force -Include '*.yedek','*.yedek-*','settings.local.json.*','*.bak','*.orig' -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -notlike '*\.git\*' })
if ($r.Count -eq 0) { 'backup leftovers: clean' } else { $r.FullName }
$tracked = @(git ls-files 2>$null | Select-String 'settings\.local\.json|\.yedek|\.env$')
if ($tracked.Count -eq 0) { 'no tracked secret files' } else { $tracked }
```

🟢 both sections clean. 🔴 if a backup file shows up: these files may be a copy of `settings.local.json`
and carry an API key; if anything shows up in the second section, the secret is already tracked
by git.
Fix: move the backup outside the vault; Windows has no `chmod 600`, the equivalent is
`icacls <file> /inheritance:r /grant:r "$env:USERNAME:(F)"`. If git tracks it,
untrack it with `git rm --cached <file>`, verify the `.gitignore` rule, and
**revoke and rotate** the leaked key at the provider.

### 16. Graph integrity (broken links + orphan notes)

`PYTHONIOENCODING` is required, not decoration. `graf_kontrol.py` prints folder names in the orphan list, and
all of the template's content folders start with an emoji (`📥 000-Inbox`, `🛠️ 600-Arsenal`). On Windows,
when output is redirected to a pipe or a file, Python uses the console code page (`cp1254` on a
Turkish system, `cp1252` on most Western European systems) and the emoji kills the scan with
`UnicodeEncodeError`. The agent always captures the output, so the redirected state is the normal state. The moment
the first orphan note appears in an emoji folder, check 16 crashes; this line prevents that up front.

```powershell
. .\.claude\hooks\lib.ps1
$env:PYTHONIOENCODING = 'utf-8'
& (Get-BeyinPython) .claude\scripts\graf_kontrol.py
```

Memory is not a flat pile of files but a **graph**: a note can only be found if there is a link
leading to it. An orphan note sits on disk, but to reach it the agent has to scan the whole vault,
which means it either burns tokens or fails to find it and makes something up. A broken link points to
an address that does not exist on the map. No other check catches either of them.

🟢 0 broken links. 🟡 1–20 broken links. 🔴 more than 20 broken links.
The orphan count alone is not 🔴: drafts, archival and one-off notes are naturally
orphans. In a Windows install the **copies** under `.agents\skills` also show up as orphans; this
is normal, since without symlinks the scanner counts them as separate files.
Fix: open the list with `--tam`. For a broken link, either create the target note or fix the
link; if the target is missing on purpose (such as a `[[wikilink]]` used as an example in a document), leave it.
For an orphan note, link to it from a related parent note or from `Dashboard.md`.

## Report format

After all checks are done, print a single table:

```
| Check | Status | Finding |
| --- | --- | --- |
| Hook files | 🟢 | all four .ps1 in place |
| settings.json wiring | 🟢 | all four events wired |
| pwsh.exe PATH | 🟢 | C:\Program Files\...\pwsh.exe |
| Recursion guard | 🟢 | present in all |
| Codex links | 🟢 | router same content, hooks.json absolute |
| Antigravity links | 🟢 | PreInvocation and Stop adapter registered |
| Python and model CLI | 🟢 | python 3.14.6, claude present |
| Model CLI session | 🟢 | logged in (claudeai) |
| python3-missing marker | 🟢 | no marker |
| Daily log freshness | 🟡 | last log 51 hours ago |
| Compile status | 🔴 | last_status fail:timeout |
| Health records | 🔴 | compile error yesterday |
| Knowledge index | 🟢 | 42 lines |
| Sync conflicts | 🟢 | clean |
| Git | 🟢 | repo present, 3 files uncommitted |
| Version | 🟢 | 2.3.0 |
| Rules | 🟢 | present, 29 lines |
| Double-active hooks | 🔴 | SessionEnd wired 2 times |
| Secret backup leftovers | 🟢 | clean |
| Graph integrity | 🟡 | 4 broken links, 12 orphan notes |
```

After the table, write one line starting with "Fix:" for each 🔴 row only, and give the command too.
Then a one-sentence verdict, for example: "The brain is up, but the compiler has been stuck for two days; fix that first."
If everything is green, keep the verdict short too: "The brain is healthy, nothing to do."
