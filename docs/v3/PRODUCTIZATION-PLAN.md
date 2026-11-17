# V3 user package and update plan

16 September 2026. The user package, updater and migration code in the plan below have been implemented. The original design text is kept below for comparison; phrases such as "proposed" or "does not exist yet" describe the moment of the design.

## Completion status

- Three core skills are distributed: beyin, beyin-doktor, beyin-guncelle.
- The installed `beyin.py`: doctor, runtime commands, update --check, update, recover, rollback. A custom runtime path is preserved.
- ZIP builder: version, schema/runtime schema, minimum Python, file SHA256 and recognized legacy hashes. Git or pip is not required.
- Updater: stable official release discovery, local ZIP, synthetic runtime pre-check, managed-file conflict check, backup/journal/lock, version written last, no-op on a repeated call.
- Rollback including the first V2 install; rolling back a clean install is reported as `uninstalled`. User notes are not deleted.
- V2 writer migration: active/customized writer blockers, an inert shim on recognized stock runners, a source/state preservation check and a migration record.
- Deterministic daily/knowledge link views for new source-linked results; the active agent skill flow in place of the automatic model compiler.
- Clickable update launchers suited to the local operating system are bound to the same updater.

In the last platform round, on Windows/macOS/Ubuntu × Python 3.11/3.13: 6/6 jobs, and 114 tests passed in each. The release package is distributed as V3.0.0. The user flow is in the [README](../../README.md), the command contract in [UPDATE.md](UPDATE.md), current evidence in [PLATFORM-TESTS.md](PLATFORM-TESTS.md) and the [client scope](LIVE-CLIENTS.md).

## Original design record

## Verified current state

The V3 runtime and three client adapters are ready. Native CI Windows/macOS/Ubuntu × Python3.11/3.13:6/6, each job 62 V3 tests + semantic evaluation. Real model sessions were verified separately on macOS. The candidate in the code repository has not yet replaced the standard V2 release.

install_v3.py was applied to a clean synthetic vault: installed,5 Python modules,0 SKILL.md, no .beyin-version, no versioned update command. The local installation manifest contains only the files/commands fields. The current template has the V2 beyin-doktor and gecmis-import; the V3 installer does not distribute them. The V2 doctor checks Bash/old-hook paths, so it must not be copied to V3 verbatim.

V2 upgrade.sh provides check/apply/finalize, backup and version stamp flow; the target is 2.3.0 and Bash-based. The V3 installer provides the infrastructure for placing new code, preserving user settings and rollback, but version discovery/download, V2 state migration, versioned upgrade continuation after an interruption and release management are missing.

V2 is already local by default and does not require Mem0. V2's flush→daily→compiler→knowledge pipeline is not an automatic equivalent of the V3 source/task/receipt index. The migration must be designed without silently losing users' existing daily, companion and compile behavior.

## Minimal package

Three core skills: beyin (finding sources, writing notes/tasks, revision, receipt and end-of-day summary), beyin-doktor (real worker/client evidence, freshness/conflict, platform-appropriate commands), beyin-guncelle (calling the single updater tool and explaining the result). These are .agents/skills entries managed by the system; Claude and Antigravity see the same contents. Selected user skills are preserved. If a user skill has the same name, there is no silent overwrite; an explicit conflict or a different system name is used. User customizations are kept separately.

AGENTS.md directs a new user to these skills. At the end of setup, three checks: find a synthetic note again in the next session, change a task and read it back, discover the skill in all three clients. A single short health report shows the results. Importing past chats stays optional and separate.

## A single update mechanism

The proposed entry: `python beyin.py update` inside the vault (Windows: `py -3 beyin.py update`). `doctor`, `update --check` and `rollback` are under the same entry. These are not yet existing commands. When the user says "update my brain" ('beynimi güncelle') to the agent, it calls the same tool; the agent does not redesign the update with free-form file copy commands.

The release package is fetched with the standard library from the official GitHub HTTPS source; Git/pip/a new account is not required. It contains a fixed release version, a file SHA256 list, the minimum runtime/schema version and migration IDs. The checksum verifies package integrity; source identity relies on the verified official distribution address. Stable is the default; preview is an explicit choice. It does not update itself from a moving development branch.

Flow: detect the version→show the plan→local backup/journal→verify the package in a temporary area→change only permitted system files→migration→health and content preservation check→write the successful version record last. On an interruption it does not present a half installation as successful; there is rolling back to the previous good version or resuming the operation. A second identical update is harmless and has no effect. Concurrent updaters are separated by a lock; intersecting writes are not applied until an active old worker has finished.

User notes, the companion personality, journals, knowledge, user skills, private settings and credentials are not files the updater may change. A user change in a system file becomes visible through a three-way comparison; apart from supported settings merging, the conflict is preserved. Database migration is tied to the version stamp, idempotent and backed up. A record boundary is kept in the old handler/state migration; old days are not reprocessed, and two summarizers do not write the same event.

If a hook definition changes, the client's required trust review is stated openly to the user; trust records are not fabricated. So a routine update becomes a single command, and zero interaction is not promised for every possible version. Clickable macOS/Windows/Linux shortcuts can be a thin layer that calls the same command; the updater is verified first.

## Acceptance scenarios to fix before implementation

1. Empty vault: the three core skills are actually installed and discovered; the ready first note/task/receipt flow completes.
2. Standard V2.3: source content hashes are preserved; the old daily/knowledge/companion are read; the new and old writers do not run together.
3. Customized V2: the user's hook, skill and settings are preserved; a managed-file conflict is visible, and the version is not marked successful.
4. V3→V3 minor version: updated with the same command; the second call is a no-op; rollback restores the previous code/schema.
5. Download interrupted, corrupt package, interruption between copies, insufficient permission and parallel update: no data loss and no false success occurs.
6. Windows/macOS/Linux: install+upgrade+rollback work, including Unicode/space paths, CRLF/LF, a limited PATH and no symlink permission.
7. After the update, a real Codex/Claude/Antigravity session uses the existing note and skill; for Codex Desktop a short cold-session delivery check is also done.

## Proposed order

First the core skill package and first use; then the version manifest/shared update tool; then the V2 migration and the interruption/rollback matrix; the shortcuts and the stable release last. Existing CI successes do not mean these new acceptance scenarios have passed.

Desktop and CLI share the same Codex configuration layers; the same runtime is expected to work. A separate Desktop check is not about building a new engine; it is a short integration check that verifies real delivery of the opened workspace/trust/session events. Sources: https://learn.chatgpt.com/guides/best-practices and https://learn.chatgpt.com/docs/hooks .
