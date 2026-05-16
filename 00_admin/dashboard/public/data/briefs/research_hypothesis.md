# Research Hypothesis

Corpus citation note: Letter evidence is cited to the extracted selected-letter files. Official source URLs, access dates, source titles, and extraction boundaries are documented in `02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv`, `00_admin/sources_master.csv`, and `03_screening_and_selection/selection_memos/ceo_letter_availability_audit.md`.

## Main Hypothesis

Across the 28 selected CEO/shareholder letters, technology-platform firms will use more explicit exploratory and option-creation language than oil-and-gas firms, while oil-and-gas firms will frame innovation more strongly through exploitation, operational discipline, safety, capital allocation, resilience, and regulated transition. However, the difference will not be a simple "tech explores / energy exploits" split: the strongest firms in both industries will display ambidextrous leadership by linking exploratory bets to existing capabilities, cash generation, ecosystem relationships, and long-term strategic renewal.

This hypothesis is testable through normalized lexical counts for Innovation Process Model themes and cross-cutting pairs, then through qualitative interpretation of how the words are used in context. The relevant evidence base is the 28-letter selected corpus and the quantitative tables generated from it.

## Supporting Sub-Hypotheses

### H1: Customer and Ecosystem Orientation

Amazon and Nvidia will show stronger customer/ecosystem language than Shell and Chevron because their innovation models depend heavily on platform adoption, developer/customer use cases, and networked complements. Amazon's 1997 and 2021 letters repeatedly justify investment by customer value and working backwards from customer experience; Nvidia's 2017 and 2025 letters frame its platform as serving AI developers, enterprises, partners, and countries. Evidence: `02_extracted_text/selected_ceo_letters/amazon/amazon_1997_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2021_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2017_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2025_ceo_letter.txt`.

### H2: Exploit-to-Explore Funding Logic

Shell and Chevron will use more exploitative language because energy innovation is constrained by asset lives, safety, commodity cycles, regulatory conditions, and capital intensity. Yet their letters should still show exploration when it is attached to advantaged assets, partnerships, lower-carbon technologies, or portfolio options. Shell's 2020 and 2025 reviews explicitly connect lower-carbon investment to cash flow, customer demand, policy, and capital discipline; Chevron's 2018, 2022, and 2024 letters connect lower-carbon and technology initiatives to operational excellence, partnerships, and returns. Evidence: `02_extracted_text/selected_ceo_letters/shell/shell_2020_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/shell/shell_2025_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2018_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2022_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2024_ceo_letter.txt`.

### H3: Long-Termism Differs by Industry

All four firms will use long-term language, but the meaning will differ. In technology, long-termism will justify experimentation, platform expansion, and willingness to endure near-term investment pressure. In energy, long-termism will justify durable assets, energy demand, safety, policy stability, balance-sheet strength, and transition pacing. Evidence: `02_extracted_text/selected_ceo_letters/amazon/amazon_1997_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/amazon/amazon_2025_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/nvidia/nvidia_2025_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/shell/shell_2025_ceo_letter.txt`, `02_extracted_text/selected_ceo_letters/chevron/chevron_2024_ceo_letter.txt`.

### H4: Innovation Process Model Emphasis

The dominant Innovation Process Model dimensions will differ by firm: Amazon should be strongest in purpose/customer vision and strategic options; Nvidia in horizon scanning and strategic options; Shell in purpose/governance plus horizon scanning around transition; and Chevron in purpose/governance plus agile execution/operational excellence. This is tested in `05_outputs/tables/ipm_comparison_matrix.csv` and interpreted in `05_outputs/company_briefs/innovation_process_model_analysis.md`.
