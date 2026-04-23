import { Routes, Route, NavLink } from 'react-router-dom'
import { useState } from 'react'
import HomePage      from './pages/HomePage.jsx'
import CallPage      from './pages/CallPage.jsx'
import LogsPage      from './pages/LogsPage.jsx'
import ChatPage      from './pages/ChatPage.jsx'

// ── SVG Icons ────────────────────────────────────────────────────
const HomeIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
)

const MicIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="23"/>
    <line x1="8" y1="23" x2="16" y2="23"/>
  </svg>
)

const ChatIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
)

const ChartIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"/>
    <line x1="12" y1="20" x2="12" y2="4"/>
    <line x1="6"  y1="20" x2="6"  y2="14"/>
    <line x1="2"  y1="20" x2="22" y2="20"/>
  </svg>
)

const SunIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1"  x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22"   x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1"  y1="12" x2="3"  y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78"  x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64"  x2="19.78" y2="4.22"/>
  </svg>
)

const MoonIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
)

const NAV_LINKS = [
  { to: '/',           label: 'Home',       icon: <HomeIcon />,  end: true  },
  { to: '/call',       label: 'Call',       icon: <MicIcon />,   end: false },
  { to: '/chat',       label: 'Chat',       icon: <ChatIcon />,  end: false },
  { to: '/statistics', label: 'Statistics', icon: <ChartIcon />, end: false },
]

export default function App() {
  const [dark, setDark] = useState(true)

  return (
    <div style={{ background: dark ? '#080612' : '#f4f4f8', minHeight: '100vh' }}>

      {/* ── Navbar ── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 32px', height: 64,
        background: dark ? 'rgba(8,6,18,0.88)' : 'rgba(244,244,248,0.9)',
        backdropFilter: 'blur(24px)',
        borderBottom: `1px solid ${dark ? 'rgba(124,58,237,0.18)' : 'rgba(124,58,237,0.12)'}`,
      }}>

        {/* ── Logo ── */}
        <NavLink to="/" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none', flexShrink: 0 }}>
          <img
            src="/gift-logo.png"
            alt="GIFT University"
            style={{ width: 44, height: 44, objectFit: 'contain', display: 'block' }}
          />
          <div style={{ lineHeight: 1 }}>
            <div style={{
              color: dark ? '#fff' : '#1a1a2e',
              fontWeight: 800, fontSize: 16,
              letterSpacing: '-0.3px',
            }}>
              GIFT University
            </div>
            <div style={{
              color: '#a78bfa',
              fontSize: 11, fontWeight: 600,
              letterSpacing: '0.07em',
              marginTop: 3,
            }}>
              HELPDESK ASSISTANT
            </div>
          </div>
        </NavLink>

        {/* ── Nav links ── */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {NAV_LINKS.map(({ to, label, icon, end }) => (
            <NavLink key={to} to={to} end={end} style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 7,
              padding: '8px 18px', borderRadius: 99,
              fontSize: 14, fontWeight: 600,
              textDecoration: 'none', transition: 'all 0.2s',
              background: isActive
                ? dark ? 'rgba(124,58,237,0.2)' : 'rgba(124,58,237,0.12)'
                : 'transparent',
              color: isActive
                ? '#a78bfa'
                : dark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)',
              border: isActive
                ? '1px solid rgba(124,58,237,0.35)'
                : '1px solid transparent',
            })}>
              {icon}
              <span style={{ display: 'inline' }}>{label}</span>
            </NavLink>
          ))}
        </div>

        {/* ── Theme toggle ── */}
        <button
          onClick={() => setDark(d => !d)}
          title={dark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          style={{
            width: 42, height: 42, borderRadius: 12,
            border: `1px solid ${dark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
            background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)',
            cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: dark ? '#fbbf24' : '#6d28d9',
            transition: 'all 0.2s', flexShrink: 0,
          }}
          onMouseEnter={e => e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)'}
          onMouseLeave={e => e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'}
        >
          {dark ? <SunIcon /> : <MoonIcon />}
        </button>
      </nav>

      {/* ── Pages ── */}
      <div style={{ paddingTop: 64 }}>
        <Routes>
          <Route path="/"           element={<HomePage   dark={dark} />} />
          <Route path="/call"       element={<CallPage   dark={dark} />} />
          <Route path="/chat"       element={<ChatPage   dark={dark} />} />
          <Route path="/statistics" element={<LogsPage   dark={dark} />} />
        </Routes>
      </div>

      <style>{`
        @media (max-width: 520px) {
          nav span { display: none !important; }
        }
      `}</style>
    </div>
  )
}
