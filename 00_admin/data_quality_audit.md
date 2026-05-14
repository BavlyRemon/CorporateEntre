# Data Quality Audit — CEO-Letter Corpus

Audit date: 2026-05-10. Auditor: Claude Code (claude-opus-4-7).

## Issues Found

### 1. Chevron 2013 — CRITICAL: truncated extract with print artifacts

**File:** `02_extracted_text/selected_ceo_letters/chevron/chevron_2013_ceo_letter.txt`

**Problem:** The prior extract (source lines 94–202) started at the "To Our Stockholders" salutation and jumped immediately to the mid-letter paragraph "In downstream and chemicals…" The PDF text extractor placed the salutation (line 94 of the source) after the first two letter paragraphs (lines 59–93) due to the two-column page layout. As a result, the full opening of the letter — upstream results, resource additions, and the financial performance summary — was never included in the selected corpus. Word count was 570, vs. 1,000–1,600 for all peer Chevron years.

The extract also contained print-production artifacts on two lines immediately after the salutation: a four-color press bar (`CYAN MAGENTA YELLOW BLACK`) and an InDesign filename (`CVX_AR2013_v10.1_021614.indd 2 2/27/14 11:06 AM`). These were counted as body words.

**Fix applied:** Re-extracted from source lines 59–203. Paragraphs are reordered to reading sequence (salutation first, then missing opening paragraphs, then the remaining body which was already present). Print artifacts and page-break markers (e.g., `Chevron Corporation 2013 Annual Report 3`) removed. A duplicate pull-quote block at lines 204–207 of the source (copy of a sentence from the body) was excluded. Word count rises from 570 to 913.

---

### 2. NVIDIA 2017 — chart-label block and philanthropy sidebar counted as letter body

**File:** `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2017_ceo_letter.txt`

**Problem:** Lines 89–123 of the extract were chart axis labels from four performance infographics embedded in the annual-report layout (revenue bar chart, gross-margin chart, operating-margin chart, EPS chart). Example content: `$ 0 / $2 B / $4 B / $6 B / FY '17 / FY '16 / $6.9 B / +38% / REVENUE / 55% / 56% / …`. These added raw numeral/percentage tokens to the word count and created spurious hits on financial terms.

Lines 125–166 were NVIDIA Foundation philanthropy sidebar content describing volunteer events, Compute the Cure grants, and Project Inspire — not part of the strategic CEO letter prose. This text was separated from the letter's closing paragraph by the chart block.

**Fix applied:** Both blocks removed. Letter reads continuously from strategic body to closing paragraph ("NVIDIA is a learning machine…") and signature. Word count drops from 930 to 634.

---

### 3. NVIDIA 2025 — GTC marketing fragment and forward-looking statements legal block

**File:** `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2025_ceo_letter.txt`

**Problem (a):** Lines 12–66 of the extract began with a partial tagline fragment ("and creating the factories / that will power the next / wave of human progress.") — the second half of a headline whose first half was not captured in the source extraction range — followed by a GTC conference marketing section ("Woodstock of AI", "27,000 attendees", "100 countries", "more than 400 of the world's most promising startups") that is event-description copy rather than strategic letter prose.

**Problem (b):** Lines 850–895 were a Forward-Looking Statements legal block required by securities law, followed by an "NVIDIA Corporation / Notice of 2025 Annual Meeting / Proxy Statement and Form 10-K" header. This ~900-word legal disclaimer was being counted as letter body, inflating word counts and adding repetitive forward-looking language to theme counts.

**Fix applied:** Both blocks removed. The letter opens cleanly with "Dear NVIDIANs and Stakeholders," followed by "Financials and Strategic Positioning." The proxy-statement letter "Lightspeed Ahead" (lines 900–960 of original extract) is retained as a legitimate short CEO communication in the corpus. Word count drops from 3,862 to 2,905.

---

### 4. Shell 2014 — page headers/footers interleaved in letter body

**File:** `02_extracted_text/selected_ceo_letters/shell/shell_2014_ceo_letter.txt`

**Problem:** The annual-report PDF printed running page titles on every page. Lines 10–13 of the extract were the page-1 header block: `STRATEGIC REPORT 07 / SHELL ANNUAL REPORT AND FORM 20-F 2014 CHIEF EXECUTIVE OFFICER'S REVIEW / CHIEF EXECUTIVE OFFICER'S / REVIEW`. Lines 119–122 were the page-2 continuation header: `08 STRATEGIC REPORT / CHIEF EXECUTIVE OFFICER'S REVIEW SHELL ANNUAL REPORT AND FORM 20-F 2014 / CHIEF EXECUTIVE OFFICER'S REVIEW / CONTINUED`. These added "leadership", "strategic", and other terms to the body word count.

**Fix applied:** Both header/footer blocks removed. Word count drops from 1,262 to 1,221.

---

### 5. Shell 2025 — stranded running title and footnote definition blocks

**File:** `02_extracted_text/selected_ceo_letters/shell/shell_2025_ceo_letter.txt`

**Problem:** Line 54–55 of the extract contained a stranded mid-document running title: `Chief Executive / Officer's review` — a page-header element that appeared mid-paragraph due to PDF extraction column ordering. Lines 113–116 were footnote definitions (`[C] On a compound annual growth rate (CAGR) basis.` etc.) anchored by inline markers `[C]`, `[D]`, `[E]`, `[F]` scattered through the body. Both added non-prose tokens to the word count.

**Fix applied:** Running title removed; footnote definition block removed; inline markers `[C]`, `[D]`, `[E]`, `[F]` stripped from body text. Word count drops from 1,696 to 1,651.

---

### 6. Shell labeling — "CEO reviews" not "CEO letters"

**Problem:** Several briefs and script string literals referred to Shell's corpus as "CEO letters" or "letters" interchangeably with Amazon, Nvidia, and Chevron. Shell does not publish a standalone shareholder letter. The selected Shell texts are the signed "Chief Executive Officer's review" sections of Shell's Annual Report and Form 20-F. The manifest's `selected_text_type` column correctly recorded `annual-report CEO review` for all Shell rows, but the generated markdown outputs did not consistently reflect this.

**Fix applied:** `00_admin/build_milestone_analysis_package.py` updated to:
- Add a "Corpus format note — Shell" paragraph to the methodology draft making the CEO-review distinction explicit and explaining why it does not affect comparability.
- Update the milestone summary description to name Shell texts as "CEO reviews" explicitly.
- Update the methodology logic summary accordingly.

Shell sections in the `final_letter_set_confirmation.md` already correctly described the format; no change needed there.

---

### 7. Manifest `word_count` column was stale

**Problem:** The `word_count` column in `selected_ceo_letters_manifest.csv` reflected values entered at extraction time and had diverged from the script-computed counts in `05_outputs/tables/quant_summary_by_letter.csv` (off by 1–14 words per row for Amazon and Nvidia, and substantially off for the fixed Chevron/NVIDIA/Shell rows).

**Fix applied:** All 28 `word_count` values recomputed using the same `word_count(strip_header(text))` logic as `build_milestone_analysis_package.py` and written back to the manifest. The Chevron 2013 `source_line_range` was updated from `94-202` to `59-203 (reading order corrected)` and the notes field updated accordingly.

---

## Limitations Not Fixed

- **Shell 2016 body/heading ordering**: The manifest notes that the PDF extraction placed the CEO review heading after the signed body. The extract retains the content as-is. The content is present but may be in a non-standard order. Fixing this would require re-extraction from the source PDF, which is outside the scope of this pass.
- **NVIDIA 2017 closing section header**: Line 189 of the original extract (`GIVING BACK TO OUR COMMUNITIES SHAPING THE FUTURE`) is a layout section-divider that was retained. It contributes a small number of generic tokens but is not strategic content. Could be removed in a future pass.
- **General Shell boilerplate**: Shell 2015, 2020, 2022, and 2024 may have residual minor page-furniture elements. These were not systematically audited in this pass. Word counts for those years are unchanged.
- **Lexical-screen caveats**: Terms like "platform", "leadership", "growth", "resilience", and "safety" mean different things in tech vs. energy contexts. The quantitative counts are a structured lexical screen, not a substitute for interpretation. See `00_admin/method_notes.md` for the full scope guardrails.

## What to Rerun After This Audit

After this pass, the build pipeline should be rerun in order:

1. `python 00_admin/build_milestone_analysis_package.py` — regenerates all tables in `05_outputs/tables/` and all briefs.
2. `python 00_admin/build_integrated_paper_pdf.py` — refreshes the integrated draft PDF.
3. `python 00_admin/build_submission_ready_report_pdf.py` — refreshes the submission-ready PDF/DOCX and appendix CSVs.

Do **not** run `build_research_workspace.py` — it re-downloads raw sources and would overwrite the Chevron 2013 corrected extract.
