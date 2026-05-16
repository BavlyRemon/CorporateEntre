#!/usr/bin/env python3
"""Regenerate 05_outputs/keyword_dictionary_reference.md from lexicon.py.

This is the human-readable listing of every word scored in every theme.
Run from anywhere: `python3 00_admin/regen_keyword_reference.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "00_admin"))
import lexicon as L  # noqa: E402

OUT = ROOT / "05_outputs" / "keyword_dictionary_reference.md"


def words(entry) -> str:
    if isinstance(entry, str):
        return f"`{entry}` *(phrase)*"
    base = entry["base"]
    al = entry.get("aliases") or []
    ex = entry.get("excludes") or []
    s = "**" + base + "**"
    if al:
        s += " · " + ", ".join(al)
    if ex:
        s += " · _excl:_ " + ", ".join(ex)
    if entry.get("stem") is False:
        s += " _(no-stem)_"
    return s


def main() -> None:
    o: list[str] = []
    o += [
        "# Keyword Dictionary Reference",
        "",
        "The **actual words** scored in every theme, generated directly from "
        "`00_admin/lexicon.py` (the canonical source). Regenerate with "
        "`python3 00_admin/regen_keyword_reference.py` whenever `lexicon.py` changes.",
        "",
        "**How to read an entry:** **base** · alias1, alias2 (extra surface "
        "forms that count via Porter stemming) · _excl:_ words that must NOT "
        "count even though their stem matches · `phrase` *(phrase)* = matched "
        "whole-word, not stemmed · _(no-stem)_ = stemming disabled for this entry.",
        "",
        "---",
        "",
        "## The five IPM themes",
        "",
    ]
    for theme, terms in L.IPM_TERMS.items():
        o += [f"### {theme}", f"*{len(terms)} entries*", ""]
        o += ["- " + words(t) for t in terms]
        o += [""]
    o += ["---", "", "## Cross-cutting paired lenses", "",
          "Each pair yields a *share* = first / (first + second). These run "
          "over the top of the five IPM themes.", ""]
    for name, terms in L.CROSS_TERMS.items():
        o += [f"### {name}", f"*{len(terms)} entries*", ""]
        o += ["- " + words(t) for t in terms]
        o += [""]
    o += ["---", "", "## IPM subthemes (report appendix breakdown)", "",
          "Each IPM theme is further split into subthemes used by the "
          "submission-ready report appendix.", ""]
    cur = None
    for row in L.THEME_SUBTHEMES:
        if row["theme"] != cur:
            cur = row["theme"]
            o += [f"### {cur}", ""]
        o += ["**" + row["subtheme"] + "** — "
              + "; ".join(words(t) for t in row["terms"]), ""]
    o += ["---", "",
          "## Regenerate", "",
          "```",
          "python3 00_admin/regen_keyword_reference.py",
          "```", ""]
    OUT.write_text("\n".join(o), encoding="utf-8")
    n_ipm = sum(len(v) for v in L.IPM_TERMS.values())
    n_cross = sum(len(v) for v in L.CROSS_TERMS.values())
    print(f"wrote {OUT.relative_to(ROOT)} — {n_ipm} IPM + {n_cross} cross-cutting "
          f"entries across {len(L.IPM_TERMS)} themes, "
          f"{len(L.THEME_SUBTHEMES)} subtheme rows")


if __name__ == "__main__":
    main()
