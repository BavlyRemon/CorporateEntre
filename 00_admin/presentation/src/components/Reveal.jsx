import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { easings } from '../theme'

// Sequenced reveal — children fade-up one after another.
export default function Reveal({ children, delay = 0, stagger = 0.12, className = '' }) {
  const items = Array.isArray(children) ? children : [children]
  return (
    <>
      {items.map((child, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: easings.expoOut, delay: delay + i * stagger }}
          className={className}
        >
          {child}
        </motion.div>
      ))}
    </>
  )
}

// Animated counter — easeOutExpo from 0 to `value`.
export function AnimatedNumber({ value, format = (v) => v.toFixed(2), duration = 1.2, delay = 0, className = '' }) {
  const [n, setN] = useState(0)
  useEffect(() => {
    let raf
    let start
    const tick = (t) => {
      if (start === undefined) start = t
      const elapsed = (t - start) / 1000 - delay
      if (elapsed < 0) {
        raf = requestAnimationFrame(tick)
        return
      }
      const p = Math.min(elapsed / duration, 1)
      const e = p === 1 ? 1 : 1 - Math.pow(2, -10 * p)
      setN(value * e)
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [value, duration, delay])
  return <span className={className}>{format(n)}</span>
}
