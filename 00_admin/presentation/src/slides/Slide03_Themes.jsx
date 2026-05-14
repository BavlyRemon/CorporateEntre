import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { easings } from '../theme'
import { Crown, Telescope, Compass, Lightbulb, Zap, Scale } from 'lucide-react'

// Five IPM themes + one cross-cutting paired lens, each with a short definition
// and the words that dominated the corpus inside that theme.
const THEMES = [
  {
    name: 'Strategic Leadership',
    icon: Crown,
    color: '#A855F7',
    define: 'How the CEO frames their role — founder vs. operator, decisive vs. disciplined.',
    words: ['process', 'safety', 'efficient', 'disciplined', 'responsible', 'productive', 'trust'],
  },
  {
    name: 'Horizon Scanning / Sense-making',
    icon: Telescope,
    color: '#76B900',
    define: 'How the firm names the future — discontinuities, technologies, threats it watches for.',
    words: ['AI', 'learn', 'future', 'demand', 'digital', 'cloud', 'opportunity', 'long-term'],
  },
  {
    name: 'Purpose, Vision & Governance',
    icon: Compass,
    color: '#FF9900',
    define: 'Who the firm says it exists for — customers, shareholders, communities — and what it stands for.',
    words: ['customer', 'experience', 'leader', 'scale', 'shareholder', 'return', 'dividend'],
  },
  {
    name: 'Strategic Options & Experimentation',
    icon: Lightbulb,
    color: '#FBCE07',
    define: 'How the firm spends choices — R&D, partnerships, acquisitions, capital allocation, bets.',
    words: ['invest', 'develop', 'technology', 'invent', 'capital', 'partner', 'iterate'],
  },
  {
    name: 'Agile Execution & Organization',
    icon: Zap,
    color: '#3B82F6',
    define: 'How the firm gets things done — people, capability, speed, infrastructure, operations.',
    words: ['people', 'fast', 'capability', 'infrastructure', 'process', 'speed', 'organization'],
  },
  {
    name: 'Cross-cutting: Explore vs. Exploit',
    icon: Scale,
    color: '#EC4899',
    define: 'Paired lens running over the top — new options (explore) vs. squeezing the known (exploit).',
    words: [
      { side: 'explore', text: 'learn · invent · innovate · research · reinvent · iterate' },
      { side: 'exploit', text: 'cost · scale · return · safety · dividend · efficient' },
    ],
    paired: true,
  },
]

export default function Slide03_Themes() {
  return (
    <Slide
      eyebrow="Section 02 · Framework"
      title="Five themes the letters live inside."
      kicker="The Innovation Process Model gives us five lenses; one paired lens runs over the top. Inside each theme: the words that dominated our 28-letter corpus."
    >
      <div className="mt-3 grid grid-cols-3 gap-4 h-full">
        {THEMES.map((t, i) => {
          const Icon = t.icon
          return (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.25 + i * 0.11, ease: easings.expoOut }}
              className="relative rounded-xl border overflow-hidden p-5"
              style={{
                background: `linear-gradient(135deg, ${t.color}18 0%, transparent 70%)`,
                borderColor: `${t.color}40`,
              }}
            >
              <div
                className="absolute -top-10 -right-10 w-36 h-36 rounded-full blur-3xl opacity-25"
                style={{ background: t.color }}
              />

              <div className="relative">
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center"
                    style={{ background: `${t.color}22`, border: `1px solid ${t.color}55` }}
                  >
                    <Icon size={18} style={{ color: t.color }} />
                  </div>
                  <h3 className="font-display font-bold text-base leading-tight">{t.name}</h3>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed mb-4 min-h-[3rem]">
                  {t.define}
                </p>

                {/* Dominant words */}
                {t.paired ? (
                  <div className="space-y-2">
                    {t.words.map((w, k) => (
                      <motion.div
                        key={w.side}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + i * 0.11 + k * 0.15, duration: 0.5 }}
                      >
                        <div className="text-[9px] uppercase tracking-widest font-mono mb-1"
                             style={{ color: t.color }}>
                          {w.side}
                        </div>
                        <div className="text-xs font-mono text-white/85 leading-relaxed">
                          {w.text}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {t.words.map((w, k) => (
                      <motion.span
                        key={w}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.55 + i * 0.11 + k * 0.05, duration: 0.45 }}
                        className="text-[11px] font-mono px-2 py-0.5 rounded"
                        style={{
                          background: `${t.color}15`,
                          border: `1px solid ${t.color}33`,
                          color: '#fff',
                        }}
                      >
                        {w}
                      </motion.span>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 0.6 }}
        className="mt-4 text-xs text-slate-500 font-mono text-center"
      >
        Counts shown elsewhere are normalised per 1,000 words and aggregated across all 28 letters.
      </motion.div>
    </Slide>
  )
}
