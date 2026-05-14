import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import Quote from '../components/Quote'
import { SHELL_TIMELINE, CHEVRON_TIMELINE } from '../data'
import { PALETTE, easings } from '../theme'

const SHELL = PALETTE.Shell.accent
const CHEVRON = PALETTE.Chevron.accent

// One chart showing BOTH timelines on the same x-axis (years 2013–2025).
// The point: Shell stays flat, Chevron has one volatile spike in 2021.
function CombinedTimeline({ visible }) {
  const w = 1100, h = 280, pad = 60
  const innerW = w - pad * 2
  const innerH = h - 80
  const top = 40

  const allYears = [2013, 2014, 2015, 2016, 2018, 2020, 2021, 2022, 2023, 2024, 2025]
  const yearX = (y) => pad + ((y - 2013) / (2025 - 2013)) * innerW
  const shareY = (s) => top + (1 - s / 0.6) * innerH
  const ambidextrousY = shareY(0.5)

  const shellPts = SHELL_TIMELINE.map(d => ({ ...d, x: yearX(d.year), y: shareY(d.share) }))
  const chevronPts = CHEVRON_TIMELINE.map(d => ({ ...d, x: yearX(d.year), y: shareY(d.share) }))
  const chevronPeak = chevronPts.find(p => p.year === 2021)

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full" preserveAspectRatio="xMidYMid meet">
      {[0, 0.2, 0.4, 0.6].map(v => (
        <g key={v}>
          <line x1={pad} y1={shareY(v)} x2={w - pad} y2={shareY(v)}
                stroke="#ffffff" strokeOpacity="0.07" />
          <text x={pad - 12} y={shareY(v) + 4} textAnchor="end" fontSize={10}
                fontFamily="monospace" fill="#64748b">{v.toFixed(1)}</text>
        </g>
      ))}

      <motion.line
        x1={pad} y1={ambidextrousY} x2={w - pad} y2={ambidextrousY}
        stroke="#FBBF24" strokeOpacity="0.4" strokeDasharray="5 5" strokeWidth="1.5"
        initial={{ pathLength: 0 }} animate={{ pathLength: visible ? 1 : 0 }}
        transition={{ duration: 1.2, delay: 0.4, ease: easings.expoOut }}
      />
      {/* Threshold label sits in the middle of the empty area, above the line,
          between Shell's and Chevron's curves where nothing else is plotted. */}
      <motion.text
        x={pad + innerW * 0.18} y={ambidextrousY - 6} textAnchor="start"
        fontSize={10} fontFamily="monospace" fill="#FBBF24"
        initial={{ opacity: 0 }} animate={{ opacity: visible ? 0.75 : 0 }}
        transition={{ delay: 1.4 }}
      >
        ambidextrous threshold (0.50)
      </motion.text>

      {allYears.map(y => (
        <text key={y} x={yearX(y)} y={h - 14} textAnchor="middle" fontSize={11}
              fontFamily="monospace" fill="#64748b">{y}</text>
      ))}
      {/* y-axis label, anchored at start so it never gets clipped */}
      <text x={pad} y={top - 14} textAnchor="start" fontSize={10}
            fontFamily="monospace" fill="#64748b">explore share</text>

      <motion.polyline
        fill="none" stroke={SHELL} strokeWidth="2.5"
        points={shellPts.map(p => `${p.x},${p.y}`).join(' ')}
        initial={{ pathLength: 0 }} animate={{ pathLength: visible ? 1 : 0 }}
        transition={{ duration: 1.6, delay: 0.6, ease: easings.expoOut }}
      />
      {shellPts.map((p, i) => (
        <motion.circle key={`s-${p.year}`}
          cx={p.x} cy={p.y} r={5} fill={SHELL}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: visible ? 1 : 0, scale: visible ? 1 : 0 }}
          transition={{ delay: 0.7 + i * 0.07, duration: 0.4, ease: easings.expoOut }}
        />
      ))}

      <motion.polyline
        fill="none" stroke={CHEVRON} strokeWidth="2.5"
        points={chevronPts.map(p => `${p.x},${p.y}`).join(' ')}
        initial={{ pathLength: 0 }} animate={{ pathLength: visible ? 1 : 0 }}
        transition={{ duration: 1.6, delay: 0.9, ease: easings.expoOut }}
      />
      {chevronPts.map((p, i) => {
        const isPeak = p.year === 2021
        return (
          <motion.circle key={`c-${p.year}`}
            cx={p.x} cy={p.y} r={isPeak ? 7 : 5}
            fill={CHEVRON}
            stroke={isPeak ? '#FBBF24' : 'none'} strokeWidth={isPeak ? 2 : 0}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: visible ? 1 : 0, scale: visible ? 1 : 0 }}
            transition={{ delay: 1.0 + i * 0.07, duration: 0.4, ease: easings.expoOut }}
          />
        )
      })}

      {chevronPeak && (
        <motion.g
          initial={{ opacity: 0 }} animate={{ opacity: visible ? 1 : 0 }}
          transition={{ delay: 1.9, duration: 0.6 }}
        >
          {/* Arrow comes from BELOW the peak — keeps the upper-right area
              clear so the threshold-label and annotation don't fight. */}
          <line x1={chevronPeak.x} y1={chevronPeak.y + 12}
                x2={chevronPeak.x} y2={chevronPeak.y + 56}
                stroke="#FBBF24" strokeWidth="1.5" />
          <polygon
            points={`${chevronPeak.x},${chevronPeak.y + 12} ${chevronPeak.x - 5},${chevronPeak.y + 22} ${chevronPeak.x + 5},${chevronPeak.y + 22}`}
            fill="#FBBF24"
          />
          <text x={chevronPeak.x} y={chevronPeak.y + 72}
                textAnchor="middle"
                fontSize={11} fontWeight={600} fill="#FBBF24">
            2021 · New Energies launch
          </text>
          <text x={chevronPeak.x} y={chevronPeak.y + 86}
                textAnchor="middle"
                fontSize={10} fill="#FBBF24" fillOpacity="0.75">
            the one ambidextrous year
          </text>
        </motion.g>
      )}

    </svg>
  )
}

// Stand-alone legend rendered as HTML above the SVG, so it never collides
// with anything inside the chart.
function ChartLegend({ visible }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: visible ? 1 : 0, y: visible ? 0 : -6 }}
      transition={{ duration: 0.6, delay: 0.2, ease: easings.expoOut }}
      className="absolute top-2 right-4 flex items-center gap-5 text-[11px] font-mono z-10"
    >
      <div className="flex items-center gap-2">
        <div className="w-4 h-[3px] rounded" style={{ background: SHELL }} />
        <span className="font-semibold" style={{ color: SHELL }}>Shell</span>
        <span className="text-slate-400">— flat at 0.10</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-4 h-[3px] rounded" style={{ background: CHEVRON }} />
        <span className="font-semibold" style={{ color: CHEVRON }}>Chevron</span>
        <span className="text-slate-400">— one volatile spike</span>
      </div>
    </motion.div>
  )
}

// Compact stat row: label on top, two bars side-by-side underneath.
// Less horizontal crunch than the prior 3-column grid.
function StatRow({ label, left, right, delay = 0, visible }) {
  const max = Math.max(left.v, right.v) * 1.1
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: visible ? 1 : 0, x: visible ? 0 : -10 }}
      transition={{ duration: 0.5, delay: visible ? delay : 0, ease: easings.expoOut }}
      className="py-1.5 border-b border-white/5 last:border-0"
    >
      <div className="text-[10px] uppercase tracking-widest text-slate-400 mb-1">{label}</div>
      <div className="grid grid-cols-2 gap-3">
        {[left, right].map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="flex-1 h-2 rounded bg-white/5 overflow-hidden min-w-0">
              <motion.div
                className="h-full rounded"
                initial={{ width: 0 }}
                animate={{ width: visible ? `${(s.v / max) * 100}%` : 0 }}
                transition={{ duration: 0.9, delay: (visible ? delay : 0) + 0.15, ease: easings.expoOut }}
                style={{ background: s.color }}
              />
            </div>
            <div className="text-[11px] font-mono w-9 text-right flex-shrink-0" style={{ color: s.color }}>
              {s.label}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

export default function Slide06_ShellVsChevron({ stage = 0 }) {
  // Flex weights per section per stage — the three regions ALWAYS share the
  // full height; non-visible regions get weight 0 so they collapse to nothing.
  const chartGrow = stage === 0 ? 4 : 2.2
  const cardsGrow = stage >= 1 ? 2 : 0
  const stripGrow = stage >= 2 ? 1.1 : 0

  return (
    <Slide
      splitBg="linear-gradient(95deg, #1A1505 0%, #2A2208 35%, #0A1733 65%, #050C1F 100%)"
      companies={['Shell', 'Chevron']}
      eyebrow="Section 07 · Shell vs Chevron"
      title={<>European stewardship. <span className="text-amber-300">/</span> American shareholder.</>}
      kicker="Both firms exploit — but one stays flat at 0.10, the other has one volatile moment."
    >
      <div className="h-full flex flex-col gap-3 min-h-0">

        {/* Chart */}
        <motion.div
          className="relative min-h-0"
          animate={{ flexGrow: chartGrow }}
          transition={{ duration: 0.6, ease: easings.expoOut }}
          style={{ flexBasis: 0 }}
        >
          <ChartLegend visible={true} />
          <CombinedTimeline visible={true} />
        </motion.div>

        {/* Firm cards (stage >= 1) */}
        <motion.div
          className="min-h-0 overflow-hidden"
          animate={{
            flexGrow: cardsGrow,
            opacity: stage >= 1 ? 1 : 0,
          }}
          transition={{ duration: 0.6, ease: easings.expoOut }}
          style={{ flexBasis: 0 }}
        >
          <div className="grid grid-cols-2 gap-4 h-full">
            <div className="rounded-xl p-4 border border-yellow-500/25 bg-gradient-to-br from-yellow-500/[0.07] to-transparent overflow-hidden flex flex-col">
              <div className="flex items-baseline justify-between mb-2 flex-shrink-0">
                <div>
                  <div className="text-[10px] uppercase tracking-[0.3em] font-mono text-yellow-400">Shell · UK/NL</div>
                  <h3 className="font-display font-bold text-xl mt-0.5">Discipline-as-virtue</h3>
                </div>
                <div className="text-right">
                  <div className="font-display text-2xl font-bold leading-none" style={{ color: SHELL }}>0.11</div>
                  <div className="text-[9px] uppercase tracking-widest text-slate-400 mt-0.5">explore share</div>
                </div>
              </div>
              <Quote
                text="Powering Progress combines our ambitions under four goals: generating shareholder value, achieving net-zero emissions, powering lives, and respecting nature."
                cite="Shell 2020 CEO Review · Ben van Beurden"
                color={SHELL}
                visible={stage >= 1}
                delay={0.15}
              />
              <ul className="mt-2 space-y-1 text-xs text-slate-300 leading-relaxed">
                <li>• <span className="text-yellow-200">Strategic Leadership 6.1 /1k</span> — twice Chevron's</li>
                <li>• Lower-carbon vocabulary <span className="text-yellow-200">persistent</span> from 2014 onward</li>
                <li>• Stakeholder framing, not deal-maker framing</li>
              </ul>
            </div>

            <div className="rounded-xl p-4 border border-blue-500/25 bg-gradient-to-bl from-blue-500/[0.08] to-transparent overflow-hidden flex flex-col">
              <div className="flex items-baseline justify-between mb-2 flex-shrink-0">
                <div>
                  <div className="text-[10px] uppercase tracking-[0.3em] font-mono text-blue-300">Chevron · USA</div>
                  <h3 className="font-display font-bold text-xl mt-0.5">Operational excellence</h3>
                </div>
                <div className="text-right">
                  <div className="font-display text-2xl font-bold leading-none" style={{ color: CHEVRON }}>0.27</div>
                  <div className="text-[9px] uppercase tracking-widest text-slate-400 mt-0.5">explore share</div>
                </div>
              </div>
              <Quote
                text="Our focus on 'higher returns, lower carbon' is underpinned by operational excellence, cost discipline and capital discipline — and financial strength."
                cite="Chevron 2021 Letter to Stockholders · Mike Wirth"
                color={CHEVRON}
                visible={stage >= 1}
                delay={0.3}
              />
              <ul className="mt-2 space-y-1 text-xs text-slate-300 leading-relaxed">
                <li>• <span className="text-blue-300">Agile Execution 10.9 /1k</span> — top of the corpus</li>
                <li>• Lower-carbon language <span className="text-blue-300">episodic</span> — spikes 2021, recedes by 2024</li>
                <li>• Customer share 0.30 — lowest in corpus (audience = shareholder)</li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Comparison strip (stage >= 2) */}
        <motion.div
          className="min-h-0 overflow-hidden"
          animate={{
            flexGrow: stripGrow,
            opacity: stage >= 2 ? 1 : 0,
          }}
          transition={{ duration: 0.6, ease: easings.expoOut }}
          style={{ flexBasis: 0 }}
        >
          <div className="rounded-xl border border-white/10 bg-black/30 backdrop-blur-sm p-4 grid grid-cols-2 gap-6 h-full overflow-hidden">
            <div className="min-w-0">
              <div className="text-[10px] uppercase tracking-widest font-mono text-slate-400 mb-2">
                Same lens · different choice
              </div>
              <StatRow visible={stage >= 2} delay={0.05} label="Strategic Leadership /1k"
                left={{ v: 6.1, label: '6.1', color: SHELL }}
                right={{ v: 3.0, label: '3.0', color: CHEVRON }} />
              <StatRow visible={stage >= 2} delay={0.15} label="Agile Execution /1k"
                left={{ v: 6.4, label: '6.4', color: SHELL }}
                right={{ v: 10.9, label: '10.9', color: CHEVRON }} />
              <StatRow visible={stage >= 2} delay={0.25} label="Customer share"
                left={{ v: 0.38, label: '0.38', color: SHELL }}
                right={{ v: 0.30, label: '0.30', color: CHEVRON }} />
            </div>
            <div className="text-xs leading-relaxed text-slate-300 min-w-0">
              <div className="text-[10px] uppercase tracking-widest font-mono text-slate-400 mb-2">
                The cultural finding
              </div>
              <p>
                Both share <span className="font-semibold text-white">Purpose, Vision &amp; Governance</span> at ~10 /1k, but the
                <em> content</em> diverges: Shell's <span className="text-yellow-200">"energy progress"</span> /
                lower carbon vs. Chevron's <span className="text-blue-300">"return capital to shareholders"</span>.
                Same IPM theme, very different referents — <span className="font-semibold text-white">measurable in the vocabulary</span>.
              </p>
            </div>
          </div>
        </motion.div>

      </div>
    </Slide>
  )
}
