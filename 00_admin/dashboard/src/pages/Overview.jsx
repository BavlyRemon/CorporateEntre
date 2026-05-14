import { Link } from 'react-router-dom'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import PageHeader from '../components/PageHeader'
import { COMPANY_COLORS, COMPANIES, IPM_SHORT, INDUSTRIES } from '../utils/constants'
import { fmtPct, fmt1 } from '../utils/format'
import {
  LineChart, Line, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend
} from 'recharts'
import ChartTooltip from '../components/ChartTooltip'

function CompanyCard({ company, data }) {
  const color = COMPANY_COLORS[company]
  const letters = data.quant.byLetter.filter(r => r.company === company)
  const byCompany = data.quant.byCompany.find(r => r.company === company)
  const years = letters.map(r => r.year).sort((a, b) => a - b)
  const exploreData = letters.sort((a, b) => a.year - b.year).map(r => ({
    year: r.year,
    explore: Number((r.explore_share_of_explore_exploit * 100).toFixed(1))
  }))

  const ipmTheme = byCompany?.dominant_ipm_theme_per_1000 || '—'
  const wordCount = byCompany?.total_word_count || 0
  const exploreShare = byCompany?.explore_share_of_explore_exploit

  return (
    <div className="card overflow-hidden">
      <div className="h-1" style={{ background: color }} />
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="font-bold text-lg text-white">{company}</div>
            <div className="text-xs text-slate-500">{INDUSTRIES[company]}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500">Letters</div>
            <div className="text-2xl font-bold" style={{ color }}>{letters.length}</div>
          </div>
        </div>

        <div className="text-xs text-slate-500 mb-1">Explore share over time</div>
        <div style={{ height: 60 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={exploreData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
              <Line type="monotone" dataKey="explore" stroke={color} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-slate-500">Dominant theme:</span>
            <div className="text-slate-200 font-medium mt-0.5">{ipmTheme}</div>
          </div>
          <div>
            <span className="text-slate-500">Explore share:</span>
            <div className="font-semibold mt-0.5" style={{ color }}>{fmtPct(exploreShare)}</div>
          </div>
          <div>
            <span className="text-slate-500">Total words:</span>
            <div className="text-slate-200">{wordCount.toLocaleString()}</div>
          </div>
          <div>
            <span className="text-slate-500">Years:</span>
            <div className="text-slate-200">{years[0]}–{years[years.length - 1]}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function CompanyRadar({ data }) {
  const ipmKeys = [
    'Strategic Leadership_per_1000',
    'Horizon Scanning / Sense-making_per_1000',
    'Purpose, Vision, and Governance_per_1000',
    'Strategic Options, Experimentation, and Choices_per_1000',
    'Agile Execution and Organization_per_1000',
  ]
  const shortLabels = Object.values(IPM_SHORT)
  const radarData = shortLabels.map((label, i) => {
    const key = ipmKeys[i]
    const row = { subject: label }
    COMPANIES.forEach(c => {
      const byC = data.quant.byCompany.find(r => r.company === c)
      row[c] = byC?.[key] ?? 0
    })
    return row
  })

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-1">IPM Theme Intensity — All Companies</div>
      <div className="text-xs text-slate-500 mb-3">Per 1,000 words across all letters</div>
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <PolarRadiusAxis tick={false} />
            {COMPANIES.map(c => (
              <Radar
                key={c}
                name={c}
                dataKey={c}
                stroke={COMPANY_COLORS[c]}
                fill={COMPANY_COLORS[c]}
                fillOpacity={0.1}
              />
            ))}
            <Legend
              formatter={(v) => <span style={{ color: COMPANY_COLORS[v], fontSize: 11 }}>{v}</span>}
            />
            <Tooltip content={<ChartTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function ExploreExploitBar({ data }) {
  const chartData = COMPANIES.map(c => {
    const byC = data.quant.byCompany.find(r => r.company === c)
    return {
      company: c,
      explore: Number(((byC?.explore_per_1000 ?? byC?.explore_count / byC?.total_word_count * 1000) || 0).toFixed(2)),
      exploit: Number(((byC?.exploit_per_1000 ?? byC?.exploit_count / byC?.total_word_count * 1000) || 0).toFixed(2)),
    }
  })

  // Compute from explore_exploit ratios instead
  const eeData = COMPANIES.map(c => {
    const rows = data.quant.exploreExploit.filter(r => r.company === c)
    const explore = rows.reduce((s, r) => s + (r.explore_per_1000 ?? 0), 0) / (rows.length || 1)
    const exploit = rows.reduce((s, r) => s + (r.exploit_per_1000 ?? 0), 0) / (rows.length || 1)
    return { company: c, explore: Number(explore.toFixed(2)), exploit: Number(exploit.toFixed(2)) }
  })

  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-1">Explore vs Exploit Intensity</div>
      <div className="text-xs text-slate-500 mb-3">Average per 1,000 words across selected letters</div>
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={eeData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="company" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Bar dataKey="explore" name="Explore" fill="#6366f1" radius={[2, 2, 0, 0]} />
            <Bar dataKey="exploit" name="Exploit" fill="#f59e0b" radius={[2, 2, 0, 0]} />
            <Tooltip cursor={{ fill: 'rgba(148,163,184,0.07)' }} content={<ChartTooltip />} />
            <Legend formatter={v => <span className="text-xs text-slate-400">{v}</span>} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

const PAGES = [
  { to: '/letters', label: 'Letter Library', desc: '28 letter cards with IPM radar & summaries', color: '#6366f1' },
  { to: '/financials', label: 'Financials', desc: 'Revenue, income, capex & headcount charts', color: '#10b981' },
  { to: '/lexical', label: 'Lexical Analysis', desc: 'Theme counts, keyword heatmap, trends over time', color: '#f59e0b' },
  { to: '/eras', label: 'Era Dashboards', desc: '12 strategic eras across 4 companies', color: '#0ea5e9' },
  { to: '/compare', label: 'Industry Compare', desc: 'Cross-case radar, scatter & comparative matrix', color: '#f43f5e' },
  { to: '/hypotheses', label: 'Hypotheses', desc: 'H1–H4 with evidence & outcome anchors', color: '#a855f7' },
  { to: '/briefs', label: 'Brief Library', desc: '15 qualitative & methodology briefs', color: '#64748b' },
]

export default function Overview() {
  const data = useData()

  const totalWords = data.quant.byCompany.reduce((s, r) => s + (r.total_word_count || 0), 0)
  const years = [...new Set(data.quant.byLetter.map(r => r.year))].sort((a, b) => a - b)

  return (
    <div className="pb-12">
      <PageHeader
        title="Corporate Entrepreneurship — Mission Control"
        subtitle="Comparative analysis of Amazon, NVIDIA, Shell & Chevron across 28 CEO letters (1997–2025)"
      />

      {/* Hero stats */}
      <div className="px-8 py-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Companies" value="4" sub="Amazon · NVIDIA · Shell · Chevron" accent="text-blue-400" />
        <StatCard label="CEO Letters" value="28" sub="7 per company" accent="text-emerald-400" />
        <StatCard label="Total Words" value={totalWords.toLocaleString()} sub="Clean corpus" accent="text-purple-400" />
        <StatCard label="Year Span" value={`${years[0]}–${years[years.length - 1]}`} sub="28 years" accent="text-amber-400" />
      </div>

      {/* Company cards */}
      <div className="px-8 mb-6">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Companies</h2>
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {COMPANIES.map(c => <CompanyCard key={c} company={c} data={data} />)}
        </div>
      </div>

      {/* Charts row */}
      <div className="px-8 grid grid-cols-1 xl:grid-cols-2 gap-4 mb-6">
        <CompanyRadar data={data} />
        <ExploreExploitBar data={data} />
      </div>

      {/* Dashboard map */}
      <div className="px-8">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Navigate the Dashboard</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
          {PAGES.map(p => (
            <Link key={p.to} to={p.to} className="card p-4 hover:border-slate-600 transition-colors group">
              <div className="w-2 h-2 rounded-full mb-3" style={{ background: p.color }} />
              <div className="font-semibold text-slate-200 text-sm group-hover:text-white transition-colors">{p.label}</div>
              <div className="text-xs text-slate-500 mt-1">{p.desc}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
