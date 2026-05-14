import { useState, useMemo } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import ChartTooltip from '../components/ChartTooltip'
import {
  COMPANY_COLORS, COMPANIES, IPM_THEMES, IPM_SHORT, IPM_COLORS
} from '../utils/constants'
import { fmt1 } from '../utils/format'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
  Tooltip, Legend, LineChart, Line, Cell
} from 'recharts'

function ThemeTab({ data }) {
  // Stacked bar: IPM per 1000 per company
  const chartData = COMPANIES.map(c => {
    const row = data.quant.byCompany.find(r => r.company === c)
    const out = { company: c }
    IPM_THEMES.forEach(t => {
      out[IPM_SHORT[t]] = Number((row?.[`${t}_per_1000`] ?? 0).toFixed(2))
    })
    return out
  })

  // Explore vs exploit horizontal bar
  const eeData = COMPANIES.map(c => {
    const rows = data.quant.exploreExploit.filter(r => r.company === c)
    const explore = rows.reduce((s, r) => s + (r.explore_per_1000 ?? 0), 0) / (rows.length || 1)
    const exploit = rows.reduce((s, r) => s + (r.exploit_per_1000 ?? 0), 0) / (rows.length || 1)
    const share = rows.reduce((s, r) => s + (r.explore_share_of_pair ?? 0), 0) / (rows.length || 1)
    return { company: c, explore: +explore.toFixed(3), exploit: +exploit.toFixed(3), share: +share.toFixed(3) }
  })

  return (
    <div className="space-y-6">
      <div className="card p-5">
        <div className="text-sm font-semibold text-slate-300 mb-1">IPM Theme Intensity by Company</div>
        <div className="text-xs text-slate-500 mb-4">Average per 1,000 words across all selected letters</div>
        <div style={{ height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="company" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              {Object.values(IPM_SHORT).map((label, i) => (
                <Bar key={label} dataKey={label} stackId="ipm" fill={IPM_COLORS[i]} />
              ))}
              <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip />} />
              <Legend formatter={v => <span style={{ fontSize: 11, color: '#94a3b8' }}>{v}</span>} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card p-5">
        <div className="text-sm font-semibold text-slate-300 mb-1">Explore vs Exploit — Average per 1,000 Words</div>
        <div className="text-xs text-slate-500 mb-4">Lexical pair across all letters</div>
        <div style={{ height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={eeData} layout="vertical" margin={{ top: 5, right: 60, bottom: 5, left: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis type="category" dataKey="company" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Bar dataKey="explore" name="Explore" fill="#6366f1" radius={[0, 2, 2, 0]} />
              <Bar dataKey="exploit" name="Exploit" fill="#f59e0b" radius={[0, 2, 2, 0]} />
              <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip />} />
              <Legend />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card p-5">
        <div className="text-sm font-semibold text-slate-300 mb-3">Explore Share Summary</div>
        <div className="space-y-3">
          {eeData.map(d => (
            <div key={d.company} className="flex items-center gap-4">
              <div className="w-16 text-sm font-medium" style={{ color: COMPANY_COLORS[d.company] }}>{d.company}</div>
              <div className="flex-1 bg-slate-800 rounded-full h-3 overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${d.share * 100}%`, background: COMPANY_COLORS[d.company] }}
                />
              </div>
              <div className="text-sm font-mono text-slate-300 w-12 text-right">{(d.share * 100).toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function KeywordTab({ data }) {
  const [search, setSearch] = useState('')
  const [filterTheme, setFilterTheme] = useState('All')

  const themes = [...new Set(data.quant.keywordByCompany.map(r => r.theme))]

  const rows = useMemo(() => {
    return data.quant.keywordByCompany.filter(r => {
      if (filterTheme !== 'All' && r.theme !== filterTheme) return false
      if (search && !r.keyword?.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [data, filterTheme, search])

  // Max per company for heat coloring
  const maxByCompany = {}
  COMPANIES.forEach(c => {
    maxByCompany[c] = Math.max(...data.quant.keywordByCompany.map(r => Number(r[c] ?? 0)), 1)
  })

  function heatOpacity(val, max) {
    const v = Number(val || 0)
    if (v === 0) return 'bg-transparent text-slate-600'
    const pct = v / max
    if (pct > 0.75) return 'bg-blue-500/40 text-blue-200'
    if (pct > 0.5) return 'bg-blue-500/25 text-blue-300'
    if (pct > 0.25) return 'bg-blue-500/15 text-blue-400'
    return 'bg-slate-800/50 text-slate-400'
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-3 flex-wrap">
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search keyword…"
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 placeholder-slate-500 w-52 focus:outline-none focus:border-slate-500"
        />
        <div className="flex gap-1 flex-wrap">
          {['All', ...themes].map(t => (
            <button
              key={t}
              onClick={() => setFilterTheme(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filterTheme === t ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'}`}
            >
              {t === 'All' ? 'All themes' : t}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-500 self-center">{rows.length} keywords</span>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0">
              <tr>
                <th className="bg-slate-800 text-slate-300 font-semibold px-3 py-2 text-left border-b border-slate-700 w-28">Theme</th>
                <th className="bg-slate-800 text-slate-300 font-semibold px-3 py-2 text-left border-b border-slate-700 w-28">Subtheme</th>
                <th className="bg-slate-800 text-slate-300 font-semibold px-3 py-2 text-left border-b border-slate-700">Keyword</th>
                {COMPANIES.map(c => (
                  <th key={c} className="bg-slate-800 font-semibold px-3 py-2 text-right border-b border-slate-700" style={{ color: COMPANY_COLORS[c] }}>{c}</th>
                ))}
                <th className="bg-slate-800 text-slate-500 font-semibold px-3 py-2 text-right border-b border-slate-700">Total</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i} className={`border-b border-slate-800/50 ${i % 2 === 0 ? '' : 'bg-slate-900/30'}`}>
                  <td className="px-3 py-1.5 text-slate-500 truncate max-w-[7rem]">{row.theme}</td>
                  <td className="px-3 py-1.5 text-slate-500 truncate max-w-[7rem]">{row.subtheme}</td>
                  <td className="px-3 py-1.5 text-slate-200 font-medium">{row.keyword}</td>
                  {COMPANIES.map(c => (
                    <td key={c} className={`px-3 py-1.5 text-right font-mono ${heatOpacity(row[c], maxByCompany[c])}`}>
                      {row[c] || 0}
                    </td>
                  ))}
                  <td className="px-3 py-1.5 text-right font-mono text-slate-400">{row.Total || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function OverTimeTab({ data }) {
  const [filterTheme, setFilterTheme] = useState('All')
  const themes = [...new Set(data.quant.themesOverTime.map(r => r.theme))]
  const companies = COMPANIES

  return (
    <div className="space-y-6">
      <div className="flex gap-1 flex-wrap">
        {['All', ...themes].map(t => (
          <button
            key={t}
            onClick={() => setFilterTheme(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filterTheme === t ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'}`}
          >
            {t === 'All' ? 'All themes' : t}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {companies.map(company => {
          const companyData = data.quant.themesOverTime.filter(r => r.company === company)
          const years = [...new Set(companyData.map(r => r.year))].sort((a, b) => a - b)
          const activeThemes = filterTheme === 'All' ? themes : [filterTheme]

          const chartData = years.map(year => {
            const row = { year }
            activeThemes.forEach(theme => {
              const r = companyData.find(d => d.year === year && d.theme === theme)
              row[theme] = r ? Number((r.per_1000_words ?? 0).toFixed(2)) : 0
            })
            return row
          })

          return (
            <div key={company} className="card p-5">
              <div className="text-sm font-semibold mb-1" style={{ color: COMPANY_COLORS[company] }}>{company}</div>
              <div className="text-xs text-slate-500 mb-3">IPM per 1,000 words over time</div>
              <div style={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 9 }} />
                    {activeThemes.map((theme, i) => (
                      <Line
                        key={theme}
                        type="monotone"
                        dataKey={theme}
                        name={IPM_SHORT[theme] || theme}
                        stroke={IPM_COLORS[i % IPM_COLORS.length]}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                    ))}
                    <Tooltip content={<ChartTooltip />} />
                    <Legend formatter={v => <span style={{ fontSize: 10, color: '#94a3b8' }}>{v}</span>} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Lexical() {
  const data = useData()
  const [tab, setTab] = useState('themes')

  return (
    <div className="pb-12">
      <PageHeader title="Lexical Analysis" subtitle="IPM theme counts, keyword heatmap, and trends over time" />

      <div className="px-8 py-4 flex gap-2 border-b border-slate-800">
        {[
          { id: 'themes', label: 'By Theme' },
          { id: 'keywords', label: 'By Keyword' },
          { id: 'overtime', label: 'Over Time' },
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`tab-btn ${tab === t.id ? 'active' : ''}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="px-8 py-6">
        {tab === 'themes' && <ThemeTab data={data} />}
        {tab === 'keywords' && <KeywordTab data={data} />}
        {tab === 'overtime' && <OverTimeTab data={data} />}
      </div>
    </div>
  )
}
