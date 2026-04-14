const CFG = {
  idle:      { label: 'Ready',     dot: '#4b5563', bg: 'rgba(75,85,99,0.15)',     text: 'rgba(255,255,255,0.4)', pulse: false },
  listening: { label: 'Listening', dot: '#10b981', bg: 'rgba(16,185,129,0.15)',   text: '#10b981',               pulse: true  },
  thinking:  { label: 'Thinking',  dot: '#c9a84c', bg: 'rgba(201,168,76,0.15)',   text: '#c9a84c',               pulse: true  },
  speaking:  { label: 'Speaking',  dot: '#3b82f6', bg: 'rgba(59,130,246,0.15)',   text: '#60a5fa',               pulse: true  },
}

export default function StatusBadge({ status }) {
  const c = CFG[status] || CFG.idle
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '5px 12px', borderRadius: 99,
      background: c.bg, color: c.text,
      fontSize: 11, fontWeight: 600, letterSpacing: '0.04em',
      border: `1px solid ${c.dot}33`,
      transition: 'all 0.3s ease',
    }}>
      <span style={{ position: 'relative', display: 'flex', width: 7, height: 7 }}>
        {c.pulse && (
          <span className="ping" style={{
            position: 'absolute', inset: 0,
            borderRadius: '50%', background: c.dot, opacity: 0.5,
          }} />
        )}
        <span style={{ width: 7, height: 7, borderRadius: '50%', background: c.dot, display: 'block' }} />
      </span>
      {c.label}
    </div>
  )
}
