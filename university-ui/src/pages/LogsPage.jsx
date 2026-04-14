import { useState, useEffect, useMemo, useCallback } from 'react'

const INTENT_COLORS = {
  programs: '#8b5cf6', fee: '#10b981', admission_process: '#3b82f6',
  eligibility: '#f59e0b', documents: '#ec4899', dates: '#06b6d4',
  scholarship: '#c9a84c', hostel: '#84cc16', transport: '#f97316',
  contact: '#6b7280', general: '#6b7280', unknown: '#4b5563',
}

function fmt(iso) {
  if (!iso) return { date: '—', time: '—' }
  const d = new Date(iso)
  if (isNaN(d)) return { date: '—', time: '—' }
  return {
    date: d.toLocaleDateString('en-PK', { day: '2-digit', month: 'short', year: 'numeric' }),
    time: d.toLocaleTimeString('en-PK', { hour: '2-digit', minute: '2-digit', hour12: true }),
  }
}

function StatCard({ label, value, icon, color, dark }) {
  return (
    <div style={{
      background: dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
      border: `1px solid ${color}25`,
      borderRadius: 20, padding: '24px 22px',
      display: 'flex', alignItems: 'center', gap: 16,
      transition: 'all 0.2s',
      boxShadow: `0 4px 24px ${color}0a`,
    }}>
      <div style={{
        width: 52, height: 52, borderRadius: 16, flexShrink: 0,
        background: `${color}15`, border: `1px solid ${color}28`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>{icon}</div>
      <div>
        <div style={{
          fontSize: 30, fontWeight: 900, lineHeight: 1,
          color: dark ? '#fff' : '#1a1a2e',
          fontFamily: "'Playfair Display', Georgia, serif",
          fontStyle: 'italic',
        }}>{value}</div>
        <div style={{ fontSize: 12, color: dark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.4)', marginTop: 5, fontWeight: 500, letterSpacing: '0.02em' }}>{label}</div>
      </div>
    </div>
  )
}

function IntentBadge({ intent }) {
  const color = INTENT_COLORS[intent?.toLowerCase()] || '#6b7280'
  return (
    <span style={{
      padding: '3px 10px', borderRadius: 99, fontSize: 11, fontWeight: 600,
      background: `${color}18`, color, border: `1px solid ${color}30`,
      whiteSpace: 'nowrap',
    }}>
      {intent?.replace('_', ' ') || '—'}
    </span>
  )
}

export default function LogsPage({ dark }) {
  const [logs, setLogs]           = useState([])
  const [loading, setLoading]     = useState(true)
  const [search, setSearch]       = useState('')
  const [dateFilter, setDate]     = useState('')
  const [intentFilter, setIntent] = useState('All')
  const [page, setPage]           = useState(1)
  const [expanded, setExpanded]   = useState(null)
  const PER_PAGE = 12

  const bg      = dark ? '#0f0a1e' : '#f1f5f9'
  const card    = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)'
  const border  = dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)'
  const text    = dark ? 'rgba(255,255,255,0.9)'  : '#1e3a5f'
  const sub     = dark ? 'rgba(255,255,255,0.4)'  : 'rgba(30,58,95,0.5)'
  const inputBg = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/history/all?limit=500')
      if (!res.ok) throw new Error()
      const data = await res.json()
      const arr = Array.isArray(data) ? data : (data.history || data.logs || [])
      setLogs(arr)
    } catch {
      setLogs([])
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load + auto-refresh every 30s
  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 30000)
    return () => clearInterval(interval)
  }, [fetchLogs])

  const today = new Date().toISOString().slice(0, 10)

  const stats = useMemo(() => {
    const todayLogs = logs.filter(l => (l.created_at || l.timestamp || '').startsWith(today))
    const counts = {}
    logs.forEach(l => { const i = l.intent || 'unknown'; counts[i] = (counts[i] || 0) + 1 })
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—'
    const uniqueUsers = new Set(logs.map(l => l.user_id)).size
    return { today: todayLogs.length, total: logs.length, top, users: uniqueUsers }
  }, [logs, today])

  const intents = useMemo(() => ['All', ...new Set(logs.map(l => l.intent).filter(Boolean))], [logs])

  const filtered = useMemo(() => logs.filter(l => {
    const q = (l.query || '').toLowerCase()
    return (
      (!search || q.includes(search.toLowerCase())) &&
      (!dateFilter || (l.created_at || l.timestamp || '').startsWith(dateFilter)) &&
      (intentFilter === 'All' || l.intent === intentFilter)
    )
  }), [logs, search, dateFilter, intentFilter])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE))
  const paginated  = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE)

  const inputStyle = {
    background: inputBg, color: text, border: `1px solid ${border}`,
    borderRadius: 10, padding: '8px 12px', fontSize: 13, outline: 'none',
    transition: 'border-color 0.2s',
  }

  return (
    <div style={{ minHeight: '100vh', background: bg, padding: '32px 24px' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: 32, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 800, color: text, margin: 0, lineHeight: 1.2 }}>
              Analytics
              <span style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontStyle: 'italic',
                color: '#a78bfa', fontWeight: 400, fontSize: 20, marginLeft: 10,
              }}>Call Statistics</span>
            </h1>
            <p style={{ color: sub, fontSize: 13, marginTop: 6 }}>
              Real-time conversation data · Auto-refreshes every 30s
            </p>
          </div>
          <button onClick={fetchLogs} style={{
            padding: '8px 18px', borderRadius: 10, border: `1px solid rgba(124,58,237,0.3)`,
            background: 'rgba(124,58,237,0.12)', color: '#a78bfa', fontSize: 13, fontWeight: 600,
            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
          }}>
            ↻ Refresh
          </button>
        </div>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 28 }}>
          <StatCard label="Calls Today"    value={stats.today} icon={<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="1.8" strokeLinecap="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.4 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.8a16 16 0 0 0 6.29 6.29l.95-.95a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>} color="#a78bfa" dark={dark} />
          <StatCard label="Total Calls"    value={stats.total} icon={<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8" strokeLinecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>} color="#7c3aed" dark={dark} />
          <StatCard label="Unique Users"   value={stats.users} icon={<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6d28d9" strokeWidth="1.8" strokeLinecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>} color="#6d28d9" dark={dark} />
          <StatCard label="Top Intent"     value={stats.top.replace('_',' ')} icon={<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>} color="#a78bfa" dark={dark} />
        </div>

        {/* Filters */}
        <div style={{
          background: card, border: `1px solid ${border}`, borderRadius: 16,
          padding: '16px 20px', marginBottom: 20,
          display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center',
        }}>
          <div style={{ position: 'relative', flex: '1 1 200px' }}>
            <svg style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }}
                 width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={sub} strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text" placeholder="Search queries..."
              value={search} onChange={e => { setSearch(e.target.value); setPage(1) }}
              style={{ ...inputStyle, width: '100%', paddingLeft: 30 }}
            />
          </div>

          <input type="date" value={dateFilter}
            onChange={e => { setDate(e.target.value); setPage(1) }}
            style={{ ...inputStyle, colorScheme: dark ? 'dark' : 'light' }}
          />

          <select value={intentFilter} onChange={e => { setIntent(e.target.value); setPage(1) }}
            style={{ ...inputStyle, cursor: 'pointer', colorScheme: dark ? 'dark' : 'light' }}>
            {intents.map(i => <option key={i} value={i} style={{ background: dark ? '#1a1025' : '#fff', color: dark ? '#fff' : '#1a1a2e' }}>{i}</option>)}
          </select>

          {(search || dateFilter || intentFilter !== 'All') && (
            <button onClick={() => { setSearch(''); setDate(''); setIntent('All'); setPage(1) }}
              style={{ ...inputStyle, background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.2)', cursor: 'pointer' }}>
              ✕ Clear
            </button>
          )}

          <span style={{ marginLeft: 'auto', color: sub, fontSize: 12 }}>
            {filtered.length} results
          </span>
        </div>

        {/* Table */}
        <div style={{ background: card, border: `1px solid ${border}`, borderRadius: 16, overflow: 'hidden' }}>
          {loading ? (
            <div style={{ padding: '60px 0', textAlign: 'center' }}>
              {[1,2,3,4,5].map(i => (
                <div key={i} className="shimmer" style={{ height: 52, margin: '1px 0' }} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: '60px 0', textAlign: 'center', color: sub }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🔍</div>
              <div>No results found</div>
            </div>
          ) : (
            <>
              {/* Table header */}
              <div style={{
                display: 'grid', gridTemplateColumns: '110px 80px 100px 1fr 1fr 110px',
                padding: '12px 20px', borderBottom: `1px solid ${border}`,
                fontSize: 11, fontWeight: 700, color: sub, letterSpacing: '0.06em', textTransform: 'uppercase',
              }}>
                {['Date', 'Time', 'User', 'Query', 'Response', 'Intent'].map(h => (
                  <div key={h}>{h}</div>
                ))}
              </div>

              {/* Rows */}
              {paginated.map((log, i) => {
                const { date, time } = fmt(log.created_at || log.timestamp)
                const isExp = expanded === (log.id || i)
                return (
                  <div key={log.id || i}
                    onClick={() => setExpanded(isExp ? null : (log.id || i))}
                    style={{
                      display: 'grid', gridTemplateColumns: '110px 80px 100px 1fr 1fr 110px',
                      padding: '14px 20px', borderBottom: `1px solid ${border}`,
                      cursor: 'pointer', transition: 'background 0.15s',
                      background: isExp ? (dark ? 'rgba(201,168,76,0.05)' : 'rgba(201,168,76,0.04)') : 'transparent',
                      alignItems: 'start',
                    }}
                    onMouseEnter={e => !isExp && (e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)')}
                    onMouseLeave={e => !isExp && (e.currentTarget.style.background = 'transparent')}
                  >
                    <div style={{ fontSize: 12, color: sub }}>{date}</div>
                    <div style={{ fontSize: 12, color: sub }}>{time}</div>
                    <div>
                      <span style={{
                        fontFamily: 'monospace', fontSize: 11, padding: '2px 7px', borderRadius: 6,
                        background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)', color: text,
                      }}>
                        {(log.user_id || '—').slice(-8)}
                      </span>
                    </div>
                    <div style={{ fontSize: 13, color: text, paddingRight: 12 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: isExp ? 'normal' : 'nowrap' }}>
                        {log.query || '—'}
                      </div>
                    </div>
                    <div style={{ fontSize: 12, color: sub, paddingRight: 12 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: isExp ? 'normal' : 'nowrap' }}>
                        {log.response || '—'}
                      </div>
                    </div>
                    <div><IntentBadge intent={log.intent} /></div>
                  </div>
                )
              })}
            </>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16 }}>
            <span style={{ fontSize: 12, color: sub }}>Page {page} of {totalPages}</span>
            <div style={{ display: 'flex', gap: 8 }}>
              {[...Array(Math.min(totalPages, 7))].map((_, i) => {
                const p = i + 1
                return (
                  <button key={p} onClick={() => setPage(p)} style={{
                    width: 32, height: 32, borderRadius: 8, border: 'none', cursor: 'pointer',
                    background: page === p ? '#7c3aed' : inputBg,
                    color: page === p ? '#fff' : text,
                    fontWeight: page === p ? 700 : 400, fontSize: 13,
                  }}>{p}</button>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
