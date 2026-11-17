# Code and content projects with Avenox Beyin

`🏰 300-Projects/` is a project **memory area**; it is not a code repository or a media archive. Keep the
project's purpose, decisions, links, current status and next task here. Let the Git repo,
`node_modules`, render outputs and large video files stay outside the vault, in their own folders.

An example of the separation:

```text
~/Documents/AylinOS/🏰 300-Projects/youtube-serisi.md   # context and decisions
~/Developer/youtube-site/                              # the real Git repo
~/Movies/youtube-serisi/                               # raw media and renders
```

## Which folder should the agent be opened in?

- For planning, research, content tracking and long-term memory, open the agent at the vault root.
- For code changes, open the agent in the real Git repo; let that repo's `AGENTS.md`/`CLAUDE.md`
  rules and tests apply.
- If you need to use both areas in one session, add the code repo to the vault session with the
  harness's additional-workspace feature and have the agent read the code repo's own instruction file
  separately. Tell the agent explicitly where the file boundary lies on each side.
- When the work is done, write only the durable outcome to the project note in the vault: the commit/PR link, the
  decision made, the verified status and the next step. Do not copy source code into the vault.

This separation is not a sandbox. Avenox Beyin's compiler produces model changes in a temporary
stage outside the vault and moves back only the permitted Markdown files under `knowledge/`. What the interactive
agent can read and write in the code repo is determined by the permission/sandbox settings of Claude Code, Codex or Antigravity themselves.

## Video and other content projects

For video, the project note can hold the brief, sources, title/thumbnail decisions, publishing status and file
locations. Raw video, audio, project files and the final render stay outside. That way iCloud
sync and Obsidian indexing do not bloat with large binary files; the brain still remembers which file is
where and which decision was made.

## OpenCode status

The automatic startup/flush adapters of v2.3 are for Claude Code, Codex and Google Antigravity.
There is currently no official hook adapter for OpenCode. OpenCode can read the vault Markdown like
ordinary files; but do not assume that an OpenCode session writes to the `daily/` log by itself or that it picks up
memory automatically at startup. Until such support is added, record a durable
summary of OpenCode output in the project note by hand or by passing it through a session of a supported harness.

## The short rule

The vault is the index of truth and decisions; the code repo is the source of the application; the media folder is the home of heavy
files. Let them refer to each other by path and link, and let them not be physically nested
inside one another.
