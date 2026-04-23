import { useState, useRef, useEffect } from 'react'

const USER_ID = `chat_${Math.random().toString(36).slice(2, 9)}`

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{ display:'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom:12, animation:'fadeUp 0.2s ease' }}>
      {!isUser && (
        <img src="/gift-logo.png" alt="GIFT" style={{ width:28, height:28, objectFit:'contain', marginRight:8, marginTop:2, flexShrink:0 }} />
      )}
      <div style={{ maxWidth:'75%' }}>
        <div style={{
          padding:'11px 16px',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          background: isUser
            ? 'linear-gradient(135deg,#7c3aed,#6d28d9)'
            : 'rgba(255,255,255,0.07)',
          border: isUser ? 'none' : '1px solid rgba(255,255,255,0.09)',
          color: isUser ? '#fff' : 'rgba(255,255,255,0.92)',
          fontSize: 14, lineHeight: 1.65,
          boxShadow: isUser ? '0 4px 16px rgba(124,58,237,0.25)' : 'none',
        }}>
          {msg.text}
        </div>
        <div style={{ fontSize:10, color:'rgba(255,255,255,0.25)', marginTop:4, textAlign: isUser ? 'right' : 'left', paddingLeft: isUser ? 0 : 4 }}>
          {msg.time}
          {msg.intent && msg.intent !== 'unknown' && !isUser && (
            <span style={{ marginLeft:6, padding:'1px 7px', borderRadius:99, background:'rgba(124,58,237,0.15)', color:'#a78bfa', fontSize:10 }}>
              {msg.intent.replace('_',' ')}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
      <img src="/gift-logo.png" alt="GIFT" style={{ width:28, height:28, objectFit:'contain', flexShrink:0 }} />
      <div style={{ display:'flex', gap:5, padding:'12px 16px', borderRadius:'18px 18px 18px 4px', background:'rgba(255,255,255,0.07)', border:'1px solid rgba(255,255,255,0.09)' }}>
        {[0,1,2].map(i => (
          <div key={i} style={{ width:7, height:7, borderRadius:'50%', background:'#a78bfa', animation:`bounce 0.7s ${i*0.15}s infinite alternate` }} />
        ))}
      </div>
    </div>
  )
}

export default function ChatPage({ dark }) {
  const [messages, setMessages] = useState([
    { role:'bot', text:"Assalam o Alaikum! I'm GIFT University's AI assistant. Ask me anything about admissions, programs, fees, or scholarships — in Urdu or English.", time: now(), id:0 }
  ])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const chatEndRef             = useRef(null)
  const inputRef               = useRef(null)

  function now() {
    return new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior:'smooth' })
  }, [messages, loading])

  const send = async (text) => {
    if (!text.trim() || loading) return
    const userMsg = { role:'user', text: text.trim(), time: now(), id: Date.now() }
    setMessages(p => [...p, userMsg])
    setInput('')
    setLoading(true)

    try {
      const r = await fetch('/demo/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim(), user_id: USER_ID }),
      })
      const d = await r.json()
      setMessages(p => [...p, {
        role: 'bot',
        text: d.response || 'Sorry, something went wrong.',
        intent: d.intent,
        time: now(),
        id: Date.now() + 1,
      }])
    } catch {
      setMessages(p => [...p, { role:'bot', text:'Connection error. Please try again.', time: now(), id: Date.now()+1 }])
    }
    setLoading(false)
    inputRef.current?.focus()
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) }
  }

  const bg   = dark ? '#080612' : '#f4f4f8'
  const card = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)'
  const bdr  = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'
  const inputBg = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'

  // Quick suggestion chips
  const suggestions = [
    'BS Data Science admission?',
    'PhD documents required?',
    'Fee structure for BS?',
    'Scholarship options?',
    'Hostel available?',
    'Admission dates 2025?',
  ]

  return (
    <div style={{ minHeight:'100vh', background: bg, display:'flex', flexDirection:'column', position:'relative' }}>

      {/* Background */}
      <div style={{ position:'fixed', inset:0, backgroundImage:'url(/gift-campus.jpg)', backgroundSize:'cover', backgroundPosition:'center top', opacity:0.1, zIndex:0 }} />
      <div style={{ position:'fixed', inset:0, background: dark ? 'linear-gradient(180deg,rgba(8,6,18,0.9) 0%,rgba(8,6,18,0.97) 100%)' : 'rgba(244,244,248,0.92)', zIndex:1 }} />

      <div style={{ position:'relative', zIndex:2, display:'flex', flexDirection:'column', height:'calc(100vh - 64px)', maxWidth:760, width:'100%', margin:'0 auto', padding:'0 16px' }}>

        {/* Header */}
        <div style={{ padding:'20px 0 16px', borderBottom:`1px solid ${bdr}`, display:'flex', alignItems:'center', gap:12 }}>
          <img src="/gift-logo.png" alt="GIFT" style={{ width:40, height:40, objectFit:'contain' }} />
          <div>
            <div style={{ color: dark ? '#fff' : '#1a1a2e', fontWeight:700, fontSize:16, letterSpacing:'-0.2px' }}>GIFT University</div>
            <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:2 }}>
              <span style={{ width:7, height:7, borderRadius:'50%', background:'#10b981', boxShadow:'0 0 6px #10b981', display:'inline-block', animation:'livePulse 2s infinite' }} />
              <span style={{ color:'#10b981', fontSize:12, fontWeight:600 }}>AI Assistant Online</span>
            </div>
          </div>
          <div style={{ marginLeft:'auto', color: dark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)', fontSize:12 }}>
            Urdu &amp; English supported
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex:1, overflowY:'auto', padding:'20px 0', minHeight:0 }}>
          {messages.map(msg => <Message key={msg.id} msg={msg} />)}
          {loading && <TypingIndicator />}
          <div ref={chatEndRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && !loading && (
          <div style={{ display:'flex', flexWrap:'wrap', gap:8, paddingBottom:12 }}>
            {suggestions.map(s => (
              <button key={s} onClick={() => send(s)} style={{
                padding:'7px 14px', borderRadius:99, fontSize:12, fontWeight:500, cursor:'pointer',
                background:'rgba(124,58,237,0.1)', color:'#a78bfa',
                border:'1px solid rgba(124,58,237,0.25)', transition:'all 0.2s',
              }}
              onMouseEnter={e => e.currentTarget.style.background='rgba(124,58,237,0.2)'}
              onMouseLeave={e => e.currentTarget.style.background='rgba(124,58,237,0.1)'}>
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div style={{ paddingBottom:20, paddingTop:8 }}>
          <div style={{ display:'flex', gap:10, alignItems:'flex-end', background: inputBg, border:`1px solid ${bdr}`, borderRadius:16, padding:'10px 12px' }}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKey}
              placeholder="Type your question in Urdu or English..."
              rows={1}
              style={{
                flex:1, background:'transparent', border:'none', outline:'none', resize:'none',
                color: dark ? 'rgba(255,255,255,0.9)' : '#1a1a2e',
                fontSize:14, lineHeight:1.6, fontFamily:'inherit',
                maxHeight:120, overflowY:'auto',
              }}
            />
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || loading}
              style={{
                width:40, height:40, borderRadius:12, border:'none', cursor:'pointer',
                background: input.trim() && !loading ? 'linear-gradient(135deg,#7c3aed,#6d28d9)' : 'rgba(255,255,255,0.08)',
                display:'flex', alignItems:'center', justifyContent:'center',
                transition:'all 0.2s', flexShrink:0,
                boxShadow: input.trim() && !loading ? '0 4px 16px rgba(124,58,237,0.4)' : 'none',
              }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={input.trim() && !loading ? '#fff' : 'rgba(255,255,255,0.3)'} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
          <p style={{ color:'rgba(255,255,255,0.2)', fontSize:11, textAlign:'center', marginTop:8 }}>
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        @keyframes bounce { from{transform:translateY(0)} to{transform:translateY(-5px)} }
        @keyframes livePulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
      `}</style>
    </div>
  )
}
