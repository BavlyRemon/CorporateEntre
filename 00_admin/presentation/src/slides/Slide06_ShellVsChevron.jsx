import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { SHELL_TIMELINE, CHEVRON_TIMELINE } from '../data'
import { PALETTE, easings } from '../theme'

const SHELL = PALETTE.Shell.accent
const CHEVRON = PALETTE.Chevron.accent

function TwinTimeline({ data, color }) {
  const w = 380, h = 90, pad = 18
  const innerW = w - pad * 2
  const innerH = h - pad * 2
  const points = data.map((d, i) => ({
    ...d,
    x: pad + (i / (data.length - 1)) * innerW,
    y: pad + (1 - d.share) * innerH,
  }))
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ maxHeight: 90 }}>
      <motion.polyline
        fill="none" stroke={color} strokeWidth="2"
        points={points.map(p => `${p.x},${p.y}`).join(' ')}
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ duration: 1.4, ease: easings.expoOut, delay: 0.6 }}
      />
      {points.map((p, i) => (
        <motion.g key={p.year}
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 0.8 + i * 0.07 }}
        >
          <circle cx={p.x} cy={p.y} r={3.5} fill={color} />
          <text x={p.x} y={h - 3} textAnchor="middle" fontSize={8.5} fontFamily="monospace" fill="#94a3b8">
            {p.year}
          </text>
          <text x={p.x} y={p.y - 7} textAnchor="middle" fontSize={8.5} fill="#fff" fontWeight={600}>
            {p.share.toFixed(2)}
          </text>
        </motion.g>
      ))}
    </svg>
  )
}

function StatRow({ label, left, right }) {
  const max = Math.max(left.v, right.v) * 1.1
  return (
    <div className="grid grid-cols-[110px_1fr_1fr] gap-3 items-center py-1.5 border-b border-white/5 last:border-0">
      <div className="text-[10px] uppercase tracking-widest text-slate-400">{label}</div>
      {[left, right].map((s, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="flex-1 h-2 rounded bg-white/5 overflow-hidden">
            <motion.div
              className="h-full rounded"
              initial={{ width: 0 }}
              animate={{ width: `${(s.v / max) * 100}%` }}
              transition={{ duration: 0.9, delay: 0.7 + i * 0.1, ease: easings.expoOut }}
              style={{ background: s.color }}
            />
          </div>
          <div className="text-[11px] font-mono w-9 text-right" style={{ color: s.color }}>
            {s.label}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Slide06_ShellVsChevron() {
  return (
    <Slide
      splitBg="linear-gradient(95deg, #1A1505 0%, #2A2208 35%, #0A1733 65%, #050C1F 100%)"
      companies={['Shell', 'Chevron']}
      eyebrow="Section 07 · Shell vs Chevron"
      title={<>European stewardship. <span className="text-amber-300">/</span> American shareholder.</>}
      kicker="Both firms exploit — but in two different dialects of exploitation."
    >
      <div className="h-full flex flex-col gap-3 min-h-0">

        {/* Two firm cards side-by-side */}
        <div className="grid grid-cols-2 gap-5 flex-1 min-h-0">
          <motion.div
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.3, ease: easings.expoOut }}
            className="rounded-2xl p-4 border border-yellow-500/25 bg-gradient-to-br from-yellow-500/[0.07] to-transparent overflow-hidden flex flex-col"
          >
            <div className="flex items-baseline justify-between mb-3">
              <div>
                <div className="text-[10px] uppercase tracking-[0.3em] font-mono text-yellow-400">Shell · UK/NL</div>
                <h3 className="font-display font-bold text-2xl mt-0.5">Discipline-as-virtue</h3>
              </div>
              <div className="text-right">
                <div className="font-display text-3xl font-bold leading-none" style={{ color: SHELL }}>0.11</div>
                <div className="text-[9px] uppercase tracking-widest text-slate-400 mt-1">Explore share</div>
              </div>
            </div>
            <TwinTimeline data={SHELL_TIMELINE} color={SHELL} />
            <div className="mt-3 space-y-1.5 text-xs text-slate-300 leading-relaxed">
              <p>• <span className="font-semibold text-yellow-200">Strategic Leadership 6.1 /1k</span> — twice Chevron — <em>disciplined, decisive, responsible, stewardship</em>.</p>
              <p>• Lower-carbon vocabulary is <span className="font-semibold text-yellow-200">persistent</span> from 2014 — bounded but always present.</p>
              <p>• Steward managing legitimacy, not deal-maker chasing returns.</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.45, ease: easings.expoOut }}
            className="rounded-2xl p-4 border border-blue-500/25 bg-gradient-to-bl from-blue-500/[0.08] to-transparent overflow-hidden flex flex-col"
          >
            <div className="flex items-baseline justify-between mb-3">
              <div>
                <div className="text-[10px] uppercase tracking-[0.3em] font-mono text-blue-300">Chevron · USA</div>
                <h3 className="font-display font-bold text-2xl mt-0.5">Operational excellence</h3>
              </div>
              <div className="text-right">
                <div className="font-display text-3xl font-bold leading-none" style={{ color: CHEVRON }}>0.27</div>
                <div className="text-[9px] uppercase tracking-widest text-slate-400 mt-1">Explore share</div>
              </div>
            </div>
            <TwinTimeline data={CHEVRON_TIMELINE} color={CHEVRON} />
            <div className="mt-3 space-y-1.5 text-xs text-slate-300 leading-relaxed">
              <p>• <span className="font-semibold text-blue-300">Agile Execution 10.9 /1k</span> — top of corpus — <em>efficient, reliable, safety, process, capital discipline</em>.</p>
              <p>• Lower-carbon is <span className="font-semibold text-blue-300">episodic</span>: peaks 2021 (New Energies), recedes 2023–24.</p>
              <p>• Operator running a returns machine; customer-share 0.30 — lowest in corpus.</p>
            </div>
          </motion.div>
        </div>

        {/* Compact comparison strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.9, ease: easings.expoOut }}
          className="rounded-xl border border-white/10 bg-black/30 backdrop-blur-sm p-3 grid grid-cols-[1.2fr_1fr] gap-5 flex-shrink-0"
        >
          <div>
            <div className="text-[10px] uppercase tracking-widest font-mono text-slate-400 mb-1.5">
              Same lens · different choice
            </div>
            <StatRow label="Strategic Leadership /1k"
              left={{ v: 6.1, label: '6.1', color: SHELL }}
              right={{ v: 3.0, label: '3.0', color: CHEVRON }} />
            <StatRow label="Agile Execution /1k"
              left={{ v: 6.4, label: '6.4', color: SHELL }}
              right={{ v: 10.9, label: '10.9', color: CHEVRON }} />
            <StatRow label="Customer share"
              left={{ v: 0.38, label: '0.38', color: SHELL }}
              right={{ v: 0.30, label: '0.30', color: CHEVRON }} />
          </div>
          <div className="text-xs leading-relaxed text-slate-300">
            <div className="text-[10px] uppercase tracking-widest font-mono text-slate-400 mb-1.5">
              The cultural finding
            </div>
            <p>
              Both share <span className="font-semibold text-white">Purpose, Vision &amp; Governance</span> at ~10 /1k, but the
              <em> content</em> diverges: Shell's <span className="text-yellow-200">"energy progress"</span> /
              lower carbon vs. Chevron's <span className="text-blue-300">"return capital to shareholders"</span>.
              Same IPM theme, very different referents — <span className="font-semibold text-white">measurable in the vocabulary</span>.
            </p>
          </div>
        </motion.div>

      </div>
    </Slide>
  )
}
