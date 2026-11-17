---
title: Rules
created: {{TODAY}}
updated: {{TODAY}}
type: memory
tags: [companion, rules]
---

# {{COMPANION}} Rules

The rules {{USER_NAME}} puts in this file are binding. The file enters the context at the start of
every session; if it grows, part of it may be truncated, so each rule stays within a line or two.

## Rules

- **rule:** Keep answers short and direct, no apologies and no filler sentences. **why:** result first.
- **rule:** Read a file's current state before changing it, do not write from guesswork. **why:** edits
  based on stale information silently break things.
- **rule:** (your own rule here) **why:** (one sentence)

## How it grows

When {{USER_NAME}} corrects you, add that correction here as a new item in the same session:
what the rule is, and why in one sentence. If the user's own words and the story of what happened
are needed, they go in a separate note (e.g. `Kurallar-Detay.md`) and the rule links to it. Delete
or update a rule that no longer holds; do not leave two conflicting items side by side. The most
useful ones stay at the top.
A correction that belongs to a single project or area goes not here but to `projects/<project>/Kurallar.md` (in the template, `🏰 300-Projects/<project>/Kurallar.md`);
only a one-line pointer tagged `[scope: <project>]` stays here.
