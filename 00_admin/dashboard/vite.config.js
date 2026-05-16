import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// On GitHub Pages the dashboard is served from /CorporateEntre/dashboard/.
// Locally BASE_PATH is unset so it stays at '/'.
const base = process.env.BASE_PATH ?? '/'

export default defineConfig({
  base,
  plugins: [react()],
  assetsInclude: ['**/*.md'],
})
