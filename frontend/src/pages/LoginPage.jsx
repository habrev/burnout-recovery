import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()

  const [mode, setMode] = useState('login')
  const [registerStep, setRegisterStep] = useState(0)

  const [email, setEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [registrationToken, setRegistrationToken] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (user) {
    navigate('/', { replace: true })
    return null
  }

  function switchMode(m) {
    setMode(m)
    setError('')
    setRegisterStep(0)
    setOtpCode('')
    setPassword('')
    setConfirmPassword('')
    setLoginPassword('')
  }

  async function handleLogin(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/api/auth/login/', { email, password: loginPassword })
      login({ access: res.data.access, refresh: res.data.refresh }, res.data.user)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleRequestOtp(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/api/auth/request-otp/', { email })
      setRegisterStep(1)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send code. Try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleVerifyOtp(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/api/auth/verify-otp/', { email, code: otpCode })
      setRegistrationToken(res.data.registration_token)
      setRegisterStep(2)
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid code. Try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setError('')
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/api/auth/register/', {
        email,
        registration_token: registrationToken,
        password,
      })
      login({ access: res.data.access, refresh: res.data.refresh }, res.data.user)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">

        {/* Brand */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 tracking-tight">RESET</h1>
          <p className="text-gray-400 mt-2 text-sm font-medium tracking-wide uppercase">
            Realtime reset for high performers
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">

          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            {['login', 'register'].map((m) => (
              <button
                key={m}
                onClick={() => switchMode(m)}
                className={`flex-1 py-4 text-sm font-semibold transition-all ${
                  mode === m
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/40'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <div className="p-8">
            {mode === 'login' ? (

              /* ── LOGIN FORM ── */
              <form onSubmit={handleLogin} className="space-y-5">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Welcome back</h2>
                  <p className="text-sm text-gray-400 mt-1">Sign in to continue your reset journey</p>
                </div>

                {error && <ErrorAlert message={error} />}

                <Field label="Email address" type="email" value={email}
                  onChange={setEmail} placeholder="you@example.com" autoFocus />
                <Field label="Password" type="password" value={loginPassword}
                  onChange={setLoginPassword} placeholder="••••••••" />

                <PrimaryButton loading={loading} disabled={!email || !loginPassword}>
                  Sign In
                </PrimaryButton>
              </form>

            ) : (

              /* ── REGISTER FLOW ── */
              <div className="space-y-6">
                <StepIndicator current={registerStep} />

                {registerStep === 0 && (
                  <form onSubmit={handleRequestOtp} className="space-y-5">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">Create your account</h2>
                      <p className="text-sm text-gray-400 mt-1">
                        We'll send a verification code to confirm your email
                      </p>
                    </div>
                    {error && <ErrorAlert message={error} />}
                    <Field label="Email address" type="email" value={email}
                      onChange={setEmail} placeholder="you@example.com" autoFocus />
                    <PrimaryButton loading={loading} disabled={!email}>
                      Send Verification Code
                    </PrimaryButton>
                  </form>
                )}

                {registerStep === 1 && (
                  <form onSubmit={handleVerifyOtp} className="space-y-5">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">Check your email</h2>
                      <p className="text-sm text-gray-400 mt-1">
                        Enter the 6-digit code sent to{' '}
                        <span className="font-semibold text-gray-600">{email}</span>
                      </p>
                    </div>
                    {error && <ErrorAlert message={error} />}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Verification code
                      </label>
                      <input
                        type="text"
                        inputMode="numeric"
                        value={otpCode}
                        onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        placeholder="000000"
                        autoFocus
                        required
                        className="w-full px-4 py-3.5 text-center text-2xl font-bold tracking-[.6em] border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition placeholder:tracking-normal placeholder:text-gray-300 placeholder:font-normal placeholder:text-base"
                      />
                    </div>
                    <PrimaryButton loading={loading} disabled={otpCode.length !== 6}>
                      Verify Code
                    </PrimaryButton>
                    <button
                      type="button"
                      onClick={() => { setRegisterStep(0); setOtpCode(''); setError('') }}
                      className="w-full text-sm text-gray-400 hover:text-gray-600 transition"
                    >
                      ← Use a different email
                    </button>
                  </form>
                )}

                {registerStep === 2 && (
                  <form onSubmit={handleRegister} className="space-y-5">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">Set your password</h2>
                      <p className="text-sm text-gray-400 mt-1">Minimum 8 characters</p>
                    </div>
                    {error && <ErrorAlert message={error} />}
                    <Field label="Password" type="password" value={password}
                      onChange={setPassword} placeholder="••••••••" autoFocus />
                    <Field label="Confirm password" type="password" value={confirmPassword}
                      onChange={setConfirmPassword} placeholder="••••••••" />
                    <PrimaryButton loading={loading} disabled={!password || !confirmPassword}>
                      Create Account
                    </PrimaryButton>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Switch mode link */}
        <p className="text-center text-sm text-gray-400 mt-6">
          {mode === 'login' ? (
            <>Don't have an account?{' '}
              <button onClick={() => switchMode('register')}
                className="text-blue-600 font-semibold hover:underline">
                Create one free
              </button>
            </>
          ) : (
            <>Already have an account?{' '}
              <button onClick={() => switchMode('login')}
                className="text-blue-600 font-semibold hover:underline">
                Sign in
              </button>
            </>
          )}
        </p>

      </div>
    </div>
  )
}

function StepIndicator({ current }) {
  const steps = ['Email', 'Verify', 'Password']
  return (
    <div className="flex items-center justify-center gap-1">
      {steps.map((label, i) => (
        <div key={i} className="flex items-center gap-1">
          <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all ${
            i < current  ? 'bg-blue-600 text-white' :
            i === current ? 'bg-blue-50 text-blue-600 ring-2 ring-blue-500' :
                            'bg-gray-100 text-gray-400'
          }`}>
            {i < current ? '✓' : i + 1}
          </div>
          <span className={`text-xs font-medium ${i === current ? 'text-blue-600' : 'text-gray-400'}`}>
            {label}
          </span>
          {i < steps.length - 1 && (
            <div className={`w-6 h-px mx-1 ${i < current ? 'bg-blue-500' : 'bg-gray-200'}`} />
          )}
        </div>
      ))}
    </div>
  )
}

function Field({ label, type, value, onChange, placeholder, autoFocus }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        required
        className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-900 placeholder:text-gray-300 text-sm"
      />
    </div>
  )
}

function PrimaryButton({ children, loading, disabled }) {
  return (
    <button
      type="submit"
      disabled={disabled || loading}
      className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-bold rounded-xl transition-colors flex items-center justify-center gap-2"
    >
      {loading ? (
        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : children}
    </button>
  )
}

function ErrorAlert({ message }) {
  return (
    <div className="flex items-start gap-2.5 px-4 py-3 bg-red-50 border border-red-100 rounded-xl">
      <span className="text-red-500 font-bold text-sm mt-px flex-shrink-0">!</span>
      <p className="text-red-600 text-sm leading-snug">{message}</p>
    </div>
  )
}
