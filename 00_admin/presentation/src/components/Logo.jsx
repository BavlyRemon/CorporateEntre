// Wrapper that renders a real brand logo from /public/logos/.
// Each company maps to its own asset; intrinsic aspect ratios differ, so
// callers pass a `size` (height in px) and the width is set to auto.

// Resolve under whatever base path the bundle was built with
// ('/' locally, '/CorporateEntre/' on GitHub Pages).
const B = import.meta.env.BASE_URL

const ASSETS = {
  Amazon:  { src: `${B}logos/amazon.svg`,  ratio: 1.00 },
  Nvidia:  { src: `${B}logos/nvidia.svg`,  ratio: 1.85 },
  Shell:   { src: `${B}logos/shell.svg`,   ratio: 1.08 },
  Chevron: { src: `${B}logos/chevron.png`, ratio: 0.88 },
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
