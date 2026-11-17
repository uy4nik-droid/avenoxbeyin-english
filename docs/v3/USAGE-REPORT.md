# Usage report: is the injected source opened afterwards?

`scripts/evaluate_v3_usage.py` is an in-repo developer tool (#172). It is not in the release package and is not a `beyin.py` command. `evaluate_v3*.py` measure the question "does the right note come up?" with synthetic question sets; this tool looks at the question "in real use, does the agent open, afterwards, the source the hook put into the context?"

```
python3 scripts/evaluate_v3_usage.py --vault /path/to/vault            # JSON, last 14 days
python3 scripts/evaluate_v3_usage.py --vault /path/to/vault --human    # readable table
python3 scripts/evaluate_v3_usage.py --vault /path/to/vault --days 0   # all history
```

## What it reads and what it does not write

- Only Claude Code transcripts: `~/.claude/projects/<folder>/*.jsonl` and, for sub-agents, `<folder>/<session>/subagents/*.jsonl` (the `projects/` under `CLAUDE_CONFIG_DIR` if it is defined). The folder name is derived from the vault path by Claude Code's rule: every UTF-16 unit other than a letter or digit becomes `-`, and Claude Code's digest is appended to names longer than 200 characters. If you started the session outside the vault root, give the folder with `--projects-dir`.
- It reads the files as a line-by-line stream; a huge transcript is not loaded into memory. `--days N` filters by file modification time.
- Read-only, no network, no model. It writes nothing to the vault, the V3 state directory or anywhere else.
- The default output is only counters and ratios. Note paths are printed only with `--names`; check this output before sharing it.

## How it counts

- Context is read only from `attachment.type == "hook_additional_context"` records and from text marked `V3 source-backed context`. In the turn context, the `records[].source` fields of the JSON are used; in the opening (companion) context, the hook's own section labels (`[<source>]`, `[Related source: ...]`, `[Knowledge map: ...]`, `Latest receipt (<source>; ...`) are used. A note name is not searched for in free text.
- A source counts as "opened" if it was opened in the same transcript **after** the injection. Two bounds are given together:
  - `read_grep`: those opened with `Read`, or with a `Grep` whose path is that file (lower bound).
  - `with_shell`: in addition, the file appearing in a Bash/PowerShell command. Commands that look like writes (`git add/commit/mv/rm/stash...`, `sed -i`, `cp/mv/rm/tee`, `Set-Content`/`Out-File`, redirection to a file, Python write calls) are not counted at all. Appearing in a command does not prove it was read; this is the upper bound.
- Breakdowns: by type (`SessionStart` / `UserPromptSubmit`), by order (1st, 2nd, 3rd, 4th+ source), fully printed and truncated companion files on separate lines, the knowledge map and the latest receipt on separate lines.
- The reverse direction: in a transcript that has V3 context, vault notes (`.md`, excluding folders that start with a dot) that were opened although they had not appeared in any injection up to that point. Files the agent opened because the work required it also fall here; this number is also an upper bound.
- Synthetic turns are separated by the hook's own classifier (`beyin_v3_hook.is_synthetic_prompt`, imported, not copied) and do not mix into the main ratios. Sub-agent transcripts are counted in a separate section.
- The transcript format is undocumented and may change with the version. Unrecognized records are skipped and counted under `skipped`; if the number is large, check the format before trusting the report.

## Limit of interpretation

"Not opened" does not mean "did not help": the preview may have been enough. The report points to search quality and noise; it is not a success rate. Only Claude Code transcripts are read; Codex, Antigravity, OpenCode, Hermes and OMP sessions are not counted.
