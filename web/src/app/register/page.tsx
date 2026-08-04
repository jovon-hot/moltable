'use client'

import { useState } from 'react'
import { localRegister } from '@/lib/supabase'
import { useLang } from '@/contexts/LanguageContext'

export default function RegisterPage() {
  const { t } = useLang()
  const a = t.auth
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await localRegister(email, password)
      // 🪄 魔法时刻：直接跳到接入页，预填 API Key
      if (data.key) {
        window.location.href = `/connect?key=${encodeURIComponent(data.key)}&new=true`
      } else {
        window.location.href = '/dashboard'
      }
    } catch (err: any) {
      setError(err.message || a.registerFailed)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#08090a' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#f7f8f8' }}>{a.registerTitle}</h1>
          <p className="text-sm" style={{ color: '#8a8f98' }}>Moltable</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-3">
          <input type="email" placeholder={a.emailPlaceholder} value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#0f1011', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder={a.passwordPlaceholder} value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#0f1011', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <p className="text-xs" style={{ color: '#5a5f68' }}>{a.passwordHint}</p>
          {error && <p className="text-sm" style={{ color: '#f87171' }}>{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-[6px] text-sm font-medium disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
            {loading ? a.registering : a.registerBtn}
          </button>
        </form>

        <p className="text-sm text-center mt-6" style={{ color: '#8a8f98' }}>
          {a.hasAccount} <a href="/login" style={{ color: '#828fff' }} className="hover:underline">{a.goLogin}</a>
        </p>
      </div>
    </div>
  )
}
