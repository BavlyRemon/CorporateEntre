import { motion } from 'framer-motion'
import { easings } from '../theme'

// A pulled quote from one of the letters. Reveals on `visible`.
export default function Quote({ text, cite, color = '#FBBF24', visible = true, delay = 0, className = '' }) {
  return (
    <motion.figure
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: visible ? 1 : 0, y: visible ? 0 : 12 }}
      transition={{ duration: 0.6, delay: visible ? delay : 0, ease: easings.expoOut }}
      className={`relative pl-4 pr-3 py-2 rounded-r ${className}`}
      style={{
        borderLeft: `3px solid ${color}`,
        background: `linear-gradient(90deg, ${color}10 0%, transparent 100%)`,
      }}
    >
      <blockquote
        className="font-display text-sm leading-snug italic text-white/90"
      >
        <span style={{ color, fontStyle: 'normal' }}>“</span>
        {text}
        <span style={{ color, fontStyle: 'normal' }}>”</span>
      </blockquote>
      {cite && (
        <figcaption className="mt-1 text-[10px] uppercase tracking-widest font-mono" style={{ color }}>
          — {cite}
        </figcaption>
      )}
    </motion.figure>
  )
}
