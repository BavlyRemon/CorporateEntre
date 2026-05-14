import { X } from 'lucide-react'
import { useData } from '../hooks/useData'
import { COMPANY_COLORS, IPM_SHORT, IPM_THEMES, IPM_COLORS } from '../utils/constants'
import { fmtPct, fmt1, fmtInt } from '../utils/format'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip
} from 'recharts'
import ChartTooltip from './ChartTooltip'
import CompanyBadge from './CompanyBadge'

export default function LetterDrawer({ letter, onClose }) {
  const data = useData()
  if (!letter) return null

  const summary = data.letterSummaries.find(
    s => s.company === letter.company && s.year === letter.year
  )

  const quant = data.quant.byLetter.find(
    r => r.company === letter.company && r.year === letter.year
  )

  const companyLetters = data.quant.byLetter.filter(r => r.company === letter.company)

  const radarData = IPM_THEMES.map((theme, i) => {
    const key = `${theme}_per_1000`
    const letterVal = quant?.[key] ?? 0
    const companyMean = companyLetters.length
      ? companyLetters.reduce((s, r) => s + (r[key] ?? 0), 0) / companyLetters.length
      : 0
    return {
      subject: IPM_SHORT[theme],
      Letter: Number(letterVal.toFixed(2)),
      CompanyMean: Number(companyMean.toFixed(2)),
    }
  })

  const color = COMPANY_COLORS[letter.company] || '#6366f1'
  const exploitClass = quant?.explore_exploit_class || letter.explore_exploit_class || '—'

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="w-[600px] bg-slate-900 border-l border-slate-700 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-5 border-b border-slate-800">
          <div>
            <CompanyBadge company={letter.company} size="lg" />
            <div className="text-xl font-bold text-white mt-2">{letter.year}</div>
            {summary?.ceo && <div className="text-slate-400 text-sm mt-0.5">{summary.ceo}</div>}
            <div className="text-slate-500 text-xs mt-1 font-mono">{letter.title}</div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 mt-1">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
          {/* Quick stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-800 rounded-lg p-3 text-center">
              <div className="text-xs text-slate-500 mb-1">Words</div>
              <div className="text-lg font-bold text-white">{fmtInt(letter.word_count)}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-3 text-center">
              <div className="text-xs text-slate-500 mb-1">Explore share</div>
              <div className="text-lg font-bold" style={{ color }}>
                {fmtPct(quant?.explore_share_of_explore_exploit)}
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-3 text-center">
              <div className="text-xs text-slate-500 mb-1">Class</div>
              <div className="text-sm font-semibold text-slate-200 leading-tight">{exploitClass}</div>
            </div>
          </div>

          {/* IPM Radar */}
          <div>
            <div className="text-sm font-semibold text-slate-300 mb-3">IPM Theme Profile vs Company Mean</div>
            <div style={{ height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <PolarRadiusAxis tick={{ fill: '#64748b', fontSize: 9 }} />
                  <Radar name="This letter" dataKey="Letter" stroke={color} fill={color} fillOpacity={0.25} />
                  <Radar name="Company mean" dataKey="CompanyMean" stroke="#64748b" fill="#64748b" fillOpacity={0.1} strokeDasharray="4 2" />
                  <Tooltip content={<ChartTooltip />} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* IPM counts */}
          {quant && (
            <div>
              <div className="text-sm font-semibold text-slate-300 mb-2">IPM Counts (per 1,000 words)</div>
              <div className="space-y-2">
                {IPM_THEMES.map((theme, i) => {
                  const val = quant[`${theme}_per_1000`] ?? 0
                  const max = Math.max(...companyLetters.map(r => r[`${theme}_per_1000`] ?? 0), 1)
                  return (
                    <div key={theme} className="flex items-center gap-3">
                      <div className="w-20 text-right text-xs text-slate-400 shrink-0">{IPM_SHORT[theme]}</div>
                      <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${(val / max) * 100}%`, background: IPM_COLORS[i] }}
                        />
                      </div>
                      <div className="w-10 text-right text-xs font-mono text-slate-300">{fmt1(val)}</div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Summary bullets */}
          {summary?.bullets?.length > 0 && (
            <div>
              <div className="text-sm font-semibold text-slate-300 mb-3">Key Points</div>
              <ul className="space-y-2">
                {summary.bullets.map((b, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <span className="text-slate-600 mt-0.5">•</span>
                    <span className="text-slate-300">{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Rationale */}
          {(() => {
            const rat = data.rationale?.find(r => r.company === letter.company && r.year === letter.year)
            if (!rat) return null
            return (
              <div>
                <div className="text-sm font-semibold text-slate-300 mb-2">Why This Year Was Selected</div>
                <div className="bg-slate-800/60 rounded-lg p-4 text-sm text-slate-300 space-y-2">
                  <div><span className="text-slate-500">Phase:</span> {rat.strategic_phase}</div>
                  <div><span className="text-slate-500">Rationale:</span> {rat.inclusion_rationale}</div>
                </div>
              </div>
            )
          })()}
        </div>
      </div>
    </div>
  )
}
