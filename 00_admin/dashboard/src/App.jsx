import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { DataContext } from './hooks/useData'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import Letters from './pages/Letters'
import Financials from './pages/Financials'
import Lexical from './pages/Lexical'
import Eras from './pages/Eras'
import Compare from './pages/Compare'
import Hypotheses from './pages/Hypotheses'
import Briefs from './pages/Briefs'
import Lexicon from './pages/Lexicon'

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/dataset.json`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  if (error) return (
    <div className="flex items-center justify-center min-h-screen text-red-400">
      <div className="text-center">
        <div className="text-2xl font-bold mb-2">Failed to load data</div>
        <div className="text-sm text-slate-500">{error}</div>
        <div className="mt-4 text-xs text-slate-600">
          Run: <code className="bg-slate-800 px-2 py-1 rounded">python build_dashboard_data.py</code> then restart Vite
        </div>
      </div>
    </div>
  )

  if (!data) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <div className="text-slate-400 text-sm">Loading corpus data…</div>
      </div>
    </div>
  )

  return (
    <DataContext.Provider value={data}>
      <div className="flex h-screen overflow-hidden bg-slate-950">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/letters" element={<Letters />} />
            <Route path="/financials" element={<Financials />} />
            <Route path="/lexical" element={<Lexical />} />
            <Route path="/lexicon" element={<Lexicon />} />
            <Route path="/eras" element={<Eras />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/hypotheses" element={<Hypotheses />} />
            <Route path="/briefs" element={<Briefs />} />
            <Route path="/briefs/:filename" element={<Briefs />} />
          </Routes>
        </main>
      </div>
    </DataContext.Provider>
  )
}
