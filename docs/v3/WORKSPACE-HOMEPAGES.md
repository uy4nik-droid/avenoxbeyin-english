# Editing selected Workspace information from the homepage

This optional first candidate links selected `facts` values in existing human notes
to a Markdown homepage that the user edits. Setup does not make you choose a field
type. An interview date can be text; the number of servings in a recipe can be a
number. There is no new service or automatic model call.

## Continuing from the main record in another area

A homepage can be linked to a single main note in another project. `workspace_readers: [bakim]`
in the frontmatter of the note the user selects opens the read
`context "pompa bakımına nereden devam" --project bakim` (Turkish example query:
"where to continue pump maintenance from") in addition to its existing owner. The
same `id`, `source` and the next step in the note body are returned; a second main
note is not produced.
A normal `context "Bakım Odası’nda pompa bakımına nereden devam ederim?"` query
("Where do I continue pump maintenance in the Maintenance Room?") uses the same scope
if it finds the single active registered Workspace name. If two area names appear,
it shows a scope ambiguity; when `--project` is selected explicitly, that selection
takes precedence. A general search in which no area name appears works as before.
Adding a link to the homepage does not by itself create read membership. Membership
is written to the selected note with normal `note-read`/`note-edit` and indexed with
`sync`. If membership is removed, the old index does not answer from the moment the
source changes; after synchronization, other authorized areas are not affected.
`private`, untrusted, blocked and excluded sources are not opened by membership.
`remote_allowed: false` is not sent to remote consultation. Membership does not grant
the right to create a homepage or write to the main record; the same project and
visibility rule below applies to `homepage-create`.

For example, if the main note `notes/kayitlar/pompa.md` gives the link
`[Form](../belgeler/Pompa%20Bak%C4%B1m%20Formu.txt)`, the target becomes
`notes/belgeler/Pompa Bakım Formu.txt`. Resolve the note's old link relative to the
note's folder, decode the URL encoding and verify the real file. If the file was
moved, do not present the old path as the current document. When there is a
`Form.pdf` in two folders, a basename link such as `[[Form.pdf]]` does not point to
an exact target; do not pick one without separating the candidates.

[Synthetic usage examples](examples/workspace-homepages/README.md) show setting up
the Kariyer (Career) flow and editing it in both directions; on the general Dersler
(Lessons) page they show the separation of source, assignment file, verified
submission, plan and personal note. The second uses the normal note writers;
nonexistent `facts` values are not produced. The runnable examples are a CLI
acceptance. A ready-made conversation draft is not an end-to-end acceptance in which
an independent agent interprets the conversation and performs the setup.

The user selects the existing notes and the information they want to show from them.
The agent writes the selection to the JSON request below and runs `python3 beyin.py
homepage-create --file REQUEST.json`. For a new page, `expected_sha256` is `null`. To
add to an existing human note, the SHA-256 value obtained first with `note-read` is
given.

```json
{"source":"notes/Kariyer/Ana Sayfa.md","expected_sha256":null,"title":"Kariyerim","project":"kariyer","selections":[{"source":"notes/Kariyer/Aksam.md","fields":[{"field":"facts.gorusme","label":"Görüşme tarihi","editable":true}]},{"source":"notes/Kariyer/Gunduz.md","fields":[{"field":"facts.gorusme","label":"Görüşme tarihi","editable":true}]}]}
```

The command reads every value and the record ID from the current main note; no ID,
previous value or hidden page marker is given in the request. The operation returns
`written`, or `unchanged` if no change is needed. Running the same request again does
not rewrite the page even if the personal note has changed in the meantime. A request
to rebuild with a different selection yields a conflict. The title and text of an
existing page are kept at the front; the selected information is appended as a new
section at the end of the body. A new page is created with the requested title.
`workspace_homepage: true` is explicitly chosen in the homepage's frontmatter.
For a page that carries no project field, `project:null` is given explicitly; this
request value does not add a `null` field to the note's frontmatter. The page and the
source must be in the same effective project scope and visibility. The effective scope
comes from a filled `project` field, or, if there is none, from the existing folder
mappings. The explicit-field precedence, the longest folder match and the blocked
folder rules are the same as the existing `record_scope`. They can be linked if both
sides are genuinely unscoped; `shared_unscoped` does not give permission to link a
source in another project to a homepage.
Before creating the homepage, the command indexes the sources afresh; there is no
need to run `sync` separately.
A request with an invalid format is rejected without starting synchronization. The
synchronization of a valid request can also complete a recovery left over from
earlier operations.
The source link, label, line layout and personal note on the page stay outside the
cell. The source link is a Markdown path relative to the homepage, with special
characters encoded. Each source is shown once with an understandable title; the
selected information is on separate lines and the personal note in a separate
paragraph. The source title is taken first from the note's `title` property, if
absent from the H1 heading on the first line of the body, and if that is absent from
the file name. A sample reading view (cell comments hidden):

```markdown
# Kariyerim

## Selected information

You can change the editable values in this note; changes are written to the source record at the next regular sync. Your personal notes stay on this page only.

### [Mavi Pusula — Akşam](Aksam.md)

- **Görüşme tarihi:** 6 Nisan 2099 _(editable)_

**My note:** yol süresini ve adresi sor

### [Mavi Pusula — Gündüz](Gunduz.md)

- **Görüşme tarihi:** 6 Nisan 2099 _(editable)_

**My note:**
```

(The headings, the explanation sentence, `_(editable)_` and `**My note:**` are written by
Beyin; the page title, source titles, the field label and the values are the user's own
Turkish data. "Görüşme tarihi" means "Interview date", "6 Nisan 2099" is "6 April 2099",
and the personal note says "ask about the travel time and the address".)

In this view the personal note was added with a normal `note-edit`. To show read-only
information, `editable:false` is used in the selection; in the example both dates
were chosen as editable. The [step-by-step example](examples/workspace-homepages/README.md)
shows, with separate snapshots, the change 6→7 April in the main note and 7→9 April on
the page, the interruption, the last personal note, the narrow conflict and the
no-write repeat. Its checked-in snapshots and screenshots were made before these labels
were translated and still show the earlier Turkish labels (`## Seçilen bilgiler`,
`_(düzenlenebilir)_`, `**Kişisel notum:**`); running the script there produces the labels
shown above.

Markdown special characters in titles and labels are shown as plain text. This layout
uses standard Markdown; it needs no separate theme, plugin or web application. Pages
created earlier are not reformatted when the same request is repeated; the existing
layout the user chose is kept.

In HTML comments immediately around the value, the cell stores the source path, the
record ID read, the information name, the previous common value and the edit
selection. The user does not edit these. A page with no selection is not linked
automatically. The comments are hidden in the Markdown reading view and visible in
source mode. There is not yet a visual builder.

After the main record or the homepage is written with `note-edit`, and during the
normal `sync`, the current files are read again. Personal text is not put on the
update interval. The main-record write uses the existing lock, SHA-256 check, backup
and index read-back. Different pieces of information merge. If the same information
was brought to the same value on both sides, no selection is needed. If there are two
different values, `workspace_homepages.conflicts` returns, with
`reason:choose_value`, only that information, the two values and the previous common
value; the other information moves forward. The user writes the value they chose only
to this cell or to the information in the main record, and runs the normal
synchronization.

If a read-only cell was changed by hand, `reason:read_only_field`, the source and the
page value are returned; `base` is not present in this response. The source is not
written; the page cell is restored to the current source value. A top-level
`written` in a normal `note-edit` result only confirms the note write. Before
reporting that the relevant cell was synchronized, check the
`workspace_homepages.conflicts` and `warnings` fields and the current value.

During creation, reread the page for an old SHA and update the request. Recreating a
page that is already linked with a different selection is not supported; retrying the
same request does not solve this. Keep the existing selections and choose a supported
path, such as a separate page. Repeating with the same selection does not reformat the
old page.

If an interruption comes between the source write and the page write, the previous
common value in the cell is kept. The next synchronization sees that the source and
the page have the same new value, and completes the cell without writing the source
again. The last personal note made in between is kept. Repeated synchronization does
not write unchanged Markdown files.

Limits of the first candidate: only existing single-line scalar `facts` values and
human notes; tasks, lists and objects require separate writer behavior. A homepage
cannot be selected as the main source of another homepage; link directly to the main
human note. Nested links left over from earlier or prepared by hand are also safely
excluded during reading.
The page and the record must carry the same effective project scope and visibility;
generated records, a changed ID and non-indexed targets are not written.
`trust:untrusted`, `trusted:false`, `status:untrusted` and `kind:untrusted` are
rejected in creation, repetition and synchronization, both in the source and on the
page. Manually changing a read-only cell does not cause a source write. A normal note
write, when writing back to the main record, may convert the frontmatter to the
existing JSON format; the content of the body and the other information is kept. A
mere file-open event without synchronization is not a trigger. In Obsidian the normal
synchronization is needed after a change. Concurrent writing by a real editor is
subject to the limits of the existing `note-edit` SHA check; no multi-file atomic
operation is claimed.

## If the source policy narrows later

Linked source traces are verified again at indexing and reading; even if the
homepage's own file has not changed, the earlier copy cannot be used with the old
permission. If the source is in a hidden, untrusted, other or blocked project scope,
or is missing or too old to be verified, the linked page is removed from search and
context. This is a narrowing applied to the whole page; the title, body and personal
note stay in the file. If a selected field was deleted in the source or is no longer
a single-line scalar, or the source is retired/archived or replaced by a trusted
record (`supersedes`), the old copy is also removed from context.
Retired records are not rewritten through the homepage.
Once the source is eligible again and synchronized, the page can be selected again.

If the source has only become `remote_allowed:false`, the verified page can stay in
local search, but the homepage's title and quotations are also not sent to remote
context. If the source's policy has not been indexed yet, the page is also removed
from local reading until it is verified. Two-way synchronization also compares the
outbound-sending policy; a new value is not transferred between different policies.
To continue local synchronization, the user can also make their homepage
`remote_allowed:false` with the normal note writer; the command does not loosen the
source's policy.

This restriction applies to the index, search, source snapshot, history and Jev's
manual/automatic context selections. Before real sending, including Jev review and
response verification, and after packaging and queuing, the linked source hashes and
scope are checked again. Passing a check does not permanently authorize a later
policy.

## Regression verification and open acceptance limits

`tests/v3_homepage_boundaries_test.py` tests, in the normal and the cleanly installed
CLI, the four trust markers, the source/page gates, creation/repetition/two-way
synchronization, folder scope changes and blocked folders. Equal effective scope and
explicit-field precedence continue to work. The earlier candidate failed these
regressions; the fix is verified with the same tests.

A keyed `note-edit` records the final hash, after the cell base is refreshed, in the
completion record under the writer lock. If there is no user write in between, the
same request is repeated successfully, preserving bytes and mtime. After a real user
write, the same key is not applied again; a conflict is returned. At the first
recovery after an interruption, preservation of bytes and mtime for the source is
also measured separately.

`tests/v3_homepage_policy_test.py` reproduces, as a failure on the old candidate, the
example of an already copied value from the [source policy review](https://github.com/avenoxai/avenoxbeyin/pull/647#issuecomment-6826486112).
In the normal and installed versions, local search, index, source snapshot and
manual/automatic remote cards are tested before/after the policy narrowing. In the
four Jev sending paths, the policy is narrowed while the real request is being created
or in the sending queue; zero calls to the synthetic provider transport are expected.
These run with real local files and product code, with a test transport in place of an
external provider.

These checks are not an end-to-end acceptance of a conversational automatic setup or
of the real Obsidian interface. There is no multi-file atomic operation guarantee. The
platform CI result must be evaluated separately for the relevant last commit.
