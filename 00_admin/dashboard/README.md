# CorpEntré Analysis Dashboard

React-based mission control for the corporate entrepreneurship research corpus.

## Quick start

```bash
cd 00_admin/dashboard

# 1 – Build the data (requires no dependencies)
python build_dashboard_data.py

# 2 – Install frontend dependencies (first time only)
npm install

# 3 – Start the dev server
npm run dev
# Opens at http://localhost:5173
```

## After editing source CSVs or markdown briefs

```bash
python build_dashboard_data.py   # regenerates src/data/dataset.json + briefs/*.md
# Vite hot-reloads automatically
```

## Pages

| Route | What you see |
|---|---|
| `/` | Overview: hero stats, company cards, radar, explore/exploit bar, nav map |
| `/letters` | 28 letter cards with filters; click any to open IPM radar + summary drawer |
| `/financials` | Per-company revenue/income/cashflow charts + raw financial tables |
| `/lexical` | IPM stacked bars · keyword heatmap · small-multiples trend lines |
| `/eras` | 12 strategic eras; explore-share bar chart; click years to open letter drawer |
| `/compare` | 4-company radar · explore/exploit scatter · comparative matrix · IPM matrix |
| `/hypotheses` | H1–H4 expandable cards + outcome anchors + IPM evidence table |
| `/briefs` | Full-text view of all 15 markdown briefs |

## Data sources

All data comes from `05_outputs/` — never recomputed, only visualised.
Run `build_milestone_analysis_package.py` first if the CSVs are stale.
