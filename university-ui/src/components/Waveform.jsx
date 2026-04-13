export default function Waveform({ active }) {
  if (!active) return null

  return (
    <div className="flex items-center justify-center gap-1 h-10 animate-fade-in">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="wave-bar" style={{ animationDelay: `${i * 0.08}s` }} />
      ))}
    </div>
  )
}
