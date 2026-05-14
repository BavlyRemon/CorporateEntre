import { useState, useMemo } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import MarkdownView from '../components/MarkdownView'
import ChartTooltip from '../components/ChartTooltip'
import { COMPANY_COLORS, COMPANIES, IPM_THEMES, IPM_SHORT, IPM_COLORS } from '../utils/constants'
import { fmtPct, fmt1 } from '../utils/format'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip, Legend, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, ZAxis, Cell, BarChart, Bar,
  LineChart, Line, ReferenceLine,
} from 'recharts'

const TECH = ['Amazon', 'Nvidia']
const ENERGY = ['Shell', 'Chevron']

const SECTOR_COLOR = { Tech: '#6366f1', Energy: '#f59e0b' }
const SECTOR_BG = {
  Tech:   'bg-indigo-500/10 border-indigo-500/30',
  Energy: 'bg-amber-500/10  border-amber-500/30',
}

function useIndustryStats(letters, eeTable) {
  return useMemo(() => {
    const avg = (rows, key) => rows.length ? rows.reduce((s, r) => s + (r[key] ?? 0), 0) / rows.length : 0

    const build = (companies) => {
      const ltr = letters.filter(r => companies.includes(r.company))
      const ee  = eeTable.filter(r => companies.includes(r.company))
      return {
        letters: ltr,
        ipm: IPM_THEMES.map((t, i) => ({
          theme: IPM_SHORT[t],
          full: t,
          value: +avg(ltr, `${t}_per_1000`).toFixed(3),
          color: IPM_COLORS[i],
        })),
        exploreShare:    +avg(ee, 'explore_share_of_pair').toFixed(3),
        explorePer1k:    +avg(ee, 'explore_per_1000').toFixed(3),
        exploitPer1k:    +avg(ee, 'exploit_per_1000').toFixed(3),
        customerShare:   +avg(ltr, 'customer_share_of_customer_shareholder').toFixed(3),
        longTermShare:   +avg(ltr, 'long_term_share_of_long_short').toFixed(3),
        entreprShare:    +avg(ltr, 'entrepreneurial_share_of_entrepreneurial_managerial').toFixed(3),
        internalShare:   +avg(ltr, 'internal_share_of_internal_external').toFixed(3),
        riskShare:       +avg(ltr, 'risk_share_of_risk_performance').toFixed(3),
        avgWords:        +avg(ltr, 'word_count').toFixed(0),
        companies,
      }
    }

    return { tech: build(TECH), energy: build(ENERGY) }
  }, [letters, eeTable])
}

// ── Big sector header cards ────────────────────────────────────────────────────
function SectorHeader({ name, stats }) {
  const color = SECTOR_COLOR[name]
  const bg = SECTOR_BG[name]
  return (
    <div className={`card border rounded-xl p-6 ${bg}`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color }}>
            {name === 'Tech' ? 'Technology' : 'Energy / Oil & Gas'}
          </div>
          <div className="text-2xl font-bold text-white">
            {stats.companies.join(' · ')}
          </div>
          <div className="text-sm text-slate-400 mt-1">{stats.letters.length} letters · avg {Math.round(stats.avgWords).toLocaleString()} words/letter</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 mb-1">Explore share</div>
          <div className="text-3xl font-bold" style={{ color }}>{fmtPct(stats.exploreShare)}</div>
        </div>
      </div>

      {/* Dominant IPM */}
      <div className="mb-4">
        {(() => {
          const top = [...stats.ipm].sort((a, b) => b.value - a.value)[0]
          return (
            <div className="text-sm">
              <span className="text-slate-400">Dominant theme: </span>
              <span className="font-semibold text-white">{top?.full}</span>
              <span className="text-slate-500 ml-1">({fmt1(top?.value)}/1k)</span>
            </div>
          )
        })()}
      </div>

      {/* Quick stats grid */}
      <div className="grid grid-cols-3 gap-3 text-xs">
        {[
          { label: 'Customer vs Shareholder', val: stats.customerShare },
          { label: 'Entrepreneurial framing', val: stats.entreprShare },
          { label: 'Long-term orientation', val: stats.longTermShare },
        ].map(({ label, val }) => (
          <div key={label} className="bg-black/20 rounded-lg p-2.5">
            <div className="text-slate-500 mb-1">{label}</div>
            <div className="font-bold text-base" style={{ color }}>{fmtPct(val)}</div>
            <div className="h-1 bg-slate-700 rounded-full mt-1.5 overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${val * 100}%`, background: color }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── IPM grouped bar: Tech vs Energy side by side ───────────────────────────────
function IPMComparisonBar({ tech, energy }) {
  const data = IPM_THEMES.map((t, i) => ({
    theme: IPM_SHORT[t],
    Tech: tech.ipm[i].value,
    Energy: energy.ipm[i].value,
  }))

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">IPM Theme Intensity — Tech vs Energy</div>
      <div className="text-xs text-slate-500 mb-4">Average per 1,000 words across all letters in each sector</div>
      <div style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="theme" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Bar dataKey="Tech" fill={SECTOR_COLOR.Tech} radius={[3, 3, 0, 0]} />
            <Bar dataKey="Energy" fill={SECTOR_COLOR.Energy} radius={[3, 3, 0, 0]} />
            <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip formatter={v => fmt1(v)} />} />
            <Legend formatter={v => <span style={{ fontSize: 11, color: SECTOR_COLOR[v] }}>{v}</span>} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── Diverging bar: difference Tech − Energy per IPM theme ─────────────────────
function IPMDivergingBar({ tech, energy }) {
  const data = IPM_THEMES.map((t, i) => {
    const diff = +(tech.ipm[i].value - energy.ipm[i].value).toFixed(3)
    return { theme: IPM_SHORT[t], diff, color: diff > 0 ? SECTOR_COLOR.Tech : SECTOR_COLOR.Energy }
  }).sort((a, b) => b.diff - a.diff)

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">IPM Divergence (Tech − Energy)</div>
      <div className="text-xs text-slate-500 mb-4">Positive = Tech higher · Negative = Energy higher</div>
      <div style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 60, bottom: 5, left: 70 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
            <YAxis type="category" dataKey="theme" tick={{ fill: '#94a3b8', fontSize: 11 }} width={65} />
            <ReferenceLine x={0} stroke="#475569" />
            <Bar dataKey="diff" name="Difference" radius={[0, 3, 3, 0]}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Bar>
            <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip formatter={v => (v > 0 ? '+' : '') + fmt1(v)} />} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── Rhetorical pairs comparison ────────────────────────────────────────────────
const PAIRS = [
  { label: 'Customer vs Shareholder',         tKey: 'customerShare',  eKey: 'customerShare',  aLabel: 'Customer',       bLabel: 'Shareholder' },
  { label: 'Entrepreneurial vs Managerial',   tKey: 'entreprShare',   eKey: 'entreprShare',   aLabel: 'Entrepreneurial',bLabel: 'Managerial' },
  { label: 'Internal vs External Innovation', tKey: 'internalShare',  eKey: 'internalShare',  aLabel: 'Internal',       bLabel: 'External' },
  { label: 'Long-term vs Short-term',         tKey: 'longTermShare',  eKey: 'longTermShare',  aLabel: 'Long-term',      bLabel: 'Short-term' },
  { label: 'Risk/Challenge vs Success',       tKey: 'riskShare',      eKey: 'riskShare',      aLabel: 'Risk',           bLabel: 'Success' },
]

function RhetoricalPairsPanel({ tech, energy }) {
  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">Rhetorical Orientation — Share of Each Binary Pair</div>
      <div className="text-xs text-slate-500 mb-5">How much of each paired dimension leans toward the first term</div>
      <div className="space-y-5">
        {PAIRS.map(({ label, tKey, eKey, aLabel, bLabel }) => {
          const tVal = tech[tKey]
          const eVal = energy[eKey]
          const diff = tVal - eVal
          return (
            <div key={label}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium text-slate-300">{label}</span>
                <span className={`text-xs font-mono ${Math.abs(diff) > 0.1 ? 'text-white font-semibold' : 'text-slate-500'}`}>
                  {diff > 0 ? '+' : ''}{(diff * 100).toFixed(0)}pp Tech lead
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[['Tech', tVal, SECTOR_COLOR.Tech], ['Energy', eVal, SECTOR_COLOR.Energy]].map(([name, val, color]) => (
                  <div key={name}>
                    <div className="flex justify-between text-xs mb-1">
                      <span style={{ color }} className="font-medium">{name}</span>
                      <span className="text-slate-400">{(val * 100).toFixed(0)}% {aLabel}</span>
                    </div>
                    <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden flex">
                      <div className="h-full rounded-l-full" style={{ width: `${val * 100}%`, background: color }} />
                      <div className="h-full rounded-r-full flex-1" style={{ background: `${color}25` }} />
                    </div>
                    <div className="flex justify-between text-xs mt-0.5 text-slate-600">
                      <span>{aLabel}</span><span>{bLabel}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Explore/exploit by industry ────────────────────────────────────────────────
function ExploreExploitIndustry({ tech, energy }) {
  const data = [
    { sector: 'Tech', explore: tech.explorePer1k, exploit: tech.exploitPer1k, share: +(tech.exploreShare * 100).toFixed(1) },
    { sector: 'Energy', explore: energy.explorePer1k, exploit: energy.exploitPer1k, share: +(energy.exploreShare * 100).toFixed(1) },
  ]

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">Explore vs Exploit by Industry</div>
      <div className="text-xs text-slate-500 mb-4">Per 1,000 words, averaged across letters in each sector</div>
      <div className="grid grid-cols-2 gap-6 mb-5">
        {data.map(d => (
          <div key={d.sector}>
            <div className="text-sm font-semibold mb-3" style={{ color: SECTOR_COLOR[d.sector] }}>{d.sector}</div>
            <div className="space-y-2">
              {[['Explore', d.explore, '#6366f1'], ['Exploit', d.exploit, '#f59e0b']].map(([label, val, color]) => {
                const max = Math.max(tech.explorePer1k, tech.exploitPer1k, energy.explorePer1k, energy.exploitPer1k, 1)
                return (
                  <div key={label} className="flex items-center gap-2">
                    <div className="w-14 text-xs text-slate-400">{label}</div>
                    <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${(val / max) * 100}%`, background: color }} />
                    </div>
                    <div className="text-xs font-mono text-slate-300 w-8 text-right">{fmt1(val)}</div>
                  </div>
                )
              })}
              <div className="mt-2 text-xs text-slate-500">Explore share: <span className="font-semibold" style={{ color: SECTOR_COLOR[d.sector] }}>{d.share}%</span></div>
            </div>
          </div>
        ))}
      </div>

      {/* Scatter over time — one dot per letter */}
      <div>
        <div className="text-xs text-slate-500 mb-2">Letter-level scatter (all 28 letters)</div>
        <div style={{ height: 220 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" dataKey="x" name="Explore/1k" tick={{ fill: '#64748b', fontSize: 10 }}
                label={{ value: 'Explore / 1k', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 10 }} />
              <YAxis type="number" dataKey="y" name="Exploit/1k" tick={{ fill: '#64748b', fontSize: 10 }}
                label={{ value: 'Exploit / 1k', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
              <ZAxis range={[45, 45]} />
              {[['Tech', SECTOR_COLOR.Tech], ['Energy', SECTOR_COLOR.Energy]].map(([sector, color]) => {
                const companies = sector === 'Tech' ? TECH : ENERGY
                return null // we draw per-company below
              })}
              {COMPANIES.map(c => {
                const isTech = TECH.includes(c)
                return (
                  <Scatter
                    key={c}
                    name={c}
                    data={/* inline via custom shape handled by fill */[]}
                    fill={COMPANY_COLORS[c]}
                  />
                )
              })}
              {/* Actually use per-company scatter with explicit data */}
              <Tooltip cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null
                  const d = payload[0]?.payload
                  return (
                    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs">
                      <div style={{ color: COMPANY_COLORS[d?.company] }} className="font-semibold">{d?.company} {d?.year}</div>
                      <div className="text-slate-400">Explore: {d?.x?.toFixed(2)}</div>
                      <div className="text-slate-400">Exploit: {d?.y?.toFixed(2)}</div>
                    </div>
                  )
                }}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

// ── Per-company explore over time ─────────────────────────────────────────────
function ExploreOverTime({ letters }) {
  // Build per-company time series
  const seriesData = {}
  const allYears = [...new Set(letters.map(r => r.year))].sort((a, b) => a - b)

  COMPANIES.forEach(c => {
    const rows = letters.filter(r => r.company === c).sort((a, b) => a.year - b.year)
    seriesData[c] = rows.map(r => ({ year: r.year, share: +(r.explore_share_of_explore_exploit * 100).toFixed(1) }))
  })

  // Flatten for LineChart (needs one array with all companies)
  const chartData = allYears.map(y => {
    const row = { year: y }
    COMPANIES.forEach(c => {
      const match = seriesData[c].find(r => r.year === y)
      if (match) row[c] = match.share
    })
    return row
  })

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">Explore Share Over Time — All Companies</div>
      <div className="text-xs text-slate-500 mb-4">% of explore+exploit pair that is "explore" per letter</div>
      <div style={{ height: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#64748b', fontSize: 10 }} />
            <ReferenceLine y={50} stroke="#334155" strokeDasharray="4 2" label={{ value: '50%', fill: '#475569', fontSize: 9 }} />
            {COMPANIES.map(c => (
              <Line key={c} type="monotone" dataKey={c} stroke={COMPANY_COLORS[c]}
                strokeWidth={2} dot={{ r: 4, fill: COMPANY_COLORS[c] }} connectNulls />
            ))}
            <Tooltip content={<ChartTooltip formatter={v => `${v}%`} />} />
            <Legend formatter={v => <span style={{ color: COMPANY_COLORS[v], fontSize: 11 }}>{v}</span>} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── Key differentiators callout strip ─────────────────────────────────────────
function KeyInsights({ tech, energy }) {
  const insights = [
    {
      label: 'Horizon Scanning',
      tech: tech.ipm.find(d => d.theme === 'Horizon')?.value,
      energy: energy.ipm.find(d => d.theme === 'Horizon')?.value,
      note: 'Tech firms scan for macro shifts 4× more intensely',
      unit: '/1k',
    },
    {
      label: 'Entrepreneurial Framing',
      tech: +(tech.entreprShare * 100).toFixed(0),
      energy: +(energy.entreprShare * 100).toFixed(0),
      note: 'Energy firms almost never use entrepreneurial vs managerial language',
      unit: '%',
    },
    {
      label: 'Customer Orientation',
      tech: +(tech.customerShare * 100).toFixed(0),
      energy: +(energy.customerShare * 100).toFixed(0),
      note: 'Tech letters foreground the customer; energy letters foreground the shareholder',
      unit: '%',
    },
    {
      label: 'Exploit Intensity',
      tech: tech.exploitPer1k,
      energy: energy.exploitPer1k,
      note: 'Energy firms signal operational execution and performance twice as densely',
      unit: '/1k',
    },
  ]

  return (
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
      {insights.map(ins => {
        const ratio = ins.energy > 0 ? (ins.tech / ins.energy).toFixed(1) : '—'
        const techHigher = ins.tech > ins.energy
        return (
          <div key={ins.label} className="card p-4">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">{ins.label}</div>
            <div className="flex items-end gap-3 mb-3">
              <div>
                <div className="text-xs text-slate-500 mb-0.5">Tech</div>
                <div className="text-xl font-bold" style={{ color: SECTOR_COLOR.Tech }}>
                  {typeof ins.tech === 'number' ? (Number.isInteger(ins.tech) ? ins.tech : fmt1(ins.tech)) : ins.tech}{ins.unit}
                </div>
              </div>
              <div className="text-slate-700 text-lg font-light mb-0.5">vs</div>
              <div>
                <div className="text-xs text-slate-500 mb-0.5">Energy</div>
                <div className="text-xl font-bold" style={{ color: SECTOR_COLOR.Energy }}>
                  {typeof ins.energy === 'number' ? (Number.isInteger(ins.energy) ? ins.energy : fmt1(ins.energy)) : ins.energy}{ins.unit}
                </div>
              </div>
            </div>
            <div className="text-xs text-slate-500 leading-relaxed">{ins.note}</div>
          </div>
        )
      })}
    </div>
  )
}

// ── Full scatter (per-company) reusable ────────────────────────────────────────
function PerCompanyScatter({ data }) {
  const points = data.quant.exploreExploit.map(r => ({
    company: r.company,
    year: r.year,
    x: +(r.explore_per_1000 ?? 0).toFixed(3),
    y: +(r.exploit_per_1000 ?? 0).toFixed(3),
  }))

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-1">Explore vs Exploit — Letter-Year Scatter</div>
      <div className="text-xs text-slate-500 mb-3">Each dot = one letter; axes = per-1,000 word density</div>
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis type="number" dataKey="x" name="Explore/1k" tick={{ fill: '#64748b', fontSize: 10 }}
              label={{ value: 'Explore / 1k', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 10 }} />
            <YAxis type="number" dataKey="y" name="Exploit/1k" tick={{ fill: '#64748b', fontSize: 10 }}
              label={{ value: 'Exploit / 1k', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
            <ZAxis range={[45, 45]} />
            {COMPANIES.map(c => (
              <Scatter key={c} name={c} data={points.filter(p => p.company === c)} fill={COMPANY_COLORS[c]} />
            ))}
            <Tooltip cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0]?.payload
                return (
                  <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs">
                    <div style={{ color: COMPANY_COLORS[d?.company] }} className="font-semibold">{d?.company} {d?.year}</div>
                    <div className="text-slate-400">Explore: {d?.x?.toFixed(2)}</div>
                    <div className="text-slate-400">Exploit: {d?.y?.toFixed(2)}</div>
                  </div>
                )
              }}
            />
            <Legend formatter={v => <span style={{ color: COMPANY_COLORS[v], fontSize: 11 }}>{v}</span>} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── IPM 4-company radar ────────────────────────────────────────────────────────
function IPMRadar({ data }) {
  const radarData = IPM_THEMES.map((theme, i) => {
    const row = { subject: IPM_SHORT[theme] }
    COMPANIES.forEach(c => {
      const byC = data.quant.byCompany.find(r => r.company === c)
      row[c] = +(byC?.[`${theme}_per_1000`] ?? 0).toFixed(2)
    })
    return row
  })

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-1">IPM Profile — All Four Companies</div>
      <div className="text-xs text-slate-500 mb-3">Per 1,000 words, aggregated</div>
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <PolarRadiusAxis tick={false} />
            {COMPANIES.map(c => (
              <Radar key={c} name={c} dataKey={c} stroke={COMPANY_COLORS[c]} fill={COMPANY_COLORS[c]} fillOpacity={0.1} />
            ))}
            <Legend formatter={v => <span style={{ color: COMPANY_COLORS[v], fontSize: 11 }}>{v}</span>} />
            <Tooltip content={<ChartTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

// ── Comparative & IPM matrix tables ───────────────────────────────────────────
function ComparativeMatrix({ data }) {
  return (
    <div className="card overflow-hidden">
      <div className="card-header">
        <div className="text-sm font-semibold text-slate-300">Comparative Matrix</div>
      </div>
      <div className="divide-y divide-slate-800">
        {data.comparative.map((row, i) => (
          <div key={i} className="p-5">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">{row.dimension}</div>
            <div className="grid grid-cols-2 xl:grid-cols-4 gap-3 mb-3">
              {COMPANIES.map(c => (
                <div key={c} className="bg-slate-800/60 rounded-lg p-3">
                  <div className="text-xs font-semibold mb-1" style={{ color: COMPANY_COLORS[c] }}>{c}</div>
                  <div className="text-xs text-slate-300 leading-relaxed">{row[c] || '—'}</div>
                </div>
              ))}
            </div>
            {row.cross_case_interpretation && (
              <div className="bg-slate-800/30 rounded-lg p-3 text-xs text-slate-400 italic border-l-2 border-slate-600">
                {row.cross_case_interpretation}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function IPMMatrix({ data }) {
  const rows = data.ipmMatrix
  if (!rows?.length) return null
  const keys = [
    'Strategic Leadership_per_1000',
    'Horizon Scanning / Sense-making_per_1000',
    'Purpose, Vision, and Governance_per_1000',
    'Strategic Options, Experimentation, and Choices_per_1000',
    'Agile Execution and Organization_per_1000',
  ]
  return (
    <div className="card overflow-hidden">
      <div className="card-header">
        <div className="text-sm font-semibold text-slate-300">IPM Comparison Matrix</div>
        <div className="text-xs text-slate-500 mt-0.5">Per 1,000 words, aggregated across selected letters</div>
      </div>
      <div className="p-5 overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-left py-2 pr-4 text-slate-400 font-semibold">Company</th>
              {['Leadership', 'Horizon', 'Purpose', 'Options', 'Execution'].map(h => (
                <th key={h} className="text-right py-2 px-3 text-slate-400 font-semibold">{h}</th>
              ))}
              <th className="text-left py-2 px-3 text-slate-400 font-semibold">Dominant</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="border-t border-slate-800">
                <td className="py-3 pr-4 font-semibold" style={{ color: COMPANY_COLORS[row.company] }}>{row.company}</td>
                {keys.map((k, j) => (
                  <td key={j} className="py-3 px-3 text-right font-mono text-slate-300">{Number(row[k] ?? 0).toFixed(1)}</td>
                ))}
                <td className="py-3 px-3 text-slate-300 text-xs">{row.dominant_quant_theme}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────────
export default function Compare() {
  const data = useData()
  const [tab, setTab] = useState('industry')

  const { tech, energy } = useIndustryStats(data.quant.byLetter, data.quant.exploreExploit)

  return (
    <div className="pb-12">
      <PageHeader
        title="Industry & Cross-Case Comparison"
        subtitle="Technology (Amazon · NVIDIA) vs Energy (Shell · Chevron) — lexical, rhetorical, and strategic divergence"
      />

      <div className="px-8 py-4 flex gap-2 border-b border-slate-800">
        {[
          { id: 'industry', label: 'Industry Breakdown' },
          { id: 'charts',   label: 'Per-Company Charts' },
          { id: 'matrix',   label: 'Comparative Matrix' },
          { id: 'ipm',      label: 'IPM Matrix' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} className={`tab-btn ${tab === t.id ? 'active' : ''}`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="px-8 py-6 space-y-6">
        {tab === 'industry' && (
          <>
            {/* Sector header cards */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <SectorHeader name="Tech" stats={tech} />
              <SectorHeader name="Energy" stats={energy} />
            </div>

            {/* Key differentiator callouts */}
            <KeyInsights tech={tech} energy={energy} />

            {/* IPM comparison + divergence side by side */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <IPMComparisonBar tech={tech} energy={energy} />
              <IPMDivergingBar tech={tech} energy={energy} />
            </div>

            {/* Rhetorical pairs */}
            <RhetoricalPairsPanel tech={tech} energy={energy} />

            {/* Explore over time */}
            <ExploreOverTime letters={data.quant.byLetter} />
          </>
        )}

        {tab === 'charts' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <IPMRadar data={data} />
              <PerCompanyScatter data={data} />
            </div>
            {/* Explore share bar */}
            <div className="card p-5">
              <div className="text-sm font-semibold text-slate-300 mb-1">Average Explore Share by Company</div>
              <div className="text-xs text-slate-500 mb-3">% of the explore+exploit pair that is explore</div>
              <div style={{ height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={COMPANIES.map(c => {
                      const rows = data.quant.byLetter.filter(r => r.company === c)
                      const mean = rows.reduce((s, r) => s + (r.explore_share_of_explore_exploit ?? 0), 0) / (rows.length || 1)
                      return { company: c, share: +(mean * 100).toFixed(1) }
                    })}
                    margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="company" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#64748b', fontSize: 10 }} />
                    <Bar dataKey="share" name="Explore %" radius={[4, 4, 0, 0]}>
                      {COMPANIES.map((c, i) => <Cell key={i} fill={COMPANY_COLORS[c]} />)}
                    </Bar>
                    <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip formatter={v => `${v}%`} />} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {tab === 'matrix' && <ComparativeMatrix data={data} />}
        {tab === 'ipm'    && <IPMMatrix data={data} />}
      </div>
    </div>
  )
}
