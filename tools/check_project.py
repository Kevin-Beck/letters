#!/usr/bin/env python3
"""Check that the project's files and data/letters.json agree.

Run from anywhere:  python3 tools/check_project.py

Checks that
  - every scan, transcription and annotation file named in the index exists;
  - every file in scans/ is named in the index exactly once;
  - each 'rescan' entry names a real page of its letter;
  - each transcription's "Source images" header lists exactly its letter's
    scans, and its page markers name only those scans;
  - the annotations still build (runs annotations/build_annotations.py);
  - the data embedded in viewer.html is up to date (tools/build_viewer.py).

Exits non-zero if anything is wrong.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_TOP = {"README.md", "rename_log.csv", "annotations", "data", "delete",
                "photos", "scans", "tools", "transcriptions", "Viewer_design.md",
                "viewer.html", ".git"}


def check_viewer():
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "tools"))
    import build_viewer
    try:
        expected = build_viewer.build_data()
    except build_viewer.BuildError as e:
        return [f"tools/build_viewer.py failed: {e}"]
    try:
        embedded = build_viewer.read_embedded()
    except json.JSONDecodeError as e:
        return [f"viewer.html data block is not valid JSON: {e}"]
    if embedded is None:
        return ["viewer.html is missing or has no letters-data block"]
    expected.pop("built", None)
    embedded.pop("built", None)
    if embedded != expected:
        return ["viewer.html data is out of date; run tools/build_viewer.py"]
    return []


def main():
    errors = []
    index = json.loads((ROOT / "data/letters.json").read_text())
    letters = index["letters"]

    named = Counter()
    ids = Counter(L["id"] for L in letters)
    errors += [f"duplicate letter id {i}" for i, n in ids.items() if n > 1]

    for L in letters:
        lid = L["id"]
        for key in ("transcription_file", "annotations_file"):
            if not (ROOT / L[key]).is_file():
                errors.append(f"{lid}: {key} {L[key]} missing")
        pages = [p["file"] for p in L["pages"]]
        for n, p in enumerate(L["pages"], 1):
            if p["page"] != n or p["file"] != f"scans/{lid}_p{n:02d}.jpg":
                errors.append(f"{lid}: page {n} is misnamed ({p['file']})")
            named[p["file"]] += 1
            if not (ROOT / p["file"]).is_file():
                errors.append(f"{lid}: {p['file']} missing")
        for r in L.get("rescan", []):
            n = r.get("page", r.get("after_page"))
            if r.get("type") not in index["rescan_types"] or not isinstance(n, int) \
                    or not 1 <= n <= len(pages):
                errors.append(f"{lid}: bad rescan entry {r}")

        txt_path = ROOT / L["transcription_file"]
        if not txt_path.is_file():
            continue
        text = txt_path.read_text(encoding="utf-8")
        header = text.split("\n======", 1)[0]
        m = re.search(r"^Source images: (.*(?:\n {15}\S.*)*)", header, re.M)
        listed = m.group(1).split() if m else []
        if listed != pages:
            errors.append(f"{lid}: 'Source images' header does not match the index")
        own = {Path(f).name for f in pages}
        for marker in re.findall(r"^\[---(.*?)---\]$", text, re.M):
            for name in re.findall(r"[^\s:/]+\.jpg", marker):
                if name not in own:
                    errors.append(f"{lid}: page marker names {name}, not one of its scans")

    on_disk = {f"scans/{p.name}" for p in (ROOT / "scans").iterdir() if p.is_file()}
    errors += [f"{f} is named {n} times in the index" for f, n in named.items() if n > 1]
    errors += [f"{f} is in the index but not on disk" for f in set(named) - on_disk]
    errors += [f"{f} is on disk but not in the index" for f in sorted(on_disk - set(named))]

    txts = {f"transcriptions/{p.name}" for p in (ROOT / "transcriptions").glob("*.txt")}
    errors += [f"{t} has no entry in the index"
               for t in sorted(txts - {L["transcription_file"] for L in letters})]

    extra = {p.name for p in ROOT.iterdir()} - EXPECTED_TOP
    errors += [f"unexpected item in the project folder: {x}" for x in sorted(extra)]

    build = subprocess.run([sys.executable, str(ROOT / "annotations/build_annotations.py")],
                           capture_output=True, text=True)
    if build.returncode:
        errors.append("annotations/build_annotations.py failed:\n" + build.stdout)
    else:
        errors += check_viewer()

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s).")
        sys.exit(1)
    n_pages = sum(len(L["pages"]) for L in letters)
    n_rescan = sum(len(L.get("rescan", [])) for L in letters)
    print(f"OK: {len(letters)} letters, {n_pages} page scans, {n_rescan} rescan items.")
    print(build.stdout.strip())


if __name__ == "__main__":
    main()
