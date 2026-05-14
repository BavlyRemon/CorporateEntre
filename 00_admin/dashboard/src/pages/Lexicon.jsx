import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import { COMPANY_COLORS, COMPANIES } from '../utils/constants'

function CountBar({ counts, total }) {
  if (!total) return <span className="text-xs text-slate-600">0 hits</span>
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-mono text-slate-300 w-10 text-right">{total}</span>
      <div className="flex h-2 rounded overflow-hidden w-44 bg-slate-800">
        {COMPANIES.map(c => {
          const n = counts?.byCompany?.[c] || 0
          if (!n) return null
          const pct = (n / total) * 100
          return (
            <div
              key={c}
              style={{ width: `${pct}%`, background: COMPANY_COLORS[c] }}
              title={`${c}: ${n}`}
            />
          )
        })}
      </div>
    </div>
  )
}

function EntryCard({ entry }) {
  return (
    <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/40">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-base font-semibold text-slate-100">{entry.base}</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded">
              {entry.kind}
            </span>
            {entry.stem === false && (
              <span className="text-[10px] uppercase tracking-wider text-amber-400 border border-amber-700 px-1.5 py-0.5 rounded">
                literal only
              </span>
            )}
          </div>
          {entry.aliases?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {entry.aliases.map(a => (
                <span key={a} className="text-xs bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                  {a}
                </span>
              ))}
            </div>
          )}
          {entry.excludes?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              <span className="text-[10px] text-rose-400 mr-1 self-center">EXCLUDE</span>
              {entry.excludes.map(a => (
                <span key={a} className="text-xs bg-rose-950/40 text-rose-300 px-1.5 py-0.5 rounded font-mono line-through">
                  {a}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex-shrink-0">
          <CountBar counts={entry.counts} total={entry.counts?.total || 0} />
        </div>
      </div>
      {entry.note && (
        <div className="mt-3 border-l-2 border-blue-500/40 bg-blue-950/20 pl-3 pr-3 py-2 rounded-r">
          <div className="text-[10px] uppercase tracking-wider text-blue-400 mb-1">
            Review note · <span className="font-mono normal-case tracking-normal text-slate-500">{entry.noteKey}</span>
          </div>
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{entry.note}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

function CategoryBlock({ category, search }) {
  const visible = useMemo(() => {
    if (!search) return category.entries
    const q = search.toLowerCase()
    return category.entries.filter(e => {
      const haystack = [e.base, ...(e.aliases || []), ...(e.excludes || []), e.note || '']
        .join(' ').toLowerCase()
      return haystack.includes(q)
    })
  }, [category.entries, search])

  if (!visible.length) return null

  const totalHits = visible.reduce((s, e) => s + (e.counts?.total || 0), 0)

  return (
    <div className="card p-5">
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-slate-500">{category.group}</div>
          <h3 className="text-lg font-bold text-white">{category.name}</h3>
        </div>
        <div className="text-xs text-slate-500">
          {visible.length} entries · {totalHits} total hits
        </div>
      </div>
      <div className="grid gap-3">
        {visible.map(e => <EntryCard key={e.base + (e.aliases || []).join('|')} entry={e} />)}
      </div>
    </div>
  )
}

export default function Lexicon() {
  const data = useData()
  const lex = data?.lexicon
  const [search, setSearch] = useState('')
  const [group, setGroup] = useState('all')

  if (!lex) {
    return (
      <div className="p-8 text-slate-400">No lexicon data — rerun <code>build_dashboard_data.py</code>.</div>
    )
  }

  const filtered = lex.categories.filter(c => group === 'all' || c.group === group)
  const totalEntries = lex.categories.reduce((s, c) => s + c.entries.length, 0)
  const totalNotes = lex.categories.reduce(
    (s, c) => s + c.entries.filter(e => e.note).length, 0
  ) + (lex.subthemes || []).reduce(
    (s, st) => s + st.entries.filter(e => e.note).length, 0
  )

  return (
    <div>
      <PageHeader
        title="Lexicon"
        subtitle="Keyword dictionaries used by the analysis. Edit 00_admin/keyword_review_notes.md to leave review notes; they appear inline below."
      />
      <div className="p-8 space-y-5">
        <div className="card p-4 flex items-center gap-4 flex-wrap">
          <div className="flex-1 min-w-[240px]">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search base, alias, exclude, or note text…"
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex gap-1">
            {['all', 'IPM', 'Cross-cutting'].map(g => (
              <button
                key={g}
                onClick={() => setGroup(g)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  group === g ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {g === 'all' ? 'All' : g}
              </button>
            ))}
          </div>
          <div className="text-xs text-slate-500">
            {totalEntries} entries · {totalNotes} notes
          </div>
        </div>

        {lex.notesUnmatched?.length > 0 && (
          <div className="card p-4 border-amber-700/50">
            <div className="text-xs uppercase tracking-wider text-amber-400 mb-1">Unmatched notes</div>
            <div className="text-xs text-slate-400 mb-2">
              These note headers in <code className="text-slate-300">keyword_review_notes.md</code> don't match any dictionary entry:
            </div>
            <ul className="text-xs font-mono text-amber-300 space-y-0.5">
              {lex.notesUnmatched.map(k => <li key={k}>## {k}</li>)}
            </ul>
          </div>
        )}

        {filtered.map(cat => (
          <CategoryBlock key={cat.group + '/' + cat.name} category={cat} search={search} />
        ))}
      </div>
    </div>
  )
}
