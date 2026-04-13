import { Routes, Route, NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import CallPage from './pages/CallPage.jsx'
import LogsPage from './pages/LogsPage.jsx'
import ThemeToggle from './components/ThemeToggle.jsx'

export default function App() {
  const [dark, setDark] = useState(true)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  return (
    <div className={dark ? 'dark' : ''}>
      <div className="min-h-screen bg-navy-dark dark:bg-navy-dark transition-colors duration-300"
           style={{ background: dark ? '#0a0f1e' : '#f0f4f8' }}>
        {/* Top nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-3"
             style={{ background: dark ? 'rgba(10,15,30,0.85)' : 'rgba(240,244,248,0.85)',
                      backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(201,168,76,0.15)' }}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, #1e3a5f, #c9a84c)' }}>
              <span className="text-white text-xs font-bold">GU</span>
            </div>
            <span className={`font-semibold text-sm ${dark ? 'text-white' : 'text-navy'}`}>
              GIFT University
              <span className="text-gold ml-1 font-normal">AI Agent</span>
            </span>
          </div>

          <div className="flex items-center gap-4">
            <NavLink to="/"
              className={({ isActive }) =>
                `text-sm font-medium transition-colors px-3 py-1 rounded-full ${
                  isActive
                    ? 'bg-gold/20 text-gold'
                    : dark ? 'text-white/60 hover:text-white' : 'text-gray-500 hover:text-gray-900'
                }`
              }>
              Call
            </NavLink>
            <NavLink to="/logs"
              className={({ isActive }) =>
                `text-sm font-medium transition-colors px-3 py-1 rounded-full ${
                  isActive
                    ? 'bg-gold/20 text-gold'
                    : dark ? 'text-white/60 hover:text-white' : 'text-gray-500 hover:text-gray-900'
                }`
              }>
              Logs
            </NavLink>
            <ThemeToggle dark={dark} onToggle={() => setDark(d => !d)} />
          </div>
        </nav>

        {/* Page content */}
        <div className="pt-14">
          <Routes>
            <Route path="/" element={<CallPage dark={dark} />} />
            <Route path="/logs" element={<LogsPage dark={dark} />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}
