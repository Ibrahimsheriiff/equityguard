export default function SignalCard({ label, value }) {
    const isRed    = /high|elevated|negative|overbought|bearish/i.test(value)
    const isGreen  = /low|good|positive|bullish|unknown|past/i.test(value)
    const color    = isRed ? '#ff4d6a' : isGreen ? '#00d4aa' : '#f5a623'
  
    return (
      <div className="bg-surface border border-border rounded-xl p-4">
        <div className="text-muted text-xs uppercase tracking-widest mb-2">{label}</div>
        <div className="text-sm font-semibold leading-snug" style={{ color }}>
          {value || '—'}
        </div>
      </div>
    )
  }