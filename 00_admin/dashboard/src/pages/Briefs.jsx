import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'
import MarkdownView from '../components/MarkdownView'

const CATEGORY_COLORS = {
  'Company Briefs': 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  'Methodology Briefs': 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  'Industry Comparison': 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
}

export default function Briefs() {
  const data = useData()
  const { filename } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)

  const index = data.briefIndex || []
  const categories = [...new Set(index.map(b => b.category))]

  const activeBrief = filename
    ? index.find(b => b.filename === filename)
    : index[0]

  useEffect(() => {
    if (!activeBrief) return
    setLoading(true)
    setContent('')
    fetch(`/src/data/briefs/${activeBrief.filename}`)
      .then(r => r.ok ? r.text() : Promise.reject(`HTTP ${r.status}`))
      .then(text => { setContent(text); setLoading(false) })
      .catch(() => { setContent('*Brief not found.*'); setLoading(false) })
  }, [activeBrief?.filename])

  return (
    <div className="pb-12 flex flex-col h-full">
      <PageHeader title="Brief Library" subtitle="Qualitative briefs, methodology notes, and industry comparisons" />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 shrink-0 border-r border-slate-800 overflow-y-auto">
          <div className="py-3">
            {categories.map(cat => (
              <div key={cat} className="mb-4">
                <div className="px-4 py-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">{cat}</div>
                {index.filter(b => b.category === cat).map(brief => (
                  <button
                    key={brief.filename}
                    onClick={() => navigate(`/briefs/${brief.filename}`)}
                    className={`w-full text-left px-4 py-2 text-sm transition-colors ${
                      activeBrief?.filename === brief.filename
                        ? 'bg-slate-800 text-white border-r-2 border-blue-500'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    {brief.title}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {activeBrief && (
            <div className="mb-6 flex items-center gap-3">
              <span className={`badge border text-xs px-2.5 py-1 ${CATEGORY_COLORS[activeBrief.category] || 'bg-slate-700 text-slate-400'}`}>
                {activeBrief.category}
              </span>
              <h1 className="text-xl font-bold text-white">{activeBrief.title}</h1>
            </div>
          )}
          {loading
            ? <div className="text-slate-500 text-sm animate-pulse">Loading…</div>
            : <MarkdownView content={content} />
          }
        </div>
      </div>
    </div>
  )
}
