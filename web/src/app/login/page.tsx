'use client'

import { useState } from 'react'
import { createClient, isLocalMode, localLogin } from '@/lib/supabase'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const local = isLocalMode()
  const supabase = local ? null : createClient()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (local) {
      try {
        await localLogin(email, password)
        window.location.href = '/dashboard'
      } catch (err: any) {
        setError(err.message || '登录失败')
      }
    } else {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) setError(error.message)
      else window.location.href = '/dashboard'
    }
    setLoading(false)
  }

  const handleGoogleLogin = async () => {
    if (local) return
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/dashboard` }
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#08090a' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#f7f8f8' }}>Moltable</h1>
          <p className="text-sm" style={{ color: '#8a8f98' }}>登录你的 AI 身份</p>
          {local && <p className="text-xs mt-1" style={{ color: '#7170ff' }}>本地开发模式</p>}
        </div>

        <form onSubmit={handleLogin} className="space-y-3">
          <input type="email" placeholder="邮箱" value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#0f1011', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder="密码" value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#0f1011', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          {error && <p className="text-sm" style={{ color: '#f87171' }}>{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-[6px] text-sm font-medium disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        {!local && (
          <div className="mt-3">
            <button onClick={handleGoogleLogin}
              className="w-full py-2.5 rounded-[6px] text-sm font-medium flex items-center justify-center gap-2 transition-all hover:opacity-90"
              style={{ background: 'rgba(255,255,255,0.04)', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 510 }}>
              <svg className="w-4 h-4" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              Google 登录
            </button>
          </div>
        )}

        <p className="text-sm text-center mt-6" style={{ color: '#8a8f98' }}>
          还没有账号？<a href="/register" style={{ color: '#828fff' }} className="hover:underline">注册</a>
        </p>
      </div>
    </div>
  )
}
