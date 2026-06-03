import RiskRing   from '../components/RiskRing'
import SignalCard  from '../components/SignalCard'
import TraceStep  from '../components/TraceStep'
import EvalPanel  from '../components/EvalPanel'

function extractSignal(pattern, text) {
  const m = text.match(new RegExp(pattern + '[:\\*⚠️✅🔴🟡]+\\s*(.+?)(?:\\n|$)', 'i'))
  return m ? m[1].trim().slice(0, 70) : '—'
}

export default function Results({ data, onBack }) {
  const { ticker, risk_score, explanation, trace } = data
  const now = new Date().toLocaleString('en-AU', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })

  const vol  = extractSignal('Volatility',  explanation)
  const tech = extractSignal('Technical',   explanation)
  const news = extractSignal('News',        explanation)
  const earn = extractSignal('Earnings',    explanation)

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      {/* Back */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-muted text-sm hover:text-teal transition mb-8"
      >
        ← Back to watchlist
      </button>

      {/* Score header */}
      <div className="bg-surface border border-border rounded-2xl p-6 flex items-center gap-8 mb-6">
        <RiskRing score={risk_score} />
        <div>
          <div className="text-text text-2xl font-black mb-2">{ticker}</div>
          <div className="text-muted text-sm">
            Live assessment · Custom ReAct agent · {now}
          </div>
          <div className="flex gap-2 mt-3">
            {data.tools_called?.map(t => (
              <span key={t} className="bg-border text-sub text-xs px-2 py-0.5 rounded-full">
                {t.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Signal summary */}
      <div className="text-muted text-xs uppercase tracking-widest mb-3">Signal Summary</div>
      <div className="grid grid-cols-4 gap-3 mb-8">
        <SignalCard label="Volatility" value={vol}  />
        <SignalCard label="Technical"  value={tech} />
        <SignalCard label="News"       value={news} />
        <SignalCard label="Earnings"   value={earn} />
      </div>

      {/* Agent trace */}
      {trace?.length > 0 && (
        <>
          <div className="text-muted text-xs uppercase tracking-widest mb-2">
            Agent Investigation Trace
          </div>
          <div className="bg-[#0a0f1a] border border-border rounded-xl p-4 mb-4 text-sub text-sm">
            Every decision the agent made — what it was thinking, which tool it chose,
            and what it found. The agent decided this path itself. It was not hardcoded.
          </div>
          {trace.map((step, i) => <TraceStep key={i} step={step} />)}
        </>
      )}

      {/* Full reasoning */}
      <div className="text-muted text-xs uppercase tracking-widest mb-3 mt-6">
        Agent Reasoning
      </div>
      <div className="bg-surface border border-border rounded-2xl p-6 text-sub text-sm leading-relaxed whitespace-pre-wrap">
        {explanation}
      </div>

      {/* Eval panel */}
      <EvalPanel />

      {/* Footer */}
      <div className="text-center mt-12 text-[#1e2d45] text-xs">
        EquityGuard · Claude API · yfinance · FastAPI · React · Custom ReAct Agent
      </div>
    </div>
  )
}