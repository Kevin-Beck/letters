# Letter Viewer: Design

This document describes the browser viewer for the TBF1 Navy Letters: what
data it uses, what files need to be created, and how each part of the
screen works.

The viewer is a single file, `viewer.html`, in the project folder. It holds
all its HTML, CSS, JavaScript and letter data. The scan images stay in
`scans/` and are loaded from there. Double-clicking `viewer.html` opens it in
any modern browser, with no web server, no internet connection and no
installation.

---

## 1. What the viewer does

The screen has three parts:

1. **Timeline** across the top. It spans July 1942 to August 1945, in four
   rows: **World** (major events of the war), **Where** (where Tom was, with
   how sure that is), **Service** (his assignments, ships and battle credits)
   and **Letters** (a dot for each letter). Clicking a dot opens that letter.
2. **Letter view** below the timeline, in two columns:
   - **Scan** (left): the original letter, one page at a time.
   - **Transcript** (right): the typed text of the letter. Words that have
     background notes are underlined.
3. **Info card**: hovering over an underlined word shows a card with notes
   about that person, ship, place, event or term, like a Wikipedia link
   preview. Clicking the word pins the card open so its links can be used.

Scrolling the transcript turns the scan to the page being read. Clicking a
page number beside the scan scrolls the transcript to that page.

---

## 2. What exists

All paths are relative to the project folder.

### 2.1 `data/letters.json` (the index)

Top-level fields used by the viewer:

| Field | Content |
|---|---|
| `collection` | Title of the collection |
| `content_warning` | One paragraph on the period language kept in some letters |
| `timeline` | Service row: 16 strings, each a date prefix, spaces, then text, e.g. `"1942-07-22  Sworn in as midshipman"`. Date prefixes take four forms: `1942-07-22`, `1944-04`, `1945-04/05`, `1943-2H` |
| `locations` | Where row: 30 objects `{start, end, place, confidence, detail}` with ISO dates. 25 are periods, which follow each other without overlapping; 5 have `start` equal to `end` and mark a specific place on a specific day. `confidence` is `confirmed`, `probable` or `speculative` |
| `world_events` | World row: 20 strings in the same format as `timeline` |
| `people` | Family guide: name → one-paragraph description |
| `letters` | 116 letter records |
| `rescan_types` | Descriptions of the three `rescan` item types |

Fields of each letter record used by the viewer:

| Field | Content |
|---|---|
| `id` | e.g. `1943-01-24_tom-to-mother`. Starts with `YYYY-MM-DD`, `YYYY-MM-xx`, `YYYY-winter` or `undated` |
| `written_by`, `written_to` | Free text, e.g. `"Tom (Ens. Thos. F. Beck)"`, `"Mother"` |
| `date` | Free text: `"1943-01-24"`, `"1942-11-04 (probable)"`, `"1942-11 (a Wednesday)"`, `"1945-01/02 (approximate; a Saturday)"`, or `null` for 5 undated letters |
| `date_source` | How the date was worked out |
| `other_dates_mentioned` | List of strings |
| `location` | Where it was written |
| `complete` | `false` for 5 letters with pages that were never scanned |
| `notes` | One-paragraph summary of the letter |
| `pages` | List of `{page, file, original_file, width, height}`; `file` is `scans/<id>_pNN.jpg`. 1 to 6 pages per letter, 267 in all |
| `rescan` | Present on 17 letters: list of `{type, page \| after_page, reason}` |

### 2.2 `transcriptions/<id>.txt`

One per letter. Plain text in UTF-8. It contains only ASCII apart from the
characters `°` and `¢`, which count as one character in both Python and
JavaScript. Each file has:

- a **header** (Letter, Date, Source images, Status, conventions). Some
  headers include a paragraph starting `NOTE:` about offensive period
  language (7 letters);
- a line of `=` signs ending the header;
- the **body**: the letter text. It keeps the original line breaks and uses
  spaces for layout, for example right-aligned dates.

The body contains **page markers** on lines of their own, in three forms:

| Marker | Meaning |
|---|---|
| Contains `<id>_pNN.jpg`, e.g. `[--- sheet 1 back: 1943-04-15_tom-to-mother_p02.jpg ---]` | Page NN starts here |
| `[--- page 1 ---]`, `[--- page 2 ---]` (1945-05-08 letter only) | Page N starts here |
| Any other, e.g. `[--- MIDDLE PAGE MISSING FROM ALL SCANS ---]` | A gap in the letter, not a page change |

Five one-page letters have no markers at all.

The transcriptions use these markings: `[?]` for an uncertain reading,
`[illegible]`, `[crossed out]` and `[crossed out: word]`, and `[bracketed
letters]` for text restored at a scan edge.

### 2.3 `annotations/annotations_resolved.json`

Built by `annotations/build_annotations.py`. It has:

- `entities`: 274 glossary entries keyed by id (`ship.lci-l-62`,
  `person.tom-beck`, …). Every entry has `id`, `type`, `name`, `summary` and
  `confidence`. Some also have `aliases`, `wikipedia`, `see_also` (list of
  entity ids), `dates`, `coords`, `sources` (list of `{title, url}`) and
  `detail`.
  - `type` is one of `ship`, `place`, `person`, `organization`, `military`,
    `event`, `culture`, `term`.
  - `confidence` is one of `confirmed`, `probable`, `speculative`.
- `letters`: a map from `<id>.txt` to a list of 702 annotations in all. Each
  annotation is `{id, start, end, text, kind, entity?, note?, confidence?}`.
  - `start` and `end` are character offsets into the whole `.txt` file, with
    `end` exclusive.
  - Spans within a letter are sorted and never overlap.
  - Every annotation has an `entity` or a `note`, or both.
  - `kind` is one of `reference`, `context`, `inference`, `content-note`,
    `transcription`.
  - Three annotation spans contain a page marker, for example the words
    either side of a page break.

### 2.4 `scans/`

267 JPEG files named `<id>_pNN.jpg`, about 2000 × 3000 pixels and 1–2 MB
each, 365 MB in all.

### 2.5 `tools/check_project.py`

Checks that the files and the index agree. Section 9 describes the changes it
needs.

---

## 3. What needs to be created

| File | What it is |
|---|---|
| `viewer.html` | The viewer: HTML, CSS and JavaScript written by hand, plus one embedded data block written by the build script |
| `tools/build_viewer.py` | Reads the data in section 2, turns it into the viewer data (section 4), and writes it into the data block of `viewer.html` |
| Changes to `tools/check_project.py` | Checks that the viewer's embedded data is up to date (section 9) |
| Changes to `README.md` | Adds `viewer.html` and `tools/build_viewer.py` to the folder table, and how to rebuild the data |

`viewer.html` uses no external libraries, fonts or network requests.

---

## 4. Embedded data

### 4.1 Where it goes

`viewer.html` contains exactly one data block:

```html
<script id="letters-data" type="application/json">
{ ...viewer data... }
</script>
```

`tools/build_viewer.py` replaces everything between the opening and closing
tags and leaves the rest of the file untouched. It writes the JSON with
`ensure_ascii=False` in UTF-8, and replaces every `</` with `<\/` so the data
can't close the script tag early. At startup the page reads the data with
`JSON.parse(document.getElementById('letters-data').textContent)`.

The embedded data is about 800 KB.

### 4.2 Viewer data format

```json
{
  "built": "2026-09-27T12:00:00",
  "collection": "TBF1 Navy Letters - WWII letters of Ens. Thomas Frazier Beck, USNR",
  "content_warning": "...",
  "range": {"start": "1942-07-01", "end": "1945-08-31"},
  "events": [
    {"start": "1942-07-22", "end": "1942-07-22", "text": "Sworn in as midshipman"},
    {"start": "1944-03-01", "end": "1944-04-30", "text": "Relieved after about 13 months overseas; returns to the U.S."}
  ],
  "locations": [
    {"start": "1943-02-10", "end": "1943-02-24", "place": "Panama Canal Zone (censored 'foreign port')", "confidence": "probable", "detail": "..."},
    {"start": "1943-07-04", "end": "1943-07-04", "place": "Rendova: Japanese air attack on Flotilla Five", "confidence": "probable", "detail": "..."}
  ],
  "world": [
    {"start": "1944-06-06", "end": "1944-06-06", "text": "D-Day: Allied invasion of Normandy"}
  ],
  "people": { "Tom": "...", "Mother": "..." },
  "entities": { "ship.lci-l-62": { ...entity as in annotations_resolved.json... } },
  "letters": [
    {
      "id": "1943-01-24_tom-to-mother",
      "title": "Tom to Mother",
      "written_by": "Tom",
      "written_to": "Mother",
      "by_tom": true,
      "date": "1943-01-24",
      "date_label": "January 24, 1943",
      "sort_date": "1943-01-24",
      "approximate": false,
      "date_source": "...",
      "other_dates_mentioned": ["..."],
      "location": "...",
      "complete": true,
      "notes": "...",
      "content_note": null,
      "rescan": [],
      "pages": [{"page": 1, "file": "scans/1943-01-24_tom-to-mother_p01.jpg", "width": 2183, "height": 3216}],
      "body": "\n[--- 1943-01-24_tom-to-mother_p01.jpg ---]\n\n...",
      "markers": [
        {"start": 1, "end": 43, "type": "page", "page": 1},
        {"start": 2210, "end": 2262, "type": "gap", "text": "MIDDLE PAGE MISSING FROM ALL SCANS"}
      ],
      "annotations": [
        {"id": "a1", "start": 510, "end": 542, "text": "Our ship was commissioned Friday", "kind": "reference", "entity": "ship.lci-l-345", "note": "USS LCI(L)-345 was commissioned Friday, Jan. 22, 1943."}
      ]
    }
  ],
  "mentions": { "ship.lci-l-62": ["1943-01-24_tom-to-mother", "..."] }
}
```

### 4.3 How `build_viewer.py` fills each field

**Letters**
- `letters` are sorted by `sort_date`, then by `id`. The five letters with
  no `sort_date` come last, sorted by `id`.
- `title` is `written_by` with any text from ` (` onward removed, then
  ` to `, then `written_to`. Example: `"Tom (Ens. Thos. F. Beck)"` and
  `"Mother"` give `"Tom to Mother"`. `written_by` in the viewer data is
  shortened the same way.
- `by_tom` is true when `written_by` starts with `Tom`.

**Dates**
- `sort_date` comes from the `id` prefix:
  - `YYYY-MM-DD` gives that date;
  - `YYYY-MM-xx` gives `YYYY-MM-15`;
  - `YYYY-winter` gives `YYYY-01-15`;
  - `undated` gives `null`;
  - `SORT_DATE_OVERRIDES` in the script sets it for letters whose id says
    `undated_` but whose content dates them well enough for the timeline.
    It has one entry: `undated_george-to-mother-allegheny` ("1942 or 1943
    (fall; a Friday)", probably the start of the fall 1942 term) is placed at
    `1942-09-15`. Being approximate, it is drawn hollow.
- `approximate` is true when `date` is anything other than exactly
  `YYYY-MM-DD`, including `null`.
- `date_label` is built from `date`:
  - if it starts with `YYYY-MM-DD`, that part becomes `Month D, YYYY` and
    the rest is kept, e.g. `"November 4, 1942 (probable)"`;
  - any other text is kept as it is, e.g. `"1942-11 (a Wednesday)"`;
  - `null` becomes `"Undated"`.

**Text**
- `content_note` is the header paragraph that starts with `NOTE:`, with its
  lines joined by single spaces. It is `null` when there isn't one.
- `body` is the file text after the line of `=` signs (the first match of
  `^={10,}\n`). Annotation offsets are shifted by the length of the header.
  For every annotation the script checks that `body[start:end] == text`.
- `markers` lists every line matching `^\[---(.*?)---\]$` in `body`, with its
  offsets:
  - a marker containing `<id>_pNN.jpg` becomes type `page` with `page` NN;
  - a marker whose inner text is exactly `page N` becomes type `page` with
    `page` N;
  - any other marker becomes type `gap`, with `text` set to its inner text,
    trimmed.
- The script checks the number of `page` markers: it must equal the number
  of pages, or be zero when the letter has one page.

**Timeline rows.** `events` (the Service row) and `world` are built from the
index's `timeline` and `world_events` strings as described below. `locations`
is copied from the index, sorted by date. The script checks that every
location has a valid `confidence` and ISO dates inside `range`, and that no
two periods overlap.

**Timeline strings** are parsed as follows. The date
prefix is the first run of non-space characters, and the text is everything
after the spaces that follow it:

| Prefix | `start` | `end` |
|---|---|---|
| `YYYY-MM-DD` | that date | same date |
| `YYYY-MM` | first of the month | last of the month |
| `YYYY-MM/MM` | first of the first month | last of the second month |
| `YYYY-2H` | `YYYY-07-01` | `YYYY-12-31` |

**Mentions** maps each entity id to the ids of the letters that have an
annotation linked to it, in letter order.

**Checks.** The script stops with an error if any check above fails, or if
any text contains a character outside the Basic Multilingual Plane. That
guarantees JavaScript string offsets equal the Python offsets.

---

## 5. Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ TBF1 Navy Letters          [World][Where][Service]  ⓘ  ◀ Prev   Next ▶    │  top bar
├──────────────────────────────────────────────────────────────────────────┤
│ World    ▕ Guadalcanal    ▕ Torch            ▕ Stalingrad        │       │
│ Where   ▕▔▔▔ New York ▔▔▔▏▕▔▏▕▔ Solomons ▔▏▕▔▏▕▔ Houston ▔▏▕▔ at sea │       │
│ Service  ▕ Reports       ▕ Commissioned     ▕ Transferred to #62  │       │
│ Letters  ●●●●● ●●●  ●●○○●●●  ●●●    ●  ●   ●      ●     ●   ●●  │Undated│ │  timeline
│          Jul  Aug  Sep  Oct  Nov  Dec │1943 Jan ...              │ ● ● ● │ │
├──────────────────────────────────┬───────────────────────────────────────┤
│ Tom to Mother                    │                                       │
│ January 24, 1943 · Houston, TX   │  letter header (spans both columns)   │
│ [Incomplete] [Content note]  About this letter ▸                         │
├──────────────────────────────────┼───────────────────────────────────────┤
│  ┌────────────────────────────┐  │  [--- page 1 ---]                     │
│  │                            │  │                       Jan. 24, 1943   │
│  │        scan image          │  │  Dear Mother,                         │
│  │                            │  │     I am sorry I slacked off on       │
│  │                            │  │  writing ... Our ship was commissioned│
│  └────────────────────────────┘  │                        ┌────────────┐ │
│      Page  [1]  2   of 2         │                        │ info card  │ │
└──────────────────────────────────┴────────────────────────┴────────────┴─┘
```

- The top bar, timeline and letter header are fixed in height. The two
  columns fill the rest of the window, and each scrolls on its own.
- The scan column is 45% wide and the transcript column 55%.
- Below 900 px wide, the columns stack: scan first, then transcript, and the
  whole page scrolls.

---

## 6. Components

### 6.1 Timeline

**Axis**
- The axis runs from `range.start` to `range.end` at **4 px per day**,
  about 120 px per month and 4,400 px in all.
- The timeline area is one screen wide and scrolls sideways.
- Month ticks carry three-letter names. At every January, and at the start
  of the axis, the year appears in bold.

**Rows.** From the top: World, Where, Service, then the Letter lane. The
first three are drawn by the same code and differ only in colour:

| Row | Data | Look |
|---|---|---|
| World | `world` | Grey flags and labels, so they read as background |
| Where | `locations` | Green-tinted bands (alternating green and sand so neighbours are distinct) and green flags. **Confidence:** a `confirmed` band is solid; `probable` is faded with a dashed edge; `speculative` is striped. A flag for an inferred place has a dashed pole. Labels of uncertain places are italic, and the tooltip adds "(probable)" or "(speculative)" and the `detail` |
| Service | `events` | Navy flags and blue-grey bands |

A dashed rule separates the rows. The label column on the left names each
row. The **World**, **Where** and **Service** buttons in the top bar show or
hide those rows. The choice is kept in `localStorage` (per browser), and the
page works normally if storage is unavailable.

**Each row**
- Each event is drawn at its dates:
  - a one-day event is a 2 px vertical line with a small flag;
  - a longer event is a shaded band covering its dates.
- The label sits beside the flag or at the start of the band. Several
  one-day events are only days apart (Nov–Dec 1942), so labels are
  **staggered** over as many rows as they need (with the current data:
  World 2, Where 6, Service 5; up
  to a limit of 12): each label goes in the lowest row where it fits in
  full, so no label overlaps another or is cut short. Only past the 12-row
  limit is a label cut short with an ellipsis before the next event in its
  row. Labels have an opaque background so the flag poles from upper rows
  pass behind them. Hovering shows the dates and full text in a tooltip.

**Letter lane** (below the Service row)
- Each dated letter is a 10 px circle at `sort_date`:
  - filled navy for letters by Tom (`by_tom`);
  - filled dark red for letters from other family members;
  - hollow, with the same outline colour, when `approximate` is true.
- **Stacking:** letters are placed in `letters` order. Each circle goes in
  the lowest row whose last circle is at least 16 px to its left. Rows are
  17 px apart, so circles never touch. The lane
  grows to fit the tallest stack.
- **Undated letters** (no `sort_date`) are in a separate box at the right end of the
  timeline, labelled "Undated", with the same circle styles in one row.
- Hovering a circle shows a tooltip with the `title` and `date_label`.
- Clicking a circle opens that letter.
- The open letter's circle is 14 px, with a 2 px ring in the accent colour.
- Opening a letter scrolls the timeline so its circle is centred, unless it
  is already visible.

### 6.2 Top bar

- The collection title.
- **◀ Prev** and **Next ▶** step through `letters` in order. They are
  disabled at the first and last letter.
- **World**, **Where** and **Service** toggle buttons show or hide those
  timeline rows (section 6.1).
- A **ⓘ** button opens a dialog with `content_warning`, the transcription
  conventions from section 2.2, a key to the timeline rows, and the `people`
  guide.

### 6.3 Letter header

- **Line 1:** `title`, in a serif heading.
- **Line 2:** `date_label` · `location`.
- **Line 3:** badges, shown only when they apply:
  - **Incomplete** when `complete` is false;
  - **Date approximate** when `approximate` is true;
  - **Content note** when `content_note` is set.
- **About this letter ▸** expands a panel under the header with:
  - `notes`;
  - "How the date was worked out:" followed by `date_source`;
  - "Other dates mentioned:" followed by a list, if there are any;
  - "Rescan needed:" followed by one line per `rescan` item, e.g. "Page 1:
    Bottom line cut off at the scan edge" or "After page 3: Back of sheet
    "-2-" was never scanned", if there are any.
- When `content_note` is set, a pale yellow notice bar at the top of the
  transcript shows its text.

### 6.4 Scan viewer

**Showing a page**
- The current page image is scaled to the column width, and never taller
  than the column. It sits on a neutral grey background.
- Below the image is the page picker, `Page [1] 2 3 of 3`. Each number is a
  button, and the current page is highlighted.
- Only the current page's image is loaded, plus the next page's in the
  background.
- A missing image shows a grey box with the text "Scan not found:
  scans/<file>".

**Full size**
- Clicking the image opens it full screen at full resolution, on a dark
  backdrop.
- Mouse wheel and trackpad scroll the image, and dragging pans it.
- **Esc**, the × button, or a click on the backdrop closes it.

### 6.5 Transcript

The transcript is one `<div class="transcript">` using
`white-space: pre-wrap` in a monospace font. This keeps the line breaks and
the spaces the transcriptions use for layout. The body is rendered as
follows:

1. Collect cut points: `0`, `body.length`, and the `start` and `end` of every
   marker and annotation. Sort them and remove duplicates.
2. Walk the pieces between neighbouring cut points in order. For each piece:
   - **Inside a marker:**
     - at the marker's start, emit the marker element. A `page` marker becomes
       `<div class="page-break" data-page="N">Page N</div>`, a full-width rule
       with the label centred. A `gap` marker becomes `<div class="gap">…</div>`,
       its text in italics between em dashes, in grey;
     - skip the marker's text.
   - **Inside an annotation:** emit
     `<span class="ann k-<kind> c-<confidence>" data-ann="<id>" tabindex="0">`
     containing the piece's text. When a marker splits an annotation, each
     part gets its own `<span>` with the same `data-ann`.
   - **Otherwise:** emit a text node.
3. Text before the first `page` marker belongs to page 1. So does the whole
   body when there are no markers.

**Styling annotated words.** The effective confidence is the annotation's
`confidence`, else its entity's `confidence`, else `confirmed`.

| Annotation | Style |
|---|---|
| `reference`, `context`, `transcription` with confirmed confidence | Solid 1 px accent-coloured underline |
| `inference`, or effective confidence `probable` or `speculative` | Dotted 1 px accent-coloured underline |
| `content-note` | No underline. A small superscript `†` after the span; hovering or focusing either one opens the card |

Hovering or focusing a span gives all its parts a pale accent background.

**Keeping the scan in step**
- An `IntersectionObserver` watches every `.page-break`. The current page is
  the last page break above the top third of the transcript column, or page 1
  if none is. When it changes, the scan viewer shows that page.
- A short last page can't scroll up to the top third, so when the transcript
  is scrolled to the bottom, the current page is the last page break that
  is on screen. A scroll listener (once per animation frame) handles this,
  since no page break crosses the line there.
- The transcript has 50vh of padding below the text, so every page break
  can be scrolled to the top.
- Clicking a page number in the scan viewer scrolls the transcript so that
  page's `.page-break` is at the top. Page 1 scrolls to the top of the
  transcript.

### 6.6 Info card

One card element, reused for every annotation.

**Opening and closing**
- **Hover:**
  - pointing at a span for 150 ms opens the card for that annotation;
  - moving the pointer off both the span and the card for 250 ms closes it;
  - the pointer can move from the span into the card without it closing.
- **Keyboard focus** on a span opens the card straight away, and moving
  focus away closes it.
- **Pinning:**
  - clicking a span (or pressing **Enter** on it) pins the card. It shows a
    × button and stays open until the × button, **Esc**, a click outside the
    card, or a click on another span;
  - clicking another span moves the pinned card to that annotation;
  - on touch screens a tap pins the card.

**Position**
- The card is 360 px wide, or the window width minus 32 px if that is
  smaller.
- It sits 8 px below the span's first line, left-aligned with the span, and
  stays inside the window.
- When there isn't room below the span, it sits above it.

**Content, top to bottom**
1. **Note**, if the annotation has one. A small label above it:
   - "Inference" for `inference`;
   - "Content note" for `content-note`;
   - "About the transcription" for `transcription`;
   - no label for `reference` and `context`.

   Then each of the annotation's `images` (see `annotations/README.md`) as a
   thumbnail with its caption. Clicking one opens it full size in the same
   viewer as the scans.
2. **Entity**, if the annotation has one:
   - `name` in bold, with a small type label (Ship, Person, Place,
     Organization, Military, Event, Culture, Term);
   - `dates`, if present;
   - a confidence label when the effective confidence isn't `confirmed`:
     "Probable" in amber, "Speculative" in orange;
   - `summary`.
3. **Pinned cards only**, below the summary:
   - `detail`, if present;
   - **See also:** the names of the `see_also` entities as links. Clicking
     one shows that entity in the same card, with a "◀ Back" link to return;
   - **Wikipedia** and each of `sources` as links, opening in a new tab;
   - **Mentioned in:** the other letters in `mentions[entity]`, listed by
     `title` and `date_label`. Clicking one opens that letter and closes the
     card.

When a card has both a note and an entity, the note comes first, then a thin
rule, then the entity. This follows `annotations/README.md`.

---

## 7. Navigation and state

- **Opening a letter:**
  - sets `location.hash` to the letter's `id`;
  - renders the header, scan viewer and transcript;
  - shows page 1 and scrolls the transcript to the top;
  - closes any card;
  - centres the letter in the timeline.
- **On load:** the viewer opens the letter named in `location.hash`. If there
  is none, or it isn't a known letter, it opens the first letter in `letters`.
- A `hashchange` listener opens the named letter, so the browser's back and
  forward buttons move between letters.
- **Keyboard:**
  - **←** and **→** open the previous and next letter, unless focus is in
    the card;
  - **Esc** closes the full-size scan, then the pinned card.
- Only the open letter is in the page at any time. Opening a letter replaces
  the scan viewer and transcript contents.

---

## 8. Visual style

CSS custom properties on `:root`:

| Token | Value | Use |
|---|---|---|
| `--paper` | `#f6f1e7` | Page background |
| `--panel` | `#fffdf8` | Transcript, header and card background |
| `--ink` | `#1f1f1f` | Text |
| `--muted` | `#6b6458` | Secondary text, gap markers, month ticks |
| `--accent` | `#1f3a5f` | Navy: links, underlines, Tom's dots, selected ring |
| `--family` | `#8a2f2f` | Dark red: dots for letters not by Tom |
| `--band` | `#dfe6ee` | Service-lane bands |
| `--notice` | `#fff4cc` | Content-note bar |
| `--scan-bg` | `#d9d6d0` | Behind the scan image |

- **Fonts** (system fonts only):
  - headings in `Georgia, "Times New Roman", serif`;
  - interface text in `system-ui, sans-serif`;
  - transcript in `ui-monospace, "Courier New", monospace` at 15 px with a
    line height of 1.5.
- **Cards and dialogs:** 6 px corner radius, 1 px `--muted` border at 30%
  opacity, and a soft shadow.
- Focused elements get a 2 px `--accent` outline.

---

## 9. Build and check workflow

- After changing anything in `data/`, `transcriptions/` or `annotations/`:
  1. run `python3 annotations/build_annotations.py` (only when annotations or
     transcriptions changed);
  2. run `python3 tools/build_viewer.py`;
  3. run `python3 tools/check_project.py`.
- `tools/build_viewer.py` has one function, `build_data()`, that returns the
  viewer data as a Python object. The script's main block calls it and writes
  the result into `viewer.html`.
- `tools/check_project.py` changes:
  - add `viewer.html` to the expected top-level items (`Viewer_design.md` is
    already there);
  - import `build_data()` from `tools/build_viewer.py`, read the embedded
    block from `viewer.html`, and compare the two with the `built` field
    removed from both. If they differ, report "viewer.html data is out of
    date; run tools/build_viewer.py".

---

## 10. Acceptance checklist

The viewer is done when all of the following are true, opening `viewer.html`
straight from disk in current Chrome, Firefox and Safari:

- [ ] The page opens with no console errors and no network requests other
      than images in `scans/` and `additional_context/`.
- [ ] The timeline shows all 111 dated letters in date order (including the
      George letter placed at fall 1942), plus 5 in the Undated box. Approximate dates are hollow circles. All 20
      world events, 30 locations and 16 service events are visible, and
      every label shows in full without overlapping another.
- [ ] The World, Where and Service buttons hide and show their rows, and the
      choice survives a reload.
- [ ] Clicking any circle opens that letter, and the URL hash changes to its
      id.
- [ ] Reloading the page reopens the same letter. Back and Forward move
      between letters.
- [ ] For every letter, the scan viewer's page count matches `pages`, and
      every image loads.
- [ ] Scrolling through a multi-page letter (e.g. `1943-04-15_tom-to-mother`)
      turns the scan at each page break. Clicking a page number scrolls the
      transcript to it.
- [ ] Gap markers show as italic notices and don't change the page.
- [ ] Every annotation is underlined (or marked `†`), and the underlined
      text equals its `text`. The three annotations that cross a page break
      highlight both parts together.
- [ ] Hovering shows the card, and moving into the card keeps it open.
      Clicking pins it. Esc and clicking outside close it.
- [ ] See also, Wikipedia, sources and Mentioned in links work from a pinned
      card.
- [ ] The 7 letters with a `NOTE:` show the content-note bar. The 5
      incomplete letters show the Incomplete badge, and the 17 letters with
      `rescan` items list them under About this letter.
- [ ] At 800 px wide the columns stack and nothing scrolls sideways except
      the timeline.
- [ ] `python3 tools/check_project.py` reports OK.

---

## 11. Not included

These are outside this design:

- full-text search;
- a map (21 entities have `coords` for it);
- a glossary page listing every entity;
- editing annotations in the browser;
- dark mode;
- printing.
