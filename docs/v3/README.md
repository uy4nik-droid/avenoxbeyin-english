# Second Brain V3

For selected project sessions outside the vault: [optional global bridge](GLOBAL-BRIDGE.md).

In V3, Markdown is the source and SQLite is the local index; Codex/Claude Code/Antigravity, [Hermes Agent](HERMES.md), [OpenCode](OPENCODE.md), [OMP](OMP.md), [Kiro](KIRO.md) and [Pi](PI.md) are clients that connect to the same engine. No extra Python packages are needed beyond Python 3.11+. In the default flow, Mem0, an API key, a daemon or a separate server is not installed. The [Jev advisor](JEV.md) is optional and off by default; unless it is turned on with `beyin.py jev`, it does not change the normal search and hook flow. The same advisor can also use a separately installed local Laya server, only in shadow mode, for measurement (`jev shadow --provider laya`).

[Getting started for new users](../../README.md) · [Setup with an agent](../../SETUP-V3.md) · [Update/rollback](UPDATE.md) · [Multiple machines](MULTI-MACHINE.md) · [Vault backup](BACKUP.md) · [Source schema](MARKDOWN.md) · [Runtime](RUNTIME.md)

[Comparing query changes and measuring on your own vault](QUERY-EXPERIMENTS.md).

For developers: [inventory of source and distribution boundaries](MODULE-BOUNDARIES.md).

Third-party [community tools](../COMMUNITY-TOOLS.md): not supported or reviewed by the project.

## User package

The installer distributes the shared engine, the `beyin`, `beyin-doktor`, `beyin-guncelle`, `beyin-kontrol` skills, the installed `beyin.py` entry point and an update shortcut suited to the operating system. The package can be unpacked as a ZIP and used; Git is not required. The installed vault works independently of the source repo folder.

The [latest stable release](https://github.com/uy4nik-droid/avenoxbeyin-english/releases/latest) and the `beyin-v3-X.Y.Z.zip` package in it are the stable distribution point. The V3.13.0 release gate covers the full offline test suite and 10 development and 6 holdout semantic scenarios; CI verifies the same package on Windows, macOS and Linux.

## Behavior

- Markdown additions, edits, deletions and renames merge into the index. A task metadata update uses an effective revision and source hash check; the body is preserved.
- Short lifecycle hooks write to a persistent metadata queue. Work starts when needed; there is no service that runs continuously while the clients are closed.
- A source-linked receipt gives the same result on a retry. The earlier result is found in the next session as a historical claim; the raw chat is not turned into verified information.
- New results appear by default under `daily/v3/` and `knowledge/v3/outcomes.md` with receipt links. With `preferences --daily-layout flat`, journals can be shown in a single list under `daily/`; details are in [daily receipt layout](PREFERENCES.md#daily-receipt-layout). Because the receipt file name is an identifier, it stays a hash; to hide it in the Obsidian graph, see [Obsidian graph and receipt files](PREFERENCES.md#obsidian-graph-and-receipt-files).
- The shared skill sources are in `.agents/skills`. Claude and Kiro reach their own project copies; personal skill conflicts are not hidden.
- The updater uses only the official stable release or an explicitly given local package. Managed-file backups, an interruption journal, checksums and runtime pre-checks are applied; the successful version record is written last.

### Notes to look at again

`python beyin.py triage --human` (and its JSON output) reports notes whose `review_at`
date has arrived in the `review` section, starting from the oldest date. This is
information only: it does not create a task, change the note or promote it. The JSON
shows at most 20 sources, the human output the first 5; the total count is given
separately.

Triage does not run `sync` automatically. Only trusted public/internal notes that are
in the index and whose source hash is still the same are counted; private, retired,
rejected or invalidated-by-another-note sources are left out. Changed/unreadable sources
are indicated with `stale_count`; for a current count of new or modified notes, run
`python beyin.py sync` first. Empty or template dates are skipped; invalid dates are
counted separately. No new line or automatic reminder is added to session start;
`doctor` keeps its existing diagnostic behavior.

## V2 migration

The [V2 migration guide](MIGRATION.md) explains the preservation of old sources and the writer migration. The recognized V2 summarizer/compiler is taken out of service. Distilling information with a model is now done deliberately by the active agent through the `beyin` skill; the deterministic views do not make up information in its place. Customized or external old jobs are evaluated separately.

The last system operation, including the first install/migration, can be undone with `rollback`; new user notes stay. `recover` completes a half-finished operation. [Commands and limits](UPDATE.md).

## Verification limit

[Platform tests](PLATFORM-TESTS.md) and [real client sessions](LIVE-CLIENTS.md) are separate evidence. The runtime's earlier native CI success does not replace the final CI or release evidence of the new updater package. A Codex CLI check also does not replace a Codex Desktop cold-session check.

The pre-fixed [semantic contract](SEMANTIC-TEST-CONTRACT.md) is a small, synthetic source-finding/state test. The engine uses word-based search; no success with embeddings or general natural-language understanding is claimed. There is no coding to the fixture; development and holdout results are recorded separately. [Baseline comparison](BASELINE.md).

A developer tool that counts, read-only and from Claude Code transcripts, whether the sources the hook injected are opened afterwards in real use: [usage report](USAGE-REPORT.md). It is not in the release package.

## Technical and historical record

[Productization status](PRODUCTIZATION-PLAN.md) · [Command details](QUICKSTART.md) · [Serai patterns](SERAI-PATTERNS.md).

The first public base examined was `2e074cc`. The [public architecture](public-architecture.md), [local architecture](local-runtime-architecture.md), [parity/migration assessment](parity-and-migration.md) and [issue reviews](issue-validation.md) are design history; they are not used in place of the current implementation.
