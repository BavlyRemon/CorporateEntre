import express from 'express'
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs'
import { createReadStream } from 'fs'
import { join, resolve, extname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = resolve(__dirname, '../..')
const MANIFEST_PATH = join(ROOT, '02_extracted_text/selected_ceo_letters/selected_ceo_letters_manifest.csv')
const REVIEW_PATH = join(ROOT, '00_admin/extraction_review.json')

const app = express()
app.use(express.json())

function parseCSV(text) {
  const lines = text.trim().split('\n')
  const headers = lines[0].split(',')
  return lines.slice(1).map(line => {
    const vals = []
    let cur = '', inQ = false
    for (const ch of line) {
      if (ch === '"') { inQ = !inQ }
      else if (ch === ',' && !inQ) { vals.push(cur); cur = '' }
      else cur += ch
    }
    vals.push(cur)
    const row = {}
    headers.forEach((h, i) => { row[h.trim()] = (vals[i] || '').trim() })
    return row
  })
}

function reviewKey(company, year) {
  return `${company.toLowerCase()}_${year}`
}

function resolveSource(company, year) {
  const c = company.toLowerCase()
  if (c === 'amazon') {
    const p = join(ROOT, `01_raw_sources/amazon/letters/amazon_${year}_shareholder_letter.html`)
    return existsSync(p) ? p : null
  }
  if (c === 'nvidia') {
    if (year === '2025') {
      const standalone = join(ROOT, '01_raw_sources/nvidia/letters/nvidia_2025_ceo_letter.pdf')
      if (existsSync(standalone)) return standalone
    }
    const p = join(ROOT, `01_raw_sources/nvidia/annual_reports/nvidia_${year}_annual_report.pdf`)
    return existsSync(p) ? p : null
  }
  if (c === 'shell') {
    const p = join(ROOT, `01_raw_sources/shell/annual_reports/shell_${year}_annual_report.pdf`)
    return existsSync(p) ? p : null
  }
  if (c === 'chevron') {
    const p = join(ROOT, `01_raw_sources/chevron/annual_reports/chevron_${year}_annual_report.pdf`)
    return existsSync(p) ? p : null
  }
  return null
}

app.get('/api/manifest', (req, res) => {
  const rows = parseCSV(readFileSync(MANIFEST_PATH, 'utf8'))
  const review = existsSync(REVIEW_PATH) ? JSON.parse(readFileSync(REVIEW_PATH, 'utf8')) : {}
  const data = rows.map(r => {
    const key = reviewKey(r.company, r.year)
    const src = resolveSource(r.company, r.year)
    return {
      key,
      company: r.company,
      year: r.year,
      title: r.title,
      type: r.selected_text_type,
      extractedPath: r.extracted_letter_path,
      sourceLineRange: r.source_line_range,
      wordCount: r.word_count,
      notes: r.notes,
      sourceAvailable: !!src,
      sourceExt: src ? extname(src) : null,
      review: review[key] || { status: null, notes: '' },
    }
  })
  res.json(data)
})

app.get('/api/text', (req, res) => {
  const rel = req.query.path
  if (!rel || !rel.startsWith('02_extracted_text/')) {
    return res.status(400).send('invalid path')
  }
  const abs = join(ROOT, rel)
  if (!existsSync(abs)) return res.status(404).send('not found')
  res.type('text/plain').send(readFileSync(abs, 'utf8'))
})

app.get('/api/source/:company/:year', (req, res) => {
  const src = resolveSource(req.params.company, req.params.year)
  if (!src) return res.status(404).send('source not found')
  const ext = extname(src).toLowerCase()
  if (ext === '.html') {
    const raw = readFileSync(src, 'utf8')
    // Extract <main> content so the iframe shows only the letter, not site chrome
    const mainMatch = raw.match(/<main[\s\S]*?>([\s\S]*?)<\/main>/i)
    const body = mainMatch ? mainMatch[0] : raw
    const cleaned = `<!doctype html><html><head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  body { font-family: Georgia, serif; font-size: 16px; line-height: 1.7; color: #222;
         max-width: 780px; margin: 0 auto; padding: 24px 32px; background: #fff; }
  nav, header, footer, [class*="nav"], [class*="Nav"], [class*="header"], [class*="Header"],
  [class*="footer"], [class*="Footer"], [class*="share"], [class*="Share"],
  [class*="social"], [class*="Social"], [class*="sidebar"], [class*="Sidebar"],
  [class*="breadcrumb"], [class*="Breadcrumb"], [class*="menu"], [class*="Menu"],
  [class*="banner"], [class*="Banner"], [class*="cookie"], [class*="Cookie"],
  [class*="related"], [class*="Related"], [class*="subscribe"], [class*="Subscribe"],
  button, [role="navigation"], [role="banner"], [role="complementary"] { display: none !important; }
  img { max-width: 100%; }
  h1 { font-size: 1.8em; margin-bottom: 0.3em; }
  h2 { font-size: 1.3em; margin-top: 1.5em; }
  p { margin: 0.8em 0; }
  a { color: inherit; }
</style>
</head><body>${body}</body></html>`
    res.setHeader('Content-Type', 'text/html')
    res.send(cleaned)
  } else {
    res.setHeader('Content-Type', 'application/pdf')
    createReadStream(src).pipe(res)
  }
})

app.post('/api/review', (req, res) => {
  const { key, status, notes } = req.body
  if (!key) return res.status(400).send('missing key')
  const existing = existsSync(REVIEW_PATH) ? JSON.parse(readFileSync(REVIEW_PATH, 'utf8')) : {}
  existing[key] = { status, notes: notes || '', reviewed_at: new Date().toISOString() }
  writeFileSync(REVIEW_PATH, JSON.stringify(existing, null, 2))
  res.json({ ok: true })
})

app.listen(3001, () => console.log('API server → http://localhost:3001'))
