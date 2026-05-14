import { motion } from 'framer-motion'
import { PALETTE, easings } from '../theme'
import Logo from '../components/Logo'

const COMPANIES = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

export default function Slide08_Conclusions() {
  return (
    <div
      className="grain absolute inset-0 overflow-hidden text-white"
      style={{ background: 'radial-gradient(circle at 50% 70%, #0c1830 0%, #050912 60%, #000 100%)' }}
    >
      {/* horizon bar of colour at top */}
      <div className="absolute top-0 left-0 right-0 h-1 flex">
        {COMPANIES.map((c, i) => (
          <motion.div
            key={c}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.9, delay: 0.2 + i * 0.1, ease: easings.expoOut }}
            style={{ background: PALETTE[c].accent, transformOrigin: 'left', flex: 1 }}
          />
        ))}
      </div>

      <div className="relative z-10 h-full px-20 pt-14 pb-12 flex flex-col">
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: easings.expoOut }}
          className="text-xs uppercase tracking-[0.4em] font-mono text-white/60 mb-4"
        >
          Section 09 · Conclusions
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: easings.expoOut, delay: 0.1 }}
          className="font-display font-bold text-5xl leading-tight max-w-5xl mb-10"
        >
          Three lines we want the room to leave with.
        </motion.h1>

        <div className="grid grid-cols-3 gap-6 flex-1">
          {[
            {
              num: '01',
              h: 'Industry dictates the vocabulary of strategy.',
              b: 'Same five IPM themes, very different content. Firm size, founder, and age move the dial less than the industry the firm is embedded in.',
              accent: '#94A3B8',
            },
            {
              num: '02',
              h: 'Language leads the financial signal.',
              b: 'Amazon 2022 caught Jassy\'s exploit pivot before the 10-K. NVIDIA 2025 caught the AI-as-infrastructure flip in the same year datacenter revenue hit $115B.',
              accent: '#FF9900',
            },
            {
              num: '03',
              h: 'Ambidexterity is a verb, not a state.',
              b: 'Every "mixed" letter in our corpus was a year the firm was changing direction. Read ambidexterity as motion, not equilibrium.',
              accent: '#76B900',
            },
          ].map((c, i) => (
            <motion.div
              key={c.num}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.4 + i * 0.15, ease: easings.expoOut }}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 flex flex-col"
            >
              <div className="font-display font-bold text-7xl mb-4 leading-none"
                   style={{ color: c.accent, opacity: 0.85 }}>
                {c.num}
              </div>
              <div className="font-display font-bold text-2xl leading-tight mb-4">{c.h}</div>
              <div className="text-slate-400 text-base leading-relaxed">{c.b}</div>
            </motion.div>
          ))}
        </div>

        {/* limitations + invitation to Q&A */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 0.8 }}
          className="mt-8 flex justify-between items-end gap-12"
        >
          <div className="text-sm text-slate-500 max-w-2xl leading-relaxed">
            <span className="uppercase tracking-widest text-xs text-slate-400 mr-2">Caveats</span>
            CEO letters are crafted communications, not lived practice. The dictionary is auditable but opinionated.
            N = 4 × 7 — patterns, not causal effects.
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-5">
              {COMPANIES.map((c, i) => (
                <motion.div
                  key={c}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 0.85, y: 0 }}
                  transition={{ duration: 0.6, delay: 1.6 + i * 0.08, ease: easings.expoOut }}
                  style={{ filter: `drop-shadow(0 0 14px ${PALETTE[c].accent}66)` }}
                >
                  <Logo company={c} size={36} />
                </motion.div>
              ))}
            </div>
            <div className="text-right pl-6 border-l border-white/15">
              <div className="text-xs uppercase tracking-[0.4em] font-mono text-white/40 mb-2">Next</div>
              <div className="font-display font-bold text-3xl text-white">
                Questions.
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
