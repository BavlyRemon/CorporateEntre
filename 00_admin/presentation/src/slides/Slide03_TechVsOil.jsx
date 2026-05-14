import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { HEADLINE_CONTRAST } from '../data'
import { PALETTE, easings } from '../theme'

const COMPANIES = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

function Bar({ value, max, color, fmt, delay }) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="relative h-5 rounded bg-white/5 overflow-hidden">
      <motion.div
        className="h-full rounded"
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 1.1, delay, ease: easings.expoOut }}
        style={{ background: color }}
      />
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.7 }}
        className="absolute right-2 top-0 h-full flex items-center text-xs font-mono text-white"
      >
        {fmt(value)}
      </motion.div>
    </div>
  )
}

export default function Slide03_TechVsOil() {
  return (
    <Slide
      splitBg="linear-gradient(95deg, rgba(118,185,0,0.10) 0%, rgba(0,0,0,1) 30%, rgba(0,0,0,1) 70%, rgba(0,51,160,0.15) 100%)"
      companies={COMPANIES}
      eyebrow="Section 04 · The headline contrast"
      title={<>Tech writes in <span className="text-green-400">horizons</span>. Oil writes in <span className="text-blue-400">discipline</span>.</>}
      kicker="Six lenses, two industries — same five themes, very different content."
    >
      <div className="grid grid-cols-[1.1fr_1.5fr] gap-8 h-full overflow-hidden">
        {/* Left: lens table */}
        <div className="space-y-2.5 overflow-hidden">
          {HEADLINE_CONTRAST.map((row, i) => {
            const max = Math.max(row.Amazon, row.Nvidia, row.Shell, row.Chevron)
            const fmt = row.fmt === 'share' ? v => v.toFixed(2) : v => v.toFixed(1)
            return (
              <motion.div
                key={row.lens}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 + i * 0.08, ease: easings.expoOut }}
              >
                <div className="text-[11px] uppercase tracking-widest text-slate-400 mb-2">{row.lens}</div>
                <div className="grid grid-cols-4 gap-2">
                  {COMPANIES.map(c => (
                    <div key={c}>
                      <Bar
                        value={row[c]} max={max} color={PALETTE[c].accent} fmt={fmt}
                        delay={0.5 + i * 0.08}
                      />
                      <div className="mt-1 text-[10px] uppercase tracking-widest" style={{ color: PALETTE[c].muted }}>
                        {c}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Right: takeaways */}
        <div className="space-y-2.5 overflow-hidden">
          {[
            { h: 'Industry trumps the firm.', b: 'Two tech firms cluster, two energy firms cluster — on five of six lenses. Industry is the largest source of variance in CEO language.' },
            { h: 'Long-term is universal.', b: 'Every firm sits at 0.87–0.94 on long-term orientation. The differentiator isn\'t time horizon — it\'s what the long term is for.' },
            { h: 'Horizon Scanning is the tech moat.', b: 'NVIDIA narrates technological inflections at 27 / 1k — ~4× the energy firms. Tech CEOs scan; energy CEOs are scanned for by cycles and regulation.' },
            { h: 'Agile Execution flips the script.', b: 'Chevron at 10.9 / 1k narrates the most operational-excellence language of anyone. Capital-intensive operations make execution the competence on display.' },
            { h: 'Strategic Options is convergent.', b: 'All four cluster around 8.5 / 1k. Every firm talks about choices — they just choose differently.' },
          ].map((p, i) => (
            <motion.div
              key={p.h}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.7 + i * 0.12, ease: easings.expoOut }}
              className="flex gap-4 group"
            >
              <div className="flex-shrink-0 w-7 h-7 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-xs font-mono text-white/60">
                {i + 1}
              </div>
              <div className="flex-1">
                <div className="font-display font-bold text-base leading-snug mb-0.5">{p.h}</div>
                <div className="text-xs text-slate-400 leading-relaxed">{p.b}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Slide>
  )
}
