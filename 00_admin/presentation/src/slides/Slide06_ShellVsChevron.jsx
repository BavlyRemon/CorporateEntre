import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { SHELL_TIMELINE, CHEVRON_TIMELINE, COMPANY_SUMMARY } from '../data'
import { PALETTE, easings } from '../theme'

const SHELL = PALETTE.Shell.accent
const CHEVRON = PALETTE.Chevron.accent

function TwinTimeline({ data, color, label, w = 380, h = 110 }) {
  const pad = 18
  const innerW = w - pad * 2
  const innerH = h - pad * 2
  const points = data.map((d, i) => ({
    ...d,
    x: pad + (i / (data.length - 1)) * innerW,
    y: pad + (1 - d.share) * innerH,
  }))
  return (
    <div>
      <div className="text-xs uppercase tracking-widest font-mono mb-2" style={{ color }}>
        {label}
      </div>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
        <motion.polyline
          fill="none" stroke={color} strokeWidth="2"
          points={points.map(p => `${p.x},${p.y}`).join(' ')}
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 1.4, ease: easings.expoOut, delay: 0.6 }}
        />
        {points.map((p, i) => (
          <motion.g key={p.year}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 0.8 + i * 0.08 }}
          >
            <circle cx={p.x} cy={p.y} r={4} fill={color} />
            <text x={p.x} y={h - 4} textAnchor="middle" fontSize={9} fontFamily="monospace" fill="#94a3b8">
              {p.year}
            </text>
            <text x={p.x} y={p.y - 8} textAnchor="middle" fontSize={9} fill="#fff" fontWeight={600}>
              {p.share.toFixed(2)}
            </text>
          </motion.g>
        ))}
      </svg>
    </div>
  )
}

function MiniStatRow({ label, leftValue, rightValue, leftColor, rightColor, fmt = v => v.toFixed(2) }) {
  const max = Math.max(leftValue, rightValue) * 1.1
  return (
    <div className="grid grid-cols-[140px_1fr_1fr] gap-4 items-center py-2 border-b border-white/5">
      <div className="text-[11px] uppercase tracking-widest text-slate-400">{label}</div>
      <div>
        <div className="h-3 rounded relative bg-white/5 overflow-hidden">
          <motion.div className="h-full rounded"
            initial={{ width: 0 }}
            animate={{ width: `${(leftValue / max) * 100}%` }}
            transition={{ duration: 1, delay: 0.5, ease: easings.expoOut }}
            style={{ background: leftColor }} />
        </div>
        <div className="text-xs font-mono mt-1" style={{ color: leftColor }}>{fmt(leftValue)}</div>
      </div>
      <div>
        <div className="h-3 rounded relative bg-white/5 overflow-hidden">
          <motion.div className="h-full rounded"
            initial={{ width: 0 }}
            animate={{ width: `${(rightValue / max) * 100}%` }}
            transition={{ duration: 1, delay: 0.6, ease: easings.expoOut }}
            style={{ background: rightColor }} />
        </div>
        <div className="text-xs font-mono mt-1" style={{ color: rightColor }}>{fmt(rightValue)}</div>
      </div>
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
      <div className="grid grid-cols-2 gap-6 h-full grid-rows-[1fr_auto] overflow-hidden">
        {/* LEFT side — Shell */}
        <motion.div
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: easings.expoOut }}
          className="rounded-2xl p-5 border border-yellow-500/25 bg-gradient-to-br from-yellow-500/[0.07] to-transparent overflow-hidden"
        >
          <div className="flex items-baseline justify-between mb-4">
            <div>
              <div className="text-xs uppercase tracking-[0.3em] font-mono text-yellow-400">Shell · UK/NL</div>
              <h3 className="font-display font-bold text-3xl mt-1">Discipline-as-virtue</h3>
            </div>
            <div className="text-right">
              <div className="font-display text-4xl font-bold" style={{ color: SHELL }}>0.11</div>
              <div className="text-[10px] uppercase tracking-widest text-slate-400">Explore share</div>
            </div>
          </div>
          <TwinTimeline data={SHELL_TIMELINE} color={SHELL} label="Explore share over time" />
          <div className="mt-3 space-y-1.5 text-xs text-slate-300">
            <p>• <span className="font-semibold text-yellow-200">Strategic Leadership 6.1 / 1k</span> — twice Chevron — driven by <em>disciplined, decisive, responsible, stewardship</em>.</p>
            <p>• Lower-carbon vocabulary is <span className="font-semibold text-yellow-200">persistent</span> from 2014 — bounded but always present.</p>
            <p>• CEO is positioned as a steward managing legitimacy, not a deal-maker chasing returns.</p>
          </div>
        </motion.div>

        {/* RIGHT side — Chevron */}
        <motion.div
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.45, ease: easings.expoOut }}
          className="rounded-2xl p-5 border border-blue-500/25 bg-gradient-to-bl from-blue-500/[0.08] to-transparent overflow-hidden"
        >
          <div className="flex items-baseline justify-between mb-4">
            <div>
              <div className="text-xs uppercase tracking-[0.3em] font-mono text-blue-300">Chevron · USA</div>
              <h3 className="font-display font-bold text-3xl mt-1">Operational excellence</h3>
            </div>
            <div className="text-right">
              <div className="font-display text-4xl font-bold" style={{ color: CHEVRON }}>0.27</div>
              <div className="text-[10px] uppercase tracking-widest text-slate-400">Explore share</div>
            </div>
          </div>
          <TwinTimeline data={CHEVRON_TIMELINE} color={CHEVRON} label="Explore share over time" />
          <div className="mt-3 space-y-1.5 text-xs text-slate-300">
            <p>• <span className="font-semibold text-blue-300">Agile Execution 10.9 / 1k</span> — top of the corpus — <em>efficient, reliable, safety, process, capital discipline</em>.</p>
            <p>• Lower-carbon language is <span className="font-semibold text-blue-300">episodic</span>: peaks in 2021 (New Energies launch), recedes by 2023–24.</p>
            <p>• CEO positioned as an operator running a returns machine; customer-share 0.30 — lowest in the corpus.</p>
          </div>
        </motion.div>

        {/* Cross-cutting comparison band */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.9, ease: easings.expoOut }}
          className="col-span-2 grid grid-cols-2 gap-6"
        >
          <div className="rounded-xl border border-white/10 bg-black/30 backdrop-blur-sm p-4">
            <div className="text-xs uppercase tracking-widest font-mono text-slate-400 mb-3">
              Same lens · different choice
            </div>
            <MiniStatRow label="Strategic Leadership /1k"
              leftValue={6.1} rightValue={3.0}
              leftColor={SHELL} rightColor={CHEVRON} fmt={v => v.toFixed(1)} />
            <MiniStatRow label="Agile Execution /1k"
              leftValue={6.4} rightValue={10.9}
              leftColor={SHELL} rightColor={CHEVRON} fmt={v => v.toFixed(1)} />
            <MiniStatRow label="Customer share"
              leftValue={0.38} rightValue={0.30}
              leftColor={SHELL} rightColor={CHEVRON} />
            <MiniStatRow label="Risk vs performance"
              leftValue={0.15} rightValue={0.25}
              leftColor={SHELL} rightColor={CHEVRON} />
          </div>
          <div className="rounded-xl border border-white/10 bg-black/30 backdrop-blur-sm p-4 text-xs leading-relaxed text-slate-300">
            <div className="text-xs uppercase tracking-widest font-mono text-slate-400 mb-3">
              The cultural finding
            </div>
            <p>
              Both share <span className="font-semibold text-white">Purpose, Vision, and Governance</span> at ~10 / 1k —
              but the <em>content</em> diverges. Shell's purpose is <span className="text-yellow-200">"energy progress"</span> and
              "lower carbon" embedded in a stakeholder narrative. Chevron's purpose is <span className="text-blue-300">"returning capital to shareholders"</span>{' '}
              dressed in operational excellence.
            </p>
            <p className="mt-3">
              Same IPM theme, very different referents. The "American shareholder vs European stakeholder" reading
              isn't a stereotype — it's <span className="font-semibold text-white">measurable in the vocabulary</span>.
            </p>
          </div>
        </motion.div>
      </div>
    </Slide>
  )
}
