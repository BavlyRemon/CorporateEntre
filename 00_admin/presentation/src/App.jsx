import { useCallback, useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { easings } from './theme'

import Slide01_Hook from './slides/Slide01_Hook'
import Slide02_Companies from './slides/Slide02_Companies'
import Slide03_Themes from './slides/Slide03_Themes'
import Slide04_Methodology from './slides/Slide02_Methodology'
import Slide05_TechVsOil from './slides/Slide03_TechVsOil'
import Slide06_Amazon from './slides/Slide04_Amazon'
import Slide07_Nvidia from './slides/Slide05_Nvidia'
import Slide08_ShellVsChevron from './slides/Slide06_ShellVsChevron'
import Slide09_Patterns from './slides/Slide07_Patterns'
import Slide10_Conclusions from './slides/Slide08_Conclusions'
import SlideNav from './components/SlideNav'

const SLIDES = [
  { Component: Slide01_Hook,            label: 'Hook' },
  { Component: Slide02_Companies,       label: 'Scope — 4 firms, 2 industries' },
  { Component: Slide03_Themes,          label: 'Framework — IPM themes' },
  { Component: Slide04_Methodology,     label: 'Methodology' },
  { Component: Slide05_TechVsOil,       label: 'Tech vs Oil' },
  { Component: Slide06_Amazon,          label: 'Amazon — eras' },
  { Component: Slide07_Nvidia,          label: 'NVIDIA — AI flip' },
  { Component: Slide08_ShellVsChevron,  label: 'Shell vs Chevron' },
  { Component: Slide09_Patterns,        label: 'Patterns' },
  { Component: Slide10_Conclusions,     label: 'Conclusions' },
]

export default function App() {
  const [index, setIndex] = useState(() => {
    const fromHash = parseInt(window.location.hash.replace('#', '')) - 1
    return Number.isFinite(fromHash) && fromHash >= 0 && fromHash < SLIDES.length ? fromHash : 0
  })
  const [dir, setDir] = useState(1)

  const goTo = useCallback((next) => {
    setIndex((i) => {
      const clamped = Math.max(0, Math.min(SLIDES.length - 1, next))
      setDir(clamped > i ? 1 : -1)
      window.location.hash = `#${clamped + 1}`
      return clamped
    })
  }, [])

  const prev = useCallback(() => goTo(index - 1), [goTo, index])
  const next = useCallback(() => goTo(index + 1), [goTo, index])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault(); next()
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault(); prev()
      } else if (e.key === 'Home') {
        e.preventDefault(); goTo(0)
      } else if (e.key === 'End') {
        e.preventDefault(); goTo(SLIDES.length - 1)
      } else if (/^[1-9]$/.test(e.key)) {
        const n = parseInt(e.key, 10) - 1
        if (n < SLIDES.length) goTo(n)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [next, prev, goTo])

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.()
    else document.exitFullscreen?.()
  }

  const { Component, label } = SLIDES[index]

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      <AnimatePresence custom={dir} mode="wait">
        <motion.div
          key={index}
          custom={dir}
          initial={{ opacity: 0, x: dir > 0 ? 60 : -60, scale: 0.99 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: dir > 0 ? -60 : 60, scale: 0.99 }}
          transition={{ duration: 0.55, ease: easings.expoOut }}
          className="absolute inset-0"
        >
          <Component />
        </motion.div>
      </AnimatePresence>

      <SlideNav
        index={index}
        total={SLIDES.length}
        onPrev={prev}
        onNext={next}
        onJump={goTo}
        onFullscreen={toggleFullscreen}
        label={label}
      />
    </div>
  )
}
