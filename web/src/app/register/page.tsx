'use client'

import { useState } from 'react'
import { createClient, isLocalMode, localRegister } from '@/lib/supabase'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const local = isLocalMode()
  const supabase = local ? null : createClient()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (local) {
      // 本地 SQLite 模式
      try {
        await localRegister(email, password)
        window.location.href = '/dashboard'
      } catch (err: any) {
        setError(err.message || '注册失败')
      }
    } else {
      // Supabase 模式
      const { error } = await supabase.auth.signUp({ email, password })
      if (error) setError(error.message)
      else window.location.href = '/dashboard'
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#08090a' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#f7f8f8' }}>创建 Moltable 账号</h1>
          <p className="text-sm" style={{ color: '#8a8f98' }}>拥有你的 AI 身份</p>
          {local && <p className="text-xs mt-1" style={{ color: '#7170ff' }}>本地开发模式</p>}
        </div>

        <form onSubmit={handleRegister} className="space-y-3">
          <input type="email" placeholder="邮箱" value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#0f1011', color: '#f7f8f8', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder="密码（至少 6 位）" value={password}
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
            {loading ? '创建中...' : '注册'}
          </button>
        </form>

        <p className="text-sm text-center mt-6" style={{ color: '#8a8f98' }}>
          已有账号？<a href="/login" style={{ color: '#828fff' }} className="hover:underline">登录</a>
        </p>
      </div>
    </div>
  )
}
