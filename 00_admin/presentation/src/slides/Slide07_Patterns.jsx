import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { PALETTE, easings } from '../theme'

const PATTERNS = [
  {
    n: '01',
    h: 'Long-term is universal.',
    b: 'Every firm sits at 0.87–0.94 on long-term orientation. Long-termism is the wallpaper of CEO letters; it doesn\'t separate strategies.',
    color: '#94A3B8',
  },
  {
    n: '02',
    h: 'Ambidexterity is transitional.',
    b: 'Only 4 of 28 letters sit in the mixed 0.40–0.60 band — and each one is a moment of redirection: Amazon 1997 founding, Amazon 2020 pandemic, Amazon 2022 Jassy pivot, Chevron 2021 New Energies launch.',
    color: PALETTE.Amazon.accent,
  },
  {
    n: '03',
    h: 'Horizon Scanning tracks growth.',
    b: 'NVIDIA scans the hardest (27 /1k) and grows the fastest. Shell scans the least and grows the slowest. Causation is unprovable here, but the language signal preceded the financial signal in our two cleanest cases.',
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
    h: 'Tech CEOs let the product carry the leadership message.',
    b: 'Strategic Leadership thinner than expected in tech (Amazon 3.4 /1k, NVIDIA 1.4 /1k) vs energy (Shell 6.1, Chevron 3.0). Where things are physical and slow, leadership has to be performed; where they\'re fast, it\'s assumed.',
    color: PALETTE.Shell.accent,
  },
]

export default function Slide07_Patterns() {
  return (
    <Slide
      eyebrow="Section 08 · What survives across all four"
      title="Five patterns that hold the dictionary up."
      kicker="Findings that aren't specific to any one firm — they're what the cross-corpus comparison teaches."
    >
      <div className="mt-6 grid grid-cols-1 gap-3">
        {PATTERNS.map((p, i) => (
          <motion.div
            key={p.n}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.3 + i * 0.12, ease: easings.expoOut }}
            className="group relative grid grid-cols-[80px_1fr] gap-6 items-start py-4 border-b border-white/10"
          >
            <div
              className="font-display font-bold text-6xl leading-none"
              style={{ color: p.color, opacity: 0.85 }}
            >
              {p.n}
            </div>
            <div>
              <div
                className="font-display font-bold text-2xl mb-1.5"
                style={{ color: '#fff' }}
              >
                {p.h}
              </div>
              <div className="text-slate-400 text-base leading-relaxed max-w-4xl">{p.b}</div>
            </div>
            <motion.div
              className="absolute left-0 bottom-0 h-px"
              style={{ background: p.color }}
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 1.6, delay: 0.5 + i * 0.12, ease: easings.expoOut }}
            />
          </motion.div>
        ))}
      </div>
    </Slide>
  )
}
