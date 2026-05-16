#!/usr/bin/env python3
"""Generate src/data/keywords.json from 00_admin/lexicon.py.

Keeps the presentation's All-Keywords appendix slide in sync with the
canonical dictionary. Run: python3 00_admin/presentation/gen_keywords.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "00_admin"))
import lexicon as L  # noqa: E402

OUT = Path(__file__).resolve().parent / "src" / "data" / "keywords.json"


def entry_str(e) -> str:
    if isinstance(e, str):
        return f'"{e}"'
    base = e["base"]
    al = e.get("aliases") or []
    s = base
    if al:
        s += " (" + ", ".join(al) + ")"
    if e.get("stem") is False:
        s += " ·literal"
    return s


PAIRS = [
    ("Explore vs Exploit", "explore", "exploit"),
    ("Customer vs Shareholder", "customer", "shareholder"),
    ("Long-term vs Short-term", "long_term", "short_term"),
    ("Entrepreneurial vs Managerial", "entrepreneurial", "managerial"),
    ("Internal vs External innovation", "internal_innovation", "external_innovation"),
    ("Risk vs Performance", "risk_challenge", "success_performance"),
]


def main() -> None:
    ipm = [
        {"name": theme, "entries": [entry_str(e) for e in terms]}
        for theme, terms in L.IPM_TERMS.items()
    ]
    cross = []
    for title, a, b in PAIRS:
        cross.append({
            "name": title,
            "left": {"label": a.replace("_", " "),
                     "entries": [entry_str(e) for e in L.CROSS_TERMS[a]]},
            "right": {"label": b.replace("_", " "),
                      "entries": [entry_str(e) for e in L.CROSS_TERMS[b]]},
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"ipm": ipm, "cross": cross}, indent=2), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(ipm)} IPM themes, {len(cross)} cross-cutting pairs")


if __name__ == "__main__":
    main()
