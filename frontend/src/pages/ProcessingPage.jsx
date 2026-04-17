import { useEffect, useRef, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import api from '../api/client'

const MESSAGES = [
  'Analyzing your state…',
  'Identifying patterns…',
  'Mapping stress indicators…',
  'Building your plan…',
  'Finalizing protocol…',
]

export default function ProcessingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const inputText = location.state?.inputText

  const [msgIndex, setMsgIndex] = useState(0)
  const [error, setError] = useState('')
  const submitted = useRef(false)

  useEffect(() => {
    if (!inputText) {
      navigate('/', { replace: true })
      return
    }

    if (submitted.current) return
    submitted.current = true

    const interval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % MESSAGES.length)
    }, 1800)

    const timeout = setTimeout(() => {
      setError('Request is taking longer than expected. Please try again.')
      clearInterval(interval)
    }, 30000)

    api.post('/api/submit/', { input_text: inputText })
      .then((res) => {
        clearInterval(interval)
        clearTimeout(timeout)
        localStorage.removeItem('reset_input_draft')
        navigate(`/results/${res.data.id}`, { replace: true })
      })
      .catch((err) => {
        clearInterval(interval)
        clearTimeout(timeout)
        const msg = err.response?.data?.error || 'Something went wrong. Please try again.'
        setError(msg)
      })

    return () => {
      clearInterval(interval)
      clearTimeout(timeout)
    }
  }, [])

  if (error) {
    return (
      <div className="page-shell">
        <div className="card card-center">
          <div className="error-icon">!</div>
          <h2 className="error-heading">Something went wrong.</h2>
          <p className="error-body">{error}</p>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/', { state: { inputText } })}
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="page-shell">
      <div className="card card-center">
        <div className="processing-ring" />
        <p className="processing-msg">{MESSAGES[msgIndex]}</p>
      </div>
    </div>
  )
}
