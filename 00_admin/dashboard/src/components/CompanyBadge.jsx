import { COMPANY_BG, COMPANY_TEXT } from '../utils/constants'

export default function CompanyBadge({ company, size = 'sm' }) {
  const cls = COMPANY_BG[company] || 'bg-slate-700 border-slate-600 text-slate-300'
  const text = COMPANY_TEXT[company] || 'text-slate-300'
  const pad = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'
  return (
    <span className={`badge border ${cls} ${pad} ${text}`}>{company}</span>
  )
}
