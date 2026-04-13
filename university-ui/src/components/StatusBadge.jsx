const STATUS_CONFIG = {
  idle: {
    label: 'Idle',
    color: 'rgba(255,255,255,0.15)',
    dot: '#6b7280',
    text: 'rgba(255,255,255,0.5)',
  },
  listening: {
    label: 'Listening',
    color: 'rgba(16,185,129,0.2)',
    dot: '#10b981',
    text: '#10b981',
  },
  thinking: {
    label: 'Thinking',
    color: 'rgba(201,168,76,0.2)',
    dot: '#c9a84c',
    text: '#c9a84c',
  },
  speaking: {
    label: 'Speaking',
    color: 'rgba(59,130,246,0.2)',
    dot: '#3b82f6',
    text: '#3b82f6',
  },
}

export default function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.idle
  const isAnimated = status === 'listening' || status === 'thinking' || status === 'speaking'

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300"
         style={{ background: cfg.color, color: cfg.text }}>
      <span className="relative flex h-2 w-2">
        {isAnimated && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ background: cfg.dot }} />
        )}
        <span className="relative inline-flex rounded-full h-2 w-2"
              style={{ background: cfg.dot }} />
      </span>
      {cfg.label}
    </div>
  )
}
