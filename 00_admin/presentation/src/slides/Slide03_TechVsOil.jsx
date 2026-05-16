import { motion, AnimatePresence } from 'framer-motion'
import Slide from '../components/Slide'
import { SPECTRA, TECH, OIL } from '../data'
import { PALETTE, easings } from '../theme'
import Logo from '../components/Logo'

const ALL = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

// ─── Spectrum: a 0–1 number line with the four firms placed on it ───────────
function Spectrum({ spec }) {
  const entries = ALL.map(c => ({ c, v: spec.values[c] }))
  const split = spec.verdict === 'split'
  const oilMax = Math.max(spec.values.Shell, spec.values.Chevron)
  const techMin = Math.min(spec.values.Amazon, spec.values.Nvidia)
  const gapL = Math.min(oilMax, techMin)
  const gapR = Math.max(oilMax, techMin)

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* end labels */}
      <div className="flex justify-between text-xs uppercase tracking-[0.3em] font-mono text-slate-500 mb-3">
        <span>← {spec.left}</span>
        <span>{spec.right} →</span>
      </div>

      <div className="relative h-44">
        {/* track */}
        <div className="absolute left-0 right-0 top-1/2 h-[3px] -translate-y-1/2 rounded-full bg-white/10" />
        {[0, 0.25, 0.5, 0.75, 1].map(t => (
          <div key={t} className="absolute top-1/2 -translate-y-1/2 w-px h-3 bg-white/15"
               style={{ left: `${t * 100}%` }} />
        ))}

        {/* gap band for "split" metrics */}
        {split && (
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 h-10 rounded"
            style={{
              left: `${gapL * 100}%`,
              width: `${(gapR - gapL) * 100}%`,
              background: 'repeating-linear-gradient(45deg, rgba(248,113,113,0.10) 0 8px, transparent 8px 16px)',
              border: '1px dashed rgba(248,113,113,0.35)',
            }}
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{ opacity: 1, scaleX: 1 }}
            transition={{ duration: 0.8, delay: 0.9, ease: easings.expoOut }}
          >
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] uppercase tracking-widest text-rose-300/80 whitespace-nowrap">
              the industry gap
            </div>
          </motion.div>
        )}

        {/* dots — staggered above / below to avoid label collisions */}
        {entries.map(({ c, v }, i) => {
          const above = i % 2 === 0
          return (
            <motion.div
              key={c}
              className="absolute top-1/2 flex flex-col items-center"
              style={{ left: `${v * 100}%` }}
              initial={{ left: '50%', opacity: 0 }}
              animate={{ left: `${v * 100}%`, opacity: 1 }}
              transition={{ duration: 1.1, delay: 0.25 + i * 0.12, ease: easings.expoOut }}
            >
              {above ? (
                <div className="absolute bottom-3 -translate-x-1/2 flex flex-col items-center gap-1">
                  <div className="text-sm font-bold" style={{ color: PALETTE[c].accent }}>
                    {(spec.rawLabel?.[c]) ?? v.toFixed(2)}
                  </div>
                  <div className="text-[10px] uppercase tracking-wider"
                       style={{ color: PALETTE[c].accent }}>{c}</div>
                  <div className="w-px h-4 bg-white/25" />
                </div>
              ) : null}
              <div className="w-4 h-4 rounded-full -translate-x-1/2 ring-2 ring-black"
                   style={{ background: PALETTE[c].accent,
                            boxShadow: `0 0 14px ${PALETTE[c].accent}` }} />
              {!above ? (
                <div className="absolute top-3 -translate-x-1/2 flex flex-col items-center gap-1">
                  <div className="w-px h-4 bg-white/25" />
                  <div className="text-[10px] uppercase tracking-wider"
                       style={{ color: PALETTE[c].accent }}>{c}</div>
                  <div className="text-sm font-bold" style={{ color: PALETTE[c].accent }}>
                    {(spec.rawLabel?.[c]) ?? v.toFixed(2)}
                  </div>
                </div>
              ) : null}
            </motion.div>
          )
        })}
      </div>

      {/* verdict chip */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="flex justify-center mt-4"
      >
        <div className={`px-4 py-1.5 rounded-full text-xs uppercase tracking-widest font-mono border ${
          split
            ? 'border-rose-500/40 text-rose-300 bg-rose-500/10'
            : 'border-emerald-500/40 text-emerald-300 bg-emerald-500/10'
        }`}>
          {split ? 'Splits by industry' : 'Shared — no industry split'}
        </div>
      </motion.div>
    </div>
  )
}

// ─── Stage 0 intro: the two teams ───────────────────────────────────────────
function TeamsIntro() {
  const Team = ({ label, members, tint, delay }) => (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay, ease: easings.expoOut }}
      className="flex-1 rounded-2xl border p-8 flex flex-col items-center gap-6"
      style={{ borderColor: `${tint}40`,
               background: `linear-gradient(135deg, ${tint}14 0%, transparent 70%)` }}
    >
      <div className="text-sm uppercase tracking-[0.4em] font-mono" style={{ color: tint }}>
        {label}
      </div>
      <div className="flex items-center gap-12">
        {members.map(c => (
          <div key={c} style={{ filter: `drop-shadow(0 0 22px ${PALETTE[c].accent}66)` }}>
            <Logo company={c} size={68} />
          </div>
        ))}
      </div>
    </motion.div>
  )
  return (
    <div className="h-full flex flex-col items-center justify-center gap-8">
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <div className="font-display font-bold text-4xl mb-2">Same five themes. Two dialects.</div>
        <div className="text-slate-400">First where tech and oil diverge — then the common ground they share.</div>
      </motion.div>
      <div className="flex gap-8 w-full max-w-4xl">
        <Team label="Tech" members={TECH} tint="#76B900" delay={0.3} />
        <Team label="Oil" members={OIL} tint="#0033A0" delay={0.5} />
      </div>
    </div>
  )
}

// Differences first, then the common ground.
const STEPS = [
  { kind: 'intro' },
  { kind: 'spectrum', spec: SPECTRA.exploreExploit,       section: 'Where they differ' },
  { kind: 'spectrum', spec: SPECTRA.customerShareholder,  section: 'Where they differ' },
  { kind: 'spectrum', spec: SPECTRA.longTerm,             section: 'What they share' },
  { kind: 'spectrum', spec: SPECTRA.options,              section: 'What they share' },
]

export default function Slide03_TechVsOil({ stage = 0 }) {
  const step = STEPS[Math.min(stage, STEPS.length - 1)]
  const headline = step.kind === 'intro' ? null : step.spec.headline
  const takeaway = step.kind === 'intro' ? null : step.spec.takeaway
  const diff = step.section === 'Where they differ'

  return (
    <Slide
      splitBg="linear-gradient(95deg, rgba(118,185,0,0.10) 0%, #04070d 32%, #04070d 68%, rgba(0,51,160,0.15) 100%)"
      eyebrow="Section 04 · Tech vs Oil"
      title="The headline contrast"
    >
      <div className="h-full flex flex-col min-h-0">
        <div className="flex-1 flex flex-col items-center justify-center min-h-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={stage}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.45, ease: easings.expoOut }}
              className="w-full flex flex-col items-center"
            >
              {headline && (
                <div className="text-center mb-8 max-w-4xl">
                  <div className={`inline-block px-3 py-1 mb-4 rounded-full text-[11px] uppercase tracking-[0.3em] font-mono border ${
                    diff
                      ? 'border-rose-500/40 text-rose-300 bg-rose-500/10'
                      : 'border-emerald-500/40 text-emerald-300 bg-emerald-500/10'
                  }`}>
                    {step.section}
                  </div>
                  <h2 className="font-display font-bold text-4xl leading-tight mb-3">{headline}</h2>
                  <p className="text-slate-400 text-base leading-relaxed">{takeaway}</p>
                </div>
              )}

              {step.kind === 'intro' && <TeamsIntro />}
              {step.kind === 'spectrum' && <Spectrum spec={step.spec} />}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* progress stepper */}
        <div className="flex justify-center gap-2 pt-4">
          {STEPS.map((_, i) => (
            <div key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === stage ? 'w-10 bg-white' : i < stage ? 'w-2 bg-white/40' : 'w-2 bg-white/15'
              }`} />
          ))}
        </div>
      </div>
    </Slide>
  )
}
