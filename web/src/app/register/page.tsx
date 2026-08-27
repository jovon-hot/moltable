'use client'

import { useState, useEffect, useRef } from 'react'
import { localRegister } from '@/lib/supabase'
import { useLang } from '@/contexts/LanguageContext'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

// Altcha 官方 React 类型声明（React 19 兼容的 JSX IntrinsicElements）
import type {} from 'altcha/types/react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

function RegisterForm() {
  const { t } = useLang()
  const searchParams = useSearchParams()
  const planParam = searchParams.get('plan') || ''
  const refParam = searchParams.get('ref') || ''
  const a = t.auth
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [altchaPayload, setAltchaPayload] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [registered, setRegistered] = useState(false)
  const widgetRef = useRef<any>(null)

  useEffect(() => {
    // 动态加载 Altcha widget（客户端，依赖 Web Crypto / Web Components）
    import('altcha')
      .then(() => {
        const el = widgetRef.current
        if (el) {
          el.addEventListener('statechange', (ev: any) => {
            if (ev.detail?.state === 'verified') {
              setAltchaPayload(ev.detail.payload || '')
            } else if (ev.detail?.state === 'expired') {
              setAltchaPayload('')
            }
          })
        }
      })
      .catch(() => {
        // 加载失败时 payload 保持空，后端会拦截并提示
      })
  }, [])

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!altchaPayload) {
      setError('请先完成人机验证')
      return
    }
    setLoading(true)
    setError('')
    try {
      await localRegister(email, password, undefined, altchaPayload)
      // 方案 A：注册不发放 key，引导用户查收验证邮件
      if (refParam) sessionStorage.setItem('moltable_ref_code', refParam)
      setRegistered(true)
    } catch (err: any) {
      setError(err.message || a.registerFailed)
      // 非验证码类错误（邮箱重复/格式/一次性邮箱等）保留 payload —— 5 分钟内可复用，
      // 用户改完表单即可直接重试；验证码过期由 widget 的 expired 状态自行清空。
    }
    setLoading(false)
  }

  if (registered) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0D0D14' }}>
        <div className="w-full max-w-sm text-center">
          <div className="text-5xl mb-4">📬</div>
          <h1 className="text-2xl mb-3" style={{ fontWeight: 590, color: '#ffffff' }}>验证你的邮箱</h1>
          <p className="text-sm mb-6" style={{ color: '#888888', lineHeight: 1.7 }}>
            注册成功！我们已向 <span style={{ color: '#fff' }}>{email}</span> 发送验证链接（30 分钟内有效）。
            点击邮件里的链接完成验证，然后登录即可获取你的 API Key。
          </p>
          <a href="/login" className="inline-block w-full py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
            style={{ background: '#4338CA', color: '#fff', fontWeight: 510, textDecoration: 'none' }}>
            前往登录 →
          </a>
          <p className="text-xs mt-4" style={{ color: '#5a5f68' }}>
            没收到邮件？检查垃圾箱，或稍后重新注册获取新链接。
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0D0D14' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#ffffff' }}>{a.registerTitle}</h1>
          <p className="text-sm" style={{ color: '#888888' }}>
            {planParam === 'pro' ? 'Pro · 30天免费' : 'Moltable'}
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-3">
          <input type="email" placeholder={a.emailPlaceholder} value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#14141E', color: '#ffffff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #4338CA'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder={a.passwordPlaceholder} value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#14141E', color: '#ffffff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #4338CA'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <p className="text-xs" style={{ color: '#5a5f68' }}>{a.passwordHint}</p>

          {/* Altcha 人机验证（PoW，防机器人批量注册） */}
          <altcha-widget
            ref={widgetRef}
            challenge={`${API_BASE}/api/auth/challenge`}
            auto="onload"
            theme="dark"
            configuration={JSON.stringify({ hideLogo: true, hideFooter: true })}
          ></altcha-widget>

          {error && <p className="text-sm" style={{ color: '#f87171' }}>{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-[6px] text-sm font-medium disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
            {loading ? a.registering : a.registerBtn}
          </button>
        </form>

        <p className="text-sm text-center mt-6" style={{ color: '#888888' }}>
          {a.hasAccount} <a href="/login" style={{ color: '#3730A3' }} className="hover:underline">{a.goLogin}</a>
        </p>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  return <Suspense fallback={<div />}><RegisterForm /></Suspense>
}
