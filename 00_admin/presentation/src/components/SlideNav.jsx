import { ChevronLeft, ChevronRight, Maximize2 } from 'lucide-react'

export default function SlideNav({ index, total, stage = 0, totalStages = 1, onPrev, onNext, onJump, onFullscreen, label }) {
  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 backdrop-blur-md bg-black/40 border border-white/10 rounded-full px-3 py-2 shadow-lg">
      <button
        onClick={onPrev}
        disabled={index === 0}
        className="p-2 rounded-full hover:bg-white/10 disabled:opacity-30 transition"
        aria-label="Previous slide"
      >
        <ChevronLeft size={18} />
      </button>
      <div className="flex items-center gap-1">
        {Array.from({ length: total }).map((_, i) => (
          <button
            key={i}
            onClick={() => onJump(i)}
            className={`h-1.5 rounded-full transition-all ${
              i === index ? 'w-8 bg-white' : 'w-1.5 bg-white/30 hover:bg-white/50'
            }`}
            aria-label={`Slide ${i + 1}`}
          />
        ))}
      </div>
      <button
        onClick={onNext}
        disabled={index === total - 1}
        className="p-2 rounded-full hover:bg-white/10 disabled:opacity-30 transition"
        aria-label="Next slide"
      >
        <ChevronRight size={18} />
      </button>
      <div className="hidden md:flex items-center gap-2 pl-3 ml-1 border-l border-white/15">
        <div className="text-[10px] uppercase tracking-widest text-white/50 font-mono">
          {String(index + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}
        </div>
        {totalStages > 1 && (
          <div className="flex items-center gap-0.5">
            {Array.from({ length: totalStages }).map((_, s) => (
              <div
                key={s}
                className={`h-2.5 w-2.5 rounded-full transition-all ${
                  s === stage ? 'bg-blue-400' : s < stage ? 'bg-white/40' : 'bg-white/15'
                }`}
              />
            ))}
          </div>
        )}
        <div className="text-xs text-white/80 max-w-[180px] truncate">{label}</div>
        <button
          onClick={onFullscreen}
          className="p-1.5 rounded-full hover:bg-white/10 transition"
          aria-label="Toggle fullscreen"
        >
          <Maximize2 size={14} />
        </button>
      </div>
    </div>
  )
}
