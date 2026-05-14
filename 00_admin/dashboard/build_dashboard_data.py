"""
build_dashboard_data.py
Reads every CSV in 05_outputs/tables/, the manifest, markdown briefs, and
financial_report.md / letter_summaries.md, then writes:
  src/data/dataset.json      — all structured data for the React app
  src/data/briefs/*.md       — copies of markdown briefs for react-markdown rendering
"""
import csv
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "05_outputs" / "tables"
BRIEFS_SRC = ROOT / "05_outputs"
OUT_DATA = Path(__file__).parent / "src" / "data"
OUT_BRIEFS = OUT_DATA / "briefs"
OUT_DATA.mkdir(parents=True, exist_ok=True)
OUT_BRIEFS.mkdir(parents=True, exist_ok=True)

MANIFEST = ROOT / "02_extracted_text" / "selected_ceo_letters" / "selected_ceo_letters_manifest.csv"
KEYWORD_NOTES = ROOT / "00_admin" / "keyword_review_notes.md"

sys.path.insert(0, str(ROOT / "00_admin"))
from lexicon import (  # noqa: E402
    IPM_TERMS, CROSS_TERMS, THEME_SUBTHEMES, Matcher, tokenize,
)


# ── helpers ────────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def numeric(val: str):
    val = val.strip()
    try:
        f = float(val)
        return int(f) if f == int(f) else round(f, 4)
    except (ValueError, TypeError):
        return val


def numerify(rows: list[dict]) -> list[dict]:
    """Convert every value that looks numeric to int/float."""
    return [{k: numeric(v) for k, v in row.items()} for row in rows]


# ── CSV tables ─────────────────────────────────────────────────────────────────

def load_table(name: str) -> list[dict]:
    path = TABLES / f"{name}.csv"
    if not path.exists():
        print(f"  WARN: {name}.csv not found")
        return []
    rows = numerify(read_csv(path))
    print(f"  {name}: {len(rows)} rows")
    return rows


# ── markdown table parser ──────────────────────────────────────────────────────

def parse_md_tables(md_text: str) -> list[dict]:
    """
    Extract all pipe-tables from a markdown string.
    Returns list of { section, table_name, headers, rows, notes }.
    """
    results = []
    current_h1 = ""
    current_h2 = ""
    current_h3 = ""
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            current_h1 = line[2:].strip()
        elif line.startswith("## "):
            current_h2 = line[3:].strip()
        elif line.startswith("### "):
            current_h3 = line[4:].strip()

        # detect pipe table
        if re.match(r"\s*\|", line):
            table_lines = []
            j = i
            while j < len(lines) and re.match(r"\s*\|", lines[j]):
                table_lines.append(lines[j])
                j += 1
            if len(table_lines) >= 3:
                header_cells = [c.strip() for c in table_lines[0].strip("|").split("|")]
                # line 1 is separator
                data_rows = []
                for tl in table_lines[2:]:
                    cells = [c.strip() for c in tl.strip("|").split("|")]
                    if len(cells) == len(header_cells):
                        row = {header_cells[k]: cells[k] for k in range(len(header_cells))}
                        data_rows.append(row)
                # collect notes (italic lines after table)
                notes = []
                k = j
                while k < len(lines) and lines[k].strip().startswith("_") or (k < len(lines) and lines[k].strip().startswith("*_")):
                    notes.append(lines[k].strip().strip("_").strip("*").strip())
                    k += 1
                results.append({
                    "section": current_h1,
                    "subsection": current_h2,
                    "table_name": current_h3 or current_h2,
                    "headers": header_cells,
                    "rows": data_rows,
                    "notes": notes,
                })
            i = j
            continue
        i += 1
    return results


# ── letter summaries parser ────────────────────────────────────────────────────

def parse_letter_summaries(md_text: str) -> list[dict]:
    """Parse letter_summaries.md into [{company, year, ceo, title, bullets}]."""
    results = []
    current_company = ""
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            current_company = line[3:].strip()
        elif line.startswith("### "):
            # e.g. "### Amazon 1997 — Jeff Bezos"
            heading = line[4:].strip()
            m = re.match(r"(.+?)\s+(\d{4})\s*[—–-]+\s*(.*)", heading)
            if m:
                company = m.group(1).strip()
                year = int(m.group(2))
                ceo = m.group(3).strip()
            else:
                company = current_company
                year = 0
                ceo = heading
            # collect bullets until next heading
            bullets = []
            i += 1
            while i < len(lines) and not lines[i].startswith("#"):
                bl = lines[i].strip()
                if bl.startswith("-") or bl.startswith("*") or bl.startswith("**"):
                    # strip leading bullet markers and bold markers
                    bl = re.sub(r"^[-*]\s+", "", bl)
                    bl = re.sub(r"\*\*([^*]+)\*\*", r"\1", bl)
                    if bl:
                        bullets.append(bl)
                i += 1
            results.append({
                "company": company,
                "year": year,
                "ceo": ceo,
                "title": heading,
                "bullets": bullets,
            })
            continue
        i += 1
    return results


# ── financials parser ─────────────────────────────────────────────────────────

def parse_financials(md_text: str) -> dict:
    """
    Parse financial_report.md into per-company structured data.
    Returns { company: { tables: [...], narrative: str } }
    """
    companies = {}
    # Map uppercase section names to canonical names
    NAME_MAP = {
        "AMAZON": "Amazon",
        "NVIDIA": "NVIDIA",
        "SHELL": "Shell",
        "CHEVRON": "Chevron",
        "CROSS-COMPANY COMPARISON — KEY METRICS": "Cross-Company",
        "NOTES ON DATA QUALITY": None,
    }
    current_company = None
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not line.startswith("## "):
            raw = line[2:].strip()
            canonical = NAME_MAP.get(raw)
            if canonical:
                current_company = canonical
                companies[current_company] = {"tables": [], "narrative_chunks": []}
        i += 1

    # Now parse tables per company via parse_md_tables but grouped
    all_tables = parse_md_tables(md_text)
    # Build reverse map: section heading -> canonical name
    rev_map = {k: v for k, v in NAME_MAP.items() if v}
    for t in all_tables:
        raw_sec = t["section"]
        canonical = rev_map.get(raw_sec)
        if canonical and canonical in companies:
            companies[canonical]["tables"].append(t)

    # Build simple narrative: headings + non-table text per company
    result = {}
    for c, data in companies.items():
        result[c] = {
            "tables": data["tables"],
        }
    return result


# ── copy briefs ────────────────────────────────────────────────────────────────

BRIEF_FILES = {
    "company_briefs": [
        "amazon_qualitative_brief.md",
        "nvidia_qualitative_brief.md",
        "shell_qualitative_brief.md",
        "chevron_qualitative_brief.md",
        "explore_exploit_analysis.md",
        "innovation_process_model_analysis.md",
        "qualitative_cross_case_synthesis.md",
        "quantitative_analysis_working_draft.md",
    ],
    "methodology_briefs": [
        "findings_and_conclusion_working_draft.md",
        "methodology_draft.md",
        "methodology_working_brief.md",
        "research_hypothesis.md",
        "initial_outline.md",
    ],
    "industry_comparison": [
        "comparative_analysis_working_draft.md",
        "why_these_companies_and_industries.md",
    ],
}

def copy_briefs() -> list[dict]:
    index = []
    for folder, files in BRIEF_FILES.items():
        for fn in files:
            src = BRIEFS_SRC / folder / fn
            if src.exists():
                dst = OUT_BRIEFS / fn
                shutil.copy2(src, dst)
                title = fn.replace("_", " ").replace(".md", "").title()
                category = folder.replace("_", " ").title()
                index.append({"filename": fn, "title": title, "category": category})
                print(f"  copied {folder}/{fn}")
            else:
                print(f"  WARN: {folder}/{fn} not found")
    return index


# ── era assignment ─────────────────────────────────────────────────────────────

ERA_MAP = {
    # Era names must match company_era_ipm_matrix.csv exactly
    ("Amazon", 1997): "1997 Bezos founder doctrine",
    ("Amazon", 2016): "2016 Bezos anti-Day-2 discipline",
    ("Amazon", 2020): "2021-2025 Jassy reinvention",
    ("Amazon", 2021): "2021-2025 Jassy reinvention",
    ("Amazon", 2022): "2021-2025 Jassy reinvention",
    ("Amazon", 2024): "2021-2025 Jassy reinvention",
    ("Amazon", 2025): "2021-2025 Jassy reinvention",
    ("Nvidia", 2017): "2017-2018 GPU platform emergence",
    ("Nvidia", 2018): "2017-2018 GPU platform emergence",
    ("Nvidia", 2020): "2020-2023 AI expansion",
    ("Nvidia", 2021): "2020-2023 AI expansion",
    ("Nvidia", 2022): "2020-2023 AI expansion",
    ("Nvidia", 2023): "2020-2023 AI expansion",
    ("Nvidia", 2025): "2025 AI infrastructure",
    ("Shell", 2014): "2014-2016 van Beurden portfolio discipline",
    ("Shell", 2015): "2014-2016 van Beurden portfolio discipline",
    ("Shell", 2016): "2014-2016 van Beurden portfolio discipline",
    ("Shell", 2020): "2020 Powering Progress reset",
    ("Shell", 2022): "2022-2025 Sawan performance transition",
    ("Shell", 2024): "2022-2025 Sawan performance transition",
    ("Shell", 2025): "2022-2025 Sawan performance transition",
    ("Chevron", 2013): "2013 Watson operational baseline",
    ("Chevron", 2018): "2018 Wirth disciplined renewal",
    ("Chevron", 2020): "2020-2024 returns/lower-carbon",
    ("Chevron", 2021): "2020-2024 returns/lower-carbon",
    ("Chevron", 2022): "2020-2024 returns/lower-carbon",
    ("Chevron", 2023): "2020-2024 returns/lower-carbon",
    ("Chevron", 2024): "2020-2024 returns/lower-carbon",
}


# ── lexicon view ───────────────────────────────────────────────────────────────

def _strip_header(text: str) -> str:
    return text.split("\n---\n", 1)[1] if "\n---\n" in text else text


def _entry_to_dict(entry):
    if isinstance(entry, str):
        return {"kind": "literal", "label": entry, "base": entry,
                "aliases": [], "excludes": [], "stem": False}
    return {
        "kind": "stem" if entry.get("stem") is not False else "surface",
        "label": entry["base"],
        "base": entry["base"],
        "aliases": entry.get("aliases") or [],
        "excludes": entry.get("excludes") or [],
        "stem": entry.get("stem", True),
    }


def _parse_notes(path: Path) -> dict[str, str]:
    """Parse the keyword review markdown file into {key: note_markdown}."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    notes: dict[str, str] = {}
    current_key = None
    buffer: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current_key is not None and buffer:
                content = "\n".join(buffer).strip()
                if content:
                    notes[current_key] = content
            header = m.group(1).strip()
            # Treat as a real entry key only if it looks like "<category>/<base>"
            current_key = header if "/" in header else None
            buffer = []
        elif line.startswith("# "):
            # Top-level heading — flush, then ignore
            if current_key is not None and buffer:
                content = "\n".join(buffer).strip()
                if content:
                    notes[current_key] = content
            current_key = None
            buffer = []
        else:
            if current_key is not None:
                buffer.append(line)
    if current_key is not None and buffer:
        content = "\n".join(buffer).strip()
        if content:
            notes[current_key] = content
    return notes


def build_lexicon_view(manifest_rows: list[dict]) -> dict:
    # Pre-tokenise all 28 letters once
    letter_tokens: list[tuple[str, int, str, list[str], list[str]]] = []
    company_words: dict[str, int] = defaultdict(int)
    for row in manifest_rows:
        path = ROOT / row["extracted_letter_path"]
        text = _strip_header(path.read_text(encoding="utf-8"))
        toks, stems = tokenize(text)
        letter_tokens.append((row["company"], int(row["year"]), text, toks, stems))
        company_words[row["company"]] += len(toks)

    companies = ["Amazon", "Nvidia", "Shell", "Chevron"]

    def per_entry_counts(entry):
        m = Matcher("_one", [entry])
        per_company = {c: 0 for c in companies}
        total = 0
        per_letter = []
        for company, year, text, toks, stems in letter_tokens:
            n = m.count(text, toks, stems)
            per_company[company] += n
            total += n
            if n:
                per_letter.append({"company": company, "year": year, "count": n})
        return {
            "total": total,
            "byCompany": per_company,
            "byLetter": per_letter,
        }

    notes = _parse_notes(KEYWORD_NOTES)
    matched_keys: set[str] = set()

    def attach_note(key: str, entry_dict: dict) -> None:
        if key in notes:
            entry_dict["note"] = notes[key]
            entry_dict["noteKey"] = key
            matched_keys.add(key)

    categories = []

    # IPM themes
    for theme, terms in IPM_TERMS.items():
        entries = []
        for term in terms:
            e = _entry_to_dict(term)
            e["counts"] = per_entry_counts(term)
            attach_note(f"{theme}/{e['base']}", e)
            entries.append(e)
        categories.append({"group": "IPM", "name": theme, "entries": entries})

    # Cross-cutting pairs
    for name, terms in CROSS_TERMS.items():
        entries = []
        for term in terms:
            e = _entry_to_dict(term)
            e["counts"] = per_entry_counts(term)
            attach_note(f"{name}/{e['base']}", e)
            entries.append(e)
        categories.append({"group": "Cross-cutting", "name": name, "entries": entries})

    # Theme subthemes (drill-down for the IPM appendix)
    subtheme_groups = []
    for row in THEME_SUBTHEMES:
        entries = []
        for term in row["terms"]:
            e = _entry_to_dict(term)
            e["counts"] = per_entry_counts(term)
            attach_note(f"{row['theme']}/{row['subtheme']}/{e['base']}", e)
            entries.append(e)
        subtheme_groups.append({
            "theme": row["theme"], "subtheme": row["subtheme"], "entries": entries,
        })

    unmatched = sorted(k for k in notes if k not in matched_keys)
    return {
        "categories": categories,
        "subthemes": subtheme_groups,
        "companies": companies,
        "companyWordCounts": dict(company_words),
        "notesFile": "00_admin/keyword_review_notes.md",
        "notesUnmatched": unmatched,
    }


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("Building dashboard data...")
    print("\nLoading CSV tables:")
    dataset = {}

    # Manifest
    manifest_rows = numerify(read_csv(MANIFEST))
    dataset["manifest"] = manifest_rows
    print(f"  manifest: {len(manifest_rows)} rows")

    # Quant tables
    dataset["quant"] = {
        "byLetter": load_table("quant_summary_by_letter"),
        "byCompany": load_table("quant_summary_by_company"),
        "themesOverTime": load_table("theme_counts_normalized"),
        "exploreExploit": load_table("explore_exploit_ratios"),
        "keywordByCompany": load_table("appendix_keyword_theme_counts"),
        "keywordByYear": load_table("appendix_keyword_counts_by_year"),
        "perYearCounts": load_table("appendix_per_year_counts"),
        "exploreExploitByCompany": load_table("explore_exploit_keyword_counts_by_company"),
        "exploreExploitByYear": load_table("explore_exploit_keyword_counts_by_year"),
        "subthemeByCompany": load_table("appendix_subtheme_counts_by_company"),
    }

    # Lexicon (dictionary + per-entry corpus hits + review notes)
    print("\nBuilding lexicon view:")
    dataset["lexicon"] = build_lexicon_view(manifest_rows)
    print(f"  {len(dataset['lexicon']['categories'])} categories, "
          f"{sum(len(c['entries']) for c in dataset['lexicon']['categories'])} entries")

    # Other analysis tables
    dataset["eras"] = load_table("company_era_ipm_matrix")
    dataset["comparative"] = load_table("comparative_matrix")
    dataset["ipmMatrix"] = load_table("ipm_comparison_matrix")
    dataset["ipmEvidence"] = load_table("ipm_detailed_evidence_matrix")
    dataset["hypotheses"] = load_table("hypothesis_test_summary")
    dataset["outcomes"] = load_table("outcome_anchors")
    dataset["selectedYears"] = load_table("selected_company_years")
    dataset["rationale"] = load_table("selected_letter_rationale")

    # Enrich byLetter with era
    for row in dataset["quant"]["byLetter"]:
        key = (row.get("company", ""), int(row.get("year", 0)))
        row["era"] = ERA_MAP.get(key, "")

    # Letter summaries
    print("\nParsing letter_summaries.md:")
    ls_path = BRIEFS_SRC / "company_briefs" / "letter_summaries.md"
    if ls_path.exists():
        summaries = parse_letter_summaries(ls_path.read_text(encoding="utf-8"))
        dataset["letterSummaries"] = summaries
        print(f"  parsed {len(summaries)} letter summaries")
    else:
        dataset["letterSummaries"] = []
        print("  WARN: letter_summaries.md not found")

    # Financials
    print("\nParsing financial_report.md:")
    fin_path = BRIEFS_SRC / "company_briefs" / "financial_report.md"
    if fin_path.exists():
        fin_text = fin_path.read_text(encoding="utf-8")
        financials = parse_financials(fin_text)
        dataset["financials"] = financials
        total_tables = sum(len(v["tables"]) for v in financials.values())
        print(f"  parsed {len(financials)} company sections, {total_tables} tables")
    else:
        dataset["financials"] = {}
        print("  WARN: financial_report.md not found")

    # Copy briefs
    print("\nCopying briefs:")
    brief_index = copy_briefs()
    dataset["briefIndex"] = brief_index

    # Write JSON
    out_path = OUT_DATA / "dataset.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = out_path.stat().st_size / 1024
    print(f"\ndataset.json written ({size_kb:.1f} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
