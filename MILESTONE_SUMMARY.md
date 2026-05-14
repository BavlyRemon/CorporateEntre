# Milestone Summary

Corpus citation note: Letter evidence is cited to the extracted selected-letter files. Official source URLs, access dates, source titles, and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `00_admin/sources_master.csv`, and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

Analysis date: 2026-04-18.

## What Is Ready

This milestone package analyzes the confirmed 28-text corpus: seven CEO/shareholder leadership texts each for Amazon, Nvidia, and Chevron, and seven CEO reviews (Chief Executive Officer's review sections of the Shell Annual Report) for Shell. The corpus is stored in `02_extracted_text/selected_ceo_letters/`, with a machine-readable manifest at `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`.

## Final Letter Set

| Company | Confirmed years | Analytical strength |
| --- | --- | --- |
| Amazon | 1997, 2016, 2020, 2021, 2022, 2024, 2025 | Founder-era Day 1 logic, late Bezos platform maturity, pandemic/CEO transition, and Jassy-era AI/platform reinvention. |
| Nvidia | 2017, 2018, 2020, 2021, 2022, 2023, 2025 | GPU-to-platform transition, AI data-center scaling, COVID/edge AI, post-boom supply/execution, and 2025 AI-infrastructure identity. |
| Shell | 2014, 2015, 2016, 2020, 2022, 2024, 2025 | Pre- and post-BG capital pressure, energy-transition reframing, pandemic strategic reset, and Wael Sawan's performance/disciplined-transition phase. |
| Chevron | 2013, 2018, 2020, 2021, 2022, 2023, 2024 | Watson-era operational excellence, Wirth transition, pandemic resilience, lower-carbon strategy, record cash returns, Hess/portfolio moves, and AI-energy adjacency. |

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
