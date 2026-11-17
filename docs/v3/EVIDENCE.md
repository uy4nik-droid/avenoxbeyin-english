# Carrying the selected evidence

`PackedContext.sources` carries the untruncated narrow passages, the view widened with
a second passage if `wider` exists, or the list of alternatives in preference order.
`evidence` carries the identity of the same sources, their SHA-256 and revision, the
channel they came from and the selected source ranges. The ranges refer to the indexed
`record.text` characters, not to raw Markdown bytes. Each view also holds the position
in the output of the source range that was copied, so for a passage cut in the middle
of the final envelope only the displayed part is remembered. These three are attributes
of the Python object; they are not added to the envelope JSON.

The full-source and section expansion of a strict record comes only from the text of
the same record, and it uses only the budget left after the existing passage shares
have been set aside. Monthly chat-trace notes (`chat_trace`,
`knowledge/conversations/YYYY-MM.md`) gather short summaries of different sessions and
projects under a single heading, so they are not expanded; each paragraph stays like a
separate source.

Strict does not change the search selection. The Jev card reserves room for every
passage of the narrow selection and, if there is one, the wide selection; for a long
piece it uses the window that matches the query. The relevant passage of a loose
candidate is chosen locally before the card. When recovered, the narrow view is the
note's first three `TOP_CONTEXT_TEXT` windows (at most 3,300 characters). Local
delivery tries, in order: the whole note, then the passage that matches the opening as
primary, then the `wider` alternatives that carry the opening plus a window of at most
600 characters of that passage chosen by the query. `pack_widened` uses only the first
alternative that fits exactly into the budget left after all narrow records have been
delivered. If none fits, the opening remains; the narrow view may be truncated by the
normal envelope quota. The final envelope makes this decision again with its own
budget; the second window cannot truncate another source or the opening. Overlapping
ranges are not duplicated. The source ranges of all views are stored; continuity
remembers only the view that was actually delivered. This local opening reserve is not
added to the Jev card; the cards keep showing the selection relevant to the query. The
card's total excerpt limit is 600 characters; the heading and range markers count
toward that limit. This view does not guarantee a semantic decision that needs the full
text. The provider thresholds have not been changed; the new view must be measured live.

`render_context` returns the evidence references only together with the sources it
delivered. `remember` uses this delivery projection. The second version of the
continuity file stores only the source identity/revision/hash and the numeric
`[start, end)` ranges; it does not store the note text, the section heading or the user
prompt. When the source changes, the old ranges are not used. On every continuation
turn, visibility, trust, project, supersession, status, hash and current strict
exclusions are checked again. The heading path is regenerated from the current source
whose hash has been verified. Only the displayed text is preserved; a larger
continuation budget does not open text that was never shown. The topic vocabulary of an
ambiguous continuation is derived from the record's title and from the delivery ranges
that were verified and rebuilt; the note's undisplayed body does not join this
vocabulary. The general action and continuation words in the `ACTIONS`, `DEICTIC` and
`GENERIC` sets are also treated as familiar. If the request has a new topic term outside
this combined vocabulary, that turn's local search result is kept. The check does not
separately distinguish a different topic expressed only with terms found in the heading,
in the displayed passage or in the general command vocabulary. Short continuations such
as "Bunu detaylandır" ("elaborate on this") and continuations that use the words of the displayed passage work
under the existing continuation conditions.

Old (version 1) continuity files that consist only of identities are not used, because
the ranges are unknown. The next concrete, successful delivery renews them as version 2.
The twenty-minute window, the session/client/project boundary and the rule that an
ambiguous continuation does not extend the window do not change. A corrupt or
unverifiable reference falls back to the local query result. The note-level fallback
that runs without the passage engine can also store, as a range, a text prefix that can
be fully verified; it does not guess the position of the passage.

The repeat filter keeps the `sources`, `wider` and `evidence` attributes of the
remaining sources. The hook also passes to continuity, with their own evidence
references, the records that were filtered out because they had already been shown in
that session.
