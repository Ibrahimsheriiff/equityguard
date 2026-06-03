const BASE = '/api'

export async function fetchPrice(ticker) {
  try {
    const res = await fetch(`${BASE}/price/${ticker}`)
    if (!res.ok) return { price: 0, change: 0 }
    return res.json()
  } catch {
    return { price: 0, change: 0 }
  }
}

export async function analyseStock(ticker) {
  const res = await fetch(`${BASE}/analyse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Analysis failed')
  }
  return res.json()
}

export async function runEvaluation() {
  const res = await fetch(`${BASE}/evaluate`)
  if (!res.ok) throw new Error('Evaluation failed')
  return res.json()
}