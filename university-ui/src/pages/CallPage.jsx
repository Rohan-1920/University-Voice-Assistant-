
import { useState, useEffect, useRef, useCallback } from 'react'

const SILENCE_THRESHOLD = 25
const SILENCE_DURATION  = 1500
const USER_ID = `user_${Math.random().toString(36).slice(2, 9)}`

function formatTime(s) {
  return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`
}
function nowTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ── Status config ────────────────────────────────────────────────
const STATUS = {
  idle:      { label: 'Ready',     color: '#9ca3af', bg: 'rgba(156,163,175,0.12)' },
  listening: { label: 'Listening', color: '#10b981', bg: 'rgba(16,185,129,0.12)'  },
  thinking:  { label: 'Thinking',  color: '#a78bfa', bg: 'rgba(167,139,250,0.12)' },
  speaking:  { label: 'Speaking',  color: '#60a5fa', bg: 'rgba(96,165,250,0.12)'  },
}

// ── Waveform bars ────────────────────────────────────────────────
function WaveBars({ active }) {
  if (!active) return null
  const heights = [6,14,22,30,26,18,12,20,16,8]
  return (
    <div style={{ display:'flex', alignItems:'center', gap:3, height:36 }}>
      {heights.map((h,i) => (
        <div key={i} style={{
          width:3, height:h, borderRadius:99,
          background:'linear-gradient(to top,#7c3aed,#a78bfa)',
          animation:`waveBounce ${0.5+(i%3)*0.15}s ease-in-out ${i*0.07}s infinite alternate`,
        }}/>
      ))}
    </div>
  )
}

// ── Chat bubble ──────────────────────────────────────────────────
function Bubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{ display:'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom:10 }}>
      <div style={{
        maxWidth:'80%', padding:'10px 14px',
        borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
        background: isUser ? 'linear-gradient(135deg,#7c3aed,#6d28d9)' : 'rgba(255,255,255,0.07)',
        border: isUser ? 'none' : '1px solid rgba(255,255,255,0.08)',
        color: isUser ? '#fff' : 'rgba(255,255,255,0.9)',
        fontSize:13.5, lineHeight:1.55,
        boxShadow: isUser ? '0 4px 16px rgba(124,58,237,0.3)' : 'none',
      }}>
        {msg.text}
        <div style={{ fontSize:10, color:'rgba(255,255,255,0.3)', marginTop:4, textAlign: isUser ? 'right' : 'left' }}>
          {msg.time}
        </div>
      </div>
    </div>
  )
}

export default function CallPage() {
  const [callActive, setCallActive] = useState(false)
  const [muted, setMuted]           = useState(false)
  const [status, setStatus]         = useState('idle')
  const [messages, setMessages]     = useState([])
  const [timer, setTimer]           = useState(0)

  const chatEndRef       = useRef(null)
  const timerRef         = useRef(null)
  const audioCtxRef      = useRef(null)
  const analyserRef      = useRef(null)
  const streamRef        = useRef(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef        = useRef([])
  const silenceTimerRef  = useRef(null)
  const vadLoopRef       = useRef(null)
  const isRecordingRef   = useRef(false)
  const isMutedRef       = useRef(false)
  const isBotSpeakingRef = useRef(false)
  const callActiveRef    = useRef(false)
  const isProcessingRef  = useRef(false)
  const audioUnlocked    = useRef(false)

  useEffect(() => { isMutedRef.current = muted }, [muted])
  useEffect(() => { callActiveRef.current = callActive }, [callActive])
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior:'smooth' }) }, [messages])

  useEffect(() => {
    if (callActive) { timerRef.current = setInterval(() => setTimer(t => t+1), 1000) }
    else { clearInterval(timerRef.current); setTimer(0) }
    return () => clearInterval(timerRef.current)
  }, [callActive])

  const addMsg = (role, text, intent=null) =>
    setMessages(p => [...p, { role, text, intent, time: nowTime(), id: Date.now()+Math.random() }])

  const unlockAudio = useCallback(async () => {
    if (audioUnlocked.current) return
    try {
      const c = new AudioContext()
      const b = c.createBuffer(1,1,22050), s = c.createBufferSource()
      s.buffer=b; s.connect(c.destination); s.start(0); await c.close()
      audioUnlocked.current = true
    } catch(e) {}
  }, [])

  const playAudio = useCallback((url) => new Promise(res => {
    const a = new Audio(url)
    a.onended = () => { URL.revokeObjectURL(url); res() }
    a.onerror = () => { URL.revokeObjectURL(url); res() }
    a.play().catch(res)
  }), [])

  const speak = useCallback(async (text) => {
    if (isBotSpeakingRef.current) return
    isBotSpeakingRef.current = true
    setStatus('speaking')
    let spoken = false
    try {
      const r = await fetch('/demo/speak', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text}) })
      if (r.ok) { const b = await r.blob(); if (b.size > 500 && callActiveRef.current) { await playAudio(URL.createObjectURL(b)); spoken = true } }
    } catch(e) {}
    if (!spoken && callActiveRef.current) {
      const sentences = text.match(/[^.!?]+[.!?]+/g) || [text]
      for (const s of sentences) {
        if (!callActiveRef.current) break  // stop if call ended
        await new Promise(res => {
          window.speechSynthesis.cancel()
          const u = new SpeechSynthesisUtterance(s.trim())
          u.rate=0.92; u.pitch=1.05; u.volume=1
          const voices = window.speechSynthesis.getVoices()
          const pref = ['Google UK English Female','Microsoft Aria Online (Natural) - English (United States)','Microsoft Jenny Online (Natural) - English (United States)','Google US English','Samantha']
          let v = null
          for (const n of pref) { v = voices.find(x => x.name===n); if(v) break }
          if (!v) v = voices.find(x => x.lang.startsWith('en'))
          if (v) u.voice=v; u.lang=v?.lang||'en-US'
          u.onend=res; u.onerror=res
          window.speechSynthesis.speak(u)
        })
      }
    }
    isBotSpeakingRef.current = false
    if (callActiveRef.current) setStatus('listening')
  }, [playAudio])

  const sendAudio = useCallback(async (blob) => {
    if (blob.size < 1500 || isProcessingRef.current) return
    isProcessingRef.current = true
    setStatus('thinking')
    try {
      const form = new FormData()
      form.append('audio', blob, 'audio.webm')
      form.append('user_id', USER_ID)
      const r = await fetch('/demo/transcribe', { method:'POST', body:form })
      if (!r.ok) throw new Error()
      const d = await r.json()
      if (!d.transcript?.trim()) { if(callActiveRef.current) setStatus('listening'); return }
      addMsg('user', d.transcript)
      addMsg('bot', d.response, d.intent)
      await speak(d.response)
    } catch(e) { if(callActiveRef.current) setStatus('listening') }
    isProcessingRef.current = false
  }, [speak])

  const startRecording = useCallback(() => {
    if (isRecordingRef.current || !streamRef.current) return
    isRecordingRef.current = true; chunksRef.current = []
    const mr = new MediaRecorder(streamRef.current, { mimeType:'audio/webm' })
    mediaRecorderRef.current = mr
    mr.ondataavailable = e => { if(e.data.size>0) chunksRef.current.push(e.data) }
    mr.onstop = () => { isRecordingRef.current=false; sendAudio(new Blob(chunksRef.current,{type:'audio/webm'})) }
    mr.start(100)
  }, [sendAudio])

  const stopRecording = useCallback(() => {
    if (!isRecordingRef.current) return
    mediaRecorderRef.current?.stop()
  }, [])

  const startVAD = useCallback(() => {
    if (!analyserRef.current) return
    const arr = new Uint8Array(analyserRef.current.frequencyBinCount)
    const tick = () => {
      if (!callActiveRef.current) return
      if (isBotSpeakingRef.current) { vadLoopRef.current=requestAnimationFrame(tick); return }
      analyserRef.current.getByteFrequencyData(arr)
      const avg = arr.reduce((a,b)=>a+b,0)/arr.length
      if (avg > SILENCE_THRESHOLD && !isMutedRef.current) {
        clearTimeout(silenceTimerRef.current); silenceTimerRef.current=null
        if (!isRecordingRef.current) startRecording()
      } else if (isRecordingRef.current && !silenceTimerRef.current) {
        silenceTimerRef.current = setTimeout(() => { silenceTimerRef.current=null; stopRecording() }, SILENCE_DURATION)
      }
      vadLoopRef.current = requestAnimationFrame(tick)
    }
    vadLoopRef.current = requestAnimationFrame(tick)
  }, [startRecording, stopRecording])

  const startCall = useCallback(async () => {
    try {
      await unlockAudio()
      if (window.speechSynthesis.getVoices().length===0) {
        await new Promise(r => { window.speechSynthesis.onvoiceschanged=r; setTimeout(r,1000) })
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio:true })
      streamRef.current = stream
      const ctx = new AudioContext(), analyser = ctx.createAnalyser()
      analyser.fftSize=256; ctx.createMediaStreamSource(stream).connect(analyser)
      audioCtxRef.current=ctx; analyserRef.current=analyser
      setMessages([]); setCallActive(true); callActiveRef.current=true
      const greeting = "Assalam o Alaikum! GIFT University. Kya madad kar sakta hoon?"
      addMsg('bot', greeting)
      await speak(greeting)
      setStatus('listening'); startVAD()
    } catch(e) { alert('Microphone access required.') }
  }, [speak, startVAD, unlockAudio])

  const endCall = useCallback(() => {
    callActiveRef.current=false
    cancelAnimationFrame(vadLoopRef.current); clearTimeout(silenceTimerRef.current)
    window.speechSynthesis.cancel()  // stop any speaking immediately
    mediaRecorderRef.current?.stop()
    streamRef.current?.getTracks().forEach(t=>t.stop())
    audioCtxRef.current?.close()
    analyserRef.current=null; streamRef.current=null
    isRecordingRef.current=false; isBotSpeakingRef.current=false; isProcessingRef.current=false
    setCallActive(false); setStatus('idle')
  }, [])


  const toggleMute = useCallback(() => {
    setMuted(m => {
      const next = !m
      if (streamRef.current) streamRef.current.getAudioTracks().forEach(t => { t.enabled = !next })
      return next
    })
  }, [])

  const sc = STATUS[status] || STATUS.idle

  return (
    <div style={{ minHeight:'100vh', background:'#080612', display:'flex', flexDirection:'column', alignItems:'center', padding:'0 20px 48px', position:'relative', overflow:'hidden' }}>

      {/* Background */}
      <div style={{ position:'fixed', inset:0, backgroundImage:'url(/gift-campus.jpg)', backgroundSize:'cover', backgroundPosition:'center top', opacity:0.35, zIndex:0 }} />
      {/* Deep gradient overlay — bottom heavy so content stays readable */}
      <div style={{ position:'fixed', inset:0, background:'linear-gradient(180deg, rgba(8,6,18,0.55) 0%, rgba(8,6,18,0.75) 50%, rgba(8,6,18,0.97) 85%, #080612 100%)', zIndex:1 }} />
      {/* Purple ambient glow top-left */}
      <div style={{ position:'fixed', top:-150, left:-150, width:500, height:500, borderRadius:'50%', background:'radial-gradient(circle,rgba(124,58,237,0.2) 0%,transparent 70%)', zIndex:1, pointerEvents:'none' }} />
      {/* Gold ambient glow bottom-right */}
      <div style={{ position:'fixed', bottom:-100, right:-100, width:400, height:400, borderRadius:'50%', background:'radial-gradient(circle,rgba(201,168,76,0.12) 0%,transparent 70%)', zIndex:1, pointerEvents:'none' }} />

      <div style={{ position:'relative', zIndex:2, width:'100%', maxWidth:500, display:'flex', flexDirection:'column', alignItems:'center' }}>

        {/* ── IDLE ── */}
        {!callActive && (
          <div style={{ width:'100%', textAlign:'center', paddingTop:56 }}>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:14, marginBottom:40 }}>
              <img src="/gift-logo.png" alt="GIFT" style={{ width:56, height:56, objectFit:'contain' }} />
              <div style={{ textAlign:'left' }}>
                <div style={{ color:'#fff', fontWeight:800, fontSize:20, letterSpacing:'-0.3px', lineHeight:1.2 }}>GIFT University</div>
                <div style={{ color:'#a78bfa', fontSize:12, fontWeight:600, letterSpacing:'0.06em', marginTop:3 }}>HELPDESK ASSISTANT</div>
              </div>
            </div>

            <h1 style={{ fontSize:'clamp(28px,6vw,42px)', fontWeight:900, lineHeight:1.15, letterSpacing:'-1px', marginBottom:18, color:'#fff' }}>
              Your intelligent<br />
              <span style={{
                background:'linear-gradient(135deg,#7c3aed,#a78bfa,#c9a84c)',
                WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent',
                fontFamily:"'Playfair Display', Georgia, serif",
                fontStyle:'italic',
                fontWeight:700,
                letterSpacing:'0.5px',
              }}>campus guide</span>
            </h1>

            <p style={{
              fontSize: 17,
              lineHeight: 1.85,
              marginBottom: 44,
              maxWidth: 400,
              margin: '0 auto 44px',
              fontFamily: "'Playfair Display', Georgia, serif",
              fontStyle: 'italic',
              fontWeight: 400,
              color: 'rgba(255,255,255,0.55)',
              letterSpacing: '0.02em',
            }}>
              Ask, speak, and discover — your university, your language, your answers.
            </p>

            <button onClick={startCall} style={{ display:'inline-flex', alignItems:'center', gap:10, padding:'16px 44px', borderRadius:99, border:'none', cursor:'pointer', background:'linear-gradient(135deg,#7c3aed,#6d28d9)', color:'#fff', fontWeight:700, fontSize:16, boxShadow:'0 0 40px rgba(124,58,237,0.5)', transition:'all 0.25s', letterSpacing:'0.01em' }}
              onMouseEnter={e=>{ e.currentTarget.style.transform='translateY(-3px)'; e.currentTarget.style.boxShadow='0 0 60px rgba(124,58,237,0.7)' }}
              onMouseLeave={e=>{ e.currentTarget.style.transform='none'; e.currentTarget.style.boxShadow='0 0 40px rgba(124,58,237,0.5)' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
              Start Conversation
            </button>
            <p style={{ color:'rgba(255,255,255,0.2)', fontSize:12, marginTop:14 }}>Microphone access required · Urdu &amp; English supported</p>
          </div>
        )}

        {/* ── ACTIVE CALL ── */}
        {callActive && (
          <div style={{ width:'100%', paddingTop:20 }}>

            {/* Header */}
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:24 }}>
              <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                <img src="/gift-logo.png" alt="GIFT" style={{ width:38, height:38, objectFit:'contain' }} />
                <div>
                  <div style={{ color:'#fff', fontWeight:700, fontSize:15, letterSpacing:'-0.2px' }}>GIFT University</div>
                  <div style={{ color:'rgba(255,255,255,0.38)', fontSize:11, fontWeight:500, marginTop:1 }}>
                    Helpdesk Assistant&nbsp;·&nbsp;<span style={{ fontFamily:'monospace', letterSpacing:'0.05em' }}>{formatTime(timer)}</span>
                  </div>
                </div>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 14px', borderRadius:99, background:sc.bg, color:sc.color, fontSize:12, fontWeight:700, border:`1px solid ${sc.color}30`, letterSpacing:'0.02em' }}>
                <span style={{ width:6, height:6, borderRadius:'50%', background:sc.color, boxShadow:`0 0 6px ${sc.color}`, animation:status!=='idle'?'pulse 1.5s infinite':'none' }}/>
                {sc.label}
              </div>
            </div>

            {/* Waveform / status */}
            <div style={{ display:'flex', justifyContent:'center', alignItems:'center', height:48, marginBottom:16 }}>
              {status==='listening' && <WaveBars active />}
              {status==='speaking' && (
                <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                  {[4,7,10,7,4].map((h,i) => (
                    <div key={i} style={{ width:3, height:h*2, borderRadius:99, background:'#60a5fa', animation:`waveBounce ${0.5+i*0.1}s ease-in-out ${i*0.08}s infinite alternate` }}/>
                  ))}
                  <span style={{ color:'rgba(255,255,255,0.4)', fontSize:12, marginLeft:8, fontWeight:500 }}>Speaking</span>
                </div>
              )}
              {status==='thinking' && (
                <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                  {[0,1,2].map(i=>(
                    <div key={i} style={{ width:8, height:8, borderRadius:'50%', background:'#a78bfa', animation:`bounce 0.7s ${i*0.15}s infinite alternate` }}/>
                  ))}
                  <span style={{ color:'rgba(255,255,255,0.4)', fontSize:12, marginLeft:6, fontWeight:500 }}>Processing</span>
                </div>
              )}
            </div>

            {/* Chat */}
            <div style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)', borderRadius:20, padding:'16px 14px', height:'min(360px,42vh)', overflowY:'auto', marginBottom:24 }}>
              {messages.length === 0 && (
                <div style={{ height:'100%', display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <p style={{ color:'rgba(255,255,255,0.2)', fontSize:13, textAlign:'center', lineHeight:1.7 }}>Conversation will appear here.<br/>Start speaking to begin.</p>
                </div>
              )}
              {messages.map(msg => <Bubble key={msg.id} msg={msg} />)}
              <div ref={chatEndRef}/>
            </div>

            {/* Controls */}
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:18 }}>
              <button onClick={toggleMute} style={{ width:52, height:52, borderRadius:'50%', border:`1px solid ${muted?'rgba(239,68,68,0.35)':'rgba(255,255,255,0.1)'}`, cursor:'pointer', background:muted?'rgba(239,68,68,0.15)':'rgba(255,255,255,0.07)', display:'flex', alignItems:'center', justifyContent:'center', transition:'all 0.2s' }}>
                {muted
                  ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round"><line x1="1" y1="1" x2="23" y2="23"/><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/><path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                  : <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="2" strokeLinecap="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                }
              </button>

              <button onClick={endCall} style={{ width:64, height:64, borderRadius:'50%', border:'none', cursor:'pointer', background:'linear-gradient(135deg,#ef4444,#dc2626)', boxShadow:'0 8px 28px rgba(239,68,68,0.4)', display:'flex', alignItems:'center', justifyContent:'center', transition:'all 0.2s' }}
                onMouseEnter={e=>e.currentTarget.style.transform='scale(1.08)'}
                onMouseLeave={e=>e.currentTarget.style.transform='none'}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-3.45-3.45"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>

              <button style={{ width:52, height:52, borderRadius:'50%', border:'1px solid rgba(255,255,255,0.1)', cursor:'pointer', background:'rgba(255,255,255,0.07)', display:'flex', alignItems:'center', justifyContent:'center' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="2" strokeLinecap="round">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
                </svg>
              </button>
            </div>
          </div>
        )}

      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
        @keyframes bounce { from{transform:translateY(0)} to{transform:translateY(-7px)} }
        @keyframes waveBounce { from{transform:scaleY(0.25)} to{transform:scaleY(1)} }
      `}</style>
    </div>
  )
}
