import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('Where is JWT validation implemented?')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!query.trim()) {
      setError('Please enter a question.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong while contacting the AI backend.')
      }

      setAnswer(data.answer || 'No answer returned.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">AI assistant</p>
        <h1>Internal Tool Assistant</h1>

        <form onSubmit={handleSubmit} className="query-form">
          <label htmlFor="user-query">Ask the system</label>
          <textarea
            id="user-query"
            rows="5"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask about policies, code, or incidents..."
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Generating answer...' : 'Send query'}
          </button>
        </form>
      </section>

      <section className="result-panel">
        <h2>Generated output</h2>
        {error ? <p className="error-message">{error}</p> : <pre>{answer || 'The response from the AI model will appear here.'}</pre>}
      </section>
    </main>
  )
}

export default App
