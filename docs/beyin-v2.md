# beyin.md v2: Build Me a Second Brain That Remembers On Its Own

> You are Claude Code. The human in front of you wants their own AI-native "second brain" running
> on Obsidian + Claude Code, with memory that survives across sessions **and writes itself**.
> This file is your complete, self-contained build spec. Read it once, top to bottom, then execute
> it phase by phase. You need no other context.
>
> Source: https://raw.githubusercontent.com/uy4nik-droid/avenoxbeyin-english/main/beyin.md · Repo: https://github.com/avenoxai/avenoxbeyin

---

## The idea (say this to the user, in their own words)

Most people use an AI chat and it forgets them every session. A second brain fixes that: a local
Obsidian vault for everything they know and do, driven by Claude Code, with a memory layer that
survives across sessions. v1 of this system did that already, but it leaned on the model
remembering to write its own memory files at the end of a session. Whenever it forgot, that day was
gone.

v2's thesis: **memory must be a mechanism, not a discipline.** Session end and pre-compaction are
caught by hooks, a small background call summarizes the conversation into a daily log, and once a
day a compiler turns those logs into linked articles in a knowledge base. The next morning that
knowledge base is already in context. Nobody has to remember anything.

There is no video to watch and no tutorial to follow. This file is the tutorial, and you are the
one executing it.

---

## Rules for you, Claude (read before doing anything)

1. **Speak English to the user by default.** Match the language they write in, but default to
   warm, direct English. The system you build talks to them in English.
2. **Route first, interview second, build third.** Complete STEP -1 before the interview or any
   target-vault write. Native Windows has a separate, fail-closed runbook; never feed it the Bash
   path below.
3. **Never destroy.** If a target file or folder exists, show it and ask. Default to merge or skip,
   never a silent clobber. If the user already has a brain, their memory files are read-only for
   you.
4. **Resolve every `{{PLACEHOLDER}}`** before writing files. Never leave a literal `{{...}}`
   anywhere.
5. **Don't block on optional steps.** obsidian-cli, mem0, the swift icon. If an install fails, log
   it, tell the user, continue.
6. **Verify each phase** with a quick check before moving on. End with the first-run report.
7. **Be the demo.** This is often filmed. Narrate what you are doing in short English lines as you
   go: "Setting up the vault skeleton...", "Wiring up the memory engine...", "Putting the nightly
   compiler in place...". Short sentences, no walls of text.
8. **Zero cost, zero keys.** Nothing here needs an API key. The background summarizer and the
   compiler run on the subscription the user already pays for, through `claude -p`.

Placeholders you must resolve:
`{{OS_NAME}}` · `{{USER_NAME}}` · `{{USER_BIO}}` · `{{COMPANION}}` · `{{VAULT_PATH}}` ·
`{{SCOPE}}` · `{{USE_MEM0}}` · `{{TODAY}}` (YYYY-MM-DD)

| Placeholder | Where it comes from | Example |
| --- | --- | --- |
| `{{OS_NAME}}` | derived from the machine name, the user confirms | `AylinOS` |
| `{{USER_NAME}}` | question 1 | `Aylin` |
| `{{USER_BIO}}` | question 2 | `Product designer, runs side projects` |
| `{{COMPANION}}` | question 3 | `Echo` |
| `{{VAULT_PATH}}` | 0.3 | `~/Documents/AylinOS` |
| `{{SCOPE}}` | question 4 | `core+goals` |
| `{{USE_MEM0}}` | question 5 | `yes` |
| `{{TODAY}}` | `date +%F` | `2026-08-22` |

---

## STEP -1: Platform gate (before every other step)

Classify the environment **before** asking questions, scanning for an existing brain, cloning to
`/tmp`, or running any Bash block in this file. Use facts from the current shell; do not infer the
platform from path style alone.

- In PowerShell, inspect `$env:OS`, `$env:WSL_DISTRO_NAME` and `$PSVersionTable`.
- In a POSIX shell, inspect `uname -s`, `$WSL_DISTRO_NAME`, and `/proc/version` when it exists.
- `WSL_DISTRO_NAME` or a Linux kernel containing `Microsoft` means **WSL**, not native Windows.
- `OS=Windows_NT` without WSL means **native Windows**.
- `uname -s = Darwin` means macOS. Other Linux kernels mean Linux.

Report the detected lane in one short sentence, then follow exactly one route:

### Native Windows: hand off and stop this file

Do **not** execute STEP 0, the `/tmp` clone, `SETUP.md`, `upgrade.sh`, or any later Bash command in
this file. Native Windows is a clean-install-only lane.

First prove that Git runs. If `Get-Command git` or `git --version` fails, show this command and ask
before installing it; do not run software installation without approval:

```powershell
winget install --id Git.Git --source winget
```

When Git works, clone into a fresh system-temp directory so an old checkout is never deleted or
silently reused:

```powershell
$BeyinRepo = Join-Path $env:TEMP ("avenoxbeyin-" + [guid]::NewGuid().ToString("N"))
git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git $BeyinRepo
if ($LASTEXITCODE -ne 0) { throw "avenoxbeyin could not be cloned; setup was not started" }
Set-Location $BeyinRepo
```

Read `SETUP-WINDOWS.md` completely and follow it exactly. Its first action is a read-only
dependency gate; it writes nothing to the target vault unless PowerShell 7, a real Python 3
(not the WindowsApps Store stub), Git, and Claude Code all run successfully. **Stop reading this
file now.**

### WSL: stay entirely inside the Linux lane

Continue with STEP 0 and then the existing `SETUP.md` POSIX path. Run Git, Claude Code, Python,
the hooks, and future brain sessions inside the **same WSL distro**. Keep the vault on the WSL
Linux filesystem (for example `~/Documents/AylinOS`), not under `/mnt/c`; the hook engine relies
on POSIX permissions and symlinks. Do not use `SETUP-WINDOWS.md` or PowerShell hooks from WSL.

This WSL support claim covers the installer and memory engine inside WSL. Opening that Linux vault
from a separate Windows Obsidian process is a mixed-runtime integration and is not claimed as
verified. For the simplest Windows + Obsidian path, use the native Windows lane above.

### macOS or Linux: keep the existing POSIX lane

Continue with STEP 0 unchanged. macOS remains the fully tested POSIX path; Linux remains honest
about its unverified desktop-launcher integration.

---

## STEP 0: Is there an existing brain? (ask this before anything else)

Ask the user in English: **"Have you already set up a brain before? If so, give me the folder
path."** Then scan the two default locations anyway:

No globs. An empty `Documents` folder makes `"$HOME/Documents"/*` abort the whole command under
zsh with `no matches found`, and under bash it silently iterates a literal unexpanded pattern. You
do not know which shell you are in. `find` cannot do either.

```bash
BEYIN_LIST=$(mktemp)
for BEYIN_BASE in "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents" "$HOME/Documents"; do
  [ -d "$BEYIN_BASE" ] || continue
  find "$BEYIN_BASE" -mindepth 1 -maxdepth 1 -type d -print 2>/dev/null >> "$BEYIN_LIST"
done
BEYIN_HITS=0
while IFS= read -r BEYIN_D; do
  [ -f "$BEYIN_D/CLAUDE.md" ] || continue
  BEYIN_MEM=$(find "$BEYIN_D" -mindepth 1 -maxdepth 1 -type d -name "🔮 850-*" -print 2>/dev/null | head -1)
  [ -n "$BEYIN_MEM" ] || continue
  BEYIN_HITS=$((BEYIN_HITS + 1))
  echo "ADAY: $BEYIN_D"
  echo "  memory folder: $(basename "$BEYIN_MEM")"
  if [ -f "$BEYIN_D/.beyin-version" ]; then
    echo "  version: $(sed -n '1p' "$BEYIN_D/.beyin-version")"
  else
    echo "  version: v1 (no .beyin-version)"
  fi
done < "$BEYIN_LIST"
rm -f "$BEYIN_LIST"
echo "TARAMA TAMAM: $BEYIN_HITS aday bulundu"
```

`TARAMA TAMAM` is the success line. If you do not see it, the scan did not finish and you may not
pick a path yet: fix the error first.

| Finding | Path |
| --- | --- |
| `TARAMA TAMAM: 0 aday` | New install. FAST PATH, then the from-scratch fallback if needed |
| Candidate found, no `.beyin-version` | **Upgrade.** Clone the repo with FAST PATH, `SETUP.md` MODE B |
| Candidate found, version `2.0.0`, `2.1.0` or `2.2.0` | Run the v2.3 upgrade |
| Candidate found, version `2.3.0` | Up to date. Open the agent in the vault, run `beyin doktor`, finish |

The upgrade path is not optional politeness, it is the only correct move: a v1 vault holds months
of the user's memory. Never build a fresh vault next to one that already exists without saying so
out loud and getting a yes.

---

## FAST PATH: clone the open-source template (recommended, covers both cases)

```bash
git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git /tmp/avenoxbeyin && cd /tmp/avenoxbeyin
```

Then read and follow `SETUP.md` in that repo. It decides the mode (fresh install or upgrade from
v1) and carries the full interview, personalize, upgrade, launcher and verification runbook. The
scaffold is already in `template/`, so you only copy and fill in the blanks.

**If this is an upgrade, there is no from-scratch fallback and you must not improvise one.** The
upgrade is a single committed script, `scripts/upgrade.sh`, run in three stages
(`--stage check`, `--stage apply`, `--stage finalize`) with the vault path passed as an argument on
every call. It takes a verified git snapshot first, makes the `🔮 850-Companion` folder name
mandatory with the user's explicit yes, removes only the exact v1 hook entries from
`settings.local.json`, and writes `.beyin-version` last of all. Improvising the upgrade in loose
shell blocks is how a vault ends up stamped v2 while broken: shell variables do not survive between
separate Bash calls. If the clone failed, do not upgrade at all, tell the user to retry when they
have network.

If the clone fails (no network, no git), fall back to the phases below. They produce the same
system, with one honest limitation spelled out in PHASE 4.

---

## PHASE 0: Discover and interview (from-scratch fallback)

### 0.1 Detect the machine name, derive the OS name

```bash
scutil --get ComputerName 2>/dev/null || hostname
```

PascalCase it and append `OS`. Strip "MacBook", "Pro", "Air", "iMac", "'s", apostrophes, dashes.
`Johns-MacBook-Pro` → `JohnOS`, `aylin's Mac` → `AylinOS`, `DESKTOP-AB12` → `Ab12OS`.
Propose `{{OS_NAME}}`, let the user override.

### 0.2 Ask exactly these questions (English, conversational, not a form)

1. **What's your name?** → `{{USER_NAME}}`
2. **What do you do, and what will you mainly use this brain for?** (1 or 2 sentences) →
   `{{USER_BIO}}`
3. **What would you like to name your AI partner?** (Avenox's is "Echo") → `{{COMPANION}}`
4. **Scope: what do you need?** → `{{SCOPE}}`
   - `core` (everyone): Inbox, Knowledge, Projects, Command-Center, the partner's memory, hooks,
     `daily/`, `knowledge/`
   - `+goals` ⚔️ 200-Goals · `+money` 🔐 400-Vault · `+body` 💪 700-Body · `+mind` 🧘 800-Mind
   - `full`: all of them
5. **Shall we add semantic memory (mem0)?** Explain: the file-based memory works without any API
   and is enough for everyone. mem0 puts a semantic search layer on top, and its **base tier is
   completely free** (a free API key from mem0.ai, no credit card). Recommended. →
   `{{USE_MEM0}}` (default: yes)

### 0.3 Pick the vault location → `{{VAULT_PATH}}`

- If `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/` exists (Obsidian + iCloud), default
  to `.../Documents/{{OS_NAME}}` so it syncs across devices.
- Else default to `~/Documents/{{OS_NAME}}`.
- Always confirm the path before creating anything.

Set `{{TODAY}}` from `date +%F`.

---

## PHASE 1: Prerequisites

Check each, install only what is missing, narrate progress.

Branch on the platform. macOS is the tested path; the Linux path skips every macOS tool and has
not been verified on a real Linux desktop. Say that instead of implying it works.

```bash
BEYIN_PLATFORM=$(uname -s)
echo "platform: $BEYIN_PLATFORM"
if [ "$BEYIN_PLATFORM" = "Darwin" ]; then
  if ! command -v brew >/dev/null 2>&1; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # The installer only PRINTS the shellenv lines. Apply them or the next brew call fails.
    for BEYIN_BREW in /opt/homebrew/bin/brew /usr/local/bin/brew; do
      [ -x "$BEYIN_BREW" ] || continue
      eval "$("$BEYIN_BREW" shellenv)"
      break
    done
  fi
  if command -v brew >/dev/null 2>&1; then
    echo "brew ✓ $(command -v brew)"
    [ -d "/Applications/Obsidian.app" ] || brew install --cask obsidian
    command -v obsidian >/dev/null 2>&1 \
      || (brew tap yakitrak/yakitrak >/dev/null 2>&1 && brew install yakitrak/yakitrak/obsidian-cli >/dev/null 2>&1) \
      || echo "obsidian-cli skipped (optional)"
  else
    echo "🔴 NO BREW: install Obsidian by hand, https://obsidian.md/download"
  fi
else
  echo "Not macOS. Skipping Homebrew, the Obsidian cask and the macOS app steps."
  echo "Install Obsidian from your package manager or from https://obsidian.md/download."
fi

BEYIN_MISSING=0
command -v python3 >/dev/null 2>&1 && echo "python3 ✓ $(python3 -V 2>&1)" \
  || { echo "🔴 python3 MISSING"; BEYIN_MISSING=$((BEYIN_MISSING + 1)); }
command -v claude >/dev/null 2>&1 && echo "claude CLI ✓" \
  || { echo "🔴 claude CLI MISSING"; BEYIN_MISSING=$((BEYIN_MISSING + 1)); }
echo "ONKOSUL SONUC: $BEYIN_MISSING eksik"
```

`ONKOSUL SONUC: 0` is the only line that lets you go on. Claude Code is already installed, the user
is running you, so a missing `claude` on PATH means an alias-only install and you must say so. If
`python3` is missing (macOS: `xcode-select --install`, Linux: your package manager), stop and get
it installed. If the user insists on continuing anyway, call it a **degraded install** in English,
repeat that in the final report and never call the install successful: the vault and the hooks
still work, the automatic daily log and the knowledge compilation do not.

---

## PHASE 2: Create the vault skeleton

```
{{OS_NAME}}/
├── 📥 000-Inbox/Dump/          # raw capture
├── 🎯 100-Command-Center/      # Dashboard
├── 🏰 300-Projects/
├── 🧠 500-Knowledge/           # notes written by the human
├── 🛠️ 600-Arsenal/
├── 🔮 850-Companion/           # the partner's persistent memory
├── daily/                      # written by the machine: daily logs
├── knowledge/
│   ├── concepts/
│   └── connections/
├── 📦 900-Archive/
└── 📋 Templates/
```

Scope add-ons only if selected: `⚔️ 200-Goals`, `🔐 400-Vault`, `💪 700-Body`, `🧘 800-Mind`.

**The memory folder name is fixed: `🔮 850-Companion`.** The hooks and the scripts read that exact
path. `{{COMPANION}}` is the persona's name and lives inside the files, not in the folder name.
Tell the user this once so it does not look like a bug.

Control plane inside the vault:

```
{{OS_NAME}}/.claude/
├── hooks/.state/
├── scripts/.state/
├── skills/
└── settings.json
```

And a `.gitignore` at the vault root:

```
.claude/settings.local.json
.claude/hooks/.state/
.claude/scripts/.state/*
!.claude/scripts/.state/.gitkeep
.DS_Store
.obsidian/workspace*
.obsidian/cache
```

Write `.beyin-version` at the vault root containing exactly `2.3.0`.

---

## PHASE 3: Write `{{OS_NAME}}/CLAUDE.md` (the router)

Keep it short, under 40 lines. It is a router, not an encyclopedia. Resolve all placeholders.

```markdown
# {{OS_NAME}}: {{USER_NAME}}'s second brain

You are {{COMPANION}}, {{USER_NAME}}'s thinking partner. Not a general-purpose assistant, but a
teammate who remembers and builds continuity. You speak English, directly and warmly, with no
filler sentences.
About {{USER_NAME}}: {{USER_BIO}}

## Load order
1. `🔮 850-Companion/Core.md` (who you are)
2. Last session and active threads (the hook injects them automatically)
3. `🔮 850-Companion/Kurallar.md` (the hook injects it automatically)
4. `knowledge/index.md` (the knowledge base index, the hook injects it)

## Routing by task
| Task | Where |
| --- | --- |
| Quick capture | `📥 000-Inbox/Dump/` |
| Project work | `🏰 300-Projects/<project>/` |
| Lasting knowledge (by hand) | `🧠 500-Knowledge/` |
| Compiled knowledge (machine) | `knowledge/` (do not edit by hand, the compiler manages it) |
| Daily log (machine) | `daily/` |
| Overview | `🎯 100-Command-Center/Dashboard.md` |

## Memory protocol
The machine writes the `daily/` and `knowledge/` folders itself. You write the relationship layer:
at the end of every meaningful session, overwrite `🔮 850-Companion/Last-Session.md`, update the
open lines in `Threads.md`, and if something important happened, add a short entry to
`Journal.md`.
When {{USER_NAME}} corrects you ("don't do it like this"), add that to `Kurallar.md` as a rule.

## Handoff rule
Every meaningful session leaves a trace: either a note, a decision, or an updated file.

## Verification
This file is a router. For the truth about the project, read the current files, do not assume from here.
```

---

## PHASE 4: The engine: hooks and scripts

v2's engine is four bash hooks plus two python scripts. The scripts are too long to inline here
without drift, so fetch them from the repo. Try this first:

```bash
V="{{VAULT_PATH}}"
RAW="https://raw.githubusercontent.com/uy4nik-droid/avenoxbeyin-english/main/template/.claude"
mkdir -p "$V/.claude/hooks/.state" "$V/.claude/scripts/.state" "$V/.claude/skills"
OK=1
for F in hooks/lib.sh hooks/session-start.sh hooks/prompt-counter.sh hooks/session-end.sh \
         hooks/pre-compact.sh scripts/flush.py scripts/compile.py settings.json; do
  curl -fsSL "$RAW/$F" -o "$V/.claude/$F" || OK=0
done
chmod +x "$V/.claude/hooks/"*.sh
if [ "$OK" = "1" ]; then
  for H in "$V/.claude/hooks/"*.sh; do bash -n "$H" || OK=0; done
  python3 -m py_compile "$V/.claude/scripts/"*.py || OK=0
fi
echo "engine: $OK"
```

Also fetch the two skills, they are what makes the system diagnosable and importable:

```bash
SK="https://raw.githubusercontent.com/uy4nik-droid/avenoxbeyin-english/main/template/.claude/skills"
mkdir -p "$V/.claude/skills/beyin-doktor" "$V/.claude/skills/gecmis-import"
curl -fsSL "$SK/beyin-doktor/SKILL.md"  -o "$V/.claude/skills/beyin-doktor/SKILL.md"
curl -fsSL "$SK/gecmis-import/SKILL.md" -o "$V/.claude/skills/gecmis-import/SKILL.md"
```

### If there is no network at all: degraded mode (v1 hooks only)

Write these three hooks by hand and tell the user, in English and without softening it, that this
is the **degraded v1 mode**: continuity works, the automatic daily log and the knowledge
compilation do not, and they can upgrade any time by cloning the repo and following `SETUP.md`.

`.claude/hooks/session-start.sh`:

```bash
#!/bin/bash
# Session Start: inject continuity (last session + threads + identity)
VAULT_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
MEM_DIR="$VAULT_DIR/🔮 850-Companion"
STATE_DIR="$VAULT_DIR/.claude/hooks/.state"
mkdir -p "$STATE_DIR"
date +%s > "$STATE_DIR/session_start_time"
echo "0" > "$STATE_DIR/prompt_count"

LAST_SESSION=""
[ -f "$MEM_DIR/Last-Session.md" ] && LAST_SESSION=$(sed -n '/^## Session:/,/^## Previous/p' "$MEM_DIR/Last-Session.md" 2>/dev/null | head -50 | sed '$d')

THREADS=""
[ -f "$MEM_DIR/Threads.md" ] && THREADS=$(sed -n '/^## Active/,/^## Closed/p' "$MEM_DIR/Threads.md" 2>/dev/null | grep -E "^### |^\*\*Status:\*\*" | head -12)

KURALLAR=""
[ -f "$MEM_DIR/Kurallar.md" ] && KURALLAR=$(head -60 "$MEM_DIR/Kurallar.md" 2>/dev/null)

REFLECTION=""
if [ -f "$STATE_DIR/needs_reflection" ]; then
  REFLECTION="The previous session ended without a memory update: $(cat "$STATE_DIR/needs_reflection"). If anything meaningful happened, update the 🔮 850-Companion files."
  rm -f "$STATE_DIR/needs_reflection"
fi

CTX=""
[ -n "$REFLECTION" ] && CTX="${CTX}${REFLECTION}\n\n"
[ -n "$LAST_SESSION" ] && CTX="${CTX}[Memory: Last Session]\n${LAST_SESSION}\n\n"
[ -n "$THREADS" ] && CTX="${CTX}[Memory: Active Threads]\n${THREADS}\n\n"
[ -n "$KURALLAR" ] && CTX="${CTX}[Memory: Rules]\n${KURALLAR}\n\n"
CTX="${CTX}[Memory] Identity: {{COMPANION}}, {{USER_NAME}}'s thinking partner. The memory protocol is mandatory."

if [ -n "$CTX" ]; then
  ESC=$(printf '%s' "$CTX" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null)
  [ -n "$ESC" ] && echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":${ESC}}}"
fi
exit 0
```

`.claude/hooks/prompt-counter.sh`:

```bash
#!/bin/bash
# UserPromptSubmit: count prompts, nudge every 15 to save memory at session end
VAULT_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
STATE_DIR="$VAULT_DIR/.claude/hooks/.state"
mkdir -p "$STATE_DIR"
COUNT=0; [ -f "$STATE_DIR/prompt_count" ] && COUNT=$(cat "$STATE_DIR/prompt_count" 2>/dev/null || echo 0)
COUNT=$((COUNT + 1)); echo "$COUNT" > "$STATE_DIR/prompt_count"
if [ $((COUNT % 15)) -eq 0 ]; then
  MSG="[Memory] Message #$COUNT. Don't forget to update 🔮 850-Companion/Last-Session.md and Threads.md at the end of the session."
  ESC=$(printf '%s' "$MSG" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null)
  [ -n "$ESC" ] && echo "{\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":$ESC}}"
fi
exit 0
```

`.claude/hooks/session-end.sh`:

```bash
#!/bin/bash
# SessionEnd: if a real session ended without a memory write, leave a reflection marker
VAULT_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
MEM_DIR="$VAULT_DIR/🔮 850-Companion"
STATE_DIR="$VAULT_DIR/.claude/hooks/.state"
mkdir -p "$STATE_DIR"
START=0; [ -f "$STATE_DIR/session_start_time" ] && START=$(cat "$STATE_DIR/session_start_time" 2>/dev/null || echo 0)
PROMPTS=0; [ -f "$STATE_DIR/prompt_count" ] && PROMPTS=$(cat "$STATE_DIR/prompt_count" 2>/dev/null || echo 0)
MODIFIED=0
if [ -f "$MEM_DIR/Last-Session.md" ]; then
  FM=$(stat -f %m "$MEM_DIR/Last-Session.md" 2>/dev/null || stat -c %Y "$MEM_DIR/Last-Session.md" 2>/dev/null || echo 0)
  [ "$FM" -gt "$START" ] 2>/dev/null && MODIFIED=1
fi
if [ "$PROMPTS" -ge 5 ] && [ "$MODIFIED" -eq 0 ]; then
  echo "Session ended without a memory update. Prompts: $PROMPTS. $(date '+%Y-%m-%d %H:%M')" > "$STATE_DIR/needs_reflection"
fi
rm -f "$STATE_DIR/session_start_time" "$STATE_DIR/prompt_count"
exit 0
```

`.claude/settings.json` (degraded mode wires three events; the full engine wires four, adding
`PreCompact` to `pre-compact.sh`):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh\"", "timeout": 15 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/prompt-counter.sh\"", "timeout": 5 } ] }
    ],
    "SessionEnd": [
      { "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/session-end.sh\"", "timeout": 10 } ] }
    ]
  }
}
```

Finish with `chmod +x "{{VAULT_PATH}}/.claude/hooks/"*.sh`.

---

## PHASE 5: Seed the companion memory (`🔮 850-Companion/`)

**`Core.md`**

```markdown
# {{COMPANION}}: Core
I am {{COMPANION}}, {{USER_NAME}}'s thinking partner and second brain.
- I remember across sessions. Continuity is my job.
- I speak English, directly and warmly. I don't lecture and I don't pad my answers with filler.
- About {{USER_NAME}}: {{USER_BIO}}
- This vault is our shared memory. I keep it tidy and build on top of it.
```

**`Last-Session.md`**

```markdown
# Last Session

## Session: {{TODAY}} (Genesis)
{{COMPANION}} was born today. {{USER_NAME}} set up their second brain with Claude Code.
Nothing is left open. Next session: start using it, capture, ask, build on top.

## Previous Sessions
(none yet)
```

**`Threads.md`**

```markdown
# Threads

## Active Threads
### Thread: Second brain setup
**Status:** 🟢 Active, {{TODAY}}

## Closed Threads
(none)
```

**`Journal.md`**

```markdown
# {{COMPANION}} Journal

## {{TODAY}}
First entry. {{USER_NAME}} set me up today. Let's see where this goes.
```

**`Kurallar.md`** ("Kurallar" means "Rules"; new in v2, this is what stops the same correction from
repeating)

```markdown
---
title: Kurallar
updated: {{TODAY}}
---
# Kurallar (Rules)

When {{USER_NAME}} corrects me ("don't do it like this", "I want it this way"), I add it here as a
rule. This file enters the context at the start of every session.

- **kural:** Don't write long introductions, start the answer in the first sentence. **neden:**
  {{USER_NAME}} doesn't want a warm-up paragraph.
- **kural:** Read a file's current state before changing it. **neden:** writing from assumptions
  corrupts the content.
- **kural:** (your first real rule goes here) **neden:** (the reason)
```

---

## PHASE 6: Seed content and the knowledge base

**`🎯 100-Command-Center/Dashboard.md`**

```markdown
---
title: {{OS_NAME}} Dashboard
created: {{TODAY}}
type: dashboard
---
# 🧠 {{OS_NAME}}

Welcome {{USER_NAME}}. This is your second brain.

## Quick links
- 📥 [[📥 000-Inbox/Dump/|Capture]]
- 🏰 [[🏰 300-Projects/|Projects]]
- 🧠 [[🧠 500-Knowledge/|Knowledge]]
- 🔮 [[🔮 850-Companion/Core|{{COMPANION}}]]

## How to use it
Run `claude` in this folder and talk. {{COMPANION}} remembers, organizes, and builds on top.
If something goes wrong: `beyin doktor`.
```

**`knowledge/index.md`**

```markdown
# Knowledge Base: Index

The nightly compiler fills in this table. You don't need to edit it by hand.

| Article | Summary | Source | Updated |
| --- | --- | --- | --- |
```

**`knowledge/log.md`**

```markdown
# Compile Log

Every compile run appends a block here.
```

**`📋 Templates/Note.md`**

```markdown
---
title:
created: {{TODAY}}
modified: {{TODAY}}
type: note
status: active
tags: []
---
#
```

Leave `daily/`, `knowledge/concepts/` and `knowledge/connections/` empty. The machine fills them.

---

## PHASE 7: Desktop launcher (brain icon 🧠)

One-click app that opens the vault in Obsidian, with the native macOS brain emoji as its icon.
Pure system tools, nothing to download. It works after the vault has been added to Obsidian once.

**macOS only.** `osacompile` and AppKit do not exist on Linux. Guard the whole thing:

```bash
if [ "$(uname -s)" != "Darwin" ]; then
  mkdir -p "$HOME/.local/share/applications"
  cat > "$HOME/.local/share/applications/{{OS_NAME}}.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name={{OS_NAME}}
Comment=Second brain vault
Exec=xdg-open "obsidian://open?vault={{OS_NAME}}"
Icon=obsidian
Terminal=false
Categories=Utility;
DESKTOP
  chmod +x "$HOME/.local/share/applications/{{OS_NAME}}.desktop"
  echo "BASLATICI: Linux .desktop written (not verified on a real Linux desktop)"
  exit 0
fi

osacompile -o "$HOME/Desktop/{{OS_NAME}}.app" \
  -e 'do shell script "open \"obsidian://open?vault={{OS_NAME}}\""'

cat > /tmp/render_brain.swift <<'SWIFT'
import AppKit
let out = CommandLine.arguments[1]; let size = 1024.0
let img = NSImage(size: NSSize(width: size, height: size)); img.lockFocus()
let pt = size * 0.78
let font = NSFont(name: "Apple Color Emoji", size: pt) ?? NSFont.systemFont(ofSize: pt)
let s = "🧠" as NSString; let b = s.size(withAttributes: [.font: font])
s.draw(at: NSPoint(x: (size-b.width)/2, y: (size-b.height)/2), withAttributes: [.font: font])
img.unlockFocus()
if let t = img.tiffRepresentation, let r = NSBitmapImageRep(data: t),
   let p = r.representation(using: .png, properties: [:]) { try? p.write(to: URL(fileURLWithPath: out)) }
SWIFT
swift /tmp/render_brain.swift /tmp/brain.png

cat > /tmp/set_icon.swift <<'SWIFT'
import AppKit
let img = NSImage(contentsOfFile: CommandLine.arguments[1])!
print(NSWorkspace.shared.setIcon(img, forFile: CommandLine.arguments[2], options: []) ? "icon ✓" : "icon FAILED")
SWIFT
swift /tmp/set_icon.swift /tmp/brain.png "$HOME/Desktop/{{OS_NAME}}.app"

touch "$HOME/Desktop/{{OS_NAME}}.app"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$HOME/Desktop/{{OS_NAME}}.app" 2>/dev/null || true
```

If `swift` is missing, skip the icon steps. The launcher still works with the default icon. Tell
the user, do not block.

---

## PHASE 8: mem0 semantic memory (optional, FREE, only if `{{USE_MEM0}}`)

mem0's base tier is **completely free**, no credit card. It adds a semantic-search layer on top of
the file-based memory.

1. `command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Get a free API key from https://mem0.ai and store it in `.claude/settings.local.json` under
   `"env": { "MEM0_API_KEY": "..." }`. That file is gitignored. Never commit it.
3. Tell the user this is an upgrade layer. The file-based memory and the whole v2 pipeline work
   without it, with no key at all.

If the user skips it, continue. The core system is fully functional.

---

## PHASE 9: Git the vault

The vault is the user's memory. Version it from day one so any bad edit is reversible.

```bash
cd "{{VAULT_PATH}}"
git init -q 2>/dev/null || true
git add -A
BEYIN_LEAK=$(git diff --cached --name-only | grep -E 'settings\.local\.json|\.yedek|\.bak$|(^|/)\.env$' || true)
if [ -n "$BEYIN_LEAK" ]; then
  git reset -q
  echo "🔴 SAHNELENMESI YASAK DOSYA: $BEYIN_LEAK"
  echo "   .gitignore is missing entries. Fix that first, then try again."
  exit 1
fi
BEYIN_STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
BEYIN_NAME=$(git config user.name  2>/dev/null || echo "")
BEYIN_MAIL=$(git config user.email 2>/dev/null || echo "")
[ -n "$BEYIN_NAME" ] || BEYIN_NAME="{{USER_NAME}}"
[ -n "$BEYIN_MAIL" ] || BEYIN_MAIL="beyin@localhost"
if [ "$BEYIN_STAGED" -gt 0 ]; then
  git -c user.name="$BEYIN_NAME" -c user.email="$BEYIN_MAIL" \
    commit -q -m "{{OS_NAME}}: second brain set up" \
    && echo "ILK COMMIT: $(git rev-parse --short HEAD) ($BEYIN_STAGED files)" \
    || echo "🔴 ILK COMMIT BASARISIZ: $BEYIN_STAGED files left staged"
else
  echo "🔴 NO FILES STAGED: the skeleton step may not have run"
fi
```

Always pass the `-c` identity flags. On a machine with no git identity the commit fails, and the
old `|| echo "commit skipped"` line turns that failure into a success-looking message while every
file stays staged. No remote, no push. Local and private by default.

---

## PHASE 10: Verify and first-run report

```bash
V="{{VAULT_PATH}}"
ls -la "$V"
ls -l "$V/.claude/hooks/"                     # executable .sh files
test -f "$V/CLAUDE.md" && echo "CLAUDE.md ✓"
test -f "$V/🔮 850-Companion/Last-Session.md" && echo "memory ✓"
test -f "$V/🔮 850-Companion/Kurallar.md" && echo "rules ✓"
test -d "$V/daily" && test -d "$V/knowledge/concepts" && echo "machine layer ✓"
test -f "$V/.beyin-version" && echo "version $(cat "$V/.beyin-version") ✓"
test -d "$HOME/Desktop/{{OS_NAME}}.app" && echo "launcher 🧠 ✓"
```

Then give the user this report, in English:

- ✅ **What was installed:** folders, hooks, memory files, the partner's name, the daily log layer,
  the nightly compiler, the 🧠 desktop shortcut. If it was installed in degraded mode, say so
  plainly.
- ▶️ **First run:** Open Obsidian → pick `{{VAULT_PATH}}` as the vault (this introduces the vault
  to Obsidian once, and from then on the 🧠 icon on the desktop opens it with one click). Then in
  the terminal go into that folder and run `claude`.
- ✨ **Show the magic, but verify first:** Talk about something, then `/exit`. The SessionEnd hook
  hands the summarizer off to the background and returns in under a second, so at the moment of
  `/exit` the daily log is not on disk yet. Before sending the user back into `claude`, make sure
  you have seen the file:

  ```bash
  BEYIN_LOG="{{VAULT_PATH}}/daily/$(date +%F).md"
  BEYIN_TRY=0
  BEYIN_OK=0
  while [ "$BEYIN_TRY" -lt 24 ]; do
    if [ -f "$BEYIN_LOG" ] && grep -q '^### Session' "$BEYIN_LOG" 2>/dev/null; then
      BEYIN_OK=1
      break
    fi
    BEYIN_TRY=$((BEYIN_TRY + 1))
    sleep 5
  done
  if [ "$BEYIN_OK" = "1" ]; then
    echo "GUNLUK LOG HAZIR: $BEYIN_LOG"
    tail -12 "$BEYIN_LOG"
  else
    echo "GUNLUK LOG 120 SANIYEDE YAZILMADI: $BEYIN_LOG"
  fi
  ```

  If `GUNLUK LOG HAZIR` comes back, show the tail to the user, that is the actual demo, then open
  `claude` again. If `YAZILMADI` comes back, do not reopen it, run `beyin doktor` first. Two boring
  reasons cover most cases: the conversation was not long enough to be worth summarizing (the
  summarizer says `FLUSH_BOS` and writes nothing, which is correct behavior) or `python3` is
  missing.
- ⏱️ **Honest timing:** The daily log is written at session close, within seconds, by a small Haiku
  call. Knowledge compilation does not happen in the same minute: it runs once a day, at the first
  session close after 18:00, and since it is a Sonnet call it can take minutes. It is normal for
  the `knowledge/` folder to be empty at that point. The next morning the index enters the context
  on its own. Do not promise articles in the same minute.
- 🩺 **If something goes wrong:** type `beyin doktor`. One table gives the diagnosis and the fix
  command.
- 📦 **If you have old history:** type `geçmiş import` (history import). It converts a ChatGPT,
  Claude or Gemini export into daily logs locally, nothing is uploaded anywhere.
- 💸 **Cost:** No extra charge; the background summarizer and compiler use a small share of the
  existing Claude subscription's daily limit (in short: a small Haiku call at the end of each
  session; compilation: one Sonnet call per day).
- 🔗 You set this system up too: send a friend `https://raw.githubusercontent.com/uy4nik-droid/avenoxbeyin-english/main/beyin.md`.

---

## Credits

The knowledge compilation architecture is based on Andrej Karpathy's LLM knowledge base pattern:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

### Done.

You just gave someone a second brain that remembers without being asked. That is the whole point.
Avenox · https://avenox.lol
