#!/usr/bin/env python3
"""Validate the letter annotations and build annotations_resolved.json.

Run from anywhere:  python3 build_annotations.py

Reads   entities.json and letters/*.json (next to this script)
        ../transcriptions/*.txt (the transcriptions)
Writes  annotations_resolved.json, which gives every annotation its exact
        character offsets in its transcription, so an app can underline text
        without doing any matching itself.

Exits non-zero if any quote cannot be found, matches in more than one place,
or points at an entity that does not exist.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRANSCRIPTIONS = HERE.parent / "transcriptions"

ENTITY_TYPES = {"ship", "place", "person", "organization", "military",
                "event", "culture", "term"}
KINDS = {"reference", "context", "inference", "content-note", "transcription"}
CONFIDENCE = {"confirmed", "probable", "speculative"}


GAP = r"(?:\s|\[--- [^\]\n]* ---\])+"


def quote_regex(text):
    """Whitespace in a quote matches any run of whitespace (line breaks,
    indentation) or page markers like '[--- 1942-07-18_tom-to-mother_p02.jpg ---]' in the
    transcription; everything else matches literally."""
    return GAP.join(re.escape(tok) for tok in text.split())


def body_start(text):
    """Quotes are matched only in the letter itself, below the '=====' line
    that ends the file header. Offsets still count from the start of the file."""
    m = re.search(r"^={10,}\n", text, re.M)
    return m.end() if m else 0


def find_quote(text, quote):
    exact = quote["exact"]
    pat = quote_regex(exact)
    matches = []
    for m in re.compile(pat).finditer(text, body_start(text)):
        start, end = m.start(), m.end()
        if quote.get("prefix"):
            before = text[max(0, start - 200):start]
            if not re.search(quote_regex(quote["prefix"]) + "(?:" + GAP + ")?$", before):
                continue
        if quote.get("suffix"):
            after = text[end:end + 200]
            if not re.match("(?:" + GAP + ")?" + quote_regex(quote["suffix"]), after):
                continue
        matches.append((start, end))
    if "occurrence" in quote:
        n = quote["occurrence"]
        return matches[n - 1:n], len(matches)
    return matches, len(matches)


def main():
    errors = []
    entities = json.loads((HERE / "entities.json").read_text())["entities"]
    for eid, e in entities.items():
        if e.get("id") != eid:
            errors.append(f"entity {eid}: id field does not match key")
        if e.get("type") not in ENTITY_TYPES:
            errors.append(f"entity {eid}: bad type {e.get('type')!r}")
        if e.get("confidence", "confirmed") not in CONFIDENCE:
            errors.append(f"entity {eid}: bad confidence")
        if not e.get("summary"):
            errors.append(f"entity {eid}: missing summary")
        for rel in e.get("see_also", []):
            if rel not in entities:
                errors.append(f"entity {eid}: see_also {rel} not found")

    resolved = {}
    used = set()
    for path in sorted((HERE / "letters").glob("*.json")):
        data = json.loads(path.read_text())
        letter = data["letter"]
        txt = TRANSCRIPTIONS / letter
        if not txt.exists():
            errors.append(f"{path.name}: transcription {letter} not found")
            continue
        text = txt.read_text(encoding="utf-8")
        out = []
        seen_ids = set()
        for a in data["annotations"]:
            aid = a.get("id")
            where = f"{path.name} {aid}"
            if not aid or aid in seen_ids:
                errors.append(f"{where}: missing or duplicate id")
            seen_ids.add(aid)
            if a.get("kind") not in KINDS:
                errors.append(f"{where}: bad kind {a.get('kind')!r}")
            if a.get("confidence", "confirmed") not in CONFIDENCE:
                errors.append(f"{where}: bad confidence")
            ent = a.get("entity")
            if ent:
                if ent not in entities:
                    errors.append(f"{where}: entity {ent} not found")
                used.add(ent)
            if not ent and not a.get("note"):
                errors.append(f"{where}: needs an entity or a note")
            matches, total = find_quote(text, a["quote"])
            if len(matches) != 1:
                errors.append(f"{where}: quote {a['quote']['exact']!r} matched "
                              f"{total} times (need exactly 1; add prefix, "
                              f"suffix or occurrence)")
                continue
            start, end = matches[0]
            item = {"id": aid, "start": start, "end": end,
                    "text": text[start:end], "kind": a["kind"]}
            for img in a.get("images", []):
                if not (HERE.parent / img.get("file", "")).is_file():
                    errors.append(f"{where}: image {img.get('file')!r} not found")
            for k in ("entity", "note", "confidence", "sources", "images"):
                if a.get(k):
                    item[k] = a[k]
            out.append(item)
        out.sort(key=lambda x: x["start"])
        for prev, cur in zip(out, out[1:]):
            if cur["start"] < prev["end"]:
                errors.append(f"{path.name}: {prev['id']} and {cur['id']} overlap")
        resolved[letter] = out

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s); annotations_resolved.json not written.")
        sys.exit(1)

    unused = sorted(set(entities) - used)
    result = {
        "schema_version": 1,
        "offsets": "0-based character offsets into the full .txt file; "
                   "end is exclusive. The files are plain ASCII, so these "
                   "are the same in Python and JavaScript.",
        "entities": entities,
        "letters": resolved,
    }
    (HERE / "annotations_resolved.json").write_text(
        json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    n = sum(len(v) for v in resolved.values())
    print(f"OK: {len(entities)} entities, {n} annotations in "
          f"{len(resolved)} letters.")
    if unused:
        print(f"Entities not linked from any letter ({len(unused)}): "
              + ", ".join(unused))


if __name__ == "__main__":
    main()
