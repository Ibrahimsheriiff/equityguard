import { useState, useEffect } from 'react'
import StockCard from '../components/StockCard'
import { fetchPrice, analyseStock } from '../api/client'

const WATCHLIST = [
  { ticker: 'CBA.AX', name: 'Commonwealth Bank' },
  { ticker: 'BHP.AX', name: 'BHP Group' },
  { ticker: 'NAB.AX', name: 'National Aust. Bank' },
  { ticker: 'WBC.AX', name: 'Westpac Banking' },
  { ticker: 'ANZ.AX', name: 'ANZ Group' },
  { ticker: 'AAPL',   name: 'Apple Inc.' },
  { ticker: 'NVDA',   name: 'NVIDIA' },
  { ticker: 'TSLA',   name: 'Tesla' },
  { ticker: 'MSFT',   name: 'Microsoft' },
  { ticker: 'GOOGL',  name: 'Alphabet' },
]

export default function Home({ onResult }) {
  const [prices,       setPrices]       = useState({})
  const [selected,     setSelected]     = useState(null)
  const [search,       setSearch]       = useState('')
  const [loading,      setLoading]      = useState(false)
  const [error,        setError]        = useState(null)
  const [searchResult, setSearchResult] = useState(null)
  const [searching,    setSearching]    = useState(false)

  useEffect(() => {
    async function loadPrices() {
      const results = await Promise.all(
        WATCHLIST.map(s => fetchPrice(s.ticker).then(d => [s.ticker, d]))
      )
      setPrices(Object.fromEntries(results))
    }
    loadPrices()
    const interval = setInterval(loadPrices, 60000)
    return () => clearInterval(interval)
  }, [])

  async function handleSearch() {
    if (!search.trim()) return
    setSearching(true)
    setSearchResult(null)
    const ticker = search.trim().toUpperCase()
    const data   = await fetchPrice(ticker)
    setSearchResult({ ticker, ...data })
    setSearching(false)
  }

  async function handleAssess() {
    if (!selected) return
    setLoading(true)
    setError(null)
    try {
      const result = await analyseStock(selected)
      onResult(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">

      {/* Hero */}
      <div className="text-center mb-10">
        <h1 className="text-5xl font-black bg-gradient-to-r from-teal to-blue bg-clip-text text-transparent mb-3">
          🛡️ EquityGuard
        </h1>
        <p className="text-muted text-sm tracking-widest uppercase">
          AI Risk Assessment · Custom ReAct Agent · Live Market Data
        </p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="text-muted text-xs uppercase tracking-widest mb-2">Search any stock</div>
        <div className="max-w-md mx-auto flex gap-2">
          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); setSearchResult(null) }}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Type any ticker e.g. WES.AX, AMZN, META..."
            className="flex-1 bg-surface border border-border rounded-xl px-4 py-3
                       text-text placeholder-muted text-sm outline-none
                       focus:border-teal focus:ring-1 focus:ring-teal/20 transition"
          />
          <button
            onClick={handleSearch}
            disabled={searching}
            className="px-4 py-3 bg-surface border border-border rounded-xl
                       text-teal hover:border-teal transition text-sm font-bold"
          >
            {searching ? '...' : 'Search'}
          </button>
        </div>

        {searchResult?.price > 0 && (
          <div className="flex justify-center mt-3">
            <div
              onClick={() => setSelected(searchResult.ticker)}
              className={`bg-surface border rounded-xl px-6 py-3 cursor-pointer flex items-center gap-6 transition
                ${selected === searchResult.ticker ? 'border-teal bg-[#0a1e1a]' : 'border-border hover:border-teal/40'}`}
            >
              <div>
                <div className="text-text font-bold">{searchResult.ticker}</div>
                <div className="text-lg font-black text-text">${searchResult.price}</div>
              </div>
              <div className={`font-bold ${searchResult.change >= 0 ? 'text-teal' : 'text-red'}`}>
                {searchResult.change >= 0 ? '+' : ''}{searchResult.change}%
              </div>
            </div>
          </div>
        )}

        {searchResult?.price === 0 && (
          <p className="text-center text-red text-sm mt-2">
            Could not find `{searchResult.ticker}`. Check the ticker symbol.
          </p>
        )}
      </div>

      {/* Watchlist */}
      <div className="text-muted text-xs uppercase tracking-widest mb-3">
        Watchlist — ASX & US Markets
      </div>
      <div className="grid grid-cols-5 gap-3 mb-8">
        {WATCHLIST.map(s => (
          <StockCard
            key={s.ticker}
            ticker={s.ticker}
            name={s.name}
            price={prices[s.ticker]?.price ?? '—'}
            change={prices[s.ticker]?.change ?? 0}
            selected={selected === s.ticker}
            onSelect={() => setSelected(s.ticker)}
          />
        ))}
      </div>

      {/* Run button */}
      {selected && (
        <div className="flex flex-col items-center gap-3">
          <p className="text-muted text-sm">
            Ready to assess <span className="text-teal font-bold">{selected}</span>
          </p>
          <button
            onClick={handleAssess}
            disabled={loading}
            className="px-10 py-3.5 rounded-xl font-black text-bg text-base tracking-wide
                       bg-gradient-to-r from-teal to-blue
                       shadow-[0_4px_24px_rgba(0,212,170,0.25)]
                       hover:shadow-[0_6px_32px_rgba(0,212,170,0.4)]
                       hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '🔍  Agent investigating...' : `🔍  Run Agent — Assess ${selected}`}
          </button>
          {error && <p className="text-red text-sm">{error}</p>}
        </div>
      )}

      {!selected && (
        <p className="text-center text-muted text-sm mt-4">
          Select a stock above or search any ticker to begin
        </p>
      )}
    </div>
  )
}