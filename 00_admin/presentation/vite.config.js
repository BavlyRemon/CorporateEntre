import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// `BASE_PATH` is set by the GitHub Actions deploy workflow to '/CorporateEntre/'.
// Locally it defaults to '/', so `npm run dev` and `npm run preview` keep
// working without any env tweaks.
const base = process.env.BASE_PATH ?? '/'

export default defineConfig({
  base,
  plugins: [react()],
  server: { port: 5174, open: true },
})
