export default function Avatar({ speaking, size = 96 }) {
  return (
    <div style={{ position: 'relative', width: size * 2.2, height: size * 2.2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {/* Ripple rings */}
      {speaking && [0, 0.6, 1.2].map((delay, i) => (
        <div key={i} className="ripple-ring" style={{
          width: size + 16 + i * 20,
          height: size + 16 + i * 20,
          animationDelay: `${delay}s`,
        }} />
      ))}

      {/* Glow */}
      <div style={{
        position: 'absolute',
        width: size + 24, height: size + 24,
        borderRadius: '50%',
        background: speaking
          ? 'radial-gradient(circle, rgba(201,168,76,0.2) 0%, transparent 70%)'
          : 'radial-gradient(circle, rgba(30,58,95,0.3) 0%, transparent 70%)',
        transition: 'all 0.5s ease',
      }} />

      {/* Avatar */}
      <div style={{
        width: size, height: size,
        borderRadius: '50%',
        background: 'linear-gradient(145deg, #1a2744 0%, #0d1628 100%)',
        border: speaking ? '2px solid rgba(201,168,76,0.6)' : '2px solid rgba(201,168,76,0.2)',
        boxShadow: speaking
          ? '0 0 32px rgba(201,168,76,0.25), 0 8px 32px rgba(0,0,0,0.5)'
          : '0 8px 32px rgba(0,0,0,0.4)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        transition: 'all 0.4s ease',
        position: 'relative', zIndex: 2,
      }}>
        <svg width={size * 0.48} height={size * 0.48} viewBox="0 0 48 48" fill="none">
          <path d="M24 6L2 18l22 11 22-11L24 6z" fill="#c9a84c" opacity="0.95"/>
          <path d="M10 22v9c0 5 6.3 8 14 8s14-3 14-8v-9" fill="none" stroke="#c9a84c" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          <line x1="42" y1="18" x2="42" y2="31" stroke="#c9a84c" strokeWidth="2.2" strokeLinecap="round"/>
          <circle cx="42" cy="32.5" r="2.5" fill="#c9a84c"/>
        </svg>
      </div>
    </div>
  )
}
