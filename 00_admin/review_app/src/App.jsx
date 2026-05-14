import React, { useState, useEffect, useRef, useCallback } from 'react'

const STATUS_LABELS = { ok: 'OK', issue: 'Issue', skip: 'Skip' }

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function buildHighlightedHtml(text, query) {
  if (!query || query.length < 2) return { html: escapeHtml(text), count: 0 }
  const escapedQ = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const re = new RegExp(escapedQ, 'gi')
  let count = 0
  const html = escapeHtml(text).replace(
    new RegExp(escapeHtml(escapedQ), 'gi'),
    (m, offset, str) => {
      const cls = count === 0 ? 'hl hl-current' : 'hl'
      count++
      return `<mark class="${cls}" data-idx="${count - 1}">${m}</mark>`
    }
  )
  return { html, count }
}

function SearchBar({ value, onChange, onPrev, onNext, matchIdx, matchCount, placeholder, inputRef }) {
  return (
    <div className="search-bar">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        onKeyDown={e => {
          if (e.key === 'Enter') { e.shiftKey ? onPrev() : onNext() }
          if (e.key === 'Escape') { e.target.blur() }
        }}
      />
      {value.length >= 2 && (
        <span className="match-count">
          {matchCount === 0 ? 'no matches' : `${matchIdx + 1} / ${matchCount}`}
        </span>
      )}
      <button onClick={onPrev} disabled={matchCount === 0} title="Previous (Shift+Enter)">↑</button>
      <button onClick={onNext} disabled={matchCount === 0} title="Next (Enter)">↓</button>
      {value && <button onClick={() => onChange('')} title="Clear">✕</button>}
    </div>
  )
}

export default function App() {
  const [letters, setLetters] = useState([])
  const [idx, setIdx] = useState(0)
  const [text, setText] = useState('')
  const [saveState, setSaveState] = useState('idle')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [localNotes, setLocalNotes] = useState('')

  // text search
  const [textQuery, setTextQuery] = useState('')
  const [textMatchIdx, setTextMatchIdx] = useState(0)
  const [textMatchCount, setTextMatchCount] = useState(0)

  // pdf/source search
  const [pdfQuery, setPdfQuery] = useState('')
  const [pdfIframeSrc, setPdfIframeSrc] = useState('')

  const notesRef = useRef(null)
  const textSearchRef = useRef(null)
  const pdfSearchRef = useRef(null)
  const saveTimer = useRef(null)
  const iframeRef = useRef(null)
  const textPaneRef = useRef(null)

  useEffect(() => {
    fetch('/api/manifest')
      .then(r => r.json())
      .then(data => {
        setLetters(data)
        setLocalNotes(data[0]?.review?.notes || '')
      })
  }, [])

  const letter = letters[idx]

  useEffect(() => {
    if (!letter) return
    setText('')
    setLocalNotes(letter.review?.notes || '')
    setTextQuery('')
    setPdfQuery('')
    const base = `/api/source/${encodeURIComponent(letter.company)}/${letter.year}`
    setPdfIframeSrc(base + (letter.sourceExt === '.pdf' ? '#view=FitH&toolbar=1' : ''))
    fetch(`/api/text?path=${encodeURIComponent(letter.extractedPath)}`)
      .then(r => r.text())
      .then(setText)
  }, [letter?.key])

  // Recompute match count when text or query changes
  useEffect(() => {
    if (!textQuery || textQuery.length < 2) { setTextMatchCount(0); setTextMatchIdx(0); return }
    const re = new RegExp(textQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
    const matches = [...text.matchAll(re)]
    setTextMatchCount(matches.length)
    setTextMatchIdx(0)
  }, [textQuery, text])

  // Scroll to current text match
  useEffect(() => {
    if (!textPaneRef.current) return
    const marks = textPaneRef.current.querySelectorAll('.hl')
    marks.forEach((m, i) => {
      m.className = i === textMatchIdx ? 'hl hl-current' : 'hl'
    })
    if (marks[textMatchIdx]) {
      marks[textMatchIdx].scrollIntoView({ block: 'center', behavior: 'smooth' })
    }
  }, [textMatchIdx, textMatchCount])

  const textSearchNext = useCallback(() => {
    setTextMatchIdx(i => textMatchCount === 0 ? 0 : (i + 1) % textMatchCount)
  }, [textMatchCount])
  const textSearchPrev = useCallback(() => {
    setTextMatchIdx(i => textMatchCount === 0 ? 0 : (i - 1 + textMatchCount) % textMatchCount)
  }, [textMatchCount])

  const submitPdfSearch = useCallback((q) => {
    if (!letter) return
    const base = `/api/source/${encodeURIComponent(letter.company)}/${letter.year}`
    if (letter.sourceExt === '.pdf') {
      // Chrome's built-in PDF viewer supports #search= fragment
      setPdfIframeSrc(`${base}#search=${encodeURIComponent(q)}&toolbar=1`)
    } else {
      // For HTML iframes (Amazon) — use postMessage to trigger window.find
      try {
        iframeRef.current?.contentWindow?.find(q, false, false, true, false, true, false)
      } catch {}
    }
  }, [letter])

  const saveReview = useCallback((key, status, notes) => {
    setSaveState('saving')
    fetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, status, notes }),
    }).then(() => {
      setSaveState('saved')
      setTimeout(() => setSaveState('idle'), 2000)
    })
  }, [])

  const setStatus = useCallback((status) => {
    if (!letter) return
    setLetters(prev => prev.map((l, i) => i === idx ? { ...l, review: { ...l.review, status } } : l))
    saveReview(letter.key, status, localNotes)
  }, [letters, idx, letter, localNotes, saveReview])

  const handleNotesChange = (e) => {
    const val = e.target.value
    setLocalNotes(val)
    clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      if (letter) saveReview(letter.key, letter.review?.status, val)
    }, 500)
    setLetters(prev => prev.map((l, i) => i === idx ? { ...l, review: { ...l.review, notes: val } } : l))
  }

  const navigate = useCallback((dir) => {
    clearTimeout(saveTimer.current)
    if (letter) saveReview(letter.key, letter.review?.status, localNotes)
    setIdx(prev => Math.max(0, Math.min(letters.length - 1, prev + dir)))
  }, [letter, letters.length, localNotes, saveReview])

  useEffect(() => {
    const onKey = (e) => {
      const tag = document.activeElement?.tagName
      const inInput = tag === 'TEXTAREA' || tag === 'INPUT'
      if (e.key === 'Escape') {
        if (inInput) { document.activeElement.blur() }
        else { setTextQuery(''); setPdfQuery('') }
        return
      }
      if (inInput) return
      if (e.key === 'j' || e.key === 'ArrowRight') { e.preventDefault(); navigate(1) }
      else if (e.key === 'k' || e.key === 'ArrowLeft') { e.preventDefault(); navigate(-1) }
      else if (e.key === '1') setStatus('ok')
      else if (e.key === '2') setStatus('issue')
      else if (e.key === '3') setStatus('skip')
      else if (e.key === '/') { e.preventDefault(); notesRef.current?.focus() }
      else if (e.key === 'f') { e.preventDefault(); textSearchRef.current?.focus() }
      else if (e.key === 'p') { e.preventDefault(); pdfSearchRef.current?.focus() }
      else if (e.key === 'n') textSearchNext()
      else if (e.key === 'N') textSearchPrev()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [navigate, setStatus, textSearchNext, textSearchPrev])

  if (!letters.length) return <div className="loading">Loading…</div>

  const companies = [...new Set(letters.map(l => l.company))]
  const status = letter?.review?.status
  const reviewedCount = letters.filter(l => l.review?.status).length
  const { html: highlightedHtml } = buildHighlightedHtml(text, textQuery)

  return (
    <div id="root" style={{ display: 'flex', flexDirection: 'column', height: '100dvh' }}>
      {/* TOP BAR */}
      <div className="topbar">
        <button className="nav-btn" onClick={() => navigate(-1)} disabled={idx === 0}>← prev</button>
        <div className="letter-title">
          {letter?.company} · {letter?.year} · <span style={{ color: '#888', fontWeight: 400 }}>{letter?.type}</span>
        </div>
        <div className="counter">{idx + 1} / {letters.length} &nbsp; ({reviewedCount} reviewed)</div>
        <div className="status-group">
          {['ok', 'issue', 'skip'].map(s => (
            <button key={s} className={`status-btn ${s}${status === s ? ' active' : ''}`} onClick={() => setStatus(s)}>
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
        <div className={`save-indicator${saveState === 'saved' ? ' saved' : ''}`}>
          {saveState === 'saving' ? 'saving…' : saveState === 'saved' ? '✓ saved' : ''}
        </div>
        <button className="nav-btn" onClick={() => navigate(1)} disabled={idx === letters.length - 1}>next →</button>
      </div>

      {/* MAIN AREA */}
      <div className="main-area">
        {/* SIDEBAR */}
        <div className={`sidebar${sidebarOpen ? '' : ' collapsed'}`}>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(o => !o)}>
            {sidebarOpen ? '◀ hide' : '▶'}
          </button>
          <div className="sidebar-content">
            {companies.map(company => (
              <div key={company} className="sidebar-group">
                <div className="sidebar-company">{company}</div>
                {letters.map((l, i) => l.company !== company ? null : (
                  <div key={l.key} className={`sidebar-item${i === idx ? ' active' : ''}`} onClick={() => setIdx(i)}>
                    <div className={`dot${l.review?.status ? ` ${l.review.status}` : ''}`} />
                    <span className="year">{l.year}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* SPLIT PANE */}
        <div className="split-pane">
          {/* LEFT: source PDF/HTML */}
          <div className="left-pane">
            <div className="pane-search-bar">
              <SearchBar
                value={pdfQuery}
                onChange={setPdfQuery}
                onNext={() => submitPdfSearch(pdfQuery)}
                onPrev={() => {
                  if (letter?.sourceExt === '.html') {
                    try { iframeRef.current?.contentWindow?.find(pdfQuery, false, true, true) } catch {}
                  }
                }}
                matchIdx={0}
                matchCount={pdfQuery.length >= 2 ? 1 : 0}
                placeholder={`Search ${letter?.sourceExt === '.pdf' ? 'PDF' : 'source'} (p)`}
                inputRef={pdfSearchRef}
              />
            </div>
            {letter?.sourceAvailable ? (
              <iframe ref={iframeRef} key={letter?.key} src={pdfIframeSrc} title="Source document" />
            ) : (
              <div className="source-missing">
                Source file not found for {letter?.company} {letter?.year}
              </div>
            )}
          </div>

          {/* RIGHT: extracted text */}
          <div className="right-pane">
            <div className="right-pane-header">
              <span><strong>Extracted text</strong></span>
              <span>Words: {letter?.wordCount}</span>
              <span>Source lines: {letter?.sourceLineRange}</span>
              <div style={{ flex: 1 }} />
              <SearchBar
                value={textQuery}
                onChange={q => { setTextQuery(q); setTextMatchIdx(0) }}
                onNext={textSearchNext}
                onPrev={textSearchPrev}
                matchIdx={textMatchIdx}
                matchCount={textMatchCount}
                placeholder="Search text (f)"
                inputRef={textSearchRef}
              />
            </div>
            <pre
              ref={textPaneRef}
              className="extracted-text"
              dangerouslySetInnerHTML={{ __html: highlightedHtml || 'Loading…' }}
            />
            <div className="notes-area">
              <label>Notes (/ to focus)</label>
              <textarea ref={notesRef} value={localNotes} onChange={handleNotesChange} placeholder="Flag issues here…" />
            </div>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <div className="footer">
        <span><kbd>J</kbd>/<kbd>→</kbd> next &nbsp; <kbd>K</kbd>/<kbd>←</kbd> prev</span>
        <span><kbd>1</kbd> OK &nbsp; <kbd>2</kbd> Issue &nbsp; <kbd>3</kbd> Skip</span>
        <span><kbd>f</kbd> text search &nbsp; <kbd>n</kbd>/<kbd>N</kbd> next/prev match</span>
        <span><kbd>p</kbd> source search &nbsp; <kbd>/</kbd> notes &nbsp; <kbd>Esc</kbd> clear/blur</span>
      </div>
    </div>
  )
}
