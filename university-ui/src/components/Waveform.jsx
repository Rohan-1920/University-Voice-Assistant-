const HEIGHTS = [8, 16, 24, 32, 28, 20, 14, 22, 18, 10]

export default function Waveform({ active }) {
  if (!active) return <div style={{ height: 40 }} />
  return (
    <div className="fade-in" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 3, height: 40 }}>
      {HEIGHTS.map((h, i) => (
        <div key={i} className="wave-bar" style={{
          height: h,
          animationDelay: `${i * 0.07}s`,
          animationDuration: `${0.5 + (i % 3) * 0.15}s`,
        }} />
      ))}
    </div>
  )
}
