// Company palette + design language tokens used across slides.

export const PALETTE = {
  Amazon: {
    accent: '#FF9900',
    accentSoft: '#FFB453',
    bg: 'linear-gradient(135deg, #0B0F14 0%, #131A22 60%, #232F3E 100%)',
    ink: '#FFFFFF',
    muted: '#94A3B8',
    glow: 'shadow-glow-amazon',
    badge: 'bg-amber-500/15 text-amber-300 border-amber-500/40',
    motif: 'smile', // brand motif: the Amazon smile curve
  },
  Nvidia: {
    accent: '#76B900',
    accentSoft: '#A8E635',
    bg: 'radial-gradient(circle at 20% 30%, #1A2710 0%, #0B0E0A 50%, #000000 100%)',
    ink: '#FFFFFF',
    muted: '#94A3B8',
    glow: 'shadow-glow-nvidia',
    badge: 'bg-green-500/15 text-green-300 border-green-500/40',
    motif: 'grid', // technical / computational grid
  },
  Shell: {
    accent: '#FBCE07',
    accentSoft: '#FFE56B',
    secondary: '#DD1D21',
    bg: 'linear-gradient(135deg, #1A1505 0%, #2A2208 50%, #1A1505 100%)',
    ink: '#FFF7E0',
    muted: '#C9B97A',
    glow: 'shadow-glow-shell',
    badge: 'bg-yellow-500/15 text-yellow-200 border-yellow-500/40',
    motif: 'pecten', // Shell's scallop / pecten silhouette
  },
  Chevron: {
    accent: '#0033A0',
    accentSoft: '#3366CC',
    secondary: '#ED1C24',
    bg: 'linear-gradient(135deg, #050C1F 0%, #0A1733 50%, #0F2253 100%)',
    ink: '#FFFFFF',
    muted: '#8AA0C9',
    glow: 'shadow-glow-chevron',
    badge: 'bg-blue-600/15 text-blue-300 border-blue-600/40',
    motif: 'chevrons', // Chevron's stacked V marks
  },
}

export const COMPANIES = ['Amazon', 'Nvidia', 'Shell', 'Chevron']

export const easings = {
  swift: [0.32, 0.72, 0, 1],
  expoOut: [0.16, 1, 0.3, 1],
  expoInOut: [0.87, 0, 0.13, 1],
}
