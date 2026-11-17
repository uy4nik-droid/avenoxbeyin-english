# Measuring a query change

Removing filler words from a query is not the same experiment as changing the search
engine's stopword list. The 48/54 → 52/54 field result in #679 is a **query
rewrite**; it is not claimed here to be repeated or generalized to all vaults.

## Comparing two queries on the same corpus and labels

From the repo root, with Python 3.11+ only:

```sh
python scripts/compare_v3_queries.py --fixture tests/fixtures/v3/turkish_query_pairs.json --variants tests/fixtures/v3/turkish_query_variants.json
```

- `fixture` contains `records` and `cases` lists, in the format of
  `evaluate_v3_search.py`, that are synthetic or stripped of sensitive information.
  Each question has a single `target_id` label.
- `variants` has the form `{"variants": [{"id": "question-id", "query": "new query"}]}`.
  **All questions** must be present exactly once; write the control questions you did
  not change with the same text too. A missing/extra/duplicate ID, an empty query or an
  attempt to change a label is rejected. This way a comparison cannot be produced by
  picking only the questions that improved.
- The two arms run on the same temporary corpus and target labels. The runtime, record
  tokenization, persistent settings and the live vault are not changed. There is no
  model call.
- `non_strict` measures normal note-level search; `context` measures the shared strict
  passage context path. They are reported separately. This is not a measurement of real
  hook delivery or of Jev decisions; it does not copy the installed vault's settings.
- For each question the JSON contains the target rank before/after and whether it
  improved/regressed/stayed the same; in total, recall@1/3/5, MRR and their differences.
  A single target label does not measure **precision**: the other returned notes are not
  assumed to be irrelevant.
- Timings are diagnostic. The first arm warms the cache; no speed advantage should be
  inferred from this experiment.

The output contains the queries and the source names. Do not put a fixture, variants and
results derived from a private vault into a public issue/PR. The command writes results
to stdout only; if you want to save them to a file, redirect them to a private location.

### Limits of the small included example

`turkish_query_pairs.json` v1: 10 synthetic notes, 6 Turkish filler questions aimed at
English topics and 4 unchanged controls. `var` ("there is"), the "Hakkında sayfası"
("About page"), "ilgi/konu" ("interest/topic") and the query containing only filler are
deliberately preserved. These can be real topics or titles; this is not a blind
word-deletion rule. The fixture and variants were fixed without looking at the results;
this is not a separate holdout set.

On `main@3841217`, in this example, normal search's recall@1 came out **0.9 → 0.9** and
strict context's **0.4 → 1.0**. This small corpus did not reproduce the field
degradation reported in normal search. The increase in the strict result is also not by
itself enough to change production behavior. The tests do not require a particular gain;
they check the calculation and matching contract. The existing frozen semantic/search
fixtures do not change.

## Read-only measurement on your own vault today

The installed `selftest` command, automatic result history or update gate that #675
asked for does not exist yet. The existing passage evaluation can be used through the
source repo:

```sh
python scripts/evaluate_v3_passages.py --vault /path/to/your/vault --questions /private/location/questions.json
```

On Windows too, you can put the full paths in quotes. The format of the question file:

```json
{
  "questions": [
    {"query": "example project backup order", "source": "knowledge/example.md", "sentence": "The backup is verified first."}
  ],
  "controls": {"unrelated": ["Shall we get coffee today?"]}
}
```

`source` is the real relative path inside the vault and `sentence` is the real answer
sentence in the note. First label 10–20 representative questions and their relevant
notes; do not pick only the successful questions after looking at the results. This
script compares note and passage paths separately: `recall` measures source delivery,
`answerable` additionally measures whether the answer sentence is in the delivered
text, and `noise` measures delivery of any record for the control queries. Instead of
measuring the user's existing index/settings, it creates a temporary runtime; the real
vault or persistent state is not written. Keep the previous report yourself; without the
same questions/corpus/settings, do not interpret two numbers as a "version improvement".
