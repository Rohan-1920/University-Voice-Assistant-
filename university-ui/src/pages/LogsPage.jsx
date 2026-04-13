import { useState, useEffect, useMemo } from 'react'

const INTENTS = ['All', 'admissions', 'fees', 'courses', 'faculty', 'hostel', 'general', 'other']

function StatCard({ label, value, icon, accent }) {
  return (
    <div className="rounded-2xl p-4 flex items-center gap-4"
         style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
           style={{ background: `${accent}22`, border: `1px solid ${accent}44` }}>
        <span style={{ color: accent }}>{icon}</span>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-xs" style={{ color: 'rgba(255,255,255,0.45)' }}>{label}</div>
      </div>
    </div>
  )
}

function IntentBadge({ intent }) {
  const colors = {
    admissions: '#3b82f6',
    fees: '#10b981',
    courses: '#8b5cf6',
    faculty: '#f59e0b',
    hostel: '#ec4899',
    general: '#6b7280',
    other: '#6b7280',
  }
  const color = colors[intent?.toLowerCase()] || '#6b7280'
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-medium"
          style={{ background: `${color}22`, color }}>
      {intent || '—'}
    </span>
  )
}

export default function LogsPage({ dark }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [intentFilter, setIntentFilter] = useState('All')
  const [page, setPage] = useState(1)
  const PER_PAGE = 15

  useEffect(() => {
    fetchLogs()
  }, [])

  async function fetchLogs() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/history/all?limit=100')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setLogs(Array.isArray(data) ? data : data.logs || [])
    } catch (err) {
      setError(err.message)
      // Demo data for preview
      setLogs(DEMO_LOGS)
    } finally {
      setLoading(false)
    }
  }

  const today = new Date().toISOString().slice(0, 10)

  const stats = useMemo(() => {
    const todayLogs = logs.filter(l => (l.created_at || l.timestamp || '').startsWith(today))
    const intentCounts = {}
    logs.forEach(l => {
      const i = l.intent || 'other'
      intentCounts[i] = (intentCounts[i] || 0) + 1
    })
    const topIntent = Object.entries(intentCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'
    return {
      todayCount: todayLogs.length,
      totalCount: logs.length,
      topIntent,
    }
  }, [logs, today])

  const filtered = useMemo(() => {
    return logs.filter(l => {
      const q = (l.query || l.transcript || '').toLowerCase()
      const matchSearch = !search || q.includes(search.toLowerCase())
      const matchDate = !dateFilter || (l.created_at || l.timestamp || '').startsWith(dateFilter)
      const matchIntent = intentFilter === 'All' || (l.intent || '').toLowerCase() === intentFilter.toLowerCase()
      return matchSearch && matchDate && matchIntent
    })
  }, [logs, search, dateFilter, intentFilter])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE))
  const paginated = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE)

  const handleSearch = (v) => { setSearch(v); setPage(1) }
  const handleDate = (v) => { setDateFilter(v); setPage(1) }
  const handleIntent = (v) => { setIntentFilter(v); setPage(1) }

  const bg = dark ? '#0a0f1e' : '#e8edf5'
  const cardBg = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'
  const border = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'
  const text = dark ? 'rgba(255,255,255,0.85)' : '#1e3a5f'
  const subtext = dark ? 'rgba(255,255,255,0.45)' : 'rgba(30,58,95,0.5)'
  const inputBg = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'

  return (
    <div className="min-h-screen p-4 md:p-8" style={{ background: bg }}>
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold" style={{ color: text }}>
            Call Logs
            <span className="ml-2 text-base font-normal" style={{ color: '#c9a84c' }}>Admin Dashboard</span>
          </h1>
          <p className="text-sm mt-1" style={{ color: subtext }}>
            All voice interactions with the GIFT University AI agent
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <StatCard label="Calls Today" value={stats.todayCount} icon="📞" accent="#10b981" />
          <StatCard label="Total Calls" value={stats.totalCount} icon="📊" accent="#c9a84c" />
          <StatCard label="Top Intent" value={stats.topIntent} icon="🎯" accent="#3b82f6" />
        </div>

        {/* Filters */}
        <div className="rounded-2xl p-4 mb-6 flex flex-wrap gap-3 items-center"
             style={{ background: cardBg, border: `1px solid ${border}` }}>

          {/* Search */}
          <div className="relative flex-1 min-w-48">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2" width="14" height="14"
                 viewBox="0 0 24 24" fill="none" stroke={subtext} strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              placeholder="Search queries..."
              value={search}
              onChange={e => handleSearch(e.target.value)}
              className="w-full pl-8 pr-4 py-2 rounded-xl text-sm outline-none transition-all"
              style={{ background: inputBg, color: text, border: `1px solid ${border}` }}
            />
          </div>

          {/* Date */}
          <input
            type="date"
            value={dateFilter}
            onChange={e => handleDate(e.target.value)}
            className="px-3 py-2 rounded-xl text-sm outline-none"
            style={{ background: inputBg, color: text, border: `1px solid ${border}` }}
          />

          {/* Intent filter */}
          <select
            value={intentFilter}
            onChange={e => handleIntent(e.target.value)}
            className="px-3 py-2 rounded-xl text-sm outline-none"
            style={{ background: inputBg, color: text, border: `1px solid ${border}` }}>
            {INTENTS.map(i => <option key={i} value={i}>{i}</option>)}
          </select>

          {/* Clear */}
          {(search || dateFilter || intentFilter !== 'All') && (
            <button
              onClick={() => { setSearch(''); setDateFilter(''); setIntentFilter('All'); setPage(1) }}
              className="px-3 py-2 rounded-xl text-sm transition-all hover:opacity-80"
              style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.2)' }}>
              Clear
            </button>
          )}

          <button onClick={fetchLogs}
                  className="px-3 py-2 rounded-xl text-sm transition-all hover:opacity-80 ml-auto"
                  style={{ background: 'rgba(201,168,76,0.15)', color: '#c9a84c', border: '1px solid rgba(201,168,76,0.2)' }}>
            ↻ Refresh
          </button>
        </div>

        {/* Table */}
        <div className="rounded-2xl overflow-hidden"
             style={{ background: cardBg, border: `1px solid ${border}` }}>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-8 h-8 rounded-full border-2 border-gold/30 border-t-gold animate-spin" />
            </div>
          ) : error && logs.length === 0 ? (
            <div className="text-center py-20" style={{ color: subtext }}>
              <p className="text-4xl mb-3">⚠️</p>
              <p>Could not connect to backend</p>
              <p className="text-xs mt-1">{error}</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-20" style={{ color: subtext }}>
              <p className="text-4xl mb-3">🔍</p>
              <p>No results found</p>
            </div>
          ) : (
            <>
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ borderBottom: `1px solid ${border}` }}>
                      {['Date', 'Time', 'User ID', 'Query', 'Response', 'Intent'].map(h => (
                        <th key={h} className="text-left px-4 py-3 font-medium text-xs uppercase tracking-wider"
                            style={{ color: subtext }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {paginated.map((log, i) => {
                      const dt = new Date(log.created_at || log.timestamp || Date.now())
                      const dateStr = isNaN(dt) ? '—' : dt.toLocaleDateString()
                      const timeStr = isNaN(dt) ? '—' : dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      return (
                        <tr key={log.id || i}
                            className="transition-colors hover:bg-white/5"
                            style={{ borderBottom: `1px solid ${border}` }}>
                          <td className="px-4 py-3 whitespace-nowrap" style={{ color: subtext }}>{dateStr}</td>
                          <td className="px-4 py-3 whitespace-nowrap" style={{ color: subtext }}>{timeStr}</td>
                          <td className="px-4 py-3">
                            <span className="font-mono text-xs px-2 py-0.5 rounded"
                                  style={{ background: 'rgba(255,255,255,0.06)', color: text }}>
                              {(log.user_id || '—').slice(0, 12)}
                            </span>
                          </td>
                          <td className="px-4 py-3 max-w-xs">
                            <p className="truncate" style={{ color: text }} title={log.query || log.transcript}>
                              {log.query || log.transcript || '—'}
                            </p>
                          </td>
                          <td className="px-4 py-3 max-w-xs">
                            <p className="truncate" style={{ color: subtext }} title={log.response}>
                              {log.response || '—'}
                            </p>
                          </td>
                          <td className="px-4 py-3">
                            <IntentBadge intent={log.intent} />
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden divide-y" style={{ borderColor: border }}>
                {paginated.map((log, i) => {
                  const dt = new Date(log.created_at || log.timestamp || Date.now())
                  const dateStr = isNaN(dt) ? '—' : `${dt.toLocaleDateString()} ${dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                  return (
                    <div key={log.id || i} className="p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs" style={{ color: subtext }}>{dateStr}</span>
                        <IntentBadge intent={log.intent} />
                      </div>
                      <p className="text-sm font-medium" style={{ color: text }}>
                        {log.query || log.transcript || '—'}
                      </p>
                      <p className="text-xs line-clamp-2" style={{ color: subtext }}>
                        {log.response || '—'}
                      </p>
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 px-1">
            <span className="text-xs" style={{ color: subtext }}>
              {filtered.length} results · page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1.5 rounded-lg text-sm disabled:opacity-30 transition-all hover:opacity-80"
                style={{ background: cardBg, color: text, border: `1px solid ${border}` }}>
                ← Prev
              </button>
              <button
                disabled={page === totalPages}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1.5 rounded-lg text-sm disabled:opacity-30 transition-all hover:opacity-80"
                style={{ background: cardBg, color: text, border: `1px solid ${border}` }}>
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Demo data shown when backend is offline
const DEMO_LOGS = [
  { id: 1, created_at: new Date().toISOString(), user_id: 'user_abc123', query: 'What are the admission requirements?', response: 'For undergraduate admission you need FSc with at least 60% marks...', intent: 'admissions' },
  { id: 2, created_at: new Date().toISOString(), user_id: 'user_def456', query: 'How much is the semester fee?', response: 'The semester fee for BS programs is PKR 45,000...', intent: 'fees' },
  { id: 3, created_at: new Date(Date.now() - 86400000).toISOString(), user_id: 'user_ghi789', query: 'What courses are offered in CS?', response: 'The CS department offers BS, MS and PhD programs...', intent: 'courses' },
  { id: 4, created_at: new Date(Date.now() - 86400000).toISOString(), user_id: 'user_jkl012', query: 'Is hostel available for female students?', response: 'Yes, GIFT University has separate hostels for male and female students...', intent: 'hostel' },
  { id: 5, created_at: new Date(Date.now() - 172800000).toISOString(), user_id: 'user_mno345', query: 'Who is the head of the CS department?', response: 'The CS department is headed by Dr. Ahmed...', intent: 'faculty' },
]
