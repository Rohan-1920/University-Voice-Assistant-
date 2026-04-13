import { useState, useEffect, useRef, useCallback } from 'react'
import Avatar from '../components/Avatar.jsx'
import ChatBubble from '../components/ChatBubble.jsx'
import CallControls from '../components/CallControls.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import Waveform from '../components/Waveform.jsx'

const SILENCE_THRESHOLD = 25   // raised — ignore background noise
const SILENCE_DURATION  = 1500 // 1.5s silence before processing
const USER_ID = `user_${Math.random().toString(36).slice(2, 9)}`

function formatTime(s) {
  return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`
}
function nowTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function CallPage({ dark }) {
  const [callActive, setCallActive]   = useState(false)
  const [muted, setMuted]             = useState(false)
  const [status, setStatus]           = useState('idle')
  const [messages, setMessages]       = useState([])
  const [timer, setTimer]             = useState(0)

  const chatEndRef       = useRef(null)
  const timerRef         = useRef(null)
  const audioCtxRef      = useRef(null)
  const analyserRef      = useRef(null)
  const streamRef        = useRef(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef        = useRef([])
  const silenceTimerRef  = useRef(null)
  const vadLoopRef       = useRef(null)

  // State refs — so VAD callbacks always see latest value
  const isRecordingRef   = useRef(false)
  const isMutedRef       = useRef(false)
  const isBotSpeakingRef = useRef(false) // KEY: block VAD while bot speaks
  const callActiveRef    = useRef(false)

  useEffect(() => { isMutedRef.current = muted }, [muted])
  useEffect(() => { callActiveRef.current = callActive }, [callActive])
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Timer
  useEffect(() => {
    if (callActive) {
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000)
    } else {
      clearInterval(timerRef.current)
      setTimer(0)
    }
    return () => clearInterval(timerRef.current)
  }, [callActive])

  const addMessage = (role, text, intent = null) =>
    setMessages(prev => [...prev, { role, text, intent, time: nowTime(), id: Date.now() + Math.random() }])

  // ── Play audio and wait until done ──────────────────────────────
  const audioContextUnlocked = useRef(false)

  const unlockAudio = useCallback(async () => {
    if (audioContextUnlocked.current) return
    try {
      const ctx = new AudioContext()
      const buf = ctx.createBuffer(1, 1, 22050)
      const src = ctx.createBufferSource()
      src.buffer = buf
      src.connect(ctx.destination)
      src.start(0)
      await ctx.close()
      audioContextUnlocked.current = true
    } catch(e) {}
  }, [])

  const playAudio = useCallback((url) => {
    return new Promise((resolve) => {
      const audio = new Audio(url)
      audio.onended  = () => { URL.revokeObjectURL(url); resolve() }
      audio.onerror  = () => { URL.revokeObjectURL(url); resolve() }
      audio.play().catch((e) => {
        console.error('Audio play failed:', e)
        resolve()
      })
    })
  }, [])

  // ── TTS: Groq se try karo, fallback browser TTS ────────────────
  const speak = useCallback(async (text) => {
    if (isBotSpeakingRef.current) return
    isBotSpeakingRef.current = true
    setStatus('speaking')

    let spoken = false

    // Try Groq TTS first
    try {
      const res = await fetch('/demo/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      if (res.ok) {
        const blob = await res.blob()
        if (blob.size > 500) {
          await playAudio(URL.createObjectURL(blob))
          spoken = true
        }
      }
    } catch (e) {}

    // Fallback: browser TTS (always works, no rate limit)
    if (!spoken) {
      // Split long text into sentences for natural speech
      const sentences = text.match(/[^.!?]+[.!?]+/g) || [text]
      for (const sentence of sentences) {
        if (!callActiveRef.current && !isBotSpeakingRef.current) break
        await new Promise((resolve) => {
          window.speechSynthesis.cancel()
          const utter = new SpeechSynthesisUtterance(sentence.trim())
          utter.rate   = 0.92
          utter.pitch  = 1.05
          utter.volume = 1.0

          const voices = window.speechSynthesis.getVoices()
          const preferred = [
            'Google UK English Female',
            'Microsoft Aria Online (Natural) - English (United States)',
            'Microsoft Jenny Online (Natural) - English (United States)',
            'Google US English',
            'Microsoft Zira - English (United States)',
            'Samantha', 'Karen', 'Moira',
          ]
          let chosen = null
          for (const name of preferred) {
            chosen = voices.find(v => v.name === name)
            if (chosen) break
          }
          if (!chosen) chosen = voices.find(v => v.lang.startsWith('en') && v.name.toLowerCase().includes('female'))
          if (!chosen) chosen = voices.find(v => v.lang === 'en-US' || v.lang === 'en-GB')
          if (chosen) utter.voice = chosen
          utter.lang  = chosen?.lang || 'en-US'
          utter.onend   = resolve
          utter.onerror = resolve
          window.speechSynthesis.speak(utter)
        })
      }
    }

    isBotSpeakingRef.current = false
    if (callActiveRef.current) setStatus('listening')
  }, [playAudio])

  const isProcessingRef = useRef(false)

  // ── Send audio to backend ────────────────────────────────────────
  const sendAudio = useCallback(async (blob) => {
    if (blob.size < 1500) return
    if (isProcessingRef.current) return // prevent double processing
    isProcessingRef.current = true
    setStatus('thinking')

    try {
      const form = new FormData()
      form.append('audio', blob, 'recording.webm')
      form.append('user_id', USER_ID)

      const res  = await fetch('/demo/transcribe', { method: 'POST', body: form })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()

      if (!data.transcript?.trim()) {
        if (callActiveRef.current) setStatus('listening')
        return
      }

      addMessage('user', data.transcript)
      addMessage('bot',  data.response, data.intent)

      // Speak response — VAD is blocked during this
      await speak(data.response)

    } catch (err) {
      console.error('sendAudio error:', err)
      if (callActiveRef.current) setStatus('listening')
    }
    isProcessingRef.current = false
  }, [speak])

  // ── Recording ────────────────────────────────────────────────────
  const startRecording = useCallback(() => {
    if (isRecordingRef.current || !streamRef.current) return
    isRecordingRef.current = true
    chunksRef.current = []

    const mr = new MediaRecorder(streamRef.current, { mimeType: 'audio/webm' })
    mediaRecorderRef.current = mr
    mr.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data) }
    mr.onstop = () => {
      isRecordingRef.current = false
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
      sendAudio(blob)
    }
    mr.start(100)
  }, [sendAudio])

  const stopRecording = useCallback(() => {
    if (!isRecordingRef.current) return
    mediaRecorderRef.current?.stop()
  }, [])

  // ── VAD loop ─────────────────────────────────────────────────────
  const startVAD = useCallback(() => {
    if (!analyserRef.current) return
    const arr = new Uint8Array(analyserRef.current.frequencyBinCount)

    const tick = () => {
      if (!callActiveRef.current) return

      // CRITICAL: do nothing while bot is speaking
      if (isBotSpeakingRef.current) {
        vadLoopRef.current = requestAnimationFrame(tick)
        return
      }

      analyserRef.current.getByteFrequencyData(arr)
      const avg = arr.reduce((a, b) => a + b, 0) / arr.length
      const userSpeaking = avg > SILENCE_THRESHOLD && !isMutedRef.current

      if (userSpeaking) {
        clearTimeout(silenceTimerRef.current)
        silenceTimerRef.current = null
        if (!isRecordingRef.current) startRecording()
      } else if (isRecordingRef.current && !silenceTimerRef.current) {
        silenceTimerRef.current = setTimeout(() => {
          silenceTimerRef.current = null
          stopRecording()
        }, SILENCE_DURATION)
      }

      vadLoopRef.current = requestAnimationFrame(tick)
    }
    vadLoopRef.current = requestAnimationFrame(tick)
  }, [startRecording, stopRecording])

  // ── Start call ───────────────────────────────────────────────────
  const startCall = useCallback(async () => {
    try {
      // Unlock browser audio + preload voices on user gesture
      await unlockAudio()
      // Preload voices (Chrome needs this)
      if (window.speechSynthesis.getVoices().length === 0) {
        await new Promise(r => {
          window.speechSynthesis.onvoiceschanged = r
          setTimeout(r, 1000) // max 1s wait
        })
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const ctx      = new AudioContext()
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 256
      ctx.createMediaStreamSource(stream).connect(analyser)

      audioCtxRef.current  = ctx
      analyserRef.current  = analyser

      setMessages([])
      setCallActive(true)
      callActiveRef.current = true

      // Greet first — VAD starts AFTER greeting finishes
      const greeting = "Assalam o Alaikum! GIFT University. Kya madad kar sakta hoon?"
      addMessage('bot', greeting)
      await speak(greeting)

      // Now start listening
      setStatus('listening')
      startVAD()

    } catch (err) {
      alert('Microphone access required.')
    }
  }, [speak, startVAD, unlockAudio])

  // ── End call ─────────────────────────────────────────────────────
  const endCall = useCallback(() => {
    callActiveRef.current = false
    cancelAnimationFrame(vadLoopRef.current)
    clearTimeout(silenceTimerRef.current)
    window.speechSynthesis.cancel()
    mediaRecorderRef.current?.stop()
    streamRef.current?.getTracks().forEach(t => t.stop())
    audioCtxRef.current?.close()
    analyserRef.current      = null
    streamRef.current        = null
    isRecordingRef.current   = false
    isBotSpeakingRef.current = false
    isProcessingRef.current  = false
    setCallActive(false)
    setStatus('idle')
  }, [])

  const toggleMute = () => setMuted(m => !m)

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
         style={{ background: dark ? '#0a0f1e' : '#e8edf5' }}>

      <div className="w-full max-w-sm mx-auto phone-frame rounded-[3rem] overflow-hidden flex flex-col"
           style={{ minHeight: '780px', maxHeight: '90vh' }}>

        {/* Status bar */}
        <div className="flex items-center justify-between px-6 pt-4 pb-2">
          <span className="text-xs text-white/40">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          <div className="flex gap-1">
            {[0,1,2].map(i => <div key={i} className="w-1 h-1 rounded-full bg-white/40" />)}
          </div>
        </div>

        {/* Header */}
        <div className="px-6 pb-3 flex items-center justify-between">
          <div>
            <h1 className="text-white font-semibold text-base">GIFT University</h1>
            <p className="text-xs" style={{ color: '#c9a84c' }}>AI Voice Assistant</p>
          </div>
          <StatusBadge status={status} />
        </div>

        {/* Avatar */}
        <div className="flex flex-col items-center py-4 px-6">
          <Avatar speaking={status === 'speaking'} size={80} />
          {callActive && (
            <div className="mt-2 text-sm font-mono" style={{ color: 'rgba(255,255,255,0.5)' }}>
              {formatTime(timer)}
            </div>
          )}
          <div className="h-10 mt-2">
            <Waveform active={status === 'listening' && callActive} />
          </div>
        </div>

        {/* Chat */}
        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1" style={{ minHeight: 0 }}>
          {messages.length === 0 && !callActive && (
            <div className="flex flex-col items-center justify-center h-full gap-3 py-8">
              <div className="w-12 h-12 rounded-full flex items-center justify-center"
                   style={{ background: 'rgba(201,168,76,0.1)', border: '1px solid rgba(201,168,76,0.2)' }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#c9a84c" strokeWidth="1.5">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
              </div>
              <p className="text-center text-sm" style={{ color: 'rgba(255,255,255,0.4)' }}>
                Tap "Start Call" to speak with<br />your AI campus guide
              </p>
            </div>
          )}
          {messages.map(msg => <ChatBubble key={msg.id} message={msg} />)}
          <div ref={chatEndRef} />
        </div>

        {/* Controls */}
        <div className="px-6 py-6" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <CallControls
            callActive={callActive}
            muted={muted}
            onStart={startCall}
            onEnd={endCall}
            onMute={toggleMute}
          />
        </div>

        <div className="flex justify-center pb-3">
          <div className="w-24 h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.15)' }} />
        </div>
      </div>
    </div>
  )
}
