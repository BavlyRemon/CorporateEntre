import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { AMAZON_TIMELINE } from '../data'
import { easings } from '../theme'

const AMAZON = '#FF9900'

function ExploreDot({ year, share, era, ceo, label, x, y, delay }) {
  const isJassy = ceo === 'Jassy'
  return (
    <motion.g
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.6, ease: easings.expoOut }}
    >
      <circle cx={x} cy={y} r={22}
              fill={isJassy ? '#1f2937' : AMAZON}
              stroke={isJassy ? AMAZON : 'white'}
              strokeWidth={isJassy ? 3 : 2} />
      <text x={x} y={y + 4} textAnchor="middle"
            fontSize={12} fontWeight={700}
            fill={isJassy ? AMAZON : '#131A22'}>
        {share.toFixed(2)}
      </text>
      <text x={x} y={y - 32} textAnchor="middle" fontSize={12} fontWeight={600} fill="#fff">
        {year}
      </text>
      <text x={x} y={y + 42} textAnchor="middle" fontSize={10} fill="#94a3b8">
        {era}
      </text>
    </motion.g>
  )
}

export default function Slide04_Amazon() {
  // Layout points along an x axis
  const pad = 80
  const w = 1100
  const innerW = w - pad * 2
  const points = AMAZON_TIMELINE.map((d, i) => ({
    ...d,
    x: pad + (i / (AMAZON_TIMELINE.length - 1)) * innerW,
    y: 180 - (d.share - 0.5) * 220, // higher share = higher up
  }))

  return (
    <Slide
      company="Amazon"
      eyebrow="Section 05 · Amazon"
      title="Founder → operator → AI builder"
      kicker="Bezos's exploration peaked twice. Jassy split it in two: a 2022 discipline pivot, then a 2024–25 AI re-exploration."
    >
      <div className="h-full flex flex-col min-h-0">
      <div className="relative flex-shrink-0" style={{ height: '54%' }}>
        <svg viewBox="0 0 1100 320" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
          <line x1={pad} y1={260} x2={w - pad} y2={260} stroke="#475569" strokeDasharray="4 4" />
          <motion.polyline
            fill="none" stroke={AMAZON} strokeWidth="2" strokeOpacity="0.45"
            points={points.map(p => `${p.x},${p.y}`).join(' ')}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.6, ease: easings.expoOut, delay: 0.3 }}
          />
          <motion.g
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 1.6, duration: 0.5 }}
          >
            <line x1={(points[3].x + points[4].x) / 2}
                  y1={30} x2={(points[3].x + points[4].x) / 2} y2={290}
                  stroke="#FF9900" strokeOpacity="0.4" strokeDasharray="6 6" />
            <text x={(points[2].x + points[3].x) / 2} y={22}
                  textAnchor="middle" fontSize={11}
                  fontFamily="monospace" letterSpacing="3" fill="#FF9900">
              BEZOS
            </text>
            <text x={(points[4].x + points[5].x) / 2} y={22}
                  textAnchor="middle" fontSize={11}
                  fontFamily="monospace" letterSpacing="3" fill="#FF9900">
              JASSY
            </text>
          </motion.g>
          {points.map((p, i) => (
            <ExploreDot key={p.year} {...p} delay={0.5 + i * 0.13} />
          ))}
        </svg>

      </div>

      <div className="mt-2 grid grid-cols-4 gap-3 flex-1 min-h-0">
        {[
          { h: 'Founder vs operator dialect.', b: 'Bezos peaks twice at >0.80 (2016, 2021). Jassy\'s first letter drops to 0.60.' },
          { h: 'Jassy phase 1 = exploit pivot.', b: '2022 explore drop coincides with the warehouse rationalisation and 27k layoffs. Language led the 10-K.' },
          { h: 'Jassy phase 2 = bounded re-explore.', b: '2024–25 revives Strategic Options around AI (Anthropic, Bedrock, custom silicon).' },
          { h: 'Purpose holds the line.', b: 'Customer-obsession / Day-1 language stays at ~13 / 1k across founders, pandemics, and CEO change.' },
        ].map((c, i) => (
          <motion.div
            key={c.h}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 2.0 + i * 0.12, ease: easings.expoOut }}
            className="rounded-lg border border-amber-500/20 bg-amber-500/[0.04] p-3"
          >
            <div className="text-[9px] uppercase tracking-widest text-amber-400 font-mono mb-1">
              Finding {i + 1}
            </div>
            <div className="font-display font-bold text-sm leading-snug mb-1">{c.h}</div>
            <div className="text-xs text-slate-400 leading-relaxed">{c.b}</div>
          </motion.div>
        ))}
      </div>
      </div>
    </Slide>
  )
}
