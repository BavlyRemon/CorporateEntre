import { motion } from 'framer-motion'
import Slide from '../components/Slide'
import { NVIDIA_TIMELINE } from '../data'
import { easings } from '../theme'
import { AnimatedNumber } from '../components/Reveal'

const GREEN = '#76B900'

export default function Slide05_Nvidia() {
  // Two paralle metrics: explore share line + datacenter revenue bars
  const pad = 70
  const w = 1100
  const h = 320
  const innerW = w - pad * 2
  const innerH = 220
  const maxDC = Math.max(...NVIDIA_TIMELINE.map(d => d.dc))
  const points = NVIDIA_TIMELINE.map((d, i) => ({
    ...d,
    x: pad + (i / (NVIDIA_TIMELINE.length - 1)) * innerW,
    yShare: 40 + (1 - d.share) * innerH,
    barH: (d.dc / maxDC) * innerH,
  }))
  const flipIdx = NVIDIA_TIMELINE.findIndex(d => d.year === 2025)
  const flipX = points[flipIdx].x

  return (
    <Slide
      company="Nvidia"
      eyebrow="Section 06 · NVIDIA"
      title="The explorer became the exploiter — in one year."
      kicker="2025 is the first year NVIDIA's letter is exploit-leaning. Same author, same firm — different mode."
    >
      <div className="h-full flex flex-col min-h-0">
      <div className="relative flex-shrink-0" style={{ height: '54%' }}>
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-full" preserveAspectRatio="xMidYMid meet">
          {/* AI boom hinge */}
          <motion.line
            x1={flipX} y1={20} x2={flipX} y2={h - 30}
            stroke={GREEN} strokeOpacity="0.4" strokeDasharray="6 6"
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: 1.4 }}
          />
          <motion.text
            x={flipX} y={14} textAnchor="middle"
            fontSize={11} fontFamily="monospace" letterSpacing="3"
            fill={GREEN}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 1.8 }}
          >
            EXPLOIT FLIP
          </motion.text>

          {/* Datacenter revenue bars */}
          {points.map((p, i) => (
            <motion.rect
              key={`b-${p.year}`}
              x={p.x - 18} width={36}
              y={h - 30 - p.barH} height={0}
              fill={GREEN} fillOpacity="0.18"
              animate={{ height: p.barH }}
              transition={{ duration: 0.9, ease: easings.expoOut, delay: 0.4 + i * 0.1 }}
            />
          ))}

          {/* Explore share line */}
          <motion.polyline
            fill="none" stroke={GREEN} strokeWidth="2.5"
            points={points.map(p => `${p.x},${p.yShare}`).join(' ')}
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
            transition={{ duration: 1.6, ease: easings.expoOut, delay: 0.6 }}
          />
          {points.map((p, i) => (
            <motion.g
              key={`d-${p.year}`}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + i * 0.1, duration: 0.5, ease: easings.expoOut }}
            >
              <circle cx={p.x} cy={p.yShare} r={9}
                      fill={p.year === 2025 ? '#000' : GREEN}
                      stroke={GREEN} strokeWidth={p.year === 2025 ? 3 : 0} />
              <text x={p.x} y={p.yShare - 16} textAnchor="middle"
                    fontSize={11} fontWeight={700} fill="#fff">
                {p.share.toFixed(2)}
              </text>
              <text x={p.x} y={h - 8} textAnchor="middle"
                    fontSize={11} fontFamily="monospace" fill="#94a3b8">
                {p.year}
              </text>
              <text x={p.x} y={h - 32 - p.barH - 6} textAnchor="middle"
                    fontSize={10} fontWeight={600} fill={GREEN} fillOpacity="0.85">
                ${p.dc < 10 ? p.dc.toFixed(1) : Math.round(p.dc)}B
              </text>
            </motion.g>
          ))}
        </svg>

        <div className="absolute top-1 left-2 text-[10px] uppercase tracking-widest font-mono text-green-400/70">
          ─── Explore share &nbsp;&nbsp; ▮ Datacenter revenue ($B)
        </div>
      </div>

      <div className="mt-2 grid grid-cols-4 gap-3 flex-1 min-h-0">
        {[
          { h: 'Horizon Scanning is the signature.', b: 'Scans at 27 / 1k — ~4× the others — continually re-names inflections (CUDA, deep learning, generative AI, AI factories).' },
          { h: '2021 was the exploratory peak.', b: 'Explore=38, exploit=6. Every emerging compute paradigm named — before ChatGPT, while the prize was still abstract.' },
          { h: '2025 is the flip year.', b: 'Vocabulary tilts to execute / deploy / scale. AI is no longer a frontier bet — it\'s infrastructure being built out.' },
          { h: 'Revenue catches up to language.', b: '$0.83B (2017) → $115B (2025). Strategic Options matured into Agile Execution. Textbook explore → exploit arc.' },
        ].map((c, i) => (
          <motion.div
            key={c.h}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.9 + i * 0.12, ease: easings.expoOut }}
            className="rounded-lg border border-green-500/25 bg-green-500/[0.04] p-3"
          >
            <div className="text-[9px] uppercase tracking-widest text-green-400 font-mono mb-1">
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
