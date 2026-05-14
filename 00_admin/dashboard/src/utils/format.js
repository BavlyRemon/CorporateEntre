export const fmt1 = (v) => (typeof v === 'number' ? v.toFixed(1) : v ?? '—')
export const fmt2 = (v) => (typeof v === 'number' ? v.toFixed(2) : v ?? '—')
export const fmtPct = (v) => (typeof v === 'number' ? `${(v * 100).toFixed(1)}%` : v ?? '—')
export const fmtInt = (v) => (typeof v === 'number' ? Math.round(v).toLocaleString() : v ?? '—')
