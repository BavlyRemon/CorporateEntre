# Methodology Working Brief

This phase prepares a corpus of official CEO/shareholder letters and annual reports for a comparative Corporate Entrepreneurship and Innovation analysis. CEO/shareholder letters are useful because they are public, recurring strategic texts in which top leaders explain priorities, tradeoffs, investment logic, stakeholder orientation, and interpretation of the external environment. They are especially relevant to strategic leadership, horizon scanning, purpose/vision/governance, option selection, and execution language.

The strength of the method is comparability over time: each company can be read across multiple strategic eras. The limitation is that letters are polished investor-facing narratives. They may understate conflict, failed experiments, organizational inertia, or political constraints. For that reason, lexical analysis should be paired with qualitative interpretation and external context.

The selected years were chosen for strategic inflection value rather than equal spacing. Each company now contributes seven years that represent baseline logic, scaling or portfolio transition, crisis/disruption, integration or recalibration, and mature renewal. Where standalone CEO letters are unavailable, the closest official equivalent is used and flagged in sources_master.csv.

The seven-letter set is not intended to be a full corporate history. This matters most for Shell and Chevron because both companies have older reports that could support a longer historical study. Older Shell years such as 2005 and 2010 and older Chevron years such as 2001/2002, 2005, 2008/2010, and 2011/2012 are treated as archival robustness candidates. They were not selected for the main corpus because the paper prioritizes comparable contemporary strategic-renewal episodes: portfolio renewal, integration, energy-transition pressure, crisis response, capital discipline, acquisition options, and mature execution under investor/regulatory scrutiny.

Lexical analysis is useful because it creates a disciplined first pass over strategic emphasis: e.g., customer vs shareholder language, explore vs exploit language, partnership/acquisition/internal invention language, and agility/execution language. It is insufficient alone because dictionary terms are ambiguous and industry-specific. The final paper should therefore report counts, then interpret passages manually.

Unit of analysis: one selected company-year strategic text, for a total selected corpus of 28 company-years. For Amazon this is usually a standalone shareholder letter. For NVIDIA, Shell, and Chevron it may be an annual report or report section where the CEO/chair strategic narrative appears. For Shell, the selected source should be the Chair's message and/or Chief Executive Officer's review section within the official annual report. For Chevron, the selected source should be the "to our stockholders" letter in the official Chevron annual report, not the SEC 10-K extract.

Reproducibility: all available source files, extracted text, source metadata, access dates, and selection rationales are stored in this workspace. Missing or blocked official sources are documented rather than fabricated.


## Source Notes
- [AMZN-Letters] Amazon shareholder letters archive. Accessed 2026-04-16. https://www.aboutamazon.com/about-us/shareholder-letters
- [NVDA-IR] NVIDIA Annual Reports and Proxies. Accessed 2026-04-16. https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx
- [Shell-Archive] Shell annual reports archive. Accessed 2026-04-16. https://www.shell.com/investors/results-and-reporting/annual-report-archive.html
- [CVX-AR] Chevron annual-report PDFs for selected years. Accessed 2026-04-16. https://www.chevron.com/annual-report
- [CVX-SEC] Chevron SEC annual filings. Accessed 2026-04-16. https://www.sec.gov/edgar/browse/?CIK=93410
- [WIPO-GII-2025] WIPO Global Innovation Index 2025 - Global Innovation Tracker. Accessed 2026-04-16. https://www.wipo.int/web-publications/global-innovation-index-2025/en/global-innovation-tracker.html
