# Kiro (IDE 1.x and CLI V3)

The V3 installer in this source version sets up a project-level connection inside the
vault for Kiro. Instead of old ZIP packages that have no Kiro support, use this source
checkout or a newer package that includes the Kiro adapter. The installer does not
install a Kiro account or the program.

## Setup

Choose the vault folder and run from the repo root:

```sh
python3 scripts/install_v3.py --vault "/full/path/Beynim"
python3 "/full/path/Beynim/beyin.py" doctor --human
```

On Windows use `py -3` instead of `python3`. The installer writes:

- `.kiro/hooks/beyin-v3.json`: four commands in Kiro's `v1` project hook format. It
  does not touch other `.kiro/hooks/*.json` files.
- `.kiro/skills/{beyin,beyin-doktor,beyin-guncelle,beyin-kontrol}/SKILL.md`: starter
  skills kept in sync with `.agents/skills`.
- A managed Beyin block in `AGENTS.md` at the vault root. Kiro reads this file
  directly; a separate `.kiro/steering/` copy is not needed.

In Kiro IDE, open the vault folder, review the Beyin hooks in the Agent Hooks panel and
start a new session. In Kiro CLI V3, open a new session from the vault folder and review
the active connections with `/hooks`. Grant Kiro's normal folder, command and hook
permissions after reviewing them; the installer does not create a permission record or
an approval. Create a trial note that contains no private data, run `beyin.py sync`, and
in a new session ask for the information back only from the automatic hook context. If
this test fails, check the source directly with `beyin.py doctor` and
`beyin.py context "topic" --harness kiro`.

## Hook behavior and limits

`SessionStart` brings the opening context and `UserPromptSubmit` brings the relevant
sources; `PostToolUse` creates an edit checkpoint in Kiro's `write` tool category.
`Stop` records the end of the turn. `SessionEnd` exists only in CLI V3, so it is not
used in the shared IDE/CLI setup; syncing continues with `Stop`. Kiro has no documented
`PreCompact` event. File changes made through shell commands do not trigger the `write`
match for `PostToolUse`; the next prompt or `beyin.py sync` refreshes the source.

Kiro adds the stdout of a successful command hook to the context as plain text. The
installed `beyin_v3_kiro.py` adapter extracts only the text from the shared Python
hook's JSON result; it writes nothing for empty events. The hook does not call a model
and does not archive the private chat transcript. There is no service that runs
continuously while the client is closed.

Kiro's old IDE 0.x `.kiro.hook` and CLI 2.x profile hook formats are not the target of
this setup. Custom Kiro agent profiles may not load steering and skill sources
automatically; if you use such a profile, explicitly add
`skill://.kiro/skills/*/SKILL.md` and, if needed, `file://AGENTS.md` to your own
`resources` setting. User skills with the same name are not silently overwritten; the
conflict shows up in `doctor`.

Sources: [Kiro Hooks](https://kiro.dev/docs/hooks/),
[hook events](https://kiro.dev/docs/hooks/types/),
[hook output](https://kiro.dev/docs/hooks/actions/),
[AGENTS.md steering](https://kiro.dev/docs/steering/),
[skills](https://kiro.dev/docs/skills/).
