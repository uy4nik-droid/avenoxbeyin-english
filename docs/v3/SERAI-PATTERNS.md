# Patterns that can be carried over from the Serai design review

The first independent source review was done with gpt-5.6-sol. Only a technical design summary is carried over; source code, private data and environment configuration were not copied. The Serai service or Mem0 is not added to this project as a dependency.

## The small piece to apply on the V3 foundation

Writing an object's new state and the event record of that change in the same SQLite transaction. A failed expected-revision check produces no event; if the same ingest is resent, the history does not multiply. The ordered snapshot history provides a foundation for later auditable restore and index rebuild. This stage does not mean a crash-recovery worker for all output files.

## Other principles kept

- Reusing an idempotency key with different content must be an error.
- The source path and the source version/hash of the search output must be preserved; the old index of a changed source must not be presented as current.
- A revision conflict is not a reason to automatically retry the same write; the new state is read.
- If there is an external effect, an intent record is needed first, then a result record. An external effect with an unknown result must not be repeated automatically. There is no external-effect executor in the V3 foundation.
- Multi-user policy, cloud backend, approval reservation and distributed control layers are not carried into the small local product.

## Evidence limit of the review

The first agent read the source code and did not run a real Serai test. Because the hub bootstrap and close did not succeed in this environment, there is no claim of a session receipt verified by Serai. Local V3 verification is done separately with synthetic tests.

## Second Sol review: source and context accuracy

The second gpt-5.6-sol agent separately reviewed the patterns of source identity/boundary, content version, context budget, abstaining from answering and selection telemetry. Excluding the old record when the source hash changes, the source/vault distinction, a deterministic budget and two harness interfaces that produce the same context are suitable pieces for this foundation.

The review also flagged two risks that should not be copied: an ambiguous alias selecting the first record, and the cache key not changing even though the output budget changed. There is no alias resolver or retrieval cache in the V3 foundation; when they are added, these cases should have separate acceptance tests. A large record not blocking small, suitable following records should also be preserved.

Both Sol processes produced reports with exit 0. The findings are a static source review; they are not real Serai tests or hub session verification. The second agent also reported that it could not create a bootstrap/close scope. Private source code was not copied and no change was made in Serai.
