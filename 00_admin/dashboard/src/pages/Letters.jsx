import { useState, useMemo } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import CompanyBadge from '../components/CompanyBadge'
import LetterDrawer from '../components/LetterDrawer'
import { COMPANY_COLORS, COMPANIES } from '../utils/constants'
import { fmtPct, fmtInt } from '../utils/format'

const CLASS_COLORS = {
  'exploratory leaning': 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  'exploitative leaning': 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  'balanced': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  'ambidextrous': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
}

function classColor(cls) {
  if (!cls) return 'bg-slate-700/40 text-slate-400 border-slate-600'
  const lower = cls.toLowerCase()
  for (const [k, v] of Object.entries(CLASS_COLORS)) {
    if (lower.includes(k.split(' ')[0])) return v
  }
  return 'bg-slate-700/40 text-slate-400 border-slate-600'
}

function LetterCard({ letter, quant, onClick }) {
  const color = COMPANY_COLORS[letter.company] || '#64748b'
  const exploreShare = quant?.explore_share_of_explore_exploit
  const exploitClass = quant?.explore_exploit_class || '—'
  const pct = typeof exploreShare === 'number' ? exploreShare : 0

  return (
    <button
      onClick={() => onClick(letter)}
      className="card p-4 text-left hover:border-slate-600 transition-all group cursor-pointer w-full"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <CompanyBadge company={letter.company} />
          <div className="text-2xl font-bold text-white mt-2 group-hover:text-slate-100">{letter.year}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500">Words</div>
          <div className="text-sm font-mono text-slate-300">{fmtInt(letter.word_count)}</div>
        </div>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-500">Explore share</span>
          <span style={{ color }}>{fmtPct(exploreShare)}</span>
        </div>
        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full" style={{ width: `${pct * 100}%`, background: color }} />
        </div>
      </div>

      <div className={`badge border text-xs px-2 py-0.5 ${classColor(exploitClass)}`}>
        {exploitClass}
      </div>

      {quant?.era && (
        <div className="text-xs text-slate-600 mt-2 truncate">{quant.era}</div>
      )}
    </button>
  )
}

export default function Letters() {
  const data = useData()
  const [selected, setSelected] = useState(null)
  const [filterCompany, setFilterCompany] = useState('All')
  const [filterClass, setFilterClass] = useState('All')
  const [search, setSearch] = useState('')

  const classes = [...new Set(data.quant.byLetter.map(r => r.explore_exploit_class).filter(Boolean))]

  const filtered = useMemo(() => {
    return data.manifest.filter(letter => {
      if (filterCompany !== 'All' && letter.company !== filterCompany) return false
      if (filterClass !== 'All') {
        const q = data.quant.byLetter.find(r => r.company === letter.company && r.year === letter.year)
        if (!q || !q.explore_exploit_class.toLowerCase().includes(filterClass.toLowerCase())) return false
      }
      if (search) {
        const needle = search.toLowerCase()
        return (
          letter.company.toLowerCase().includes(needle) ||
          String(letter.year).includes(needle) ||
          (letter.title || '').toLowerCase().includes(needle)
        )
      }
      return true
    })
  }, [data, filterCompany, filterClass, search])

  const selectedQuant = selected
    ? data.quant.byLetter.find(r => r.company === selected.company && r.year === selected.year)
    : null

  return (
    <div className="pb-12">
      <PageHeader title="Letter Library" subtitle="28 CEO / shareholder letters across 4 companies, 1997–2025">
        <div className="text-sm text-slate-400">{filtered.length} of 28 letters</div>
      </PageHeader>

      {/* Filters */}
      <div className="px-8 py-4 flex flex-wrap gap-3 border-b border-slate-800">
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search company, year, title…"
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 placeholder-slate-500 w-64 focus:outline-none focus:border-slate-500"
        />
        <div className="flex gap-1">
          {['All', ...COMPANIES].map(c => (
            <button
              key={c}
              onClick={() => setFilterCompany(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filterCompany === c ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'
              }`}
              style={filterCompany === c && c !== 'All' ? { color: COMPANY_COLORS[c] } : {}}
            >
              {c}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          {['All', ...classes].map(c => (
            <button
              key={c}
              onClick={() => setFilterClass(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filterClass === c ? 'bg-slate-700 text-white' : 'text-slate-400 hover:bg-slate-800'
              }`}
            >
              {c === 'All' ? 'All classes' : c}
            </button>
          ))}
        </div>
      </div>

      <div className="px-8 py-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {filtered.map(letter => (
          <LetterCard
            key={`${letter.company}-${letter.year}`}
            letter={letter}
            quant={data.quant.byLetter.find(r => r.company === letter.company && r.year === letter.year)}
            onClick={setSelected}
          />
        ))}
      </div>

      {selected && (
        <LetterDrawer
          letter={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}
