/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        amazon: '#FF9900',
        nvidia: '#76B900',
        shell: '#FBCE07',
        chevron: '#0033A0',
        slate: {
          850: '#1a2234',
          950: '#0d1220',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
