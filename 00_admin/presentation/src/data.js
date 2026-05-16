// Numeric facts referenced in the slides. Kept here so we can update once.

export const HEADLINE = {
  letters: 28,
  companies: 4,
  yearsCovered: '1997 – 2025',
  totalWords: 61318, // 27870+16443+8456+8549
}

export const COMPANY_SUMMARY = {
  Amazon:  { exploreShare: 0.68, customerShare: 0.93, longTermShare: 0.87, words: 27870,
             ipm: { lead: 3.4, horizon: 7.1, purpose: 13.0, options: 8.6, agile: 5.5 } },
  Nvidia:  { exploreShare: 0.65, customerShare: 0.83, longTermShare: 0.87, words: 16443,
             ipm: { lead: 1.4, horizon: 27.0, purpose: 3.9, options: 8.8, agile: 10.0 } },
  Shell:   { exploreShare: 0.11, customerShare: 0.38, longTermShare: 0.94, words: 8456,
             ipm: { lead: 6.1, horizon: 3.8, purpose: 10.3, options: 8.0, agile: 6.4 } },
  Chevron: { exploreShare: 0.27, customerShare: 0.30, longTermShare: 0.91, words: 8549,
             ipm: { lead: 3.0, horizon: 5.7, purpose: 10.8, options: 8.7, agile: 10.9 } },
}

export const AMAZON_TIMELINE = [
  { year: 1997, share: 0.54, era: 'Bezos founding',     label: 'Day-1 letter',          ceo: 'Bezos' },
  { year: 2016, share: 0.94, era: 'Peak Bezos',         label: '"We are inventors"',    ceo: 'Bezos' },
  { year: 2020, share: 0.50, era: 'Pandemic',           label: 'Safety + scale',         ceo: 'Bezos' },
  { year: 2021, share: 0.80, era: 'Bezos farewell',     label: 'Differentiation = survival', ceo: 'Bezos' },
  { year: 2022, share: 0.60, era: 'Jassy phase 1',      label: 'Cost discipline pivot',  ceo: 'Jassy' },
  { year: 2024, share: 0.76, era: 'Jassy phase 2',      label: 'AI re-exploration',      ceo: 'Jassy' },
  { year: 2025, share: 0.60, era: 'Jassy continuing',   label: 'AI as infrastructure',   ceo: 'Jassy' },
]

export const NVIDIA_TIMELINE = [
  { year: 2017, share: 0.82, dc: 0.83,  note: '"GPU computing has arrived"' },
  { year: 2018, share: 0.67, dc: 2.9,   note: 'AI + autonomous + cloud' },
  { year: 2020, share: 0.68, dc: 6.7,   note: 'Mellanox + scale' },
  { year: 2021, share: 0.86, dc: 10.6,  note: 'Peak exploratory' },
  { year: 2022, share: 0.65, dc: 15.0,  note: 'Crypto winter pause' },
  { year: 2023, share: 0.72, dc: 47.5,  note: 'Post-ChatGPT narrative' },
  { year: 2025, share: 0.36, dc: 115.2, note: 'Exploit flip — AI is infrastructure' },
]

export const SHELL_TIMELINE = [
  { year: 2014, share: 0.12 }, { year: 2015, share: 0.00 }, { year: 2016, share: 0.06 },
  { year: 2020, share: 0.10 }, { year: 2022, share: 0.17 }, { year: 2024, share: 0.10 },
  { year: 2025, share: 0.22 },
]

export const CHEVRON_TIMELINE = [
  { year: 2013, share: 0.31 }, { year: 2018, share: 0.26 }, { year: 2020, share: 0.25 },
  { year: 2021, share: 0.45 }, { year: 2022, share: 0.27 }, { year: 2023, share: 0.17 },
  { year: 2024, share: 0.15 },
]

export const HEADLINE_CONTRAST = [
  { lens: 'Explore share',                         Amazon: 0.68, Nvidia: 0.65, Shell: 0.11, Chevron: 0.27, fmt: 'share' },
  { lens: 'Customer share (vs. shareholder)',     Amazon: 0.93, Nvidia: 0.83, Shell: 0.38, Chevron: 0.30, fmt: 'share' },
  { lens: 'Long-term share',                       Amazon: 0.87, Nvidia: 0.87, Shell: 0.94, Chevron: 0.91, fmt: 'share' },
  { lens: 'Horizon Scanning / 1k',                 Amazon: 7.1,  Nvidia: 27.0, Shell: 3.8,  Chevron: 5.7,  fmt: 'rate' },
  { lens: 'Agile Execution / 1k',                  Amazon: 5.5,  Nvidia: 10.0, Shell: 6.4,  Chevron: 10.9, fmt: 'rate' },
  { lens: 'Strategic Leadership / 1k',             Amazon: 3.4,  Nvidia: 1.4,  Shell: 6.1,  Chevron: 3.0,  fmt: 'rate' },
]

// Canonical figures from 05_outputs/tables/quant_summary_by_company.csv
// (regenerated 2026-05-16). TECH = Amazon + NVIDIA, OIL = Shell + Chevron.
export const TECH = ['Amazon', 'Nvidia']
export const OIL = ['Shell', 'Chevron']

// 0–1 paired-lens shares. `right` is what a value near 1.0 means.
export const SPECTRA = {
  longTerm: {
    left: 'Short-term', right: 'Long-term',
    headline: 'All four are long-term.',
    takeaway: 'Long-term share sits at 0.84–0.89 for everyone. It is the wallpaper of CEO letters — it does not separate these strategies.',
    verdict: 'shared',
    values: { Amazon: 0.843, Nvidia: 0.836, Shell: 0.886, Chevron: 0.894 },
  },
  exploreExploit: {
    left: 'Exploit', right: 'Explore',
    headline: 'Tech explores. Oil exploits.',
    takeaway: 'Explore share splits cleanly by industry: tech at 0.65–0.68, energy at 0.11–0.27. A wide, empty gap in the middle.',
    verdict: 'split',
    values: { Amazon: 0.684, Nvidia: 0.645, Shell: 0.111, Chevron: 0.273 },
  },
  customerShareholder: {
    left: 'Shareholder-voiced', right: 'Customer-voiced',
    headline: 'Tech speaks to customers. Oil speaks to shareholders.',
    takeaway: 'Customer share: tech 0.69–0.93, energy 0.27–0.32. Survives the B2C/B2B objection — NVIDIA is B2B and still 0.69.',
    verdict: 'split',
    values: { Amazon: 0.931, Nvidia: 0.686, Shell: 0.323, Chevron: 0.268 },
  },
  options: {
    left: 'Low', right: 'High',
    headline: 'One common ground: strategic options.',
    takeaway: 'Strategic Options language is 6.6–8.3 /1k for all four — the one IPM theme where the industries converge. Everyone weighs choices the same; they just choose differently.',
    verdict: 'shared',
    // Normalised: Strategic Options /1k ÷ 10 so it maps onto the 0–1 track.
    values: { Amazon: 0.829, Nvidia: 0.803, Shell: 0.662, Chevron: 0.784 },
    rawLabel: { Amazon: '8.3', Nvidia: '8.0', Shell: '6.6', Chevron: '7.8' },
  },
}

// Per-1,000-word theme rates for the two "flip" bar charts.
export const FLIP = {
  horizon: {
    title: 'Horizon Scanning / 1k',
    headline: 'NVIDIA scans the future like nothing else.',
    takeaway: 'NVIDIA at 26.8 /1k — roughly 5× every other firm. Tech narrates discontinuity; energy is scanned for by commodity and regulatory cycles.',
    values: { Amazon: 4.84, Nvidia: 26.82, Shell: 3.67, Chevron: 5.50 },
  },
  leadership: {
    title: 'Strategic Leadership / 1k',
    headline: 'Oil performs leadership. Tech assumes it.',
    takeaway: 'The one theme that inverts: energy is thicker (Shell 2.25, Chevron 1.52) than tech (Amazon 1.04, NVIDIA 0.67). Slow physical businesses narrate leadership; fast ones let the product carry it.',
    values: { Amazon: 1.04, Nvidia: 0.67, Shell: 2.25, Chevron: 1.52 },
  },
}
