const ICONS = {
    get_price_data:           '📈',
    get_technical_signals:    '📊',
    get_news_sentiment:       '📰',
    get_earnings_risk:        '📅',
    retrieve_company_docs:    '📄',
    search_company_knowledge: '🔍',
  }
  
  export default function TraceStep({ step }) {
    const icon    = ICONS[step.tool_name] || '🔧'
    const display = step.tool_name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  
    return (
      <div className="flex gap-4 bg-surface border border-border rounded-xl p-4 mb-3">
        <div className="text-2xl flex-shrink-0 mt-0.5">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <span className="bg-border text-teal text-xs font-bold px-2 py-0.5 rounded-full">
              STEP {step.step_number}
            </span>
            <span className="text-text font-semibold text-sm">{display}</span>
            <span className="text-muted text-xs ml-auto">{step.timestamp}</span>
          </div>
          <div className="text-sm text-sub mb-1">
            <span className="text-muted">Thought: </span>{step.thought}
          </div>
          <div className="text-sm text-sub mb-1">
            <span className="text-muted">Input: </span>
            <code className="bg-border text-sub px-1.5 py-0.5 rounded text-xs">
              {JSON.stringify(step.tool_input)}
            </code>
          </div>
          <div className="text-sm text-teal">
            <span className="text-muted">Found: </span>{step.tool_output_summary}
          </div>
        </div>
      </div>
    )
  }