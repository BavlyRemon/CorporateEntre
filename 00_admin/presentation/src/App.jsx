import { useCallback, useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { easings } from './theme'

import Slide01_Hook from './slides/Slide01_Hook'
import Slide02_Companies from './slides/Slide02_Companies'
import SlideTechVsOil from './slides/Slide03_TechVsOil'
import SlideAmazon from './slides/Slide04_Amazon'
import SlideNvidia from './slides/Slide05_Nvidia'
import SlideShellVsChevron from './slides/Slide06_ShellVsChevron'
import SlideThankYou from './slides/SlideThankYou'
import SlideMethodology from './slides/Slide02_Methodology'
import SlideKeywords, { KEYWORD_STAGES } from './slides/SlideKeywords'
import SlideNav from './components/SlideNav'

// ── Main talk (7 slides) ──────────────────────────────────────────────
// Hook · Scope · Tech vs Oil · Amazon · NVIDIA · Shell vs Chevron · Thank You
// ── Appendix (after Thank You — NOT part of the timed talk) ───────────
// Methodology · Full keyword dictionary
const SLIDES = [
  { Component: Slide01_Hook,           label: 'Hook',                    stages: 1 },
  { Component: Slide02_Companies,      label: 'Scope — 4 firms, 2 industries', stages: 1 },
  { Component: SlideTechVsOil,         label: 'Tech vs Oil',             stages: 6 },
  { Component: SlideAmazon,            label: 'Amazon — eras',           stages: 3 },
  { Component: SlideNvidia,            label: 'NVIDIA — AI flip',        stages: 3 },
  { Component: SlideShellVsChevron,    label: 'Shell vs Chevron',        stages: 3 },
  { Component: SlideThankYou,          label: 'Thank you',               stages: 1 },
  // appendix
  { Component: SlideMethodology,       label: 'Appendix · Methodology',  stages: 1 },
  { Component: SlideKeywords,          label: 'Appendix · All keywords', stages: KEYWORD_STAGES },
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
