# Yakala: Codex `apply_patch` read boundary and Windows compatibility

Research and Linux measurement: **19 October 2026 UTC**. Related upstream PR: [#384](https://github.com/avenoxai/avenoxbeyin/pull/384).

## Result and the change made

Blocking writes from the `apply_patch` tool does not, on its own, block guess
verification against existing file content. Under `-a never -s read-only`, a correct
patch context proceeds as far as the write policy, while a wrong context fails at
verification. This distinction was reproduced with the current stable Codex
**0.163.0** as well.

The solution measured on Linux uses Codex's documented **named permission profile**
to restrict the filesystem reads that patch verification uses as well. On Linux and
macOS, Yakala (capture) generates a fresh `beyin_yakala_<32 hex characters>` name for
every command and passes these two `-c` settings; native macOS verification has not
been done yet:

```text
permissions.beyin_yakala_<random>.filesystem={":root"="deny"}
default_permissions="beyin_yakala_<random>"
```

The profile has no other filesystem entry and no `extends` ancestor. No extra read
permission is added for `:minimal`, the Python directory, the vault or the temporary
directory. `-s read-only` is not passed to the client; this legacy selector is
replaced by the named profile. The user's existing config file is not modified. The
random name prevents a narrower `read`/`write` entry from a user profile of the same
name from being inherited through deep merging. That 128 bits of randomness make a
collision practically negligible is a probability assessment; it is not uniqueness
proven by scanning all system states.

The POSIX preflight rejects the job without starting it if `allowed_permission_profiles`,
`allowed_sandbox_modes` or `remote_sandbox_config` is present. `--strict-config` is not
enough, because Codex 0.163.0 could silently fall back to the managed default instead
of a random profile that is not on the allow list [S7]. `CODEX_HOME` (default
`~/.codex`), `/etc/codex`, project/parent-directory configs and profile fragments are
scanned; permission selectors in managed files are rejected too. If a config is
unreadable or corrupt, a cloud management cache is present, or a macOS management
preference exists, a safe profile is not assumed. In both views the card becomes
`onay-bekliyor` with an ASCII Turkish description; the Windows `-s read-only` path is
unchanged.

**Windows uses a separate compatibility path: `-s read-only`.** In the user's real
Windows 11 / Codex 0.155.1 trial on 19 October 2026, the previous fix (`dc2a1bc2`,
fork #9) stopped while loading `AGENTS.md`; the model event file stayed empty. The
Windows `elevated` sandbox requires root read permission. For this reason the
root-deny profile is not passed to the Windows command; `gizli` and `pencere` use the
same read-only selector. The write block and the other tool gates are kept, but **on
Windows the `apply_patch` content-guessing channel is not considered closed**. The
native Windows startup of the new branch has not been measured yet; the compatibility
section below explains this distinction [S12-S14].

`--strict-config` turns unknown top-level settings into errors. Unsupported flags and
old/pre-release versions are already rejected in the preflight. The oldest binary
measurement is **0.155.1**, so the lower version bound did not change. The general
shell, image reading, subagent, app, plugin and other MCP gates keep the shutdown
checks from the earlier job baseline.

This profile is documented as **beta**. A setting being accepted does not guarantee
the same security behavior in every future version. For this reason an optional
regression that can be repeated with the real binary was also added. The Linux result
must not be generalized to native Windows and macOS until the measurements below are
completed.

## Why this solution?

In the 0.163.0 source code, `ApplyPatchHandler::handle_call` passes the selected
environment's `FileSystemSandboxContext` to the `verify_apply_patch_args` call.
Context matching in `Update`/`Move` operations and reading the old content in a
`Delete` operation happen through this filesystem. For `Add`, the write decision is
made without reading existing content. So a profile that denies both reads and writes
is applied before the content check that would vary with the guess result. The source
path is in links [S4] and [S5] below.

The permission compiler starts a custom profile with an empty restricted filesystem
policy; it does not add vault or `:minimal` reads on its own [S6]. Because a more
specific permission can reopen a broad root deny, it is not sufficient to add a bare
root deny to an existing fixed-name profile [S2].

The official permissions page warns against mixing old sandbox settings with new
profiles [S2]. In the three versions examined, source and real-binary measurement also
confirmed a more specific precedence rule: an explicit `default_permissions` in
`SessionFlags` overrides a legacy `sandbox_mode` setting in a loaded file, while a
real `--sandbox`/`-s` command-line selector disables the profile [S7]. The regression's
temporary config file deliberately contains `sandbox_mode="workspace-write"`. A second
test also loads `sandbox_mode="read-only"` from `fixture_legacy.config.toml` through
the supported `--profile fixture_legacy` selector. In both, all native file
read/write attempts are rejected. The Yakala production command does not use this
extra `--profile` flag; the second test forces Codex's layer precedence. This detail
is stated only for the examined versions, with source and run evidence.

### Alternatives examined

| Path | Evidence and decision |
| --- | --- |
| `--disable apply_patch_freeform` | `removed` in the 0.155.1 and 0.163.0 feature list/source. With the 0.163.0 binary the same content-guessing distinction occurred despite the flag. Not used. |
| `read-only` alone and `never` | Writes were rejected; correct/wrong context errors stayed different. This is the cause of the finding. |
| Rejecting `apply_patch` in `PreToolUse` | The supported hook can run before handler verification. However, on an ordinary hook error/timeout/corrupt output the call can proceed; not chosen as the sole security boundary [S8, S9]. |
| `apply_patch_tool_type=null` via `model_catalog_json` | In a temporary-catalog trial with the official 0.163.0 binary it removed the tool; a forced call became `unsupported custom tool call`. This is a broader intervention that requires managing the model catalog as a whole. The filesystem profile, which does not change model features, was chosen [S3, S10]. |
| Tool ban in the model prompt | Does not provide a tool-level boundary. Not counted as a security solution. |

No current standalone CLI switch that disables only the `apply_patch` tool was found;
this result is limited to the examined config schema, CLI help text, feature list and
registration code. The POSIX profile closes the channel on Linux; on the Windows
read-only compatibility path this finding stays open. No issue was opened in the Codex
repository.

## Test with the real binary

`tests/v3_yakala_codex_boundary_test.py` uses the Python stdlib. Codex is not a
dependency of the project; the normal CI test is skipped unless `BEYIN_CODEX_BINARY`
is given. The binary is not downloaded automatically. A known official binary is
selected explicitly:

```bash
BEYIN_CODEX_BINARY=/absolute/path/to/codex \
BEYIN_CODEX_EVIDENCE=/absolute/path/to/codex-boundary.json \
python3 -m unittest tests.v3_yakala_codex_boundary_test -v
```

These two native regressions test the POSIX root-deny contract. On Windows they are
skipped with an explicit platform reason; the skip cannot be counted as success of the
Windows startup or of read isolation. Windows acceptance trials are listed separately
below.

The test creates a fresh temporary `CODEX_HOME`, vault, state and harmless notes. The
Responses protocol is mocked on `127.0.0.1` only; no model account, API key or
external model service is used. The outputs come from the real Codex binary; the fake
server only determines the model's tool calls. The `gpt-5.5` name chosen as input is
there to test these versions' direct custom-tool transport; the capability, price or
quality of a hosted model is not measured.

In each of the two end-to-end regressions, for every version, the following were
verified:

- **28 patch calls:** Update and Move with correct/wrong context for four path writes
  (relative/absolute, inside/outside the vault), Delete, and Add to an existing and a
  new file. Correct/wrong pairs on the same path/operation produced byte-identical
  output. Update/Move and Delete were rejected with a file read error; Add was
  rejected by the write policy. It is not claimed that a single error text was used
  across operation types.
- The SHA-256 values of the four starting files were preserved. No new or moved
  target was created; no patch output carried the synthetic correct/wrong content line.
- **5 real MCP calls:** a normal note and `AGENTS.md` were read; a private note was not
  read; a new result note was written; `complete` was accepted and a manifest was
  created. A real stdio MCP process that verifies Yakala's job/PID generation ran.
- **Normal memory startup:** the single synthetic `SessionStart` hook produced by the
  test gets a trust record for its own hash seen through `hooks/list`. The trust-skip
  flag is not passed. The hook adds the context it reads from the file to the first
  model request; native patch reads are still rejected in the same session.
- An unknown top-level config key is rejected under `--strict-config` before any
  model request is created. The config hash is the same after the run.

The measurement scope for `--strict-config` is the unknown top-level key. The
research also showed that a nested unknown field such as
`permissions.<other profile>.unknown_field` is not always rejected in these three
versions. This flag is not presented on its own as general profile-validation
evidence. The effectiveness of the root deny was tested directly with patch calls;
a missing/empty filesystem table in a custom profile also starts restricted [S2, S6].

| Binary | Official release time (UTC) | Linux result |
| --- | --- | --- |
| 0.155.1 | 2026-09-18 20:03:04 | 2/2 real CLI regressions passed; per test 28 patches + 5 MCP + hook |
| 0.160.0 | 2026-10-01 20:19:13 | 2/2 real CLI regressions passed; per test 28 patches + 5 MCP + hook |
| 0.163.0 | 2026-10-15 21:30:38 | 2/2 real CLI regressions passed; per test 28 patches + 5 MCP + hook |
| 0.164.0-alpha.3 | 2026-10-17 04:03:25 | Source comparison only; the real binary was not run, Yakala rejects pre-releases |

After the Windows compatibility change, on **19 October 2026 UTC**, the same six
Linux CLI tests passed again as `nobody` / UID 65534: two tests per version, taking
**25.313**, **19.736** and **19.640 seconds** respectively. In total 168 patches, 30
real MCP calls and six memory hooks were audited; config hashes were preserved.

For the updated command expectations and the existing Codex preflights, **20 targeted
tests, 20 passes / 0.086 seconds** were measured. The platform/view matrix included in
this run failed on two Windows sub-checks with the old code (**1 test / 2 fail,
0.020 seconds**); after the fix it became **1 test / 1 pass, 0.025 seconds**. The
matrix also ran on Linux as UID 65534. Each check in the `subTest` loops is not
counted as a separate test; these numbers do not replace the full V3 combined test.

### Binary integrity

The official `codex-x86_64-unknown-linux-musl.tar.gz` assets were downloaded; the
SHA-256 values below matched the `digest` field in the GitHub release API.

```text
0.155.1 a0ef8b2debc3bf747e07b1a039354de31300ac0dcc2276498ba281470b5d9115
0.160.0 306865417d4ee7a927785852910a527f41e1e159add390ac5ae3accb67d44a13
0.163.0 beb339e8ecd9ba057a6bb2dc81ad8ca474812edfbf0fc5056ca818797648dde4
```

## Windows compatibility and remaining native verification

In the source review of 19 October 2026 UTC, the same `elevated` precondition was
found in Codex **0.155.1**, **0.163.0**, **0.164.0-alpha.3** and `main` **89461ea6**:
``elevated Windows sandbox requires effective `:root` read access`` [S13, S15].
The startup error reported by the user matches this condition; the Windows sandbox
was not run on Linux. The user reported that, on the same machine, the older `69ac79c`
branch with `-s read-only` ended as `completed` in both views. This is the user's
measurement of the previous branch; it is not an acceptance measurement of the fixed
branch.

| Option | Source and decision |
| --- | --- |
| Root-deny on Windows | Does not satisfy the `elevated` root read permission precondition; the cause of the reported real startup error. Removed from the Windows command. |
| `:root=read` and exact-path deny for vault/home/state | The `elevated` source test accepts this kind of subpath deny. `unelevated` does not support deny-read. A restricted profile does AGENTS discovery/reading from inside the sandbox; a permission/metadata error can stop startup. That it would run without opening the required startup/runtime paths was not measured natively; opening those paths, and unlisted paths, also does not give a general oracle closure. Not chosen as the default [S12-S14]. |
| MXC | The current documentation requires a compatible Windows 11 device/policy; the single-command MXC trial is for 0.162.0+. `prefer_mxc` can fall back to the legacy selection if there is no support. It was not substituted for 0.155.1 support; root-deny success under MXC was not measured [S12]. |
| Windows `-s read-only` | Chosen for consistency with the previously working Windows flow. Native write permission is not granted; the content-guessing boundary stays open. |
| Linux/macOS root-deny | The code path is kept. The real-binary evidence belongs to Linux; it is not a macOS Seatbelt measurement. |

The platform choice is made while the command is being prepared; there is no
automatic retry that widens permissions after a startup error. The user's
`windows.sandbox`, `prefer_mxc`, project/hook trust and config files are not
modified. The general shell, image reading, subagent, app/plugin and other MCP
shutdown checks, `-a never`, `--strict-config`, the job's network choice and the
trusted Yakala MCP bridge are kept.

Remaining acceptance measurements:

1. **Windows:** install the current branch and, with the real Codex 0.155.1, use first
   `gizli`, then `pencere`, `ag: kisitli` and a harmless card. Verify that the
   `AGENTS.md` startup, the normal trusted memory hooks and the
   `read_note → write_note → complete → receipt → Last-Session` chain are completed.
   Record a separate job ID and the real result for the two views; this document does
   not yet claim success.
2. **Windows:** record the effective tool/config state together with the CLI version,
   Windows version, sandbox type and filesystem information. Measure on a harmless
   file that `apply_patch` writes are blocked; do not use the assumption that the
   correct/wrong context difference is closed. UNC, different-drive and 8.3 alias
   coverage was not measured.
3. **macOS:** run the two real CLI regressions above with the selected official
   binary; verify the normal memory startup separately. The Linux result does not
   replace this measurement.

The command-matrix test imitates three platforms and two views on Linux; it does not
run the real Windows/macOS sandbox. The existing POSIX binary tests go as far as MCP
delivery without a model account; they do not measure the receipt/Last-Session
publication or the desktop notification.

Normal hooks and the Yakala MCP are trusted local code and keep their own file
access. The profile does not turn this code, or the CLI's loading of the startup
context, into a general process sandbox. The concrete boundary examined here is the
guess verification of the patch content that the model submits to the tool.

## Sources

The official English sources below were reviewed on **19 October 2026 UTC**.
Version information was verified with the GitHub release list, the `latest` redirect
and the release API. When the web view could not open some GitHub source pages, the
same official repo was examined with a read-only `git` checkout.

- **[S1] Releases:** [list](https://github.com/openai/codex/releases),
  [latest](https://github.com/openai/codex/releases/latest),
  [0.155.1](https://github.com/openai/codex/releases/tag/rust-v0.155.1),
  [0.160.0](https://github.com/openai/codex/releases/tag/rust-v0.160.0),
  [0.163.0](https://github.com/openai/codex/releases/tag/rust-v0.163.0),
  [0.164.0-alpha.3](https://github.com/openai/codex/releases/tag/rust-v0.164.0-alpha.3),
  [release API](https://api.github.com/repos/openai/codex/releases?per_page=30).
- **[S2] Named profiles, beta, deny, precedence, MCP scope and platform limits:**
  [Permissions](https://learn.chatgpt.com/docs/permissions).
- **[S3] CLI/config contract:**
  [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference),
  [CLI source](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/cli/src/main.rs).
- **[S4] Patch handler and passing the sandbox to verification:**
  [0.163.0 apply_patch handler](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/tools/handlers/apply_patch.rs).
- **[S5] Update/Move/Delete pre-reads:**
  [apply-patch invocation](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/apply-patch/src/invocation.rs).
- **[S6] Compiling the custom profile:**
  [config/permissions.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/config/permissions.rs).
- **[S7] `resolve_permission_config_syntax` and legacy selector precedence:**
  [config/mod.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/config/mod.rs).
- **[S8] Hook trust, tool order and callback error limits:**
  [Hooks](https://learn.chatgpt.com/docs/hooks).
- **[S9] Hook decision and handler call:**
  [hook_runtime.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/hook_runtime.rs),
  [tools/registry.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/tools/registry.rs).
- **[S10] Tool registration and removed flag:**
  [spec_plan.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/tools/spec_plan.rs),
  [features/lib.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/features/src/lib.rs).
- **[S11] Strict config loading:**
  [config/loader/mod.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/config/src/loader/mod.rs).
- **[S12] Windows sandbox types, deny-read limits and MXC requirements:**
  [Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).
- **[S13] Elevated root-read requirement and subpath-deny test:**
  [0.155.1 resolved_permissions.rs](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/windows-sandbox-rs/src/resolved_permissions.rs),
  [0.163.0 resolved_permissions.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/windows-sandbox-rs/src/resolved_permissions.rs),
  [unelevated limit](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/windows-sandbox-rs/src/lib.rs).
- **[S14] AGENTS discovery/reading and startup error path:**
  [0.155.1 agents_md.rs](https://github.com/openai/codex/blob/be2951ea34f0d295ed0becf97079f92fa5f6950e/codex-rs/core/src/agents_md.rs),
  [0.163.0 agents_md.rs](https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/core/src/agents_md.rs).
- **[S15] The same condition in later sources:**
  [0.164.0-alpha.3](https://github.com/openai/codex/blob/bd43893f3db678fcb7124296905a65b2dfa9dac0/codex-rs/windows-sandbox-rs/src/resolved_permissions.rs),
  [main as read on 19 October 2026](https://github.com/openai/codex/blob/89461ea6833832b0551ce24ee32205824d5c108d/codex-rs/windows-sandbox-rs/src/resolved_permissions.rs).

Resolved commits of the examined tags:

```text
rust-v0.155.1       be2951ea34f0d295ed0becf97079f92fa5f6950e
rust-v0.160.0       a956835d020762cb2b570053af06f643a11c0ecc
rust-v0.163.0       83086188ae0614bd882818ff1aa23f3194962012
rust-v0.164.0-alpha.3 bd43893f3db678fcb7124296905a65b2dfa9dac0
```
