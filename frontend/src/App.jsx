import { useState } from 'react'
import Home    from './pages/Home'
import Results from './pages/Results'

export default function App() {
  const [result, setResult] = useState(null)

  return result
    ? <Results data={result} onBack={() => setResult(null)} />
    : <Home    onResult={setResult} />
}