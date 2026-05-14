# Method Notes

The immediate corpus is a set of official strategic texts: CEO/shareholder letters where a company provides standalone letters, annual-report front matter where the letter is embedded in the annual report, and SEC annual filings as a reproducible official fallback.

Unit of analysis for the later quantitative pass should be the selected letter/report-year text for each company. When a company has no clean standalone CEO letter, the closest official equivalent should be recorded explicitly: e.g., Shell annual-report chair/CEO sections and Chevron annual-report/10-K material.

The quantitative framework should be treated as a structured lexical screen, not a substitute for interpretation. Keyword counts can indicate relative emphasis, but ambiguity must be checked manually because terms such as "platform," "leadership," "growth," and "resilience" can have different meanings in digital-platform and oil-and-gas contexts.

Reproducibility is handled through foldered source files, text extracts, sources_master.csv, and selection memos that record the exact year, title, source URL, access date, and local path where available.

## Data quality audit (2026-05-10)

A structured audit of the 28-letter corpus was completed on 2026-05-10. Six issues were identified and corrected: Chevron 2013 truncation, NVIDIA 2017 chart-label inflation, NVIDIA 2025 GTC sidebar and legal-block inflation, Shell 2014 and 2025 page-furniture boilerplate, Shell corpus labeling (CEO reviews, not standalone letters), and stale manifest word counts. See `00_admin/data_quality_audit.md` for the full record of findings and fixes.
