/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        amazon: { DEFAULT: '#FF9900', deep: '#232F3E', ink: '#131A22' },
        nvidia: { DEFAULT: '#76B900', deep: '#0B0E0A', ink: '#000000' },
        shell:  { DEFAULT: '#FBCE07', red: '#DD1D21', cream: '#FFF7E0' },
        chevron:{ DEFAULT: '#0033A0', red: '#ED1C24', ink: '#0A1733' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 18s linear infinite',
      },
    },
  },
  plugins: [],
}
