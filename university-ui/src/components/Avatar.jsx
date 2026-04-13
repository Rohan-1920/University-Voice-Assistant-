export default function Avatar({ speaking, size = 96 }) {
  return (
    <div className="relative flex items-center justify-center" style={{ width: size * 2.5, height: size * 2.5 }}>
      {/* Ripple rings - only when speaking */}
      {speaking && (
        <>
          <div className="absolute rounded-full animate-ripple1"
               style={{
                 width: size + 20, height: size + 20,
                 background: 'rgba(201,168,76,0.15)',
                 border: '1px solid rgba(201,168,76,0.3)',
               }} />
          <div className="absolute rounded-full animate-ripple2"
               style={{
                 width: size + 20, height: size + 20,
                 background: 'rgba(201,168,76,0.1)',
                 border: '1px solid rgba(201,168,76,0.2)',
               }} />
          <div className="absolute rounded-full animate-ripple3"
               style={{
                 width: size + 20, height: size + 20,
                 background: 'rgba(201,168,76,0.05)',
                 border: '1px solid rgba(201,168,76,0.1)',
               }} />
        </>
      )}

      {/* Outer glow ring */}
      <div className="absolute rounded-full transition-all duration-500"
           style={{
             width: size + 12, height: size + 12,
             background: speaking
               ? 'linear-gradient(135deg, rgba(201,168,76,0.4), rgba(30,58,95,0.4))'
               : 'linear-gradient(135deg, rgba(30,58,95,0.4), rgba(201,168,76,0.1))',
             boxShadow: speaking ? '0 0 30px rgba(201,168,76,0.3)' : 'none',
           }} />

      {/* Avatar circle */}
      <div className="relative rounded-full flex items-center justify-center overflow-hidden"
           style={{
             width: size, height: size,
             background: 'linear-gradient(145deg, #1e3a5f 0%, #0a1628 60%, #c9a84c22 100%)',
             border: '2px solid rgba(201,168,76,0.4)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
           }}>
        {/* University crest / bot icon */}
        <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 48 48" fill="none">
          {/* Graduation cap */}
          <path d="M24 8L4 18l20 10 20-10L24 8z" fill="#c9a84c" opacity="0.9"/>
          <path d="M12 23v10c0 4 5.4 7 12 7s12-3 12-7V23" fill="none" stroke="#c9a84c" strokeWidth="2" strokeLinecap="round"/>
          <line x1="40" y1="18" x2="40" y2="30" stroke="#c9a84c" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="40" cy="31" r="2" fill="#c9a84c"/>
          {/* AI circuit dots */}
          <circle cx="24" cy="24" r="2" fill="white" opacity="0.6"/>
        </svg>
      </div>
    </div>
  )
}
