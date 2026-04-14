
import { useNavigate } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import {
  MicIcon, BookIcon, ZapIcon, GlobeIcon, CpuIcon, BarChartIcon,
  MonitorIcon, PhoneCallIcon, MessageIcon, LightbulbIcon, SettingsIcon,
  GraduationIcon, DollarIcon, AwardIcon, HomeIcon2, TruckIcon,
  UsersIcon, CalendarIcon, FileIcon, FlaskIcon, StarIcon, MapPinIcon,
} from '../components/Icons.jsx'

// Icon box helper
const IconBox = ({ icon, color, size = 54 }) => (
  <div style={{
    width: size, height: size, borderRadius: size * 0.3,
    background: `${color}15`, border: `1px solid ${color}28`,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0,
  }}>
    {icon}
  </div>
)

export default function HomePage({ dark }) {
  const navigate = useNavigate()
  const heroRef  = useRef(null)

  // Parallax on scroll
  useEffect(() => {
    const onScroll = () => {
      if (heroRef.current) {
        heroRef.current.style.transform = `translateY(${window.scrollY * 0.3}px)`
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div style={{ minHeight: '100vh', background: '#080612', color: '#fff', fontFamily: "'Inter', sans-serif", overflowX: 'hidden' }}>

      {/* ── Background layers ── */}
      <div ref={heroRef} style={{
        position: 'fixed', inset: 0, zIndex: 0,
        backgroundImage: 'url(/gift-campus.jpg)',
        backgroundSize: 'cover', backgroundPosition: 'center 30%',
        willChange: 'transform',
      }} />
      {/* Gradient overlay */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 1,
        background: 'linear-gradient(to bottom, rgba(8,6,18,0.7) 0%, rgba(8,6,18,0.85) 40%, rgba(8,6,18,0.97) 80%, #080612 100%)',
      }} />
      {/* Purple glow top-left */}
      <div style={{
        position: 'fixed', top: -200, left: -200, width: 600, height: 600,
        borderRadius: '50%', zIndex: 1,
        background: 'radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      {/* Gold glow bottom-right */}
      <div style={{
        position: 'fixed', bottom: -100, right: -100, width: 500, height: 500,
        borderRadius: '50%', zIndex: 1,
        background: 'radial-gradient(circle, rgba(201,168,76,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* ── Content ── */}
      <div style={{ position: 'relative', zIndex: 2 }}>

        {/* ══ HERO ══ */}
        <section style={{ minHeight: '92vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '100px 24px 60px', textAlign: 'center' }}>

          {/* Live pill */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 32,
            padding: '8px 20px', borderRadius: 99,
            background: 'rgba(124,58,237,0.1)',
            border: '1px solid rgba(124,58,237,0.35)',
            backdropFilter: 'blur(12px)',
          }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 10px #10b981', display: 'inline-block', animation: 'livePulse 2s infinite' }} />
            <span style={{ color: '#a78bfa', fontSize: 12, fontWeight: 700, letterSpacing: '0.08em' }}>AI HELPDESK · LIVE 24/7</span>
          </div>

          {/* Heading */}
          <h1 style={{ fontSize: 'clamp(38px,7vw,72px)', fontWeight: 900, lineHeight: 1.08, marginBottom: 24, letterSpacing: '-2px', maxWidth: 800 }}>
            Your GIFT University<br />
            <span style={{
              background: 'linear-gradient(135deg, #a78bfa 0%, #7c3aed 40%, #c9a84c 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              display: 'inline-block',
              fontFamily: "'Playfair Display', Georgia, serif",
              fontStyle: 'italic',
              fontWeight: 700,
              letterSpacing: '0px',
            }}>
              AI Campus Guide
            </span>
          </h1>

          <p style={{ fontSize: 'clamp(15px,2vw,19px)', color: 'rgba(255,255,255,0.55)', lineHeight: 1.8, maxWidth: 560, marginBottom: 48, fontWeight: 400, letterSpacing: '0.01em' }}>
            Ask about admissions, programs, fees, scholarships — anything.<br />
            Speak in{' '}
            <span style={{ color: '#a78bfa', fontWeight: 600, fontFamily:"'Playfair Display', Georgia, serif", fontStyle:'italic' }}>Urdu or English</span>
            , get answers in seconds.
          </p>

          {/* CTA */}
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', justifyContent: 'center' }}>
            <button onClick={() => navigate('/call')} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '16px 40px', borderRadius: 99, border: 'none', cursor: 'pointer',
              background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
              color: '#fff', fontWeight: 700, fontSize: 17,
              boxShadow: '0 0 40px rgba(124,58,237,0.5), 0 8px 32px rgba(0,0,0,0.3)',
              transition: 'all 0.3s',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform='translateY(-3px)'; e.currentTarget.style.boxShadow='0 0 60px rgba(124,58,237,0.7), 0 12px 40px rgba(0,0,0,0.4)' }}
            onMouseLeave={e => { e.currentTarget.style.transform='none'; e.currentTarget.style.boxShadow='0 0 40px rgba(124,58,237,0.5), 0 8px 32px rgba(0,0,0,0.3)' }}>
              <MicIcon size={20} color="#fff" /> Start Conversation
            </button>

            <button onClick={() => { const el = document.getElementById('about'); el?.scrollIntoView({ behavior: 'smooth' }) }} style={{
              padding: '16px 36px', borderRadius: 99, cursor: 'pointer',
              background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(12px)',
              color: 'rgba(255,255,255,0.8)', fontWeight: 600, fontSize: 16,
              border: '1px solid rgba(255,255,255,0.15)', transition: 'all 0.3s',
            }}
            onMouseEnter={e => e.currentTarget.style.background='rgba(255,255,255,0.1)'}
            onMouseLeave={e => e.currentTarget.style.background='rgba(255,255,255,0.06)'}>
              Learn More ↓
            </button>
          </div>

          {/* Scroll indicator */}
          <div style={{ marginTop: 64, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, opacity: 0.4 }}>
            <div style={{ width: 1, height: 48, background: 'linear-gradient(to bottom, transparent, rgba(255,255,255,0.5))', animation: 'scrollLine 2s ease-in-out infinite' }} />
          </div>
        </section>

        {/* ══ STATS BAR ══ */}
        <section style={{ padding: '0 24px 80px' }}>
          <div style={{
            maxWidth: 900, margin: '0 auto',
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: 2,
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 20, overflow: 'hidden',
            backdropFilter: 'blur(20px)',
          }}>
            {[
              { n: '24/7',  l: 'Always Available',  c: '#10b981' },
              { n: '<2s',   l: 'Response Time',      c: '#a78bfa' },
              { n: '50+',   l: 'Topics Covered',     c: '#60a5fa' },
              { n: '100%',  l: 'Bilingual Support',  c: '#c9a84c' },
            ].map((s, i) => (
              <div key={s.l} style={{
                padding: '28px 20px', textAlign: 'center',
                borderRight: i < 3 ? '1px solid rgba(255,255,255,0.06)' : 'none',
              }}>
                <div style={{ fontSize: 34, fontWeight: 900, color: s.c, lineHeight: 1, marginBottom: 6 }}>{s.n}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.45)', fontWeight: 500, letterSpacing: '0.03em' }}>{s.l}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ══ FEATURES ══ */}
        <section id="about" style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <p style={{ color: '#a78bfa', fontSize: 13, fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>CAPABILITIES</p>
            <h2 style={{ fontSize: 'clamp(28px,4vw,42px)', fontWeight: 900, letterSpacing: '-1px', lineHeight: 1.2 }}>
              Built for students.<br />Powered by AI.
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: 16 }}>
            {[
              { icon: <MicIcon size={24} color="#a78bfa"/>,    t:'Voice First',       d:'Speak naturally — no typing. The AI listens and responds in real-time.',                         c:'#7c3aed' },
              { icon: <BookIcon size={24} color="#60a5fa"/>,   t:'Complete Knowledge', d:'Programs, fees, admissions, scholarships, hostel, faculty — all GIFT data in one place.',       c:'#2563eb' },
              { icon: <ZapIcon size={24} color="#34d399"/>,    t:'Instant Answers',    d:'No queues, no waiting. Get accurate answers in under 2 seconds, any time of day.',              c:'#059669' },
              { icon: <GlobeIcon size={24} color="#fbbf24"/>,  t:'Urdu & English',     d:'Fully bilingual — switch languages mid-conversation. The AI understands both perfectly.',       c:'#d97706' },
              { icon: <CpuIcon size={24} color="#f87171"/>,    t:'Groq AI + RAG',      d:'Powered by LLaMA 4 with Retrieval Augmented Generation — answers grounded in real GIFT data.', c:'#dc2626' },
              { icon: <BarChartIcon size={24} color="#a78bfa"/>,t:'Full Analytics',    d:'Every conversation logged with intent, timestamp, and transcript for admin review.',            c:'#7c3aed' },
            ].map(f => (
              <div key={f.t} style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 20, padding: '30px 26px',
                backdropFilter: 'blur(16px)',
                transition: 'all 0.3s', cursor: 'default',
              }}
              onMouseEnter={e => { e.currentTarget.style.background=`${f.c}12`; e.currentTarget.style.border=`1px solid ${f.c}40`; e.currentTarget.style.transform='translateY(-5px)' }}
              onMouseLeave={e => { e.currentTarget.style.background='rgba(255,255,255,0.04)'; e.currentTarget.style.border='1px solid rgba(255,255,255,0.07)'; e.currentTarget.style.transform='none' }}>
                <IconBox icon={f.icon} color={f.c} />
                <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 10, color: '#fff', marginTop: 20 }}>{f.t}</div>
                <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.75 }}>{f.d}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ══ WHAT YOU CAN ASK ══ */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 28, padding: '48px 40px',
            backdropFilter: 'blur(20px)',
          }}>
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <p style={{ color: '#c9a84c', fontSize: 13, fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>KNOWLEDGE BASE</p>
              <h2 style={{ fontSize: 32, fontWeight: 900, letterSpacing: '-0.5px' }}>What can you ask?</h2>
              <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 15, marginTop: 10 }}>The AI has complete knowledge of GIFT University</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10 }}>
              {[
                [<GraduationIcon size={18} color="#a78bfa"/>, 'Admissions Process'],
                [<BookIcon size={18} color="#60a5fa"/>,       'Programs & Degrees'],
                [<DollarIcon size={18} color="#34d399"/>,     'Fee Structure'],
                [<AwardIcon size={18} color="#fbbf24"/>,      'Scholarships (GAP)'],
                [<HomeIcon2 size={18} color="#f87171"/>,      'Hostel & Rooms'],
                [<TruckIcon size={18} color="#a78bfa"/>,      'Transport Routes'],
                [<UsersIcon size={18} color="#60a5fa"/>,      'Faculty Info'],
                [<CalendarIcon size={18} color="#34d399"/>,   'Admission Dates'],
                [<FileIcon size={18} color="#fbbf24"/>,       'Required Documents'],
                [<FlaskIcon size={18} color="#f87171"/>,      'Labs & Research'],
                [<StarIcon size={18} color="#a78bfa"/>,       'Campus Events'],
                [<MapPinIcon size={18} color="#60a5fa"/>,     'Contact & Location'],
              ].map(([icon, label]) => (
                <div key={label} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '13px 16px', borderRadius: 12,
                  background: 'rgba(124,58,237,0.07)',
                  border: '1px solid rgba(124,58,237,0.15)',
                  transition: 'all 0.2s', cursor: 'default',
                }}
                onMouseEnter={e => { e.currentTarget.style.background='rgba(124,58,237,0.18)'; e.currentTarget.style.border='1px solid rgba(124,58,237,0.4)' }}
                onMouseLeave={e => { e.currentTarget.style.background='rgba(124,58,237,0.07)'; e.currentTarget.style.border='1px solid rgba(124,58,237,0.15)' }}>
                  {icon}
                  <span style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.85)' }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ HOW IT WORKS ══ */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <p style={{ color: '#a78bfa', fontSize: 13, fontWeight: 700, letterSpacing: '0.1em', marginBottom: 12 }}>SIMPLE PROCESS</p>
            <h2 style={{ fontSize: 'clamp(28px,4vw,40px)', fontWeight: 900, letterSpacing: '-1px' }}>How it works</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 0, position: 'relative' }}>
            {[
              { n:'01', icon:<MonitorIcon size={26} color="#a78bfa"/>,    t:'Open the App',       d:'Visit on any device — mobile, tablet, or desktop.' },
              { n:'02', icon:<MicIcon size={26} color="#60a5fa"/>,        t:'Tap Start Call',     d:'Click the mic button and allow microphone access.' },
              { n:'03', icon:<MessageIcon size={26} color="#34d399"/>,    t:'Ask Your Question',  d:'Speak in Urdu or English — ask anything about GIFT.' },
              { n:'04', icon:<ZapIcon size={26} color="#fbbf24"/>,        t:'Get Your Answer',    d:'AI responds in under 2 seconds with accurate info.' },
            ].map((h, i) => (
              <div key={h.n} style={{
                padding: '36px 28px', textAlign: 'center', position: 'relative',
                borderRight: i < 3 ? '1px solid rgba(255,255,255,0.06)' : 'none',
              }}>
                <div style={{
                  width: 48, height: 48, borderRadius: '50%', margin: '0 auto 20px',
                  background: 'linear-gradient(135deg, rgba(124,58,237,0.3), rgba(124,58,237,0.1))',
                  border: '1px solid rgba(124,58,237,0.4)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 11, fontWeight: 900, color: '#a78bfa', letterSpacing: '0.05em',
                }}>{h.n}</div>
                <div style={{ display:'flex', justifyContent:'center', marginBottom: 14 }}>{h.icon}</div>
                <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10, color: '#fff' }}>{h.t}</div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', lineHeight: 1.7 }}>{h.d}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ══ ABOUT ══ */}
        <section style={{ maxWidth: 1000, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>

            <div style={{
              background: 'linear-gradient(135deg, rgba(124,58,237,0.1), rgba(109,40,217,0.06))',
              border: '1px solid rgba(124,58,237,0.2)', borderRadius: 24, padding: '40px 32px',
              backdropFilter: 'blur(16px)',
            }}>
              <IconBox icon={<LightbulbIcon size={24} color="#a78bfa"/>} color="#7c3aed" size={56} />
              <h3 style={{ fontSize: 22, fontWeight: 800, marginBottom: 16, letterSpacing: '-0.3px', marginTop: 20 }}>Why we built this</h3>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.55)', lineHeight: 1.85 }}>
                Thousands of students call GIFT University every year asking the same questions —
                admission dates, fee structure, required documents. Staff spends hours on repetitive queries.
              </p>
              <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.55)', lineHeight: 1.85, marginTop: 14 }}>
                We built this AI assistant to handle those queries instantly, 24/7, in both Urdu and English —
                so students get answers immediately and staff can focus on what matters.
              </p>
            </div>

            <div style={{
              background: 'linear-gradient(135deg, rgba(201,168,76,0.08), rgba(201,168,76,0.04))',
              border: '1px solid rgba(201,168,76,0.18)', borderRadius: 24, padding: '40px 32px',
              backdropFilter: 'blur(16px)',
            }}>
              <IconBox icon={<SettingsIcon size={24} color="#c9a84c"/>} color="#c9a84c" size={56} />
              <h3 style={{ fontSize: 22, fontWeight: 800, marginBottom: 20, letterSpacing: '-0.3px', marginTop: 20 }}>Tech stack</h3>
              {[
                ['Voice Input',    'Groq Whisper STT'],
                ['AI Model',       'LLaMA 4 Scout'],
                ['Knowledge',      'RAG + pgvector'],
                ['Voice Output',   'Orpheus TTS'],
                ['Database',       'Supabase PostgreSQL'],
                ['Frontend',       'React + Vite'],
              ].map(([k, v]) => (
                <div key={k} style={{
                  display: 'flex', justifyContent: 'space-between',
                  padding: '11px 0', borderBottom: '1px solid rgba(255,255,255,0.06)',
                }}>
                  <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', fontWeight: 500 }}>{k}</span>
                  <span style={{ fontSize: 13, color: '#c9a84c', fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══ FINAL CTA ══ */}
        <section style={{ maxWidth: 700, margin: '0 auto', padding: '0 24px 100px', textAlign: 'center' }}>
          <div style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 32, padding: '56px 40px',
            backdropFilter: 'blur(20px)',
            position: 'relative', overflow: 'hidden',
          }}>
            {/* Glow */}
            <div style={{
              position: 'absolute', top: -60, left: '50%', transform: 'translateX(-50%)',
              width: 300, height: 300, borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(124,58,237,0.2) 0%, transparent 70%)',
              pointerEvents: 'none',
            }} />

            <img src="/gift-logo.png" alt="GIFT" style={{ width: 64, height: 64, objectFit: 'contain', marginBottom: 24, position: 'relative' }} />
            <h3 style={{ fontSize: 32, fontWeight: 900, marginBottom: 14, letterSpacing: '-0.5px', position: 'relative' }}>
              Ready to get started?
            </h3>
            <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 16, marginBottom: 36, lineHeight: 1.75, position: 'relative' }}>
              No forms. No waiting. No queues.<br />Just tap and ask your AI campus guide.
            </p>
            <button onClick={() => navigate('/call')} style={{
              padding: '16px 48px', borderRadius: 99, border: 'none', cursor: 'pointer',
              background: 'linear-gradient(135deg, #7c3aed, #6d28d9)',
              color: '#fff', fontWeight: 700, fontSize: 17,
              boxShadow: '0 0 40px rgba(124,58,237,0.5)',
              transition: 'all 0.3s', position: 'relative',
              display: 'inline-flex', alignItems: 'center', gap: 10,
            }}
            onMouseEnter={e => { e.currentTarget.style.transform='translateY(-3px)'; e.currentTarget.style.boxShadow='0 0 60px rgba(124,58,237,0.7)' }}
            onMouseLeave={e => { e.currentTarget.style.transform='none'; e.currentTarget.style.boxShadow='0 0 40px rgba(124,58,237,0.5)' }}>
              <MicIcon size={20} color="#fff" /> Talk to AI Assistant
            </button>
            <p style={{ color: 'rgba(255,255,255,0.18)', fontSize: 12, marginTop: 20, position: 'relative' }}>
              GIFT University Gujranwala · 055-111-GIFT-00 · gift.edu.pk
            </p>
          </div>
        </section>

      </div>

      <style>{`
        @keyframes livePulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }
        @keyframes scrollLine { 0%{opacity:0;transform:scaleY(0) translateY(-100%)} 50%{opacity:1} 100%{opacity:0;transform:scaleY(1) translateY(0)} }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  )
}
