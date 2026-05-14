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
