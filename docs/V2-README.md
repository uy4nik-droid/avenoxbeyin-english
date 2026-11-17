# Historical V2 guide

This document describes V2 behavior. For a new install and the V3 transition, use the [current README](../README.md). The background model compiler described here is not the V3 default. Old links belong to the install of their own era.

# 🧠 avenoxbeyin v2.3: a second brain that doesn't forget to remember

> **The V3 install is being worked on.** You can tell your existing Codex, Claude Code or Antigravity agent
> "Set up my vault by following the [SETUP-V3.md](../SETUP-V3.md) file in this repo."
> Apart from Python, no extra package, service or Mem0 account is needed. The platform verification status
> is listed openly [here](v3/PLATFORM-TESTS.md).


An open-source **second brain** that runs on [Obsidian](https://obsidian.md) plus Claude Code, Codex or Google Antigravity.
A local Markdown vault, persistent memory, zero dependencies,
zero extra cost. You don't manage files, you talk.

**v1's thesis was continuity: when a session opened, the previous session went into context.** It worked, but it rested on a single
fragile assumption: that the model would remember to update the memory files when a session ended. Every time it didn't
remember, that day was lost. **v2's thesis is this: memory is a mechanism, not a request.** Now a hook catches
the session close, summarizes the conversation in the background and writes it under `daily/` as a daily log, and
once a day in the evening a compiler turns those logs into interlinked articles under `knowledge/`. The next
morning the index of that knowledge base goes into context on its own. Nobody has to remember to write anything.

You don't need to watch a video, and there is no install video. Paste the single line below and Claude
Code does the install itself.

---

## Quick start

Run `claude` in a terminal and paste this:

```
Read https://raw.githubusercontent.com/uy4nik-droid/avenoxbeyin-english/main/beyin.md and follow it exactly to build my second brain.
```

This one-line entry first tells platforms apart: macOS/Linux stay on the existing `SETUP.md` path, native
Windows moves to `SETUP-WINDOWS.md` + the PowerShell installer, and WSL uses the POSIX path that stays entirely
inside the same Linux distribution. That way no Bash/macOS commands get run on Windows.

Or on macOS, Linux or WSL, clone the repo directly, three commands:

```bash
git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git avenoxbeyin
cd avenoxbeyin
claude "Read SETUP.md and follow it exactly to set up my second brain from this template."
```

Claude asks a few questions (your name, what you do, the name of your AI partner), sets up the vault, wires the hooks,
and puts a shortcut with a 🧠 icon on your desktop.

If you use Codex, on this POSIX path you can open `codex` in the same repo and have it
carry out `SETUP.md`. The install
generates `AGENTS.md`, `.agents/skills` and an absolute-path `.codex/hooks.json`. On first launch you need to approve the project hooks from Codex's
`/hooks` screen; the trust hashes are not
changed on the user's behalf. Claude Code and Codex read the same router, skill and hook code; there are no two separate copies.

If you use Google Antigravity:

```bash
git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git avenoxbeyin
cd avenoxbeyin
agy -p "Read SETUP-ANTIGRAVITY.md and follow it exactly to set up my second brain."
```

The Antigravity adapter also uses the same `.claude/scripts` engine; it does not create a second copy of `flush.py`, `compile.py` or
the skills. It does not ask for a direct Gemini API key.

### Native Windows (not WSL)

There is a separate install path for native Windows:

```powershell
git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git avenoxbeyin
cd avenoxbeyin
claude "Read SETUP-WINDOWS.md and follow it exactly to set up my second brain."
```

The requirements are checked by **running** them before the install (PowerShell 7,
Python 3, Git, Claude Code), and if even one is missing **nothing is written to disk**.

What was done, which Windows traps were measured, and what is not claimed:
[`docs/WINDOWS-PORT.md`](WINDOWS-PORT.md).

Out of scope: v1 → v2 upgrade, moving over from WSL, running with PowerShell 5.1.
The macOS and Linux paths are unchanged.

### If you already have a v1, v2.0, v2.1 or v2.2 brain

The same command is enough. `SETUP.md` first looks for an existing brain, and if it finds one it switches to upgrade mode and delegates the work to
a single script: `scripts/upgrade.sh`. The upgrade **only adds**: your existing memory
files, Dashboard and notes are not touched. `daily/`, `knowledge/`, scripts and skills
are added, the four hook files are replaced with the new ones, and the `settings.json` hook registration is merged
in a way that can be run again and again.

Three things are good to know up front:

- **The memory folder's name must be `🔮 850-Companion`.** The hooks and scripts read this fixed path. If the folder's name is your partner's name (like `🔮 850-Echo`), the script offers to change it with `git mv`. The contents never change, only the folder name does. If you say no, the upgrade never
  starts and the vault does not get stamped as v2; an honest v1 beats a half-installed v2.
- **The first job is a git snapshot.** If it can't be taken, the upgrade stops and does not continue. The way back is always
  open.
- **The version stamp is written last.** After the hooks, scripts, placeholders, hook count and
  `.gitignore` protection have been verified one by one. If even one gate fails, `.beyin-version` is not
  written.

---

## v1/v2.0/v2.1/v2.2 → v2.3

| | v1 | v2 |
| --- | --- | --- |
| Daily memory | written if the model remembers | written **automatically** when the session closes |
| Hook count | 3 | 4 (`PreCompact` added) |
| Compaction | lost when the conversation is compressed | captured before compression |
| Knowledge base | none | compiled, interlinked articles under `knowledge/` |
| Context at session start | last session + threads | + rules, latest journal, knowledge index, today's log |
| Persistent rules | none | `Kurallar.md`; when you say "don't do it like this", it gets written there |
| Health check | none | `beyin doktor` skill, diagnosis in one table |
| Old history | none | `geçmiş import`: ChatGPT, Claude, Gemini exports |
| Upgrade | none | in place, additive, can be re-run |
| Dependency | bash | bash + python3 (both are on the system) |

---

## Architecture

```
   session ends                    conversation about to be compacted
   (SessionEnd)                         (PreCompact)
        |                                    |
        v                                    v
  session-end.sh                       pre-compact.sh
        |                                    |
        +------------------+-----------------+
                           v
                       flush.py           (claude -p or agy -p)
                  reads the transcript, produces an English summary
                           v
                 daily/YYYY-MM-DD.md      <-- the machine writes, not you
                           |
        (after 18:00, once a day, if a log changed)
                           v
                      compile.py          (claude -p or agy -p)
                           v
   knowledge/concepts/*.md + knowledge/connections/*.md + knowledge/index.md
                           |
                           v
                   session-start.sh
        injects the index + today's log + memory into the next session
```

The writing side belongs to the machine, the relationship layer belongs to you: your partner still updates the `Last-Session.md` and `Threads.md`
files by hand. The machine layer does not replace it, it fills in underneath.

## What you get

```
{Name}OS/
├── 📥 000-Inbox/Dump/        # raw capture
├── 🎯 100-Command-Center/    # Dashboard
├── 🏰 300-Projects/          # one folder per project
├── 🧠 500-Knowledge/         # notes a human writes
├── 🛠️ 600-Arsenal/           # tools, people, resources
├── 🔮 850-Companion/         # the partner's persistent memory (+ Kurallar.md)
├── daily/                    # the machine writes: daily logs
├── knowledge/                # the machine compiles: articles + connections + index
├── 📦 900-Archive/
├── 📋 Templates/
└── .claude/                  # hooks, scripts, skills (the continuity engine)
```

- **An AI partner you name yourself.** The default language is English.
- **A continuity engine.** Four zero-dependency hooks put memory into context on every launch and write the session to disk on every
  close.
- **File-based memory.** No API key, no paid service, everything is on your disk.
- **Local memory is the default.** No Mem0 account or API key is needed. Third-party
  memory services are added only by explicit choice; the base system does not depend on them.
- **A one-click launcher.** On macOS, an app with a 🧠 icon on the desktop opens the vault instantly. On Linux, a `.desktop` shortcut
  is written instead (not tested).

## Cost, honestly

There is no extra API bill; the background summarizer and compiler use a small share of the existing quota of the Claude Code or
Antigravity account you already use.

## Requirements

Required, on every platform: [Claude Code](https://claude.com/claude-code) **or** the Google
Antigravity CLI, [Obsidian](https://obsidian.md) and Python 3 (`python3` on macOS/Linux; a working
`python` or `python3` on native Windows). Python is not optional: both the daily log and the nightly compile
run on top of it.

| Platform | Status | What works, what doesn't |
| --- | --- | --- |
| macOS | **tested** | everything: hooks, `daily/`, `knowledge/`, the 🧠 desktop shortcut |
| Linux | **not tested** | the install branches on `uname`: the Homebrew, Obsidian cask and macOS `.app` steps are skipped, and an XDG `.desktop` shortcut is written instead. The vault, hooks and scripts are written to be portable but have not been verified on a real Linux desktop. If you try it, open an issue. |
| Windows | WSL, **or** native Windows | The one-line `beyin.md` entry tells the two paths apart. For native Windows, [`SETUP-WINDOWS.md`](../SETUP-WINDOWS.md). On WSL the engine and the vault stay in the same Linux distribution, on the Linux filesystem; mixed use with Windows Obsidian is not considered verified. See [`docs/WINDOWS-PORT.md`](WINDOWS-PORT.md). |

The desktop shortcut uses `osacompile` and AppKit on macOS, and neither exists on Linux. The vault
itself is plain Markdown, so it opens anywhere; the only platform verified for the whole install flow
right now is macOS.

For the boundary between code repos, video files and `🏰 300-Projects/`, see the
[`docs/PROJECT-WORKFLOW.md`](PROJECT-WORKFLOW.md) guide. OpenCode's current support
boundary is stated openly there too.

## If something goes wrong

In the vault folder, open the agent you use and type `beyin doktor`. The hooks, scripts, python3, model CLI,
daily log freshness, last compile status, iCloud conflict files and git status come back in one table,
and under every red row it gives the fix command.

---

## Credits

The knowledge-compilation architecture is based on Andrej Karpathy's LLM knowledge base pattern:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

The rest was extracted from the system [Avenox](https://avenox.lol) uses daily, stripped of personal data and
generalized for everyone.

## License

MIT, see the [LICENSE](../LICENSE) file. PRs are open.

---

## In English (short version)

**avenoxbeyin** is an open-source AI second brain: an Obsidian vault driven by Claude Code,
Codex, or Google Antigravity, with
memory that survives across sessions. v1 gave you continuity but depended on the model remembering
to write its memory files. v2's thesis is that **memory must be a mechanism, not a discipline**: a
`SessionEnd` and a `PreCompact` hook flush every conversation into `daily/` logs automatically via
a small background Haiku call, and once a day a Sonnet compile pass turns those logs into linked
articles under `knowledge/`. The next session starts with that knowledge index already in context.

On macOS, Linux, or WSL, install with `git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git avenoxbeyin && cd
avenoxbeyin && claude "Read SETUP.md and follow it exactly to set up my second brain from this
template."` Codex can follow the same `SETUP.md`; its project hooks are rendered with absolute
paths and require one-time approval in `/hooks`. On native Windows, use the same clone but ask
Claude Code to read `SETUP-WINDOWS.md`; do not run the Bash installer. Already running v1 or v2.0?
The same command detects it and hands the work to one committed script, `scripts/upgrade.sh`:
additive only, your memory files are never touched, the settings merge is idempotent, and it takes
a **verified** git snapshot before it changes anything. Two things it will ask you about, and stop
for if you say no: renaming the memory folder to the fixed `🔮 850-Companion` path (a `git mv`, the
contents never move), and removing v1 hook wiring left behind in `settings.local.json` so hooks
stop firing twice. The `.beyin-version` stamp is the last write of all, only after every gate
passes.

Platform honesty: macOS is the tested POSIX path. The installer branches on `uname` and writes an
XDG `.desktop` launcher instead of a macOS app on Linux, but that path has not been verified on a
real Linux desktop. Native Windows has its own PowerShell installer and CI suite; the generated
Codex wiring is regression-tested, but a live native-Windows Codex session has not yet been
claimed as verified.

No extra API bill: the engine uses your existing Claude Code or Antigravity login through
`claude -p` or `agy -p`. No direct model API keys are required. Knowledge-compilation architecture credit:
Andrej Karpathy's LLM knowledge base pattern,
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f. MIT licensed.

## V3 foundation preview

The V3 development foundation is separate and optional, under [docs/v3/QUICKSTART.md](v3/QUICKSTART.md).
It offers source-referenced search, task revisions and result records with local SQLite;
no Mem0 or model call is needed. This preview does not automatically change the existing V2 hook/installer
flow. Accuracy scenarios and measurement limits:
[SEMANTIC-TEST-CONTRACT.md](v3/SEMANTIC-TEST-CONTRACT.md).
