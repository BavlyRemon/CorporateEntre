#!/usr/bin/env python3
"""Build a polished comparative report in PDF and DOCX with appendices.

The report is generated from the verified 28-letter corpus and quantitative
tables already in the workspace. It avoids internal-document citations in the
PDF body and cites official company letters/reports by company/year/title.
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lexicon import (  # noqa: E402
    IPM_TERMS,
    CROSS_TERMS,
    THEME_SUBTHEMES,
    Matcher,
    tokenize,
    format_entry_for_csv,
)
OUT = ROOT / "05_outputs" / "corporate_entrepreneurship_submission_ready_report.pdf"
DOCX_OUT = ROOT / "05_outputs" / "corporate_entrepreneurship_submission_ready_report.docx"
KEYWORD_APPENDIX = ROOT / "05_outputs" / "tables" / "appendix_keyword_theme_counts.csv"
KEYWORD_YEAR_APPENDIX = ROOT / "05_outputs" / "tables" / "appendix_keyword_counts_by_year.csv"
SUBTHEME_APPENDIX = ROOT / "05_outputs" / "tables" / "appendix_subtheme_counts_by_company.csv"
EXPLORE_EXPLOIT_DICT = ROOT / "04_quant_framework" / "keyword_lists" / "explore_exploit_dictionary.csv"
EXPLORE_EXPLOIT_TABLE = ROOT / "05_outputs" / "tables" / "explore_exploit_ratios.csv"
EXPLORE_EXPLOIT_KEYWORD_YEAR = ROOT / "05_outputs" / "tables" / "explore_exploit_keyword_counts_by_year.csv"
EXPLORE_EXPLOIT_KEYWORD_COMPANY = ROOT / "05_outputs" / "tables" / "explore_exploit_keyword_counts_by_company.csv"
HYPOTHESIS_APPENDIX = ROOT / "05_outputs" / "tables" / "hypothesis_test_summary.csv"
ERA_IPM_APPENDIX = ROOT / "05_outputs" / "tables" / "company_era_ipm_matrix.csv"
SELECTION_RATIONALE_APPENDIX = ROOT / "05_outputs" / "tables" / "selected_letter_rationale.csv"
OUTCOME_ANCHORS_APPENDIX = ROOT / "05_outputs" / "tables" / "outcome_anchors.csv"
YEAR_COUNTS_APPENDIX = ROOT / "05_outputs" / "tables" / "appendix_per_year_counts.csv"


def clean(text: object) -> str:
    s = str(text)
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2192": "->",
        "\u2022": "-",
        "\u00a0": " ",
        "\u00ad": "",
        "\u2011": "-",
    }
    for src, dst in replacements.items():
        s = s.replace(src, dst)
    return s.encode("latin-1", "replace").decode("latin-1")


def read_csv(path: str | Path) -> list[dict[str, str]]:
    path = ROOT / path if isinstance(path, str) else path
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def strip_header(text: str) -> str:
    return text.split("\n---\n", 1)[1] if "\n---\n" in text else text


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def normalize_theme_name(theme: str) -> str:
    return theme.replace("Horizon Scanning / Context", "Horizon Scanning / Sense-making").replace(
        "Purpose, Vision, Governance", "Purpose, Vision, and Governance"
    )


def term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term.strip())
    escaped = escaped.replace(r"\ ", r"[\s\-]+").replace(r"\-", r"[\s\-]+")
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def count_term(text: str, term: str) -> int:
    return len(term_pattern(term).findall(text))


def split_terms(s: str) -> list[str]:
    return [part.strip() for part in s.split(",") if part.strip()]


def esc_pdf(text: str) -> str:
    return clean(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class PDF:
    def __init__(self) -> None:
        self.pages: list[list[tuple[str, int, float, float, str]]] = []
        self.current: list[tuple[str, int, float, float, str]] = []
        self.margin = 50
        self.width = 512
        self.page_no = 0
        self.y = 742
        self.new_page(header=False)

    def new_page(self, header: bool = True) -> None:
        if self.current:
            self.pages.append(self.current)
        self.current = []
        self.page_no += 1
        self.y = 742
        if header and self.page_no > 1:
            self.text("Corporate Entrepreneurship and Innovation Comparative Report", 8, "Helvetica-Oblique")
            self.y -= 8

    def text(self, text: str, size: int = 10, font: str = "Helvetica", indent: int = 0) -> None:
        if self.y < 62:
            self.new_page()
        self.current.append((font, size, self.margin + indent, self.y, clean(text)))
        self.y -= size + 4

    def blank(self, h: int = 8) -> None:
        self.y -= h
        if self.y < 62:
            self.new_page()

    def wrap(self, text: str, size: int = 10, indent: int = 0) -> list[str]:
        max_chars = max(38, int((self.width - indent) / (size * 0.50)))
        words = clean(text).split()
        lines: list[str] = []
        cur = ""
        for word in words:
            test = word if not cur else cur + " " + word
            if len(test) <= max_chars:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, text: str, size: int = 10, indent: int = 0) -> None:
        for line in self.wrap(text, size=size, indent=indent):
            self.text(line, size=size, indent=indent)
        self.blank(4)

    def bullet(self, text: str, size: int = 10) -> None:
        lines = self.wrap(text, size=size, indent=20)
        if not lines:
            return
        self.text("- " + lines[0], size=size, indent=8)
        for line in lines[1:]:
            self.text("  " + line, size=size, indent=8)

    def h1(self, text: str) -> None:
        if self.y < 150:
            self.new_page()
        self.blank(10)
        self.text(text.upper(), 15, "Helvetica-Bold")
        self.blank(5)

    def h2(self, text: str) -> None:
        if self.y < 100:
            self.new_page()
        self.blank(6)
        self.text(text, 12, "Helvetica-Bold")
        self.blank(2)

    def h3(self, text: str) -> None:
        if self.y < 85:
            self.new_page()
        self.blank(4)
        self.text(text, 10, "Helvetica-Bold")

    def table(self, headers: list[str], rows: list[list[object]], widths: list[int], size: int = 7) -> None:
        fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
        separator = "-" * min(sum(widths) + (2 * (len(widths) - 1)), 118)
        self.text(fmt.format(*[clean(h)[:w] for h, w in zip(headers, widths)]), size, "Courier-Bold")
        self.text(separator, size, "Courier")
        for row in rows:
            cells = [clean(c).replace("\n", " ") for c in row]
            parts_by_cell: list[list[str]] = []
            max_parts = 1
            for cell, width in zip(cells, widths):
                parts: list[str] = []
                while len(cell) > width:
                    cut = cell.rfind(" ", 0, width)
                    if cut < 5:
                        cut = width
                    parts.append(cell[:cut].strip())
                    cell = cell[cut:].strip()
                parts.append(cell)
                parts_by_cell.append(parts)
                max_parts = max(max_parts, len(parts))
            for i in range(max_parts):
                if self.y < 72:
                    self.new_page()
                    self.text(fmt.format(*[clean(h)[:w] for h, w in zip(headers, widths)]), size, "Courier-Bold")
                    self.text(fmt.format(*["-" * w for w in widths]), size, "Courier")
                line = [parts[i] if i < len(parts) else "" for parts in parts_by_cell]
                self.text(fmt.format(*[c[:w] for c, w in zip(line, widths)]), size, "Courier")
            if self.y < 72:
                self.new_page()
                self.text(fmt.format(*[clean(h)[:w] for h, w in zip(headers, widths)]), size, "Courier-Bold")
                self.text(separator, size, "Courier")
            self.text(separator, size, "Courier")
            self.blank(2)
        self.blank(6)

    def build(self, path: Path) -> None:
        if self.current:
            self.pages.append(self.current)
            self.current = []
        objects: list[bytes] = []

        def add(data: bytes) -> int:
            objects.append(data)
            return len(objects)

        catalog_id = add(b"<< /Type /Catalog /Pages 2 0 R >>")
        pages_id = add(b"")
        font_ids = {
            "Helvetica": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
            "Helvetica-Bold": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"),
            "Helvetica-Oblique": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>"),
            "Courier": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"),
            "Courier-Bold": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>"),
        }
        font_resource = " ".join(f"/F{i} {obj} 0 R" for i, obj in enumerate(font_ids.values(), 1))
        font_lookup = {name: f"F{i}" for i, name in enumerate(font_ids, 1)}
        page_ids: list[int] = []
        for page_no, lines in enumerate(self.pages, 1):
            stream_lines = [
                f"BT /{font_lookup[font]} {size} Tf {x:.1f} {y:.1f} Td ({esc_pdf(text)}) Tj ET"
                for font, size, x, y, text in lines
            ]
            stream_lines.append(f"BT /F1 8 Tf 50 35 Td (Page {page_no}) Tj ET")
            stream = "\n".join(stream_lines).encode("latin-1", "replace")
            content_id = add(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream")
            page_id = add(
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << {font_resource} >> >> /Contents {content_id} 0 R >>"
                ).encode("latin-1")
            )
            page_ids.append(page_id)
        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, obj in enumerate(objects, 1):
            offsets.append(len(out))
            out.extend(f"{i} 0 obj\n".encode("latin-1"))
            out.extend(obj)
            out.extend(b"\nendobj\n")
        xref = len(out)
        out.extend(f"xref\n0 {len(objects)+1}\n".encode("latin-1"))
        out.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            out.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
        out.extend(
            (
                f"trailer\n<< /Size {len(objects)+1} /Root {catalog_id} 0 R >>\n"
                f"startxref\n{xref}\n%%EOF\n"
            ).encode("latin-1")
        )
        path.write_bytes(out)


class DOCX:
    def __init__(self) -> None:
        self.blocks: list[tuple] = []

    def text(self, text: str, size: int = 10, font: str = "Helvetica", indent: int = 0) -> None:
        self.blocks.append(("text", clean(text), size, font, indent))

    def blank(self, h: int = 8) -> None:
        self.blocks.append(("blank",))

    def para(self, text: str, size: int = 10, indent: int = 0) -> None:
        self.blocks.append(("para", clean(text), size, indent))

    def bullet(self, text: str, size: int = 10) -> None:
        self.blocks.append(("bullet", clean(text), size))

    def h1(self, text: str) -> None:
        self.blocks.append(("h1", clean(text)))

    def h2(self, text: str) -> None:
        self.blocks.append(("h2", clean(text)))

    def h3(self, text: str) -> None:
        self.blocks.append(("h3", clean(text)))

    def table(self, headers: list[str], rows: list[list[object]], widths: list[int], size: int = 7) -> None:
        self.blocks.append(("table", [clean(h) for h in headers], [[clean(c) for c in row] for row in rows]))

    def _paragraph_xml(self, text: str, bold: bool = False, italic: bool = False, size: int = 20) -> str:
        text = xml_escape(text)
        props = []
        if bold:
            props.append("<w:b/>")
        if italic:
            props.append("<w:i/>")
        if size:
            props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
        rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
        return (
            '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>'
            f'<w:r>{rpr}<w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
        )

    def _table_xml(self, headers: list[str], rows: list[list[str]]) -> str:
        def cell(text: str, bold: bool = False) -> str:
            text = xml_escape(text)
            rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
            return (
                "<w:tc><w:tcPr><w:tcW w:w=\"2200\" w:type=\"dxa\"/></w:tcPr>"
                f"<w:p><w:pPr><w:spacing w:after=\"80\"/></w:pPr><w:r>{rpr}<w:t xml:space=\"preserve\">{text}</w:t></w:r></w:p></w:tc>"
            )

        tbl = [
            "<w:tbl><w:tblPr><w:tblBorders>"
            "<w:top w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "<w:left w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "<w:bottom w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "<w:right w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "<w:insideH w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "<w:insideV w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"auto\"/>"
            "</w:tblBorders></w:tblPr>"
        ]
        tbl.append("<w:tr>" + "".join(cell(h, True) for h in headers) + "</w:tr>")
        for row in rows:
            tbl.append("<w:tr>" + "".join(cell(c) for c in row) + "</w:tr>")
        tbl.append("</w:tbl>")
        return "".join(tbl)

    def build(self, path: Path) -> None:
        body_parts: list[str] = []
        for block in self.blocks:
            kind = block[0]
            if kind == "blank":
                body_parts.append("<w:p/>")
            elif kind == "text":
                _, text, size, font, _indent = block
                body_parts.append(self._paragraph_xml(text, "Bold" in font, "Oblique" in font, size * 2))
            elif kind == "para":
                _, text, size, _indent = block
                body_parts.append(self._paragraph_xml(text, False, False, size * 2))
            elif kind == "bullet":
                _, text, size = block
                body_parts.append(self._paragraph_xml("- " + text, False, False, size * 2))
            elif kind == "h1":
                body_parts.append(self._paragraph_xml(block[1], True, False, 30))
            elif kind == "h2":
                body_parts.append(self._paragraph_xml(block[1], True, False, 26))
            elif kind == "h3":
                body_parts.append(self._paragraph_xml(block[1], True, False, 22))
            elif kind == "table":
                _, headers, rows = block
                body_parts.append(self._table_xml(headers, rows))
                body_parts.append("<w:p/>")
        body_parts.append(
            "<w:sectPr><w:pgSz w:w=\"12240\" w:h=\"15840\"/><w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\"/></w:sectPr>"
        )
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
            'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
            'xmlns:o="urn:schemas-microsoft-com:office:office" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
            'xmlns:v="urn:schemas-microsoft-com:vml" '
            'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
            'xmlns:w10="urn:schemas-microsoft-com:office:word" '
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
            'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
            'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
            'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
            'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14">'
            "<w:body>"
            + "".join(body_parts)
            + "</w:body></w:document>"
        )
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""
        core = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Corporate Entrepreneurship Comparative Report</dc:title>
  <dc:creator>OpenAI Codex</dc:creator>
</cp:coreProperties>"""
        app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>"""
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", rels)
            zf.writestr("word/document.xml", document_xml)
            zf.writestr("docProps/core.xml", core)
            zf.writestr("docProps/app.xml", app)


def load_letters() -> dict[tuple[str, int], str]:
    rows = read_csv("02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv")
    out: dict[tuple[str, int], str] = {}
    for r in rows:
        path = ROOT / r["extracted_letter_path"]
        out[(r["company"], int(r["year"]))] = strip_header(path.read_text(encoding="utf-8"))
    return out


def _count_entry(entry, text: str, tokens: list[str], stems: list[str]) -> int:
    return Matcher("_one", [entry]).count(text, tokens, stems)


def build_appendix_counts() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    letters = load_letters()
    # Pre-tokenise each letter once; entries are matched against the cached tokens/stems.
    letter_tokens: dict[tuple[str, int], tuple[list[str], list[str]]] = {
        key: tokenize(text) for key, text in letters.items()
    }
    keyword_rows: list[dict[str, str]] = []
    keyword_year_rows: list[dict[str, str]] = []
    subtheme_acc: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    companies = ["Amazon", "Nvidia", "Shell", "Chevron"]

    def add_entry(theme: str, subtheme: str, entry) -> None:
        label = format_entry_for_csv(entry)
        per_letter: dict[tuple[str, int], int] = {}
        counts = {c: 0 for c in companies}
        total = 0
        for (company, year), text in letters.items():
            toks, stems = letter_tokens[(company, year)]
            n = _count_entry(entry, text, toks, stems)
            per_letter[(company, year)] = n
            counts[company] += n
            total += n
        if total == 0:
            return
        for c in companies:
            subtheme_acc[(theme, subtheme)][c] += counts[c]
        subtheme_acc[(theme, subtheme)]["Total"] += total
        for (company, year), text in sorted(letters.items()):
            keyword_year_rows.append({
                "company": company, "year": str(year),
                "theme": theme, "subtheme": subtheme,
                "keyword": label, "count": str(per_letter[(company, year)]),
            })
        keyword_rows.append({
            "theme": theme, "subtheme": subtheme, "keyword": label,
            "Amazon": str(counts["Amazon"]), "Nvidia": str(counts["Nvidia"]),
            "Shell": str(counts["Shell"]), "Chevron": str(counts["Chevron"]),
            "Total": str(total),
        })
        return counts, total

    for row in THEME_SUBTHEMES:
        for entry in row["terms"]:
            add_entry(row["theme"], row["subtheme"], entry)

    explicit_year_rows: list[dict[str, str]] = []
    explicit_company_rows: list[dict[str, str]] = []
    for subtheme_name, key in [("Explore", "explore"), ("Exploit", "exploit")]:
        theme = "Explore vs Exploit"
        subtheme = subtheme_name
        for entry in CROSS_TERMS[key]:
            label = format_entry_for_csv(entry)
            per_letter: dict[tuple[str, int], int] = {}
            counts = {c: 0 for c in companies}
            total = 0
            for (company, year), text in letters.items():
                toks, stems = letter_tokens[(company, year)]
                n = _count_entry(entry, text, toks, stems)
                per_letter[(company, year)] = n
                counts[company] += n
                total += n
            if total == 0:
                continue
            for c in companies:
                subtheme_acc[(theme, subtheme)][c] += counts[c]
            subtheme_acc[(theme, subtheme)]["Total"] += total
            for (company, year), text in sorted(letters.items()):
                year_row = {
                    "company": company, "year": str(year),
                    "theme": theme, "subtheme": subtheme,
                    "keyword": label, "count": str(per_letter[(company, year)]),
                }
                keyword_year_rows.append(year_row)
                explicit_year_rows.append(year_row)
            keyword_rows.append({
                "theme": theme, "subtheme": subtheme, "keyword": label,
                "Amazon": str(counts["Amazon"]), "Nvidia": str(counts["Nvidia"]),
                "Shell": str(counts["Shell"]), "Chevron": str(counts["Chevron"]),
                "Total": str(total),
            })
            explicit_company_rows.append({
                "theme": theme, "subtheme": subtheme, "keyword": label,
                "Amazon": str(counts["Amazon"]), "Nvidia": str(counts["Nvidia"]),
                "Shell": str(counts["Shell"]), "Chevron": str(counts["Chevron"]),
                "Total": str(total),
            })
    subtheme_rows: list[dict[str, str]] = []
    for (theme, subtheme), counts in sorted(subtheme_acc.items()):
        subtheme_rows.append(
            {
                "theme": theme,
                "subtheme": subtheme,
                "Amazon": str(counts["Amazon"]),
                "Nvidia": str(counts["Nvidia"]),
                "Shell": str(counts["Shell"]),
                "Chevron": str(counts["Chevron"]),
                "Total": str(counts["Total"]),
            }
        )
    for path, rows, fields in [
        (KEYWORD_APPENDIX, keyword_rows, ["theme", "subtheme", "keyword", "Amazon", "Nvidia", "Shell", "Chevron", "Total"]),
        (KEYWORD_YEAR_APPENDIX, keyword_year_rows, ["company", "year", "theme", "subtheme", "keyword", "count"]),
        (SUBTHEME_APPENDIX, subtheme_rows, ["theme", "subtheme", "Amazon", "Nvidia", "Shell", "Chevron", "Total"]),
    ]:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    write_csv(
        EXPLORE_EXPLOIT_KEYWORD_YEAR,
        explicit_year_rows,
        ["company", "year", "theme", "subtheme", "keyword", "count"],
    )
    write_csv(
        EXPLORE_EXPLOIT_KEYWORD_COMPANY,
        explicit_company_rows,
        ["theme", "subtheme", "keyword", "Amazon", "Nvidia", "Shell", "Chevron", "Total"],
    )
    return keyword_rows, subtheme_rows, keyword_year_rows


EXPLORE_MATCHER = Matcher("explore", CROSS_TERMS["explore"])
EXPLOIT_MATCHER = Matcher("exploit", CROSS_TERMS["exploit"])
IPM_MATCHERS_SR = {name: Matcher(name, terms) for name, terms in IPM_TERMS.items()}


def classify_explore(explore_share: float) -> str:
    if explore_share >= 0.6:
        return "exploratory leaning"
    if explore_share <= 0.4:
        return "exploitative leaning"
    return "ambidextrous/mixed"


def refresh_explore_exploit_outputs() -> None:
    manifest = read_csv("02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv")
    quant_letter = read_csv("05_outputs/tables/quant_summary_by_letter.csv")
    quant_company = read_csv("05_outputs/tables/quant_summary_by_company.csv")

    text_by_key: dict[tuple[str, int], str] = {}
    for row in manifest:
        key = (row["company"], int(row["year"]))
        text = strip_header((ROOT / row["extracted_letter_path"]).read_text(encoding="utf-8"))
        text_by_key[key] = text

    letter_by_key = {(row["company"], int(row["year"])): row for row in quant_letter}
    ratio_rows: list[dict[str, str]] = []
    for key, row in letter_by_key.items():
        text = text_by_key[key]
        words = word_count(text)
        toks, stems = tokenize(text)
        explore_count = EXPLORE_MATCHER.count(text, toks, stems)
        exploit_count = EXPLOIT_MATCHER.count(text, toks, stems)
        share = explore_count / (explore_count + exploit_count) if explore_count + exploit_count else 0.0
        row["word_count"] = str(words)
        row["explore_count"] = str(explore_count)
        row["exploit_count"] = str(exploit_count)
        row["explore_share_of_explore_exploit"] = f"{share:.3f}"
        row["explore_exploit_class"] = classify_explore(share)
        ratio_rows.append(
            {
                "company": row["company"],
                "year": row["year"],
                "word_count": row["word_count"],
                "explore_count": row["explore_count"],
                "exploit_count": row["exploit_count"],
                "explore_per_1000": f"{(1000 * explore_count / words) if words else 0:.3f}",
                "exploit_per_1000": f"{(1000 * exploit_count / words) if words else 0:.3f}",
                "explore_share_of_pair": f"{share:.3f}",
                "interpretive_class": row["explore_exploit_class"],
                "source_file": row["source_file"],
            }
        )

    quant_letter_fields = list(quant_letter[0].keys())
    write_csv(
        ROOT / "05_outputs" / "tables" / "quant_summary_by_letter.csv",
        sorted(quant_letter, key=lambda r: (r["company"], int(r["year"]))),
        quant_letter_fields,
    )

    company_acc: dict[str, dict[str, int]] = defaultdict(lambda: {"words": 0, "explore": 0, "exploit": 0})
    for row in quant_letter:
        company_acc[row["company"]]["words"] += int(row["word_count"])
        company_acc[row["company"]]["explore"] += int(row["explore_count"])
        company_acc[row["company"]]["exploit"] += int(row["exploit_count"])

    for row in quant_company:
        company = row["company"]
        row["total_word_count"] = str(company_acc[company]["words"])
        row["explore_count"] = str(company_acc[company]["explore"])
        row["exploit_count"] = str(company_acc[company]["exploit"])
        share = company_acc[company]["explore"] / (company_acc[company]["explore"] + company_acc[company]["exploit"]) if company_acc[company]["explore"] + company_acc[company]["exploit"] else 0.0
        row["explore_share_of_explore_exploit"] = f"{share:.3f}"

    quant_company_fields = list(quant_company[0].keys())
    write_csv(ROOT / "05_outputs" / "tables" / "quant_summary_by_company.csv", quant_company, quant_company_fields)
    write_csv(
        EXPLORE_EXPLOIT_TABLE,
        sorted(ratio_rows, key=lambda r: (r["company"], int(r["year"]))),
        ["company", "year", "word_count", "explore_count", "exploit_count", "explore_per_1000", "exploit_per_1000", "explore_share_of_pair", "interpretive_class", "source_file"],
    )


def year_breakdown_rows(quant_letter: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = {(r["company"], int(r["year"])): r for r in quant_letter}
    manifest = read_csv("02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv")
    rows: list[dict[str, str]] = []
    for entry in sorted(manifest, key=lambda r: (r["company"], int(r["year"]))):
        company = entry["company"]
        year = int(entry["year"])
        text = strip_header((ROOT / entry["extracted_letter_path"]).read_text(encoding="utf-8"))
        words = word_count(text)
        toks, stems = tokenize(text)
        theme_counts = {
            theme: IPM_MATCHERS_SR[theme].count(text, toks, stems)
            for theme in IPM_TERMS
        }
        prior = existing[(company, year)]
        rows.append(
            {
                "company": company,
                "year": str(year),
                "words": str(words),
                "lead_per_1000": f"{(1000 * theme_counts['Strategic Leadership'] / words) if words else 0:.3f}",
                "horizon_per_1000": f"{(1000 * theme_counts['Horizon Scanning / Sense-making'] / words) if words else 0:.3f}",
                "purpose_per_1000": f"{(1000 * theme_counts['Purpose, Vision, and Governance'] / words) if words else 0:.3f}",
                "options_per_1000": f"{(1000 * theme_counts['Strategic Options, Experimentation, and Choices'] / words) if words else 0:.3f}",
                "execution_per_1000": f"{(1000 * theme_counts['Agile Execution and Organization'] / words) if words else 0:.3f}",
                "explore_count": prior["explore_count"],
                "exploit_count": prior["exploit_count"],
                "customer_count": prior["customer_count"],
                "shareholder_count": prior["shareholder_count"],
                "explore_share": prior["explore_share_of_explore_exploit"],
                "customer_share": prior["customer_share_of_customer_shareholder"],
            }
        )
    return rows


def q(rows: list[dict[str, str]], company: str, year: int) -> dict[str, str]:
    return next(r for r in rows if r["company"] == company and int(r["year"]) == year)


def era(rows: list[dict[str, str]], company: str, years: list[int]) -> dict[str, float]:
    selected = [r for r in rows if r["company"] == company and int(r["year"]) in years]
    words = sum(int(r["word_count"]) for r in selected)
    fields = [
        "Strategic Leadership_count",
        "Horizon Scanning / Sense-making_count",
        "Purpose, Vision, and Governance_count",
        "Strategic Options, Experimentation, and Choices_count",
        "Agile Execution and Organization_count",
        "explore_count",
        "exploit_count",
        "customer_count",
        "shareholder_count",
    ]
    out = {"words": float(words)}
    for f in fields:
        out[f] = float(sum(int(r[f]) for r in selected))
    for f in fields[:5]:
        out[f.replace("_count", "_per_1000")] = 1000 * out[f] / words if words else 0
    out["explore_share"] = out["explore_count"] / (out["explore_count"] + out["exploit_count"]) if out["explore_count"] + out["exploit_count"] else 0
    out["customer_share"] = out["customer_count"] / (out["customer_count"] + out["shareholder_count"]) if out["customer_count"] + out["shareholder_count"] else 0
    return out


def selected_reference_rows() -> list[dict[str, str]]:
    selected = read_csv("02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv")
    sources = read_csv("00_admin/sources_master.csv")
    refs: list[dict[str, str]] = []
    for s in selected:
        company = s["company"].lower()
        year = s["year"]
        candidates = [r for r in sources if r["company"].lower() == company and r["year"] == year]
        if company == "amazon":
            candidates = [r for r in candidates if "shareholder" in r["document_title"].lower()] or candidates
        elif company == "nvidia" and year == "2025":
            candidates = [r for r in candidates if "ceo letter" in r["document_title"].lower()] or candidates
        elif company == "nvidia":
            candidates = [r for r in candidates if r["document_type"] == "annual_report_pdf"] or candidates
        elif company in {"shell", "chevron"}:
            candidates = [r for r in candidates if r["document_type"] == "annual_report_pdf"] or candidates
        r = candidates[0]
        refs.append(
            {
                "company": s["company"],
                "year": year,
                "title": r["document_title"],
                "source": r["official_source"],
                "url": r["url"],
                "access_date": r["access_date"],
            }
        )
    return refs


def add_report(pdf: PDF) -> None:
    refresh_explore_exploit_outputs()
    quant_company = read_csv("05_outputs/tables/quant_summary_by_company.csv")
    quant_letter = read_csv("05_outputs/tables/quant_summary_by_letter.csv")
    ipm = read_csv("05_outputs/tables/ipm_comparison_matrix.csv")
    keyword_rows, subtheme_rows, keyword_year_rows = build_appendix_counts()
    refs = selected_reference_rows()
    yearly_rows = year_breakdown_rows(quant_letter)
    company_quant = {row["company"]: row for row in quant_company}
    write_csv(
        YEAR_COUNTS_APPENDIX,
        yearly_rows,
        [
            "company",
            "year",
            "words",
            "lead_per_1000",
            "horizon_per_1000",
            "purpose_per_1000",
            "options_per_1000",
            "execution_per_1000",
            "explore_count",
            "exploit_count",
            "customer_count",
            "shareholder_count",
            "explore_share",
            "customer_share",
        ],
    )
    hypothesis_rows = [
        {
            "hypothesis": "H1: Technology firms show stronger horizon/exploration language.",
            "evidence": f"Nvidia Horizon Scanning 24.873 per 1,000; Amazon explore share {company_quant['Amazon']['explore_share_of_explore_exploit']}; Shell {company_quant['Shell']['explore_share_of_explore_exploit']}; Chevron {company_quant['Chevron']['explore_share_of_explore_exploit']}.",
            "result": "Supported, with nuance: Amazon is more customer-purpose-led than pure horizon-led.",
        },
        {
            "hypothesis": "H2: Energy firms frame innovation through exploitation, discipline, and renewal constraints.",
            "evidence": f"Shell 2025 uses performance/discipline/simplification; Chevron 2013 centers Operational Excellence; Shell and Chevron remain the lower company-level explore shares at {company_quant['Shell']['explore_share_of_explore_exploit']} and {company_quant['Chevron']['explore_share_of_explore_exploit']}.",
            "result": "Supported, but not as no-innovation: both firms show bounded exploration through portfolio and lower-carbon options.",
        },
        {
            "hypothesis": "H3: Customer/shareholder orientation differs by industry and firm.",
            "evidence": "Amazon customer share 0.933; Nvidia 0.828; Shell 0.379; Chevron 0.300.",
            "result": "Supported: technology letters are more customer/ecosystem oriented; energy letters balance customers with shareholders, returns, and social legitimacy.",
        },
        {
            "hypothesis": "H4: Strategy evolves across leadership eras or strategic phases.",
            "evidence": "Amazon 2021 Options 8.229; Nvidia 2025 Horizon 37.419; Shell 2020 Purpose 17.637; Chevron 2021 Options and Purpose both 8.252.",
            "result": "Supported: each company changes emphasis over time while preserving a durable strategic identity.",
        },
    ]
    write_csv(HYPOTHESIS_APPENDIX, hypothesis_rows, ["hypothesis", "evidence", "result"])

    era_ipm_rows = [
        {
            "company": "Amazon",
            "era": "1997 Bezos founder doctrine",
            "explore_exploit_diagnosis": "Near-balanced lexical mix, exploratory strategic posture.",
            "dominant_ipm": "Purpose, Vision, and Governance",
            "evidence": "Purpose/Vision/Governance 17.640 per 1,000; customer 25 vs shareholder 4; 'focus relentlessly on our customers'.",
            "interpretation": "Customer purpose legitimates bold long-term investment and early platform exploration.",
        },
        {
            "company": "Amazon",
            "era": "2016 Bezos anti-Day-2 discipline",
            "explore_exploit_diagnosis": "Exploratory leaning in strict lexical pair.",
            "dominant_ipm": "Purpose plus Agile Execution",
            "evidence": "Customer share 1.000; 'experiment patiently, accept failures, plant seeds'.",
            "interpretation": "Day 1 becomes an anti-bureaucracy system for entrepreneurial behavior at scale.",
        },
        {
            "company": "Amazon",
            "era": "2021-2025 Jassy reinvention",
            "explore_exploit_diagnosis": "Ambidextrous: platform exploitation funds AI, robotics, AWS, chips, and satellite exploration.",
            "dominant_ipm": "Options and Agile Execution",
            "evidence": "2021 Options 8.229; 2025 Horizon 7.096 and Execution 6.137; 'AI is not a standalone initiative-it's a multiplier'.",
            "interpretation": "The mature firm uses speed, infrastructure, and selective investment to keep Day 1 operating inside a large organization.",
        },
        {
            "company": "Nvidia",
            "era": "2017-2018 GPU platform emergence",
            "explore_exploit_diagnosis": "Exploratory technology-wave recognition.",
            "dominant_ipm": "Horizon Scanning / Sense-making",
            "evidence": "2017 Horizon 19.334; 'GPU computing has arrived'.",
            "interpretation": "Leadership identifies GPU computing as the next general-purpose architecture.",
        },
        {
            "company": "Nvidia",
            "era": "2020-2023 AI expansion",
            "explore_exploit_diagnosis": "Ambidextrous ecosystem expansion.",
            "dominant_ipm": "Horizon Scanning with Options",
            "evidence": "Horizon above 20 per 1,000 in 2020, 2021, 2022, and 2023; 'Graphics. Accelerated Computing. AI'.",
            "interpretation": "The company converts horizon sensing into software, data-center, edge, and autonomous-system options.",
        },
        {
            "company": "Nvidia",
            "era": "2025 AI infrastructure",
            "explore_exploit_diagnosis": "Exploitative lexical shift inside an exploratory AI frontier.",
            "dominant_ipm": "Horizon Scanning plus Execution",
            "evidence": f"2025 Horizon 37.419; exploit count {q(quant_letter, 'Nvidia', 2025)['exploit_count']}; 'AI infrastructure platform'.",
            "interpretation": "AI becomes a scaled infrastructure business, so execution and monetization become as visible as frontier language.",
        },
        {
            "company": "Shell",
            "era": "2014-2016 van Beurden portfolio discipline",
            "explore_exploit_diagnosis": "Exploitative discipline with acquisition-led renewal.",
            "dominant_ipm": "Strategic Options / Choices",
            "evidence": "2016 Options 9.494; exploit 11 vs explore 1; 'Strict capital discipline' and BG as growth accelerator.",
            "interpretation": "Shell uses portfolio restructuring, LNG, deep water, and capital allocation as entrepreneurship mechanisms.",
        },
        {
            "company": "Shell",
            "era": "2020 Powering Progress reset",
            "explore_exploit_diagnosis": "Ambidextrous transition legitimacy.",
            "dominant_ipm": "Purpose, Vision, and Governance",
            "evidence": "2020 Purpose 17.637; customer 10 vs shareholder 9; 'generating shareholder value, achieving net-zero emissions'.",
            "interpretation": "The firm attempts to reconcile shareholders, customers, society, and net-zero commitments.",
        },
        {
            "company": "Shell",
            "era": "2022-2025 Sawan performance transition",
            "explore_exploit_diagnosis": "Selective exploration under stricter exploitation discipline.",
            "dominant_ipm": "Agile Execution / Governance",
            "evidence": "2025 Execution 3.529; customer share 0.778; 'performance, discipline and simplification'.",
            "interpretation": "Lower-carbon options remain, but the letter narrows them to attractive business models and advantaged assets.",
        },
        {
            "company": "Chevron",
            "era": "2013 Watson operational baseline",
            "explore_exploit_diagnosis": "Strongly exploitative.",
            "dominant_ipm": "Agile Execution / Operational discipline",
            "evidence": f"Explore {q(quant_letter, 'Chevron', 2013)['explore_count']} vs exploit {q(quant_letter, 'Chevron', 2013)['exploit_count']} in 583 words; 'Operational Excellence'.",
            "interpretation": "Innovation is framed primarily as safety, reliability, and execution discipline.",
        },
        {
            "company": "Chevron",
            "era": "2018 Wirth disciplined renewal",
            "explore_exploit_diagnosis": "Exploitative core with visible option creation.",
            "dominant_ipm": "Agile Execution plus Options",
            "evidence": "2018 Agile Execution 6.223; 'Future Energy Fund' and 'energy enables human progress'.",
            "interpretation": "Chevron adds venture-style and digital options without dislodging operating culture.",
        },
        {
            "company": "Chevron",
            "era": "2020-2024 returns/lower-carbon",
            "explore_exploit_diagnosis": "Disciplined adjacency-based ambidexterity.",
            "dominant_ipm": "Purpose plus Options",
            "evidence": "2021 Purpose and Options both 8.252; 'higher returns, lower carbon'; 2024 'strategy remains consistent'.",
            "interpretation": "The company adds lower-carbon and technology adjacencies while preserving continuity and shareholder-return discipline.",
        },
    ]
    write_csv(ERA_IPM_APPENDIX, era_ipm_rows, ["company", "era", "explore_exploit_diagnosis", "dominant_ipm", "evidence", "interpretation"])

    selection_rows = [
        {"company": "Amazon", "year": "1997", "strategic_phase": "Founder doctrine / IPO-era scaling", "inclusion_rationale": "Earliest canonical shareholder letter; establishes Day 1, customer obsession, long-term investment, and market-leadership logic."},
        {"company": "Amazon", "year": "2016", "strategic_phase": "Mature Bezos / anti-Day-2 doctrine", "inclusion_rationale": "Best compact statement of how Amazon tries to preserve entrepreneurial behavior inside a large organization."},
        {"company": "Amazon", "year": "2020", "strategic_phase": "Pandemic scale and stakeholder value", "inclusion_rationale": "Shows mature-platform outcomes: Prime, AWS, Marketplace, Alexa, employees, sellers, and shareholder value."},
        {"company": "Amazon", "year": "2021", "strategic_phase": "Jassy CEO transition", "inclusion_rationale": "Captures leadership transition and explicit speed/experimentation mechanisms under Andy Jassy."},
        {"company": "Amazon", "year": "2022", "strategic_phase": "Post-pandemic discipline and portfolio adjustment", "inclusion_rationale": "Adds evidence of adjustment after rapid expansion; useful for exploit/explore tension."},
        {"company": "Amazon", "year": "2024", "strategic_phase": "AI and organizational speed", "inclusion_rationale": "Shows Jassy-era emphasis on AI, delivery speed, and execution discipline."},
        {"company": "Amazon", "year": "2025", "strategic_phase": "AI/platform reinvention", "inclusion_rationale": "Most explicit selected Amazon letter on AI as a multiplier and on capex-intensive reinvention."},
        {"company": "Nvidia", "year": "2017", "strategic_phase": "GPU computing inflection", "inclusion_rationale": "Captures the emergence of GPU computing and early AI/data-center strategic framing."},
        {"company": "Nvidia", "year": "2018", "strategic_phase": "Platform expansion", "inclusion_rationale": "Shows continuation from GPU leadership into gaming, data center, professional visualization, and autonomous/robotics options."},
        {"company": "Nvidia", "year": "2020", "strategic_phase": "AI platform broadening", "inclusion_rationale": "Contains explicit Graphics / Accelerated Computing / AI architecture and full-stack platform language."},
        {"company": "Nvidia", "year": "2021", "strategic_phase": "Data-center ecosystem and Arm ambition", "inclusion_rationale": "Captures data-center-as-computer logic, ecosystem expansion, and major strategic-option ambition."},
        {"company": "Nvidia", "year": "2022", "strategic_phase": "Omniverse, robotics, automotive and developer scale", "inclusion_rationale": "Selected after CEO-letter audit; provides stronger signed CEO/stakeholder text than earlier alternatives."},
        {"company": "Nvidia", "year": "2023", "strategic_phase": "Generative AI acceleration", "inclusion_rationale": "Captures ChatGPT/generative-AI sense-making and market-expansion narrative."},
        {"company": "Nvidia", "year": "2025", "strategic_phase": "AI infrastructure company", "inclusion_rationale": "Most explicit selected Nvidia letter on full-stack AI infrastructure and scaled execution outcomes."},
        {"company": "Shell", "year": "2014", "strategic_phase": "van Beurden early discipline", "inclusion_rationale": "Establishes the post-transition CEO frame around portfolio focus, efficiency, and integrated-energy discipline."},
        {"company": "Shell", "year": "2015", "strategic_phase": "BG acquisition decision", "inclusion_rationale": "Captures the strategic rationale for BG and the oil-price downturn context."},
        {"company": "Shell", "year": "2016", "strategic_phase": "BG integration and portfolio reshaping", "inclusion_rationale": "Shows acquisition integration, LNG/deep-water growth, divestments, and capital discipline in one letter."},
        {"company": "Shell", "year": "2020", "strategic_phase": "Powering Progress / net-zero reset", "inclusion_rationale": "Captures the strongest purpose/governance reset around net-zero, customers, shareholders, and pandemic context."},
        {"company": "Shell", "year": "2022", "strategic_phase": "Transition leadership handoff", "inclusion_rationale": "Bridges van Beurden to Sawan and captures energy-security/transition tension after geopolitical shock."},
        {"company": "Shell", "year": "2024", "strategic_phase": "Sawan performance discipline", "inclusion_rationale": "Shows the move from broad transition language toward performance, discipline, simplification, and selective capital allocation."},
        {"company": "Shell", "year": "2025", "strategic_phase": "Integrated energy with tighter targets", "inclusion_rationale": "Provides concrete outcome anchors for cost reductions, LNG sales, emissions targets, and shareholder distributions."},
        {"company": "Chevron", "year": "2013", "strategic_phase": "Watson operational baseline", "inclusion_rationale": "Provides the earliest selected Chevron operational-excellence baseline for comparison with later lower-carbon language."},
        {"company": "Chevron", "year": "2018", "strategic_phase": "Wirth early renewal", "inclusion_rationale": "Captures Future Energy Fund, digital/technology language, and operational-culture continuity under Wirth."},
        {"company": "Chevron", "year": "2020", "strategic_phase": "Pandemic, Noble acquisition, capital discipline", "inclusion_rationale": "Shows resilience, acquisition-led strengthening, and lower-carbon options under severe market stress."},
        {"company": "Chevron", "year": "2021", "strategic_phase": "Higher returns, lower carbon", "inclusion_rationale": "Best concise statement of Chevron's main strategic formula and New Energies agenda."},
        {"company": "Chevron", "year": "2022", "strategic_phase": "Energy security and lower-carbon investment", "inclusion_rationale": "Adds geopolitical/energy-demand pressure and lower-carbon capital-investment commitment."},
        {"company": "Chevron", "year": "2023", "strategic_phase": "Returns, Permian, renewable fuels, CCS", "inclusion_rationale": "Shows scaling of core production and lower-carbon adjacencies after the 2021 strategy frame."},
        {"company": "Chevron", "year": "2024", "strategic_phase": "Record production and continuity", "inclusion_rationale": "Captures recent continuity: record production, stockholder returns, Hess/PDC portfolio moves, AI-related demand and lower-carbon projects."},
    ]
    write_csv(SELECTION_RATIONALE_APPENDIX, selection_rows, ["company", "year", "strategic_phase", "inclusion_rationale"])

    outcome_anchor_rows = [
        {"company": "Amazon", "year": "1997/2020", "outcome_anchor": "Amazon reports more than 1.5 million customer accounts in 1997 and, by 2020, more than 200 million Prime members plus AWS at a $50 billion annualized run rate.", "interpretation": "Customer-led exploration became multiple scaled platforms, not only rhetoric."},
        {"company": "Amazon", "year": "2025", "outcome_anchor": "Revenue grew from $638 billion to $717 billion; AWS grew from $108 billion to $129 billion; free cash flow fell as AI capex rose.", "interpretation": "The AI multiplier claim is tied to measurable reinvestment and platform growth."},
        {"company": "Nvidia", "year": "2017", "outcome_anchor": "Revenue reached $6.9 billion; gaming reached $4.1 billion; data-center annual revenue reached $830 million.", "interpretation": "The GPU-computing narrative had already produced both core-market and emerging AI/data-center growth."},
        {"company": "Nvidia", "year": "2025", "outcome_anchor": "Revenue more than doubled to $130.5 billion; data-center revenue reached $115.2 billion; Blackwell produced $11 billion in Q4 revenue.", "interpretation": "Horizon scanning is linked to execution at infrastructure scale."},
        {"company": "Shell", "year": "2016", "outcome_anchor": "Production rose to 3.7 million boe/d from 3.0 million in 2015, largely driven by BG; capital investment excluding BG was around $27 billion, about $20 billion below the combined 2014 level.", "interpretation": "Portfolio renewal combined growth with capital discipline rather than simple expansion."},
        {"company": "Shell", "year": "2025", "outcome_anchor": "Shell reports $5.1 billion in structural cost reductions, LNG sales up 11%, around 70% progress toward halving Scope 1 and 2 operational emissions, and routine flaring eliminated.", "interpretation": "The energy-transition narrative has measurable operating and emissions anchors, though safety remains a major unresolved tension."},
        {"company": "Chevron", "year": "2021", "outcome_anchor": "Chevron reports best-ever free cash flow, Noble integration completion, dividend increase, and reinstated share repurchases while launching lower-carbon priorities.", "interpretation": "Lower-carbon renewal is explicitly tied to exploitation of financial and operational strength."},
        {"company": "Chevron", "year": "2024", "outcome_anchor": "Chevron reports record $27.0 billion returned to stockholders, 3.3 million net boe/d production, and Permian production of 921,000 net boe/d.", "interpretation": "The continuity frame is outcome-backed: lower-carbon adjacency sits beside record core execution."},
    ]
    write_csv(OUTCOME_ANCHORS_APPENDIX, outcome_anchor_rows, ["company", "year", "outcome_anchor", "interpretation"])

    pdf.text("Corporate Entrepreneurship and Innovation", 17, "Helvetica-Bold")
    pdf.text("CEO/Shareholder Letter Analysis of Amazon, Nvidia, Shell, and Chevron", 15, "Helvetica-Bold")
    pdf.blank(10)

    pdf.h1("1. Introduction")
    pdf.para("This report compares the innovation narratives of Amazon and Nvidia in technology/digital platforms with Shell and Chevron in oil and gas / energy. The evidence base is a 28-letter corpus: seven selected CEO/shareholder leadership communications per company. The selected texts cover 60,742 counted words: Amazon 27,870; Nvidia 15,720; Shell 8,675; and Chevron 8,477.")
    pdf.para("The central comparison is industry vs industry first, then company vs company within each industry. The paper asks whether technology-platform firms and energy incumbents narrate corporate entrepreneurship through different balances of exploration, exploitation, leadership, strategic options, and execution.")
    pdf.h2("Letter Corpus")
    pdf.para("This section defines the corpus and explains why the selected years are analytically comparable without forcing the same calendar years across industries.")
    pdf.table(
        ["Company", "Years", "Strategic coverage"],
        [
            ["Amazon", "1997, 2016, 2020, 2021, 2022, 2024, 2025", "Bezos Day 1 doctrine; pandemic; Jassy-era AI/platform reinvention"],
            ["Nvidia", "2017, 2018, 2020, 2021, 2022, 2023, 2025", "GPU platform; AI/data-center scale; full-stack AI infrastructure"],
            ["Shell", "2014, 2015, 2016, 2020, 2022, 2024, 2025", "BG/LNG; Powering Progress; Sawan performance discipline"],
            ["Chevron", "2013, 2018, 2020, 2021, 2022, 2023, 2024", "Operational excellence; Wirth transition; higher returns/lower carbon"],
        ],
        [10, 31, 48],
    )
    pdf.h2("Selection Logic")
    pdf.para("The corpus uses purposive longitudinal sampling rather than a fixed-interval rule. A fixed interval would look systematic, but it would miss leadership transitions, strategy resets, acquisition/integration moments, crisis periods, and cases where the CEO letter is thin or unavailable. The selection rule was therefore: include years where an official CEO/shareholder leadership text is available and where the letter captures a distinct strategic phase. Adjacent years were excluded when they mainly repeated a phase already represented by a stronger letter.")
    pdf.bullet("Amazon: the years trace Bezos's Day 1 doctrine, mature scale, the pandemic/stakeholder moment, and Jassy-era AI/platform reinvention.")
    pdf.bullet("Nvidia: the years trace GPU-computing emergence, AI/data-center expansion, generative-AI acceleration, and full-stack AI infrastructure.")
    pdf.bullet("Shell: the years trace van Beurden's BG/LNG portfolio renewal, the Powering Progress/net-zero reset, and Sawan's performance-discipline phase.")
    pdf.bullet("Chevron: the years trace Watson's operational-excellence baseline, Wirth's early renewal, and the later higher-returns/lower-carbon continuity strategy.")
    pdf.para("The complete one-line rationale for all 28 selected letters is moved to Appendix D.")

    pdf.h1("2. Hypothesis & Rationale")
    pdf.para("This section states the argument to be tested. It does not preview the results; the evidence appears in the quantitative and qualitative sections.")
    pdf.h2("Main Hypothesis")
    pdf.para("Technology-platform firms will show more explicit exploration, horizon scanning, and strategic-option language than oil-and-gas firms, while oil-and-gas firms will frame innovation through exploitation, capital discipline, operational reliability, safety, and transition legitimacy. The hypothesis is not that technology firms innovate and energy firms do not. Rather, the letters should show two forms of corporate entrepreneurship: platform/category creation in technology and disciplined incumbent renewal in energy.")
    pdf.h2("Sub-Hypotheses")
    pdf.bullet("H1, industry difference: technology letters will emphasize horizon scanning, exploration, platforms, and emerging technology more visibly than energy letters.")
    pdf.bullet("H2, energy constraint: energy letters will frame innovation through exploitation, reliability, capital discipline, safety, transition legitimacy, and controlled strategic options.")
    pdf.bullet("H3, stakeholder orientation: Amazon and Nvidia will show stronger customer/ecosystem orientation, while Shell and Chevron will more explicitly balance customers, shareholders, society, and policy constraints.")
    pdf.bullet("H4, era evolution: each company will show continuity in strategic identity but meaningful shifts across leadership eras, crises, or strategic inflection points.")
    pdf.h2("Rationale")
    pdf.para("The comparison is rigorous because both industries face disruption and long-term capital commitments, but the letters show different innovation processes. Amazon's 1997 letter states, \"focus relentlessly on our customers\" (Amazon, 1997). Nvidia's 2017 letter declares, \"GPU computing has arrived\" (Nvidia, 2017). Shell's 2020 review links Powering Progress with \"generating shareholder value, achieving net-zero emissions\" (Shell, 2020). Chevron's 2021 letter compresses its strategic frame into \"higher returns, lower carbon\" (Chevron, 2021). These short source phrases show that each company uses different language to make innovation legitimate.")
    pdf.h1("3. Methodology")
    pdf.para("This section explains how the letters are treated as strategic texts and how the lexical analysis is made auditable.")
    pdf.para("The unit of analysis is the CEO/shareholder leadership letter or official CEO-review equivalent, not the full annual report. Amazon uses standalone shareholder letters; Nvidia uses annual-review CEO/stakeholder letters, with 2025 from a standalone CEO-letter PDF; Shell uses official annual-report Chief Executive Officer review sections; Chevron uses official annual-report To our stockholders letters signed by the Chairman and CEO.")
    pdf.para("Quantitative analysis uses a strict lexical dictionary mapped to the Innovation Process Model and cross-cutting pairs. Counts are normalized per 1,000 words to avoid overstating longer letters. Qualitative analysis interprets the counted patterns against short source evidence and company-era shifts. This mixed design prevents the analysis from becoming either a word-count dump or an unsupported narrative.")
    pdf.h2("Dictionary Construction And Reliability Safeguards")
    pdf.para("The dictionary was built deductively from the Innovation Process Model, then refined into subthemes that match the course lens: leadership, horizon scanning, purpose/governance, experimentation/options, and execution/organization. Cross-cutting dictionaries were then added for explore/exploit, customer/shareholder, long-term/short-term, entrepreneurial/managerial, internal/external innovation, and risk/performance language.")
    pdf.para("Strict counts use exact keywords and phrases from the strict dictionary only; expanded or close-call terms are not used as primary evidence. Terms are unweighted: one strict hit counts as one hit, whether the word appears in Amazon, Nvidia, Shell, or Chevron. Multi-word terms are counted as phrases, and counts are normalized per 1,000 words to reduce length bias. This makes the quantitative analysis transparent, but conservative.")
    pdf.para("Ambiguity is handled through triangulation rather than hidden adjustment. No keyword is silently recoded after the fact. Instead, noisy terms are flagged in interpretation and major claims must be supported by a count plus a quote or outcome anchor. This matters for words such as platform, growth, leadership, and resilience, which can mean different things across technology and energy contexts.")
    pdf.h2("Framework Definitions And Coding Logic")
    pdf.para("Exploration is coded as language about invention, experimentation, discovery, emerging technologies, new platforms, future markets, uncertainty, and strategic options. Exploitation is coded as language about operational excellence, efficiency, returns, productivity, scale, reliability, safety, asset performance, and optimization of existing capabilities. Ambidexterity is present when a letter shows the firm using existing platforms, assets, capabilities, or cash generation to pursue new options.")
    pdf.para("The report distinguishes lexical explore/exploit from strategic explore/exploit. Lexical evidence counts strict keyword hits. Strategic interpretation asks what the words mean in context. This distinction matters most for Shell and Chevron: a low explore count does not mean no renewal; it often means that renewal is expressed through portfolio, lower-carbon, partnership, or capital-allocation language rather than explicit experimentation language.")
    pdf.para("The Innovation Process Model is operationalized as a sequence rather than a checklist. Strategic Leadership identifies the leadership posture; Horizon Scanning / Sense-making identifies how the firm interprets external change; Purpose, Vision, and Governance identifies how strategy is legitimated; Strategic Options, Experimentation, and Choices identifies the portfolio of possible moves; Agile Execution and Organization identifies how the firm turns choices into organizational action.")
    pdf.h2("Innovation Process Model")
    pdf.bullet("Strategic Leadership: leadership posture, ownership, discipline, stewardship, boldness, and accountability.")
    pdf.bullet("Horizon Scanning / Sense-making: disruption, uncertainty, technology transition, long-term orientation, regulation, energy transition, geopolitics, and macro context.")
    pdf.bullet("Purpose, Vision, and Governance: customer, shareholder, mission, market leadership, responsibility, ethics, climate, and governance.")
    pdf.bullet("Strategic Options, Experimentation, and Choices: invention, R&D, partnerships, acquisitions, pilots, portfolios, allocation, divestment, and scaling choices.")
    pdf.bullet("Agile Execution and Organization: speed, adaptability, operational excellence, reliability, productivity, talent, infrastructure, capacity, and implementation.")
    pdf.h2("Analytical Limits And Mitigations")
    limits = [
        ("Strategic rhetoric", "CEO letters may frame actions favorably and omit failures.", "Claims are treated as leadership framing and checked against letter-level outcome anchors when available."),
        ("Construct validity", "Lexical exploration may undercount energy renewal because energy firms use portfolio or transition language.", "The report separates lexical explore/exploit from strategic explore/exploit and interprets counts within industry context."),
        ("Selection bias", "A purposive sample may appear curated to fit the argument.", "The selection rationale states why every year was included; the rule prioritizes official letter availability and strategic phase coverage."),
        ("Outcome evidence", "Letters are not independent proof that innovations succeeded.", "Outcome anchors are used cautiously as company-reported evidence, not as external performance validation."),
    ]
    for title, risk, mitigation in limits:
        pdf.h3(title)
        pdf.para(f"Risk: {risk}", size=9)
        pdf.para(f"Mitigation: {mitigation}", size=9)

    pdf.h1("4. Quantitative Analysis")
    pdf.para("This section establishes the main quantitative contrasts across firms. Interpretation is intentionally reserved for the qualitative section.")
    pdf.h2("Company-Level Innovation Process Model Counts")
    pdf.table(
        ["Company", "Words", "Lead", "Horizon", "Purpose", "Options", "Exec", "Dominant"],
        [
            [r["company"], r["total_word_count"], r["Strategic Leadership_per_1000"], r["Horizon Scanning / Sense-making_per_1000"], r["Purpose, Vision, and Governance_per_1000"], r["Strategic Options, Experimentation, and Choices_per_1000"], r["Agile Execution and Organization_per_1000"], r["dominant_ipm_theme_per_1000"]]
            for r in quant_company
        ],
        [9, 7, 6, 7, 7, 7, 6, 26],
    )
    pdf.para("This table reports normalized Innovation Process Model frequencies by company. The main descriptive pattern is that Nvidia is highest on Horizon Scanning, Amazon is highest on Purpose/Vision/Governance, and Shell and Chevron also peak on Purpose/Vision/Governance.")
    pdf.h2("Cross-Cutting Ratios")
    pdf.table(
        ["Company", "Explore", "Customer", "LongTerm", "Internal", "Risk"],
        [
            [r["company"], r["explore_share_of_explore_exploit"], r["customer_share_of_customer_shareholder"], r["long_term_share_of_long_short"], r["internal_share_of_internal_external"], r["risk_share_of_risk_performance"]]
            for r in quant_company
        ],
        [9, 8, 9, 9, 8, 7],
    )
    pdf.para("This table reports the main paired ratios used later in interpretation: explore/exploit, customer/shareholder, long-term/short-term, internal/external innovation, and risk/performance language.")
    pdf.h2("Era-Level Quantitative Patterns")
    era_specs = [
        ("Amazon", "Bezos founder doctrine", [1997], "1997: Day 1 and customer/long-term doctrine"),
        ("Amazon", "Bezos mature scale / pandemic", [2016, 2020], "2016/2020: scale, resilience, pandemic and stakeholder framing"),
        ("Amazon", "Jassy reinvention", [2021, 2022, 2024, 2025], "2021-2025: iterative invention, AI, chips, robotics, organizational speed"),
        ("Nvidia", "GPU platform emergence", [2017, 2018], "2017-2018: GPU computing and platform evolution"),
        ("Nvidia", "AI expansion", [2020, 2021, 2022, 2023], "2020-2023: AI, data center, edge, autonomous systems"),
        ("Nvidia", "AI infrastructure", [2025], "2025: full-stack AI infrastructure company"),
        ("Shell", "van Beurden portfolio discipline", [2014, 2015, 2016], "2014-2016: oil-price pressure, BG, capital discipline"),
        ("Shell", "Powering Progress reset", [2020], "2020: pandemic, net-zero, Powering Progress"),
        ("Shell", "Sawan performance transition", [2022, 2024, 2025], "2022/2024/2025: more value with less emissions, discipline, simplification"),
        ("Chevron", "Watson operational excellence", [2013], "2013: safety and operational excellence"),
        ("Chevron", "Wirth transition", [2018], "2018: culture, digital, Future Energy Fund"),
        ("Chevron", "Higher returns / lower carbon", [2020, 2021, 2022, 2023, 2024], "2020-2024: lower carbon, shareholder returns, portfolio and energy security"),
    ]
    era_rows = []
    for company, label, years, note in era_specs:
        e = era(quant_letter, company, years)
        era_rows.append([company, label, f"{e['words']:.0f}", f"{e['Horizon Scanning / Sense-making_per_1000']:.2f}", f"{e['Purpose, Vision, and Governance_per_1000']:.2f}", f"{e['Strategic Options, Experimentation, and Choices_per_1000']:.2f}", f"{e['explore_share']:.2f}"])
    pdf.table(["Company", "Era", "Words", "Horizon", "Purpose", "Options", "Explore"], era_rows, [8, 28, 6, 7, 7, 7, 7])
    pdf.para("These tables are the quantitative base for the interpretation that follows. Appendix E preserves the outcome-anchor audit trail that connects selected claims to company-reported outcomes inside the letters.")

    pdf.h1("5. Qualitative Analysis")
    pdf.para("This section interprets how the quantitative contrasts change across eras, companies, and industries.")
    pdf.h2("A. Company Evolution Across Eras and CEOs")
    pdf.para("This section adds the layer that pure counts cannot provide: how each company changes across leadership eras and strategic phases. Each claim is tied to a count and a short phrase from the relevant letter.")
    pdf.h3("Amazon: Bezos Day 1 Doctrine to Jassy AI Reinvention")
    pdf.table(
        ["Era", "Quant evidence", "Quote evidence", "Interpretation"],
        [
            ["1997 Bezos founder doctrine", "Purpose/Vision/Governance 17.640 per 1,000; customer 25 vs shareholder 4.", "\"Day 1 for the Internet\"; \"focus relentlessly on our customers\" (Amazon, 1997).", "The early letter defines innovation as customer value creation and long-term market leadership, not short-term financial optimization."],
            ["2016 Bezos anti-Day-2 discipline", "Customer share remains 1.000; explore share 1.000 in the strict pair.", "\"experiment patiently, accept failures, plant seeds\" (Amazon, 2016).", "The mature Bezos letter turns founding DNA into an organizational system for avoiding bureaucracy and preserving entrepreneurial behavior at scale."],
            [f"2021 Jassy transition", f"Strategic Options 8.229 per 1,000; explore count {q(quant_letter, 'Amazon', 2021)['explore_count']}; customer count 59.", "\"Speed is not pre-ordained. It's a leadership choice\" (Amazon, 2021).", "Jassy reframes Day 1 as managerial design: speed, two-way-door decisions, tools, and many concurrent invention paths."],
            ["2025 Jassy AI/platform phase", "Horizon 7.096 and Execution 6.137 per 1,000; customer count 58.", "\"AI is not a standalone initiative-it's a multiplier\" (Amazon, 2025).", "Amazon's later letters connect exploration to execution through AWS, chips, robotics, satellites, and AI embedded into existing customer systems."],
        ],
        [20, 25, 27, 31],
        size=6,
    )
    pdf.para("Amazon therefore evolves from founder-led long-termism to a more distributed ambidextrous operating model. The continuity is customer obsession; the change is that Jassy's letters describe more explicit mechanisms of reinvention: speed, experimentation, AI, infrastructure, and selective investment.")
    pdf.para("A year-by-year Innovation Process Model reading sharpens that pattern:")
    pdf.bullet("1997: Purpose/Vision/Governance is dominant at 17.640 per 1,000, while Horizon is also high at 5.474. Bezos fuses strategic leadership and purpose by making customer obsession the rationale for long-term market leadership.", size=8)
    pdf.bullet(f"2016: Purpose remains high at 10.388, but Agile Execution rises to 3.280 and explore share reaches {q(quant_letter, 'Amazon', 2016)['explore_share_of_explore_exploit']}. Day 1 becomes an organizational method for keeping experimentation alive inside a large firm.", size=8)
    pdf.bullet("2020: Purpose falls to 7.241 and Options to 1.207, while the letter shifts to stakeholder scale: Prime, AWS, third-party sellers, employees, and shareowners. The IPM emphasis is less on new options than on what earlier options have become.", size=8)
    pdf.bullet("2021: Options jump to 8.229 and customer count reaches 59. Under Jassy, the strategic-options dimension moves to the foreground as speed, tools, and multi-path invention become the leadership mechanism.", size=8)
    pdf.bullet("2022: Purpose stays high at 12.759 while Horizon and Execution both reach 3.999. The letter shows a firm rebalancing after overexpansion: customer purpose remains intact, but sense-making and organizational execution become more explicit.", size=8)
    pdf.bullet("2024: Purpose rises to 13.730 and Execution peaks at 6.382. This is Amazon's most execution-heavy selected letter, suggesting that AI and logistics are being translated into operational systems rather than discussed as abstract opportunities.", size=8)
    pdf.bullet("2025: Horizon reaches 7.096, the highest Amazon value in the sample, while Execution stays high at 6.137. The IPM sequence becomes clear: customer purpose still legitimates the firm, but AI-driven horizon scanning and execution now dominate how reinvention is narrated.", size=8)

    pdf.h3("Nvidia: GPU Platform to AI Infrastructure")
    pdf.table(
        ["Era", "Quant evidence", "Quote evidence", "Interpretation"],
        [
            ["2017-2018 GPU platform emergence", "2017 Horizon 19.334 per 1,000; 2018 Horizon 12.382.", "\"GPU computing has arrived\" (Nvidia, 2017).", "Nvidia frames innovation first as recognition of a technological inflection: GPUs become a general-purpose computing architecture."],
            ["2020-2023 AI expansion", "2020, 2021, 2022, and 2023 each exceed 20 Horizon terms per 1,000 except 2018.", "\"Graphics. Accelerated Computing. AI\" (Nvidia, 2020).", "The strategic story expands from hardware to platforms, data centers, autonomous systems, edge computing, and AI software ecosystems."],
            [f"2025 AI infrastructure phase", f"2025 Horizon 37.419; Options 5.419; Execution 5.161 per 1,000; exploit count {q(quant_letter, 'Nvidia', 2025)['exploit_count']}.", "\"AI infrastructure platform\" (Nvidia, 2025).", "The 2025 letter is both exploratory and exploitative: it describes the frontier of AI while emphasizing platform deployment, ecosystem scale, and production discipline."],
        ],
        [23, 26, 26, 31],
        size=6,
    )
    pdf.para("Nvidia's evolution is less a CEO transition than an architecture transition under Jensen Huang. The repeated high Horizon scores show that Nvidia's leadership narrative is built around sensing and naming computing waves, then converting them into a full-stack platform business.")
    pdf.para("A year-by-year Innovation Process Model reading shows unusual consistency around Horizon Scanning:")
    pdf.bullet("2017: Horizon dominates at 19.334 per 1,000, far above all other IPM dimensions. The letter frames GPU computing as an inflection and links that sense-making directly to gaming, AI, and data-center growth.", size=8)
    pdf.bullet("2018: Horizon falls to 12.382 but remains dominant, while Purpose and Options both rise to 2.913. The narrative broadens from breakthrough architecture to a platform with multiple growth arenas.", size=8)
    pdf.bullet("2020: Horizon returns to 20.755 and Execution rises to 6.125. The letter reads as a bridge from technology recognition to system-level execution across graphics, accelerated computing, and AI.", size=8)
    pdf.bullet("2021: Horizon increases again to 22.593. The data-center-as-computer idea shows the IPM moving from scanning to architecture and then to ecosystem orchestration.", size=8)
    pdf.bullet("2022: Horizon remains above 22 and Execution rises to 5.122. Omniverse, robotics, automotive, and the developer ecosystem expand the options dimension without displacing the horizon-led identity.", size=8)
    pdf.bullet("2023: Horizon reaches 23.310 and Purpose rises to 5.128. Generative AI gives Nvidia a more public platform mission, not just a product roadmap.", size=8)
    pdf.bullet(f"2025: Horizon surges to 37.419 while Options and Execution both exceed 5.0 and exploit count rises to {q(quant_letter, 'Nvidia', 2025)['exploit_count']}. This is Nvidia's clearest example of ambidexterity: frontier scanning remains dominant, but large-scale infrastructure execution and monetization become inseparable from it.", size=8)

    pdf.h3("Shell: van Beurden Portfolio Renewal to Sawan Discipline")
    pdf.table(
        ["Era", "Quant evidence", "Quote evidence", "Interpretation"],
        [
            ["2014-2016 van Beurden discipline and BG", "2016 Strategic Options 9.494 per 1,000; exploit 11 vs explore 1.", "\"Strict capital discipline\"; \"BG has proven to be an important growth accelerator\" (Shell, 2016).", "Shell treats acquisition, divestment, LNG, deep water, and capital allocation as the main corporate entrepreneurship tools."],
            ["2020 Powering Progress reset", "2020 Purpose/Vision/Governance 17.637 per 1,000; customer 10 vs shareholder 9.", "\"generating shareholder value, achieving net-zero emissions\" (Shell, 2020).", "The strategic frame widens: innovation must satisfy customers, society, emissions goals, and investors at the same time."],
            ["2022-2025 Sawan performance transition", "2025 Execution 3.529 per 1,000; customer share 0.778 in the customer/shareholder pair.", "\"performance, discipline and simplification\"; \"more value with less emissions\" (Shell, 2025).", "Sawan's letters narrow the transition agenda toward investable options, LNG/upstream strength, simplification, and business-model realism."],
        ],
        [23, 27, 29, 31],
        size=6,
    )
    pdf.para("Shell's evolution is therefore not a straight movement from old energy to new energy. It is a sequence of portfolio restructuring, transition commitment, and tighter selectivity. The letters show ambidexterity under capital-market pressure: Shell explores lower-carbon options while explicitly preserving cash-generating energy assets.")
    pdf.para("A year-by-year Innovation Process Model reading makes Shell's internal tension clearer:")
    pdf.bullet("2014: Horizon and Purpose are both 5.547 per 1,000, indicating a company diagnosing industry conditions while reaffirming integrated-energy legitimacy. This is an early discipline phase rather than a transition breakthrough phase.", size=8)
    pdf.bullet("2015: Horizon, Purpose, and Options all sit at 3.717. The BG deal is a strategic-options move under external pressure, not a free-form exploration story.", size=8)
    pdf.bullet("2016: Options jump to 9.494, the strongest Shell options score in the sample, while Leadership reaches 3.165. BG integration, divestments, LNG, deep water, and debt reduction make this the most portfolio-entrepreneurial Shell letter.", size=8)
    pdf.bullet("2020: Purpose peaks at 17.637 and Leadership rises to 3.527. Powering Progress turns the IPM toward governance reconciliation: customers, shareholders, society, and net-zero all have to be held together in one strategy.", size=8)
    pdf.bullet("2022: Purpose remains high at 8.966, with Leadership and Execution both at 3.448. The transition is still present, but the letter increasingly stresses resilience, energy security, and execution under geopolitical shock.", size=8)
    pdf.bullet("2024: Purpose drops to 3.639 and Options to 2.183 while leadership language remains visible. This is the clearest sign that Sawan is narrowing the agenda from broad transition rhetoric toward performance discipline and simplification.", size=8)
    pdf.bullet("2025: Purpose recovers to 5.294 and Execution rises to 3.529, while customer/shareholder balance shifts toward customers at 0.778. The integrated-energy company framing now ties LNG growth, cost reduction, and emissions milestones to a more selective transition logic.", size=8)

    pdf.h3("Chevron: Operational Excellence to Higher Returns, Lower Carbon")
    pdf.table(
        ["Era", "Quant evidence", "Quote evidence", "Interpretation"],
        [
            [f"2013 Watson operational baseline", f"Explore {q(quant_letter, 'Chevron', 2013)['explore_count']} vs exploit {q(quant_letter, 'Chevron', 2013)['exploit_count']} in 583 words; Purpose 3.431 per 1,000.", "\"Operational Excellence\" (Chevron, 2013).", "The starting innovation frame is reliability, safety, and execution discipline rather than experimentation."],
            ["2018 Wirth disciplined renewal", "Agile Execution 6.223 per 1,000; explore 3 vs exploit 14.", "\"Future Energy Fund\"; \"energy enables human progress\" (Chevron, 2018).", "Chevron introduces more visible innovation mechanisms while anchoring them in operational culture and energy-demand purpose."],
            ["2020-2024 returns/lower-carbon era", "2021 Purpose and Options both 8.252 per 1,000; 2024 Purpose 8.850.", "\"higher returns, lower carbon\" (Chevron, 2021); \"strategy remains consistent\" (Chevron, 2024).", "Chevron evolves by adding lower-carbon businesses, partnerships, CCUS, hydrogen, renewable fuels, and AI-related power demand without changing the core continuity narrative."],
        ],
        [23, 27, 28, 32],
        size=6,
    )
    pdf.para("Chevron is the most stable narrative in the corpus. The company evolves, but it evolves by adjacency: it keeps the exploitative operating model visible while adding lower-carbon and technology options around the core business.")
    pdf.para("A year-by-year Innovation Process Model reading shows how Chevron changes without abandoning continuity:")
    pdf.bullet(f"2013: Horizon and Purpose are both 3.431 per 1,000, but explore count is {q(quant_letter, 'Chevron', 2013)['explore_count']} and exploit count is {q(quant_letter, 'Chevron', 2013)['exploit_count']}. The IPM is anchored in execution discipline and operational legitimacy rather than explicit experimentation.", size=8)
    pdf.bullet("2018: Agile Execution jumps to 6.223, the strongest Chevron execution score in the sample. Even when Future Energy Fund appears, the letter still presents innovation through culture, safety, and operating performance.", size=8)
    pdf.bullet("2020: Purpose rises to 10.802, Horizon to 6.173, and Options to 5.401. Under pandemic stress and acquisition activity, Chevron's language broadens beyond continuity into resilience, portfolio strengthening, and lower-carbon positioning.", size=8)
    pdf.bullet("2021: Purpose and Options both reach 8.252 while Leadership rises to 3.001. This is the clearest Chevron formulation of a strategic bridge between shareholder returns and lower-carbon renewal.", size=8)
    pdf.bullet("2022: Purpose remains high at 8.118 and Options at 6.642. The letter links energy security, lower-carbon investment, and disciplined capital allocation more explicitly than earlier Chevron letters.", size=8)
    pdf.bullet("2023: Purpose climbs to 11.321 while Options remain at 4.717. The lower-carbon story is now more visible, but it still operates in the shadow of stockholder returns, Permian scale, and capital efficiency.", size=8)
    pdf.bullet("2024: Purpose is 8.850 and Horizon 4.023, with record production and strong returns in the same letter. Chevron's IPM sequence remains continuity-first: execution and financial strength authorize the firm's adjacent moves into lower-carbon and technology-linked growth.", size=8)

    pdf.h2("B. Explore vs Exploit by Company")
    pdf.para("This subsection makes the explore-vs-exploit diagnosis explicit at the company level. The lexical ratios are useful, but the interpretation rests on the letters' strategic meaning rather than on raw word counts alone.")
    pdf.h3("Amazon")
    pdf.para(f"Amazon is best described as ambidextrous with a slight exploratory tilt that is legitimized through customer purpose. At the company level, its explore share is {company_quant['Amazon']['explore_share_of_explore_exploit']}, but the more important point is how exploration is narrated. In 1997 Bezos frames exploration as long-term market creation - \"Day 1 for the Internet\" and relentless customer focus - and under the refreshed strict pair the letter is close to balanced rather than clearly exploitative. By 2021 and 2025, the exploration logic becomes more explicit through speed, experimentation, AI, chips, robotics, Kuiper, and portfolio reinvestment. Amazon therefore exploits scale, logistics, AWS, and installed customer relationships in order to keep exploring new categories.")
    pdf.h3("Nvidia")
    pdf.para(f"Nvidia is also ambidextrous, but with a different center of gravity: it explores by naming technological inflections early and then exploits the resulting architecture at scale. Its company-level explore share is {company_quant['Nvidia']['explore_share_of_explore_exploit']}, lower than Amazon's, and that still understates how exploratory the letters are in strategic substance because much of Nvidia's language is coded through Horizon Scanning rather than through the narrower explore dictionary. Huang's recurring logic is to identify the next computing wave - GPUs, accelerated computing, generative AI, AI factories - and then turn that wave into a deployed ecosystem and infrastructure business. By 2025, exploitation becomes more visible because frontier AI has become a scaled operating system for customers rather than only a frontier bet.")
    pdf.h3("Shell")
    pdf.para(f"Shell is the clearest case where lexical exploration and strategic exploration diverge. Its explore share is {company_quant['Shell']['explore_share_of_explore_exploit']}, which remains low even after recalculation. But the letters show real corporate entrepreneurship in the form of portfolio reconfiguration, BG integration, LNG expansion, divestments, lower-carbon options, and the attempt to reconcile shareholder value with net-zero commitments. Shell's letters are therefore exploitative in vocabulary but selectively exploratory in strategy. The exploitative language is not noise: it reflects the firm's need to make renewal legitimate through capital discipline, safety, reliability, and cash generation.")
    pdf.h3("Chevron")
    pdf.para(f"Chevron is still more exploitative than exploratory in narrative style, but not a static company. Its company-level explore share is {company_quant['Chevron']['explore_share_of_explore_exploit']}, above Shell's but still below a balanced midpoint. The letters consistently start from operational excellence, returns, and continuity, then attach lower-carbon businesses, partnerships, CCUS, hydrogen, renewable fuels, and technology-linked demand as bounded options. That makes Chevron a disciplined ambidextrous case rather than a transformational one: the company explores from the edge of a stable operating formula instead of redesigning the whole narrative around exploration.")

    pdf.h2("C. Industry vs Industry")
    pdf.para("The industry comparison is the cleanest organizing structure. Technology firms present exploration as visible category creation. Nvidia's Horizon Scanning rate is 24.873 per 1,000 words, and Amazon's customer share is 0.933. The quotes match the counts: Amazon's 1997 letter says the company will \"focus relentlessly on our customers\"; Nvidia's 2017 letter says \"GPU computing has arrived.\" These are not merely slogans. They identify how each firm justifies entrepreneurial investment: Amazon through customer-backward invention, Nvidia through technology-wave recognition.")
    pdf.para(f"Energy firms present innovation as disciplined renewal under constraints. Shell's explore share is {company_quant['Shell']['explore_share_of_explore_exploit']} and Chevron's is {company_quant['Chevron']['explore_share_of_explore_exploit']}, but the qualitative evidence shows bounded exploration, not absence of innovation. Shell's transition formula is \"more value with less emissions\" (Shell, 2025); Chevron's is \"higher returns, lower carbon\" (Chevron, 2021). Both phrases tie innovation to legitimacy, returns, and asset productivity, which is consistent with oil-and-gas capital intensity, safety requirements, regulatory exposure, and long asset lives.")
    pdf.table(
        ["Comparison", "Technology pattern", "Energy pattern", "Interpretive result"],
        [
            ["Innovation visibility", "High: AI, cloud, GPU platforms, chips, robotics, customer systems.", "Lower and more filtered: LNG, CCUS, hydrogen, renewable fuels, lower-carbon operations.", "Tech exploration is easier to see lexically; energy exploration is embedded in portfolio and governance language."],
            ["Dominant constraint", "Speed, scale, ecosystem adoption, customer experience.", "Safety, returns, reliability, emissions, policy, capital discipline.", "Different constraints produce different CE vocabularies."],
            ["Explore/exploit", f"Amazon {company_quant['Amazon']['explore_share_of_explore_exploit']} explore share; Nvidia {company_quant['Nvidia']['explore_share_of_explore_exploit']}.", f"Shell {company_quant['Shell']['explore_share_of_explore_exploit']}; Chevron {company_quant['Chevron']['explore_share_of_explore_exploit']}.", "Tech firms narrate exploration more explicitly overall; energy firms narrate exploitation as the basis for renewal."],
        ],
        [17, 28, 30, 30],
        size=6,
    )

    pdf.h2("D. Within Technology: Amazon vs Nvidia")
    pdf.para("Amazon and Nvidia are both platform firms, but their strategic narratives differ. Amazon is customer-backward: the company-level dominant IPM theme is Purpose, Vision, and Governance at 11.841 per 1,000 words, and the customer/shareholder pair is overwhelmingly customer-weighted at 0.933. Nvidia is technology-architecture-forward: its dominant IPM theme is Horizon Scanning at 24.873 per 1,000 words, with 2025 reaching 37.419.")
    pdf.para(f"The difference matters for Corporate Entrepreneurship. Amazon's letters make exploration legitimate by tying invention to customer value and by treating long-term investment as a shareholder duty. Nvidia's letters make exploration legitimate by naming computing transitions and building ecosystems around them. In 2025, Nvidia's exploit count rises to {q(quant_letter, 'Nvidia', 2025)['exploit_count']} because the AI story has become an execution story: supply, deployment, data centers, full-stack platforms, and monetization. That is ambidexterity in a platform firm: exploit the installed architecture while exploring the next computing wave.")

    pdf.h2("E. Within Energy: Shell vs Chevron")
    pdf.para("Shell and Chevron are closer to each other than Amazon and Nvidia are, but the difference inside energy is still analytically important. Shell is more transformational in its transition narrative. Its 2020 Purpose/Vision/Governance rate of 17.637 per 1,000 words is the highest Shell purpose score and appears in the same letter that links shareholder value to net-zero. Chevron is more continuity-oriented. Its 2018 Agile Execution rate of 6.223 per 1,000 words and repeated \"higher returns, lower carbon\" frame show a company adding adjacencies while preserving operational discipline.")
    pdf.para("This is not a simple moral contrast between bold Shell and conservative Chevron. Shell's 2025 letter is more disciplined and selective than its 2020 transition reset, while Chevron's later letters contain more lower-carbon and partnership language than Watson's 2013 letter. The better interpretation is that Shell's renewal process is portfolio-transformational, whereas Chevron's is operationally incremental and adjacency-based.")
    pdf.para("The energy-company tension is therefore richer than discipline versus innovation. Shell's entrepreneurial tension is portfolio reconfiguration: BG/LNG, deep water, divestments, structural cost reductions, climate targets, and the safety problem that remains visible in the 2025 letter. Chevron's entrepreneurial tension is adjacency without rupture: Future Energy Fund, New Energies, Noble/PDC/Hess portfolio moves, renewable fuels, CCS, hydrogen, AI-related power demand, and record core production. In CE terms, Shell more visibly redesigns the portfolio; Chevron more visibly preserves the operating formula while attaching new options to it.")

    pdf.h2("F. Framework Synthesis")
    pdf.para("This subsection pulls the frameworks together rather than treating them as separate boxes. The Innovation Process Model helps identify which dimensions are most visible in each company's letters and how those dimensions interact. Explore versus exploit shows whether the company is extending the core, searching for new options, or doing both at once. Greiner-style scaling logic helps explain where growth creates coordination strain, and the 4Ps lens clarifies whether innovation is mainly about products, processes, positions, or deeper shifts in the firm's underlying business paradigm.")
    pdf.h3("Amazon")
    pdf.para("Amazon's letters are anchored most visibly in Purpose, Vision, and Governance, with customer purpose acting as the legitimating mechanism that allows the firm to pursue experiments that would otherwise look too expensive, too uncertain, or too long-term. That pattern is already visible in 1997, where customer focus and long-term market creation justify losses and investment, and it becomes more organizationally explicit in 2016's anti-bureaucracy Day 1 warning. Under Jassy, the same logic scales into a more explicit options portfolio: AI, custom silicon, logistics, Kuiper, robotics, and AWS all appear as new bets backed by an existing platform base. In explore/exploit terms, Amazon is ambidextrous because the company repeatedly uses an exploited installed system - customers, infrastructure, Prime, marketplace, AWS, fulfillment - to keep funding and legitimating exploration.")
    pdf.para("Greiner is useful here because Amazon's main entrepreneurial tension is not whether to innovate, but how to preserve initiative as organizational scale increases. The repeated warnings against process drag, slow decisions, and loss of Day 1 energy are signs of a scaling firm trying to keep entrepreneurial behavior alive inside a very large system. In 4Ps terms, Amazon combines product innovation, process innovation, and position innovation: it launches offerings, redesigns internal operating systems, and repeatedly reframes what kind of company it is.")
    pdf.h3("Nvidia")
    pdf.para("Nvidia's letters are anchored most visibly in Horizon Scanning / Sense-making. Huang's letters consistently begin by naming a technological inflection - GPU computing, accelerated computing, generative AI, AI factories - and then move to the platform architecture required to capture that shift. This is why Nvidia scores so strongly on Horizon Scanning but still becomes more execution-heavy in the later letters: once the wave is identified, the entrepreneurial problem becomes one of building and scaling the ecosystem around it.")
    pdf.para("The company's ambidexterity is therefore architecture-led. Nvidia explores by reading the next computing wave early, then exploits by standardizing it into systems, software stacks, developer ecosystems, data-center relationships, and infrastructure partnerships. Greiner adds a useful nuance: growth creates coordination demands across product lines, software, manufacturing, cloud partners, and enterprise deployment, so entrepreneurial leadership has to be matched by operational integration. In 4Ps terms, Nvidia begins with product innovation but increasingly shifts toward paradigm and position innovation, because the letters recast the firm from a chip company into an AI infrastructure platform.")
    pdf.h3("Shell")
    pdf.para("Shell's letters are most revealing when read through the interaction between Purpose, Vision, and Governance and Strategic Options, Experimentation, and Choices. The letters do not show a firm lacking entrepreneurial options; they show a firm trying to decide which options can survive the tests imposed by capital intensity, safety, policy exposure, emissions commitments, and shareholder expectations. That is why the most entrepreneurial Shell moments are not the most rhetorically exploratory ones. The 2016 BG/LNG integration phase is entrepreneurial because it reorders the portfolio, while 2020 is entrepreneurial because it tries to legitimate a transition narrative that still has to hold together value creation, net-zero ambition, and operating resilience.")
    pdf.para("Explore/exploit therefore has to be read carefully in Shell. The low lexical explore share does not contradict entrepreneurship; it reveals that exploration is embedded in governance and portfolio language rather than in startup-style experimentation words. Greiner is relevant because large integrated firms often struggle less with discovering options than with reallocating authority, capital, and organizational attention fast enough to act on them. In 4Ps terms, Shell's renewal is less about breakthrough product novelty and more about process, position, and partial paradigm change: LNG, lower-carbon businesses, divestments, and integrated-energy framing reshape how the company positions and organizes itself.")
    pdf.h3("Chevron")
    pdf.para("Chevron's letters are anchored most visibly in Agile Execution and Organization, with new options attached to a base of operational excellence, returns, reliability, and safety rather than presented as a full narrative reset. This does not mean Chevron lacks corporate entrepreneurship. It means the company defines entrepreneurship more narrowly: new options must fit the existing operating formula and must be explained as accretive to, rather than disruptive of, that formula.")
    pdf.para("That pattern makes Chevron the clearest adjacency case in the corpus. The firm explores through lower-carbon businesses, CCUS, hydrogen, renewable fuels, partnerships, and technology-linked demand, but it does so from an exploitative base that remains highly visible in the letters. Greiner helps here too: continuity can be a scaling advantage, but it can also become a coordination and incentive constraint if new businesses are always forced to prove themselves against the same short-horizon operating logic as the core. In 4Ps terms, Chevron's innovation is weighted toward process and position change rather than paradigm change, which is why the letters feel steadier than Shell's even when meaningful renewal is occurring.")
    pdf.para("Taken together, the frameworks sharpen the comparative result. Amazon and Nvidia both show visible ambidexterity, but Amazon's entrepreneurship is purpose-led and organizationally expansive, whereas Nvidia's is horizon-led and architecture-driven. Shell and Chevron both show constrained ambidexterity, but Shell's entrepreneurial pressure is portfolio transformation under transition tension, whereas Chevron's is disciplined adjacency around a stable operating model. The value of the combined framework is that it shows not only who appears more exploratory, but how different firms move from leadership stance to option formation to execution under different industry conditions.")

    pdf.h1("6. Findings & Conclusion")
    pdf.para("This section synthesizes the analysis rather than restating the tables.")
    pdf.h2("Findings")
    pdf.bullet("Across industries, the main pattern is not innovation versus non-innovation. It is visible platform exploration in technology versus disciplined incumbent renewal in energy.")
    pdf.bullet("Within technology, Amazon legitimates innovation through customer value and long-term reinvention, while Nvidia legitimates innovation through technology-wave recognition and ecosystem architecture.")
    pdf.bullet("Within energy, Shell appears more portfolio-transformational, using transition, LNG, divestments, cost reduction, and emissions commitments to reshape the firm; Chevron appears more continuity-oriented, attaching lower-carbon and technology options to operational excellence and shareholder-return discipline.")
    pdf.bullet("Across all four firms, ambidexterity is the shared CE pattern: each company uses an established core to pursue new options, but the acceptable vocabulary and pace of exploration are shaped by industry economics and governance constraints.")
    pdf.h2("Conclusion")
    pdf.para("The findings support the main hypothesis. The letters do not separate the firms into innovative technology companies and non-innovative energy incumbents. Instead, they reveal two different forms of corporate entrepreneurship. Amazon and Nvidia make exploration more visible because digital-platform and AI competition reward horizon scanning, category creation, ecosystem building, and rapid scaling. Shell and Chevron make exploitation more visible because entrepreneurial action has to be justified through safety, reliability, capital discipline, shareholder distributions, transition legitimacy, and long-lived assets.")
    pdf.para("The sub-hypotheses are also clarified by the evidence. H1 is supported: technology letters more visibly emphasize horizon scanning and explicit exploratory language, especially in Nvidia's recurring technology-wave framing and Amazon's later experimentation and AI language. H2 is supported: energy letters consistently frame innovation through disciplined options rather than through open-ended experimentation. H3 is supported with nuance: Amazon and Nvidia are more customer- and ecosystem-facing, but Shell and Chevron do not simply prioritize shareholders; they balance shareholder claims with customers, society, climate, energy security, and policy legitimacy. H4 is strongly supported: every company retains a recognizable strategic identity, yet each also changes meaningfully across eras, leadership phases, shocks, and strategic resets.")
    pdf.para("The conclusion therefore turns on innovation logic rather than simple innovativeness. Amazon and Nvidia illustrate platform-based corporate entrepreneurship, but they do so differently: Amazon is customer-backward, purpose-led, and organizationally expansive, while Nvidia is horizon-led, architecture-driven, and ecosystem-executed. Shell and Chevron illustrate incumbent-energy renewal, but again in different forms: Shell is more portfolio-transformational and governance-tensioned, while Chevron is more continuity-oriented and adjacency-based.")
    pdf.h3("Company Conclusions")
    pdf.para("Amazon's letters show a company that keeps returning to customer purpose as the source of legitimacy, while shifting the operating logic from founder doctrine to large-scale ambidextrous reinvention under Jassy. The company evolves from early market-creation rhetoric to a much broader portfolio of AI, infrastructure, logistics, and platform options, but the through-line remains the same: customer value authorizes experimentation.")
    pdf.para("Nvidia's letters show the clearest horizon-scanning identity in the corpus: Jensen Huang repeatedly turns technological inflection points into platform architecture, then into execution at ecosystem and infrastructure scale. The later letters do not replace exploration with exploitation; they show exploration becoming institutionalized as a scalable platform business.")
    pdf.para("Shell's letters show the most visible tension between transition ambition and incumbent discipline. Its entrepreneurship is strongest when portfolio choices, LNG/upstream strength, divestment, cost reduction, and governance legitimacy are held together rather than treated as separate agendas. Shell therefore supports the hypothesis that energy entrepreneurship is real, but more constrained, contested, and legitimacy-dependent than technology entrepreneurship.")
    pdf.para("Chevron's letters show the most continuity. Its corporate entrepreneurship is real, but it is adjacency-based: operational excellence and shareholder-return discipline remain the base from which lower-carbon and technology options are pursued. That makes Chevron the clearest case that exploitative language can still coexist with meaningful, if bounded, strategic renewal.")
    pdf.para("Taken together, these findings matter for Corporate Entrepreneurship beyond the four cases in this study. They suggest that the same broad innovation-process logic can be present across industries while taking very different visible forms. A firm can be entrepreneurial through customer-backed experimentation, architecture-led ecosystem building, portfolio transformation under transition pressure, or disciplined adjacency around a durable core. The practical implication is that CE should be evaluated against industry-shaped constraints and enabling structures rather than against a single vocabulary of disruption.")

    pdf.h1("Appendix Guide")
    pdf.para("The appendices separate audit material from the main argument. Appendix A identifies the official primary-source corpus. Appendix B lists strict keyword counts by theme and subtheme. Appendix C aggregates subtheme counts by company. Appendix D records the year-selection rationale. Appendix E links rhetoric to company-reported outcomes. Appendix F preserves the detailed company-era IPM mapping. Appendix G provides the per-year quantitative breakdown used to analyze each selected letter, including the raw explore and exploit counts for each year.")
    pdf.h1("Appendix A. Letter Corpus")
    pdf.para("This appendix lists the 28 official primary-source letters and review sections used in the analysis, with the source titles that anchor citation and reproducibility.", size=8)
    pdf.table(
        ["Company", "Year", "Official source title"],
        [[r["company"], r["year"], r["title"]] for r in refs],
        [10, 6, 70],
        size=7,
    )
    pdf.h1("Appendix B. Keyword Counts By Theme And Subtheme")
    pdf.para("Counts below use strict dictionary keywords. They are not sentiment scores, causality tests, or complete measures of strategy. A keyword may appear in more than one conceptual category if the dictionary deliberately places it there; counts should therefore be interpreted as coded lexical emphasis, not unique word totals. Ambiguous words require context checks: for example, platform may mean a digital platform in technology letters or a physical/drilling platform in energy letters. The report therefore treats the appendix as quantitative evidence to be interpreted alongside the letter quotations and company-era analysis.", size=8)
    pdf.table(
        ["Theme", "Subtheme", "Keyword", "Amz", "Nvd", "Shl", "Chv", "Tot"],
        [[r["theme"], r["subtheme"], r["keyword"], r["Amazon"], r["Nvidia"], r["Shell"], r["Chevron"], r["Total"]] for r in keyword_rows],
        [18, 19, 19, 4, 4, 4, 4, 4],
        size=5,
    )
    pdf.h1("Appendix C. Subtheme Counts By Company")
    pdf.para("This appendix aggregates strict dictionary hits by subtheme and company. It shows which subthemes are most visible at the company level before those counts are interpreted in the main text.", size=8)
    pdf.table(
        ["Theme", "Subtheme", "Amazon", "Nvidia", "Shell", "Chevron", "Total"],
        [[r["theme"], r["subtheme"], r["Amazon"], r["Nvidia"], r["Shell"], r["Chevron"], r["Total"]] for r in subtheme_rows],
        [22, 24, 6, 6, 6, 7, 6],
        size=6,
    )
    pdf.h1("Appendix D. Selected Letter Rationale")
    pdf.para("Detailed selection rationale is moved here to keep the main body focused on argument and interpretation.", size=8)
    pdf.table(
        ["Company", "Year", "Strategic phase", "Why included"],
        [[r["company"], r["year"], r["strategic_phase"], r["inclusion_rationale"]] for r in selection_rows],
        [8, 5, 28, 55],
        size=5,
    )
    pdf.h1("Appendix E. Outcome Anchors")
    pdf.para("These anchors connect selected claims to company-reported outcomes inside the letters. They are supporting evidence, not independent external validation.", size=8)
    pdf.table(
        ["Company", "Year", "Outcome anchor", "Interpretation"],
        [[r["company"], r["year"], r["outcome_anchor"], r["interpretation"]] for r in outcome_anchor_rows],
        [8, 9, 50, 39],
        size=5,
    )
    pdf.h1("Appendix F. Company-Era IPM Matrix")
    pdf.para("This appendix preserves the detailed company-era framework mapping behind the shorter synthesis in the qualitative section.", size=8)
    pdf.table(
        ["Company", "Era", "Explore/exploit", "Dominant IPM", "Evidence"],
        [[r["company"], r["era"], r["explore_exploit_diagnosis"], r["dominant_ipm"], r["evidence"]] for r in era_ipm_rows],
        [8, 24, 28, 22, 35],
        size=5,
    )
    pdf.h1("Appendix G. Per-Year Quantitative Breakdown")
    pdf.para("This appendix reports the main year-level counts for each selected letter. It lets the reader see how each company's Innovation Process Model profile changes year by year rather than only at the company or era level, and it also shows the raw strict explore and exploit counts used in the paired analysis.", size=8)
    for company in ["Amazon", "Nvidia", "Shell", "Chevron"]:
        pdf.h3(company)
        company_rows = [r for r in yearly_rows if r["company"] == company]
        pdf.table(
            ["Year", "Words", "Lead", "Horiz", "Purpose", "Options", "Exec", "Expl", "Explt"],
            [[r["year"], r["words"], r["lead_per_1000"], r["horizon_per_1000"], r["purpose_per_1000"], r["options_per_1000"], r["execution_per_1000"], r["explore_count"], r["exploit_count"]] for r in company_rows],
            [5, 6, 5, 6, 7, 7, 5, 5, 5],
            size=6,
        )
    pdf.h1("References: Official Primary Sources")
    for r in refs:
        pdf.para(f"{r['company']} ({r['year']}). {r['title']}. {r['source']}. Accessed {r['access_date']}. URL: {r['url']}", size=8)


def main() -> None:
    pdf = PDF()
    add_report(pdf)
    pdf.build(OUT)
    docx = DOCX()
    add_report(docx)
    docx.build(DOCX_OUT)
    print(OUT)
    print(DOCX_OUT)
    print(KEYWORD_APPENDIX)
    print(KEYWORD_YEAR_APPENDIX)
    print(SUBTHEME_APPENDIX)
    print(HYPOTHESIS_APPENDIX)
    print(ERA_IPM_APPENDIX)
    print(SELECTION_RATIONALE_APPENDIX)
    print(OUTCOME_ANCHORS_APPENDIX)
    print(YEAR_COUNTS_APPENDIX)


if __name__ == "__main__":
    main()
