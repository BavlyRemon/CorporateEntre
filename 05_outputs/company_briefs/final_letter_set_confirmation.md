# Final Letter Set Confirmation

Corpus citation note: Letter evidence is cited to the extracted selected-letter files. Official source URLs, access dates, source titles, and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `00_admin/sources_master.csv`, and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

Access and analysis date: 2026-04-18.

This confirmation uses the previously extracted selected-letter corpus and the CEO-letter availability audit. The unit of analysis is the selected leadership-letter text, not the full annual report. The corpus contains 28 texts: seven per company. Source availability and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv` and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

| Company | Confirmed years | Analytical strength |
| --- | --- | --- |
| Amazon | 1997, 2016, 2020, 2021, 2022, 2024, 2025 | Founder-era Day 1 logic, late Bezos platform maturity, pandemic/CEO transition, and Jassy-era AI/platform reinvention. |
| Nvidia | 2017, 2018, 2020, 2021, 2022, 2023, 2025 | GPU-to-platform transition, AI data-center scaling, COVID/edge AI, post-boom supply/execution, and 2025 AI-infrastructure identity. |
| Shell | 2014, 2015, 2016, 2020, 2022, 2024, 2025 | Pre- and post-BG capital pressure, energy-transition reframing, pandemic strategic reset, and Wael Sawan's performance/disciplined-transition phase. |
| Chevron | 2013, 2018, 2020, 2021, 2022, 2023, 2024 | Watson-era operational excellence, Wirth transition, pandemic resilience, lower-carbon strategy, record cash returns, Hess/portfolio moves, and AI-energy adjacency. |

## Company Notes

### Amazon

The Amazon set is analytically strong because it spans the original 1997 shareholder-letter doctrine, a later Bezos-era scale/platform moment, the pandemic period, and Jassy's CEO-transition and AI-era reinvention letters. The 1997 letter establishes the enduring logic of customer obsession, long-term investment, bold choices, and willingness to trade short-term profitability for market leadership. The 2021 letter is especially valuable because it makes the mechanism of iterative invention explicit through fulfillment, AWS, devices, Prime Video, climate, and Kuiper examples. The 2025 letter is a high-value end point because it frames AI, robotics, satellite broadband, chips, and organizational speed as related inflections rather than isolated projects. Evidence: `02_extracted_text/selected_ceo_letters/amazon/amazon_1997_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2021_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2025_ceo_letter.txt`.

### Nvidia

The Nvidia set is analytically strong because it captures the shift from GPU computing as a distinctive platform to AI infrastructure as the company's central strategic identity. The 2017 and 2018 letters already frame NVIDIA as moving from chips to platforms and systems. The 2020-2023 letters show accelerated computing, cloud, edge AI, and data-center expansion becoming the core strategic narrative. The 2025 standalone CEO letter is the clearest mature statement of NVIDIA as a full-stack AI infrastructure company, with ecosystem partnerships, supply-chain execution, and AI factories at the center. Evidence: `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2017_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2020_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2025_ceo_letter.txt`.

### Shell

The Shell set is analytically strong because it captures the move from Ben van Beurden's post-oil-price/BG acquisition leadership period to pandemic-era Powering Progress and then Wael Sawan's sharper performance, discipline, simplification, and integrated-energy framing. Shell's format differs from Amazon and NVIDIA: these are official annual-report Chief Executive Officer review sections rather than standalone letter PDFs. They are still suitable for this design because they are signed/presented CEO strategic communications and are isolated from financial-report sections in the corpus. Evidence: `02_extracted_text/selected_ceo_letters/shell/shell_2015_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/shell/shell_2020_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/shell/shell_2025_ceo_letter.txt`.

### Chevron

The Chevron set is analytically strong because it spans operational-excellence continuity, a CEO transition from John Watson to Michael Wirth, pandemic and post-pandemic energy-market volatility, explicit lower-carbon framing, record cash-return years, and the 2024 link between energy security and AI/data-center demand. Chevron's selected texts are annual-report "To our stockholders" letters signed by the Chairman and Chief Executive Officer. They are leadership letters, not merely financial statements. Evidence: `02_extracted_text/selected_ceo_letters/chevron/chevron_2013_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2018_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2024_ceo_letter.txt`.

## Boundary Conditions

The set should remain intact unless the instructor requires standalone CEO-letter PDFs only. If that requirement is imposed, Shell would need a design note because the selected Shell corpus uses CEO-review sections. Chevron 2025 remains excluded because the official annual-report PDF was unavailable during the previous audit; the 2024 letter is therefore the most recent clean Chevron leadership letter in the current corpus.
