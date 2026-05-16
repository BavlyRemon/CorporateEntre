# Methodology Draft

Corpus citation note: Letter evidence is cited to the extracted selected-letter files. Official source URLs, access dates, source titles, and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `00_admin/sources_master.csv`, and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

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
