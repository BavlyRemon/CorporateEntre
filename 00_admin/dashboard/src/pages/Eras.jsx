import { useState } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import LetterDrawer from '../components/LetterDrawer'
import CompanyBadge from '../components/CompanyBadge'
import ChartTooltip from '../components/ChartTooltip'
import { COMPANY_COLORS, COMPANIES, IPM_THEMES, IPM_SHORT, IPM_COLORS } from '../utils/constants'
import { fmtPct, fmt1 } from '../utils/format'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  ResponsiveContainer, Tooltip, Cell, RadarChart,
  Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts'

const CLASS_CHIP = {
  'exploratory': 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30',
  'exploitative': 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
  'balanced': 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
  'ambidextrous': 'bg-purple-500/20 text-purple-300 border border-purple-500/30',
}
function exploitChip(cls) {
  if (!cls) return 'bg-slate-700 text-slate-400'
  const lower = cls.toLowerCase()
  for (const [k, v] of Object.entries(CLASS_CHIP)) {
    if (lower.includes(k)) return v
  }
  return 'bg-slate-700 text-slate-400'
}

// Compute aggregated lexical stats for a set of letter rows
function aggregateLetters(letters) {
  if (!letters.length) return null
  const n = letters.length

  const avg = key => letters.reduce((s, r) => s + (r[key] ?? 0), 0) / n

  const ipm = IPM_THEMES.map((theme, i) => ({
    subject: IPM_SHORT[theme],
    value: Number(avg(`${theme}_per_1000`).toFixed(2)),
    color: IPM_COLORS[i],
  }))

  const explore = avg('explore_count')
  const exploit = avg('exploit_count')
  const exploreShare = (explore + exploit) > 0 ? explore / (explore + exploit) : null

  const pairCounts = [
    { label: 'Customer', a: avg('customer_count'), b: avg('shareholder_count'), shareKey: 'customer_share_of_customer_shareholder' },
    { label: 'Long-term', a: avg('long_term_count'), b: avg('short_term_count'), shareKey: 'long_term_share_of_long_short' },
    { label: 'Entrepreneurial', a: avg('entrepreneurial_count'), b: avg('managerial_count'), shareKey: 'entrepreneurial_share_of_entrepreneurial_managerial' },
    { label: 'Internal Innov.', a: avg('internal_innovation_count'), b: avg('external_innovation_count'), shareKey: 'internal_share_of_internal_external' },
    { label: 'Risk/Challenge', a: avg('risk_challenge_count'), b: avg('success_performance_count'), shareKey: 'risk_share_of_risk_performance' },
  ].map(p => ({
    ...p,
    share: avg(p.shareKey),
  }))

  const classes = letters.map(l => l.explore_exploit_class).filter(Boolean)
  const classSummary = [...new Set(classes)].join(', ')

  return { ipm, exploreShare, pairCounts, classSummary, n, explore, exploit }
}

function EraLexicalBreakdown({ letters, color }) {
  const stats = aggregateLetters(letters)
  if (!stats) return null

  const maxIpm = Math.max(...stats.ipm.map(d => d.value), 1)

  return (
    <div className="mt-4 pt-4 border-t border-slate-800 space-y-4">
      {/* IPM theme bars */}
      <div>
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
          IPM Theme Intensity — avg per 1,000 words
        </div>
        <div className="space-y-1.5">
          {stats.ipm.map((d, i) => (
            <div key={d.subject} className="flex items-center gap-2">
              <div className="w-16 text-right text-xs text-slate-500 shrink-0">{d.subject}</div>
              <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${(d.value / maxIpm) * 100}%`, background: d.color }}
                />
              </div>
              <div className="w-8 text-right text-xs font-mono text-slate-300">{fmt1(d.value)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Explore / exploit */}
      <div>
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
          Explore vs Exploit
        </div>
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-500">Explore share of pair</span>
              <span style={{ color }}>{fmtPct(stats.exploreShare)}</span>
            </div>
            <div className="h-2.5 bg-slate-800 rounded-full overflow-hidden flex">
              <div
                className="h-full rounded-l-full"
                style={{ width: `${(stats.exploreShare ?? 0) * 100}%`, background: '#6366f1' }}
              />
              <div
                className="h-full rounded-r-full"
                style={{ width: `${(1 - (stats.exploreShare ?? 0)) * 100}%`, background: '#f59e0b' }}
              />
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-indigo-400">Explore ({fmt1(stats.explore)}/ltr)</span>
              <span className="text-amber-400">Exploit ({fmt1(stats.exploit)}/ltr)</span>
            </div>
          </div>
        </div>
        {stats.classSummary && (
          <div className="text-xs text-slate-500 mt-1.5">
            Class{stats.n > 1 ? 'es' : ''}: <span className="text-slate-300">{stats.classSummary}</span>
          </div>
        )}
      </div>

      {/* Rhetorical pairs */}
      <div>
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
          Rhetorical Orientation (avg share of pair)
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
          {stats.pairCounts.map(p => (
            <div key={p.label} className="flex items-center gap-2">
              <div className="w-20 text-xs text-slate-500 truncate shrink-0">{p.label}</div>
              <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${(p.share ?? 0) * 100}%`, background: color }}
                />
              </div>
              <div className="text-xs font-mono text-slate-400 w-8 text-right">{(p.share * 100).toFixed(0)}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function EraExploreChart({ data }) {
  const eraData = data.eras.map(era => {
    const letters = data.quant.byLetter.filter(r => r.company === era.company && r.era === era.era)
    const share = letters.length
      ? letters.reduce((s, r) => s + (r.explore_share_of_explore_exploit ?? 0), 0) / letters.length
      : null
    return {
      label: `${era.company.slice(0, 3)} ${era.era.split(' ')[0]}`,
      company: era.company,
      share: share !== null ? Number((share * 100).toFixed(1)) : null,
    }
  }).filter(d => d.share !== null)

  return (
    <div className="card p-5 mb-6">
      <div className="text-sm font-semibold text-slate-300 mb-1">Explore Share by Era</div>
      <div className="text-xs text-slate-500 mb-3">Average across letters in each era</div>
      <div style={{ height: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={eraData} layout="vertical" margin={{ top: 5, right: 60, bottom: 5, left: 100 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => `${v}%`} />
            <YAxis type="category" dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} width={95} />
            <Bar dataKey="share" name="Explore share %" radius={[0, 2, 2, 0]}>
              {eraData.map((entry, i) => (
                <Cell key={i} fill={COMPANY_COLORS[entry.company]} />
              ))}
            </Bar>
            <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip formatter={v => `${v}%`} />} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function Eras() {
  const data = useData()
  const [filterCompany, setFilterCompany] = useState('All')
  const [selectedLetter, setSelectedLetter] = useState(null)
  const [expandAll, setExpandAll] = useState(false)

  const eras = filterCompany === 'All'
    ? data.eras
    : data.eras.filter(e => e.company === filterCompany)

  function handleLetterClick(letterInfo) {
    const manifest = data.manifest.find(
      m => m.company === letterInfo.company && m.year === letterInfo.year
    )
    setSelectedLetter(manifest || letterInfo)
  }

  return (
    <div className="pb-12">
      <PageHeader
        title="Era Dashboards"
        subtitle="12 strategic eras — IPM theme intensity, explore/exploit balance, and rhetorical orientation"
      />

      <div className="px-8 py-4 flex items-center gap-3 border-b border-slate-800">
        <div className="flex gap-1">
          {['All', ...COMPANIES].map(c => (
            <button
              key={c}
              onClick={() => setFilterCompany(c)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${filterCompany === c ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'}`}
              style={filterCompany === c && c !== 'All' ? { color: COMPANY_COLORS[c] } : {}}
            >
              {c}
            </button>
          ))}
        </div>
        <div className="ml-auto">
          <button
            onClick={() => setExpandAll(v => !v)}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors border border-slate-700 px-3 py-1.5 rounded-lg"
          >
            {expandAll ? 'Collapse all lexical' : 'Expand all lexical'}
          </button>
        </div>
      </div>

      <div className="px-8 py-6">
        {filterCompany === 'All' && <EraExploreChart data={data} />}

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {eras.map((era, i) => (
            <EraCardControlled
              key={i}
              era={era}
              allLetters={data.quant.byLetter}
              onLetterClick={handleLetterClick}
              forceExpand={expandAll}
            />
          ))}
        </div>
      </div>

      {selectedLetter && (
        <LetterDrawer letter={selectedLetter} onClose={() => setSelectedLetter(null)} />
      )}
    </div>
  )
}

// Wrapper that respects both local toggle and global forceExpand
function EraCardControlled({ era, allLetters, onLetterClick, forceExpand }) {
  const color = COMPANY_COLORS[era.company]
  const eraLetters = allLetters.filter(l => l.era === era.era && l.company === era.company)
  const [localOpen, setLocalOpen] = useState(false)
  const showLexical = forceExpand || localOpen

  return (
    <div className="card overflow-hidden">
      <div className="h-1" style={{ background: color }} />
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <CompanyBadge company={era.company} />
            <div className="font-semibold text-slate-200 text-sm mt-2 leading-tight">{era.era}</div>
          </div>
          <div className={`text-xs px-2 py-1 rounded-full ${exploitChip(era.explore_exploit_diagnosis)}`}>
            {era.explore_exploit_diagnosis}
          </div>
        </div>

        <div className="mb-3">
          <div className="text-xs text-slate-500 mb-1">Dominant IPM theme</div>
          <div className="text-sm font-medium" style={{ color }}>{era.dominant_ipm}</div>
        </div>

        <div className="mb-3">
          <div className="text-xs text-slate-500 mb-1">Evidence</div>
          <div className="text-xs text-slate-400 leading-relaxed">{era.evidence}</div>
        </div>

        <div className="mb-4">
          <div className="text-xs text-slate-500 mb-1">Interpretation</div>
          <div className="text-xs text-slate-300 leading-relaxed italic">{era.interpretation}</div>
        </div>

        {eraLetters.length > 0 && (
          <div className="mb-3">
            <div className="text-xs text-slate-500 mb-2">Letters ({eraLetters.length})</div>
            <div className="flex flex-wrap gap-1.5">
              {eraLetters.map(l => (
                <button
                  key={l.year}
                  onClick={() => onLetterClick(l)}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-mono transition-colors"
                  style={{ color }}
                >
                  {l.year}
                </button>
              ))}
            </div>
          </div>
        )}

        {eraLetters.length > 0 && (
          <button
            onClick={() => setLocalOpen(v => !v)}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            <span className="text-slate-600">{showLexical ? '▲' : '▼'}</span>
            {showLexical ? 'Hide' : 'Show'} lexical breakdown
          </button>
        )}

        {showLexical && (
          <EraLexicalBreakdown letters={eraLetters} color={color} />
        )}
      </div>
    </div>
  )
}
