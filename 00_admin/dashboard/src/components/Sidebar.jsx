import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, BookOpen, DollarSign, BarChart2,
  Clock, GitCompare, FlaskConical, FileText, BookA
} from 'lucide-react'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/letters', icon: BookOpen, label: 'Letters' },
  { to: '/financials', icon: DollarSign, label: 'Financials' },
  { to: '/lexical', icon: BarChart2, label: 'Lexical' },
  { to: '/lexicon', icon: BookA, label: 'Lexicon' },
  { to: '/eras', icon: Clock, label: 'Eras' },
  { to: '/compare', icon: GitCompare, label: 'Compare' },
  { to: '/hypotheses', icon: FlaskConical, label: 'Hypotheses' },
  { to: '/briefs', icon: FileText, label: 'Briefs' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col">
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-1">CorpEntré</div>
        <div className="text-base font-bold text-white leading-tight">Corporate Entrepreneurship<br/>Analysis</div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-3 border-t border-slate-800 text-xs text-slate-600">
        4 companies · 28 letters · 1997–2025
      </div>
    </aside>
  )
}
