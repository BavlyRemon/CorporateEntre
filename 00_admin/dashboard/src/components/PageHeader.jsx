export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="px-8 pt-8 pb-5 border-b border-slate-800 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {subtitle && <p className="text-slate-400 text-sm mt-1">{subtitle}</p>}
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  )
}
