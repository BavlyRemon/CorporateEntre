import { useState } from 'react'
import { useData } from '../hooks/useData'
import PageHeader from '../components/PageHeader'

const RESULT_COLORS = {
  supported: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  'not supported': 'bg-red-500/15 text-red-300 border-red-500/30',
  partial: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  nuance: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
}

function resultColor(result) {
  if (!result) return 'bg-slate-700 text-slate-400 border-slate-600'
  const lower = result.toLowerCase()
  if (lower.includes('not support')) return RESULT_COLORS['not supported']
  if (lower.includes('support')) return RESULT_COLORS['supported']
  if (lower.includes('partial')) return RESULT_COLORS['partial']
  return RESULT_COLORS['nuance']
}

function HypothesisCard({ row }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="card overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="font-semibold text-white text-sm mb-2">{row.hypothesis}</div>
            <span className={`badge border text-xs px-2.5 py-1 ${resultColor(row.result)}`}>
              {row.result}
            </span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-slate-500 hover:text-slate-300 text-xs mt-0.5 shrink-0"
          >
            {expanded ? '▲ Less' : '▼ Evidence'}
          </button>
        </div>
        {expanded && (
          <div className="mt-4 bg-slate-800/50 rounded-lg p-4 text-sm text-slate-300 leading-relaxed">
            {row.evidence}
          </div>
        )}
      </div>
    </div>
  )
}

function OutcomeAnchor({ row }) {
  return (
    <div className="card p-5">
      <div className="flex items-start gap-3">
        <div className="text-xs font-mono text-slate-500 mt-0.5 whitespace-nowrap">{row.company} {row.year}</div>
        <div>
          <div className="text-sm font-semibold text-slate-200 mb-1">{row.outcome_anchor}</div>
          <div className="text-xs text-slate-400 leading-relaxed">{row.interpretation}</div>
        </div>
      </div>
    </div>
  )
}

export default function Hypotheses() {
  const data = useData()

  return (
    <div className="pb-12">
      <PageHeader
        title="Hypotheses & Outcomes"
        subtitle="Research hypotheses with evidence from the 28-letter corpus, plus outcome anchors"
      />

      <div className="px-8 py-6 space-y-8">
        <div>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Research Hypotheses</h2>
          <div className="space-y-3">
            {data.hypotheses.map((row, i) => <HypothesisCard key={i} row={row} />)}
          </div>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Outcome Anchors</h2>
          <p className="text-xs text-slate-500 mb-4">Concrete performance milestones that validate (or complicate) the lexical / qualitative claims</p>
          <div className="space-y-3">
            {data.outcomes.map((row, i) => <OutcomeAnchor key={i} row={row} />)}
          </div>
        </div>

        {data.ipmEvidence?.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">IPM Detailed Evidence</h2>
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr>
                      {['Company', 'IPM Dimension', 'Primary Years', 'Evidence Summary', 'Interpretive Claim'].map((h, i) => (
                        <th key={i} className="bg-slate-800 text-slate-300 font-semibold px-3 py-2 text-left border-b border-slate-700">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.ipmEvidence.map((row, i) => (
                      <tr key={i} className={`border-b border-slate-800 ${i % 2 === 0 ? '' : 'bg-slate-900/30'}`}>
                        <td className="px-3 py-2 text-slate-300 font-medium whitespace-nowrap">{row.company}</td>
                        <td className="px-3 py-2 text-slate-400">{row.ipm_dimension}</td>
                        <td className="px-3 py-2 font-mono text-slate-400 whitespace-nowrap">{row.primary_years}</td>
                        <td className="px-3 py-2 text-slate-300 max-w-xs">{row.evidence_summary}</td>
                        <td className="px-3 py-2 text-slate-400 italic max-w-xs">{row.interpretive_claim}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
