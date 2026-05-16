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

// Each slide declares how many stages it has. The space bar / right-arrow
// advances stage within a slide; once at the last stage, advancing moves
// to the next slide. left-arrow walks back one stage at a time.
const SLIDES = [
  { Component: Slide01_Hook,            label: 'Hook',                       stages: 1 },
  { Component: Slide02_Companies,       label: 'Scope — 4 firms, 2 industries', stages: 1 },
  { Component: Slide03_Themes,          label: 'Framework — IPM themes',     stages: 1 },
  { Component: Slide04_Methodology,     label: 'Methodology',                stages: 1 },
  { Component: Slide05_TechVsOil,       label: 'Tech vs Oil',                stages: 6 },
  { Component: Slide06_Amazon,          label: 'Amazon — eras',              stages: 3 },
  { Component: Slide07_Nvidia,          label: 'NVIDIA — AI flip',           stages: 3 },
  { Component: Slide08_ShellVsChevron,  label: 'Shell vs Chevron',           stages: 3 },
  { Component: Slide09_Patterns,        label: 'Patterns',                   stages: 1 },
  { Component: Slide10_Conclusions,     label: 'Conclusions',                stages: 1 },
]

function parseHash() {
  const m = window.location.hash.match(/^#(\d+)(?:\.(\d+))?$/)
  if (!m) return { slide: 0, stage: 0 }
  return {
    slide: Math.max(0, Math.min(SLIDES.length - 1, parseInt(m[1], 10) - 1)),
    stage: Math.max(0, parseInt(m[2] || '1', 10) - 1),
  }
}

export default function App() {
  const init = parseHash()
  const [index, setIndex] = useState(init.slide)
  const [stage, setStage] = useState(Math.min(init.stage, (SLIDES[init.slide].stages || 1) - 1))
  const [dir, setDir] = useState(1)

  const totalStages = SLIDES[index].stages || 1

  // Keep the URL hash in sync so refresh and deep-link work.
  useEffect(() => {
    window.location.hash = `#${index + 1}.${stage + 1}`
  }, [index, stage])

  const goToSlide = useCallback((next) => {
    setIndex((i) => {
      const clamped = Math.max(0, Math.min(SLIDES.length - 1, next))
      setDir(clamped > i ? 1 : -1)
      setStage(0)
      return clamped
    })
  }, [])

  const advance = useCallback(() => {
    if (stage < totalStages - 1) {
      setStage(stage + 1)
    } else if (index < SLIDES.length - 1) {
      setDir(1)
      setIndex(index + 1)
      setStage(0)
    }
  }, [stage, totalStages, index])

  const retreat = useCallback(() => {
    if (stage > 0) {
      setStage(stage - 1)
    } else if (index > 0) {
      setDir(-1)
      const prevIdx = index - 1
      setIndex(prevIdx)
      // Land on the *last* stage of the previous slide so backward feels continuous.
      setStage((SLIDES[prevIdx].stages || 1) - 1)
    }
  }, [stage, index])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault(); advance()
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault(); retreat()
      } else if (e.key === 'Home') {
        e.preventDefault(); goToSlide(0)
      } else if (e.key === 'End') {
        e.preventDefault(); goToSlide(SLIDES.length - 1)
      } else if (/^[1-9]$/.test(e.key)) {
        const n = parseInt(e.key, 10) - 1
        if (n < SLIDES.length) goToSlide(n)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [advance, retreat, goToSlide])

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
          <Component stage={stage} />
        </motion.div>
      </AnimatePresence>

      <SlideNav
        index={index}
        total={SLIDES.length}
        stage={stage}
        totalStages={totalStages}
        onPrev={retreat}
        onNext={advance}
        onJump={goToSlide}
        onFullscreen={toggleFullscreen}
        label={label}
      />
    </div>
  )
}
