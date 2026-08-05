'use client'

import { useState } from 'react'
import { localLogin } from '@/lib/supabase'
import { useLang } from '@/contexts/LanguageContext'

export default function LoginPage() {
  const { t, lang } = useLang()
  const a = t.auth
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await localLogin(email, password)
      window.location.href = '/dashboard'
    } catch (err: any) {
      setError(err.message || a.loginFailed)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#111111' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#ffffff' }}>Moltable</h1>
          <p className="text-sm" style={{ color: '#888888' }}>{a.loginTitle}</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-3">
          <input type="email" placeholder={a.emailPlaceholder} value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[8px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#16161a', color: '#fff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #00e040'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder={a.passwordPlaceholder} value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[8px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#16161a', color: '#fff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #00e040'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          {error && <p className="text-sm" style={{ color: '#f87171' }}>{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-[8px] text-sm font-medium disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: '#00e040', color: '#111', fontWeight: 510 }}>
            {loading ? a.loggingIn : a.loginBtn}
          </button>
        </form>

        <p className="text-sm text-center mt-6" style={{ color: '#888888' }}>
          {a.noAccount} <a href="/register" style={{ color: '#00e040' }} className="hover:underline">{a.goRegister}</a>
        </p>
      </div>
    </div>
  )
}
