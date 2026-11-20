#!/usr/bin/env python3
"""Print every empty value in site.config.js as a checklist line. Always exits 0."""
import re
import sys
from pathlib import Path

WHAT = {
    "callqa": "Loom URL for the Call QA demo",
    "triage": "Loom URL for the exception triage demo",
    "gtm": "Loom URL for the gtm_agent demo",
    "tender": "Loom URL for the tender tracker demo",
    "capstone": "Loom URL for the capstone demo",
    "callqaResult": "Call QA live result text, shown on the project page",
    "capstoneResult": "Capstone result text, shown under Research",
    "cvPath": 'path to the CV PDF, for example "assets/archit-rishabh-cv.pdf"',
    "windstreamPhotos": "Windstream photos as src, caption and alt objects",
    "degreeTitle": "exact degree title",
}

EMPTY_RE = re.compile(r'^\s*(\w+):\s*(""|\[\])\s*,?\s*(?://.*)?$', re.M)


def empty_keys(text):
    return [m.group(1) for m in EMPTY_RE.finditer(text)]


def main(argv):
    default = Path(__file__).resolve().parent.parent / "site.config.js"
    path = Path(argv[1]) if len(argv) > 1 else default
    keys = empty_keys(path.read_text(encoding="utf-8"))
    if not keys:
        print("Nothing to fill in.")
    for k in keys:
        print(f"- [ ] {k}: {WHAT.get(k, 'value needed')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
