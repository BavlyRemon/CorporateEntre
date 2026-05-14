import { motion } from 'framer-motion'
import { PALETTE, easings } from '../theme'
import { HEADLINE } from '../data'
import { AnimatedNumber } from '../components/Reveal'
import Logo from '../components/Logo'

const COMPANIES = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

export default function Slide01_Hook() {
  return (
    <div
      className="grain absolute inset-0 overflow-hidden text-white"
      style={{ background: 'radial-gradient(circle at 50% 30%, #1a2440 0%, #050912 60%, #000 100%)' }}
    >
      {/* Corner glow blobs in each brand colour */}
      {COMPANIES.map((c, i) => {
        const pos = [
          { top: '-10%', left: '-10%' },
          { top: '-10%', right: '-10%' },
          { bottom: '-10%', left: '-10%' },
          { bottom: '-10%', right: '-10%' },
        ][i]
        return (
          <motion.div
            key={c}
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 0.32, scale: 1 }}
            transition={{ duration: 1.6, delay: 0.2 + i * 0.15, ease: easings.expoOut }}
            className="absolute w-[480px] h-[480px] rounded-full blur-3xl"
            style={{ ...pos, background: PALETTE[c].accent }}
          />
        )
      })}

      <div className="relative z-10 h-full flex flex-col items-center justify-center text-center px-8">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: easings.expoOut }}
          className="text-xs uppercase tracking-[0.5em] font-mono text-white/60 mb-6"
        >
          A comparative study · {HEADLINE.yearsCovered}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: easings.expoOut, delay: 0.15 }}
          className="font-display font-bold text-7xl leading-[0.95] max-w-5xl tracking-tight"
        >
          The Vocabulary of <br />
          <span className="bg-gradient-to-r from-amber-400 via-green-400 to-blue-400 bg-clip-text text-transparent">
            Corporate Entrepreneurship
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.55 }}
          className="mt-8 text-xl text-white/70 max-w-3xl leading-relaxed"
        >
          How four firms talk about innovation — and how that talk
          predicts where they actually go.
        </motion.p>

        {/* Four real logos in a row */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.85, ease: easings.expoOut }}
          className="mt-12 flex items-center gap-14"
        >
          {COMPANIES.map((c, i) => (
            <motion.div
              key={c}
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, delay: 1.0 + i * 0.12, ease: easings.expoOut }}
              className="flex items-center justify-center"
              style={{ filter: `drop-shadow(0 0 28px ${PALETTE[c].accent}88)` }}
            >
              <Logo company={c} size={64} />
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.6, ease: easings.expoOut }}
          className="mt-12 flex items-center gap-12"
        >
          {[
            { label: 'CEO Letters', value: HEADLINE.letters, fmt: v => Math.round(v) },
            { label: 'Companies',   value: HEADLINE.companies, fmt: v => Math.round(v) },
            { label: 'Words analysed', value: HEADLINE.totalWords, fmt: v => Math.round(v).toLocaleString() },
          ].map(s => (
            <div key={s.label} className="text-center">
              <div className="font-display text-5xl font-bold text-white">
                <AnimatedNumber value={s.value} format={s.fmt} duration={1.6} delay={1.7} />
              </div>
              <div className="text-xs uppercase tracking-widest text-white/50 mt-2">{s.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}
