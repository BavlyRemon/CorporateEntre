#!/usr/bin/env python3
"""Create a single integrated PDF draft for the CEI comparative letter project.

The environment does not include Pandoc, wkhtmltopdf, or ReportLab, so this
script writes a simple text-based PDF directly using built-in PDF primitives.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "corporate_entrepreneurship_integrated_analysis_draft.pdf"


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
    }
    for src, dst in replacements.items():
        s = s.replace(src, dst)
    return s.encode("latin-1", "replace").decode("latin-1")


def read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc_pdf(text: str) -> str:
    return clean(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class SimplePDF:
    def __init__(self) -> None:
        self.pages: list[list[tuple[str, int, float, float, str]]] = []
        self.current: list[tuple[str, int, float, float, str]] = []
        self.y = 742
        self.page_no = 0
        self.margin = 54
        self.width = 504
        self.new_page()

    def new_page(self) -> None:
        if self.current:
            self.pages.append(self.current)
        self.page_no += 1
        self.current = []
        self.y = 742
        if self.page_no > 1:
            self.add_text("Corporate Entrepreneurship and Innovation Comparative Letter Analysis", size=8, font="Helvetica-Oblique")
            self.y -= 8

    def add_text(self, text: str, size: int = 10, font: str = "Helvetica", indent: int = 0) -> None:
        line_height = size + 4
        if self.y < 66:
            self.new_page()
        self.current.append((font, size, self.margin + indent, self.y, clean(text)))
        self.y -= line_height

    def add_blank(self, height: int = 8) -> None:
        self.y -= height
        if self.y < 66:
            self.new_page()

    def wrap(self, text: str, size: int = 10, indent: int = 0) -> list[str]:
        avg_char = size * 0.50
        max_chars = max(42, int((self.width - indent) / avg_char))
        words = clean(text).split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = word if not current else current + " " + word
            if len(test) <= max_chars:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def para(self, text: str, size: int = 10, indent: int = 0) -> None:
        for line in self.wrap(text, size=size, indent=indent):
            self.add_text(line, size=size, indent=indent)
        self.add_blank(4)

    def bullet(self, text: str, size: int = 10) -> None:
        lines = self.wrap(text, size=size, indent=18)
        if not lines:
            return
        self.add_text("- " + lines[0], size=size, indent=6)
        for line in lines[1:]:
            self.add_text("  " + line, size=size, indent=6)

    def h1(self, text: str) -> None:
        self.add_blank(10)
        self.add_text(text.upper(), size=15, font="Helvetica-Bold")
        self.add_blank(4)

    def h2(self, text: str) -> None:
        self.add_blank(8)
        self.add_text(text, size=12, font="Helvetica-Bold")
        self.add_blank(2)

    def h3(self, text: str) -> None:
        self.add_blank(5)
        self.add_text(text, size=10, font="Helvetica-Bold")

    def table(self, headers: list[str], rows: list[list[object]], widths: list[int] | None = None) -> None:
        if widths is None:
            widths = [max(8, int(92 / len(headers)))] * len(headers)
        fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
        self.add_text(fmt.format(*[clean(h)[:w] for h, w in zip(headers, widths)]), size=8, font="Courier-Bold")
        self.add_text(fmt.format(*["-" * w for w in widths]), size=8, font="Courier")
        for row in rows:
            cells = [clean(c).replace("\n", " ") for c in row]
            split_cells = []
            max_lines = 1
            for cell, width in zip(cells, widths):
                parts = []
                while len(cell) > width:
                    cut = cell.rfind(" ", 0, width)
                    if cut < 5:
                        cut = width
                    parts.append(cell[:cut].strip())
                    cell = cell[cut:].strip()
                parts.append(cell)
                split_cells.append(parts)
                max_lines = max(max_lines, len(parts))
            for idx in range(max_lines):
                printable = [parts[idx] if idx < len(parts) else "" for parts in split_cells]
                if self.y < 78:
                    self.new_page()
                    self.add_text(fmt.format(*[clean(h)[:w] for h, w in zip(headers, widths)]), size=8, font="Courier-Bold")
                    self.add_text(fmt.format(*["-" * w for w in widths]), size=8, font="Courier")
                self.add_text(fmt.format(*[c[:w] for c, w in zip(printable, widths)]), size=8, font="Courier")
        self.add_blank(8)

    def build(self, path: Path) -> None:
        if self.current:
            self.pages.append(self.current)
            self.current = []
        objects: list[bytes] = []

        def add_obj(data: bytes) -> int:
            objects.append(data)
            return len(objects)

        catalog_id = add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
        pages_placeholder_id = add_obj(b"")
        font_ids = {
            "Helvetica": add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
            "Helvetica-Bold": add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"),
            "Helvetica-Oblique": add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>"),
            "Courier": add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"),
            "Courier-Bold": add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>"),
        }
        font_resource = " ".join(f"/F{i} {obj} 0 R" for i, obj in enumerate(font_ids.values(), start=1))
        font_lookup = {name: f"F{i}" for i, name in enumerate(font_ids, start=1)}
        page_ids: list[int] = []
        for page_no, lines in enumerate(self.pages, start=1):
            stream_lines = []
            for font, size, x, y, text in lines:
                stream_lines.append(f"BT /{font_lookup[font]} {size} Tf {x:.1f} {y:.1f} Td ({esc_pdf(text)}) Tj ET")
            footer = f"BT /F1 8 Tf 54 35 Td (Page {page_no}) Tj ET"
            stream = ("\n".join(stream_lines + [footer])).encode("latin-1", "replace")
            content_id = add_obj(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream")
            page_id = add_obj(
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << {font_resource} >> >> /Contents {content_id} 0 R >>"
                ).encode("latin-1")
            )
            page_ids.append(page_id)
        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects[pages_placeholder_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, obj in enumerate(objects, start=1):
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

def company_letter_set_rows() -> list[list[str]]:
    return [
        ["Amazon", "1997, 2016, 2020, 2021, 2022, 2024, 2025", "Day 1 doctrine, Bezos/Jassy transition, pandemic, AI/platform reinvention"],
        ["Nvidia", "2017, 2018, 2020, 2021, 2022, 2023, 2025", "GPU-to-platform shift, AI infrastructure, edge/data center scaling"],
        ["Shell", "2014, 2015, 2016, 2020, 2022, 2024, 2025", "BG/LNG, oil-price pressure, pandemic reset, Powering Progress, Sawan discipline"],
        ["Chevron", "2013, 2018, 2020, 2021, 2022, 2023, 2024", "Operational excellence, Wirth transition, lower carbon, Hess/portfolio, AI-energy demand"],
    ]


def main() -> None:
    quant = read_csv("05_outputs/tables/quant_summary_by_company.csv")
    ipm = read_csv("05_outputs/tables/ipm_comparison_matrix.csv")
    comparative = read_csv("05_outputs/tables/comparative_matrix.csv")

    p = SimplePDF()
    p.add_text("Corporate Entrepreneurship and Innovation", size=17, font="Helvetica-Bold")
    p.add_text("Comparative CEO/Shareholder Letter Analysis", size=17, font="Helvetica-Bold")
    p.add_blank(12)
    p.add_text("Integrated Working Draft in Final Paper Structure", size=12, font="Helvetica-Bold")
    p.add_text("Companies: Amazon, Nvidia, Shell, Chevron", size=11)
    p.add_text("Industries: Technology / digital platforms and oil & gas / energy", size=11)
    p.add_text("Corpus: 28 selected CEO/shareholder leadership letters, seven per company", size=11)
    p.add_text("Generated: 2026-04-19", size=10)
    p.add_blank(10)
    p.para(
        "This PDF consolidates the research workspace into one structured working document. It is not a final polished paper; it is a writing-ready analysis package organized in the requested final-paper sections: Introduction, Hypothesis & Rationale, Methodology, Quantitative Analysis, Qualitative Analysis, and Findings & Conclusion."
    )
    p.para(
        "Citation note: letter evidence is cited to the extracted selected-letter files in 02_extracted_text/selected_ceo_letters/. Official source URLs, access dates, titles, and extraction boundaries remain documented in selected_ceo_letters_manifest.csv, sources_master.csv, and ceo_letter_availability_audit.md."
    )

    p.h1("1. Introduction")
    p.para(
        "This project compares how four large firms narrate corporate entrepreneurship and innovation in CEO/shareholder letters. Amazon and Nvidia represent technology and digital-platform competition, where innovation is often visible through platform expansion, AI, cloud, chips, robotics, developer ecosystems, and rapid category creation. Shell and Chevron represent oil and gas / energy, where innovation is filtered through capital intensity, safety, commodity cycles, regulation, energy security, climate-transition pressure, and long-lived assets."
    )
    p.para(
        "The core analytical claim is not that technology firms innovate and energy firms do not. The stronger comparison is that innovation has different strategic grammar across industries. Amazon and Nvidia tend to narrate innovation as inflection sensing, platform expansion, and customer/ecosystem opportunity. Shell and Chevron tend to narrate innovation as disciplined renewal of reliable, safety-critical, capital-intensive systems."
    )
    p.h2("Final Letter Corpus")
    p.table(["Company", "Selected years", "What the set captures"], company_letter_set_rows(), [10, 31, 45])

    p.h1("2. Hypothesis & Rationale")
    p.h2("Main Hypothesis")
    p.para(
        "Across the 28 selected letters, technology-platform firms will use more explicit exploratory and option-creation language than oil-and-gas firms, while oil-and-gas firms will frame innovation more strongly through exploitation, operational discipline, safety, capital allocation, resilience, and regulated transition. However, the expected pattern is not a simple tech-explores / energy-exploits split. The strongest firms in both industries display ambidextrous leadership by linking exploratory bets to existing capabilities, cash generation, ecosystem relationships, and long-term strategic renewal."
    )
    p.h2("Supporting Hypotheses")
    p.bullet("H1: Amazon and Nvidia will show stronger customer/ecosystem and technology-horizon language because their innovation models depend on platform adoption, customer use cases, developers, partners, and networked complements.")
    p.bullet("H2: Shell and Chevron will use more exploitative language because energy innovation is constrained by asset lives, safety, commodity cycles, regulation, and capital intensity; exploration appears through selective lower-carbon, portfolio, partnership, and acquisition options.")
    p.bullet("H3: Long-termism will appear in all four firms, but with different meanings: technology letters use it to justify experimentation and platform bets, while energy letters use it to justify asset durability, policy stability, reliability, and transition pacing.")
    p.bullet("H4: The Innovation Process Model will reveal different dominant process patterns: Amazon as customer-purpose and experimentation; Nvidia as horizon scanning and ecosystem architecture; Shell as transition governance and portfolio discipline; Chevron as operational execution and controlled adjacency.")
    p.h2("Rationale For Comparing These Industries")
    p.para(
        "The comparison is analytically useful because both industries face disruption, large capital commitments, ecosystem dependencies, and long-term uncertainty, but the speed, visibility, and governance of innovation differ sharply. Technology firms can more openly narrate category creation and platform expansion. Energy firms must narrate innovation while defending reliability, safety, affordability, capital discipline, and social license."
    )

    p.h1("3. Methodology")
    p.h2("Research Design")
    p.para(
        "The study uses a comparative longitudinal text-analysis design. The unit of analysis is each selected CEO/shareholder leadership letter, not the full annual report. This distinction matters because the research design requires analysis of leadership communication rather than irrelevant financial-report boilerplate. The selected corpus contains 28 leadership texts, seven per company."
    )
    p.h2("Why CEO/Shareholder Letters")
    p.para(
        "CEO and shareholder letters are valid strategic texts because they are recurring, public, leadership-authored narratives of performance, strategic priorities, risk, purpose, and future direction. They are not neutral records of strategy; they are managerial framing documents. That limitation is also their value for Corporate Entrepreneurship and Innovation because the project studies how leaders justify innovation, renewal, risk, investment, and ambidexterity to investors and stakeholders."
    )
    p.h2("Analytical Frameworks")
    p.bullet("Innovation Process Model: Strategic Leadership; Horizon Scanning / Sense-making; Purpose, Vision, and Governance; Strategic Options, Experimentation, and Choices; Agile Execution and Organization.")
    p.bullet("Explore vs exploit: exploration is identified through invention, experimentation, emerging opportunity, pilots, R&D, new businesses, and option creation; exploitation is identified through operational excellence, cash flow, returns, efficiency, reliability, safety, capital discipline, and scale.")
    p.bullet("Comparative design: within-company over time, within-industry comparison (Amazon vs Nvidia; Shell vs Chevron), cross-industry comparison (technology vs energy), and all-four synthesis.")
    p.h2("Quantitative Method")
    p.para(
        "The quantitative analysis applies a strict lexical dictionary to the selected letter bodies and normalizes counts per 1,000 words because letter lengths differ substantially. Counts are treated as indicators of emphasis, not direct proof of actual innovation performance. Ambiguous terms such as platform, return, growth, and safety require qualitative interpretation."
    )
    p.h2("Qualitative Method")
    p.para(
        "The qualitative analysis reads the letters for recurring strategic themes, leadership posture, purpose, customer/shareholder framing, strategic options, execution logic, and changes over time. The Innovation Process Model is used as a process chain: how each company moves from leadership framing to sense-making, purpose, options, and execution."
    )

    p.h1("4. Quantitative Analysis")
    p.h2("Company-Level Theme Results")
    qrows = []
    for r in quant:
        qrows.append([
            r["company"],
            r["total_word_count"],
            r["Strategic Leadership_per_1000"],
            r["Horizon Scanning / Sense-making_per_1000"],
            r["Purpose, Vision, and Governance_per_1000"],
            r["Strategic Options, Experimentation, and Choices_per_1000"],
            r["Agile Execution and Organization_per_1000"],
            r["dominant_ipm_theme_per_1000"],
        ])
    p.table(["Company", "Words", "Lead", "Horizon", "Purpose", "Options", "Exec", "Dominant"], qrows, [9, 7, 6, 7, 7, 7, 6, 26])
    p.para(
        "The normalized counts show that Amazon's dominant measured IPM theme is Purpose, Vision, and Governance, driven by repeated customer, shareholder, long-term, and value language. Nvidia's dominant measured theme is Horizon Scanning / Sense-making, reflecting the density of AI, GPU, accelerated computing, platform, and infrastructure language. Shell and Chevron also show Purpose, Vision, and Governance as dominant, but their purpose language is tied to energy reliability, shareholder value, net-zero or lower-carbon framing, safety, and disciplined transition."
    )
    p.h2("Cross-Cutting Ratios")
    ratio_rows = []
    for r in quant:
        ratio_rows.append([
            r["company"],
            r["explore_share_of_explore_exploit"],
            r["customer_share_of_customer_shareholder"],
            r["long_term_share_of_long_short"],
            r["entrepreneurial_share_of_entrepreneurial_managerial"],
            r["internal_share_of_internal_external"],
            r["risk_share_of_risk_performance"],
        ])
    p.table(["Company", "Explore", "Customer", "LongTerm", "Entrepr", "Internal", "Risk"], ratio_rows, [9, 8, 9, 9, 8, 8, 7])
    p.para(
        "The paired ratios support the broad hypothesis but require caution. Amazon shows the highest customer share and a balanced explore/exploit profile. Nvidia's strict explore share is lower than its qualitative exploratory posture because many of its exploration signals appear as named technology-horizon terms such as AI, GPU, accelerated computing, inference, and AI factories rather than words like experiment or pilot. Shell and Chevron show lower explore shares because their letters emphasize capital discipline, safety, cash flow, reliability, and returns."
    )
    p.h2("Quantitative Interpretation")
    p.bullet("Amazon: customer-purpose language is quantitatively dominant; strategic-options and execution language support a reading of mature-firm ambidexterity.")
    p.bullet("Nvidia: horizon-scanning intensity is the clearest quantitative signal; the corpus is saturated with AI and accelerated-computing sense-making.")
    p.bullet("Shell: purpose/governance language dominates because transition is narrated through shareholder value, net-zero ambition, customer demand, trust, and discipline.")
    p.bullet("Chevron: purpose/governance and strategic-options terms appear within an exploitative operational frame: lower carbon, stockholder value, safety, production, and portfolio optimization.")

    p.h1("5. Qualitative Analysis")
    p.h2("Innovation Process Model Analysis")
    ipm_rows = []
    for r in ipm:
        ipm_rows.append([r["company"], r["qualitative_ipm_pattern"], r["dominant_quant_theme"]])
    p.table(["Company", "Qualitative IPM process pattern", "Dominant quant theme"], ipm_rows, [9, 55, 28])
    p.para(
        "The Innovation Process Model shows that the four firms do not merely differ in how many innovation words they use. They differ in the process by which leadership turns external change into strategic action. Amazon follows a customer-purpose -> inflection-sensing -> multiple-options -> fast-scaling model. Nvidia follows a technology-sensing -> platform-architecture -> ecosystem-scaling -> infrastructure-execution model. Shell follows a transition-sensing -> purpose/governance-reconciliation -> portfolio-choices -> disciplined-transformation model. Chevron follows an energy-demand-sensing -> disciplined-purpose -> adjacency-options -> operational-execution model."
    )
    p.h2("Company Qualitative Findings")
    p.h3("Amazon")
    p.para(
        "Amazon projects an innovation identity built around customer obsession, long-term investment, iterative invention, and organizational willingness to endure misunderstanding. The 1997 letter establishes the doctrine of Day 1, customer focus, market leadership, bold investment, and learning. The 2021 and 2025 letters show the same logic at mature scale through fulfillment, AWS, devices, Prime Video, climate, Kuiper/Amazon Leo, AI, chips, robotics, grocery, and organizational speed. Amazon is exploratory, but its exploration is grounded in scale, customer data, infrastructure, and disciplined measurement."
    )
    p.para(
        "Evidence anchors: 02_extracted_text/selected_ceo_letters/amazon/amazon_1997_ceo_letter.txt; amazon_2021_ceo_letter.txt; amazon_2025_ceo_letter.txt.",
        size=9,
    )
    p.h3("Nvidia")
    p.para(
        "Nvidia's letters narrate strategic renewal from GPU computing to full-stack AI infrastructure. The key qualitative pattern is not trial-and-error experimentation but technological sense-making and architectural platform expansion. Nvidia frames itself as moving from chips to platforms, systems, software, AI factories, and global AI infrastructure. Its exploration is anchored in accumulated technical capability, developer ecosystems, partnerships, and supply-chain execution."
    )
    p.para(
        "Evidence anchors: 02_extracted_text/selected_ceo_letters/nvidia/nvidia_2017_ceo_letter.txt; nvidia_2020_ceo_letter.txt; nvidia_2025_ceo_letter.txt.",
        size=9,
    )
    p.h3("Shell")
    p.para(
        "Shell frames innovation through energy transition, integrated assets, safety, capital discipline, and value creation. The 2020 review is especially rich because it joins pandemic resilience, Powering Progress, net-zero ambition, customer-led low-carbon markets, and strategic relationships. The 2025 review sharpens the performance-and-discipline frame: Shell will develop lower-carbon platforms where policy and customer demand support attractive business models. Shell is ambidextrous under constraint."
    )
    p.para(
        "Evidence anchors: 02_extracted_text/selected_ceo_letters/shell/shell_2015_ceo_letter.txt; shell_2020_ceo_letter.txt; shell_2025_ceo_letter.txt.",
        size=9,
    )
    p.h3("Chevron")
    p.para(
        "Chevron projects the most operationally disciplined innovation identity. Its letters foreground operational excellence, safety, strong balance sheet, shareholder returns, and reliable energy. Exploration is present, but it appears as controlled adjacency: Future Energy Fund, OGCI, Renewable Energy Group, hydrogen, CCUS, renewable diesel, Hess, exploration acreage, and AI/data-center power partnerships. Chevron's renewal logic is extension of the core, not radical identity change."
    )
    p.para(
        "Evidence anchors: 02_extracted_text/selected_ceo_letters/chevron/chevron_2013_ceo_letter.txt; chevron_2018_ceo_letter.txt; chevron_2024_ceo_letter.txt.",
        size=9,
    )
    p.h2("Explore vs Exploit Patterns")
    p.para(
        "All four firms are ambidextrous, but in structurally different ways. Amazon exploits fulfillment, AWS, customer relationships, data, and scale to explore new products and platforms. Nvidia exploits GPU architecture, developer ecosystems, and supply-chain capability to explore AI infrastructure. Shell exploits hydrocarbon cash flows, LNG, trading, and integrated energy capabilities to fund and discipline transition options. Chevron exploits operational excellence, advantaged assets, and capital discipline to pursue selective lower-carbon and portfolio adjacencies."
    )
    p.h2("Comparative Analysis")
    for r in comparative:
        p.h3(r["dimension"])
        p.para(
            f"Amazon: {r['Amazon']} Nvidia: {r['Nvidia']} Shell: {r['Shell']} Chevron: {r['Chevron']} Cross-case interpretation: {r['cross_case_interpretation']}"
        )
    p.para(
        "Within technology, Amazon and Nvidia both use platform logic, but Amazon is customer-backward and business-model expansive, while Nvidia is technology-roadmap and ecosystem-architecture driven. Within energy, Shell sounds more transformational and transition-market oriented, while Chevron sounds more continuity-based and operationally disciplined. Across industries, the difference is not innovation versus non-innovation; it is visible platform/category creation versus disciplined renewal of physical, regulated, safety-critical systems."
    )

    p.h1("6. Findings & Conclusion")
    p.h2("Main Findings")
    p.bullet("Finding 1: The quantitative analysis supports a broad industry difference. Amazon and Nvidia show more visible technology, customer/ecosystem, and option-creation emphasis, while Shell and Chevron show more operational, governance, capital-discipline, safety, and value-return emphasis.")
    p.bullet("Finding 2: The qualitative analysis complicates the keyword results. Nvidia's exploratory posture is stronger than the strict explore/exploit ratio alone suggests because much of its exploration is expressed through domain-specific technology language.")
    p.bullet("Finding 3: The Innovation Process Model is the strongest integrative framework. It shows how each firm links leadership, external sense-making, purpose, strategic options, and execution.")
    p.bullet("Finding 4: All four companies exhibit ambidexterity, but their ambidexterity is industry-shaped. Tech ambidexterity is platform expansion at speed; energy ambidexterity is core cash generation plus disciplined transition options.")
    p.bullet("Finding 5: Similar language can mean different things. Long-termism in Amazon supports experimentation and reinvestment; long-termism in Chevron supports durable assets, energy security, and shareholder returns.")
    p.h2("Conclusion")
    p.para(
        "The evidence supports a defensible Corporate Entrepreneurship and Innovation argument: large firms in both technology and energy pursue strategic renewal, but the form and rhetoric of innovation differ by industry context. Amazon and Nvidia make exploration more visible through customer experiences, platform ecosystems, AI, cloud, chips, robotics, and infrastructure roadmaps. Shell and Chevron make exploitation more visible because their innovation strategies must preserve reliability, safety, capital discipline, and social legitimacy while building transition options."
    )
    p.para(
        "The final paper should therefore avoid ranking the firms by apparent innovativeness. A stronger conclusion is that corporate entrepreneurship takes different forms: digital-platform exploration at speed in Amazon and Nvidia, and incumbent-energy renewal under constraint in Shell and Chevron. The Innovation Process Model makes this distinction visible and helps connect quantitative patterns with qualitative interpretation."
    )
    p.h2("Methodological Cautions")
    p.bullet("CEO/shareholder letters are strategic rhetoric; they reveal leadership framing, not complete internal reality.")
    p.bullet("Lexical counts are indicators of emphasis, not direct measures of innovation output.")
    p.bullet("Energy firms' lower explore-word counts should not be read as absence of innovation; much of their exploration appears as portfolio, partnership, and lower-carbon adjacency.")
    p.bullet("Shell uses official annual-report CEO review sections rather than standalone shareholder-letter PDFs; this remains a documented boundary condition.")
    p.h2("Source Base For Citations")
    p.para(
        "Primary evidence: Amazon selected shareholder letters; Nvidia selected CEO/stakeholder letters; Shell selected annual-report Chief Executive Officer reviews; Chevron selected annual-report To our stockholders letters. The precise file paths, official source URLs, access dates, and extraction notes are in the project manifest and source ledgers. Key local audit files: 02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv; 00_admin/sources_master.csv; 03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md."
    )
    p.h2("Recommended Next Steps")
    p.bullet("Use this PDF as the single working draft for coaching or instructor review.")
    p.bullet("Before final submission, choose a smaller number of direct quotes from the extracted letters and convert local file citations into the required citation style.")
    p.bullet("Freeze the dictionary before creating any final charts, because small changes to terms such as return, platform, growth, and safety can affect counts.")
    p.bullet("Add a short limitations paragraph explaining Shell's CEO-review format and the interpretive limits of CEO/shareholder letters.")

    p.build(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
