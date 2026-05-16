# Corporate Entrepreneurship Research Workspace

This workspace is the research groundwork for a paper comparing Amazon, NVIDIA, Shell, and Chevron across technology/digital platforms and oil & gas/energy. It is not the final paper.

> **Live presentation:** <https://bavlyremon.github.io/CorporateEntre/>
> **Live command center (dashboard):** <https://bavlyremon.github.io/CorporateEntre/dashboard/>
> Both auto-deployed from `00_admin/` on every push to `main` via GitHub Actions.

## Apps in this repo

- `00_admin/presentation/` — React/Vite slide deck deployed to GitHub Pages.
- `00_admin/dashboard/` — Internal analysis dashboard (run locally with `npm run dev`).
- `00_admin/review_app/` — Letter-by-letter review tool (Express + Vite).

## Raw sources

`01_raw_sources/` is **not committed** — it contains official annual-report PDFs (the largest is 103 MB) that exceed GitHub's per-file limit. Regenerate locally with `python 00_admin/build_research_workspace.py`.

## What Was Done

- Created the requested folder structure.
- Downloaded official source material where accessible: Amazon shareholder-letter pages, SEC annual filings, NVIDIA official annual-review PDFs for 2011-2025 plus SEC filings and the standalone 2025 Jensen Huang CEO letter, Shell official annual-report PDFs, Chevron official annual-report PDFs for verified letter years plus SEC annual filings, and requested industry benchmark pages.
- Extracted machine-readable text where feasible.
- Built company timelines, candidate-year screening tables, company selection memos, a cross-company industry rationale, a lexical/theme dictionary, pilot counts, methodology notes, and a research log.
- Added a CEO-letter availability audit so selected years are checked for actual leadership-letter sections, not just annual-report PDFs.
- Recorded all source metadata in `00_admin/sources_master.csv` and `06_appendices/download_manifest/download_manifest.csv`.

## Source Counts In Ledger

- amazon: 24
- bcg: 1
- chevron: 20
- forbes: 1
- NVIDIA: 29
- shell: 13
- wipo: 1

## Selected Seven Years Per Company

- Amazon: 1997, 2016, 2020, 2021, 2022, 2024, 2025
- Nvidia: 2017, 2018, 2020, 2021, 2022, 2023, 2025
- Shell: 2014, 2015, 2016, 2020, 2022, 2024, 2025
- Chevron: 2013, 2018, 2020, 2021, 2022, 2023, 2024

## Selection Defense

The selected years are not simply the oldest available reports. They are inflection-point years chosen to support a Corporate Entrepreneurship comparison. The corpus now contains 28 company-years: seven per company. For Shell and Chevron, older years were considered as archival robustness candidates, but the main seven-year sets prioritize comparable strategic-renewal episodes: portfolio renewal, integration, crisis response, energy-transition pressure, acquisition options, capital discipline, and mature execution.

Older Shell candidates: 2005 and 2010. Shell 2014 is now selected as the pre-BG baseline. Older Chevron candidates: 2001/2002, 2005, 2008/2010, and 2011/2012. These remain useful for background, but they were not selected because they would shift the paper toward long-run corporate history rather than the current CE/innovation lens. Chevron 2025 remains a future follow-up candidate because the official Chevron annual-report PDF returned HTTP 503 during the latest audit; the SEC filing exists but is not a substitute for the official stockholder-letter PDF.

The letter-specific audit is in `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`, with a machine-readable version in `03_screening_and_selection/letter_selection_tables/ceo_letter_availability_audit.csv`.

## Key Industry Comparison Points

The tech cases emphasize platform/ecosystem scaling, AI/cloud/accelerated computing, customer/developer adoption, and rapid strategic renewal. The energy cases emphasize capital discipline, long-cycle assets, regulation, commodity volatility, energy transition, portfolio renewal, and safety/reliability. This makes the comparison useful for Corporate Entrepreneurship because all four firms face explore-vs-exploit tensions, but the constraints differ sharply.

## Quantitative Framework

The dictionary is organized around five themes: Strategic Leadership; Horizon Scanning / Context; Purpose, Vision, Governance; Strategic Options, Experimentation, and Choices; and Agile Execution and Organization. Cross-cutting dictionaries cover explore vs exploit, customer vs shareholder, long-term vs short-term, internal vs external innovation, and crisis/risk vs performance language.

## Pilot Status

Pilot lexical counts were run on one text per company where a text extract existed. These are noise tests only. The next pass should manually define letter boundaries, remove non-letter material, and rerun normalized counts.

## Known Gaps

- Chevron official annual-report PDFs were later downloaded successfully for the selected years 2013, 2018, 2020, 2021, 2022, 2023, and 2024 using the official Chevron annual-report PDF URL pattern. SEC filings remain as supporting annual-report coverage.
- NVIDIA annual-report / annual-review PDFs are now downloaded for 2011-2025 from the official Investor Relations / Q4 CDN archive. The selected NVIDIA set uses years with a clear letter address and Jensen Huang CEO/founder signature. NVIDIA 2016 is retained as background because its "Dear NVIDIANs and Stakeholders" section is not cleanly signed in the extracted letter section.
- No attached Amazon sample analysis file was present in the workspace; a standardization note was created instead.
- Forbes was downloaded as a requested secondary benchmark source; use only after verifying the relevant list/rankings at citation time.

## Next Recommended Steps

1. Manually inspect the selected source texts and mark exact letter boundaries.
2. Create cleaned selected-letter text files for all 28 company-years.
3. Rerun lexical counts on cleaned text only.
4. Build source cards with short, compliant quotations for qualitative analysis.
5. Draft the paper sections using the memos here as scaffolding.
