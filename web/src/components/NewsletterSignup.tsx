'use client'

import { useState } from 'react'
import { Mail } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

interface NewsletterSignupProps {
  /** Compact inline style vs full card */
  variant?: 'card' | 'inline'
  /** CSS class override for outer container */
  className?: string
}

export default function NewsletterSignup({ variant = 'card', className = '' }: NewsletterSignupProps) {
  const { t, lang } = useLang()
  const isEn = lang === 'en'
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const input = form.querySelector('input') as HTMLInputElement
    const email = input?.value?.trim()
    if (!email) return

    setStatus('loading')
    try {
      const res = await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: variant === 'inline' ? 'inline' : 'landing' }),
      })
      if (res.ok) {
        setStatus('success')
        setMessage(isEn ? 'Subscribed! Check your inbox. 🎉' : '已订阅！请查看邮箱 🎉')
        input.value = ''
        setTimeout(() => { setStatus('idle'); setMessage('') }, 4000)
      } else {
        const data = await res.json()
        setStatus('error')
        setMessage(data.message || (isEn ? 'Something went wrong' : '出错了，请重试'))
        setTimeout(() => { setStatus('idle'); setMessage('') }, 3000)
      }
    } catch {
      setStatus('error')
      setMessage(isEn ? 'Network error — try again' : '网络错误，请重试')
      setTimeout(() => { setStatus('idle'); setMessage('') }, 3000)
    }
  }

  if (variant === 'inline') {
    return (
      <div className={className}>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2.5 max-w-md">
          <div className="relative flex-1">
            <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: '#6E6B80' }} />
            <input
              type="email"
              required
              disabled={status === 'loading'}
              placeholder={isEn ? 'you@email.com' : '输入你的邮箱'}
              className="w-full pl-9 pr-3 py-2.5 rounded-lg text-sm bg-[#0D0D14] border border-[rgba(255,255,255,0.08)] text-[#F5F4F8] placeholder-[#6E6B80] focus:outline-none focus:border-[#6366F1] transition-colors disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={status === 'loading'}
            className="px-5 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90 whitespace-nowrap disabled:opacity-50"
            style={{ background: status === 'success' ? '#22C55E' : '#4338CA', color: '#fff' }}
          >
            {status === 'loading' ? (isEn ? '...' : '...') :
             status === 'success' ? (isEn ? 'Done! ✓' : '完成 ✓') :
             isEn ? 'Subscribe' : '订阅'}
          </button>
        </form>
        {message && (
          <p className={`text-xs mt-2 ${status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
            {message}
          </p>
        )}
      </div>
    )
  }

  // Card variant (default)
  return (
    <div className={`p-8 rounded-xl text-center ${className}`}
      style={{ background: '#14141E', border: '1px solid rgba(99,102,241,0.15)', boxShadow: '0 4px 30px rgba(67,56,202,0.08)' }}>
      <div className="text-3xl mb-3">📬</div>
      <h3 className="text-lg font-bold mb-2">
        {isEn ? 'Get AI Identity insights weekly' : '每周获取 AI Identity 深度内容'}
      </h3>
      <p className="text-sm mb-5 max-w-md mx-auto" style={{ color: '#85829E' }}>
        {isEn
          ? 'Deep dives into AI identity, MCP protocol, and agent infrastructure — delivered to your inbox. No spam.'
          : 'Agent 灵魂资产、MCP 协议、跨框架迁移的深度内容，每周五推送。不打扰，可随时退订。'}
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
        <input
          type="email"
          required
          disabled={status === 'loading'}
          placeholder={isEn ? 'you@email.com' : '输入你的邮箱'}
          className="flex-1 px-4 py-2.5 rounded-lg text-sm bg-[#0D0D14] border border-[rgba(255,255,255,0.08)] text-[#F5F4F8] focus:outline-none focus:border-[#6366F1] transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="px-6 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90 whitespace-nowrap disabled:opacity-50"
          style={{ background: status === 'success' ? '#22C55E' : '#4338CA', color: '#fff' }}
        >
          {status === 'loading' ? (isEn ? 'Subscribing...' : '订阅中...') :
           status === 'success' ? (isEn ? 'Subscribed! 🎉' : '已订阅！🎉') :
           isEn ? 'Subscribe' : '订阅'}
        </button>
      </form>
      {message && (
        <p className={`text-xs mt-3 ${status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
          {message}
        </p>
      )}
      <p className="text-[11px] mt-4" style={{ color: '#6E6B80' }}>
        {isEn ? 'No spam, unsubscribe anytime. One email per week.' : '不打扰，可随时退订。每周一封邮件。'}
      </p>
    </div>
  )
}
