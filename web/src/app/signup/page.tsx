'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'
import { Gift, ArrowRight, Shield, Zap, Users } from 'lucide-react'

function SignupContent() {
  const { lang } = useLang()
  const searchParams = useSearchParams()
  const refCode = searchParams.get('ref') || ''
  const zh = lang === 'zh'

  const benefits = [
    {
      icon: Gift,
      title: zh ? '30 天 Pro 免费试用' : '30-Day Free Pro Trial',
      desc: zh
        ? '通过邀请链接注册，自动获得 30 天 Pro 版全部功能'
        : 'Sign up via invite link and get 30 days of full Pro features automatically',
    },
    {
      icon: Zap,
      title: zh ? '3 分钟恢复 AI 环境' : 'Restore AI Environment in 3 Min',
      desc: zh
        ? '换电脑、换设备都不怕，Moltable 同步你的 AI 记忆与偏好'
        : 'Switch devices freely — Moltable syncs your AI memory and preferences across all agents',
    },
    {
      icon: Shield,
      title: zh ? '加密存储，数据自主' : 'Encrypted & Self-Sovereign',
      desc: zh
        ? '你的记忆数据加密存储，随时可导出或删除，完全由你掌控'
        : 'Your memory data is encrypted at rest, exportable anytime, fully under your control',
    },
  ]

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-20" style={{ background: '#0D0D14', color: '#F5F4F8' }}>
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] pointer-events-none"
        style={{ background: 'radial-gradient(circle at 45% 30%, rgba(99,102,241,0.08), transparent 55%), radial-gradient(circle at 60% 40%, rgba(251,107,75,0.04), transparent 55%)' }} />

      <div className="relative max-w-lg mx-auto text-center">
        {/* Referral badge */}
        {refCode && (
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs mb-6"
            style={{ background: 'rgba(99,102,241,0.1)', color: '#A5B4FC', border: '1px solid rgba(99,102,241,0.12)' }}>
            <Gift size={13} />
            {zh ? `好友邀请你加入 Moltable` : `A friend invited you to Moltable`}
          </div>
        )}

        <h1 className="text-3xl md:text-4xl font-extrabold mb-3 leading-tight" style={{ letterSpacing: '-1px' }}>
          {zh ? '你的 AI 终于' : 'Your AI finally'}{' '}
          <span style={{ color: '#FB6B4B' }}>{zh ? '认识你' : 'knows you'}</span>
        </h1>
        <p className="text-base mb-2" style={{ color: '#A8A5B8' }}>
          {zh
            ? '一个账户，所有 AI Agent 共享记忆与偏好'
            : 'One account, all AI agents share your memory and preferences'}
        </p>
        <p className="text-sm mb-10" style={{ color: '#85829E' }}>
          {zh
            ? '支持 Hermes、Claude、ChatGPT、Cursor 及所有 MCP 兼容 Agent'
            : 'Works with Hermes, Claude, ChatGPT, Cursor, and all MCP-compatible agents'}
        </p>

        {/* CTA */}
        <Link
          href={refCode ? `/register?ref=${encodeURIComponent(refCode)}` : '/register'}
          className="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg text-base font-semibold transition-all hover:-translate-y-0.5 mb-4"
          style={{ background: '#4338CA', color: '#fff', boxShadow: '0 0 0 1px rgba(99,102,241,0.3)' }}
        >
          {zh ? '免费注册' : 'Sign Up Free'} <ArrowRight size={18} />
        </Link>

        <p className="text-xs mb-12" style={{ color: '#6E6B80' }}>
          {zh ? '无需信用卡 · 90 天免费试用' : 'No credit card · 90-day free trial'}
        </p>

        {/* Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
          {benefits.map((b, i) => {
            const Icon = b.icon
            return (
              <div key={i} className="p-4 rounded-xl" style={{ background: '#14141E', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Icon size={18} style={{ color: '#6366F1', marginBottom: 8 }} />
                <h3 className="text-sm font-semibold mb-1">{b.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: '#85829E' }}>{b.desc}</p>
              </div>
            )
          })}
        </div>

        {/* Social proof */}
        <div className="mt-10 pt-8" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <p className="text-xs mb-3" style={{ color: '#6E6B80' }}>
            {zh ? '已有 1,000+ 开发者和 AI 用户加入' : 'Trusted by 1,000+ developers and AI users'}
          </p>
          <div className="flex items-center justify-center gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <span key={i} style={{ color: '#6366F1', fontSize: 12 }}>★</span>
            ))}
            <span className="text-xs ml-1" style={{ color: '#85829E' }}>4.9</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SignupPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0D0D14' }}>
        <div className="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: '#4338CA', borderTopColor: 'transparent' }} />
      </div>
    }>
      <SignupContent />
    </Suspense>
  )
}
