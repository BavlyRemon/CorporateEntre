import { motion } from 'framer-motion'
import { PALETTE, easings } from '../theme'
import Logo from '../components/Logo'

const COMPANIES = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

export default function SlideThankYou() {
  return (
    <div
      className="grain absolute inset-0 overflow-hidden text-white flex flex-col items-center justify-center"
      style={{ background: 'radial-gradient(circle at 50% 45%, #14203c 0%, #050912 60%, #000 100%)' }}
    >
      {COMPANIES.map((c, i) => {
        const pos = [
          { top: '-12%', left: '-12%' }, { top: '-12%', right: '-12%' },
          { bottom: '-12%', left: '-12%' }, { bottom: '-12%', right: '-12%' },
        ][i]
        return (
          <motion.div
            key={c}
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 0.28, scale: 1 }}
            transition={{ duration: 1.6, delay: 0.2 + i * 0.15, ease: easings.expoOut }}
            className="absolute w-[460px] h-[460px] rounded-full blur-3xl"
            style={{ ...pos, background: PALETTE[c].accent }}
          />
        )
      })}

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: easings.expoOut }}
        className="relative z-10 text-center"
      >
        <div className="text-xs uppercase tracking-[0.5em] font-mono text-white/50 mb-6">
          Corporate Entrepreneurship · Amazon · NVIDIA · Shell · Chevron
        </div>
        <h1 className="font-display font-bold text-7xl tracking-tight bg-gradient-to-r from-amber-400 via-green-400 to-blue-400 bg-clip-text text-transparent">
          Thank you
        </h1>
        <p className="mt-6 text-lg text-white/60">Questions &amp; discussion</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.7, ease: easings.expoOut }}
        className="relative z-10 mt-14 flex items-center gap-12"
      >
        {COMPANIES.map(c => (
          <div key={c} style={{ filter: `drop-shadow(0 0 22px ${PALETTE[c].accent}66)` }}>
            <Logo company={c} size={52} />
          </div>
        ))}
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4, duration: 0.6 }}
        className="absolute bottom-24 text-[11px] font-mono text-white/35"
      >
        Appendix follows (methodology · full keyword dictionary) — not part of the talk
      </motion.div>
    </div>
  )
}
