# Workspace homepages: fictional usage examples

The Mavi Pusula ("Blue Compass") interviews, courses, dates and files in these
examples are entirely made up. The script installs the v3 package into a temporary
vault, creates the examples with the public CLI commands and checks the results. It
does not touch a real user vault. The generated notes, file names and quoted page
text are produced in Turkish by the script and are quoted here as they are.

Run from the repository root:

```sh
python3 scripts/example_workspace_homepages.py --output /tmp/workspace-homepage-examples
```

On Windows you can choose a path from your own temporary folder for `--output`.
The command writes the check result to the screen and to the `result.json` file. The
Markdown files in the same output folder are readable snapshots of the flow; the HTML
comments belonging to the binding have been removed from these copies. They can be
moved together with the fictional note and source copies under `vault/`. The links in
the views go to these files in the **final state** of the flow; they do not rebuild
the source content of a past step. The script verifies the original links in the
temporary vault and the exported links in the output folder. The temporary installed
working environment is not exported.

## Kariyerim ("My Career"): editing selected information in both directions

The **Akşam** (Evening) and **Gündüz** (Daytime) records of the fictional Mavi Pusula
are separate main notes. Both first carry the interview date of **6 April 2099**
(`6 Nisan 2099`); the invitation text is a separate original file.
`homepage-create` links the `facts.gorusme` fields ("interview") the user selected to
the **Kariyerim** page. The link of each record is relative to the homepage. The
interview date is in an editable cell, and the personal note is outside the cell.

Example user request: "I want to see the dates of both interviews on one page and
correct them from there. I'd also like to write a note next to the Akşam record about
the travel time." This sentence is an explanatory usage draft; it is not claimed that
an automatic agent conversation was run.

At the start there are two separate main notes:

| Main note | Title | `facts.gorusme` | Original document |
| --- | --- | --- | --- |
| `notes/Kariyer/Aksam.md` | Mavi Pusula — Akşam | 6 Nisan 2099 | `Davet.txt` |
| `notes/Kariyer/Gunduz.md` | Mavi Pusula — Gündüz | 6 Nisan 2099 | `Davet.txt` |

The script creates these with a normal `note-create`. It then gives the following
request to the `homepage-create --file` input; it does not prepare values or cell
markers:

```json
{
  "source": "notes/Kariyer/Ana Sayfa.md",
  "expected_sha256": null,
  "title": "Kariyerim",
  "project": "kariyer",
  "selections": [
    {"source": "notes/Kariyer/Aksam.md", "fields": [
      {"field": "facts.gorusme", "label": "Görüşme tarihi", "editable": true}
    ]},
    {"source": "notes/Kariyer/Gunduz.md", "fields": [
      {"field": "facts.gorusme", "label": "Görüşme tarihi", "editable": true}
    ]}
  ]
}
```

On the resulting page the user sees two separate source links and two editable dates.
The note "yol süresini ve adresi sor" ("ask about the travel time and the address"),
added with a normal `note-edit`, stays only in the Akşam section; it is not written to
the main note's `facts` field.

![General Markdown preview of the Kariyerim page](career.png)

*Kariyerim: a general preview of the generated Markdown; it is not a real Obsidian screenshot.*

Follow the example flow through these snapshots:

| Operation and snapshot | Akşam main note | Akşam page value | Gündüz | Personal note |
| --- | --- | --- | --- | --- |
| [Create](career-created.md) | 6 April | 6 April | 6 April | ask about the travel time and the address |
| [Edit the main note](career-from-source.md) | 7 April | 7 April | 6 April | kept |
| [Edit the date on the page](career-from-homepage.md) | 9 April | 9 April | 6 April | kept |
| [Interrupt after the source write, change the last note, synchronize](career-recovered.md) | 11 April | 11 April | 6 April | ask about the address and the entrance door |
| [Write two different values to the same information](career-conflict.md) | 12 April | 13 April — conflict | advances to 8 April | the last note is kept |
| [The user chooses the value in the main note](career-resolved.md) | 12 April | 12 April | 8 April | the last note is kept |

All the dates in the table are in 2099. For example, the reading view of the Akşam
section after the first change coming from the main note is as follows:

```markdown
### Mavi Pusula — Akşam

- **Görüşme tarihi:** 7 Nisan 2099 _(düzenlenebilir)_

**Kişisel notum:** yol süresini ve adresi sor
```

In the real output the subheading opens the [correct main note](vault/notes/Kariyer/Aksam.md).
Gündüz's separate file and the original invitation stay the same in the first two
changes.

An edit in the source note passes to the page, and an editable cell on the page passes
to the correct source note. The other record and the original invitation file are
kept. After the source is written, the script cuts the synchronization with a hook
used only for the example. The next `sync` completes the page without rewriting the
source; it keeps the latest personal note updated in between. The script compares the
bytes and the pinned mtime of the main note before/after exactly this first recovery;
rewriting the same bytes also fails the test. The real product has no interruption
hook.

In the interruption step, the 9 April value on the page is first changed to 11 April.
After the main note is written as 11 April, and before the page's synchronization
record is completed, the process is stopped. At that moment the user changes their
personal note to "adresi ve giriş kapısını sor" ("ask about the address and the
entrance door"). The next `sync` completes the work, keeping both the 11 April and
this last note.

When the Akşam date is made **12 April** in the main note and **13 April** on the page,
the conflict is reported only for this field. The Gündüz date becomes **8 April** in
the same synchronization. The example writes **12 April**, the source value, into the
Akşam cell and synchronizes again. Running `sync` again on unchanged Markdown
preserves both the file bytes and the modification time.

This last check also includes repeating `homepage-create`: the same selection returns
`unchanged` and does not rewrite the personal page layout. For the keyed `note-edit`
repeat, the final hash and a real user edit, there are separate
[regression tests](../../WORKSPACE-HOMEPAGES.md#regression-verification-and-open-acceptance-limits);
the no-write `sync` acceptance in this example does not replace that separate check.

## Derslerim ("My Courses"): general navigation page

Made-up course notes, source texts and work files are created for **Bulut Bahçeleri**
(Cloud Gardens), **Ses Haritaları** (Sound Maps) and **Işık Atölyesi** (Light
Workshop). The general page gives relative links to the course notes, the original
sources and the assignment files. The existence of a file does not mean an open task
or a submission obligation.

Example user request: "I'd like to be able to open all my sources and assignment files
from a general page. There should also be room for submission information, a plan and
a personal note." This purpose does not require a particular course to be selected or
a date to be produced.

| Fictional course note | Original source | Assignment/work file |
| --- | --- | --- |
| [Bulut Bahçeleri](vault/notes/Dersler/Bulut-Bahceleri.md) | [Kaynak.txt](vault/sources/Ornek-Dersler/Bulut-Bahceleri/Kaynak.txt) | [Calisma-Dosyasi.txt](vault/sources/Ornek-Dersler/Bulut-Bahceleri/Calisma-Dosyasi.txt) |
| [Ses Haritaları](vault/notes/Dersler/Ses-Haritalari.md) | [Kaynak.txt](vault/sources/Ornek-Dersler/Ses-Haritalari/Kaynak.txt) | [Calisma-Dosyasi.txt](vault/sources/Ornek-Dersler/Ses-Haritalari/Calisma-Dosyasi.txt) |
| [Işık Atölyesi](vault/notes/Dersler/Isik-Atolyesi.md) | [Kaynak.txt](vault/sources/Ornek-Dersler/Isik-Atolyesi/Kaynak.txt) | [Calisma-Dosyasi.txt](vault/sources/Ornek-Dersler/Isik-Atolyesi/Calisma-Dosyasi.txt) |

The normal note writer creates one general page and three course notes. From the
general page both the course note and the original files can be reached; in the course
note, the source and the assignment file appear under separate headings. The originals
of the sources stay in place.

![General Markdown preview of the Derslerim page](lessons.png)

*Derslerim: a general preview of the generated Markdown; it is not a real Obsidian screenshot.*

[lessons-homepage.md](lessons-homepage.md) shows the general navigation page,
[lessons-course.md](lessons-course.md) the Bulut Bahçeleri note. This example uses the
normal `note-create` and `note-edit` flow. Because there is no verified submission
date, progress or selected study order, it does not produce them; the personal note is
updated only with the given text. The original files are kept.

The real output of the general page after the file links:

```markdown
## Teslimler

Henüz doğrulanmış bir teslim bilgisi verilmedi.

## Çalışma planım

Henüz bir ders veya çalışma sırası seçilmedi.

## Kişisel notum

Kaynak bağlantıları burada toplu dursun; teslim bilgisi gelince ilgili ders notuna ekle.
```

(In English: "Submissions: no verified submission information has been given yet."
"My study plan: no course or study order has been selected yet." "My personal note:
keep the source links together here; add the submission information to the relevant
course note when it arrives.")

The final personal note comes from editing the first sentence, "Kaynak bağlantıları
burada toplu dursun." ("Keep the source links together here."), with a normal
`note-edit`. After that, `sync` and a no-write repeat are checked. No task is created,
no submission date is assigned, no particular course is selected and no progress is
calculated. Because there are no `facts` or linked cells, no automatic value update
from the source is claimed for this navigation page.

## Request example

The conversation below is **only an explanatory draft**; the script is not an
end-to-end test in which an agent interprets a conversation with the user and acts.

> **User intent:** "I want to see the dates of my Akşam and Gündüz interviews on the
> Kariyerim page and be able to correct them from there. I'd also like to add my own
> note."
>
> **Suggested draft:** "I'll link the interview-date field of the two existing records
> to the page. I'll synchronize the dates with the main notes; I'll keep your personal
> note on the page."

For the scope of the setup and the `homepage-create` request format, see the
[feature document](../../WORKSPACE-HOMEPAGES.md).
