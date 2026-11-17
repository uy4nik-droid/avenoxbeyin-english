# Optional Jev advisor

Normal `context`, lifecycle hooks and automatic jobs stay local. This add-on is **off by default**. Jev does not save memory, does not give user approval, and does not widen the source or project boundary.

## Explicit activation

The installer does not ask about this add-on and does not install it. To turn it on, turn it off and see its state, use these commands in the installed vault:

```sh
python beyin.py jev status
python beyin.py jev shadow
python beyin.py jev on
python beyin.py jev off
```

The same command from the source repository: `python scripts/beyin_v3.py --vault /path/to/vault --state /path/to/state jev status`.

`status` only reads; `off|shadow|on` writes the setting and returns the result and `"changed": true`. The command does not need the vault index or source synchronization. It does not accept or print a key; there is deliberately no `--key`-like option.

Features turn on and off individually; `--enable` and `--disable` can be repeated and cannot be combined with `status`:

```sh
python beyin.py jev on --enable auto_context
python beyin.py jev shadow --disable answer
```

| Feature | Command that uses it | Default |
| --- | --- | --- |
| `context` | `context --jev` | on |
| `review` | `jev-review`, `jev-memory` | on |
| `answer` | `jev-answer` | on |
| `auto_context` | the per-turn hook path; [see below](#automatic-context-on-every-turn-auto_context); off unless explicitly enabled | off |

If the purpose of a disabled feature is called, the client returns the `off` mode with a `feature_disabled` diagnostic, without reading a key and without going to the network.

When `auto_context` is on, `status` output shows `automatic_model_calls: true`; the command adds a `notice` to it saying that on every turn the prompt, plus the title and a query-selected passage view of at most 600 characters for each of up to 8 candidate `internal`/`public` notes, goes to the provider. That text can come from any section of the note. `private` notes are not sent. If the mode is not `off` and there is no key, a `warning` is added and calls fall back to the local result.

### Emergency kill switch

The `BEYIN_JEV_DISABLE=1` environment variable, or a `jev.disabled` file in the state directory, stops calls without changing the saved mode. In that case `status` shows `mode: "off"`, the old value as `saved_mode`, and `kill_switch: true`. When the variable is removed or the file is deleted, the saved mode applies again.

### Call log

Every call writes a one-line counter to `jev-calls.jsonl` in the state directory: purpose, mode, provider (`provider`), cache hit, `degraded`, error code, latency, input token count, HTTP request count (`http_requests`) and time. Query text, candidate text, response content and the key are not written. When the file exceeds its limit, the older half is discarded. `jev status` and `doctor` summarize the last 24 hours from it.

### Manual editing

`jev.json` can still be edited by hand; advanced keys such as `timeout`, `max_candidates`, `base_url` and `env_file` are preserved when the command writes. The command is the only writer of this file: it writes atomically with 0600 permissions. If the file is corrupt the command returns an error and does not touch the file.

```json
{"mode":"shadow","model":"jev-1.13.0","provider":"typesafe","timeout":3,"max_candidates":32,"max_questions":96,"max_input_chars":24000,"cache_ttl":3600}
```

`TYPESAFE_API_KEY` must be in the environment. Do not write the key into Markdown, version control or a command argument. If `env_file` is used, it needs an absolute path. The provider URL is chosen with `base_url` or `TYPESAFE_BASE_URL`; HTTPS and local HTTP are supported. Calls to local addresses (`localhost`, `127.0.0.1`, `::1`) do not use `HTTP_PROXY`, `ALL_PROXY` or the system proxy settings; remote HTTPS addresses still go through the configured proxy. If a Vercel-compatible bridge is used, `provider: "vercel"` can be selected; this is not a Vercel account/key installer. For a keyless, open-weight model running locally, see [the Laya section](#local-laya-backend-optional).

```sh
python scripts/beyin_v3.py --vault /path/to/vault --state /path/to/state context "short notes" --project demo --jev
```

The equivalent in an installed vault: `python beyin.py context "short notes" --project demo --jev --json`. `--json` also shows the advisor diagnostics. For review, use `python beyin.py jev-review --project demo --file proposal.json --json`.

`--jev` and an explicit project identity are required together. This call sends, from at most 16 candidates of the local search, those allowed for remote evaluation: their titles (160 characters), text excerpts (800 characters), project/status/date information and the query. The number of records in the final output is a separate limit. If the pool does not fit the limits of a single request (`max_candidates`, `max_questions`, `max_input_chars`), it is split into at most three packets in turn; with the default 24,000 characters, 16 candidates with 800-character excerpts do not fit one request. Each packet is sent once and is not retried; if one fails, all scores are discarded and the local order is used. If the pool does not fit into three packets, no call is made (`budget_exceeded`). `internal` visibility can also be sent; use `--audience public` for public text only. `private`, out-of-scope, untrusted, changed and superseded records are not sent. If a local secret pattern matches, no call is made; pattern scanning is not a guarantee of recognizing all sensitive information.

- `off`: no network/key/cache access.
- `shadow`: scores are in the `jev` field; the local result and order are preserved.
- `on`: selection is made from the candidate pool; a relevant candidate that did not fit into the first local output can be taken. Up to three sub-requests separated by semicolons are evaluated separately. The character budget does not change. Jev cannot find a record that the local candidate search did not find at all.

`remote_allowed: false` or `sensitivity: sensitive` source metadata prevents the record, including its title, from being sent to Jev. For `remote_allowed`, use a JSON/YAML boolean, not text. Such sources, when found suitable locally, are packed alternately with the ones selected remotely; they cannot fill the whole quota from the start. `aliases: ["sound offset", "audio offset"]` widens the local candidate search; it does not bypass the permission gates.

After the call, source hashes, index revisions and access conditions are checked again. If anything changed, the score is discarded and the current local result is used. A timeout, 429, missing key or malformed response does not block local results. Diagnostics do not contain raw service errors.

### Project scope by folder (optional)

By default the project scope is the record's own `project` field. In a vault that organizes notes by folder and never writes this field, every command that takes `--project` (`context --jev`, `jev-review`, `jev-memory`, `jev-answer`) ends up with an empty scope. A `.beyin-projects.json` in the vault root resolves this without touching the notes:

```json
{
  "folders": {"Projects/Game Channels": "games", "Projects/Archive": "archive"},
  "shared_unscoped": true
}
```

- `folders`: folder relative to the vault → project. The record's own non-empty `project` field always comes first; with nested folders, the longest match wins. A match stops at the folder boundary (the `Projects/Game` folder does not cover what is in `Projects/Game Old`); paths are compared as Unicode NFC, regardless of `/` and upper/lower case (like macOS and Windows vaults). Every folder you write must actually exist in the vault: a misspelled or renamed folder maps no note. A folder that cannot be found gives a warning but its mapping is kept as a boundary; old index rows are not opened to every project as shared records through `shared_unscoped`.
- `shared_unscoped`: if `true`, records that fall under no project (rules, general notes) enter the scope as shared records in every explicit-project query. Another project's records never enter under any condition. Default `false`.
- The file is read only in calls with an explicit project. Vaults where a turn sends no project, and vaults without this file, work exactly as before. The visibility, trust, freshness and superseded gates apply unchanged inside the scope too.
- A corrupt file (invalid JSON, unknown key, a `folders` that is not an object, a `shared_unscoped` that is not a boolean) stops an explicit-project call with an error. A single bad entry (an absolute path or one containing `..`/`.`, an empty project name, a folder assigned to two projects) is instead skipped with a stderr warning and the other mappings keep working: the folder the entry could have pointed to inside the vault is not opened to any project, does not fall to the parent folder's project either, and `shared_unscoped` is treated as off until the entry is fixed. The scope never widens silently; `doctor` and `project-scope list` show skipped entries by name. When you rename a project folder, update the file too.
- A sibling repository outside the vault (for example `../repo`) is not written into the scope file; such an entry is skipped. If the name of the working directory or of one of its parent directories equals a project's name or the last name of a mapped folder, that project is selected for the session rules.
- With `shared_unscoped: true` on, `context --project` searches made through the external project bridge also see the shared records; if personal notes are to stay off the shared shelf, use `private` visibility.

## Reviewing an unrecorded knowledge candidate

First get the source record's `id` and `source_sha256` with normal `context`. Prepare a separate JSON file:

```json
{
  "status":"proposed",
  "project":"demo",
  "claim":"Short notes are preferred in the Demo project.",
  "evidence":[{
    "record_id":"demo-notlar",
    "source_sha256":"CURRENT_SHA256_OF_THE_SOURCE_FILE",
    "quote":"Let's use short notes for Demo."
  }]
}
```

```sh
python scripts/beyin_v3.py --vault /path/to/vault --state /path/to/state jev-review --project demo --file proposal.json
```

1–8 pieces of evidence, an exact quote, the same project and a current hash are required; the quote must be present both in the index text and in the real source. If source synchronization is missing, the review stops. The response always contains `approved: false` and `memory_written: false`. The result is only the score of how well the quote supports the claim; it does not automatically merge with other cards or resolve contradictions. A separate reviewing person/agent evaluates scope and time limits and, if needed, uses the existing `note-create` flow.

## Source-backed memory evaluation (`jev-memory`)

It uses the `review` feature and accepts the same `proposal.json` format:

```sh
python beyin.py jev-memory --project demo --file proposal.json --json
```

With the optional `prior_record_ids: ["old-decision"]` field, up to four prior
records can be specified. If the field is absent, they are chosen from suitable
local candidates in the same project; an empty list turns off the comparison with
prior records. One request asks three independent Choice questions (support,
certainty/intent, type of knowledge) and one relationship question per prior record.
The relationships: repeat, elaboration, changed decision, contradiction or unrelated record.

If any answer has low confidence, the source does not support the claim, the wording
is not definite, or it contradicts a prior record, `route: inspect_sources` is
returned. For a changed decision, the source dates are additionally checked in code.
Even a suitable candidate only becomes `candidate_for_agent_review`; `approved`,
`memory_written`, `task_created` and `task_completed` always stay `false`. The active
agent inspects the source and uses the normal recording flow within its existing authority.

If the claim restates an `inference` or `preference` record that was rejected in the
same project and audience boundary, the result carries a `previously_rejected`
diagnosis and the identifiers of those records; it returns `inspect_sources` instead
of `candidate_for_agent_review`. This check runs locally in every mode, including `off`:
there is no model call and no write, and the rejected text and rationale do not enter
the provider request. The match is lexical: `rejected_matches(store, text, project, audience)`
(`beyin_v3.py`) normalizes the text on both sides the same way as context search
(lower case, Unicode form, Turkish suffixes), and it matches if at least 60% and at
least two terms of the rejected statement, by its title or text, appear in the new
claim. A title counts only if it carries at least three terms; a short title like
"Coffee preference" is a topic label, not a claim. It does not catch a claim that
means the same but is written in other words. Nor does it distinguish negation: a new
sentence that corrects the rejected claim can match because it carries the same terms.
The result only turns the routing into `inspect_sources`, and blocks nothing; the final
decision is the agent that reads the source. The same function can also be called from
other paths that produce candidates.

In `off` mode the source/quote check is local; there is no key, Jev cache or provider
access. `shadow` can evaluate but does not apply the dimensions and routing. The full
text of the permitted evidence and prior records is sent; if 4,000 characters per source
or the total request budget is exceeded, it falls back to local review. If one source is
local-only, the whole semantic evaluation is skipped.

## Follow-up context without Jev

At most three sources that the hook actually delivered are remembered, in the same
harness and session, for short follow-ups like "test that one too". The raw message
or transcript is not saved; only the source identifier, hash, revision, project and
time are kept. It expires 20 minutes after a concrete topic; vague follow-ups do not
extend the time. A source is not carried over on a different project, a new topic, a
source change or loss of permission. The topic distinction is a limited set of
Turkish/English word rules; it is not a guarantee of general language understanding.
This local feature is independent of the Jev modes.

For the current implementation, research links, measurement and limits:
[PR 69 review evidence](decision-quality/REVIEW.md).

## Ported solutions and measurement

From Forn Hafıza OS version `524fd07`, the budgeted client, the source/scope-bound score cache, strict score validation and a narrow tolerance for Vercel's probabilities rounded to two decimals were ported. The tolerance applies only to distributions that are mathematically possible on Vercel; direct TypeSafe validation is not loosened. The MIT attribution is inside the client and in [the license file](THIRD-PARTY-JEV.txt).

The cache stores only validated scores and limited metadata in the state directory; it does not store the query, source text or key. The cache key depends on source version, project, purpose, model, endpoint and rubric. Token counters are reported if they come from the provider; the character budget is not a token/billing figure. The client has no special 400-call limit; the counter of the earlier experimental bridge was not a provider account quota.

When measuring learning changes, freeze the sources and questions before writing. With the same code/routing, measure final context delivery and spill outside the project before/after; do the model on/off comparison separately. Cards in the private vault and experiment results were not moved into this repository. The synthetic offline tests here are not proof of general semantic success or of a live Jev connection.

## Checking the claims in an answer against their sources

`jev-answer` evaluates 1–20 claims in a prepared answer one by one.
The source gate and the support/contradiction distinction from the Forn Hafıza OS
local `jev_answer.py` flow were adapted to the V3 record identity, project scope
and revision contract. Personal records and other memory-system updates were not ported.

First take the record identifier and current hash from the `context` output. `claims.json`:

```json
[
  {
    "text": "Short notes are preferred in the Demo project.",
    "citations": [
      {
        "record_id": "demo-notlar",
        "source_sha256": "CURRENT_SHA256_OF_THE_SOURCE_FILE",
        "quote": "Let's use short notes for Demo."
      }
    ]
  }
]
```

```sh
python beyin.py jev-answer --project demo --file claims.json --json
```

Usage from the source repository:

```sh
python scripts/beyin_v3.py --vault /path/to/vault --state /path/to/state jev-answer --project demo --file claims.json
```

At most 8 citations per claim and 32,000 input characters in total are accepted.
Claims go to the provider in packets of 8 (at most 4 requests at the same time).
Within a packet each claim stands under its own key (`items.k3`) and its question
addresses that path in backticks; with addressing by list order and by indirect
citation, scores leaked to neighboring claims in live Jev. If a packet exceeds the
`max_input_chars` limit, it is split in two without making a network call. A request
that fails makes `degraded` only the claims in its own packet.

Along with the quote, the full index text of the source records and limited scope
metadata are sent (4,000 characters in total per claim). If the full context does not
fit, it is not truncated: the claim returns to local review as `uncertain` with
`source_context_incomplete`. A quote can be exactly right while the rest of the note
says the opposite ("old plan ... this plan was cancelled"); when only the quote was
sent, such claims came out `supported`. This context goes through the same secret
scan; if there is a match, that claim is not sent and becomes `degraded` with
`context_sensitive`.

An empty citation or a hash/quote that does not match returns `insufficient`, and that
claim is not sent to the provider. The quote must be found verbatim both in the index
record and in the real source. The project, visibility, trust and secret checks of the
other Jev commands apply. This explicit command can send `internal` record quotes and
the text around them to the provider; `private` records are filtered out. The normal
context and hook flow does not change.

`mechanical_verified` reports the source/quote match; it is not semantic verification.
In `off` and `shadow` modes the semantic result stays `uncertain`. In `on` mode a single
choice question is asked for each claim: does the evidence support the claim, contradict
the claim, or say nothing about the claim. This is the provider's own recipe for citation checking.

| Choice | Confidence ≥ 0.8 | Confidence < 0.8 |
|---|---|---|
| `supports` | `supported` | `uncertain` |
| `contradicts` | `contradicted` | `uncertain` |
| `says_nothing` | `insufficient` | `uncertain` |

The result also returns `relation` and `confidence` fields; for `uncertain` results
the diagnosis is `low_confidence`. Confidence is a value derived from the provider's
option probabilities; it is not a probability of correctness.

The 0.8 threshold is the starting value in the provider's recipe; it is not a calibrated
probability of correctness or a measure of general success. If, after the call, the
source, index revision, access conditions or configuration change, the result becomes
`degraded`. Service errors also produce no verified result. The command does not rewrite
the answer, approve a candidate or create a canonical memory record;
`approved`, `memory_written` and `rewrites` are always `false`. The CLI's normal source
synchronization may refresh the local index; the Jev score cache may also be updated in
the state directory.

The tests run with synthetic sources and an offline transport. The design was chosen on
2026-09-20 on live `jev-1.13.0` with 26 synthetic Turkish/English claims (negation
suffix, different number/day, scope widening, unrelated quote, exact quote but the rest
of the note says the opposite). End to end, with two orderings and three repeats each,
156 results: 138 expected clear labels, 18 `uncertain`, no wrong clear label; 26 claims
in 4 requests and about 250 input tokens per claim. The earlier version, with two Score
questions and sending only the quote, spent about 750 tokens per claim and missed 3 of
the 4 claims that contained a quote from a cancelled plan. Packing is not free: hard
claims near the end of a packet can lose confidence and become `uncertain` (24/24 with
one request per claim, 18-21/24 in a packet). This is a small configuration trial; no
general accuracy, cost advantage or user acceptance on real vaults is claimed.

## Automatic context on every turn (`auto_context`)

The other three features are called by hand. This feature runs inside the hook, on
every message; so choosing a mode does **not** turn it on, it is requested separately:

```sh
python beyin.py jev shadow --enable auto_context   # measure first
python beyin.py jev on --enable auto_context       # then apply
python beyin.py jev on --disable auto_context      # turn off only this
```

Why it exists: local "strict" matching brings a note only with two shared words. This
keeps an unrelated note out, but also misses a question asked in other words (the
question "how do I go back to the previous version after a deploy" cannot find the
note that says "rollback"). When on, the hook works in two stages:

1. Besides the strict matches, local search finds loose candidates. At most 8 records allowed for remote evaluation are selected: strict matches first, loose candidates in the remaining places. Loose candidates are an alternating merge of two rankings: the word weight of the whole note, and the weight of the section of the note that best fits the prompt (the strict section score, without a threshold). This way the answer in a single section of a long note does not stay behind short notes that repeat a general word of the prompt; the first candidate of the word ranking also keeps its place (#533). The section ranking uses the section index that strict search built in the same turn; if the index is not ready yet, only the word ranking is used. At most 64 candidates from each ranking are looked at. `daily/`, excluded folders, local-only records and records already in strict are filtered out before the ranking is cut, and use up no place. The pool goes through the same visibility, trust, freshness and supersede gates; `daily/` and `private` records do not enter the pool. The number of cards going to the provider and the per-card text limit did not change.
2. A single Jev request asks a topic gate ("is this message a concrete topic, or a greeting/acknowledgement") and one yes/no per candidate.

In `on` mode the result is applied like this: if the topic gate is under 0.25, no note is added. A strict match that falls under 0.4 is removed. A loose candidate is added only at 0.6 and above. At most 5 records, same character budget. If nothing changes, the local result is used as it is. In `shadow` mode the call is made, the result does not change, only the counters are written (`dropped`, `rescued`).

Cases that fall back to the local result: a message shorter than 12 characters, a local secret pattern match, missing key, timeout, 429, malformed response, a source that changed during the call, kill switch. The hook waits at most 2 seconds, and does not call at all if it is close to its own 5-second limit. If `jev.json` does not exist, the Jev module is not imported.

The cost, plainly: on every message, the message text and the title of the candidate notes, along with a query-selected passage view of at most 600 characters, go to the provider. If strict search has two passages, room is reserved for both; for long passages the window matching the query is chosen. The relevant section of a loose candidate is also chosen locally. If it is rescued, the final envelope gives priority to the opening of at most 3,300 characters. It uses the first of the views that fits exactly into the remaining budget: the whole note, the passage that primarily matches together with the opening, or the opening with the query-selected window of at most 600 characters of that passage (`pack_widened`). If none fits, the opening stays. This local delivery preference does not enlarge the Jev card. The section heading and the `[…]` mark between ranges are included in these 600 characters. The card schema, the number of candidates, the 2,000-character limit of the prompt, the metadata fields and the secret scan before the final send do not change. The `private` / `remote_allowed` checks apply as usual. A single-shot call measured earlier from Istanbul had a median of 1.3 seconds and its 90th percentile was above 2 seconds (the server is on the US west coast); live latency and threshold behavior for the new passage view must be measured separately.

Measurement (2026-09-20, live Jev, 12 synthetic Turkish/English notes, 26 messages, single run): finding the relevant note rose from 13/17 to 15/17, unrelated-note injection fell from 2 to 1, no relevant note found by strict was lost, and one call timed out and fell back to the local result. There was one wrong addition (a test-strategy note for the message "refactor this function for testing"). This is a synthetic measurement and Jev gives slightly different scores to the same request each time; on a real vault the hit rate may come out lower. On your own notes, first look at the counters with `shadow` for a few days, then switch to `on`.

## Local Laya backend (optional)

[Laya](https://github.com/NandhaKishorM/laya) is Convai Innovations' Apache 2.0 licensed, open-weight System One decision model. The `laya-serve` server speaks the same `POST /v1/systemone` protocol as Jev. Beyin uses Laya as a separately installed local server: no Laya code, model weights or PyTorch enter the Beyin package; the hook and CLI do not import `torch` or `laya` (`tests/v3_stdlib_imports_test.py` checks this). The default provider does not change; Laya is used only when explicitly selected and runs only in shadow mode: its scores are recorded for measurement and do not change the result the user sees ([Shadow mode only](#shadow-mode-only)).

### Installing Laya outside Beyin

Laya needs Python 3.10+ and PyTorch. Install it into a separate tool environment, not Beyin's environment:

    pipx install "laya[serve]"
    LAYA_HOST=127.0.0.1 LAYA_PORT=8765 LAYA_MODELS=multilingual laya-serve

Windows PowerShell:

    $env:LAYA_HOST = "127.0.0.1"; $env:LAYA_PORT = "8765"; $env:LAYA_MODELS = "multilingual"; laya-serve

`LAYA_HOST=127.0.0.1` is required: `laya-serve` listens on `0.0.0.0` by default and opens to devices on the same network. Since Beyin's default address is `http://127.0.0.1:8765`, give `LAYA_PORT=8765`. `laya-serve`'s own default, 8000, is a commonly used development port; Beyin does not assume 8000, so that another application running there while Laya is down does not receive the note text. The first run downloads the model from Hugging Face (multilingual is about 650 MB). After the download, starting with `HF_HUB_OFFLINE=1` prevents the server from going to the network and downloading a new model on request. On Apple Silicon `LAYA_DEVICE=mps` can be used; if there is only a CPU, `LAYA_THREADS` should not exceed the number of physical cores. The server holds several GB of memory together with the loaded models.

### Turning on and off

    python beyin.py jev shadow --provider laya
    python beyin.py jev status --check
    python beyin.py jev shadow --provider laya --model multilingual
    python beyin.py jev on --provider typesafe

The last command returns to Jev; the Laya settings are kept. `jev on --provider laya` is not accepted (`laya_shadow_only`); see below. `--base-url` and `--model` are accepted only with the Laya provider. `status --check` reads only the `/health` address of the configured local server, once (1 second), and sends no note or key; it never probes TypeSafe. `doctor` does not go to the network.

The setting sits in a separate `laya` block in `jev.json`:

    {"mode":"shadow","provider":"laya","laya":{"base_url":"http://127.0.0.1:8765","model":"multilingual"}}

- `base_url` can only be `127.0.0.1` or `::1`; even `localhost` is not accepted, because the hosts file can redirect it to another address. `TYPESAFE_BASE_URL` does not redirect Laya calls; HTTP proxy settings in the environment are not used for these calls.
- No key is needed. If `laya-serve` runs with `LAYA_API_KEY`, the same value must be present in Beyin's environment (or in `env_file`) as `LAYA_API_KEY`. `TYPESAFE_API_KEY` is never sent to Laya.
- `model`: `multilingual` (default; Turkish and English, 1024 tokens per row) or `english` (English only, 512 tokens). A single model is pinned; candidates in the same question are not scored with different models. If the server answers with another model, the result is discarded (`laya_checkpoint_mismatch`). `typed-decisions` is not supported: it was trained for other workflows and on a server where it is not loaded it starts an 843 MB download on the first request.
- `timeout` is at most 10 seconds, default 8. The hook path still waits at most 2 seconds; if it does not make it, the local result is used.
- If a `rollback` is made to a version from before Laya support, the old version does not recognize the `laya` block, treats the setting as invalid and turns the advisor off; it does not send the TypeSafe key to the local port. To return to Jev in the old version, delete the block from `jev.json`. This behavior is verified with the published 3.1.0 in `scripts/verify_v3_jev_package.py`.

### Differences from Jev

Laya evaluates each question in a separate row and truncates anything beyond the first 512 or 1024 tokens of the row without an error. For Jev, the format that addresses several notes by key in one request would make the later notes invisible in Laya. For this reason the Laya backend puts a single candidate and a single question in each request: for `auto_context` one topic request and one request per note, for `context --jev` one request per candidate and sub-request, for `jev-answer` one request per claim, for `jev-memory` one request each for the three dimensions and per prior record. The questions are short, question-first and in English; the option texts are the same as Jev's. At most 48 requests are made; requests go in a single sequence, because `laya-serve` does one inference at a time. With Laya, `jev-answer` also sends packets in sequence, not in parallel.

The text is not truncated to make it fit. Before each request is sent, it is compared with a measured size limit; if one exceeds it, no request is made and the result falls back to the local result with `laya_state_too_large`. The only deliberate shortening is the prompt's share in the `auto_context` request: the topic request and each note request carry as much of the prompt as fits within the limit, without cutting the note. A row that still fills the limit is caught after the answer: if the row reached the token limit, the result is discarded (`laya_state_truncated`). In Laya, the source context per claim is limited to 1,200 characters instead of 4,000 (400 for `english`); a claim that exceeds it returns to local review with `source_context_incomplete`, for that claim only.

The limits were measured on 2026-09-24 with the two models' own tokenizers: the templates take between 39 and 102 tokens for the question and options, leaving at least 918 (multilingual) or 403 (english) tokens for the state. The size unit is the character count; digits and characters above U+024F (CJK, emoji) count heavier, Turkish letters are a single unit. On Turkish documents, ASCII Turkish, English text, 493 real Markdown notes and Python code, tokens per unit came out at most 0.52 (multilingual) and 0.50 (english). Of 1,080 `auto_context`, 960 `context --jev` and 909 `jev-answer` requests built from real notes and exceeding the context limit, none exceeded the multilingual limit; at most 57 percent of the room was used. With the `english` model none of the same note requests fit; this model is only for short English content and falls back to the local result on note-sized requests.

For `choice` questions, confidence is taken not from Laya's entropy-based `confidence` field but from the probability of the most likely option; this is the value Laya calibrates. In the record, `confidence_provenance.origin` is `laya_max_probability`.

### Shadow mode only

Laya scores do not change any result the user sees. The reason is [the measurement](#measurement) below: zero-shot Laya came out much weaker than Jev on these decision tasks.

- `jev on --provider laya`, `jev on` while Laya is configured, and a switch from the saved `on` mode to Laya are rejected with the `laya_shadow_only` code; `jev.json` does not change. The command error carries an English `hint` that points to the next step.
- Even if `jev.json` is set by hand to `"mode":"on"`, Laya runs in shadow mode. `jev status` shows this with `mode: "shadow"`, `saved_mode: "on"`, `shadow_only: true` and `mode_refused: "laya_shadow_only"`; in the human output of `jev status` and `doctor` the mode is written as `shadow (only)`.
- With Laya, `auto_context` and `context --jev` do not change the order and content of the context; the automatic context record becomes `scored_unverified`. `jev-answer` claims stay `uncertain` with `semantic_shadow`, the `jev-review` result carries `mode: "shadow"`, and `jev-memory` produces no decision (`shadow_not_applied`). Scores are visible in the output and counters for measurement.
- Decision thresholds sit in the `beyin_v3_jev_client.THRESHOLDS` table by provider and model pair. The Laya rows are copies of Jev's values and are marked `verified: false`; `status` shows this with `calibration: "jev_thresholds_unverified_for_laya"` and `auto_context_applied: false`, and the outputs show it with `calibration: "unverified_for_provider"`. The shadow boundary is independent of this mark: unless Laya is removed from the `client.SHADOW_ONLY` list by a separate decision, setting a row to `verified: true` changes no result.

### Privacy

Even though Laya runs locally, the sending rules are the same as Jev's: `private` notes, `remote_allowed: false` and `sensitivity: sensitive` records, `daily/` session notes and text matching a secret pattern are not sent. Not only `laya-serve` but any local process can listen on a loopback port. An option that opens local-only notes to local Laya only (`local_only_notes`) will be evaluated separately in the future; today this key is invalid in the `laya` block. The kill switch (`BEYIN_JEV_DISABLE=1`, `jev.disabled`), feature switches, call log and cache work the same way; in the record the `provider` field is `laya` and `http_requests` is the real request count. The Jev and Laya caches do not mix.

### Measurement

The Laya tests in this repository run against a fake local server and say nothing about model quality. The accuracy numbers in Laya's own README were not verified in this repository.

<!-- BENCH -->
**Jev vs Laya comparison (2026-09-24).** Jev: `jev-1.13.0`, the official TypeSafe API. [Laya](https://github.com/NandhaKishorM/laya): 0.3.20, Hugging Face `convaiinnovations/laya` revision `55cf4c4e`, `multilingual` and `english` models, `laya-serve` over loopback, Apple M5 (24 GB, MPS). Laya was used zero-shot, with no fine-tuning. Only synthetic, fictional or previously published labeled sets were used; the items and correct labels were frozen with sha256 before the first model call. Laya received, besides the same bytes that went to Jev, also formats better suited to it (one item per request, English phrasing, pinned model); the table has the best Laya result for each row. Confidence is the largest probability; the square brackets are the 95 percent interval.

| Task | Metric | Jev | Best Laya |
| --- | --- | --- | --- |
| Claim and source (190 claims) | Accuracy, Beyin `jev-answer` format | 0.930 | 0.579 [0.51; 0.65] |
| Claim and source (190 claims) | Wrong `supports` that passes the confidence gate in Beyin format | 6 | 42 |
| Memory review (100 statements, 64 hedged or negated) | Relation accuracy | 1.000 | 0.450 [0.36; 0.55] |
| Memory review (100 statements, 64 hedged or negated) | Wrong promotion that passes the confidence gate (on 64 statements) | 0 | 5 (11 in the English phrasing) |
| Action risk gate (315 synthetic tool calls) | Catch / false alarm | 97.9% / 3.7% | 54.7% / 21.8% |
| Topic gate (279 short Turkish and English messages) | Accuracy, Beyin phrasing, threshold 0.25 (Jev: mean of 3 runs) | 0.866 | 0.652 [0.59; 0.71] |
| Robustness to small changes (98 sentence pairs) | Both sentences on the correct side | 0.918 | 0.316 |
| Existing synthetic labeled sets (1,285 binary decisions) | AUC / ECE | 0.994 / 0.073 | 0.609 / 0.227 |

In the action gate the privacy filter did not send 5 calls to Jev; the Jev rates are over the remaining 310 calls. On neither side were there HTTP errors, timeouts or invalid answers; Laya gave bit-for-bit identical results on every repeat check.

The result is clear: zero-shot Laya is much weaker than Jev on these Turkish and English decision tasks and no format difference that was tried closed the gap. The main reasons: nearly the same score for every item in cases that address several notes by key, missing most negations, short Turkish text or Turkish text without Turkish characters being routed to the `english` model in automatic routing, and error-free truncation at the row limit. For this reason the only provider in Beyin that can change the result is Jev. Laya stays as an optional local option that runs only in shadow mode: the data does not leave the machine, there is no API cost, and it always gives the same answer to the same input; for this reason it is kept for measurement and privacy experiments. The server holds 4.5 to 5.9 GB of memory and its cold start takes 11 to 19 seconds. The Laya rows in `THRESHOLDS` stay `verified: false`. Among the surfaces tried, Laya's only strong signal was whether two claims say the same thing in the English phrasing (AUC 0.915); this use also must not be turned on without measuring its own threshold on separate development and test sets.

Limits: most items are synthetic or fictional; in some sets the same author prepared the items and labels, and some rubrics and thresholds were tuned earlier against Jev, so some sets are in-sample for Jev. The results are for zero-shot Laya at revision `55cf4c4e`; weights can change, and fine-tuning was not tried. Latency was not measured in this comparison.
<!-- /BENCH -->
