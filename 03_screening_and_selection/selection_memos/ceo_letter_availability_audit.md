# CEO Letter Availability Audit

Access/audit date: 2026-04-18.

This audit checks the selected seven-year corpus for actual CEO/shareholder/chair letter availability, not merely annual-report availability. A report-year is treated as selected only when the source contains a standalone shareholder letter or an official annual-report leadership-letter section such as a CEO review, Chair message, or To our stockholders letter.

## Bottom Line

- Confirmed selected corpus: 28 company-years, seven per company.
- Amazon: all seven are official standalone shareholder-letter pages signed by Jeff Bezos or Andy Jassy.
- NVIDIA: all seven selected years now have a clean Dear NVIDIANs / stakeholder letter signed by Jensen Huang as CEO and Founder. NVIDIA 2016 was removed from the selected set because its letter section is not cleanly signed in the extracted text.
- Shell: all seven use official annual-report Chair message / Chief Executive Officer review sections. These are official leadership-letter sections, not standalone letter PDFs.
- Chevron: all seven use official annual-report To our stockholders letters signed by John Watson or Michael Wirth. Chevron 2025 is not selected because the official annual-report PDF returned HTTP 503 during the audit.

## Selected Corpus Audit Table

| Company | Year | Selected text type | Status | Evidence |
|---|---:|---|---|---|
| Amazon | 1997 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 1: To our shareholders: ; CEO signature: line 45: Jeffrey P. Bezos ; CEO title: line 46: Founder and Chief Executive Officer |
| Amazon | 2016 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | letter closing: line 64: Sincerely, ; CEO signature: line 65: Jeff ; CEO title: line 67: Founder and Chief Executive Officer |
| Amazon | 2020 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 78: To our shareholders: ; CEO signature: line 120: Jeffrey P. Bezos ; CEO title: line 121: Founder and Chief Executive Officer |
| Amazon | 2021 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 1: Dear shareholders: ; CEO signature: line 77: Andy Jassy ; CEO title: line 78: President and Chief Executive Officer |
| Amazon | 2022 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 1: Dear shareholders: ; CEO signature: line 59: Andy Jassy ; CEO title: line 60: President and Chief Executive Officer |
| Amazon | 2024 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 1: Dear Shareholders: ; CEO signature: line 103: Andy Jassy ; CEO title: line 104: President and Chief Executive Officer |
| Amazon | 2025 | standalone shareholder letter HTML | Confirmed CEO/shareholder letter available | shareholder greeting: line 1: Dear Shareholders: ; CEO signature: line 76: Andy Jassy ; CEO title: line 77: President and Chief Executive Officer |
| Nvidia | 2017 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 173: DEAR NVIDIANS AND STAKEHOLDERS, ; CEO signature: line 354: Jensen Huang ; CEO title: line 355: CEO and Founder, NVIDIA |
| Nvidia | 2018 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 155: DEAR NVIDIANS AND STAKEHOLDERS, ; CEO signature: line 421: Jensen Huang ; CEO title: line 422: CEO and Founder, NVIDIA |
| Nvidia | 2020 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 114: DEAR NVIDIANS ; CEO signature: line 632: Jensen Huang ; CEO title: line 633: CEO and Founder, NVIDIA |
| Nvidia | 2021 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 257: DEAR NVIDIANS ; CEO signature: line 732: Jensen Huang ; CEO title: line 733: CEO and Founder, NVIDIA |
| Nvidia | 2022 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 220: DEAR NVIDIANS ; CEO signature: line 585: Jensen Huang ; CEO title: line 586: CEO and Founder, NVIDIA |
| Nvidia | 2023 | annual-report CEO letter | Confirmed CEO/shareholder letter available | letter greeting: line 238: Dear NVIDIANs ; CEO signature: line 675: Jensen Huang ; CEO title: line 676: CEO and Founder, NVIDIA |
| Nvidia | 2025 | standalone CEO-letter PDF | Confirmed CEO/shareholder letter available | letter greeting: line 240: Dear NVIDIANs ; CEO signature: line 1191: Jensen Huang ; CEO title: line 1192: CEO and Founder, NVIDIA |
| Shell | 2014 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 15: 07 Chief Executive Officer’s review ; CEO name: line 640: Ben van Beurden ; CEO title: line 641: Chief Executive Officer |
| Shell | 2015 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 621: SHELL ANNUAL REPORT AND FORM 20-F 2015 CHIEF EXECUTIVE OFFICER’S REVIEW ; CEO name: line 700: Ben van Beurden ; CEO title: line 701: Chief Executive Officer |
| Shell | 2016 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 15: 07 Chief Executive Officer’s review ; CEO name: line 593: Ben van Beurden ; CEO title: line 594: Chief Executive Officer |
| Shell | 2020 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 18: 6 Chief Executive Officer’s review ; CEO name: line 590: BEN VAN BEURDEN ; CEO title: line 591: Chief Executive Officer |
| Shell | 2022 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 17: 4 Chief Executive Officer's review ; CEO name: line 678: Wael Sawan ; CEO title: line 679: Chief Executive Officer |
| Shell | 2024 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 29: 4 Chief Executive Officer's review ; CEO name: line 594: Wael Sawan ; CEO title: line 595: Chief Executive Officer |
| Shell | 2025 | annual-report CEO/chair section | Confirmed CEO/shareholder letter available | CEO review section: line 10: 4 Chief Executive Officer's review ; CEO name: line 614: Wael Sawan ; CEO title: line 615: Chief Executive Officer |
| Chevron | 2013 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 94: To Our Stockholders ; CEO signature: line 200: John S. Watson ; CEO title: lines 201-202: Chairman of the Board and Chief Executive Officer |
| Chevron | 2018 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 124: to our stockholders ; CEO signature: line 319: Michael K. Wirth ; CEO title: line 320: Chairman of the Board and Chief Executive Officer |
| Chevron | 2020 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 151: To our stockholders: ; CEO signature: line 366: Michael K. Wirth ; CEO title: line 367: Chairman of the Board and Chief Executive Ofcer |
| Chevron | 2021 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 51: to our stockholders IV ; CEO signature: line 350: Michael K. Wirth ; CEO title: line 352: and Chief Executive Officer |
| Chevron | 2022 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 83: to our stockholders ; CEO signature: line 286: Michael K. Wirth ; CEO title: line 288: and Chief Executive Officer |
| Chevron | 2023 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 100: to our stockholders ; CEO signature: line 255: Michael K. Wirth ; CEO title: line 257: and Chief Executive Officer |
| Chevron | 2024 | annual-report stockholder letter | Confirmed CEO/shareholder letter available | stockholder letter heading: line 110: to our stockholders ; CEO signature: line 300: Michael K. Wirth ; CEO title: line 302: and Chief Executive Officer |

## Important Boundary Notes

- For the final quantitative pass, do not count the whole PDF for NVIDIA, Shell, or Chevron. Extract only the letter/review section before running lexical counts.
- Shell is acceptable only if the research design allows official CEO review / Chair message sections as CEO-letter equivalents. If the instructor requires standalone CEO-letter PDFs only, Shell will need additional source links or the design should explicitly call these annual-report leadership letters.
- NVIDIA 2016 should remain background, not selected, unless a clean official signed CEO-letter version is found.
- Chevron 2025 should remain background/follow-up until the official annual-report PDF with the stockholder letter is accessible.

## Source Ledger

The machine-readable audit table is saved at `03_screening_and_selection/letter_selection_tables/ceo_letter_availability_audit.csv`. Source metadata remains in `00_admin/sources_master.csv` and `06_appendices/download_manifest/download_manifest.csv`.
