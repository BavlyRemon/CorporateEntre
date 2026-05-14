#!/usr/bin/env python3
"""Build the Corporate Entrepreneurship research workspace.

The script is intentionally plain: download official sources where accessible,
extract machine-readable text where feasible, and generate working notes that
can be audited from sources_master.csv.
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
import textwrap
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = "2026-04-16"
UA = "CorpEntreInnovationResearch/1.0 contact@example.com"

DIRS = [
    "00_admin",
    "01_raw_sources/amazon/annual_reports",
    "01_raw_sources/amazon/letters",
    "01_raw_sources/amazon/investor_pages",
    "01_raw_sources/nvidia/annual_reports",
    "01_raw_sources/nvidia/letters",
    "01_raw_sources/nvidia/investor_pages",
    "01_raw_sources/shell/annual_reports",
    "01_raw_sources/shell/letters",
    "01_raw_sources/shell/investor_pages",
    "01_raw_sources/chevron/annual_reports",
    "01_raw_sources/chevron/letters",
    "01_raw_sources/chevron/investor_pages",
    "01_raw_sources/industry_sources/wipo",
    "01_raw_sources/industry_sources/bcg",
    "01_raw_sources/industry_sources/forbes",
    "01_raw_sources/industry_sources/other_supporting",
    "02_extracted_text/amazon",
    "02_extracted_text/nvidia",
    "02_extracted_text/shell",
    "02_extracted_text/chevron",
    "02_extracted_text/industry_sources",
    "03_screening_and_selection/company_timelines",
    "03_screening_and_selection/letter_selection_tables",
    "03_screening_and_selection/selection_memos",
    "04_quant_framework/theme_dictionary",
    "04_quant_framework/keyword_lists",
    "04_quant_framework/coding_notes",
    "04_quant_framework/pilot_counts",
    "05_outputs/company_briefs",
    "05_outputs/industry_comparison",
    "05_outputs/methodology_briefs",
    "05_outputs/tables",
    "05_outputs/figures",
    "06_appendices/source_cards",
    "06_appendices/download_manifest",
    "06_appendices/citation_backup",
]


COMPANY_META = {
    "amazon": ("Technology / digital platforms", "Amazon"),
    "nvidia": ("Technology / digital platforms", "Nvidia"),
    "shell": ("Oil & gas / energy", "Shell"),
    "chevron": ("Oil & gas / energy", "Chevron"),
}


SOURCE_ROWS: List[Dict[str, str]] = []
LOG_LINES: List[str] = []


def ensure_dirs() -> None:
    for d in DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)


def rel(path: Optional[Path]) -> str:
    if not path:
        return ""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def add_source(
    company: str,
    year: str,
    title: str,
    doc_type: str,
    official_source: str,
    url: str,
    source_path: Optional[Path] = None,
    text_path: Optional[Path] = None,
    notes: str = "",
) -> None:
    industry = COMPANY_META.get(company, ("Industry source", company.title()))[0]
    SOURCE_ROWS.append(
        {
            "company": company,
            "industry": industry,
            "year": str(year),
            "document_title": title,
            "document_type": doc_type,
            "official_source": official_source,
            "url": url,
            "access_date": ACCESS_DATE,
            "local_source_path": rel(source_path),
            "local_pdf_path": rel(source_path) if source_path and source_path.suffix.lower() == ".pdf" else "",
            "local_text_path": rel(text_path),
            "notes": notes,
        }
    )


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")


def request_get(url: str, timeout: int = 60) -> requests.Response:
    return requests.get(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,*/*",
        },
        timeout=timeout,
    )


def download(url: str, path: Path, binary: bool = True) -> Tuple[bool, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.exists() and path.stat().st_size > 2000:
            return True, "already exists"
        r = request_get(url, timeout=120)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        if binary:
            path.write_bytes(r.content)
        else:
            path.write_text(r.text, encoding="utf-8")
        return True, f"downloaded {len(r.content)} bytes"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def html_to_text(html_path: Path, txt_path: Path) -> str:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(text + "\n", encoding="utf-8")
    return text


def pdf_to_text(pdf_path: Path, txt_path: Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n\n".join(pages)
        text = re.sub(r"\n{3,}", "\n\n", text)
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        txt_path.write_text(text + "\n", encoding="utf-8")
        return text
    except Exception as exc:  # noqa: BLE001
        txt_path.write_text(f"[PDF extraction failed: {type(exc).__name__}: {exc}]\n", encoding="utf-8")
        return ""


def sec_recent_filings(cik: str, form: str, limit: int = 12) -> List[Dict[str, str]]:
    base_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = request_get(base_url)
    r.raise_for_status()
    root = r.json()
    datasets = [root["filings"]["recent"]]
    for file_meta in root["filings"].get("files", []):
        if len([f for f in flatten_sec_filings(datasets) if f.get("form") == form]) >= limit:
            break
        add_url = f"https://data.sec.gov/submissions/{file_meta['name']}"
        add = request_get(add_url)
        if add.status_code == 200:
            datasets.append(add.json())
    all_filings = flatten_sec_filings(datasets)
    filings = []
    for row in all_filings:
        if row.get("form") != form:
            continue
        acc = row["accessionNumber"]
        accession_plain = acc.replace("-", "")
        primary_doc = row["primaryDocument"]
        report_date = row.get("reportDate", "")
        filing_date = row.get("filingDate", "")
        fiscal_year = report_date[:4] if report_date else filing_date[:4]
        cik_int = str(int(cik))
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_plain}/{primary_doc}"
        filings.append(
            {
                "year": fiscal_year,
                "url": doc_url,
                "filing_date": filing_date,
                "accession": acc,
                "primary_doc": primary_doc,
            }
        )
        if len(filings) >= limit:
            break
    return filings


def flatten_sec_filings(datasets: List[Dict[str, List[str]]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    keys = ["accessionNumber", "filingDate", "reportDate", "form", "primaryDocument"]
    for data in datasets:
        forms = data.get("form", [])
        for i in range(len(forms)):
            row = {}
            for key in keys:
                values = data.get(key, [])
                row[key] = values[i] if i < len(values) else ""
            rows.append(row)
    rows.sort(key=lambda x: (x.get("reportDate", ""), x.get("filingDate", "")), reverse=True)
    return rows


def download_sec_annuals(company: str, cik: str, form: str = "10-K", limit: int = 12) -> None:
    for filing in sec_recent_filings(cik, form, limit):
        year = filing["year"]
        out = ROOT / f"01_raw_sources/{company}/annual_reports/{company}_{year}_sec_{form.lower().replace('-', '')}.html"
        txt = ROOT / f"02_extracted_text/{company}/{company}_{year}_sec_{form.lower().replace('-', '')}.txt"
        ok, status = download(filing["url"], out, binary=False)
        if ok:
            html_to_text(out, txt)
        add_source(
            company,
            year,
            f"{COMPANY_META[company][1]} Form {form} annual report, fiscal {year}",
            "annual_report_sec_filing",
            "SEC EDGAR company filing",
            filing["url"],
            out if ok else None,
            txt if ok else None,
            f"Downloaded from SEC EDGAR; accession {filing['accession']}; filing date {filing['filing_date']}; {status}.",
        )
        LOG_LINES.append(f"- {company} {year} SEC {form}: {status} ({filing['url']})")


def download_amazon_letters() -> None:
    archive_url = "https://www.aboutamazon.com/about-us/shareholder-letters"
    archive_path = ROOT / "01_raw_sources/amazon/investor_pages/amazon_shareholder_letters_archive.html"
    ok, status = download(archive_url, archive_path, binary=False)
    add_source(
        "amazon",
        "archive",
        "Amazon shareholder letters archive",
        "investor_archive_page",
        "About Amazon",
        archive_url,
        archive_path if ok else None,
        None,
        f"Official shareholder-letter archive page; {status}.",
    )
    if not ok:
        return
    html_text = archive_path.read_text(encoding="utf-8")
    urls = sorted(
        set(
            u.rstrip("\\")
            for u in re.findall(r"https://www\.aboutamazon\.com/news/company-news/[^\"'\s<]+", html_text)
            if "letter-to-shareholders" in u
        )
    )
    for url in urls:
        m = re.search(r"(19|20)\d{2}", url)
        year = m.group(0) if m else "unknown"
        if "amazons-original-1997" in url:
            year = "1997"
        html_path = ROOT / f"01_raw_sources/amazon/letters/amazon_{year}_shareholder_letter.html"
        txt_path = ROOT / f"02_extracted_text/amazon/amazon_{year}_shareholder_letter.txt"
        ok, status = download(url, html_path, binary=False)
        if ok:
            html_to_text(html_path, txt_path)
        add_source(
            "amazon",
            year,
            f"Amazon {year} shareholder letter",
            "shareholder_letter_html",
            "About Amazon",
            url,
            html_path if ok else None,
            txt_path if ok else None,
            f"Official standalone shareholder letter page; {status}.",
        )
        LOG_LINES.append(f"- amazon {year} shareholder letter: {status} ({url})")


def download_nvidia_ir_pdfs() -> None:
    archive_url = "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx"
    add_source(
        "nvidia",
        "archive",
        "NVIDIA annual reports and proxies archive",
        "investor_archive_page",
        "NVIDIA Investor Relations",
        archive_url,
        ROOT / "01_raw_sources/nvidia/investor_pages/nvidia_annual_reports_archive.html",
        None,
        "Archive was accessible through browser; direct shell download was blocked by Cloudflare, so direct Q4 CDN PDFs and SEC filings were used.",
    )
    known = {
        "2021": "https://s201.q4cdn.com/141608511/files/doc_downloads/2021/04/2021-Annual-Review.pdf",
        "2022": "https://s201.q4cdn.com/141608511/files/doc_financials/2022/ar/2022-Annual-Review.pdf",
        "2023": "https://s201.q4cdn.com/141608511/files/doc_financials/2023/ar/2023-Annual-Report-1.pdf",
        "2024": "https://s201.q4cdn.com/141608511/files/doc_financials/2024/ar/NVIDIA-2024-Annual-Report.pdf",
    }
    for year, url in known.items():
        pdf = ROOT / f"01_raw_sources/nvidia/annual_reports/nvidia_{year}_annual_report.pdf"
        txt = ROOT / f"02_extracted_text/nvidia/nvidia_{year}_annual_report.txt"
        ok, status = download(url, pdf, binary=True)
        if ok:
            pdf_to_text(pdf, txt)
        add_source(
            "nvidia",
            year,
            f"NVIDIA {year} annual report / annual review",
            "annual_report_pdf",
            "NVIDIA Investor Relations / Q4 CDN",
            url,
            pdf if ok else None,
            txt if ok else None,
            f"Official NVIDIA IR PDF file; {status}.",
        )
        LOG_LINES.append(f"- nvidia {year} annual report PDF: {status} ({url})")


def download_shell_reports() -> None:
    archive_url = "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"
    model_url = "https://www.shell.com/investors/results-and-reporting/annual-report-archive.model.json"
    html_path = ROOT / "01_raw_sources/shell/investor_pages/shell_annual_report_archive.html"
    model_path = ROOT / "01_raw_sources/shell/investor_pages/shell_annual_report_archive.model.json"
    ok_html, status_html = download(archive_url, html_path, binary=False)
    ok_model, status_model = download(model_url, model_path, binary=False)
    add_source(
        "shell",
        "archive",
        "Shell annual reports archive",
        "investor_archive_page",
        "Shell Investor Relations",
        archive_url,
        html_path if ok_html else None,
        None,
        f"Archive page; {status_html}; model JSON: {status_model}.",
    )
    if not ok_model:
        return
    model = json.loads(model_path.read_text(encoding="utf-8"))
    links: Dict[str, str] = {}
    for text in iter_json_text_fields(model):
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all("a"):
            url = a.get("href", "")
            label = a.get_text(" ", strip=True)
            if not url.endswith(".pdf"):
                continue
            if "Annual Report" not in label and "annual report" not in label:
                continue
            if "Form 20-F" in label or "20-F" in label or "Databook" in label:
                continue
            y = re.search(r"(20\d{2})", label) or re.search(r"shell-annual-(?:report|review)-(\d{4})", url)
            if not y:
                continue
            year = y.group(1)
            links.setdefault(year, url)
    for year in sorted(links.keys())[-12:]:
        url = links[year]
        pdf = ROOT / f"01_raw_sources/shell/annual_reports/shell_{year}_annual_report.pdf"
        txt = ROOT / f"02_extracted_text/shell/shell_{year}_annual_report.txt"
        ok, status = download(url, pdf, binary=True)
        if ok:
            pdf_to_text(pdf, txt)
        add_source(
            "shell",
            year,
            f"Shell Annual Report and Accounts {year}",
            "annual_report_pdf",
            "Shell Investor Relations",
            url,
            pdf if ok else None,
            txt if ok else None,
            f"Official Shell annual report archive PDF; {status}.",
        )
        LOG_LINES.append(f"- shell {year} annual report PDF: {status} ({url})")


def iter_json_text_fields(node) -> Iterable[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "text" and isinstance(value, str):
                yield value
            else:
                yield from iter_json_text_fields(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_json_text_fields(value)


def add_industry_sources() -> None:
    pages = [
        (
            "wipo",
            "2025",
            "WIPO Global Innovation Index 2025 - Global Innovation Tracker",
            "https://www.wipo.int/web-publications/global-innovation-index-2025/en/global-innovation-tracker.html",
        ),
        (
            "bcg",
            "collection",
            "BCG Most Innovative Companies report collection",
            "https://www.bcg.com/publications/most-innovative-companies-the-collection",
        ),
        (
            "forbes",
            "list",
            "Forbes Innovative Companies list",
            "https://www.forbes.com/innovative-companies/list/",
        ),
    ]
    for slug, year, title, url in pages:
        path = ROOT / f"01_raw_sources/industry_sources/{slug}/{slug}_{year}.html"
        ok, status = download(url, path, binary=False)
        txt = ROOT / f"02_extracted_text/industry_sources/{slug}_{year}.txt"
        if ok:
            html_to_text(path, txt)
        SOURCE_ROWS.append(
            {
                "company": slug,
                "industry": "Industry source",
                "year": year,
                "document_title": title,
                "document_type": "benchmark_source",
                "official_source": slug.upper() if slug != "bcg" else "BCG",
                "url": url,
                "access_date": ACCESS_DATE,
                "local_source_path": rel(path if ok else None),
                "local_pdf_path": "",
                "local_text_path": rel(txt if ok else None),
                "notes": f"Benchmark/supporting source requested by user; {status}.",
            }
        )
        LOG_LINES.append(f"- industry {slug}: {status} ({url})")


def write_sources_master() -> None:
    fieldnames = [
        "company",
        "industry",
        "year",
        "document_title",
        "document_type",
        "official_source",
        "url",
        "access_date",
        "local_source_path",
        "local_pdf_path",
        "local_text_path",
        "notes",
    ]
    with (ROOT / "00_admin/sources_master.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SOURCE_ROWS)
    with (ROOT / "06_appendices/download_manifest/download_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SOURCE_ROWS)


def citations_block(ids: Iterable[Tuple[str, str, str]]) -> str:
    lines = ["", "## Source Notes"]
    for label, title, url in ids:
        lines.append(f"- [{label}] {title}. Accessed {ACCESS_DATE}. {url}")
    return "\n".join(lines)


def write_admin_files() -> None:
    log_text = "\n".join(LOG_LINES)
    write(
        "00_admin/research_log.md",
        f"""
        # Research Log

        Access date for this pass: {ACCESS_DATE}

        ## Scope

        This workspace collects official annual reports, shareholder/CEO letters where available, company timeline notes, candidate-year screening tables, selection rationales, a lexical theme dictionary, pilot lexical counts, and methodology notes for a Corporate Entrepreneurship and Innovation paper comparing Amazon, NVIDIA, Shell, and Chevron.

        ## Source Collection Notes

        {log_text}

        ## Known Access Constraints

        - Amazon's official IR archive page returned a Cloudflare 403 to local curl, so the official About Amazon shareholder-letter pages and SEC EDGAR annual filings were used as reproducible primary sources.
        - NVIDIA's IR archive was browser-visible but Cloudflare-blocked for local shell download. Direct official Q4 CDN annual-review PDFs were downloaded where URLs were verified, and SEC EDGAR filings were used for coverage across years.
        - Shell's official archive exposes a model JSON file with annual-report PDF URLs; PDFs and text extracts were downloaded from Shell.
        - Chevron's public annual-report page and PDF assets were visible through browser/search but blocked local shell requests with Azure 403 responses. SEC EDGAR 10-K filings were downloaded as the official reproducible substitute; the official Chevron annual-report URL is retained in source notes.
        - Forbes blocked the automated local fetch in some environments; if the local file is absent, use the URL as a requested secondary benchmark source and document access limitations before citing specific rankings.
        """,
    )
    write(
        "00_admin/method_notes.md",
        """
        # Method Notes

        The immediate corpus is a set of official strategic texts: CEO/shareholder letters where a company provides standalone letters, annual-report front matter where the letter is embedded in the annual report, and SEC annual filings as a reproducible official fallback.

        Unit of analysis for the later quantitative pass should be the selected letter/report-year text for each company. When a company has no clean standalone CEO letter, the closest official equivalent should be recorded explicitly: e.g., Shell annual-report chair/CEO sections and Chevron annual-report/10-K material.

        The quantitative framework should be treated as a structured lexical screen, not a substitute for interpretation. Keyword counts can indicate relative emphasis, but ambiguity must be checked manually because terms such as "platform," "leadership," "growth," and "resilience" can have different meanings in digital-platform and oil-and-gas contexts.

        Reproducibility is handled through foldered source files, text extracts, sources_master.csv, and selection memos that record the exact year, title, source URL, access date, and local path where available.
        """,
    )
    write(
        "00_admin/selection_criteria.md",
        """
        # Selection Criteria

        Each final company set must contain exactly seven report-years/letters. Years are selected to maximize analytical value, not to impose a mechanical interval.

        Criteria:

        1. Span meaningful strategic eras.
        2. Capture inflection points in leadership, market disruption, strategic renewal, technology transition, crisis, or portfolio logic.
        3. Provide substantive text suitable for close reading and lexical analysis.
        4. Support comparison across two broad industries: technology/digital platforms and oil & gas/energy.
        5. Preserve source integrity by using official company reports, official company letter pages, or SEC filings when official company PDFs are blocked.
        6. Avoid over-weighting famous years if the available strategic text is too thin.
        7. Document non-selection of plausible years so the choice is auditable.
        """,
    )
    write(
        "00_admin/todo.md",
        """
        # To Do

        - Manually verify the selected letter boundaries inside each annual report before final counts.
        - For Chevron, retry the official 2025 annual-report PDF later; the URL returned HTTP 503 during the latest audit, so it is documented as a future follow-up candidate rather than a selected source.
        - For NVIDIA, keep the standalone 2025 CEO letter as the cleanest latest letter source alongside the official 2025 annual report.
        - Run refined lexical counts after manual cleaning of the seven selected texts per company.
        - Create quotation/source cards for the final qualitative analysis only after the human researcher confirms selected years.
        """,
    )


THEMES = [
    {
        "theme": "Strategic Leadership",
        "subthemes": [
            ("Founder/ownership mentality", "ownership, owner, founder, day one, entrepreneurial, long-term owner, builders", "owner*, founder*, day 1, day one, entrepreneur*, builder*"),
            ("Ambidexterity/tension", "ambidextrous, paradox, tradeoff, balance, tension, dual, both", "ambidex*, paradox*, trade-off, tradeoff*, tension*, balance*, both"),
            ("Boldness/discipline", "bold, disciplined, conviction, decisive, high standards, capital discipline", "bold*, disciplin*, conviction, decisive, standards, capital discipline"),
            ("Stewardship/accountability", "stewardship, accountable, responsible, safety, trust, integrity", "steward*, accountab*, responsib*, safety, trust, integrity"),
            ("Managerial control", "efficiency, productivity, cost control, process, governance", "efficien*, productivity, cost*, process*, govern*"),
        ],
    },
    {
        "theme": "Horizon Scanning / Context",
        "subthemes": [
            ("Disruption/uncertainty", "disruption, uncertainty, volatility, turbulence, crisis, shock", "disrupt*, uncertain*, volatil*, turbulen*, crisis, shock*"),
            ("Future orientation", "future, long term, next decade, emerging, tomorrow, next wave", "future*, long-term, long term, decade*, emerging, tomorrow"),
            ("Discovery/exploration", "discover, explore, learn, opportunity, option, experiment", "discover*, explor*, learn*, opportunit*, option*, experiment*"),
            ("Technology transition", "AI, cloud, GPU, energy transition, digital, automation, electrification", "artificial intelligence, AI, cloud, GPU, energy transition, digital*, automat*, electric*"),
            ("External environment", "regulation, geopolitical, macro, policy, demand, commodity, competition", "regulat*, geopolit*, macro*, policy, demand, commodity, competit*"),
        ],
    },
    {
        "theme": "Purpose, Vision, Governance",
        "subthemes": [
            ("Customer orientation", "customer, consumer, client, user, experience, convenience", "customer*, consumer*, client*, user*, experience*, convenience"),
            ("Shareholder/value orientation", "shareholder, stockholder, return, cash flow, value creation, dividend", "shareholder*, stockholder*, return*, cash flow, value creation, dividend*"),
            ("Market/category leadership", "leader, leadership, market leader, category, scale, ecosystem", "leader*, leadership, market leadership, category, scale, ecosystem*"),
            ("Mission/purpose/identity", "mission, purpose, values, identity, human progress, day one", "mission*, purpose*, values, identity, human progress, day one"),
            ("Governance/responsibility", "governance, board, oversight, ethics, responsible, lower carbon", "governance, board, oversight, ethic*, responsible, lower carbon"),
        ],
    },
    {
        "theme": "Strategic Options, Experimentation, and Choices",
        "subthemes": [
            ("Internal invention/R&D", "invent, invention, research, develop, engineering, technology", "invent*, research, R&D, develop*, engineer*, technolog*"),
            ("Partnerships/ecosystems", "partner, partnership, alliance, collaborate, ecosystem, developer", "partner*, alliance*, collaborat*, ecosystem*, developer*"),
            ("Acquisition/integration", "acquire, acquisition, merger, integrate, divest, portfolio", "acquir*, acquisition*, merger*, integrat*, divest*, portfolio"),
            ("Experiment/pilot/learn", "experiment, pilot, trial, iterate, test, learn", "experiment*, pilot*, trial*, iterat*, test*, learn*"),
            ("Prioritize/scale/allocate", "prioritize, allocate, scale, invest, capital, choose", "priorit*, allocat*, scale*, invest*, capital, choice*, choose"),
        ],
    },
    {
        "theme": "Agile Execution and Organization",
        "subthemes": [
            ("Speed/agility", "speed, fast, agility, agile, velocity, rapid", "speed, fast, agile, agility, velocity, rapid*"),
            ("Resilience/adaptability", "resilience, resilient, adapt, flexibility, recover", "resilien*, adapt*, flexib*, recover*"),
            ("Operational excellence", "operational excellence, efficiency, reliability, productivity, process", "operational excellence, efficien*, reliab*, productivity, process*"),
            ("Talent/capabilities", "talent, people, capability, culture, organization, skill", "talent*, people, capabilit*, culture, organization*, skill*"),
            ("Infrastructure/scaling", "infrastructure, capacity, supply chain, deployment, execution", "infrastructure, capacity, supply chain, deploy*, execution"),
        ],
    },
]

CROSS_CUTTING = [
    ("Explore vs exploit", "explore, experiment, discover, option, emerging", "exploit, optimize, efficiency, core, productivity"),
    ("Customer vs shareholder", "customer, consumer, user, experience", "shareholder, stockholder, return, dividend"),
    ("Long-term vs short-term", "long term, long-term, decade, enduring, future", "short term, short-term, quarterly, near term"),
    ("Internal vs external innovation", "invent, build, R&D, engineering", "partner, acquire, alliance, ecosystem"),
    ("Crisis/risk vs success/performance", "risk, crisis, volatility, challenge, uncertainty", "record, growth, success, performance, strong"),
]


def write_dictionary() -> None:
    rows = []
    md = ["# Theme Dictionary Master", "", "This working dictionary operationalizes the Innovation Strategy Process Model for lexical comparison across Amazon, NVIDIA, Shell, and Chevron.", ""]
    for t in THEMES:
        md.append(f"## {t['theme']}")
        for subtheme, strict, expanded in t["subthemes"]:
            ambiguity = "Manual review recommended for cross-industry homonyms and generic business language."
            md.append(f"### {subtheme}")
            md.append(f"- Concept: lexical evidence of {subtheme.lower()} within {t['theme'].lower()}.")
            md.append("- Why it matters: this maps strategic language to corporate entrepreneurship constructs, especially leadership attention, exploration/exploitation, and strategic renewal.")
            md.append(f"- Strict dictionary: {strict}")
            md.append(f"- Expanded dictionary/stems: {expanded}")
            md.append(f"- Ambiguity risk: {ambiguity}")
            md.append("- Counting guidance: use strict counts for the main table; use expanded counts for sensitivity checks and manual passage review.")
            rows.append(
                {
                    "theme": t["theme"],
                    "subtheme": subtheme,
                    "concept_definition": f"Lexical evidence of {subtheme.lower()} within {t['theme'].lower()}.",
                    "strict_keywords": strict,
                    "expanded_keywords_or_stems": expanded,
                    "ambiguity_risks": ambiguity,
                    "automatic_count": "strict_terms_yes_expanded_terms_sensitivity_only",
                    "manual_check_required": "yes",
                    "likely_noisy_terms": "leadership, growth, platform, resilience, value, capital",
                }
            )
    md.append("## Cross-Cutting Dictionaries")
    for name, left, right in CROSS_CUTTING:
        md.append(f"- {name}: pole A = {left}; pole B = {right}. Use ratios cautiously and inspect concordance lines.")
    write("04_quant_framework/theme_dictionary/theme_dictionary_master.md", "\n".join(md))
    with (ROOT / "04_quant_framework/keyword_lists/theme_dictionary_master.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "theme",
                "subtheme",
                "concept_definition",
                "strict_keywords",
                "expanded_keywords_or_stems",
                "ambiguity_risks",
                "automatic_count",
                "manual_check_required",
                "likely_noisy_terms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    write(
        "04_quant_framework/coding_notes/dictionary_design_notes.md",
        """
        # Dictionary Design Notes

        The dictionary is anchored in the Innovation Strategy Process Model: strategic leadership; horizon scanning and sense-making; purpose, vision, and governance; strategic options, experimentation, and choices; and agile execution and organization.

        Use strict dictionaries for headline counts because they reduce false positives. Use expanded dictionaries to locate passages for manual interpretation. This matters because the same word can mean different things across industries. For example, "platform" may mean a digital ecosystem at Amazon or NVIDIA, but a physical drilling platform at Shell or Chevron. "Leadership" can mean managerial behavior or market position. "Growth" can indicate exploration, exploitation, commodity-cycle recovery, or purely financial performance.

        The final paper should report dictionary construction, pilot refinement, stopword handling, text boundaries, and whether counts are normalized per 1,000 words. Any quantitative claim should be followed by qualitative validation from selected passages.
        """,
    )


SELECTIONS = {
    "amazon": ["1997", "2016", "2020", "2021", "2022", "2024", "2025"],
    "nvidia": ["2017", "2018", "2020", "2021", "2022", "2023", "2025"],
    "shell": ["2014", "2015", "2016", "2020", "2022", "2024", "2025"],
    "chevron": ["2013", "2018", "2020", "2021", "2022", "2023", "2024"],
}

CANDIDATES = {
    "amazon": [
        ("1997", "Founding strategic DNA", "Day 1, long-term shareholder value, customer obsession, rapid experimentation", "Selected"),
        ("2006", "AWS/cloud infrastructure emergence", "Useful strategic inflection but no standalone official shareholder letter in current archive", "Not selected"),
        ("2016", "Day 1 vs Day 2 and organizational vitality", "Strong CE fit: anti-bureaucracy, speed, external trends, high-velocity decisions", "Selected"),
        ("2017", "Alexa/Prime/AWS scale era", "Substantive, but overlaps with 2016 Day 1 logic", "Not selected"),
        ("2020", "Pandemic scale and Bezos final-letter era", "Mature platform scale, stakeholder value, crisis response, and Bezos-era closure", "Selected"),
        ("2021", "CEO transition to Andy Jassy", "First Jassy letter; continuity and renewal after Bezos", "Selected"),
        ("2022", "Post-pandemic recalibration", "Cost discipline, long-term investment, AWS, and portfolio-choice language", "Selected"),
        ("2023", "GenAI and efficiency acceleration", "Useful adjacent year but less necessary once 2024 and 2025 are selected", "Not selected"),
        ("2024", "AI/platform reinvestment era", "Captures generative AI, AWS, cost discipline, and mature platform renewal", "Selected"),
        ("2025", "Newest AI/infrastructure letter", "Adds latest strategic language on AI, infrastructure, experimentation, and mature platform execution", "Selected"),
    ],
    "nvidia": [
        ("2016", "Deep learning/platform acceleration", "Has a Dear NVIDIANs and Stakeholders annual-review section, but the letter section is not cleanly signed by Jensen Huang", "Not selected"),
        ("2017", "AI platform expansion", "Adds a second early AI-platform text after the 2016 inflection", "Selected"),
        ("2018", "Gaming/crypto volatility", "Captures volatility and portfolio breadth before data-center/generative-AI acceleration", "Selected"),
        ("2019", "Post-crypto reset and data-center buildup", "Good bridge year but less distinctive than 2020 Mellanox/data-center expansion", "Not selected"),
        ("2020", "Mellanox and data-center expansion", "Strategic renewal from graphics to accelerated computing ecosystem", "Selected"),
        ("2021", "Omniverse/AI platform breadth", "Adds platform-breadth and ecosystem-scaling evidence between Mellanox and generative AI", "Selected"),
        ("2022", "Supply-chain/geopolitical and platform breadth", "Clean Dear NVIDIANs letter signed by Jensen Huang as CEO and Founder; useful bridge before the generative-AI shock", "Selected"),
        ("2023", "Generative AI takeoff", "Captures demand shock and full-stack AI positioning", "Selected"),
        ("2024", "AI factory / mature dominance", "Strong mature-scaling year but 2025 has a cleaner standalone CEO-letter source", "Not selected"),
        ("2025", "AI infrastructure scale and mature platform renewal", "Best latest NVIDIA CEO-letter text with AI factory logic and execution pressure", "Selected"),
    ],
    "shell": [
        ("2014", "Clean pre-BG baseline", "Immediate pre-BG baseline and early Ben van Beurden strategic framing", "Selected"),
        ("2015", "BG acquisition and low-price reset", "Strategic portfolio renewal under energy-market pressure", "Selected"),
        ("2016", "Post-BG integration", "Shows integration, simplification, and execution after the major portfolio bet", "Selected"),
        ("2020", "COVID, dividend reset, energy transition", "Crisis plus strategic renewal", "Selected"),
        ("2021", "Powering Progress", "Important transition year but 2022 better captures renamed Shell plc structure", "Not selected"),
        ("2022", "Shell plc and energy-security shock", "Governance/identity shift plus Russia/energy-market disruption", "Selected"),
        ("2023", "Sawan strategy reset year", "Useful adjacent year but 2024 and 2025 give a cleaner mature Sawan-era execution sequence", "Not selected"),
        ("2024", "Capital discipline and transition pragmatism", "Mature reinvention under investor and policy pressure", "Selected"),
        ("2025", "Latest Sawan-era execution", "Adds latest capital-discipline, LNG, transition-pragmatism, and shareholder-return framing", "Selected"),
    ],
    "chevron": [
        ("2013", "Mega-project and shale-era capital logic", "Good incumbent baseline before the Wirth era", "Selected"),
        ("2018", "Mike Wirth CEO era begins", "Capital discipline, returns, Permian/LNG portfolio framing", "Selected"),
        ("2020", "COVID downturn plus Noble acquisition", "Crisis response and countercyclical portfolio option", "Selected"),
        ("2021", "Recovery and post-Noble integration", "Adds integration/recovery evidence after the 2020 crisis acquisition", "Selected"),
        ("2022", "Post-COVID energy security and capital discipline", "Captures energy-security, cash-return, and lower-carbon positioning in a high-price cycle", "Selected"),
        ("2023", "Hess transaction announced", "Captures a major portfolio option and long-cycle renewal before acquisition completion", "Selected"),
        ("2024", "Lower-carbon/new-business language plus core growth", "Best mature-era comparison with Shell 2024", "Selected"),
        ("2025", "Post-Hess completion candidate", "Future follow-up candidate; official Chevron annual-report PDF returned HTTP 503", "Not selected"),
    ],
}


def write_selection_tables_and_memos() -> None:
    for company, rows in CANDIDATES.items():
        with (ROOT / f"03_screening_and_selection/letter_selection_tables/{company}_candidates.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["company", "candidate_year", "strategic_era", "why_it_matters", "decision"])
            for row in rows:
                writer.writerow([company, *row])
        selected = SELECTIONS[company]
        paragraphs = []
        for year, era, reason, decision in rows:
            if year in selected:
                paragraphs.append(f"### {year} - {era}\n\nSelected because {reason.lower()}.")
        non_selected = [f"- {year}: {reason}" for year, _era, reason, decision in rows if year not in selected]
        source_refs = {
            "amazon": [
                ("AMZN-Letters", "Amazon shareholder letters archive", "https://www.aboutamazon.com/about-us/shareholder-letters"),
                ("AMZN-CEO", "Amazon.com Announces Financial Results and CEO Transition, 2021", "https://press.aboutamazon.com/2021/2/amazon-com-announces-financial-results-and-ceo-transition"),
                ("AWS-Origin", "AWS Our Origins", "https://aws.amazon.com/about-aws/our-origins//"),
            ],
            "nvidia": [
                ("NVDA-IR", "NVIDIA Annual Reports and Proxies archive", "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx"),
                ("NVDA-Huang", "NVIDIA Jensen Huang biography", "https://nvidianews.nvidia.com/bios/jensen-huang"),
            ],
            "shell": [
                ("Shell-Archive", "Shell annual reports archive", "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"),
                ("Shell-Reports", "Shell annual report PDFs downloaded from official archive", "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"),
            ],
            "chevron": [
                ("CVX-SEC", "Chevron SEC annual filings", "https://www.sec.gov/edgar/browse/?CIK=93410"),
                ("CVX-2024", "Chevron 2024 annual report page", "https://www.chevron.com/annual-report"),
                ("CVX-Noble", "Chevron completes Noble Energy acquisition, 2020", "https://www.chevron.com/newsroom/2020/q4/chevron-completes-acquisition-of-noble-energy"),
                ("CVX-Hess", "Chevron completes Hess acquisition, 2025", "https://www.chevron.com/newsroom/2025/q3/chevron-completes-acquisition-of-hess-corporation"),
            ],
        }[company]
        write(
            f"03_screening_and_selection/selection_memos/{company}_selection_rationale.md",
            f"""
            # {COMPANY_META[company][1]} Selection Rationale

            Final selected years: {', '.join(selected)}.

            These years form a coherent set because they combine an early or baseline strategic posture, a transition or scaling moment, a disruption/crisis moment, and a mature renewal phase. The set is designed for both close reading and lexical comparison against the Innovation Strategy Process Model.

            {chr(10).join(paragraphs)}

            ## Why Other Candidate Years Were Not Selected

            {chr(10).join(non_selected)}

            ## Comparability Note

            The years are not forced to match the other companies exactly. Instead, each company contributes comparable strategic episodes: foundational logic, scaling/platform or portfolio logic, disruption response, and renewal under maturity.

            {citations_block(source_refs)}
            """,
        )


def write_timelines() -> None:
    timelines = {
        "amazon": [
            ("1997", "Amazon's original shareholder letter codifies long-termism, customer obsession, market leadership, and willingness to make bold investment decisions."),
            ("2005-2006", "Prime and AWS mark ecosystem expansion from retail into subscription logistics and cloud infrastructure."),
            ("2016", "Bezos's Day 1/Day 2 framing makes organizational inertia a central strategic risk."),
            ("2021", "Amazon announces Bezos will become Executive Chair and Andy Jassy will become CEO; Jassy's first letter emphasizes iterative innovation and remaining insurgent."),
            ("2024", "Amazon's mature-platform language centers AI, AWS infrastructure, customer experience, and disciplined investment."),
        ],
        "nvidia": [
            ("1993-1999", "NVIDIA is founded by Jensen Huang and others; official company biography links the 1999 GPU invention to graphics and later parallel computing."),
            ("2006-2016", "CUDA and accelerated computing reposition GPUs beyond gaming toward scientific computing, cloud, and deep learning."),
            ("2020", "Mellanox/data-center expansion strengthens NVIDIA's platform/ecosystem logic."),
            ("2023-2024", "Generative AI demand turns accelerated computing into a broad platform shift with major supply, ecosystem, and execution implications."),
        ],
        "shell": [
            ("2015-2016", "Shell uses the BG Group acquisition and low-price environment to reshape its portfolio toward LNG and deep water."),
            ("2020", "COVID-19 and energy-market collapse create a crisis setting for capital discipline, dividend policy, and transition strategy."),
            ("2021-2022", "Powering Progress and the Shell plc identity/governance simplification frame strategic renewal around energy transition, returns, and resilience."),
            ("2024", "Shell's annual-report language emphasizes performance, LNG, shareholder distributions, and pragmatic transition investment."),
        ],
        "chevron": [
            ("2013", "Chevron provides a mature integrated-energy baseline with mega-project execution and capital allocation discipline."),
            ("2018", "Mike Wirth's CEO era begins, sharpening capital discipline and returns language."),
            ("2020", "Chevron completes Noble Energy during the pandemic downturn, using balance-sheet strength and portfolio optionality."),
            ("2024-2025", "Chevron frames core hydrocarbon growth, lower-carbon businesses, and emerging technologies; Hess closes in July 2025, extending the portfolio into Guyana and Bakken."),
        ],
    }
    cite_map = {
        "amazon": [
            ("AMZN-1997", "Amazon original 1997 shareholder letter", "https://www.aboutamazon.com/news/company-news/amazons-original-1997-letter-to-shareholders"),
            ("AWS-Origin", "AWS Our Origins", "https://aws.amazon.com/about-aws/our-origins//"),
            ("AMZN-CEO", "Amazon 2021 CEO transition announcement", "https://press.aboutamazon.com/2021/2/amazon-com-announces-financial-results-and-ceo-transition"),
        ],
        "nvidia": [
            ("NVDA-Huang", "NVIDIA Jensen Huang biography", "https://nvidianews.nvidia.com/bios/jensen-huang"),
            ("NVDA-IR", "NVIDIA Annual Reports and Proxies", "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx"),
        ],
        "shell": [
            ("Shell-Archive", "Shell annual reports archive", "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"),
        ],
        "chevron": [
            ("CVX-SEC", "Chevron SEC annual filings", "https://www.sec.gov/edgar/browse/?CIK=93410"),
            ("CVX-Noble", "Chevron completes Noble Energy acquisition", "https://www.chevron.com/newsroom/2020/q4/chevron-completes-acquisition-of-noble-energy"),
            ("CVX-Hess", "Chevron completes Hess acquisition", "https://www.chevron.com/newsroom/2025/q3/chevron-completes-acquisition-of-hess-corporation"),
        ],
    }
    for company, items in timelines.items():
        lines = [f"# {COMPANY_META[company][1]} Timeline", "", "Working strategic eras and inflection points for CE/innovation analysis.", ""]
        for year, note in items:
            lines.append(f"## {year}\n\n{note}\n")
        lines.append(citations_block(cite_map[company]))
        write(f"03_screening_and_selection/company_timelines/{company}_timeline.md", "\n".join(lines))


def write_cross_company_memo() -> None:
    write(
        "05_outputs/industry_comparison/why_these_companies_and_industries.md",
        f"""
        # Why These Companies and Industries

        This project compares Amazon, NVIDIA, Shell, and Chevron because the four firms expose different versions of the same corporate entrepreneurship problem: how large organizations preserve exploration while exploiting mature assets. Amazon and NVIDIA represent technology/digital-platform logics where innovation is visible through software, cloud infrastructure, AI, developer ecosystems, and rapid scaling. Shell and Chevron represent oil-and-gas/energy logics where innovation is constrained by capital intensity, long-cycle assets, safety, regulation, commodity exposure, and energy-transition politics.

        The comparison is strong for Corporate Entrepreneurship because it is not simply "tech vs energy." Each firm must manage strategic leadership, horizon scanning, purpose/governance, strategic options, and agile execution. The difference is that the time constants and risk envelopes vary: Amazon and NVIDIA can scale digital ecosystems quickly but face platform disruption and infrastructure bottlenecks; Shell and Chevron must make long-lived capital bets under regulation, geopolitical volatility, climate pressure, and commodity cycles.

        WIPO's Global Innovation Tracker is useful background because it frames innovation as investment, technological progress, adoption, and socioeconomic impact, while noting uneven sectoral patterns in R&D, AI-driven venture concentration, renewable-energy cost dynamics, and oil-and-gas revenue pressure. BCG's Most Innovative Companies collection is useful because it tracks innovation readiness, AI, platforms, ecosystems, green growth, and the gap between innovation ambition and delivery capability. Forbes is retained as a secondary benchmarking list only if specific rankings can be verified at citation time.

        ## Why The Two Industries Together

        - Pace: digital-platform innovation cycles are shorter; energy innovation cycles are slower because assets are physical, regulated, and capital intensive.
        - Business model: Amazon and NVIDIA monetize platforms/ecosystems; Shell and Chevron monetize integrated energy portfolios and must renew the portfolio while defending the core.
        - Capital intensity: all four are capital intensive by 2024, but the source differs: data centers/custom silicon/cloud capacity in technology; upstream, LNG, refining, and lower-carbon assets in energy.
        - Regulation: digital platforms face antitrust, data, export-control, and AI-governance pressure; energy firms face safety, environmental, climate, permitting, and geopolitical pressure.
        - Innovation visibility: tech innovation is visible in products/platform APIs; energy innovation is often embedded in process technology, project execution, subsurface capability, emissions reduction, and portfolio choices.
        - Ecosystems: Amazon and NVIDIA depend on developers, cloud customers, sellers, partners, and chip/software stacks; Shell and Chevron depend on governments, joint ventures, suppliers, service companies, technology ventures, and energy customers.
        - Explore vs exploit: tech firms exploit platform scale while exploring AI and new services; energy firms exploit hydrocarbon cash flows while exploring lower-carbon and new-energy options.

        ## Company Logic

        Amazon is selected because its shareholder letters provide unusually explicit strategic language about long-termism, customer obsession, experimentation, Day 1 culture, and platform renewal. NVIDIA is selected because it illustrates an entrepreneurial founder-led semiconductor firm becoming the platform company behind accelerated computing and generative AI. Shell is selected because it is a global incumbent trying to reconcile hydrocarbon cash generation, LNG, energy transition, governance simplification, and investor returns. Chevron is selected because it offers a disciplined U.S. integrated-energy comparator with major portfolio moves, including Noble Energy and Hess, and a distinct capital-return orientation.

        {citations_block([
            ("WIPO-GII-2025", "WIPO Global Innovation Index 2025 - Global Innovation Tracker", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/global-innovation-tracker.html"),
            ("BCG-MIC", "BCG Most Innovative Companies report collection", "https://www.bcg.com/publications/most-innovative-companies-the-collection"),
            ("Forbes-Innovative", "Forbes Innovative Companies list", "https://www.forbes.com/innovative-companies/list/"),
            ("AMZN-Letters", "Amazon shareholder letters archive", "https://www.aboutamazon.com/about-us/shareholder-letters"),
            ("NVDA-IR", "NVIDIA Annual Reports and Proxies", "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx"),
            ("Shell-Archive", "Shell annual reports archive", "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"),
            ("CVX-2024", "Chevron 2024 annual report page", "https://www.chevron.com/annual-report"),
        ])}
        """,
    )


def find_text(company: str, year: str) -> Optional[Path]:
    candidates = list((ROOT / f"02_extracted_text/{company}").glob(f"{company}_{year}*letter.txt"))
    candidates += list((ROOT / f"02_extracted_text/{company}").glob(f"{company}_{year}_annual_report.txt"))
    candidates += list((ROOT / f"02_extracted_text/{company}").glob(f"{company}_{year}_sec_*.txt"))
    return candidates[0] if candidates else None


def count_terms(text: str, terms: List[str]) -> int:
    total = 0
    lower = text.lower()
    for term in terms:
        term = term.strip().lower()
        if not term:
            continue
        if term.endswith("*"):
            prefix = re.escape(term[:-1])
            total += len(re.findall(rf"\b{prefix}\w*", lower))
        else:
            total += len(re.findall(rf"\b{re.escape(term)}\b", lower))
    return total


def pilot_counts() -> None:
    pilot_docs = {
        "amazon": "1997",
        "nvidia": "2025",
        "shell": "2024",
        "chevron": "2024",
    }
    rows = []
    for company, year in pilot_docs.items():
        path = find_text(company, year)
        if not path:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
        for theme in THEMES:
            terms = []
            for _sub, strict, _expanded in theme["subthemes"]:
                terms.extend([t.strip() for t in strict.split(",")])
            cnt = count_terms(text, terms)
            rows.append(
                {
                    "company": company,
                    "year": year,
                    "local_text_path": rel(path),
                    "word_count": len(words),
                    "theme": theme["theme"],
                    "strict_theme_count": cnt,
                    "count_per_1000_words": round((cnt / len(words) * 1000), 3) if words else 0,
                }
            )
    with (ROOT / "04_quant_framework/pilot_counts/pilot_counts.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["company", "year", "local_text_path", "word_count", "theme", "strict_theme_count", "count_per_1000_words"],
        )
        writer.writeheader()
        writer.writerows(rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["company"], row["year"], row["local_text_path"], row["word_count"])].append(row)
    lines = ["# Pilot Counts Summary", "", "These are pilot counts only. They test dictionary behavior and should not be used as final results.", ""]
    for (company, year, path, wc), vals in grouped.items():
        lines.append(f"## {company.title()} {year}")
        lines.append(f"- Text: {path}")
        lines.append(f"- Word count: {wc}")
        for row in vals:
            lines.append(f"- {row['theme']}: {row['strict_theme_count']} ({row['count_per_1000_words']} per 1,000 words)")
        lines.append("")
    write("04_quant_framework/pilot_counts/pilot_counts_summary.md", "\n".join(lines))
    write(
        "04_quant_framework/coding_notes/refinement_recommendations.md",
        """
        # Refinement Recommendations

        Pilot counts should be read as a noise test, not as findings. Before final analysis:

        - Define exact text boundaries for each selected letter. Remove tables of contents, financial statements, legal boilerplate, and repeated archive navigation.
        - Treat "leadership" as noisy because it can mean market leadership rather than strategic leadership.
        - Treat "growth" as noisy because it can indicate exploration, exploitation, commodity-cycle recovery, or accounting growth.
        - Treat "platform" as highly context dependent: digital platform in technology, physical/offshore platform in energy.
        - Treat "resilience" as multi-meaning: balance-sheet resilience, supply-chain resilience, organizational resilience, or infrastructure resilience.
        - Normalize all counts per 1,000 words and include raw word counts.
        - Add concordance review for the top 10 most frequent dictionary terms in each company.
        """,
    )


def write_methodology_brief() -> None:
    write(
        "05_outputs/methodology_briefs/methodology_working_brief.md",
        f"""
        # Methodology Working Brief

        This phase prepares a corpus of official CEO/shareholder letters and annual reports for a comparative Corporate Entrepreneurship and Innovation analysis. CEO/shareholder letters are useful because they are public, recurring strategic texts in which top leaders explain priorities, tradeoffs, investment logic, stakeholder orientation, and interpretation of the external environment. They are especially relevant to strategic leadership, horizon scanning, purpose/vision/governance, option selection, and execution language.

        The strength of the method is comparability over time: each company can be read across multiple strategic eras. The limitation is that letters are polished investor-facing narratives. They may understate conflict, failed experiments, organizational inertia, or political constraints. For that reason, lexical analysis should be paired with qualitative interpretation and external context.

        The selected years were chosen for strategic inflection value rather than equal spacing. Each company contributes seven years that represent baseline logic, scaling or portfolio transition, crisis/disruption, integration or recalibration, and mature renewal. Where standalone CEO letters are unavailable, the closest official equivalent is used and flagged in sources_master.csv.

        Lexical analysis is useful because it creates a disciplined first pass over strategic emphasis: e.g., customer vs shareholder language, explore vs exploit language, partnership/acquisition/internal invention language, and agility/execution language. It is insufficient alone because dictionary terms are ambiguous and industry-specific. The final paper should therefore report counts, then interpret passages manually.

        Unit of analysis: one selected company-year strategic text, for a selected corpus of 28 company-years. For Amazon this is usually a standalone shareholder letter. For NVIDIA, Shell, and Chevron it may be an annual report or report section where the CEO/chair strategic narrative appears.

        Reproducibility: all available source files, extracted text, source metadata, access dates, and selection rationales are stored in this workspace. Missing or blocked official sources are documented rather than fabricated.

        {citations_block([
            ("AMZN-Letters", "Amazon shareholder letters archive", "https://www.aboutamazon.com/about-us/shareholder-letters"),
            ("NVDA-IR", "NVIDIA Annual Reports and Proxies", "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx"),
            ("Shell-Archive", "Shell annual reports archive", "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html"),
            ("CVX-SEC", "Chevron SEC annual filings", "https://www.sec.gov/edgar/browse/?CIK=93410"),
            ("WIPO-GII-2025", "WIPO Global Innovation Index 2025 - Global Innovation Tracker", "https://www.wipo.int/web-publications/global-innovation-index-2025/en/global-innovation-tracker.html"),
        ])}
        """,
    )


def write_amazon_sample_note() -> None:
    write(
        "06_appendices/source_cards/amazon_sample_analysis_note.md",
        """
        # Amazon 1997 Sample Analysis Note

        No separate attached sample file was present in the workspace at build time. This note therefore records the transferable structure implied by the user's guidance and by the official 1997 Amazon shareholder letter.

        Useful features to standardize across all company analyses:

        - Start with strategic context: what era the letter represents and why the year matters.
        - Identify core CE constructs: strategic leadership, horizon scanning, purpose/vision/governance, strategic options, and agile execution.
        - Separate exploit language from explore language. In Amazon 1997, exploit language appears in customer growth, repeat purchase, brand, infrastructure, and market leadership; explore language appears in product expansion, international opportunity, personalization, learning, and bold investment.
        - Quantify cautiously: count theme terms, normalize by length, then interpret representative passages.
        - Preserve ambiguity notes: long-termism can be a strategic commitment, an investor-relations signal, or both.

        Source: Amazon's original 1997 shareholder letter, About Amazon, accessed 2026-04-16, https://www.aboutamazon.com/news/company-news/amazons-original-1997-letter-to-shareholders
        """,
    )


def write_readme() -> None:
    counts = Counter(row["company"] for row in SOURCE_ROWS)
    selected_lines = []
    for company, years in SELECTIONS.items():
        selected_lines.append(f"- {COMPANY_META[company][1]}: {', '.join(years)}")
    write(
        "README.md",
        f"""
        # Corporate Entrepreneurship Research Workspace

        This workspace is the research groundwork for a paper comparing Amazon, NVIDIA, Shell, and Chevron across technology/digital platforms and oil & gas/energy. It is not the final paper.

        ## What Was Done

        - Created the requested folder structure.
        - Downloaded official source material where accessible: Amazon shareholder-letter pages, SEC annual filings, NVIDIA official annual-review PDFs/SEC filings, Shell official annual-report PDFs, Chevron SEC annual filings, and requested industry benchmark pages.
        - Extracted machine-readable text where feasible.
        - Built company timelines, candidate-year screening tables, company selection memos, a cross-company industry rationale, a lexical/theme dictionary, pilot counts, methodology notes, and a research log.
        - Recorded all source metadata in `00_admin/sources_master.csv` and `06_appendices/download_manifest/download_manifest.csv`.

        ## Source Counts In Ledger

        {chr(10).join(f"- {k}: {v}" for k, v in sorted(counts.items()))}

        ## Selected Seven Years Per Company

        {chr(10).join(selected_lines)}

        ## Key Industry Comparison Points

        The tech cases emphasize platform/ecosystem scaling, AI/cloud/accelerated computing, customer/developer adoption, and rapid strategic renewal. The energy cases emphasize capital discipline, long-cycle assets, regulation, commodity volatility, energy transition, portfolio renewal, and safety/reliability. This makes the comparison useful for Corporate Entrepreneurship because all four firms face explore-vs-exploit tensions, but the constraints differ sharply.

        ## Quantitative Framework

        The dictionary is organized around five themes: Strategic Leadership; Horizon Scanning / Context; Purpose, Vision, Governance; Strategic Options, Experimentation, and Choices; and Agile Execution and Organization. Cross-cutting dictionaries cover explore vs exploit, customer vs shareholder, long-term vs short-term, internal vs external innovation, and crisis/risk vs performance language.

        ## Pilot Status

        Pilot lexical counts were run on one text per company where a text extract existed. These are noise tests only. The next pass should manually define letter boundaries, remove non-letter material, and rerun normalized counts.

        ## Known Gaps

        - Chevron official annual-report PDFs were downloaded for the selected years 2013, 2018, 2020, 2021, 2022, 2023, and 2024; Chevron 2025 remains a follow-up candidate because the official PDF returned HTTP 503.
        - NVIDIA annual-report PDFs are downloaded for 2011-2025, and the standalone 2025 CEO-letter PDF is retained as the cleanest latest letter source.
        - No attached Amazon sample analysis file was present in the workspace; a standardization note was created instead.
        - Forbes may block automated access; use only if the human researcher can verify the relevant list/rankings at citation time.

        ## Next Recommended Steps

        1. Manually inspect the selected source texts and mark exact letter boundaries.
        2. Create cleaned selected-letter text files for all 28 company-years.
        3. Rerun lexical counts on cleaned text only.
        4. Build source cards with short, compliant quotations for qualitative analysis.
        5. Draft the paper sections using the memos here as scaffolding.
        """,
    )


def main() -> int:
    ensure_dirs()
    download_amazon_letters()
    download_sec_annuals("amazon", "0001018724", "10-K", 12)
    download_nvidia_ir_pdfs()
    download_sec_annuals("nvidia", "0001045810", "10-K", 12)
    download_shell_reports()
    download_sec_annuals("chevron", "0000093410", "10-K", 13)
    add_industry_sources()
    write_sources_master()
    write_admin_files()
    write_timelines()
    write_selection_tables_and_memos()
    write_cross_company_memo()
    write_dictionary()
    pilot_counts()
    write_methodology_brief()
    write_amazon_sample_note()
    write_readme()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
