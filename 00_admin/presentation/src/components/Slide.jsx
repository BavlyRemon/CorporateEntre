import { motion } from 'framer-motion'
import { PALETTE, easings } from '../theme'
import Logo from './Logo'

// Decorative logo watermark in a slide corner.
// Sits behind the content with low opacity + soft glow.
function Watermark({ company, position = 'tr', size = 360 }) {
  if (!company || !PALETTE[company]) return null

  const positions = {
    tr: { top: 48, right: 48 },
    tl: { top: 48, left: 48 },
    br: { bottom: 48, right: 48 },
    bl: { bottom: 48, left: 48 },
  }

  // Each logo gets a unique on-enter motion: scale-in, soft rotate, fade.
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.6, rotate: -6 }}
      animate={{ opacity: 0.85, scale: 1, rotate: 0 }}
      transition={{ duration: 1.2, ease: easings.expoOut, delay: 0.15 }}
      className="absolute pointer-events-none"
      style={{ ...positions[position], filter: `drop-shadow(0 0 32px ${PALETTE[company].accent}66)` }}
    >
      <Logo company={company} size={size} />
    </motion.div>
  )
}

// Smaller logo "chip" for multi-company slides.
function LogoChip({ company, position = 'tr', size = 96 }) {
  if (!company || !PALETTE[company]) return null

  const positions = {
    tr: { top: 36, right: 36 },
    tl: { top: 36, left: 36 },
    br: { bottom: 36, right: 36 },
    bl: { bottom: 36, left: 36 },
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 0.85, y: 0 }}
      transition={{ duration: 0.7, ease: easings.expoOut, delay: 0.2 }}
      className="absolute pointer-events-none"
      style={{ ...positions[position], filter: `drop-shadow(0 0 18px ${PALETTE[company].accent}55)` }}
    >
      <Logo company={company} size={size} />
    </motion.div>
  )
}

export default function Slide({ company, companies, eyebrow, title, kicker, children, splitBg, watermarkSize = 360 }) {
  const single = company && PALETTE[company]
  const bg = splitBg
    ? splitBg
    : single
      ? PALETTE[company].bg
      : 'linear-gradient(135deg, #050912 0%, #0F1525 60%, #0A0F1C 100%)'
  const ink = single ? PALETTE[company].ink : '#FFFFFF'
  const accent = single ? PALETTE[company].accent : '#94A3B8'

  return (
    <div
      className="grain absolute inset-0 overflow-hidden flex flex-col"
      style={{ background: bg, color: ink }}
    >
      {single && <Watermark company={company} position="tr" size={watermarkSize} />}

      {companies && companies.length === 2 && (
        <>
          <LogoChip company={companies[0]} position="bl" size={110} />
          <LogoChip company={companies[1]} position="tr" size={110} />
        </>
      )}

      {companies && companies.length > 2 && (
        <>
          <LogoChip company={companies[0]} position="tl" size={90} />
          <LogoChip company={companies[1]} position="tr" size={90} />
          <LogoChip company={companies[2]} position="bl" size={90} />
          <LogoChip company={companies[3]} position="br" size={90} />
        </>
      )}

      {(eyebrow || title) && (
        <div className="px-20 pt-10 pb-2 relative z-10 flex-shrink-0">
          {eyebrow && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: easings.expoOut }}
              className="text-[11px] uppercase tracking-[0.3em] font-mono mb-2"
              style={{ color: accent }}
            >
              {eyebrow}
            </motion.div>
          )}
          {title && (
            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: easings.expoOut, delay: 0.08 }}
              className="font-display font-bold text-4xl leading-[1.05] max-w-5xl"
            >
              {title}
            </motion.h1>
          )}
          {kicker && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.85 }}
              transition={{ delay: 0.35, duration: 0.6 }}
              className="mt-2 text-base text-slate-300 max-w-4xl"
            >
              {kicker}
            </motion.div>
          )}
        </div>
      )}

      <div className="flex-1 px-20 pb-12 pt-2 relative z-10 min-h-0 overflow-hidden">
        {children}
      </div>
    </div>
  )
}
