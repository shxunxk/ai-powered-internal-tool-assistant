import { useState } from 'react'
import './App.css'

async function readResponse(response) {
  const body = await response.text()
  if (!body) {
    return {}
  }

  try {
    return JSON.parse(body)
  } catch {
    return { detail: body }
  }
}

function App() {
  const [query, setQuery] = useState('Where is the main request flow implemented?')
  const [repoUrl, setRepoUrl] = useState('https://github.com/psf/requests')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [indexedRepo, setIndexedRepo] = useState('')
  const [error, setError] = useState('')
  const [indexError, setIndexError] = useState('')

  const handleIndexSubmit = async (event) => {
    event.preventDefault()
    if (!repoUrl.trim()) {
      setIndexError('Please enter a public GitHub repository URL.')
      return
    }

    setIndexing(true)
    setIndexError('')
    setIndexedRepo('')
    setAnswer('')

    try {
      const response = await fetch('/api/repository/index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
      })
      const data = await readResponse(response)
      if (!response.ok) throw new Error(data.detail || 'Repository indexing failed.')
      setIndexedRepo(data.repo_url)
    } catch (err) {
      setIndexError(err.message)
    } finally {
      setIndexing(false)
    }
  }

  const handleQuestionSubmit = async (event) => {
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })
      const data = await readResponse(response)
      if (!response.ok) throw new Error(data.detail || 'Question failed.')
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
        <p className="eyebrow">Repository intelligence</p>
        <h1>Ask one codebase.</h1>

        <form onSubmit={handleIndexSubmit} className="repository-form">
          <div className="section-heading">
            <span className="section-mark">01</span>
            <div>
              <h2>Create the vector database</h2>
              <p>Enter a public GitHub URL to index its code and documentation.</p>
            </div>
          </div>
          <label htmlFor="repository-url">GitHub repository URL</label>
          <input id="repository-url" type="url" value={repoUrl} onChange={(event) => setRepoUrl(event.target.value)} placeholder="https://github.com/owner/repository" />
          <button type="submit" disabled={indexing}>
            {indexing ? 'Creating vector database...' : 'Create vector database'}
          </button>
          {indexError && <p className="error-message">{indexError}</p>}
          {indexedRepo && <p className="success-message">Indexed and ready: {indexedRepo}</p>}
        </form>

        <form onSubmit={handleQuestionSubmit} className="query-form">
          <div className="section-heading">
            <span className="section-mark">02</span>
            <div>
              <h2>Ask about the repository</h2>
              <p>{indexedRepo ? 'Your questions are grounded in the indexed repository.' : 'Create the vector database before asking questions.'}</p>
            </div>
          </div>
          <label htmlFor="user-query">Question</label>
          <textarea id="user-query" rows="5" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask about the indexed repository..." />
          <button type="submit" disabled={loading || !indexedRepo}>
            {loading ? 'Finding answer...' : 'Ask question'}
          </button>
        </form>
      </section>

      <section className="result-panel">
        <p className="result-label">Repository answer</p>
        {error ? <p className="error-message">{error}</p> : <pre>{answer || 'Your repository answer will appear here.'}</pre>}
      </section>
    </main>
  )
}

export default App
