# TBF1 Navy Letters: WWII Letters of Ens. Thomas Frazier Beck

This folder holds scanned letters written by **Thomas Frazier "Tom" Beck** of
Karns City, Pennsylvania during his U.S. Navy service in World War II
(1942–1945). Most are to his mother, Elva Beck (Mrs. John A. Beck). There are
also a few family letters, a telegram, V-mail forms, and a newspaper clipping.

In September 2026 every scan was read and typed out, so the letters can be
read, searched, and shared without the images. The folder was then
reorganized so that every letter has one set of scans, one transcription and
one set of notes, all with matching names. This is the groundwork for a
browser app for reading the letters.

## What's in this folder

| Location | What it is |
|---|---|
| `scans/` | The best scan of every page: 267 pages from 116 letters |
| `transcriptions/` | The typed text of each letter, one file per letter |
| `annotations/` | Background notes on the people, ships, places and events in the letters (see `annotations/README.md`) |
| `data/letters.json` | The index: every letter's date, writer, recipient, location, pages and notes |
| `photos/` | Family photographs (not letters; not transcribed) |
| `delete/` | Duplicate scans and old drafts. **Safe to delete** (see `delete/README.md`) |
| `tools/check_project.py` | Checks that the files and the index agree |
| `rename_log.csv` | Every file's old name and new name from the reorganization |

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
- notes on the people and events it mentions;
- its pages, in order. Each page has its scan, its width and height, its
  **original filename** from before the reorganization, and any duplicate
  scans of it.

The index also has a short family guide (`people`), a timeline of Tom's
service (`timeline`), and notes on scans that were misdated or misfiled
(`scan_notes`).

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
  the cleaned-up Adobe scan was kept. The rest are in `delete/scans/`.
- **Five letters are still incomplete** because some pages were never
  scanned (for example, the backs of two sheets of the April 15, 1943
  letter). They are marked `"complete": false` in the index. If the original
  letters still exist, those pages could be rescanned.
- Notes in some transcription headers mention the old folder names or
  filenames (for example, "page 2 was found in TBF0defective"). They record
  where each page was found. The index gives each scan's original filename.

## Keeping things consistent

After changing any file, run:

```
python3 tools/check_project.py
```

It checks that every file in the index exists, that every scan appears in
the index exactly once, that each transcription's header and page markers
match its scans, and that the annotations still line up with the text. The
folder is also a git repository, so every change can be reviewed or undone.

## Tom's service, in brief

| Date | Event |
|---|---|
| July 1942 | Enters the Naval Reserve Midshipmen's School at Columbia University, New York |
| Oct 21, 1942 | Commissioned Ensign at Riverside Church |
| Nov 1942 | Amphibious training at Norfolk, VA and Solomons, MD |
| Jan 1943 | Houston, TX; his first ship, USS LCI(L) 345, is commissioned |
| Feb 1943 | Becomes executive officer of **USS LCI(L) 62** and sails for the South Pacific |
| 1943 – early 1944 | Serves in the South Pacific (details censored in the letters) |
| Spring 1944 | Returns to the United States |
| 1944 – 1945 | Shore duty at the U.S. Naval Station, Portland, Maine |
| Spring 1945 | Hospitalized with malaria; writes home on V-E Day |

The index has a fuller timeline and notes on the family members who appear in
the letters.
