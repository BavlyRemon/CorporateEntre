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

// Chip size auto-shrinks with total *text volume* (not just entry count) —
// entries with 6–7 long aliases wrap to 2 lines and are the real overflow
// driver, so we tier off the summed character count.
// Full-width (single-column IPM) size scale.
function chipClass(c) {
  if (c <= 350) return 'text-xl px-4 py-2 gap-3'
  if (c <= 600) return 'text-lg px-3.5 py-1.5 gap-2.5'
  if (c <= 850) return 'text-base px-3 py-1.5 gap-2'
  if (c <= 1150) return 'text-sm px-2.5 py-1 gap-2'
  if (c <= 1500) return 'text-xs px-2 py-1 gap-1.5'
  if (c <= 1900) return 'text-[11px] px-2 py-0.5 gap-1'
  return 'text-[10px] px-1.5 py-0.5 gap-1'
}

// Narrow (two-column cross-cutting pair) size scale — columns are ~half
// width, so the same text volume needs roughly double the shrink.
function chipClassNarrow(c) {
  if (c <= 130) return 'text-base px-3 py-1 gap-2'
  if (c <= 250) return 'text-sm px-2.5 py-1 gap-1.5'
  if (c <= 400) return 'text-xs px-2 py-1 gap-1.5'
  if (c <= 700) return 'text-[11px] px-2 py-0.5 gap-1'
  return 'text-[10px] px-1.5 py-0.5 gap-1'
}

function Chips({ entries, accent, narrow = false }) {
  const chars = entries.reduce((s, e) => s + e.length, 0)
  const cls = (narrow ? chipClassNarrow : chipClass)(chars)
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
      className="absolute inset-0 rounded-2xl border p-6 overflow-hidden flex flex-col"
      style={{ borderColor: panel.accent,
               background: 'linear-gradient(135deg, #0c1018 0%, #05070c 100%)' }}
      transition={{ duration: 0.6, ease: easings.expoOut }}
    >
      <div className="flex items-baseline justify-between mb-3 flex-shrink-0">
        <div>
          <div className="text-[11px] uppercase tracking-[0.3em] font-mono"
               style={{ color: panel.accent }}>
            {panel.kind === 'ipm' ? 'IPM theme · all keywords' : 'Cross-cutting lens · all keywords'}
          </div>
          <h2 className="font-display font-bold text-3xl mt-1">{panel.name}</h2>
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
          <div className="grid grid-cols-2 gap-8 h-full w-full">
            {[panel.left, panel.right].map((side) => (
              <div key={side.label} className="min-h-0 overflow-hidden flex flex-col">
                <div className="text-xs uppercase tracking-[0.2em] font-mono mb-2 font-semibold"
                     style={{ color: panel.accent }}>
                  {side.label} · {side.entries.length}
                </div>
                <Chips entries={side.entries} accent={panel.accent} narrow />
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-2 text-[10px] font-mono text-slate-500 flex-shrink-0">
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
