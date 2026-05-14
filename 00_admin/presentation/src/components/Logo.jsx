// Wrapper that renders a real brand logo from /public/logos/.
// Each company maps to its own asset; intrinsic aspect ratios differ, so
// callers pass a `size` (height in px) and the width is set to auto.

const ASSETS = {
  Amazon:  { src: '/logos/amazon.svg',  ratio: 1.00 },
  Nvidia:  { src: '/logos/nvidia.svg',  ratio: 1.85 },
  Shell:   { src: '/logos/shell.svg',   ratio: 1.08 },
  Chevron: { src: '/logos/chevron.png', ratio: 0.88 },
}

export default function Logo({ company, size = 80, className = '', style = {} }) {
  const asset = ASSETS[company]
  if (!asset) return null
  return (
    <img
      src={asset.src}
      alt={`${company} logo`}
      style={{ height: size, width: 'auto', ...style }}
      className={`select-none pointer-events-none ${className}`}
      draggable={false}
    />
  )
}
