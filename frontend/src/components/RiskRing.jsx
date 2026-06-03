export default function RiskRing({ score }) {
    const color =
      score <= 3 ? '#00d4aa' :
      score >= 7 ? '#ff4d6a' : '#f5a623'
  
    const bg =
      score <= 3 ? '#061a14' :
      score >= 7 ? '#1a0610' : '#1a1206'
  
    const label =
      score <= 3 ? 'LOW RISK' :
      score >= 7 ? 'HIGH RISK' : 'MEDIUM RISK'
  
    return (
      <div className="flex flex-col items-center gap-3">
        <div
          className="w-28 h-28 rounded-full flex items-center justify-center text-3xl font-black"
          style={{ border: `6px solid ${color}`, background: bg, color }}
        >
          {score}/10
        </div>
        <span
          className="px-4 py-1 rounded-full text-xs font-bold tracking-widest border"
          style={{ color, borderColor: color, background: bg }}
        >
          {label}
        </span>
      </div>
    )
  }