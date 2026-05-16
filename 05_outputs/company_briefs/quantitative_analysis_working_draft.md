# Quantitative Analysis Working Draft

Corpus citation note: Letter evidence is cited to the extracted selected-letter files. Official source URLs, access dates, source titles, and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `00_admin/sources_master.csv`, and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

Analysis date: 2026-04-18. Counts are strict lexical counts from the selected letter bodies only. Extraction metadata headers were excluded before counting.

## Company-Level IPM Pattern

| Company | Words | Leadership/1k | Horizon/1k | Purpose/1k | Options/1k | Execution/1k | Dominant IPM theme |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Amazon | 27870 | 1.7 | 13.4 | 13.2 | 8.3 | 5.3 | Horizon Scanning / Sense-making |
| Nvidia | 16443 | 0.7 | 49.4 | 3.5 | 8.0 | 9.6 | Horizon Scanning / Sense-making |
| Shell | 8456 | 2.6 | 12.3 | 8.5 | 7.3 | 3.3 | Horizon Scanning / Sense-making |
| Chevron | 8549 | 1.6 | 16.0 | 14.0 | 8.9 | 6.4 | Horizon Scanning / Sense-making |

## Cross-Cutting Pair Pattern

Shares below represent the first term as a share of the paired total. For example, Explore share = explore / (explore + exploit). These are interpretive indicators, not final findings.

| Company | Explore share | Customer share | Long-term share | Entrepreneurial share | Internal innovation share | Risk/challenge share |
| --- | --- | --- | --- | --- | --- | --- |
| Amazon | 0.687 | 0.936 | 0.840 | 0.576 | 0.908 | 0.288 |
| Nvidia | 0.640 | 0.694 | 0.838 | 0.407 | 0.810 | 0.261 |
| Shell | 0.090 | 0.323 | 0.896 | 0.030 | 0.458 | 0.148 |
| Chevron | 0.253 | 0.268 | 0.891 | 0.046 | 0.438 | 0.212 |

## Interpretation

Amazon shows the clearest customer-purpose and strategic-options profile. This is consistent with the text of the 1997 letter, which makes customer focus, long-term market leadership, and bold investment decisions the central doctrine, and the 2021 and 2025 letters, which describe iterative invention, multiple paths, and AI-era reinvention as leadership mechanisms. Evidence: `02_extracted_text/selected_ceo_letters/amazon/amazon_1997_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2021_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2025_ceo_letter.txt`.

Nvidia shows the strongest technology-horizon and strategic-options profile. The 2017 letter describes GPU computing as arriving across gaming, VR, AI, and self-driving cars, while the 2025 letter explicitly reframes NVIDIA as a full-stack AI infrastructure company. That combination explains why AI, platform, ecosystem, engineering, and infrastructure language is intense in the Nvidia corpus. Evidence: `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2017_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2025_ceo_letter.txt`.

The explore/exploit pair should be read more conservatively than the IPM horizon and options themes. Nvidia's strict explore share is low because the pair dictionary counts words such as "experiment," "pilot," and "discovery," while much of Nvidia's exploratory posture is expressed through specific technology-horizon terms such as AI, GPU, accelerated computing, Blackwell, inference, and AI factories. Amazon has a similar, though less extreme, issue when AI, AWS capacity, chips, and robotics function as exploration signals but are counted under horizon scanning or execution rather than the explore pair. This is why the qualitative interpretation weighs the IPM counts and close reading alongside the paired ratio.

Shell's counts are shaped by transition, governance, value, customer, and capital-allocation language. The 2020 review is especially dense because it joins pandemic resilience, net-zero strategy, customer-led low-carbon markets, and strategic relationships. The 2025 review shifts toward performance, discipline, simplification, LNG, upstream strength, and lower-carbon platforms only where policy and customer demand create attractive business models. Evidence: `02_extracted_text/selected_ceo_letters/shell/shell_2020_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/shell/shell_2025_ceo_letter.txt`.

Chevron's quantitative pattern is the most exploitative and execution-oriented, but not innovation-free. Its letters repeatedly connect energy demand, operational excellence, safety, capital discipline, shareholder returns, and lower-carbon investments. The 2018 letter introduces the Future Energy Fund and OGCI investment; the 2024 letter connects technology, lower-carbon projects, partnerships, and AI/data-center power demand to the existing asset base. Evidence: `02_extracted_text/selected_ceo_letters/chevron/chevron_2018_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2024_ceo_letter.txt`.

## Dictionary Cautions

The strict dictionary improves comparability but still requires manual interpretation. "Return" can mean shareholder return or a return to conditions. "Platform" is noisy across industries. "AI" is straightforward in Amazon and Nvidia but appears in energy letters as a demand driver or contextual force, not always as internal innovation. "Safety" is exploitative in the operational sense, but in energy it is also part of governance and legitimacy. The qualitative briefs therefore treat the quantitative results as a map of emphasis rather than a substitute for reading.

## Generated Tables

- `05_outputs/tables/quant_summary_by_company.csv`
- `05_outputs/tables/quant_summary_by_letter.csv`
- `05_outputs/tables/theme_counts_normalized.csv`
- `05_outputs/tables/explore_exploit_ratios.csv`
- `05_outputs/tables/ipm_comparison_matrix.csv`
- `05_outputs/tables/comparative_matrix.csv`
