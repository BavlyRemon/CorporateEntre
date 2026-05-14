import { useState } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import ChartTooltip from '../components/ChartTooltip'
import { COMPANY_COLORS } from '../utils/constants'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  ResponsiveContainer, Tooltip, Legend, Cell
} from 'recharts'

const COMPANIES_FIN = ['Amazon', 'NVIDIA', 'Shell', 'Chevron']

// Strip markdown formatting and parse to number; returns null if not numeric
function parseVal(s) {
  if (!s || s === '—' || s === '-' || s.toLowerCase() === 'n/a' || s === '') return null
  // Strip markdown bold, italic, approx prefix, then parse
  let clean = s.replace(/\*\*/g, '').replace(/\*/g, '').replace(/^~/, '').trim()
  // Handle parentheses as negative: ($123) → -123
  const neg = /^\((.+)\)$/.exec(clean)
  if (neg) clean = '-' + neg[1]
  clean = clean.replace(/[$,\s%]/g, '')
  // Handle B/M/K suffixes
  const m = /^(-?\d[\d.]*)([BbMmKk])?$/.exec(clean)
  if (!m) return null
  let v = parseFloat(m[1])
  if (m[2]) {
    const u = m[2].toLowerCase()
    if (u === 'b') v *= 1000        // B → treat as $B × 1000 → millions
    else if (u === 'k') v /= 1000   // K → thousands → millions
  }
  return isNaN(v) ? null : v
}

function stripMd(s) {
  return (s || '').replace(/\*\*/g, '').replace(/\*/g, '').replace(/[—–]/g, '-').trim()
}

// Find a row whose label column contains any of the given substrings (case-insensitive).
// labelKey must be passed explicitly — do NOT use Object.values()[0] because JS sorts
// numeric string keys ("2014", "2020"…) before non-numeric ones (""), so the year value
// would come first, not the metric label.
function findRow(rows, labelKey, ...needles) {
  return rows.find(r => {
    const label = stripMd(r[labelKey] || '').toLowerCase()
    return needles.some(n => label.includes(n.toLowerCase()))
  })
}

// Build [{year, ...metrics}] from a table for given {displayName: rowNeedle[]} map
function buildChart(table, metricMap) {
  if (!table?.headers?.length || !table?.rows?.length) return []
  const labelCol = table.headers[0]  // '' for income/cash/balance tables
  const yearCols = table.headers.slice(1)
  const result = {}
  yearCols.forEach(y => { result[y] = { year: y } })
  for (const [displayName, needles] of Object.entries(metricMap)) {
    const row = findRow(table.rows, labelCol, ...needles)
    if (!row) continue
    yearCols.forEach(y => {
      const v = parseVal(row[y])
      if (v !== null) result[y][displayName] = v
    })
  }
  return Object.values(result).filter(d =>
    Object.keys(d).some(k => k !== 'year')
  )
}

const CHART_COLORS = ['#FF9900', '#6366f1', '#10b981', '#f43f5e', '#0ea5e9', '#a855f7']

function SmartChart({ title, subtitle, data: chartData, height = 240, yFmt }) {
  if (!chartData?.length) return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-400 mb-1">{title}</div>
      <div className="text-xs text-slate-600 italic">No numeric data parsed for this chart</div>
    </div>
  )
  const keys = Object.keys(chartData[0]).filter(k => k !== 'year')
  const defaultFmt = v => {
    if (v === null || v === undefined) return '—'
    const abs = Math.abs(v)
    if (abs >= 1000) return `$${(v / 1000).toFixed(1)}B`
    return `$${v.toLocaleString()}M`
  }
  const fmt = yFmt || defaultFmt
  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">{title}</div>
      {subtitle && <div className="text-xs text-slate-500 mb-3">{subtitle}</div>}
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => {
              const abs = Math.abs(v)
              if (abs >= 1000) return `${(v/1000).toFixed(0)}B`
              return `${v}M`
            }} />
            {keys.map((k, i) => (
              <Line
                key={k}
                type="monotone"
                dataKey={k}
                name={k}
                stroke={CHART_COLORS[i % CHART_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
                connectNulls
              />
            ))}
            <Tooltip content={<ChartTooltip formatter={(v) => fmt(v)} />} />
            <Legend formatter={v => <span style={{ fontSize: 11, color: '#94a3b8' }}>{v}</span>} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function CashBarChart({ title, subtitle, data: chartData, color, height = 200 }) {
  if (!chartData?.length) return null
  const keys = Object.keys(chartData[0]).filter(k => k !== 'year')
  return (
    <div className="card p-5">
      <div className="text-sm font-semibold text-slate-300 mb-0.5">{title}</div>
      {subtitle && <div className="text-xs text-slate-500 mb-3">{subtitle}</div>}
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={v => {
              const abs = Math.abs(v)
              if (abs >= 1000) return `${(v/1000).toFixed(0)}B`
              return `${v}M`
            }} />
            {keys.map((k, i) => {
              const barColor = i === 0 ? color : CHART_COLORS[i + 1]
              return (
                <Bar key={k} dataKey={k} name={k} fill={barColor} radius={[2, 2, 0, 0]}>
                  {chartData.map((entry, idx) => (
                    <Cell
                      key={idx}
                      fill={entry[k] < 0 ? '#f43f5e' : barColor}
                    />
                  ))}
                </Bar>
              )
            })}
            <Tooltip content={<ChartTooltip formatter={v => {
              const abs = Math.abs(v)
              return `${v < 0 ? '-' : ''}$${abs >= 1000 ? (abs/1000).toFixed(1)+'B' : abs.toLocaleString()+'M'}`
            }} />} />
            <Legend formatter={v => <span style={{ fontSize: 11, color: '#94a3b8' }}>{v}</span>} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function FinancialTable({ table }) {
  if (!table?.headers?.length) return <div className="text-slate-500 text-sm">No data</div>
  const labelCol = table.headers[0]
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr>
            {table.headers.map((h, i) => (
              <th
                key={i}
                className={`bg-slate-800/80 text-slate-300 font-semibold px-3 py-2 border border-slate-700 whitespace-nowrap
                  ${i === 0 ? 'text-left sticky left-0 bg-slate-800' : 'text-right'}`}
              >
                {h || 'Metric'}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => {
            const labelCol = table.headers[0]
            const label = stripMd(row[labelCol] || '')
            const isBold = (row[labelCol] || '').includes('**')
            return (
              <tr key={i} className={`border-b border-slate-800/50 ${i % 2 === 0 ? '' : 'bg-slate-900/30'}`}>
                {table.headers.map((h, j) => (
                  <td
                    key={j}
                    className={`px-3 py-1.5 border-r border-slate-800/50 whitespace-nowrap
                      ${j === 0 ? 'text-left sticky left-0 bg-slate-900' : 'text-right font-mono'}
                      ${isBold ? 'font-semibold text-slate-100' : 'text-slate-300'}`}
                  >
                    {j === 0 ? label : (row[h] || '—')}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
      {table.notes?.length > 0 && (
        <div className="mt-2 text-xs text-slate-500 italic">{table.notes.join(' ')}</div>
      )}
    </div>
  )
}

function InvestingTable({ table }) {
  if (!table?.rows?.length) return null
  return (
    <div className="space-y-2">
      {table.rows.map((row, i) => {
        const year = row['Year'] || row[table.headers[0]]
        const theme = row['Primary Investment Theme'] || row[table.headers[1]] || ''
        const extra = table.headers.slice(2).map(h => row[h]).filter(Boolean).join(' · ')
        return (
          <div key={i} className="flex gap-3 text-sm bg-slate-800/40 rounded-lg px-4 py-2.5">
            <span className="font-mono text-slate-400 w-16 shrink-0">{year}</span>
            <span className="text-slate-200">{theme}</span>
            {extra && <span className="text-slate-500 text-xs self-center ml-auto">{extra}</span>}
          </div>
        )
      })}
    </div>
  )
}

// Per-company chart configs
const COMPANY_METRICS = {
  Amazon: {
    income: {
      'Revenue': ['Total Net Sales', 'total net sales'],
      'Operating Income': ['Operating Income', 'operating income'],
      'Net Income': ['Net Income (Loss)', 'net income'],
    },
    cash: {
      'Operating CF': ['Operating Cash Flow'],
      'Capex': ['Cash Capex'],
      'FCF': ['Free Cash Flow'],
    },
  },
  NVIDIA: {
    income: {
      'Revenue': ['Total Revenue'],
      'Gross Profit': ['Gross Profit'],
      'Operating Income': ['Operating Income'],
      'Net Income': ['Net Income'],
    },
    cash: {
      'Operating CF': ['Operating Cash Flow'],
      'Capex': ['CapEx'],
      'FCF': ['Free Cash Flow'],
      'Buybacks': ['Share Buybacks'],
    },
  },
  Shell: {
    income: {
      'Revenue': ['Revenue'],
      'Adj. Earnings': ['CCS', 'Adjusted Earnings'],
      'Net Income': ['Net Income', 'GAAP'],
    },
    cash: {
      'Operating CF': ['Operating Cash Flow'],
      'Capex': ['Cash Capital Expenditure'],
      'FCF': ['Free Cash Flow'],
      'Buybacks': ['Share Buybacks'],
    },
  },
  Chevron: {
    income: {
      'Revenue': ['Sales & Other Operating Revenues', 'Total Revenues'],
      'Net Income': ['Net Income (Loss) Attrib', 'Net Income'],
    },
    cash: {
      'Operating CF': ['Operating Cash Flow'],
      'Capex': ['Cash Capital Expenditures'],
      'FCF': ['Free Cash Flow'],
      'Buybacks': ['Share Buybacks'],
    },
  },
}

function CompanyFinancials({ company, data }) {
  const color = COMPANY_COLORS[company]
  const fin = data.financials?.[company]
  const [showRaw, setShowRaw] = useState(false)

  const incomeTable = fin?.tables?.find(t => t.table_name?.toLowerCase().includes('income'))
  const cashTable = fin?.tables?.find(t => t.table_name?.toLowerCase().includes('cash'))
  const investingTable = fin?.tables?.find(t =>
    t.table_name?.toLowerCase().includes('invest') || t.table_name?.toLowerCase().includes('investing')
  )
  const opTable = fin?.tables?.find(t =>
    t.table_name?.toLowerCase().includes('operating') || t.table_name?.toLowerCase().includes('r&d')
  )

  const cfg = COMPANY_METRICS[company] || {}
  const incomeChart = buildChart(incomeTable, cfg.income || {})
  const cashChart = buildChart(cashTable, cfg.cash || {})

  // Segment revenue chart for NVIDIA
  const segmentChart = company === 'NVIDIA'
    ? buildChart(incomeTable, {
        'Gaming': ['— Gaming'],
        'Data Center': ['— Data Center'],
        'Pro Viz': ['— Professional Visualization'],
        'Automotive': ['— Automotive'],
      })
    : company === 'Amazon'
    ? buildChart(incomeTable, {
        'N. America': ['— North America'],
        'International': ['— International'],
        'AWS': ['— AWS'],
      })
    : null

  return (
    <div className="space-y-5">
      <SmartChart
        title={`${company} — Revenue, Operating Income & Net Income`}
        subtitle="USD millions"
        data={incomeChart}
        color={color}
      />

      {segmentChart?.length > 0 && (
        <SmartChart
          title={`${company} — Revenue by Segment`}
          subtitle="USD millions"
          data={segmentChart}
          color={color}
        />
      )}

      <CashBarChart
        title={`${company} — Cash Flow & Capital Allocation`}
        subtitle="USD millions · negative FCF shown in red"
        data={cashChart}
        color={color}
      />

      {investingTable && (
        <div className="card p-5">
          <div className="text-sm font-semibold text-slate-300 mb-3">What {company} Is Investing In</div>
          <InvestingTable table={investingTable} />
        </div>
      )}

      {opTable && (
        <div className="card p-5">
          <div className="text-sm font-semibold text-slate-300 mb-3">{opTable.table_name}</div>
          <FinancialTable table={opTable} />
        </div>
      )}

      <div>
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors underline underline-offset-2"
        >
          {showRaw ? '▲ Hide' : '▼ Show'} all raw tables
        </button>
        {showRaw && fin?.tables?.map((table, i) => (
          <div key={i} className="card p-5 mt-4">
            <div className="text-sm font-semibold text-slate-400 mb-3">{table.table_name || table.subsection}</div>
            <FinancialTable table={table} />
          </div>
        ))}
      </div>
    </div>
  )
}

function CrossCompany({ data }) {
  const crossData = data.financials?.['Cross-Company']
  if (!crossData?.tables?.length) return <div className="text-slate-500">Cross-company data not available</div>
  return (
    <div className="space-y-6">
      {crossData.tables.map((table, i) => (
        <div key={i} className="card p-5">
          <div className="text-sm font-semibold text-slate-300 mb-3">{table.table_name || table.subsection}</div>
          <FinancialTable table={table} />
        </div>
      ))}
    </div>
  )
}

export default function Financials() {
  const data = useData()
  const [activeCompany, setActiveCompany] = useState('Amazon')

  return (
    <div className="pb-12">
      <PageHeader
        title="Financial Breakdown"
        subtitle="Key figures from full annual reports & 10-K filings — USD millions unless noted"
      />

      <div className="px-8 py-4 flex gap-2 flex-wrap border-b border-slate-800">
        {[...COMPANIES_FIN, 'Cross-Company'].map(c => (
          <button
            key={c}
            onClick={() => setActiveCompany(c)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeCompany === c ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'
            }`}
            style={activeCompany === c && COMPANY_COLORS[c] ? { color: COMPANY_COLORS[c] } : {}}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="px-8 py-6">
        {activeCompany === 'Cross-Company'
          ? <CrossCompany data={data} />
          : <CompanyFinancials company={activeCompany} data={data} />
        }
      </div>
    </div>
  )
}
