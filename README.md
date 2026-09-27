# TBF1 Navy Letters: WWII Letters of Ens. Thomas Frazier Beck

This folder holds scanned letters written by **Thomas Frazier "Tom" Beck** of
Karns City, Pennsylvania during his U.S. Navy service in World War II
(1942–1945). Most are to his mother, Elva Beck (Mrs. John A. Beck). There are
also a few family letters, a telegram, V-mail forms, and a newspaper clipping.

In September 2026 every scan was read and typed out, so the letters can be
read, searched, and shared without the images. The folder was then
reorganized so that every letter has one set of scans, one transcription and
one set of notes, all with matching names. To read them, open
`viewer.html` (see [Reading the letters](#reading-the-letters)).

## What's in this folder

| Location | What it is |
|---|---|
| `scans/` | The best scan of every page: 267 pages from 116 letters |
| `transcriptions/` | The typed text of each letter, one file per letter |
| `additional_context/` | Other material the notes refer to, such as the Time magazine page Tom recommended in Nov. 1942 |
| `annotations/` | Background notes on the people, ships, places and events in the letters (see `annotations/README.md`) |
| `data/letters.json` | The index: every letter's date, writer, recipient, location, pages and notes |
| `photos/` | Family photographs (not letters; not transcribed) |
| `delete/` | Duplicate scans and old drafts. **Safe to delete** (see `delete/README.md`) |
| `viewer.html` | The letter viewer: open it in a browser to read the letters (see below) |
| `tools/build_viewer.py` | Rebuilds the letter data inside `viewer.html` |
| `tools/check_project.py` | Checks that the files, the index and the viewer agree |
| `Viewer_design.md` | Design for `viewer.html` |
| `rename_log.csv` | Every file's old name and new name from the reorganization |

## Reading the letters

Double-click `viewer.html`. It opens in any modern browser (Chrome, Firefox,
Safari, Edge) with no internet connection, installation or web server. Keep
it in this folder, next to `scans/`, because it loads the scan images from
there.

- **Timeline** (top), in four rows:
  - **World**: major events of the war, for comparison.
  - **Where**: where Tom was. His letters from Feb. 1943 to spring 1944 were
    censored, so most of those places are worked out from clues and from
    his ship's record. Solid blocks are confirmed, faded ones probable, and
    striped ones reasoned guesses.
  - **Service**: his assignments, ships and battle credits.
  - **Letters**: each dot is a letter. Navy dots are Tom's letters, red dots
    are from other family members, and hollow dots have approximate dates.
    Click a dot to open that letter. Five undated family letters, which
    don't belong on the timeline, are left out of the viewer (see below).

  The **World**, **Where** and **Service** buttons in the top bar hide or
  show those rows.
- **Scan** (left) and **transcript** (right). Scrolling the transcript turns
  the scan to the page you're reading. Click a page number to jump to it,
  and click the scan to see it full size.
- **Underlined words** have background notes. Point at one to preview the
  note, or click it to pin the note open and follow its links. A dotted
  underline means the note is a guess. A † marks a note on offensive period
  language.
- **◀ Prev / Next ▶**, or the ← and → keys, step through the letters in date
  order. Each letter has its own web address, so you can bookmark one or use
  the browser's Back button.
- **ⓘ** shows the transcription conventions and a guide to the family.

## How files are named

Every letter has an **id** made from its date and a short description, in
lowercase with hyphens:

```
1943-01-24_tom-to-mother
```

That id is used everywhere for the letter:

| File | Name |
|---|---|
| Scan of page 1 | `scans/1943-01-24_tom-to-mother_p01.jpg` |
| Transcription | `transcriptions/1943-01-24_tom-to-mother.txt` |
| Annotations | `annotations/letters/1943-01-24_tom-to-mother.json` |

- Sorting by name puts the letters in date order.
- Pages are numbered in reading order: `_p01`, `_p02`, and so on.
- If only part of a date is known, the unknown parts stay as letters, as in
  `1942-11-xx_…` and `1945-winter_…`. Letters with no date start with
  `undated_`.
- Names use only lowercase letters, numbers and hyphens, so they are safe to
  use in web addresses.

## The index (`data/letters.json`)

For each letter the index lists:

- its id, date, and how the date was worked out;
- who wrote it, who it was to, and where it was written;
- whether any pages are missing;
- whether it appears in the viewer: `"viewer": false` leaves a letter out
  of `viewer.html` but keeps its scans, transcription and notes in the
  project. The five undated family letters (not George's Allegheny letter,
  which can be dated to about fall 1942) are marked this way;
- notes on the people and events it mentions;
- its pages, in order. Each page has its scan, its width and height, and
  its **original filename** from before the reorganization;
- for letters with pages that should be rescanned, a `rescan` list (see
  [Pages to rescan](#pages-to-rescan)).

The index also has a short family guide (`people`), a timeline of Tom's
service (`timeline`), where he was and how sure that is (`locations`), and
major world events for comparison (`world_events`).

All paths in the index are relative to this folder.

## The transcriptions

Each text file starts with a header (date, source scans, completeness),
followed by the letter, page by page. A line like
`[--- 1943-01-24_tom-to-mother_p02.jpg ---]` marks where each page begins.

### How the transcriptions were written

- Spelling and grammar are kept exactly as written.
- `[?]` marks a word that was hard to read, and `[illegible]` marks one that
  couldn't be read.
- `[crossed out]` marks text Tom struck through.
- `[bracketed letters]` are letters cut off at the edge of a scan.
- A few letters contain racist or antisemitic language that was common at
  the time. It has been kept as written, as part of the historical record,
  and each affected file has a note at the top.

## Things to know about the scans

- **The letters used to be spread over three folders:** the main folder,
  `TBF1Adobe/Adobe finished/` (a cleaned-up set) and `TBF0defective/` (loose
  pages). Most pages had been scanned two or three times under different
  names. Some were misdated or misfiled. For example, `420716*` is really a
  November 1942 letter.
- **Only the best copy of each page is in `scans/`.** Duplicate scans were
  matched by comparing the images themselves, not by filename, and the copy
  with the highest resolution was kept. When two copies were the same size,
  the cleaned-up Adobe scan was kept. The rest are in `delete/scans/`, and
  `rename_log.csv` shows where each one came from.
- **Some text is cut off or was never scanned.** Every existing scan of
  those pages was checked, and none shows the missing text, so the original
  letters would have to be rescanned. See [Pages to rescan](#pages-to-rescan).
- Notes in some transcription headers mention the old folder names or
  filenames (for example, "page 2 was found in TBF0defective"). They record
  where each page was found. The index gives each scan's original filename.

## Pages to rescan

If the original letters still exist, rescanning these pages would fill in
text that no current scan shows. In the index, each affected letter has a
`rescan` list, and each item has a `type`:

- `cut-off`: text on this page runs past the edge of every scan. Rescan the
  page with a margin all round.
- `not-scanned`: a page or the back of a sheet was never scanned. It belongs
  after page `after_page`. These five letters are marked `"complete": false`.
- `possible-gap`: the text suggests something may be missing. Check the
  original.

**Text cut off at the scan edge**

| Letter | Page(s) | What's cut off |
|---|---|---|
| 1942-07-06, Tom to Mother | 1, 3 | Bottom line |
| 1942-07-27, Tom to Mother | 1 | Bottom line |
| 1942-11-01, Tom to Mother | 1 | Last line(s) |
| 1943-02-18, Tom to Mother (typed) | 1 | Signature |
| 1943-05-03, Tom to Mother | 1, 5 | Last line of page 1; signature on page 5 |
| 1943-05-16, Tom to Mother | 1, 2, 3 | Bottom line of each page |
| 1943-08-01, Tom to Mother | 2 | Left edge |
| 1943-08-31, Tom to Mother | 4 | Top line |
| 1943-09-09, Tom to Mom | 1–4 | A word or two at the edges |
| 1944-04-03, Tom to Mum | 1 | Closing and signature |

**Pages never scanned**

| Letter | What's missing |
|---|---|
| 1942-11-22, Tom to Sis (Betty) | The back of the sheet (marked "over") |
| 1943-04-15, Tom to Mother | The backs of sheets "-2-" and "-3-" |
| 1943-06-11, Tom to Mother | Everything after page 2 |
| 1943-12-17, Tom to Mother | A middle page |
| Undated, Janny to Mother | A page between pages 2 and 3 |

**Possible gaps to check:** 1942-11 (a Wednesday), Tom to Mother, after
page 1; 1943-04-21, Tom to Mother, after page 1; 1943-08-01, Tom to Mother,
after page 1.

## Keeping things consistent

`viewer.html` holds its own copy of the index, transcriptions and
annotations, so it has to be rebuilt after any of them change. After
changing any file, run:

```
python3 annotations/build_annotations.py   # only if annotations or transcriptions changed
python3 tools/build_viewer.py
python3 tools/check_project.py
```

It checks that every file in the index exists, that every scan appears in
the index exactly once, that each transcription's header and page markers
match its scans, that the rescan lists point at real pages, and that the
annotations still line up with the text, and that the data in `viewer.html`
is up to date. The
folder is also a git repository, so every change can be reviewed or undone.

## Tom's service, in brief

| Date | Event |
|---|---|
| July 1942 | Enters the Naval Reserve Midshipmen's School at Columbia University, New York |
| Oct 21, 1942 | Commissioned Ensign at Riverside Church |
| Nov 1942 | Amphibious training at Norfolk, VA and Solomons, MD |
| Jan 1943 | Houston, TX; his first ship, USS LCI(L) 345, is commissioned |
| Feb 1943 | Becomes executive officer of **USS LCI(L) 62** and sails for the South Pacific |
| Spring 1943 | Trains with LCI Flotilla Five, probably at Nouméa, New Caledonia |
| July 1943 | First combat: New Georgia landings, probably at Rendova (battle star, July 1 and 4) |
| Dec 1943 | Treasury–Bougainville operation (battle star, Dec. 3–4) |
| Spring 1944 | Returns to the United States |
| 1944 – 1945 | Shore duty at the U.S. Naval Station, Portland, Maine |
| Spring 1945 | Hospitalized with malaria; writes home on V-E Day |

The index has a fuller timeline and notes on the family members who appear in
the letters.
