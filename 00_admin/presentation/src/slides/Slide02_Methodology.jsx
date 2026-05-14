import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import Reveal from '../components/Reveal'
import { easings } from '../theme'

const cards = [
  {
    n: '01',
    title: 'Stemming',
    body: 'A single entry — say "innovate" — counts whether the letter writes innovate, innovating, innovation, or innovative.',
    why: 'Without it, NVIDIA 2017 reads as 0% exploration purely because "we innovate" replaced "we invent" in the prose.',
    accent: '#76B900',
  },
  {
    n: '02',
    title: 'Synonyms + excludes',
    body: 'Each entry carries hand-picked synonyms (founder / founders / founded; acquire / acquisition) and refuses false neighbours (decisive ≠ decision; experiment ≠ experience; productive ≠ production).',
    why: 'Naïve stemming creates 60+ false hits per letter. Curated excludes keep the dictionary honest.',
    accent: '#FF9900',
  },
  {
    n: '03',
    title: 'Per 1,000 words',
    body: 'Letters range from 777 (Shell 2015) to 5,251 words (Amazon 2022). Raw counts would just measure verbosity.',
    why: 'Normalisation turns the metric into emphasis — what share of available narrative each construct receives.',
    accent: '#3B82F6',
  },
]

export default function Slide02_Methodology() {
  return (
    <Slide
      eyebrow="Section 03 · Methodology"
      title="How we read 28 letters"
      kicker="Five Innovation Process Model themes and six paired lenses, applied through one curated keyword dictionary."
    >
      <div className="mt-6 grid grid-cols-3 gap-6 h-full">
        {cards.map((c, i) => (
          <motion.div
            key={c.n}
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: easings.expoOut, delay: 0.3 + i * 0.15 }}
            className="relative rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-7 overflow-hidden flex flex-col"
          >
            <div
              className="absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl opacity-30"
              style={{ background: c.accent }}
            />
            <div
              className="text-7xl font-display font-bold opacity-15 absolute right-6 top-2"
              style={{ color: c.accent }}
            >
              {c.n}
            </div>
            <div className="relative">
              <div className="text-xs uppercase tracking-widest font-mono mb-2"
                   style={{ color: c.accent }}>
                Choice {parseInt(c.n)}
              </div>
              <h3 className="font-display font-bold text-3xl mb-4">{c.title}</h3>
              <p className="text-slate-300 leading-relaxed text-base">{c.body}</p>
            </div>
            <div className="mt-auto pt-5 relative">
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mb-1.5">Why</div>
              <p className="text-sm text-slate-400 italic">{c.why}</p>
            </div>
          </motion.div>
        ))}
      </div>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.0, duration: 0.7 }}
        className="mt-7 text-center text-slate-500 text-sm font-mono"
      >
        The dictionary <span className="text-white/70">is</span> the methodology · everything else is just counting.
      </motion.div>
    </Slide>
  )
}
