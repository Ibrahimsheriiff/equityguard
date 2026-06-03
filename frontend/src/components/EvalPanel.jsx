import { useState } from 'react'
import { runEvaluation } from '../api/client'

export default function EvalPanel() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handleRun() {
    setLoading(true)
    setError(null)
    try {
      const data = await runEvaluation()
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const passed = results ? results.filter(r => r.status === 'PASS').length : 0

  return (
    <div className="mt-12 border-t border-border pt-8">
      <div className="text-muted text-xs uppercase tracking-widest mb-2">
        Evaluation Framework
      </div>
      <div className="bg-[#0a0f1a] border border-border rounded-xl p-4 mb-4 text-sub text-sm">
        Runs 6 automated test cases — tool selection, financial advice refusal,
        prompt injection resistance, and error handling on invalid tickers.
      </div>

      <div className="flex justify-center mb-6">
        <button
          onClick={handleRun}
          disabled={loading}
          className="px-8 py-3 rounded-xl font-bold text-bg text-sm tracking-wide
                     bg-gradient-to-r from-teal to-blue
                     shadow-[0_4px_24px_rgba(0,212,170,0.25)]
                     hover:shadow-[0_6px_32px_rgba(0,212,170,0.4)]
                     hover:-translate-y-0.5 transition-all disabled:opacity-50"
        >
          {loading ? 'Running...' : '▶  Run Agent Evaluation'}
        </button>
      </div>

      {error && (
        <div className="text-red text-sm text-center mb-4">{error}</div>
      )}

      {results && (
        <>
          <div className="text-center mb-4">
            <span className="text-teal text-2xl font-black">{passed}/{results.length}</span>
            <span className="text-muted text-sm"> test cases passed</span>
          </div>
          <div className="space-y-2">
            {results.map((r, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 p-3 rounded-xl border text-sm ${
                  r.status === 'PASS'
                    ? 'bg-[#061a14] border-teal/30 text-teal'
                    : 'bg-[#1a0610] border-red/30 text-red'
                }`}
              >
                <span className="text-base flex-shrink-0">
                  {r.status === 'PASS' ? '✅' : '❌'}
                </span>
                <div>
                  <div className="font-semibold">{r.name}</div>
                  <div className="text-xs opacity-80 mt-0.5">{r.reason}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}