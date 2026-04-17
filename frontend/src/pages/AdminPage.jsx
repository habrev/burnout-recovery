import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

export default function AdminPage() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const [tab, setTab] = useState('sessions')
  const [users, setUsers] = useState([])
  const [sessions, setSessions] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    fetchData()
  }, [tab])

  async function fetchData() {
    setLoading(true)
    setError('')
    try {
      if (tab === 'sessions') {
        const res = await api.get('/api/admin4reset/results/')
        setSessions(res.data)
      } else {
        const res = await api.get('/api/admin4reset/users/')
        setUsers(res.data)
      }
    } catch {
      setError('Failed to load data.')
    } finally {
      setLoading(false)
    }
  }

  async function handleSearch(e) {
    e.preventDefault()
    setLoading(true)
    try {
      if (tab === 'sessions') {
        const res = await api.get('/api/admin4reset/results/', { params: { search } })
        setSessions(res.data)
      } else {
        const res = await api.get('/api/admin4reset/users/', { params: { search } })
        setUsers(res.data)
      }
    } catch {
      setError('Search failed.')
    } finally {
      setLoading(false)
    }
  }

  async function toggleAdmin(user) {
    try {
      await api.patch(`/api/admin4reset/users/${user.id}/`, { is_admin: !user.is_admin })
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, is_admin: !u.is_admin } : u))
      )
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to update user.')
    }
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="page-shell admin-shell">
      <div className="admin-card">

        <header className="admin-header">
          <div>
            <h1 className="admin-title">Admin Panel</h1>
            <p className="admin-sub">RESET / admin4reset</p>
          </div>
          <div className="header-actions">
            <button className="btn-link" onClick={() => navigate('/')}>App</button>
            <button className="btn-link" onClick={handleLogout}>Sign out</button>
          </div>
        </header>

        <div className="tab-bar">
          <button
            className={`tab-btn ${tab === 'sessions' ? 'tab-active' : ''}`}
            onClick={() => { setTab('sessions'); setSearch('') }}
          >
            Sessions
          </button>
          <button
            className={`tab-btn ${tab === 'users' ? 'tab-active' : ''}`}
            onClick={() => { setTab('users'); setSearch('') }}
          >
            Users
          </button>
        </div>

        <form onSubmit={handleSearch} className="search-bar">
          <input
            className="input"
            type="text"
            placeholder={tab === 'sessions' ? 'Search by email or content…' : 'Search by email…'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">Search</button>
          {search && (
            <button type="button" className="btn btn-ghost" onClick={() => { setSearch(''); fetchData() }}>
              Clear
            </button>
          )}
        </form>

        {error && <p className="error-text">{error}</p>}

        {loading ? (
          <div className="admin-loading"><div className="spinner" /></div>
        ) : tab === 'sessions' ? (
          <div className="sessions-list">
            {sessions.length === 0 && <p className="empty-state">No sessions found.</p>}
            {sessions.map((s) => (
              <div key={s.id} className="session-card">
                <div
                  className="session-summary"
                  onClick={() => setExpandedId(expandedId === s.id ? null : s.id)}
                >
                  <div className="session-meta">
                    <span className="session-email">{s.user_email}</span>
                    <span className={`stress-badge stress-${getStressClass(s.ai_output?.stress_level_int)}`}>
                      Stress {s.ai_output?.stress_level_int ?? '—'}/10
                    </span>
                    {s.feedback && (
                      <span className={`feedback-tag ${s.feedback.rating === 'helpful' ? 'tag-helpful' : 'tag-not'}`}>
                        {s.feedback.rating === 'helpful' ? 'Helpful' : 'Not Helpful'}
                      </span>
                    )}
                  </div>
                  <div className="session-right">
                    <span className="session-date">{formatDate(s.created_at)}</span>
                    <span className="expand-icon">{expandedId === s.id ? '▲' : '▼'}</span>
                  </div>
                </div>

                {expandedId === s.id && (
                  <div className="session-detail">
                    <div className="detail-block">
                      <span className="detail-label">Input</span>
                      <p className="detail-text">{s.input_text}</p>
                    </div>
                    <div className="detail-block">
                      <span className="detail-label">Tier</span>
                      <p className="detail-text">{s.ai_output?.tier}</p>
                    </div>
                    <div className="detail-block">
                      <span className="detail-label">Diagnosis</span>
                      <p className="detail-text">{s.ai_output?.context_summary}</p>
                    </div>
                    {s.feedback?.comment && (
                      <div className="detail-block">
                        <span className="detail-label">Feedback note</span>
                        <p className="detail-text">{s.feedback.comment}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="users-list">
            {users.length === 0 && <p className="empty-state">No users found.</p>}
            {users.map((u) => (
              <div key={u.id} className="user-row">
                <div className="user-info">
                  <span className="user-email">{u.email}</span>
                  <span className="user-count">{u.submission_count} session{u.submission_count !== 1 ? 's' : ''}</span>
                </div>
                <div className="user-actions">
                  {u.is_admin && <span className="admin-tag">Admin</span>}
                  <button
                    className={`btn btn-sm ${u.is_admin ? 'btn-danger' : 'btn-ghost'}`}
                    onClick={() => toggleAdmin(u)}
                  >
                    {u.is_admin ? 'Remove admin' : 'Make admin'}
                  </button>
                </div>
              </div>
            ))}
          </div>
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
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
