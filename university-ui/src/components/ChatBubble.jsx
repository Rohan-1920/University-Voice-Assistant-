const INTENT_COLORS = {
  programs: '#8b5cf6', fee: '#10b981', admission_process: '#3b82f6',
  eligibility: '#f59e0b', documents: '#ec4899', dates: '#06b6d4',
  scholarship: '#c9a84c', hostel: '#84cc16', transport: '#f97316',
  contact: '#6b7280', general: '#6b7280',
}

export default function ChatBubble({ message, dark = true }) {
  const isUser = message.role === 'user'
  const intentColor = INTENT_COLORS[message.intent] || '#6b7280'

  return (
    <div className="slide-up" style={{
      display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 10, alignItems: 'flex-end', gap: 8,
    }}>
      {!isUser && (
        <div style={{
          width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
          background: 'linear-gradient(135deg, #1e3a5f, #c9a84c)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700, color: 'white',
          boxShadow: '0 2px 8px rgba(201,168,76,0.2)',
        }}>G</div>
      )}

      <div style={{ maxWidth: '76%' }}>
        <div style={{
          padding: '10px 14px', borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          fontSize: 13.5, lineHeight: 1.6,
          background: isUser
            ? 'linear-gradient(135deg, #1d4ed8, #2563eb)'
            : 'rgba(255,255,255,0.07)',
          border: isUser ? 'none' : '1px solid rgba(255,255,255,0.08)',
          color: isUser ? '#fff' : 'rgba(255,255,255,0.92)',
          boxShadow: isUser ? '0 4px 16px rgba(37,99,235,0.25)' : 'none',
        }}>
          {message.text}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4, justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
          {!isUser && message.intent && message.intent !== 'unknown' && (
            <span style={{
              fontSize: 10, padding: '2px 8px', borderRadius: 99, fontWeight: 500,
              background: `${intentColor}18`, color: intentColor,
              border: `1px solid ${intentColor}30`,
            }}>
              {message.intent.replace('_', ' ')}
            </span>
          )}
          <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)' }}>{message.time}</span>
        </div>
      </div>

      {isUser && (
        <div style={{
          width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
          background: 'rgba(37,99,235,0.25)', border: '1px solid rgba(37,99,235,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700, color: '#93c5fd',
        }}>U</div>
      )}
    </div>
  )
}
