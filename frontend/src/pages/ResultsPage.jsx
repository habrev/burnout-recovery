import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function ResultsPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [feedbackSent, setFeedbackSent] = useState(false)
  const [checkedActions, setCheckedActions] = useState([])

  useEffect(() => {
    api.get(`/api/results/${id}/`)
      .then((res) => {
        setResult(res.data)
        if (res.data.feedback) {
          setFeedback(res.data.feedback.rating)
          setFeedbackSent(true)
        }
      })
      .catch(() => setError('Could not load this session.'))
      .finally(() => setLoading(false))
  }, [id])

  function toggleAction(i) {
    setCheckedActions((prev) =>
      prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i]
    )
  }

  async function sendFeedback(rating) {
    if (feedbackSent) return
    setFeedback(rating)
    try {
      await api.post(`/api/results/${id}/feedback/`, {
        rating,
        comment: feedbackComment,
      })
      setFeedbackSent(true)
    } catch {
      setFeedback(null)
    }
  }

  if (loading) {
    return (
      <div className="page-shell">
        <div className="card card-center">
          <div className="spinner" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-shell">
        <div className="card card-center">
          <p className="error-body">{error}</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>Back to home</button>
        </div>
      </div>
    )
  }

  const out = result?.ai_output || {}
  const stressLevel = out.stress_level_int ?? 0
  const confidence = Math.round((out.burnout_risk_score ?? 0) * 100)
  const stressClass = stressLevel > 7 ? 'high' : stressLevel >= 4 ? 'mid' : 'low'

  return (
    <div className="page-shell">
      <div className="card results-card">

        <header className="results-header">
          <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
          <h1 className="results-title">Recovery Plan</h1>
          <span className="results-date">{formatDate(result?.created_at)}</span>
        </header>

        {/* STATUS */}
        <section className="result-section">
          <h2 className="section-label">Status</h2>
          <div className="status-row">
            <div className="stat-block">
              <span className={`stress-score stress-${stressClass}`}>{stressLevel}</span>
              <span className="stat-label">/ 10 stress</span>
            </div>
            <div className="stat-block">
              <span className={`stress-score stress-${stressClass}`}>{confidence}%</span>
              <span className="stat-label">confidence</span>
            </div>
            <div className="stat-block">
              <span className="emotion-tag">{out.primary_emotion?.toUpperCase()}</span>
            </div>
          </div>
        </section>

        <div className="divider" />

        {/* DIAGNOSIS */}
        <section className="result-section">
          <h2 className="section-label">Diagnosis</h2>
          <p className="section-body">{out.context_summary}</p>
        </section>

        <div className="divider" />

        {/* CRITICAL STATE */}
        <section className="result-section">
          <h2 className="section-label">Critical State</h2>
          <div className={`state-badge state-${stressClass}`}>{out.label}</div>
          <p className="section-body tone-text">{out.tone}</p>
        </section>

        <div className="divider" />

        {/* RECOVERY WINDOW */}
        <section className="result-section">
          <h2 className="section-label">Recovery Window</h2>
          <div className="recovery-window-value">{out.recovery_window}</div>
        </section>

        <div className="divider" />

        {/* PROTOCOL */}
        <section className="result-section protocol-section">
          <h2 className="section-label">Protocol</h2>
          <p className="section-sublabel">Complete these actions to begin your reset:</p>
          <ul className="action-list">
            {(out.actions || []).map((action, i) => (
              <li
                key={i}
                className={`action-item ${checkedActions.includes(i) ? 'action-done' : ''}`}
                onClick={() => toggleAction(i)}
              >
                <span className="action-check">{checkedActions.includes(i) ? '✓' : ''}</span>
                <span className="action-text">{action}</span>
              </li>
            ))}
          </ul>
        </section>

        <div className="divider" />

        {/* NEXT CHECK-IN */}
        <section className="result-section">
          <h2 className="section-label">Next Check-in</h2>
          <p className="section-body">{out.next_checkin}</p>
        </section>

        <div className="divider" />

        {/* FOOTER + FEEDBACK */}
        <section className="result-section footer-section">
          <button className="btn btn-outline" onClick={() => navigate('/')}>
            Check again after reset
          </button>

          <div className="feedback-block">
            <p className="feedback-label">Was this plan helpful?</p>
            {feedbackSent ? (
              <p className="feedback-sent">
                Thanks for your feedback{feedback === 'helpful' ? ' 👍' : ' 👎'}
              </p>
            ) : (
              <div className="feedback-btns">
                <button
                  className={`feedback-btn ${feedback === 'helpful' ? 'active-helpful' : ''}`}
                  onClick={() => sendFeedback('helpful')}
                >
                  Helpful
                </button>
                <button
                  className={`feedback-btn ${feedback === 'not_helpful' ? 'active-not' : ''}`}
                  onClick={() => sendFeedback('not_helpful')}
                >
                  Not Helpful
                </button>
              </div>
            )}
            {!feedbackSent && feedback && (
              <div className="feedback-comment">
                <textarea
                  className="input"
                  rows={2}
                  placeholder="Optional: anything to add?"
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                />
                <button className="btn btn-ghost" onClick={() => sendFeedback(feedback)}>
                  Submit
                </button>
              </div>
            )}
          </div>
        </section>

      </div>
    </div>
  )
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
