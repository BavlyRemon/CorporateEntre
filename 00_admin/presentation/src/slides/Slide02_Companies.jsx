import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { PALETTE, easings } from '../theme'
import Logo from '../components/Logo'

const FIRMS = [
  {
    company: 'Amazon',
    industry: 'Tech',
    role: 'Digital platform / B2C ecosystem',
    window: '1997 – 2025',
    note: 'Founder-era (Bezos) to operator-era (Jassy) — a CEO transition inside one firm.',
  },
  {
    company: 'Nvidia',
    industry: 'Tech',
    role: 'Accelerated computing / B2B platform',
    window: '2017 – 2025',
    note: 'Pre- and post-AI-boom — the cleanest technology-discontinuity case in the corpus.',
  },
  {
    company: 'Shell',
    industry: 'Energy',
    role: 'European supermajor',
    window: '2014 – 2025',
    note: 'Stakeholder governance model; embedded energy-transition narrative.',
  },
  {
    company: 'Chevron',
    industry: 'Energy',
    role: 'American supermajor',
    window: '2013 – 2024',
    note: 'Shareholder-primacy model; operational-excellence + capital-discipline narrative.',
  },
]

export default function Slide02_Companies() {
  return (
    <Slide
      companies={['Amazon', 'Nvidia', 'Shell', 'Chevron']}
      eyebrow="Section 01 · Scope"
      title="Two industries. Two firms each. Built for contrast."
      kicker="A 2×2 design: industry differences across rows, within-industry differences across columns."
    >
      <div className="mt-2 grid grid-cols-2 grid-rows-2 gap-5 h-full">
        {FIRMS.map((f, i) => {
          const p = PALETTE[f.company]
          return (
            <motion.div
              key={f.company}
              initial={{ opacity: 0, y: 24, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.7, delay: 0.3 + i * 0.12, ease: easings.expoOut }}
              className="relative rounded-2xl border overflow-hidden p-7"
              style={{
                background: `linear-gradient(135deg, ${p.accent}22 0%, transparent 60%)`,
                borderColor: `${p.accent}40`,
              }}
            >
              <div
                className="absolute -bottom-12 -right-12 w-64 h-64 rounded-full blur-3xl opacity-25"
                style={{ background: p.accent }}
              />

              <div className="relative flex items-start justify-between gap-6">
                <div className="flex-1">
                  <div
                    className="text-[10px] uppercase tracking-[0.3em] font-mono mb-3"
                    style={{ color: p.accent }}
                  >
                    {f.industry} · {f.window}
                  </div>
                  <h3 className="font-display font-bold text-3xl mb-1" style={{ color: '#fff' }}>
                    {f.company}
                  </h3>
                  <div className="text-sm text-slate-300 mb-4">{f.role}</div>
                  <p className="text-sm text-slate-400 leading-relaxed max-w-md">{f.note}</p>
                </div>
                <div
                  className="flex-shrink-0"
                  style={{ filter: `drop-shadow(0 0 18px ${p.accent}66)` }}
                >
                  <Logo company={f.company} size={72} />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.1, duration: 0.7 }}
        className="mt-5 text-sm text-slate-400 leading-relaxed max-w-5xl"
      >
        <span className="text-white/80 font-semibold">Tech vs. Energy</span> for the industry contrast.
        Within each: a <span className="text-white/80">B2C / B2B</span> pair on the tech side and a{' '}
        <span className="text-white/80">European / American</span> pair on the energy side — so any pattern
        we find has to survive both the industry boundary and the within-industry difference.
      </motion.div>
    </Slide>
  )
}
