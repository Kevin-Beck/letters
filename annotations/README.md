# Letter annotations

This folder holds background notes on the people, ships, places and events in
the letters, stored so an app can show them as hover text, the way Wikipedia
shows a preview when you hover over a blue link.

The transcriptions (`../transcriptions/*.txt`) are **not changed**. The annotations sit
alongside them and point into them by quoting the exact words.

## Files

| File | What it is | Who edits it |
|---|---|---|
| `entities.json` | The glossary: one entry per ship, person, place, event or term, written once and shared by every letter that mentions it | People |
| `letters/<letter>.json` | One file per transcription, with the same name (`letters/1943-02-13_tom-to-mother.json` goes with `../transcriptions/1943-02-13_tom-to-mother.txt`), listing which words in that letter are linked and to what | People |
| `build_annotations.py` | Checks everything and produces the file below | Run it after any edit |
| `annotations_resolved.json` | Everything in one file with exact character positions, ready for an app to load | Generated; don't edit |

## Entities (`entities.json`)

```json
"ship.lci-l-62": {
  "id": "ship.lci-l-62",
  "type": "ship",
  "name": "USS LCI(L)-62",
  "aliases": ["#62", "the 62"],
  "summary": "Short hover text: one to three sentences.",
  "detail": "Optional longer text for a click-through or side panel.",
  "dates": "1942-11-13 to 1947",
  "coords": [lat, lon],
  "confidence": "confirmed",
  "see_also": ["event.new-georgia"],
  "wikipedia": "https://en.wikipedia.org/wiki/...",
  "sources": [{"title": "...", "url": "..."}]
}
```

- **id** is `type.short-name` and never changes once letters link to it.
- **type** is one of: `ship`, `place`, `person`, `organization`,
  `military` (ranks, jargon, procedures), `event`, `culture` (films,
  books, radio, sports, daily life), `term`.
- **confidence** tells the reader how sure the note is:
  - `confirmed`: from the letters themselves or a reliable source.
  - `probable`: strongly suggested, but not proven.
  - `speculative`: a reasoned guess (for example, a censored port worked out
    from the ship's known movements).
- Only `id`, `type`, `name`, `summary` and `confidence` are always present.

## Letter annotations (`letters/*.json`)

```json
{
  "letter": "1943-02-13_tom-to-mother.txt",
  "annotations": [
    {
      "id": "a2",
      "quote": {"exact": "Almost every other door leads to a bar"},
      "entity": "place.panama-canal-zone",
      "kind": "inference",
      "confidence": "probable",
      "note": "Text that applies only to this passage."
    }
  ]
}
```

- **quote.exact** is the linked text, copied from the transcription. Line
  breaks and indentation don't matter, and a page marker such as
  `[--- 1943-02-13_tom-to-mother_p02.jpg ---]` in the middle of a phrase is skipped. Only the
  letter itself is searched, not the header above the `=====` line.
- If the words appear more than once, add `"occurrence": 2` (the 2nd match),
  or `"prefix"` / `"suffix"` (text just before or after).
- **entity** links to the glossary. **note** adds something specific to
  this spot. An annotation can have either one or both. When it has both, show
  the note first and the entity's summary under it.
- **kind**:
  - `reference`: a plain link to a glossary entry.
  - `context`: an explanation of this passage.
  - `inference`: a conclusion drawn from evidence, such as a censored location
    or the meaning of a gap in the letters.
  - `content-note`: historical context for offensive language, kept as
    written.
  - `transcription`: a note about the document itself, such as a misdated
    letter or added handwriting.
- **confidence** on an annotation overrides the entity's value for that
  passage.
- **images** (optional) is a list of `{"file": ..., "caption": ...}` pictures
  shown in the note, for example a scanned magazine page the letter refers
  to. `file` is relative to the project folder (put new pictures in
  `additional_context/`). The build checks that each file exists.
- Annotation ids (`a1`, `a2`, …) are stable. Add new ones at the end with the
  next number, and don't renumber.

This quote-based approach follows the W3C Web Annotation "TextQuoteSelector".
Because a link finds its words rather than a character position, it survives
typo fixes elsewhere in the transcription.

## For app builders: `annotations_resolved.json`

```json
{
  "entities": { "ship.lci-l-62": { ... } },
  "letters": {
    "1943-02-13_tom-to-mother.txt": [
      {"id": "a2", "start": 1003, "end": 1041, "text": "Almost every other door leads to a\nbar",
       "kind": "inference", "entity": "place.panama-canal-zone",
       "confidence": "probable", "note": "..."}
    ]
  }
}
```

`start` and `end` are character offsets into the full `.txt` file (0-based,
end exclusive). The files are plain ASCII, so JavaScript's `text.slice(start,
end)` returns exactly `text`. The spans in each letter are sorted and never
overlap, so an app can wrap each one in a `<span>` in a single pass.

Suggested display:
- Underline `reference` links like Wikipedia links, and mark `inference` and
  `speculative` ones with a dotted underline so readers know it's a guess.
- Show `content-note` items as a small marker rather than a link.
- An entity page can list every letter that mentions it by collecting the
  annotations whose `entity` matches.

## Editing workflow

1. Add or change entries in `entities.json` and/or `letters/*.json`.
2. Run `python3 build_annotations.py`.
3. Fix anything it reports: a quote that isn't found, one that matches more
   than once, or a link to a missing entity. It then rewrites
   `annotations_resolved.json` and lists any glossary entries that no letter
   uses.

## What's here (Sept. 2026)

- 274 glossary entries and 702 annotations across all 116 letters.
- Sources: the letters, `../data/letters.json`, NavSource and uboat.net ship
  histories, the Naval History and Heritage Command, the Pro Football Hall of
  Fame, and Wikipedia.
- **Things to check with the family:** the relationships marked `probable` or
  `speculative` (Betty, Isabel, Dick, the McClungs, John Mc.), and whether
  Tom's father died in Dec. 1942 or Jan. 1943. The letters strongly suggest it
  but never say so.
- **Censored locations** (Panama, Bora Bora, Nouméa, Guadalcanal) are worked
  out from the timing and from LCI Flotilla Five's known movements, and are
  marked `probable` or `speculative`. LCI(L)-62's official battle credits
  (New Georgia, July 1943; Treasury-Bougainville, Dec. 1943) are confirmed,
  and they line up with the gaps in the letters.
