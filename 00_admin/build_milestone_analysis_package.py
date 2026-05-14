#!/usr/bin/env python3
"""Build the comparative milestone analysis package from the selected letter corpus."""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "02_extracted_text" / "selected_ceo_letters"
MANIFEST = CORPUS_DIR / "selected_ceo_letters_manifest.csv"
TODAY = date(2026, 4, 18).isoformat()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import (  # noqa: E402  pylint: disable=wrong-import-position
    IPM_TERMS,
    CROSS_TERMS,
    THEME_SUBTHEMES,
    build_matchers,
    tokenize,
    format_entry_for_csv,
)



COMPANY_YEARS = {
    "Amazon": [1997, 2016, 2020, 2021, 2022, 2024, 2025],
    "Nvidia": [2017, 2018, 2020, 2021, 2022, 2023, 2025],
    "Shell": [2014, 2015, 2016, 2020, 2022, 2024, 2025],
    "Chevron": [2013, 2018, 2020, 2021, 2022, 2023, 2024],
}

COMPANY_PATH = {
    "Amazon": "amazon",
    "Nvidia": "nvidia",
    "Shell": "shell",
    "Chevron": "chevron",
}


def ensure_dirs() -> None:
    for path in [
        ROOT / "05_outputs" / "company_briefs",
        ROOT / "05_outputs" / "methodology_briefs",
        ROOT / "05_outputs" / "industry_comparison",
        ROOT / "05_outputs" / "tables",
        ROOT / "05_outputs" / "figures",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def strip_header(text: str) -> str:
    marker = "\n---\n"
    if marker in text:
        return text.split(marker, 1)[1]
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


IPM_MATCHERS = build_matchers(IPM_TERMS)
CROSS_MATCHERS = build_matchers(CROSS_TERMS)


def count_in(text: str, matcher, tokens=None, stems=None) -> int:
    return matcher.count(text, tokens, stems)


def pct(value: float) -> str:
    return f"{value:.1f}"


def per_1000(count: int, words: int) -> float:
    return 1000 * count / words if words else 0.0


def ratio(a: int, b: int) -> float:
    total = a + b
    return a / total if total else 0.0


def classify_explore(explore_share: float) -> str:
    if explore_share >= 0.6:
        return "exploratory leaning"
    if explore_share <= 0.4:
        return "exploitative leaning"
    return "ambidextrous/mixed"


def load_letters(manifest_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    letters: list[dict[str, object]] = []
    for row in manifest_rows:
        path = ROOT / row["extracted_letter_path"]
        text = strip_header(path.read_text(encoding="utf-8"))
        words = word_count(text)
        tokens, stems = tokenize(text)
        ipm_counts = {theme: IPM_MATCHERS[theme].count(text, tokens, stems) for theme in IPM_TERMS}
        cross_counts = {name: CROSS_MATCHERS[name].count(text, tokens, stems) for name in CROSS_TERMS}
        letters.append(
            {
                "company": row["company"],
                "year": int(row["year"]),
                "title": row["title"],
                "type": row["selected_text_type"],
                "path": row["extracted_letter_path"],
                "words": words,
                "ipm": ipm_counts,
                "cross": cross_counts,
            }
        )
    letters.sort(key=lambda x: (str(x["company"]), int(x["year"])))
    return letters


def aggregate_company(letters: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for company in COMPANY_YEARS:
        items = [l for l in letters if l["company"] == company]
        words = sum(int(l["words"]) for l in items)
        ipm = {theme: sum(int(l["ipm"][theme]) for l in items) for theme in IPM_TERMS}
        cross = {name: sum(int(l["cross"][name]) for l in items) for name in CROSS_TERMS}
        out[company] = {"items": items, "words": words, "ipm": ipm, "cross": cross}
    return out


def write_csvs(letters: list[dict[str, object]], company_data: dict[str, dict[str, object]]) -> None:
    table_dir = ROOT / "05_outputs" / "tables"
    ipm_names = list(IPM_TERMS)
    cross_names = list(CROSS_TERMS)

    with (table_dir / "quant_summary_by_letter.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["company", "year", "word_count"]
        fields += [f"{t}_count" for t in ipm_names]
        fields += [f"{t}_per_1000" for t in ipm_names]
        fields += [f"{c}_count" for c in cross_names]
        fields += [
            "explore_share_of_explore_exploit",
            "customer_share_of_customer_shareholder",
            "long_term_share_of_long_short",
            "entrepreneurial_share_of_entrepreneurial_managerial",
            "internal_share_of_internal_external",
            "risk_share_of_risk_performance",
            "explore_exploit_class",
            "source_file",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for letter in letters:
            row = {"company": letter["company"], "year": letter["year"], "word_count": letter["words"]}
            row.update({f"{t}_count": letter["ipm"][t] for t in ipm_names})
            row.update({f"{t}_per_1000": f"{per_1000(int(letter['ipm'][t]), int(letter['words'])):.3f}" for t in ipm_names})
            row.update({f"{c}_count": letter["cross"][c] for c in cross_names})
            row["explore_share_of_explore_exploit"] = f"{ratio(int(letter['cross']['explore']), int(letter['cross']['exploit'])):.3f}"
            row["customer_share_of_customer_shareholder"] = f"{ratio(int(letter['cross']['customer']), int(letter['cross']['shareholder'])):.3f}"
            row["long_term_share_of_long_short"] = f"{ratio(int(letter['cross']['long_term']), int(letter['cross']['short_term'])):.3f}"
            row["entrepreneurial_share_of_entrepreneurial_managerial"] = f"{ratio(int(letter['cross']['entrepreneurial']), int(letter['cross']['managerial'])):.3f}"
            row["internal_share_of_internal_external"] = f"{ratio(int(letter['cross']['internal_innovation']), int(letter['cross']['external_innovation'])):.3f}"
            row["risk_share_of_risk_performance"] = f"{ratio(int(letter['cross']['risk_challenge']), int(letter['cross']['success_performance'])):.3f}"
            row["explore_exploit_class"] = classify_explore(float(row["explore_share_of_explore_exploit"]))
            row["source_file"] = letter["path"]
            writer.writerow(row)

    with (table_dir / "quant_summary_by_company.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["company", "letter_count", "total_word_count"]
        fields += [f"{t}_count" for t in ipm_names]
        fields += [f"{t}_per_1000" for t in ipm_names]
        fields += [f"{c}_count" for c in cross_names]
        fields += [
            "explore_share_of_explore_exploit",
            "customer_share_of_customer_shareholder",
            "long_term_share_of_long_short",
            "entrepreneurial_share_of_entrepreneurial_managerial",
            "internal_share_of_internal_external",
            "risk_share_of_risk_performance",
            "dominant_ipm_theme_per_1000",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for company, data in company_data.items():
            words = int(data["words"])
            row = {"company": company, "letter_count": len(data["items"]), "total_word_count": words}
            row.update({f"{t}_count": data["ipm"][t] for t in ipm_names})
            row.update({f"{t}_per_1000": f"{per_1000(int(data['ipm'][t]), words):.3f}" for t in ipm_names})
            row.update({f"{c}_count": data["cross"][c] for c in cross_names})
            row["explore_share_of_explore_exploit"] = f"{ratio(int(data['cross']['explore']), int(data['cross']['exploit'])):.3f}"
            row["customer_share_of_customer_shareholder"] = f"{ratio(int(data['cross']['customer']), int(data['cross']['shareholder'])):.3f}"
            row["long_term_share_of_long_short"] = f"{ratio(int(data['cross']['long_term']), int(data['cross']['short_term'])):.3f}"
            row["entrepreneurial_share_of_entrepreneurial_managerial"] = f"{ratio(int(data['cross']['entrepreneurial']), int(data['cross']['managerial'])):.3f}"
            row["internal_share_of_internal_external"] = f"{ratio(int(data['cross']['internal_innovation']), int(data['cross']['external_innovation'])):.3f}"
            row["risk_share_of_risk_performance"] = f"{ratio(int(data['cross']['risk_challenge']), int(data['cross']['success_performance'])):.3f}"
            row["dominant_ipm_theme_per_1000"] = max(ipm_names, key=lambda t: per_1000(int(data["ipm"][t]), words))
            writer.writerow(row)

    with (table_dir / "theme_counts_normalized.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "year", "theme", "count", "per_1000_words", "source_file"])
        writer.writeheader()
        for letter in letters:
            for theme in ipm_names:
                writer.writerow(
                    {
                        "company": letter["company"],
                        "year": letter["year"],
                        "theme": theme,
                        "count": letter["ipm"][theme],
                        "per_1000_words": f"{per_1000(int(letter['ipm'][theme]), int(letter['words'])):.3f}",
                        "source_file": letter["path"],
                    }
                )

    with (table_dir / "explore_exploit_ratios.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "company",
                "year",
                "word_count",
                "explore_count",
                "exploit_count",
                "explore_per_1000",
                "exploit_per_1000",
                "explore_share_of_pair",
                "interpretive_class",
                "source_file",
            ],
        )
        writer.writeheader()
        for letter in letters:
            ex = int(letter["cross"]["explore"])
            xp = int(letter["cross"]["exploit"])
            share = ratio(ex, xp)
            writer.writerow(
                {
                    "company": letter["company"],
                    "year": letter["year"],
                    "word_count": letter["words"],
                    "explore_count": ex,
                    "exploit_count": xp,
                    "explore_per_1000": f"{per_1000(ex, int(letter['words'])):.3f}",
                    "exploit_per_1000": f"{per_1000(xp, int(letter['words'])):.3f}",
                    "explore_share_of_pair": f"{share:.3f}",
                    "interpretive_class": classify_explore(share),
                    "source_file": letter["path"],
                }
            )

    with (table_dir / "ipm_comparison_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["company"] + [f"{theme}_per_1000" for theme in ipm_names] + [
            "dominant_quant_theme",
            "qualitative_ipm_pattern",
            "strategic_leadership_evidence",
            "horizon_scanning_evidence",
            "purpose_vision_governance_evidence",
            "options_choices_evidence",
            "execution_organization_evidence",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        notes = {
            "Amazon": {
                "qualitative_ipm_pattern": "customer purpose -> inflection sensing -> multiple options -> fast scaling",
                "strategic_leadership_evidence": "Day 1, long-term orientation, bold investment, willingness to be misunderstood",
                "horizon_scanning_evidence": "Internet, pandemic, cloud migration, AI, robotics, satellite broadband, geopolitical turbulence",
                "purpose_vision_governance_evidence": "customer value creates long-term shareholder value; responsibility expands with scale",
                "options_choices_evidence": "parallel paths, MLPs, AWS, chips, grocery formats, robotics, Alexa reinvention, satellites",
                "execution_organization_evidence": "separable teams, speed, fulfillment capacity, robotics, AWS capex, organizational flattening",
            },
            "Nvidia": {
                "qualitative_ipm_pattern": "technology sensing -> platform architecture -> ecosystem scaling -> infrastructure execution",
                "strategic_leadership_evidence": "founder-led technical conviction; repeated reinvention from chips to platforms to AI infrastructure",
                "horizon_scanning_evidence": "GPU computing, accelerated computing, AI, edge, inference, agentic AI, physical AI, AI factories",
                "purpose_vision_governance_evidence": "enable developers, enterprises, countries, researchers, and industries through accelerated computing",
                "options_choices_evidence": "full-stack architecture, AI factories, software/models, roadmaps, ecosystem partnerships",
                "execution_organization_evidence": "engineering scale, product ramps, deployment tools, supply commitments, partner execution",
            },
            "Shell": {
                "qualitative_ipm_pattern": "transition sensing -> purpose/governance reconciliation -> portfolio choices -> disciplined transformation",
                "strategic_leadership_evidence": "safety, responsibility, resilience, performance, discipline, transformation under constraint",
                "horizon_scanning_evidence": "oil/gas market uncertainty, climate change, energy transition, policy, geopolitics, AI, customer decarbonization",
                "purpose_vision_governance_evidence": "shareholder value, net-zero, powering lives, respecting nature, trust, more value with less emissions",
                "options_choices_evidence": "BG/LNG, hydrogen, CCS, SAF, renewable power, digital tools, divestments, selective project pruning",
                "execution_organization_evidence": "simplification, cost reductions, faster decisions, trading/optimization, safe operations",
            },
            "Chevron": {
                "qualitative_ipm_pattern": "energy-demand sensing -> disciplined purpose -> adjacency options -> operational execution",
                "strategic_leadership_evidence": "operational excellence, safety, reliability, financial discipline, capital stewardship",
                "horizon_scanning_evidence": "energy demand, commodity cycles, geopolitical volatility, energy security, lower-carbon opportunities, AI power demand",
                "purpose_vision_governance_evidence": "affordable reliable ever-cleaner energy, human progress, customer needs, stockholder returns",
                "options_choices_evidence": "Future Energy Fund, OGCI, REG, hydrogen, CCUS, renewable diesel, Hess, exploration acreage",
                "execution_organization_evidence": "project delivery, record production, Permian scaling, deepwater engineering, refinery retrofits, balance sheet, capital discipline",
            },
        }
        for company, data in company_data.items():
            words = int(data["words"])
            rates = {theme: per_1000(int(data["ipm"][theme]), words) for theme in ipm_names}
            row = {"company": company}
            row.update({f"{theme}_per_1000": f"{rates[theme]:.3f}" for theme in ipm_names})
            row["dominant_quant_theme"] = max(ipm_names, key=lambda t: rates[t])
            row.update(notes[company])
            writer.writerow(row)

    with (table_dir / "comparative_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "dimension",
                "Amazon",
                "Nvidia",
                "Shell",
                "Chevron",
                "cross_case_interpretation",
            ],
        )
        writer.writeheader()
        rows = [
            {
                "dimension": "Innovation identity",
                "Amazon": "Customer-obsessed builder of platforms, logistics, cloud, devices, and AI-enabled experiences.",
                "Nvidia": "Full-stack AI infrastructure platform and ecosystem orchestrator.",
                "Shell": "Integrated energy company seeking more value with less emissions.",
                "Chevron": "Operationally disciplined energy incumbent pursuing profitable lower-carbon adjacencies.",
                "cross_case_interpretation": "Technology firms make exploration highly visible; energy firms frame innovation through reliability, discipline, and transition risk.",
            },
            {
                "dimension": "Explore/exploit balance",
                "Amazon": "Exploration is explicit but tied to scale economics and customer proof.",
                "Nvidia": "Strongest exploratory posture, especially around AI waves and platform evolution.",
                "Shell": "Ambidextrous but more constrained by capital allocation, safety, and policy conditions.",
                "Chevron": "Most exploitative/operational posture, with exploration through selective ventures, partnerships, and lower-carbon projects.",
                "cross_case_interpretation": "All four are ambidextrous, but the rhetorical center of gravity differs by industry.",
            },
            {
                "dimension": "Customer and stakeholder framing",
                "Amazon": "Customer language is central and repeatedly used to justify investment patience.",
                "Nvidia": "Customers, developers, partners, and countries are framed as ecosystem participants.",
                "Shell": "Customers are central to energy-transition market formation, alongside investors and society.",
                "Chevron": "Stockholder returns and energy customers/nations are paired with reliability and human progress.",
                "cross_case_interpretation": "Customer orientation is strongest in Amazon; stakeholder/value language is more explicit in energy.",
            },
            {
                "dimension": "Strategic choice mechanisms",
                "Amazon": "Parallel paths, working backwards, iterative invention, selective persistence, and shutdown learning.",
                "Nvidia": "Roadmap sequencing, platform integration, ecosystem partnerships, and full-stack investment.",
                "Shell": "Portfolio reshaping, divestment, LNG/gas priority, lower-carbon platforms when business models are attractive.",
                "Chevron": "Capital discipline, advantaged assets, acquisitions/divestitures, and selective lower-carbon investments.",
                "cross_case_interpretation": "Technology firms stress experimentation cycles; energy firms stress portfolio and capital allocation discipline.",
            },
        ]
        writer.writerows(rows)


def md_table(rows: list[list[object]], headers: list[str]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def company_rate_table(company_data: dict[str, dict[str, object]]) -> str:
    rows = []
    for company, data in company_data.items():
        words = int(data["words"])
        rates = {theme: per_1000(int(data["ipm"][theme]), words) for theme in IPM_TERMS}
        rows.append(
            [
                company,
                words,
                pct(rates["Strategic Leadership"]),
                pct(rates["Horizon Scanning / Sense-making"]),
                pct(rates["Purpose, Vision, and Governance"]),
                pct(rates["Strategic Options, Experimentation, and Choices"]),
                pct(rates["Agile Execution and Organization"]),
                max(rates, key=rates.get),
            ]
        )
    return md_table(
        rows,
        [
            "Company",
            "Words",
            "Leadership/1k",
            "Horizon/1k",
            "Purpose/1k",
            "Options/1k",
            "Execution/1k",
            "Dominant IPM theme",
        ],
    )


def cross_rate_table(company_data: dict[str, dict[str, object]]) -> str:
    rows = []
    for company, data in company_data.items():
        cc = data["cross"]
        rows.append(
            [
                company,
                f"{ratio(int(cc['explore']), int(cc['exploit'])):.3f}",
                f"{ratio(int(cc['customer']), int(cc['shareholder'])):.3f}",
                f"{ratio(int(cc['long_term']), int(cc['short_term'])):.3f}",
                f"{ratio(int(cc['entrepreneurial']), int(cc['managerial'])):.3f}",
                f"{ratio(int(cc['internal_innovation']), int(cc['external_innovation'])):.3f}",
                f"{ratio(int(cc['risk_challenge']), int(cc['success_performance'])):.3f}",
            ]
        )
    return md_table(
        rows,
        [
            "Company",
            "Explore share",
            "Customer share",
            "Long-term share",
            "Entrepreneurial share",
            "Internal innovation share",
            "Risk/challenge share",
        ],
    )


def cite(company: str, year: int) -> str:
    cpath = COMPANY_PATH[company]
    return f"`02_extracted_text/selected_ceo_letters/{cpath}/{cpath}_{year}_ceo_letter.txt`"


def write(path: str, content: str) -> None:
    target = ROOT / path
    if path == "05_outputs/company_briefs/innovation_process_model_analysis.md" and target.exists():
        existing = target.read_text(encoding="utf-8")
        if "## How The Model Is Used" in existing and "## Company Process Readings" in existing:
            return
    cleaned = content.strip()
    if path.endswith(".md") and cleaned.startswith("# ") and "Corpus citation note:" not in cleaned:
        lines = cleaned.splitlines()
        note = (
            "Corpus citation note: Letter evidence is cited to the extracted selected-letter files. "
            "Official source URLs, access dates, source titles, and extraction boundaries are documented in "
            "`02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, "
            "`00_admin/sources_master.csv`, and "
            "`03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`."
        )
        lines.insert(1, "")
        lines.insert(2, note)
        cleaned = "\n".join(lines)
    target.write_text(cleaned + "\n", encoding="utf-8")


def write_docs(letters: list[dict[str, object]], company_data: dict[str, dict[str, object]]) -> None:
    company_year_summary = md_table(
        [
            [
                company,
                ", ".join(str(y) for y in years),
                {
                    "Amazon": "Founder-era Day 1 logic, late Bezos platform maturity, pandemic/CEO transition, and Jassy-era AI/platform reinvention.",
                    "Nvidia": "GPU-to-platform transition, AI data-center scaling, COVID/edge AI, post-boom supply/execution, and 2025 AI-infrastructure identity.",
                    "Shell": "Pre- and post-BG capital pressure, energy-transition reframing, pandemic strategic reset, and Wael Sawan's performance/disciplined-transition phase.",
                    "Chevron": "Watson-era operational excellence, Wirth transition, pandemic resilience, lower-carbon strategy, record cash returns, Hess/portfolio moves, and AI-energy adjacency.",
                }[company],
            ]
            for company, years in COMPANY_YEARS.items()
        ],
        ["Company", "Confirmed years", "Analytical strength"],
    )

    write(
        "05_outputs/company_briefs/final_letter_set_confirmation.md",
        f"""
# Final Letter Set Confirmation

Access and analysis date: {TODAY}.

This confirmation uses the previously extracted selected-letter corpus and the CEO-letter availability audit. The unit of analysis is the selected leadership-letter text, not the full annual report. The corpus contains 28 texts: seven per company. Source availability and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv` and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

{company_year_summary}

## Company Notes

### Amazon

The Amazon set is analytically strong because it spans the original 1997 shareholder-letter doctrine, a later Bezos-era scale/platform moment, the pandemic period, and Jassy's CEO-transition and AI-era reinvention letters. The 1997 letter establishes the enduring logic of customer obsession, long-term investment, bold choices, and willingness to trade short-term profitability for market leadership. The 2021 letter is especially valuable because it makes the mechanism of iterative invention explicit through fulfillment, AWS, devices, Prime Video, climate, and Kuiper examples. The 2025 letter is a high-value end point because it frames AI, robotics, satellite broadband, chips, and organizational speed as related inflections rather than isolated projects. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

### Nvidia

The Nvidia set is analytically strong because it captures the shift from GPU computing as a distinctive platform to AI infrastructure as the company's central strategic identity. The 2017 and 2018 letters already frame NVIDIA as moving from chips to platforms and systems. The 2020-2023 letters show accelerated computing, cloud, edge AI, and data-center expansion becoming the core strategic narrative. The 2025 standalone CEO letter is the clearest mature statement of NVIDIA as a full-stack AI infrastructure company, with ecosystem partnerships, supply-chain execution, and AI factories at the center. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2020)}, {cite("Nvidia", 2025)}.

### Shell

The Shell set is analytically strong because it captures the move from Ben van Beurden's post-oil-price/BG acquisition leadership period to pandemic-era Powering Progress and then Wael Sawan's sharper performance, discipline, simplification, and integrated-energy framing. Shell's format differs from Amazon and NVIDIA: these are official annual-report Chief Executive Officer review sections rather than standalone letter PDFs. They are still suitable for this design because they are signed/presented CEO strategic communications and are isolated from financial-report sections in the corpus. Evidence: {cite("Shell", 2015)}, {cite("Shell", 2020)}, {cite("Shell", 2025)}.

### Chevron

The Chevron set is analytically strong because it spans operational-excellence continuity, a CEO transition from John Watson to Michael Wirth, pandemic and post-pandemic energy-market volatility, explicit lower-carbon framing, record cash-return years, and the 2024 link between energy security and AI/data-center demand. Chevron's selected texts are annual-report "To our stockholders" letters signed by the Chairman and Chief Executive Officer. They are leadership letters, not merely financial statements. Evidence: {cite("Chevron", 2013)}, {cite("Chevron", 2018)}, {cite("Chevron", 2024)}.

## Boundary Conditions

The set should remain intact unless the instructor requires standalone CEO-letter PDFs only. If that requirement is imposed, Shell would need a design note because the selected Shell corpus uses CEO-review sections. Chevron 2025 remains excluded because the official annual-report PDF was unavailable during the previous audit; the 2024 letter is therefore the most recent clean Chevron leadership letter in the current corpus.
""",
    )

    write(
        "05_outputs/methodology_briefs/initial_outline.md",
        f"""
# Initial Outline

## 1. Introduction

Purpose: Introduce the comparative research design: Amazon and Nvidia represent technology/digital-platform innovation, while Shell and Chevron represent oil-and-gas/energy innovation under capital intensity, regulation, safety, and transition pressure.

Evidence: The final 28-letter corpus, the selected-letter manifest, and the prior industry-rationale memo. The introduction should not narrate full company histories. It should frame why CEO/shareholder letters are useful windows into strategic intent, leadership framing, and innovation rhetoric.

Use of letters: Establish that each company is analyzed longitudinally across seven selected leadership texts. Cite the manifest and the final-letter confirmation.

Innovation Process Model: Introduce the five dimensions as the main analytical structure.

Explore vs exploit: Preview the central tension: all four firms must exploit existing capabilities while exploring new growth domains, but industry conditions shape how openly and aggressively exploration is narrated.

Comparative integration: End the introduction with the logic of two within-industry comparisons and one cross-industry comparison.

## 2. Hypothesis & Rationale

Purpose: State the main hypothesis and sub-hypotheses about how innovation language differs by industry and over time.

Evidence: Use the quantitative tables for normalized lexical patterns and selected qualitative examples from the letters.

Use of letters: Show how letters reveal management's own framing of strategic priorities, not just externally observed strategy.

Innovation Process Model: Position the model as the dependent interpretive structure: leadership, scanning, purpose/governance, options/experimentation, and execution.

Explore vs exploit: Define expected variation in exploration and exploitation language by company and industry.

Comparative integration: Explain why Amazon vs Nvidia tests platform/digital differences, Shell vs Chevron tests energy-incumbent differences, and tech vs energy tests industry-level innovation logic.

## 3. Methodology

Purpose: Explain corpus construction, selection logic, dictionary design, quantitative counting, qualitative reading, and limitations.

Evidence: `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`, `04_quant_framework/keyword_lists/clean_review_keywords.txt`, and the generated quantitative CSVs.

Use of letters: Define each company-year letter as the unit of analysis. Explain that full reports were not counted.

Innovation Process Model: Describe mapping of strict keywords to each IPM dimension and then interpretive manual reading.

Explore vs exploit: Explain paired keyword ratios and why they are interpreted cautiously.

Comparative integration: Explain normalization per 1,000 words because letter length differs greatly across firms.

## 4. Quantitative Analysis

Purpose: Present normalized lexical patterns, not final causal proof.

Evidence: `05_outputs/tables/quant_summary_by_company.csv`, `05_outputs/tables/quant_summary_by_letter.csv`, `05_outputs/tables/theme_counts_normalized.csv`, and `05_outputs/tables/explore_exploit_ratios.csv`.

Use of letters: Compare both company-level aggregates and within-company year changes.

Innovation Process Model: Present IPM theme intensity by company and selected years.

Explore vs exploit: Present paired ratios and classify company-years as exploratory leaning, exploitative leaning, or ambidextrous/mixed.

Comparative integration: Use the tables to compare Amazon vs Nvidia, Shell vs Chevron, and technology vs energy.

## 5. Qualitative Analysis

Purpose: Interpret strategic narratives, leadership posture, innovation identity, and changes over time.

Evidence: Short, carefully selected examples from the extracted letters.

Use of letters: Analyze recurring motifs: Amazon's customer-backward invention, Nvidia's full-stack AI platform, Shell's more-value-with-less-emissions transition, and Chevron's operationally disciplined lower-carbon energy logic.

Innovation Process Model: Organize qualitative findings around the five IPM dimensions.

Explore vs exploit: Interpret whether exploitation funds exploration, whether exploration is bounded by existing assets, and whether ambidexterity is explicit or implicit.

Comparative integration: Build from company briefs into cross-case synthesis.

## 6. Findings & Conclusion

Purpose: Synthesize the strongest findings while preserving methodological caution.

Evidence: Combine quantitative patterning with qualitative interpretation.

Use of letters: Return to the research question: how do large firms narrate corporate entrepreneurship and innovation under different industry conditions?

Innovation Process Model: Identify which dimensions dominate in each firm and why.

Explore vs exploit: Conclude that all four firms are ambidextrous, but with different rhetorical and strategic centers of gravity.

Comparative integration: Distinguish real similarities from superficial similarities. For example, all four discuss long-term investment, but Amazon and Nvidia frame it as technology/customer inflection while Shell and Chevron frame it through asset life, policy, energy security, safety, and shareholder-return discipline.
""",
    )

    write(
        "05_outputs/methodology_briefs/research_hypothesis.md",
        f"""
# Research Hypothesis

## Main Hypothesis

Across the 28 selected CEO/shareholder letters, technology-platform firms will use more explicit exploratory and option-creation language than oil-and-gas firms, while oil-and-gas firms will frame innovation more strongly through exploitation, operational discipline, safety, capital allocation, resilience, and regulated transition. However, the difference will not be a simple "tech explores / energy exploits" split: the strongest firms in both industries will display ambidextrous leadership by linking exploratory bets to existing capabilities, cash generation, ecosystem relationships, and long-term strategic renewal.

This hypothesis is testable through normalized lexical counts for Innovation Process Model themes and cross-cutting pairs, then through qualitative interpretation of how the words are used in context. The relevant evidence base is the 28-letter selected corpus and the quantitative tables generated from it.

## Supporting Sub-Hypotheses

### H1: Customer and Ecosystem Orientation

Amazon and Nvidia will show stronger customer/ecosystem language than Shell and Chevron because their innovation models depend heavily on platform adoption, developer/customer use cases, and networked complements. Amazon's 1997 and 2021 letters repeatedly justify investment by customer value and working backwards from customer experience; Nvidia's 2017 and 2025 letters frame its platform as serving AI developers, enterprises, partners, and countries. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2021)}, {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

### H2: Exploit-to-Explore Funding Logic

Shell and Chevron will use more exploitative language because energy innovation is constrained by asset lives, safety, commodity cycles, regulatory conditions, and capital intensity. Yet their letters should still show exploration when it is attached to advantaged assets, partnerships, lower-carbon technologies, or portfolio options. Shell's 2020 and 2025 reviews explicitly connect lower-carbon investment to cash flow, customer demand, policy, and capital discipline; Chevron's 2018, 2022, and 2024 letters connect lower-carbon and technology initiatives to operational excellence, partnerships, and returns. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}, {cite("Chevron", 2018)}, {cite("Chevron", 2022)}, {cite("Chevron", 2024)}.

### H3: Long-Termism Differs by Industry

All four firms will use long-term language, but the meaning will differ. In technology, long-termism will justify experimentation, platform expansion, and willingness to endure near-term investment pressure. In energy, long-termism will justify durable assets, energy demand, safety, policy stability, balance-sheet strength, and transition pacing. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}, {cite("Nvidia", 2025)}, {cite("Shell", 2025)}, {cite("Chevron", 2024)}.

### H4: Innovation Process Model Emphasis

The dominant Innovation Process Model dimensions will differ by firm: Amazon should be strongest in purpose/customer vision and strategic options; Nvidia in horizon scanning and strategic options; Shell in purpose/governance plus horizon scanning around transition; and Chevron in purpose/governance plus agile execution/operational excellence. This is tested in `05_outputs/tables/ipm_comparison_matrix.csv` and interpreted in `05_outputs/company_briefs/innovation_process_model_analysis.md`.
""",
    )

    write(
        "05_outputs/methodology_briefs/methodology_draft.md",
        f"""
# Methodology Draft

## Research Design

This milestone uses a comparative, longitudinal text-analysis design. The dataset consists of 28 selected CEO leadership communications: seven each from Amazon, Nvidia, Shell, and Chevron. Each company-year text is treated as one unit of analysis. The selected text extracts are saved separately from full annual reports so that the analysis counts leadership-communication language rather than entire financial reports. The corpus boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`.

**Corpus format note — Shell.** Amazon, Nvidia, and Chevron selected texts are standalone CEO/shareholder letters (PDF documents distributed separately from the annual report, or clearly demarcated "To our stockholders" sections signed by the CEO/Chairman). Shell does not publish a standalone shareholder letter equivalent. The Shell corpus uses the signed "Chief Executive Officer's review" sections from Shell's Annual Report and Form 20-F — the closest functional equivalent in Shell's reporting practice. These sections are signed by the CEO, address strategy and performance in the CEO's voice, and are isolated from financial-report tables and risk-factor boilerplate in the corpus. They are referred to throughout this analysis as "CEO reviews" to distinguish them from standalone letter formats. This boundary condition does not affect comparability in any material way: all selected texts are recurring, public, CEO-authored strategic communications.

## Why CEO and Shareholder Letters Are Valid Strategic Texts

CEO/shareholder letters and CEO reviews are useful strategic texts because they are public, recurring, management-authored communications that explain how leaders want investors and stakeholders to understand the firm's performance, priorities, risks, and future direction. They do not reveal strategy in a pure or neutral form; they reveal strategy as leadership framing. That makes them especially appropriate for Corporate Entrepreneurship and Innovation analysis, where leadership sense-making, resource commitment, strategic renewal, and ambidexterity are central concerns.

## Strengths and Limits

The strength of this method is comparability. Each letter is a formal annual leadership communication, and the selected set allows within-company change over time and cross-company comparison. The limitation is rhetorical bias: letters are polished documents that emphasize strategic confidence and may understate failed experiments, internal conflict, or organizational inertia. Quantitative lexical counts are therefore treated as indicators of emphasis, not direct measures of actual innovation output.

## Selection Logic

The study uses seven letters per company to balance depth and longitudinal coverage. The selected years were chosen because they capture strategic eras and inflection points rather than arbitrary intervals. Amazon spans founding doctrine, Bezos-era scale, pandemic/CEO transition, and Jassy-era AI/platform reinvention. Nvidia spans the GPU-to-platform transition and the rise of AI infrastructure. Shell spans BG/post-oil-price pressure, pandemic reset, Powering Progress, and Wael Sawan's performance-disciplined transition. Chevron spans operational excellence, Wirth's CEO transition, pandemic and post-pandemic volatility, lower-carbon strategy, and 2024 energy-security/AI demand framing. Selection confirmation is documented in `05_outputs/company_briefs/final_letter_set_confirmation.md`.

## Quantitative Analysis

The quantitative analysis uses a strict lexical dictionary organized by the Innovation Process Model: Strategic Leadership; Horizon Scanning / Sense-making; Purpose, Vision, and Governance; Strategic Options, Experimentation, and Choices; and Agile Execution and Organization. It also calculates cross-cutting paired counts for explore vs exploit, customer vs shareholder, long-term vs short-term, entrepreneurial vs managerial, internal vs external innovation, and risk/challenge vs success/performance.

Counts are normalized per 1,000 words because letter lengths vary substantially. Amazon's recent letters are much longer than Chevron's stockholder letters, and direct raw counts would overstate longer texts. The outputs are saved in `05_outputs/tables/quant_summary_by_company.csv`, `05_outputs/tables/quant_summary_by_letter.csv`, `05_outputs/tables/theme_counts_normalized.csv`, and `05_outputs/tables/explore_exploit_ratios.csv`.

## Qualitative Analysis

The qualitative analysis reads each company's seven-letter set for recurring strategic themes, shifts in leadership framing, innovation identity, customer/shareholder logic, and evidence of exploration, exploitation, or ambidexterity. The analysis is anchored in the letters rather than generic company history. Quotes are used sparingly, and every interpretive claim is tied to the selected corpus.

## Explore vs Exploit Identification

Exploration is identified through language of invention, experimentation, discovery, new business formation, emerging opportunities, pilots, R&D, and option creation. Exploitation is identified through language of operational excellence, reliability, productivity, efficiency, capital discipline, returns, cash flow, safety, and execution. Because some terms are context-dependent, the ratio is not interpreted mechanically. For example, "platform" can mean a digital ecosystem in technology or a physical oil-and-gas platform in energy; "growth" can refer to exploratory expansion or exploitation of known assets. The analysis therefore combines counts with manual reading.

## Innovation Process Model Application

The Innovation Process Model is the main interpretive structure. Strategic Leadership captures leader posture and ambidextrous framing. Horizon Scanning / Sense-making captures external disruption, technology shifts, regulation, geopolitics, and transition pressures. Purpose, Vision, and Governance captures customer, shareholder, societal, mission, and responsibility language. Strategic Options, Experimentation, and Choices captures invention, partnerships, acquisitions, pilots, portfolio moves, and allocation choices. Agile Execution and Organization captures speed, capability building, infrastructure, reliability, operational excellence, and resilience.

## Reproducibility

All source extracts, selected years, extraction boundaries, dictionaries, and generated CSV tables are stored in the workspace. The script `00_admin/build_milestone_analysis_package.py` rebuilds the quantitative tables and milestone draft package from the selected corpus. The approach is reproducible as long as the extracted letter files and dictionary logic remain unchanged.
""",
    )

    write(
        "05_outputs/company_briefs/quantitative_analysis_working_draft.md",
        f"""
# Quantitative Analysis Working Draft

Analysis date: {TODAY}. Counts are strict lexical counts from the selected letter bodies only. Extraction metadata headers were excluded before counting.

## Company-Level IPM Pattern

{company_rate_table(company_data)}

## Cross-Cutting Pair Pattern

Shares below represent the first term as a share of the paired total. For example, Explore share = explore / (explore + exploit). These are interpretive indicators, not final findings.

{cross_rate_table(company_data)}

## Interpretation

Amazon shows the clearest customer-purpose and strategic-options profile. This is consistent with the text of the 1997 letter, which makes customer focus, long-term market leadership, and bold investment decisions the central doctrine, and the 2021 and 2025 letters, which describe iterative invention, multiple paths, and AI-era reinvention as leadership mechanisms. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

Nvidia shows the strongest technology-horizon and strategic-options profile. The 2017 letter describes GPU computing as arriving across gaming, VR, AI, and self-driving cars, while the 2025 letter explicitly reframes NVIDIA as a full-stack AI infrastructure company. That combination explains why AI, platform, ecosystem, engineering, and infrastructure language is intense in the Nvidia corpus. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

The explore/exploit pair should be read more conservatively than the IPM horizon and options themes. Nvidia's strict explore share is low because the pair dictionary counts words such as "experiment," "pilot," and "discovery," while much of Nvidia's exploratory posture is expressed through specific technology-horizon terms such as AI, GPU, accelerated computing, Blackwell, inference, and AI factories. Amazon has a similar, though less extreme, issue when AI, AWS capacity, chips, and robotics function as exploration signals but are counted under horizon scanning or execution rather than the explore pair. This is why the qualitative interpretation weighs the IPM counts and close reading alongside the paired ratio.

Shell's counts are shaped by transition, governance, value, customer, and capital-allocation language. The 2020 review is especially dense because it joins pandemic resilience, net-zero strategy, customer-led low-carbon markets, and strategic relationships. The 2025 review shifts toward performance, discipline, simplification, LNG, upstream strength, and lower-carbon platforms only where policy and customer demand create attractive business models. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Chevron's quantitative pattern is the most exploitative and execution-oriented, but not innovation-free. Its letters repeatedly connect energy demand, operational excellence, safety, capital discipline, shareholder returns, and lower-carbon investments. The 2018 letter introduces the Future Energy Fund and OGCI investment; the 2024 letter connects technology, lower-carbon projects, partnerships, and AI/data-center power demand to the existing asset base. Evidence: {cite("Chevron", 2018)}, {cite("Chevron", 2024)}.

## Dictionary Cautions

The strict dictionary improves comparability but still requires manual interpretation. "Return" can mean shareholder return or a return to conditions. "Platform" is noisy across industries. "AI" is straightforward in Amazon and Nvidia but appears in energy letters as a demand driver or contextual force, not always as internal innovation. "Safety" is exploitative in the operational sense, but in energy it is also part of governance and legitimacy. The qualitative briefs therefore treat the quantitative results as a map of emphasis rather than a substitute for reading.

## Generated Tables

- `05_outputs/tables/quant_summary_by_company.csv`
- `05_outputs/tables/quant_summary_by_letter.csv`
- `05_outputs/tables/theme_counts_normalized.csv`
- `05_outputs/tables/explore_exploit_ratios.csv`
- `05_outputs/tables/ipm_comparison_matrix.csv`
- `05_outputs/tables/comparative_matrix.csv`
""",
    )

    write(
        "05_outputs/company_briefs/amazon_qualitative_brief.md",
        f"""
# Amazon Qualitative Brief

## Strategic Narrative

Amazon's letters project an innovation identity built around customer obsession, long-term investment, iterative invention, and organizational willingness to endure misunderstanding. The 1997 letter establishes the template: Amazon will prioritize customers, market leadership, long-term cash flows, bold investment, learning from failure, and employee ownership over short-term accounting optics. Evidence: {cite("Amazon", 1997)}.

By 2021, the same logic is applied at much larger scale. Jassy explains pandemic demand, fulfillment expansion, AWS, devices, Prime Video, climate commitments, and Kuiper as examples of iterative invention rather than one-time breakthroughs. This is a strong Corporate Entrepreneurship text because it describes internal venture building, experimentation, minimum loveable products, autonomous teams, speed, failure tolerance, and long-term orientation. Evidence: {cite("Amazon", 2021)}.

The 2025 letter makes the narrative more explicitly ambidextrous. Amazon is already a mature firm with enormous retail and AWS scale, yet Jassy argues that AI, robotics, satellite broadband, chips, and delivery reinvention require going back to first principles. The letter links exploration to disciplined capex, customer commitments, ROIC, and operational scaling. Evidence: {cite("Amazon", 2025)}.

## Innovation Framing

Innovation is framed as customer-backward problem solving. Amazon does not present invention as novelty for its own sake; it presents invention as a way to improve customer experience, lower cost, expand selection, increase speed, and create long-term shareholder value. This links Purpose/Vision with Strategic Options in the Innovation Process Model.

## Explore vs Exploit

Amazon is exploratory but not undisciplined. The 1997 letter already says Amazon will measure investments analytically, stop programs that do not provide acceptable returns, and increase investment in those that work. The 2025 letter expands this into a portfolio logic: pursue multiple paths, bet big on disproportionate inflections, and pull back when something is not working. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}.

## Shifts Over Time

The main shift is not away from Day 1 logic but toward mature-company ambidexterity. Early Amazon is concerned with building scale and legitimacy in online commerce. Later Amazon is concerned with renewing a scaled organization through AI, logistics automation, chips, satellite connectivity, and organizational flattening. The rhetoric changes from founder manifesto to mature platform-renewal playbook, but the underlying logic of long-term customer-centered invention remains stable.
""",
    )

    write(
        "05_outputs/company_briefs/nvidia_qualitative_brief.md",
        f"""
# Nvidia Qualitative Brief

## Strategic Narrative

Nvidia's selected letters tell a coherent story of strategic renewal from GPU computing to full-stack AI infrastructure. The 2017 letter states that GPU computing has arrived and connects the platform to gaming, VR, AI, self-driving cars, cloud providers, and enterprise systems. It already frames the company as more than a chip designer: NVIDIA is described as moving from chips to platforms and products. Evidence: {cite("Nvidia", 2017)}.

The 2020 and 2021 letters develop this narrative through accelerated computing, AI at the edge, data centers, autonomous systems, and pandemic-era scientific computing. Nvidia's innovation identity is strongly technological and ecosystemic: the company repeatedly emphasizes architectures, platforms, software, partners, developers, and vertical markets. Evidence: {cite("Nvidia", 2020)}, {cite("Nvidia", 2021)}.

The 2025 letter is the most explicit strategic identity statement. It says NVIDIA has transformed from a chip company to a full-stack computing platform, to data-center-scale AI systems, to an AI infrastructure company. It also frames AI factories, Blackwell/Rubin/Feynman roadmaps, reasoning, inference, agentic AI, physical AI, and partnerships as parts of one strategic system. Evidence: {cite("Nvidia", 2025)}.

## Innovation Framing

Innovation is framed as platform architecture plus ecosystem orchestration. Nvidia's letters emphasize technological discontinuity and the ability to build integrated systems across chips, networking, software, models, developers, and supply chain. This maps strongly onto Horizon Scanning and Strategic Options in the Innovation Process Model.

## Explore vs Exploit

Nvidia is strongly exploratory, but the exploration is anchored in exploitation of accumulated GPU architecture, developer ecosystems, engineering depth, and supply-chain capability. The 2025 letter is especially ambidextrous: it pairs frontier AI language with discipline, efficiency, supply commitments, customer continuity, buybacks, and operational scale. Evidence: {cite("Nvidia", 2025)}.

## Shifts Over Time

The major shift is from "GPU computing has arrived" to "AI infrastructure is the economy's next foundation." In 2017, the opportunity is broad but still framed around GPU platform expansion. By 2025, Nvidia frames itself as strategic infrastructure for enterprises, countries, and industries. The leadership posture becomes less about entering a promising market and more about orchestrating a global AI infrastructure layer.
""",
    )

    write(
        "05_outputs/company_briefs/shell_qualitative_brief.md",
        f"""
# Shell Qualitative Brief

## Strategic Narrative

Shell's selected CEO reviews present innovation through the language of energy transition, integrated assets, safety, capital discipline, and value creation. The 2015 review centers on difficult economic conditions and the BG acquisition, linking strategic renewal to portfolio strengthening, LNG, and long-term demand for energy. Evidence: {cite("Shell", 2015)}.

The 2020 review is the most strategically rich Shell text in the corpus. It combines pandemic crisis, safety, dividend rebasing, cash preservation, net-zero ambition, Powering Progress, customer-led low-carbon markets, and strategic relationships with Amazon and Microsoft. The review makes Shell's ambidexterity explicit: upstream cash flows fund low-carbon investments while the company changes with the energy system. Evidence: {cite("Shell", 2020)}.

The 2025 review marks a sharper performance-and-discipline phase under Wael Sawan. Shell frames the world as uncertain because of fragmented geopolitics, AI, and climate pressure. It then defines transformation through performance, discipline, simplification, LNG strength, upstream portfolio renewal, divestments, and selective lower-carbon platforms where policies and customer demand support attractive business models. Evidence: {cite("Shell", 2025)}.

## Innovation Framing

Innovation is less often framed as pure invention and more often as strategic renewal of an integrated energy company. Shell's innovation logic is market-formation and portfolio-based: develop low-carbon markets with customers, partners, and policy support while preserving cash generation from advantaged hydrocarbons.

## Explore vs Exploit

Shell is ambidextrous but constrained. The exploit side appears in cash flow, shareholder distributions, LNG/upstream strength, cost reductions, safety, and capital discipline. The explore side appears in hydrogen, CCS, biofuels, low-carbon fuels, digital tools, renewable power, and customer decarbonization. The 2025 letter narrows this exploration through an explicit value filter: lower-carbon platforms will be developed as government policies and customer demand create attractive business models. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

## Shifts Over Time

The shift is from acquisition-led strengthening and transition ambition to a more disciplined transition narrative. Shell does not abandon transformation, but the later reviews make the economic conditions for transformation more explicit. This is useful for the paper because it shows organizational ambidexterity under capital-market scrutiny and policy uncertainty.
""",
    )

    write(
        "05_outputs/company_briefs/chevron_qualitative_brief.md",
        f"""
# Chevron Qualitative Brief

## Strategic Narrative

Chevron's letters project an innovation identity rooted in operational excellence, safety, capital discipline, advantaged assets, and shareholder returns. The 2013 letter emphasizes operational excellence, safety, long-term production growth, and enduring stockholder value under John Watson. Evidence: {cite("Chevron", 2013)}.

The 2018 letter, Michael Wirth's first in the selected set, adds a stronger culture and innovation narrative. It links dynamic conditions, employee ingenuity, digital technologies, operational excellence, safety, and the Future Energy Fund. This is a key inflection because Chevron begins to present lower-carbon and breakthrough technology investment as compatible with its traditional performance culture. Evidence: {cite("Chevron", 2018)}.

The 2022 and 2024 letters sharpen the formula: "higher returns, lower carbon" and reliable energy to a growing world. Chevron frames the energy transition through customer relationships, lower-carbon intensity, partnerships, acquisitions, hydrogen, CCUS, renewable fuels, and energy security. In 2024, Chevron also connects natural-gas power solutions to AI/data-center demand, making energy infrastructure part of digital-economy growth. Evidence: {cite("Chevron", 2022)}, {cite("Chevron", 2024)}.

## Innovation Framing

Innovation is framed as operational and asset-based. Chevron does discuss technology and lower-carbon initiatives, but these are usually embedded in existing capabilities: deepwater engineering, Permian production, refining synergies, partnerships, venture funds, hydrogen, CCUS, and renewable fuels.

## Explore vs Exploit

Chevron is the most exploitative-leaning of the four firms, but this does not mean it lacks exploration. Rather, exploration is bounded by disciplined capital allocation and existing competitive strengths. The company uses exploitative language in service of selective exploration: reliable operations and strong cash flows enable lower-carbon projects, acquisitions, and partnerships. Evidence: {cite("Chevron", 2018)}, {cite("Chevron", 2024)}.

## Shifts Over Time

The shift is from classic operational excellence and production growth toward a broader "affordable, reliable, ever-cleaner energy" narrative. However, Chevron's rhetoric remains more stable than Amazon's or Nvidia's. Strategic renewal is presented as continuity with Chevron's capabilities, not as reinvention of the company's identity.
""",
    )

    write(
        "05_outputs/company_briefs/qualitative_cross_case_synthesis.md",
        f"""
# Qualitative Cross-Case Synthesis

## Strategic Narratives Over Time

Amazon presents innovation as customer-backward invention compounded over time. Its letters create a throughline from Day 1 and long-term market leadership in 1997 to AI, robotics, chips, satellite broadband, and organizational speed in 2025. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}.

Nvidia presents innovation as architectural and ecosystemic. Its strategic narrative is about sensing a technological discontinuity, building a platform around it, and scaling that platform into a full-stack infrastructure layer. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

Shell presents innovation as integrated-energy renewal under transition pressure. It does not narrate innovation mainly as invention; it narrates it as portfolio reshaping, low-carbon market formation, customer partnerships, LNG/gas strength, and capital discipline. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Chevron presents innovation as disciplined improvement of an advantaged asset base. It emphasizes safety, operational excellence, shareholder returns, and lower-carbon solutions that fit customer needs and Chevron capabilities. Evidence: {cite("Chevron", 2018)}, {cite("Chevron", 2024)}.

## Innovation Identities

Amazon's identity is the customer-obsessed builder. Nvidia's identity is the AI platform/infrastructure orchestrator. Shell's identity is the integrated energy transition company. Chevron's identity is the reliable, operationally excellent energy incumbent adapting through profitable lower-carbon adjacencies.

## Explore, Exploit, and Ambidexterity

All four companies are ambidextrous, but the balance differs. Amazon and Nvidia make exploration more visible and more central to identity. Shell and Chevron make exploitation more visible because safety, cash generation, asset productivity, policy stability, and shareholder distributions are strategic constraints and legitimacy conditions. The important finding is not that energy firms avoid exploration; it is that they narrate exploration as conditional on capital discipline, customer demand, policy support, and operational reliability.

## Rhetoric vs Strategic Reality

The letters are leadership narratives, so they should not be treated as objective records of innovation success. Amazon's failure-tolerant rhetoric is unusually explicit, but it still selects successful examples more often than unsuccessful ones. Nvidia's platform narrative is compelling, but it is written during a period of extraordinary AI demand and may understate concentration and supply risks. Shell and Chevron present lower-carbon transition as compatible with shareholder value, but their letters also show how strongly transition is bounded by demand, policy, and hydrocarbon cash flows. These are not contradictions; they are evidence of ambidextrous tension.
""",
    )

    write(
        "05_outputs/company_briefs/explore_exploit_analysis.md",
        f"""
# Explore vs Exploit Analysis

## Quantitative Starting Point

Explore/exploit ratios are saved in `05_outputs/tables/explore_exploit_ratios.csv`. The ratios count strict exploration terms such as invention, experimentation, discovery, emerging opportunity, R&D, and pilots against exploitation terms such as operational excellence, cash flow, returns, capital discipline, productivity, reliability, safety, execution, and scale.

This ratio is a starting signal, not the final classification. Technology-specific exploration often appears as named domains such as AI, GPU computing, cloud, robotics, and chips. Those terms are counted primarily under Horizon Scanning / Sense-making and Strategic Options, not always under the explore pair. The company assessments below therefore combine paired counts with the Innovation Process Model counts and qualitative context.

## Company Patterns

### Amazon

Amazon leans exploratory in rhetoric, but the exploration is consistently tied to exploitation of scale, customer data, infrastructure, and operating mechanisms. In 1997, Bezos frames bold investment as acceptable only when measured analytically and connected to long-term market leadership. In 2025, Jassy argues for parallel paths and large AI capex while grounding those bets in customer commitments, ROIC, AWS capacity, and long-term FCF. Amazon therefore appears highly ambidextrous: it uses exploitative measurement to justify exploratory investment. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}.

### Nvidia

Nvidia is the most exploratory in strategic posture. The selected letters repeatedly identify new waves: GPU computing, AI, accelerated computing, edge AI, agentic AI, physical AI, and AI factories. Yet Nvidia's exploration is not abstract. It is anchored in accumulated architectural capability, developer ecosystems, partnerships, and supply-chain execution. The 2025 letter pairs frontier AI language with operational scale and disciplined investment. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

### Shell

Shell is ambidextrous under constraint. It explicitly needs hydrocarbon cash flows, LNG, upstream assets, safety, and disciplined capital allocation to fund and pace transition. The 2020 review states that upstream oil and gas cash flows will help fund low-carbon investments; the 2025 review says lower-carbon platforms will be developed when policy and customer demand create attractive business models. This is classic incumbent ambidexterity: preserve the core while building transition options. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

### Chevron

Chevron is the most exploitative-leaning firm in the corpus. Its letters repeatedly foreground operational excellence, safety, capital discipline, strong balance sheet, dividends, buybacks, record production, and advantaged assets. Exploration exists, but it is bounded by strategic fit: Future Energy Fund, OGCI, Renewable Energy Group, hydrogen, CCUS, renewable diesel, Hess, and AI/data-center power partnerships are framed as extensions of Chevron's strengths rather than as identity-breaking moves. Evidence: {cite("Chevron", 2018)}, {cite("Chevron", 2022)}, {cite("Chevron", 2024)}.

## Pairwise Comparisons

### Amazon vs Nvidia

Amazon's exploration is customer-experience and business-model centered. Nvidia's exploration is technology-architecture and ecosystem centered. Amazon talks more about experimentation mechanisms and customer proof; Nvidia talks more about waves of computing, full-stack platforms, and infrastructure scale.

### Shell vs Chevron

Shell's exploration is more explicitly tied to energy-transition market formation and customer decarbonization. Chevron's exploration is more tightly attached to operational excellence, advantaged assets, and shareholder returns. Shell sounds more transformational; Chevron sounds more continuity-based.

### Technology vs Energy

The technology companies narrate exploration as a source of category creation and platform expansion. The energy companies narrate exploration as renewal under physical, capital, safety, commodity, and policy constraints. That distinction is central to the paper: both industries innovate, but their innovation visibility and rhetorical grammar differ.
""",
    )

    write(
        "05_outputs/company_briefs/innovation_process_model_analysis.md",
        f"""
# Innovation Process Model Analysis

## Company Mapping

### Amazon

Strategic Leadership: Amazon frames leadership as long-term, customer-obsessed, willing to be misunderstood, and comfortable with bold investment. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}.

Horizon Scanning / Sense-making: Amazon identifies inflections such as the Internet, pandemic disruption, cloud migration, AI, robotics, space connectivity, and geopolitical turbulence. Evidence: {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

Purpose, Vision, and Governance: Customer value is the most stable purpose language. Shareholder value is justified through long-term customer value rather than near-term distributions. Evidence: {cite("Amazon", 1997)}.

Strategic Options, Experimentation, and Choices: Amazon is strongest here. The letters discuss parallel paths, iterative invention, MLPs, autonomous teams, failure, and selective persistence. Evidence: {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

Agile Execution and Organization: Amazon emphasizes speed, separable teams, infrastructure, fulfillment capacity, robotics, and organizational flattening. Evidence: {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

### Nvidia

Strategic Leadership: Nvidia frames leadership through technical conviction, company reinvention, and platform ambition. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

Horizon Scanning / Sense-making: This is a dominant dimension. Nvidia repeatedly names technology waves and argues that AI is restructuring computing and industry. Evidence: {cite("Nvidia", 2025)}.

Purpose, Vision, and Governance: Purpose is expressed through enabling industries, developers, enterprises, countries, and scientific/industrial progress.

Strategic Options, Experimentation, and Choices: Nvidia's options logic is roadmap and platform based: chips, systems, software, models, networking, partners, and ecosystems are integrated into AI factories. Evidence: {cite("Nvidia", 2025)}.

Agile Execution and Organization: Execution language centers on engineering, supply-chain scale, deployment velocity, customer continuity, and disciplined investment.

### Shell

Strategic Leadership: Shell's leadership language emphasizes safety, responsibility, resilience, performance, and discipline. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Horizon Scanning / Sense-making: Shell scans climate change, energy demand, geopolitics, AI, policy, and the evolving energy system. Evidence: {cite("Shell", 2025)}.

Purpose, Vision, and Governance: The company links shareholder value, net-zero ambition, respect for nature, energy security, customers, and trust.

Strategic Options, Experimentation, and Choices: Shell's choices are portfolio and market-formation choices: BG, LNG, hydrogen, CCS, renewable power, SAF, divestments, and stopping projects that do not meet competitiveness tests. Evidence: {cite("Shell", 2015)}, {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Agile Execution and Organization: Shell emphasizes simplification, faster decisions, reorganization, cost reduction, operational performance, and integrated trading/optimization.

### Chevron

Strategic Leadership: Chevron frames leadership through reliability, operational excellence, safety, trust, and disciplined capital stewardship. Evidence: {cite("Chevron", 2013)}, {cite("Chevron", 2018)}.

Horizon Scanning / Sense-making: Chevron scans energy demand, geopolitical volatility, climate concerns, lower-carbon opportunities, and AI/data-center demand. Evidence: {cite("Chevron", 2024)}.

Purpose, Vision, and Governance: The recurring purpose phrase is affordable, reliable, ever-cleaner energy enabling human progress, paired with stockholder value.

Strategic Options, Experimentation, and Choices: Options appear through Future Energy Fund, OGCI, Renewable Energy Group, Hess, CCUS, hydrogen, renewable diesel, partnerships, and exploration acreage. Evidence: {cite("Chevron", 2018)}, {cite("Chevron", 2022)}, {cite("Chevron", 2024)}.

Agile Execution and Organization: Chevron is strongest in operational execution: safety, reliability, productivity, project milestones, capital efficiency, and portfolio optimization.

## Cross-Firm Interpretation

Amazon and Nvidia are strongest in horizon scanning and strategic options because their industries reward rapid category creation and platform scaling. Shell and Chevron are strongest in purpose/governance and agile execution because energy innovation must be legitimate, safe, capital-disciplined, policy-aware, and operationally reliable. The Innovation Process Model therefore does not rank firms by innovativeness; it shows how industry context changes the visible form of innovation strategy.
""",
    )

    write(
        "05_outputs/industry_comparison/comparative_analysis_working_draft.md",
        f"""
# Comparative Analysis Working Draft

## 1. Within-Company Over Time

Amazon evolves from founder doctrine to mature platform renewal. The 1997 letter establishes Day 1, customer obsession, long-termism, and bold investment. The Jassy letters retain that doctrine but apply it to scale problems: pandemic logistics, AWS, devices, climate, Kuiper/Amazon Leo, robotics, chips, and AI. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

Nvidia evolves from GPU computing platform to AI infrastructure company. The letters move from gaming, visualization, AI, and self-driving cars toward full-stack AI factories, inference, agentic AI, physical AI, sovereign/enterprise adoption, and global supply-chain execution. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

Shell evolves from acquisition and transition ambition toward a more disciplined integrated-energy strategy. The 2020 review is expansive about Powering Progress and low-carbon market formation; the 2025 review narrows the strategy around performance, discipline, simplification, LNG/upstream strength, and lower-carbon platforms with attractive business models. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Chevron evolves less dramatically. It adds lower-carbon and digital/AI-adjacent language over time, but its core narrative remains stable: operational excellence, safety, disciplined capital, shareholder returns, and reliable energy. Evidence: {cite("Chevron", 2013)}, {cite("Chevron", 2024)}.

## 2. Within-Industry Comparisons

### Amazon vs Nvidia

Both firms narrate innovation as platform expansion, but their platform logics differ. Amazon's platform logic is customer-backward and business-model expansive: retail, logistics, AWS, ads, devices, entertainment, grocery, satellites, AI, and chips. Nvidia's platform logic is architecture-forward: GPUs, systems, software, networking, models, developers, partners, and AI factories. Amazon emphasizes experimentation mechanisms; Nvidia emphasizes technological waves and integrated stack control.

### Shell vs Chevron

Both firms narrate energy innovation through reliability, capital discipline, and transition. Shell is more explicit about transformation of the energy system, net-zero ambition, customer decarbonization, and lower-carbon market formation. Chevron is more explicit about operational excellence, safety, stockholder returns, record production, and lower-carbon projects that extend its existing capabilities.

## 3. Across Industries

The central cross-industry difference is not whether firms innovate, but how innovation becomes visible. In technology, exploration is public, central, and identity-forming. Amazon and Nvidia can present AI, cloud, robotics, chips, and platforms as growth engines. In energy, exploration is filtered through capital intensity, safety, commodity cycles, regulation, policy, asset lives, and shareholder distributions. Shell and Chevron therefore present innovation as disciplined transition, asset optimization, and selective lower-carbon options.

## 4. Across All Four Firms

All four firms use long-term language, but they mean different things. Amazon uses long-termism to defend investment patience and invention. Nvidia uses it to justify infrastructure roadmaps and ecosystem scale. Shell uses it to explain energy transition pacing, policy dependence, and integrated energy positioning. Chevron uses it to defend durable assets, production growth, balance-sheet strength, and energy security.

All four firms also use ambidextrous logic. Amazon and Nvidia exploit scale and platforms to explore new domains. Shell and Chevron exploit hydrocarbon cash flows, operational excellence, and customer relationships to explore lower-carbon adjacencies. The similarities are real, but superficial comparison would miss the different constraints and strategic grammar of each industry.
""",
    )

    write(
        "05_outputs/methodology_briefs/findings_and_conclusion_working_draft.md",
        f"""
# Findings & Conclusion Working Draft

## Main Quantitative Findings

The normalized lexical results support the broad hypothesis but require careful interpretation. Amazon and Nvidia show more visible exploratory, technology, and strategic-options language than the energy firms. Shell and Chevron show stronger exploitative and execution/governance language, especially around safety, capital discipline, cash flow, reliability, shareholder distributions, and portfolio management. Company-level tables are saved in `05_outputs/tables/quant_summary_by_company.csv` and `05_outputs/tables/theme_counts_normalized.csv`.

## Main Qualitative Findings

Amazon's letters show a durable customer-obsessed innovation doctrine that scales from online commerce to AI, robotics, chips, satellites, fulfillment, and organizational design. Nvidia's letters show strategic renewal from GPU computing to full-stack AI infrastructure. Shell's letters show transition ambidexterity: fund and transform through integrated energy, LNG, customer decarbonization, and lower-carbon platforms. Chevron's letters show disciplined continuity: operational excellence, safety, advantaged assets, and selective lower-carbon expansion. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2025)}, {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}, {cite("Shell", 2020)}, {cite("Shell", 2025)}, {cite("Chevron", 2018)}, {cite("Chevron", 2024)}.

## Explore vs Exploit Findings

The strongest conclusion is that all four companies are ambidextrous, but they narrate ambidexterity differently. Amazon uses exploitative scale, data, infrastructure, and metrics to support exploration. Nvidia uses technical leadership, platforms, and supply-chain scale to pursue AI frontier opportunities. Shell uses hydrocarbon cash flow and integrated capabilities to fund transition options. Chevron uses operational excellence and capital discipline to pursue lower-carbon adjacencies without destabilizing the core.

## Innovation Process Model Findings

The Innovation Process Model helps avoid a shallow "more innovation words equals more innovation" conclusion. Amazon is strongest in Purpose/Vision and Strategic Options. Nvidia is strongest in Horizon Scanning and Strategic Options. Shell combines Horizon Scanning with Purpose/Governance under energy-transition pressure. Chevron combines Purpose/Governance with Agile Execution and Organization. These patterns reflect industry context as much as leadership preference.

## Methodological Cautions

CEO/shareholder letters are strategic rhetoric, not neutral evidence. They are valuable because they show how leaders frame strategy, but they can omit failed projects, internal conflict, and implementation problems. Lexical counts are also imperfect: terms such as growth, platform, return, and safety are context-dependent. The final paper should therefore treat the quantitative analysis as a structured signal and the qualitative analysis as the interpretive core.

## Conclusion for Milestone

The milestone evidence supports a defensible CE hypothesis: technology-platform firms make exploration more explicit and central to identity, while energy firms frame innovation through disciplined renewal of capital-intensive, regulated, safety-critical asset systems. The best comparison is not tech innovation versus energy non-innovation. It is two different forms of corporate entrepreneurship: digital-platform exploration at speed and incumbent-energy renewal under constraint.
""",
    )

    write(
        "MILESTONE_SUMMARY.md",
        f"""
# Milestone Summary

Analysis date: {TODAY}.

## What Is Ready

This milestone package analyzes the confirmed 28-text corpus: seven CEO/shareholder leadership texts each for Amazon, Nvidia, and Chevron, and seven CEO reviews (Chief Executive Officer's review sections of the Shell Annual Report) for Shell. The corpus is stored in `02_extracted_text/selected_ceo_letters/`, with a machine-readable manifest at `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`.

## Final Letter Set

{company_year_summary}

## Research Hypothesis

The working hypothesis is that technology-platform firms will use more explicit exploratory and option-creation language, while oil-and-gas firms will frame innovation through operational discipline, capital allocation, safety, resilience, and regulated transition. The hypothesis explicitly avoids a simplistic split: all four firms display ambidexterity, but industry context changes how exploration and exploitation are narrated.

## Methodology Logic

The method combines normalized lexical analysis with qualitative interpretation. The unit of analysis is each selected leadership communication (letter or CEO review), not each full annual report. Counts were normalized per 1,000 words. The Innovation Process Model is the main framework, and explore/exploit analysis is used as a supporting lens.

## Quantitative Status

The quantitative tables have been generated:

- `05_outputs/tables/quant_summary_by_company.csv`
- `05_outputs/tables/quant_summary_by_letter.csv`
- `05_outputs/tables/theme_counts_normalized.csv`
- `05_outputs/tables/explore_exploit_ratios.csv`
- `05_outputs/tables/ipm_comparison_matrix.csv`
- `05_outputs/tables/comparative_matrix.csv`

The analysis uses strict dictionary terms and documents ambiguity risks in `05_outputs/company_briefs/quantitative_analysis_working_draft.md`.

## Qualitative Status

Company-level qualitative briefs are complete for Amazon, Nvidia, Shell, and Chevron, along with a cross-case synthesis. The qualitative analysis is grounded in the selected letters and focuses on innovation identity, leadership framing, strategic options, exploit/explore balance, and shifts over time.

## Explore vs Exploit Findings

Amazon and Nvidia make exploration more visible and identity-defining. Shell and Chevron make exploitation more visible because their innovation logic is constrained by safety, capital intensity, asset life, commodity cycles, regulation, policy, and shareholder distributions. All four firms are ambidextrous, but the form of ambidexterity differs.

## Innovation Process Model Findings

Amazon: customer purpose plus strategic options and experimentation.

Nvidia: horizon scanning plus strategic options around AI infrastructure.

Shell: transition sense-making, purpose/governance, and disciplined portfolio renewal.

Chevron: purpose/governance plus agile execution, operational excellence, and selective lower-carbon options.

## Comparative Insights

The project is strongest when framed as a comparison of innovation logics rather than a ranking of innovativeness. Technology innovation is visible as platform expansion and category creation. Energy innovation is visible as disciplined renewal of large, regulated, safety-critical, capital-intensive systems.

## Key Files for Human Review

- `05_outputs/company_briefs/final_letter_set_confirmation.md`
- `05_outputs/methodology_briefs/initial_outline.md`
- `05_outputs/methodology_briefs/research_hypothesis.md`
- `05_outputs/methodology_briefs/methodology_draft.md`
- `05_outputs/company_briefs/quantitative_analysis_working_draft.md`
- `05_outputs/company_briefs/qualitative_cross_case_synthesis.md`
- `05_outputs/company_briefs/explore_exploit_analysis.md`
- `05_outputs/company_briefs/innovation_process_model_analysis.md`
- `05_outputs/industry_comparison/comparative_analysis_working_draft.md`
- `05_outputs/methodology_briefs/findings_and_conclusion_working_draft.md`

## Next Recommended Steps

1. Human-review the extracted letter corpus for any remaining extraction artifacts.
2. Review the strict dictionary against the qualitative briefs and remove any terms the instructor considers too noisy.
3. Use the generated tables to create simple charts only after the final dictionary is frozen.
4. Convert this milestone package into the final paper sections, keeping the quantitative analysis as supporting evidence and the qualitative/IPM analysis as the interpretive core.
""",
    )


def patch_missing_comparative() -> None:
    """Write comparative draft after the accidental guard in write_docs."""
    write(
        "05_outputs/industry_comparison/comparative_analysis_working_draft.md",
        f"""
# Comparative Analysis Working Draft

## 1. Within-Company Over Time

Amazon evolves from founder doctrine to mature platform renewal. The 1997 letter establishes Day 1, customer obsession, long-termism, and bold investment. The Jassy letters retain that doctrine but apply it to scale problems: pandemic logistics, AWS, devices, climate, Kuiper/Amazon Leo, robotics, chips, and AI. Evidence: {cite("Amazon", 1997)}, {cite("Amazon", 2021)}, {cite("Amazon", 2025)}.

Nvidia evolves from GPU computing platform to AI infrastructure company. The letters move from gaming, visualization, AI, and self-driving cars toward full-stack AI factories, inference, agentic AI, physical AI, sovereign/enterprise adoption, and global supply-chain execution. Evidence: {cite("Nvidia", 2017)}, {cite("Nvidia", 2025)}.

Shell evolves from acquisition and transition ambition toward a more disciplined integrated-energy strategy. The 2020 review is expansive about Powering Progress and low-carbon market formation; the 2025 review narrows the strategy around performance, discipline, simplification, LNG/upstream strength, and lower-carbon platforms with attractive business models. Evidence: {cite("Shell", 2020)}, {cite("Shell", 2025)}.

Chevron evolves less dramatically. It adds lower-carbon and digital/AI-adjacent language over time, but its core narrative remains stable: operational excellence, safety, disciplined capital, shareholder returns, and reliable energy. Evidence: {cite("Chevron", 2013)}, {cite("Chevron", 2024)}.

## 2. Within-Industry Comparisons

### Amazon vs Nvidia

Both firms narrate innovation as platform expansion, but their platform logics differ. Amazon's platform logic is customer-backward and business-model expansive: retail, logistics, AWS, ads, devices, entertainment, grocery, satellites, AI, and chips. Nvidia's platform logic is architecture-forward: GPUs, systems, software, networking, models, developers, partners, and AI factories. Amazon emphasizes experimentation mechanisms; Nvidia emphasizes technological waves and integrated stack control.

### Shell vs Chevron

Both firms narrate energy innovation through reliability, capital discipline, and transition. Shell is more explicit about transformation of the energy system, net-zero ambition, customer decarbonization, and lower-carbon market formation. Chevron is more explicit about operational excellence, safety, stockholder returns, record production, and lower-carbon projects that extend its existing capabilities.

## 3. Across Industries

The central cross-industry difference is not whether firms innovate, but how innovation becomes visible. In technology, exploration is public, central, and identity-forming. Amazon and Nvidia can present AI, cloud, robotics, chips, and platforms as growth engines. In energy, exploration is filtered through capital intensity, safety, commodity cycles, regulation, policy, asset lives, and shareholder distributions. Shell and Chevron therefore present innovation as disciplined transition, asset optimization, and selective lower-carbon options.

## 4. Across All Four Firms

All four firms use long-term language, but they mean different things. Amazon uses long-termism to defend investment patience and invention. Nvidia uses it to justify infrastructure roadmaps and ecosystem scale. Shell uses it to explain energy transition pacing, policy dependence, and integrated energy positioning. Chevron uses it to defend durable assets, production growth, balance-sheet strength, and energy security.

All four firms also use ambidextrous logic. Amazon and Nvidia exploit scale and platforms to explore new domains. Shell and Chevron exploit hydrocarbon cash flows, operational excellence, and customer relationships to explore lower-carbon adjacencies. The similarities are real, but superficial comparison would miss the different constraints and strategic grammar of each industry.

## Evidence Tables

Use `05_outputs/tables/comparative_matrix.csv` as the compact matrix version of this analysis, and `05_outputs/tables/ipm_comparison_matrix.csv` for the Innovation Process Model comparison.
""",
    )


def update_research_log() -> None:
    log = ROOT / "00_admin" / "research_log.md"
    existing = log.read_text(encoding="utf-8") if log.exists() else "# Research Log\n"
    note = f"""

## {TODAY} - Milestone Comparative Letter Analysis Package

- Built a 28-letter milestone analysis package from `02_extracted_text/selected_ceo_letters/`.
- Generated normalized lexical tables for Innovation Process Model themes and cross-cutting paired comparisons.
- Produced working drafts for outline, hypothesis, methodology, quantitative analysis, qualitative company briefs, explore/exploit analysis, Innovation Process Model analysis, comparative analysis, findings/conclusion, and `MILESTONE_SUMMARY.md`.
- Reproducibility script: `00_admin/build_milestone_analysis_package.py`.
"""
    if "Milestone Comparative Letter Analysis Package" not in existing:
        log.write_text(existing.rstrip() + note + "\n", encoding="utf-8")


def write_dictionary_csvs() -> None:
    """Regenerate the CSV dictionaries from the canonical Python dicts so the
    public lexicons mirror what the matcher actually applies."""
    kw_dir = ROOT / "04_quant_framework" / "keyword_lists"
    kw_dir.mkdir(parents=True, exist_ok=True)
    with (kw_dir / "explore_exploit_dictionary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "base", "aliases", "excludes"])
        for dim, terms in CROSS_TERMS.items():
            for term in terms:
                if isinstance(term, str):
                    w.writerow([dim, term, "", ""])
                else:
                    w.writerow([dim, term["base"], ", ".join(term.get("aliases") or []), ", ".join(term.get("excludes") or [])])
    with (kw_dir / "theme_dictionary_master.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "theme", "subtheme", "concept_definition",
            "strict_keywords", "aliases", "excludes",
            "automatic_count", "manual_check_required", "likely_noisy_terms",
        ])
        for row in THEME_SUBTHEMES:
            bases, aliases, excludes = [], [], []
            for term in row["terms"]:
                if isinstance(term, str):
                    bases.append(term)
                else:
                    bases.append(term["base"])
                    aliases.extend(term.get("aliases") or [])
                    excludes.extend(term.get("excludes") or [])
            w.writerow([
                row["theme"], row["subtheme"],
                f"Stem-aware lexical evidence of {row['subtheme'].lower()} within {row['theme'].lower()}.",
                ", ".join(bases),
                ", ".join(sorted(set(aliases))),
                ", ".join(sorted(set(excludes))),
                "stem_match_with_curated_aliases_and_excludes",
                "yes",
                "leadership, growth, platform, resilience, value, capital",
            ])


def main() -> None:
    ensure_dirs()
    write_dictionary_csvs()
    manifest_rows = read_manifest()
    letters = load_letters(manifest_rows)
    company_data = aggregate_company(letters)
    write_csvs(letters, company_data)
    write_docs(letters, company_data)
    patch_missing_comparative()
    update_research_log()
    print(f"Built milestone package from {len(letters)} letters.")
    for company, data in company_data.items():
        print(f"{company}: {len(data['items'])} letters, {data['words']} body words")


if __name__ == "__main__":
    main()
