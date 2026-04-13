export default function ChatBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex animate-slide-up ${isUser ? 'justify-end' : 'justify-start'} mb-2`}>
      {!isUser && (
        <div className="w-6 h-6 rounded-full flex-shrink-0 mr-2 mt-1 flex items-center justify-center text-xs font-bold"
             style={{ background: 'linear-gradient(135deg, #1e3a5f, #c9a84c)', color: 'white' }}>
          G
        </div>
      )}

      <div className="max-w-[75%]">
        <div className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'rounded-tr-sm text-white'
            : 'rounded-tl-sm text-white/90'
        }`}
          style={{
            background: isUser
              ? 'linear-gradient(135deg, #2563eb, #1d4ed8)'
              : 'rgba(255,255,255,0.08)',
            border: isUser ? 'none' : '1px solid rgba(255,255,255,0.08)',
            boxShadow: isUser ? '0 4px 12px rgba(37,99,235,0.3)' : 'none',
          }}>
          {message.text}
        </div>

        {message.intent && !isUser && (
          <div className="mt-1 ml-1">
            <span className="text-xs px-2 py-0.5 rounded-full"
                  style={{ background: 'rgba(201,168,76,0.15)', color: '#c9a84c' }}>
              {message.intent}
            </span>
          </div>
        )}

        <div className={`text-xs mt-1 ${isUser ? 'text-right' : 'text-left'}`}
             style={{ color: 'rgba(255,255,255,0.3)' }}>
          {message.time}
        </div>
      </div>

      {isUser && (
        <div className="w-6 h-6 rounded-full flex-shrink-0 ml-2 mt-1 flex items-center justify-center text-xs font-bold"
             style={{ background: 'rgba(37,99,235,0.3)', color: '#93c5fd' }}>
          U
        </div>
      )}
    </div>
  )
}
