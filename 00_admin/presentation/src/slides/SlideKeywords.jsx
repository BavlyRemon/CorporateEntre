import { motion, AnimatePresence, LayoutGroup } from 'framer-motion'
import Slide from '../components/Slide'
import { easings } from '../theme'
import kw from '../data/keywords.json'

// Build a flat list of panels: 5 IPM themes + 6 cross-cutting pairs.
const ACCENTS = ['#A855F7', '#76B900', '#FF9900', '#FBCE07', '#3B82F6',
                 '#EC4899', '#10B981', '#38BDF8', '#F97316', '#22D3EE', '#F43F5E']

const PANELS = [
  ...kw.ipm.map((t, i) => ({
    kind: 'ipm', name: t.name, entries: t.entries, accent: ACCENTS[i % ACCENTS.length],
  })),
  ...kw.cross.map((c, i) => ({
    kind: 'pair', name: c.name, left: c.left, right: c.right,
    accent: ACCENTS[(i + 5) % ACCENTS.length],
  })),
]

function Tile({ panel, onActive }) {
  const count = panel.kind === 'ipm'
    ? panel.entries.length
    : panel.left.entries.length + panel.right.entries.length
  return (
    <motion.div
      layoutId={`kw-${panel.name}`}
      className="rounded-xl border p-4 cursor-default flex flex-col justify-between overflow-hidden"
      style={{ borderColor: `${panel.accent}45`,
               background: `linear-gradient(135deg, ${panel.accent}18 0%, transparent 70%)` }}
      transition={{ duration: 0.55, ease: easings.expoOut }}
    >
      <div className="text-[10px] uppercase tracking-[0.25em] font-mono"
           style={{ color: panel.accent }}>
        {panel.kind === 'ipm' ? 'IPM theme' : 'Cross-cutting'}
      </div>
      <div className="font-display font-bold text-lg leading-tight mt-1">{panel.name}</div>
      <div className="text-xs text-slate-500 mt-2">{count} entries</div>
    </motion.div>
  )
}

// Chip size auto-shrinks with entry count so the panel never overflows.
function chipClass(n) {
  if (n <= 14) return 'text-xl px-4 py-2 gap-3'
  if (n <= 22) return 'text-lg px-3.5 py-1.5 gap-2.5'
  if (n <= 34) return 'text-base px-3 py-1.5 gap-2'
  return 'text-sm px-2.5 py-1 gap-2'
}

function Chips({ entries, accent }) {
  const cls = chipClass(entries.length)
  const [, , , gap] = cls.split(' ')
  return (
    <div className={`flex flex-wrap content-start ${gap}`}>
      {entries.map((e, i) => (
        <motion.span
          key={e + i}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 + Math.min(i, 40) * 0.008, duration: 0.28 }}
          className={`font-mono rounded-md leading-tight font-medium ${cls.split(' ').slice(0, 3).join(' ')}`}
          style={{ background: `${accent}33`, border: `1px solid ${accent}`, color: '#ffffff' }}
        >
          {e}
        </motion.span>
      ))}
    </div>
  )
}

function FocusPanel({ panel }) {
  return (
    <motion.div
      layoutId={`kw-${panel.name}`}
      className="absolute inset-0 rounded-2xl border p-9 overflow-hidden flex flex-col"
      style={{ borderColor: panel.accent,
               background: 'linear-gradient(135deg, #0c1018 0%, #05070c 100%)' }}
      transition={{ duration: 0.6, ease: easings.expoOut }}
    >
      <div className="flex items-baseline justify-between mb-6 flex-shrink-0">
        <div>
          <div className="text-sm uppercase tracking-[0.3em] font-mono"
               style={{ color: panel.accent }}>
            {panel.kind === 'ipm' ? 'IPM theme · all keywords' : 'Cross-cutting lens · all keywords'}
          </div>
          <h2 className="font-display font-bold text-5xl mt-2">{panel.name}</h2>
        </div>
        <div className="text-sm font-mono text-slate-500">
          {panel.kind === 'ipm'
            ? `${panel.entries.length} entries`
            : `${panel.left.entries.length + panel.right.entries.length} entries`}
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        {panel.kind === 'ipm' ? (
          <Chips entries={panel.entries} accent={panel.accent} />
        ) : (
          <div className="grid grid-cols-2 gap-12 h-full w-full">
            {[panel.left, panel.right].map((side) => (
              <div key={side.label} className="min-h-0 overflow-hidden flex flex-col">
                <div className="text-base uppercase tracking-[0.25em] font-mono mb-5 font-semibold"
                     style={{ color: panel.accent }}>
                  {side.label} · {side.entries.length}
                </div>
                <Chips entries={side.entries} accent={panel.accent} />
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-5 text-xs font-mono text-slate-500 flex-shrink-0">
        format: <span className="text-slate-300">base (aliases…)</span> ·
        <span className="text-slate-300"> "phrase"</span> = literal whole-word ·
        <span className="text-slate-300"> ·literal</span> = stemming disabled
      </div>
    </motion.div>
  )
}

export default function SlideKeywords({ stage = 0 }) {
  const focusIdx = stage - 1            // stage 0 = grid; stage k → PANELS[k-1]
  const focused = focusIdx >= 0 && focusIdx < PANELS.length ? PANELS[focusIdx] : null

  return (
    <Slide
      eyebrow="Appendix · Full keyword dictionary"
      title={focused ? null : 'Every word we scored'}
      kicker={focused ? null : 'The complete dictionary — 5 IPM themes + 6 cross-cutting lenses. Advance to zoom into each.'}
    >
      <LayoutGroup>
        <div className="h-full relative min-h-0">
          {/* Grid of all panels (focused one is lifted out into FocusPanel) */}
          <div className="grid grid-cols-4 grid-rows-3 gap-3 h-full">
            {PANELS.map((p) => (
              focused && p.name === focused.name
                ? <div key={p.name} />
                : <Tile key={p.name} panel={p} />
            ))}
          </div>

          <AnimatePresence>
            {focused && (
              <FocusPanel key={focused.name} panel={focused} />
            )}
          </AnimatePresence>
        </div>
      </LayoutGroup>
    </Slide>
  )
}

export const KEYWORD_STAGES = PANELS.length + 1
