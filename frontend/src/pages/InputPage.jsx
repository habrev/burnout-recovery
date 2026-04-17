import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

const DRAFT_KEY = 'reset_input_draft'

export default function InputPage() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  const [inputText, setInputText] = useState(() => localStorage.getItem(DRAFT_KEY) || '')
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(true)

  useEffect(() => {
    api.get('/api/results/')
      .then((res) => setHistory(res.data.slice(0, 5)))
      .catch(() => {})
      .finally(() => setHistoryLoading(false))
  }, [])

  function handleChange(e) {
    setInputText(e.target.value)
    localStorage.setItem(DRAFT_KEY, e.target.value)
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!inputText.trim()) return
    navigate('/processing', { state: { inputText: inputText.trim() } })
  }

  function handleResultClick(id) {
    navigate(`/results/${id}`)
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="page-shell">
      <div className="card">
        <header className="page-header">
          <div>
            <h1 className="brand-title">Burnout Recovery</h1>
            <p className="brand-sub">Realtime reset for high performers</p>
          </div>
          <div className="header-actions">
            {isAdmin && (
              <button className="btn-link" onClick={() => navigate('/admin4reset')}>
                Admin
              </button>
            )}
            <button className="btn-link" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="form">
          <label className="prompt-label" htmlFor="input-text">
            What's going on right now?
          </label>
          <textarea
            id="input-text"
            className="textarea"
            rows={5}
            placeholder="Describe what's happening — your workload, your state of mind, how your body feels, what's weighing on you..."
            value={inputText}
            onChange={handleChange}
          />
          <button
            type="submit"
            className="btn btn-primary btn-large"
            disabled={!inputText.trim()}
          >
            Get My RESET Plan
          </button>
        </form>

        {!historyLoading && history.length > 0 && (
          <section className="history-section">
            <h2 className="section-title">Recent sessions</h2>
            <ul className="history-list">
              {history.map((item) => (
                <li key={item.id} className="history-item" onClick={() => handleResultClick(item.id)}>
                  <div className="history-item-left">
                    <span className={`stress-badge stress-${getStressClass(item.ai_output?.stress_level_int)}`}>
                      {item.ai_output?.stress_level_int ?? '—'}/10
                    </span>
                    <span className="history-preview">
                      {item.input_text.slice(0, 60)}{item.input_text.length > 60 ? '…' : ''}
                    </span>
                  </div>
                  <span className="history-date">{formatDate(item.created_at)}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}

function getStressClass(level) {
  if (!level) return 'low'
  if (level > 7) return 'high'
  if (level >= 4) return 'mid'
  return 'low'
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
