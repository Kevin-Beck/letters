#!/usr/bin/env python3
"""Build the letter data embedded in index.html.

Run from anywhere:  python3 tools/build_viewer.py

Reads data/letters.json, transcriptions/*.txt and
annotations/annotations_resolved.json, turns them into the viewer data
described in Viewer_design.md section 4, and writes it into the
<script id="letters-data"> block of index.html. The rest of index.html is
left untouched.

Stops with an error if any check fails.
"""
import calendar
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWER = ROOT / "index.html"
RANGE = {"start": "1942-07-01", "end": "1945-08-31"}
CONFIDENCE = {"confirmed", "probable", "speculative"}

# Letters whose id says "undated" but whose content dates them well enough to
# place on the timeline (approximate, so drawn hollow).
SORT_DATE_OVERRIDES = {
    # "1942 or 1943 (fall; a Friday)", likely the start of the fall 1942 term
    "undated_george-to-mother-allegheny": "1942-09-15",
}

DATA_BLOCK = re.compile(
    r'(<script id="letters-data" type="application/json">)(.*?)(</script>)', re.S)
MONTHS = calendar.month_name


class BuildError(Exception):
    pass


def check(ok, message):
    if not ok:
        raise BuildError(message)


def short_name(name):
    return name.split(" (", 1)[0]


def sort_date(lid):
    if lid in SORT_DATE_OVERRIDES:
        return SORT_DATE_OVERRIDES[lid]
    if m := re.match(r"(\d{4}-\d\d-\d\d)_", lid):
        return m.group(1)
    if m := re.match(r"(\d{4}-\d\d)-xx_", lid):
        return m.group(1) + "-15"
    if m := re.match(r"(\d{4})-winter_", lid):
        return m.group(1) + "-01-15"
    check(lid.startswith("undated_"), f"{lid}: unrecognised id prefix")
    return None


def date_label(date):
    if date is None:
        return "Undated"
    if m := re.match(r"(\d{4})-(\d\d)-(\d\d)", date):
        y, mo, d = (int(x) for x in m.groups())
        return f"{MONTHS[mo]} {d}, {y}" + date[10:]
    return date


def month_end(y, m):
    return f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"


def parse_event(line):
    m = re.match(r"(\S+)\s+(.*)$", line)
    check(m, f"timeline entry not understood: {line!r}")
    prefix, text = m.groups()
    if re.fullmatch(r"\d{4}-\d\d-\d\d", prefix):
        start = end = prefix
    elif m := re.fullmatch(r"(\d{4})-(\d\d)", prefix):
        y, mo = int(m.group(1)), int(m.group(2))
        start, end = f"{y:04d}-{mo:02d}-01", month_end(y, mo)
    elif m := re.fullmatch(r"(\d{4})-(\d\d)/(\d\d)", prefix):
        y, m1, m2 = (int(x) for x in m.groups())
        start, end = f"{y:04d}-{m1:02d}-01", month_end(y, m2)
    elif m := re.fullmatch(r"(\d{4})-2H", prefix):
        start, end = f"{m.group(1)}-07-01", f"{m.group(1)}-12-31"
    else:
        raise BuildError(f"timeline date prefix not understood: {prefix!r}")
    return {"start": start, "end": end, "text": text}


def parse_location(item):
    check(item.get("confidence") in CONFIDENCE, f"location {item!r}: bad confidence")
    for key in ("start", "end"):
        check(re.fullmatch(r"\d{4}-\d\d-\d\d", item.get(key) or ""),
              f"location {item!r}: bad {key} date")
    check(item["start"] <= item["end"], f"location {item['place']!r} ends before it starts")
    check(RANGE["start"] <= item["start"] and item["end"] <= RANGE["end"],
          f"location {item['place']!r} is outside the timeline range")
    return {k: item.get(k) for k in ("start", "end", "place", "confidence", "detail")}


def build_locations(items):
    locations = [parse_location(x) for x in items]
    periods = sorted((x for x in locations if x["start"] != x["end"]), key=lambda x: x["start"])
    for a, b in zip(periods, periods[1:]):
        check(a["end"] < b["start"], f"locations {a['place']!r} and {b['place']!r} overlap")
    return sorted(locations, key=lambda x: (x["start"], x["end"]))


def split_transcription(lid, text):
    m = re.search(r"^={10,}\n", text, re.M)
    check(m, f"{lid}: no line of '=' ending the header")
    header, body = text[:m.end()], text[m.end():]
    note = None
    for para in re.split(r"\n\s*\n", header):
        if para.startswith("NOTE:"):
            note = " ".join(line.strip() for line in para.strip().splitlines())
    return header, body, note


def find_markers(lid, body, n_pages):
    markers = []
    for m in re.finditer(r"^\[---(.*?)---\]$", body, re.M):
        inner = m.group(1)
        marker = {"start": m.start(), "end": m.end()}
        if p := re.search(re.escape(lid) + r"_p(\d\d)\.jpg", inner):
            marker.update(type="page", page=int(p.group(1)))
        elif p := re.fullmatch(r"\s*page (\d+)\s*", inner):
            marker.update(type="page", page=int(p.group(1)))
        else:
            marker.update(type="gap", text=inner.strip())
        markers.append(marker)
    n_page_markers = sum(mk["type"] == "page" for mk in markers)
    check(n_page_markers == n_pages or (n_page_markers == 0 and n_pages == 1),
          f"{lid}: {n_page_markers} page markers for {n_pages} pages")
    return markers


def build_data():
    index = json.loads((ROOT / "data/letters.json").read_text(encoding="utf-8"))
    resolved = json.loads(
        (ROOT / "annotations/annotations_resolved.json").read_text(encoding="utf-8"))
    entities = resolved["entities"]

    letters = []
    for L in index["letters"]:
        check(L.get("viewer", True) in (True, False), f"{L['id']}: 'viewer' must be true or false")
        if not L.get("viewer", True):
            continue   # kept in the project, left out of the viewer
        lid = L["id"]
        text = (ROOT / L["transcription_file"]).read_text(encoding="utf-8")
        header, body, content_note = split_transcription(lid, text)
        shift = len(header)

        annotations = []
        for a in resolved["letters"].get(f"{lid}.txt", []):
            a = dict(a, start=a["start"] - shift, end=a["end"] - shift)
            check(a["start"] >= 0 and body[a["start"]:a["end"]] == a["text"],
                  f"{lid}: annotation {a['id']} does not match the body text")
            check("entity" not in a or a["entity"] in entities,
                  f"{lid}: annotation {a['id']} names unknown entity {a.get('entity')}")
            annotations.append(a)

        date = L["date"]
        written_by = short_name(L["written_by"])
        letters.append({
            "id": lid,
            "title": f"{written_by} to {L['written_to']}",
            "written_by": written_by,
            "written_to": L["written_to"],
            "by_tom": L["written_by"].startswith("Tom"),
            "date": date,
            "date_label": date_label(date),
            "sort_date": sort_date(lid),
            "approximate": not (isinstance(date, str)
                                and re.fullmatch(r"\d{4}-\d\d-\d\d", date)),
            "date_source": L.get("date_source"),
            "other_dates_mentioned": L.get("other_dates_mentioned") or [],
            "location": L.get("location"),
            "complete": L.get("complete", True),
            "notes": L.get("notes"),
            "content_note": content_note,
            "rescan": L.get("rescan", []),
            "pages": [{k: p[k] for k in ("page", "file", "width", "height")}
                      for p in L["pages"]],
            "body": body,
            "markers": find_markers(lid, body, len(L["pages"])),
            "annotations": annotations,
        })

    letters.sort(key=lambda x: (x["sort_date"] is None, x["sort_date"] or "", x["id"]))

    mentions = {}
    for x in letters:
        for a in x["annotations"]:
            if "entity" in a:
                ids = mentions.setdefault(a["entity"], [])
                if not ids or ids[-1] != x["id"]:
                    ids.append(x["id"])

    data = {
        "built": datetime.now().isoformat(timespec="seconds"),
        "collection": index["collection"],
        "content_warning": index["content_warning"],
        "range": RANGE,
        "events": [parse_event(t) for t in index["timeline"]],
        "locations": build_locations(index.get("locations", [])),
        "world": [parse_event(t) for t in index.get("world_events", [])],
        "people": index["people"],
        "entities": entities,
        "letters": letters,
        "mentions": mentions,
    }
    check(not re.search(r"[^\u0000-￿]", json.dumps(data, ensure_ascii=False)),
          "text contains a character outside the Basic Multilingual Plane")
    return data


def embed(data):
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def read_embedded():
    """Return the data currently embedded in index.html (or None)."""
    if not VIEWER.is_file():
        return None
    m = DATA_BLOCK.search(VIEWER.read_text(encoding="utf-8"))
    return json.loads(m.group(2)) if m else None


def main():
    try:
        data = build_data()
    except BuildError as e:
        sys.exit(f"build_viewer.py: {e}")
    html = VIEWER.read_text(encoding="utf-8")
    blocks = DATA_BLOCK.findall(html)
    if len(blocks) != 1:
        sys.exit(f"build_viewer.py: index.html must contain exactly one letters-data "
                 f"block (found {len(blocks)})")
    html = DATA_BLOCK.sub(lambda m: m.group(1) + "\n" + embed(data) + "\n" + m.group(3),
                          html)
    VIEWER.write_text(html, encoding="utf-8")
    n_ann = sum(len(x["annotations"]) for x in data["letters"])
    print(f"index.html: {len(data['letters'])} letters, {n_ann} annotations, "
          f"{len(data['entities'])} entities, {len(data['events'])} service events, "
          f"{len(data['locations'])} locations, {len(data['world'])} world events "
          f"({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
