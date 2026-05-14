import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { PALETTE, easings } from '../theme'

const PATTERNS = [
  {
    n: '01',
    h: 'Long-term is universal.',
    b: 'Every firm sits at 0.87–0.94 on long-term orientation. Long-termism is wallpaper; it doesn\'t separate strategies.',
    color: '#94A3B8',
  },
  {
    n: '02',
    h: 'Ambidexterity is transitional.',
    b: 'Only 4 of 28 letters sit in the mixed 0.40–0.60 band — each is a redirection moment (Amazon 1997, 2020, 2022; Chevron 2021).',
    color: PALETTE.Amazon.accent,
  },
  {
    n: '03',
    h: 'Horizon Scanning tracks growth.',
    b: 'NVIDIA scans hardest (27 /1k) and grows fastest. Shell scans least and grows slowest. Language preceded financials in our cleanest cases.',
    color: PALETTE.Nvidia.accent,
  },
  {
    n: '04',
    h: 'Customer-share is the cleanest separator.',
    b: 'Tech 0.83–0.93 vs energy 0.30–0.38. Survives the "isn\'t this just B2C vs B2B?" check — NVIDIA is B2B and still 0.83.',
    color: '#3B82F6',
  },
  {
    n: '05',
    h: 'Product carries the leadership message.',
    b: 'Strategic Leadership thinner in tech (Amazon 3.4, NVIDIA 1.4 /1k) vs energy (Shell 6.1). Where things are slow and physical, leadership is performed.',
    color: PALETTE.Shell.accent,
  },
]

export default function Slide07_Patterns() {
  return (
    <Slide
      eyebrow="Section 08 · What survives across all four"
      title="Five patterns that hold the dictionary up."
      kicker="Findings that aren't specific to any one firm — what the cross-corpus comparison teaches."
    >
      <div className="h-full grid grid-cols-3 grid-rows-2 gap-4">
        {PATTERNS.map((p, i) => {
          // Last card spans the bottom row's remaining columns (cards 4 & 5 share the second row)
          const span = i === 4 ? 'col-span-2' : ''
          return (
            <motion.div
              key={p.n}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.25 + i * 0.1, ease: easings.expoOut }}
              className={`relative rounded-xl border overflow-hidden p-4 flex flex-col ${span}`}
              style={{
                background: `linear-gradient(135deg, ${p.color}15 0%, transparent 70%)`,
                borderColor: `${p.color}40`,
              }}
            >
              <div
                className="absolute -top-8 -right-8 w-32 h-32 rounded-full blur-3xl opacity-30"
                style={{ background: p.color }}
              />
              <div className="relative flex items-start gap-3">
                <div
                  className="font-display font-bold text-4xl leading-none flex-shrink-0"
                  style={{ color: p.color, opacity: 0.9 }}
                >
                  {p.n}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-display font-bold text-base leading-snug mb-1.5">{p.h}</div>
                  <div className="text-xs text-slate-400 leading-relaxed">{p.b}</div>
                </div>
              </div>
              <motion.div
                className="absolute left-0 bottom-0 h-[2px]"
                style={{ background: p.color, opacity: 0.7 }}
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 1.4, delay: 0.45 + i * 0.1, ease: easings.expoOut }}
              />
            </motion.div>
          )
        })}
      </div>
    </Slide>
  )
}
