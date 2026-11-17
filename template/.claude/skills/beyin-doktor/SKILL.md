---
name: beyin-doktor
description: Health check for the brain. Reports hooks, scripts, memory files, daily logs, compile status and vault hygiene in a single table. Use when the user says "brain doctor", "doctor", "health check", "is the brain working", "is memory broken" (or in Turkish "beyin doktor", "doktor", "sağlık kontrolü", "beyin çalışıyor mu", "hafıza bozuk mu"), or when you suspect a memory mechanism is silently not working.
---

# Brain Doctor

This skill audits the brain's mechanical layer: are the hooks firing, have the scripts run,
are the logs staying fresh, has the vault been polluted. The goal is to make silent failures visible.

## How you work

1. Work in the vault root (the folder containing CLAUDE.md/AGENTS.md). All paths are relative; do not write absolute paths.
2. Run the checks below **in order with Bash**. Use the commands exactly as written; do not guess.
3. Classify each check's output as 🟢 / 🟡 / 🔴.
4. Give the result in a single table and write one fix line for each 🔴.
5. At the very end, give a one-sentence verdict.

The checks are read-only. Do not fix anything on your own: report first, then fix if the user
asks.

## Checks

### 1. Do the hook files exist and are they executable

```bash
for h in session-start prompt-counter session-end pre-compact; do f=".claude/hooks/$h.sh"; if [ ! -f "$f" ]; then echo "$h: FILE MISSING"; elif [ ! -x "$f" ]; then echo "$h: not executable"; else echo "$h: ok"; fi; done
```

🟢 all four `ok`. 🔴 missing or not executable.
Fix: `chmod +x .claude/hooks/*.sh`; if a file is missing, copy it from the repo.

### 2. Are the hooks wired in settings.json

```bash
for h in session-start prompt-counter session-end pre-compact; do if grep -q "$h.sh" .claude/settings.json 2>/dev/null; then echo "$h: wired"; else echo "$h: NOT IN SETTINGS"; fi; done
```

🟢 all four wired. 🔴 if even one is missing, that hook never runs at all.
Fix: add the missing event to the `hooks` block in `.claude/settings.json` (SessionStart,
UserPromptSubmit, SessionEnd, PreCompact), then restart Claude Code.

### 3. Does every hook have the recursion guard

```bash
for f in .claude/hooks/*.sh; do if grep -q 'BEYIN_INVOKED_BY' "$f"; then echo "$(basename "$f"): guard present"; else echo "$(basename "$f"): NO GUARD"; fi; done
```

🟢 present in all. 🔴 missing. A hook without the guard fires again inside the background `claude -p`
call, which risks an infinite loop.
Fix: add `[ -n "${BEYIN_INVOKED_BY:-}" ] && exit 0` on the line right after the file's shebang.

### 3b. Codex router, skill and hook links

```bash
test -L AGENTS.md && [ "$(readlink AGENTS.md)" = "CLAUDE.md" ] && echo "router: shared" || echo "router: SEPARATE/MISSING"; test -L .agents/skills && [ "$(readlink .agents/skills)" = "../.claude/skills" ] && echo "skills: shared" || echo "skills: SEPARATE/MISSING"; test -L .codex/hooks && [ "$(readlink .codex/hooks)" = "../.claude/hooks" ] && echo "hooks: shared" || echo "hooks: SEPARATE/MISSING"; python3 -c "import json,os;d=json.load(open('.codex/hooks.json')); w={'SessionStart':('session-start.sh',15),'UserPromptSubmit':('prompt-counter.sh',5),'PreCompact':('pre-compact.sh',10),'SessionEnd':('session-end.sh',3)}; print('codex:', 'ok' if all(sum(n in (h.get('command') or '') and os.path.isabs((h.get('command') or '').strip(chr(39)+chr(34))) and h.get('timeout')==t for m in d.get('hooks',{}).get(e,[]) for h in m.get('hooks',[]))==1 for e,(n,t) in w.items()) else 'BROKEN')" 2>/dev/null || echo "codex: BROKEN/MISSING"
```

🟢 all four lines shared/ok. 🔴 means Codex is not seeing the same engine, or is reading a relative/stale command.
Fix: `python3 .claude/scripts/render_codex_hooks.py --vault "$PWD" --platform posix`, then
approve the changed project hooks in Codex's `/hooks` screen. Do not write the trust hash by hand.

### 3c. Antigravity hook adapter

```bash
python3 -c "import json;d=json.load(open('.agents/hooks.json'));h=d.get('avenox-beyin',{});print('antigravity:', 'ok' if len(h.get('PreInvocation',[]))==1 and len(h.get('Stop',[]))==1 else 'BROKEN')" 2>/dev/null || echo "antigravity: BROKEN/MISSING"
```

🟢 `ok`. 🔴 means Antigravity is not injecting memory or not carrying the last turn into the daily log.
Fix: `python3 .claude/scripts/render_antigravity_hooks.py --vault "$PWD" --platform posix`.

### 4. Are python3 and the model CLI on the PATH

```bash
if command -v python3 >/dev/null 2>&1; then echo "python3: $(python3 -V 2>&1)"; else echo "python3: MISSING"; fi; if command -v claude >/dev/null 2>&1; then echo "claude: present"; elif command -v agy >/dev/null 2>&1; then echo "agy: present"; else echo "model CLI: MISSING"; fi
```

🟢 python3 plus `claude` or `agy` present. 🔴 without python3 the engine does not run at all; if both
model CLIs are missing, the background summarizer stops.
Fix: install python3; add the Claude Code or Antigravity CLI you use to the PATH.

### 4b. Is the model CLI logged in

Being present is not enough. The background summarizer and compiler run through `claude -p`; if the CLI
is installed but logged out, every flush gets `Not logged in` and dies, and **no daily log is created
anywhere**. The engine looks like it is running, `daily/` stays empty: check 6 turns red but the cause
does not show there.
Being logged in to a GUI app does not cover the CLI; the credential stores are separate.
`auth status` does not spend tokens.

```bash
if command -v claude >/dev/null 2>&1; then
  if claude auth status 2>/dev/null | grep -q '"loggedIn": *true'; then echo "session: logged in"; else echo "session: LOGGED OUT"; fi
elif command -v agy >/dev/null 2>&1; then echo "using agy, this check is specific to claude"
else echo "model CLI: MISSING"; fi
```

🟢 `session: logged in`. 🔴 `session: LOGGED OUT`: this is the sneakiest failure.
Fix: **the user must run** `claude auth login` **themselves**; it opens OAuth in the browser. You, as
the agent, cannot do this step. Once login is done, verify with `claude auth status`, open and close
a session, and repeat check 6.

### 5. python3-missing marker

```bash
if [ -f .claude/scripts/.state/python3-missing ]; then echo "marker PRESENT, date: $(head -1 .claude/scripts/.state/python3-missing 2>/dev/null)"; else echo "no marker"; fi
```

🟢 no marker. 🔴 marker present: the hooks could not find python3, so they could not do the JSON escaping.
Fix: install python3, then delete the file: `rm .claude/scripts/.state/python3-missing`.

### 6. Daily log freshness

```bash
f=$(ls -t daily/*.md 2>/dev/null | head -1); if [ -z "$f" ]; then echo "daily: no logs at all"; else m=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f"); n=$(date +%s); echo "daily: $f, written $(( (n - m) / 3600 )) hours ago"; fi
```

🟢 newer than 48 hours. 🟡 between 48 and 96 hours. 🔴 older than 96 hours, or no logs at all.
Fix: end the session and start again, then repeat this check. If it is still empty, go back to checks
1, 2 and 4; the fault is in the flush chain.

### 7. Compile status

```bash
f=".claude/scripts/.state/compile-state.json"; if [ -f "$f" ]; then m=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f"); n=$(date +%s); echo "state: updated $(( (n - m) / 3600 )) hours ago"; python3 -c "import json;d=json.load(open('.claude/scripts/.state/compile-state.json'));print('last_run:',d.get('last_run','none'));print('last_status:',d.get('last_status','none'));print('ingested:',len(d.get('ingested',{})),'logs')" 2>/dev/null || echo "state file corrupt, could not read JSON"; else echo "compile: no state file, no compile has run yet"; fi
```

🟢 `last_run` newer than 48 hours and `last_status` is `ok`. 🟡 no state, but the vault was just set up or
it is not yet 18:00 in the evening. 🔴 `last_status` starts with `fail:` or is older than 48 hours.
Fix: run one round by hand and look at the error: `python3 .claude/scripts/compile.py --dry-run`,
then `python3 .claude/scripts/compile.py`.

### 8. Recent errors in the health records

`health.json` holds one JSON record per line (JSONL). Not every record is a failure: if the
`error` field starts with `warn:`, the engine **resolved the problem itself** (for example
`warn:summary-schema-retried` — the summary's first output did not match the schema, it was retried and
it worked; the daily log was written in full). A check that counts warnings as errors produces a
permanent red on a healthy vault and trains the user to ignore the doctor. Tell the two apart.

```bash
python3 - <<'PYCHK'
import json, os, time
p = ".claude/scripts/.state/health.json"
if not os.path.exists(p):
    print("health: no records"); raise SystemExit(0)
now = time.time(); err = warn = 0
for line in open(p, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    try: r = json.loads(line)
    except ValueError: continue
    yas = int((now - r.get("ts", now)) / 3600)
    e = str(r.get("error", ""))
    if e.startswith("warn:"):
        tur = "WARNING"
        if yas < 48: warn += 1
    else:
        tur = "ERROR"
        if yas < 48: err += 1
    print("%s | %s | %s | %d hours ago" % (tur, r.get("component", "?"), e, yas))
print("summary: %d errors, %d warnings in the last 48 hours" % (err, warn))
PYCHK
```

🟢 no records, or `0 errors` in the last 48 hours (warnings are fine). 🟡 warnings but no errors in the
last 48 hours: the engine recovered by itself; look into it if it keeps repeating. 🔴 at least one `ERROR` in the last 48 hours.
Fix: look at the `component` field. If it is `flush`, the transcript or the claude CLI — check 4b
first; `claude-exit-1` almost always means a logged-out session. If it is `compile`, the model call
is the problem. After reading the record and fixing its cause you may delete the file; the script writes it again.

### 9. Knowledge index size

```bash
if [ -f knowledge/index.md ]; then echo "index: $(wc -l < knowledge/index.md | tr -d ' ') lines"; else echo "index: FILE MISSING"; fi
```

Only the first 150 lines of the index enter the context at session start.
🟢 150 lines or fewer. 🟡 between 151 and 300 lines; the lower rows are no longer injected.
🔴 over 300 lines: time for a summary index.
Fix: group the index under theme headings, collapse old rows into a single summary row,
and leave the detail in the article. If the file is missing entirely, restore the seed file from the repo.

### 10. iCloud conflict files

```bash
find . -name "* 2.*" -not -path "./.git/*" 2>/dev/null | head -20
```

🟢 empty output. 🔴 output present: iCloud kept two copies of the same file, and some of the memory files
may be in the wrong copy.
Fix: compare each listed file with its original (`diff "file.md" "file 2.md"`), move the needed
content into the original, then delete the conflict copy. Do not delete without asking the user.

### 11. Git repository and uncommitted changes

```bash
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then echo "git: present, uncommitted: $(git status --porcelain | wc -l | tr -d ' ') files"; else echo "git: NO REPO"; fi
```

🟢 repo present and fewer than 50 uncommitted files. 🟡 more than 50 piled up. 🔴 no repo, meaning
the memory has no history you can roll back to.
Fix: if there is no repo, `git init` and a first commit. If changes have piled up, commit.

### 12. Version file

```bash
if [ -f .beyin-version ]; then echo "version: $(head -1 .beyin-version)"; else echo "version: FILE MISSING, v1 vault"; fi
```

🟢 `2.3.0`. 🟡 `2.2.0`, `2.1.0`, `2.0.0` or no file: an upgrade is available.
Fix: follow the upgrade path (mode B) in SETUP.md. The upgrade does not touch existing memory
files; it only adds the missing pieces.

### 13. Rules file

```bash
if [ -f "🔮 850-Companion/Kurallar.md" ]; then echo "rules: present, $(wc -l < "🔮 850-Companion/Kurallar.md" | tr -d ' ') lines"; else echo "rules: MISSING"; fi
```

🟢 present. 🟡 missing: the user's corrections are not being made permanent.
Fix: copy the seed `Kurallar.md` file from the repo into `🔮 850-Companion/`.

### 14. Double-active hooks (settings.json + settings.local.json)

```bash
python3 - <<'PYCHK'
import json, os
EV = ("SessionStart", "UserPromptSubmit", "SessionEnd", "PreCompact")
V1 = ("session-start.sh", "prompt-counter.sh", "session-end.sh", "pre-compact.sh")
n = {e: 0 for e in EV}
for f in (".claude/settings.json", ".claude/settings.local.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except FileNotFoundError:
        continue
    except ValueError:
        print("%s: CORRUPT JSON" % f); raise SystemExit(0)
    if not isinstance(d, dict):
        print("%s: not a JSON object" % f); continue
    for ev, ms in (d.get("hooks") or {}).items():
        if ev not in EV: continue
        for m in (ms or []):
            for h in (m.get("hooks") or []):
                if any(b in (h.get("command") or "") for b in V1):
                    n[ev] += 1
for e in EV:
    print("%s: %d" % (e, n[e]))
PYCHK
```

🟢 the count for all four events is exactly `1`. 🔴 any of them `2` or more: on that event the
hooks run twice every time, so every prompt is counted twice and two flushes fire at the end of every
session. `0` means that event is not wired at all.
Fix: delete the brain hook entry in `.claude/settings.local.json`; do not touch unrelated
hooks or other keys such as `env` and `permissions`. The single wiring must stay
in `.claude/settings.json`.

### 15. Backup leftovers in the vault that may carry secrets

```bash
find . -path ./.git -prune -o -type f \( -name "*.yedek" -o -name "*.yedek-*" -o -name "settings.local.json.*" -o -name "*.bak" -o -name "*.orig" \) -print 2>/dev/null | head -10; echo "---"; git ls-files 2>/dev/null | grep -E 'settings\.local\.json|\.yedek|\.env$' || echo "no tracked secret files"
```

🟢 both sections empty. 🔴 if a backup file shows up: these files may be a copy of `settings.local.json`
and carry an API key; if anything shows up in the second section, the secret is already tracked
by git.
Fix: move the backup outside the vault and give it `chmod 600`; if git tracks it,
untrack it with `git rm --cached <file>`, verify the `.gitignore` rule, and
**revoke and rotate** the leaked key at the provider.

### 16. Graph integrity (broken links + orphan notes)

```bash
python3 .claude/scripts/graf_kontrol.py
```

Memory is not a flat pile of files but a **graph**: a note can only be found if there is a link
leading to it. An orphan note sits on disk, but to reach it the agent has to scan the whole vault,
which means it either burns tokens or fails to find it and makes something up. A broken link points to
an address that does not exist on the map. No other check catches either of them.

🟢 0 broken links. 🟡 1–20 broken links. 🔴 more than 20 broken links.
The orphan count alone is not 🔴: drafts, archival and one-off notes are naturally
orphans. The core files the hook injects every session are explicitly exempted by the
scanner; the remaining results are an advisory signal for ease of access.
Fix: open the list with `--tam`. For a broken link, either create the target note or fix the
link; if the target is missing on purpose (such as a `[[wikilink]]` used as an example in a document), leave it.
For an orphan note, link to it from a related parent note or from `Dashboard.md`.

## Report format

After all checks are done, print a single table:

```
| Check | Status | Finding |
| --- | --- | --- |
| Hook files | 🟢 | all four in place and executable |
| settings.json wiring | 🟢 | all four events wired |
| Codex links | 🟢 | router, skill and hook store shared; hooks.json absolute |
| Antigravity links | 🟢 | PreInvocation and Stop adapter registered |
| Recursion guard | 🟢 | present in all |
| python3 and model CLI | 🟢 | python3 3.11.6, agy present |
| Model CLI session | 🟢 | logged in |
| python3-missing marker | 🟢 | no marker |
| Daily log freshness | 🟡 | last log 51 hours ago |
| Compile status | 🔴 | last_status fail:timeout |
| Health records | 🔴 | compile error yesterday |
| Knowledge index | 🟢 | 42 lines |
| iCloud conflicts | 🟢 | clean |
| Git | 🟢 | repo present, 3 files uncommitted |
| Version | 🟢 | 2.3.0 |
| Rules | 🟢 | present, 24 lines |
| Double-active hooks | 🔴 | SessionEnd wired 2 times |
| Secret backup leftovers | 🟢 | clean |
| Graph integrity | 🟡 | 4 broken links, 12 orphan notes |
```

After the table, write one line starting with "Fix:" for each 🔴 row only, and give the command too.
Then a one-sentence verdict, for example: "The brain is up, but the compiler has been stuck for two days; fix that first."
If everything is green, keep the verdict short too: "The brain is healthy, nothing to do."
