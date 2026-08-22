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
      title: zh ? '引用同步' : 'Reference Sync',
      desc: zh
        ? '你引用的知识库、内容来源一并备份，换机完整还原工作环境'
        : 'Knowledge bases and content sources you reference are backed up too',
    },
    {
      icon: Zap,
      title: zh ? '一条命令备份' : 'One-Command Backup',
      desc: zh
        ? 'moltable backup push —— 打包上传你的 SOUL、Skills、MCP 配置和记忆'
        : 'moltable backup push — pack and upload your SOUL, Skills, MCP configs, and memories',
    },
    {
      icon: Shield,
      title: zh ? '版本管理，可回滚' : 'Versioned & Rollback',
      desc: zh
        ? '每个备份源独立版本库，快照 + 版本号，改坏了随时回滚'
        : 'Each source has its own version history — roll back to any point anytime',
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
          {zh ? '换 Agent，' : 'Switch agents, '}
          <span style={{ color: '#FB6B4B' }}>{zh ? '不换灵魂' : 'keep your soul'}</span>
        </h1>
        <p className="text-base mb-2" style={{ color: '#A8A5B8' }}>
          {zh
            ? '备份你的 Agent 灵魂资产，换框架、换电脑都不丢失'
            : 'Back up your agent soul — never lose your tuning when you switch frameworks or machines'}
        </p>
        <p className="text-sm mb-10" style={{ color: '#85829E' }}>
          {zh
            ? '支持 Hermes、OpenClaw、Claude、Codex 及所有 MCP 兼容 Agent'
            : 'Works with Hermes, OpenClaw, Claude, Codex, and all MCP-compatible agents'}
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
          {zh ? '无需信用卡 · 免费开始' : 'No credit card · Start free'}
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
            {zh ? '开源 MIT · 你的数据永远属于你' : 'Open source MIT · your data always belongs to you'}
          </p>
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
