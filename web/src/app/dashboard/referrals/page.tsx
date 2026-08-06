'use client'

import { useCallback, useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import {
  Loader2, Copy, Check, Gift, Share2, Users, UserCheck, Clock,
  Mail, Twitter, Send, MessageCircle, Link2,
} from 'lucide-react'

interface ReferralStats {
  referrer_id: string
  invites_sent: number
  claimed: number
  pending: number
  codes: { code: string; status: string; referred_email?: string; created_at?: string; claimed_at?: string }[]
}

export default function ReferralsPage() {
  const { toast } = useToast()
  const { lang } = useLang()
  const zh = lang === 'zh'

  const [code, setCode] = useState('')
  const [stats, setStats] = useState<ReferralStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [userId, setUserId] = useState<string | null>(null)

  const shareUrl = code && typeof window !== 'undefined' ? `${window.location.origin}/signup?ref=${code}` : ''
  const shareText = zh
    ? `用我的邀请码 ${code} 注册 Moltable，打造你的 AI 身份层！`
    : `Sign up for Moltable with my invite code ${code} — your AI identity layer!`

  const loadStats = useCallback(async (uid: string) => {
    const data = await apiFetch<ReferralStats>(`/api/referrals/stats/${uid}`)
    setStats(data)
    if (data.codes && data.codes.length > 0) {
      setCode(data.codes[0].code)
    } else {
      // No code yet — generate one automatically
      const gen = await apiFetch<{ code: string }>('/api/referrals/generate', {
        method: 'POST',
        body: JSON.stringify({}),
      })
      setCode(gen.code)
      const fresh = await apiFetch<ReferralStats>(`/api/referrals/stats/${uid}`)
      setStats(fresh)
    }
  }, [])

  useEffect(() => {
    (async () => {
      try {
        const me = await apiFetch<{ id: string; email: string }>('/api/auth/me')
        setUserId(me.id)
        await loadStats(me.id)
      } catch (err: any) {
        toast(err?.message || (zh ? '加载推荐信息失败' : 'Failed to load referral info'), 'error')
      } finally {
        setLoading(false)
      }
    })()
  }, [loadStats, toast, zh])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const gen = await apiFetch<{ code: string }>('/api/referrals/generate', {
        method: 'POST',
        body: JSON.stringify({}),
      })
      setCode(gen.code)
      if (userId) await loadStats(userId)
      toast(zh ? '新邀请码已生成' : 'New invite code generated', 'success')
    } catch (err: any) {
      toast(err?.message || (zh ? '生成失败' : 'Failed to generate'), 'error')
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast(label, 'success')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast(zh ? '复制失败' : 'Copy failed', 'error')
    }
  }

  const socialLinks = code
    ? [
        {
          label: 'X / Twitter',
          icon: Twitter,
          href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
          cls: 'hover:bg-ln-hover',
        },
        {
          label: 'WhatsApp',
          icon: MessageCircle,
          href: `https://wa.me/?text=${encodeURIComponent(`${shareText} ${shareUrl}`)}`,
          cls: 'hover:bg-ln-hover',
        },
        {
          label: 'Telegram',
          icon: Send,
          href: `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`,
          cls: 'hover:bg-ln-hover',
        },
        {
          label: 'Email',
          icon: Mail,
          href: `mailto:?subject=${encodeURIComponent(zh ? '邀请你加入 Moltable' : 'Join me on Moltable')}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`,
          cls: 'hover:bg-ln-hover',
        },
      ]
    : []

  const statCards = [
    { label: zh ? '已发送邀请' : 'Invites Sent', value: stats?.invites_sent ?? 0, icon: Users, accent: 'text-ln-accent' },
    { label: zh ? '已注册' : 'Claimed', value: stats?.claimed ?? 0, icon: UserCheck, accent: 'text-emerald-400' },
    { label: zh ? '待处理' : 'Pending', value: stats?.pending ?? 0, icon: Clock, accent: 'text-amber-400' },
  ]

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-heading tracking-[-0.3px] text-ln-text">{zh ? '邀请好友' : 'Referrals'}</h1>
          <p className="text-sm text-ln-tertiary font-body mt-1">
            {zh ? '分享你的专属邀请码，邀请朋友加入 Moltable' : 'Share your unique invite code and bring friends to Moltable'}
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-sm font-ui transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? <Loader2 size={15} className="animate-spin" /> : <Gift size={15} />}
          {zh ? '生成新邀请码' : 'New Invite Code'}
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-6 h-6 animate-spin text-ln-accent" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Referral code card */}
          <div className="p-6 rounded-card bg-ln-surface shadow-card">
            <div className="flex items-center gap-2 mb-4">
              <Gift size={16} className="text-ln-accent" />
              <h2 className="text-base font-ui text-ln-text">{zh ? '你的专属邀请码' : 'Your Invite Code'}</h2>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch gap-3">
              <div className="flex-1 flex items-center justify-center gap-3 px-4 py-5 rounded-btn bg-ln-bg shadow-border-subtle">
                <span className="text-3xl font-mono font-semibold tracking-[0.35em] text-ln-accent select-all">
                  {code || '········'}
                </span>
              </div>
              <button
                onClick={() => code && handleCopy(code, zh ? '邀请码已复制' : 'Invite code copied')}
                disabled={!code}
                className="flex items-center justify-center gap-1.5 px-5 py-2 rounded-btn text-sm font-ui transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover disabled:opacity-50"
              >
                {copied ? <Check size={15} /> : <Copy size={15} />}
                {copied ? (zh ? '已复制' : 'Copied') : (zh ? '复制' : 'Copy')}
              </button>
            </div>

            {code && (
              <button
                onClick={() => handleCopy(shareUrl, zh ? '邀请链接已复制' : 'Invite link copied')}
                className="mt-3 flex items-center gap-2 w-full px-4 py-2.5 rounded-btn bg-ln-bg text-ln-secondary text-xs font-mono shadow-border-subtle hover:shadow-border-accent transition-all duration-150 text-left truncate"
              >
                <Link2 size={13} className="flex-shrink-0 text-ln-tertiary" />
                <span className="truncate">{shareUrl}</span>
              </button>
            )}
          </div>

          {/* Stats */}
          <div className="grid sm:grid-cols-3 gap-3">
            {statCards.map(({ label, value, icon: Icon, accent }) => (
              <div key={label} className="p-5 rounded-card bg-ln-surface shadow-card">
                <div className="flex items-center gap-2 mb-3">
                  <Icon size={15} className={accent} />
                  <span className="text-xs text-ln-tertiary font-ui">{label}</span>
                </div>
                <p className="text-3xl font-heading tracking-[-0.5px] text-ln-text">{value}</p>
              </div>
            ))}
          </div>

          {/* Share links */}
          <div className="p-6 rounded-card bg-ln-surface shadow-card">
            <div className="flex items-center gap-2 mb-4">
              <Share2 size={16} className="text-ln-accent" />
              <h2 className="text-base font-ui text-ln-text">{zh ? '分享邀请' : 'Share Your Invite'}</h2>
            </div>
            {socialLinks.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {socialLinks.map(({ label, icon: Icon, href, cls }) => (
                  <a
                    key={label}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`flex items-center justify-center gap-2 px-4 py-3 rounded-btn bg-ln-bg text-ln-secondary text-sm font-body shadow-border-subtle transition-all duration-150 ${cls}`}
                  >
                    <Icon size={15} className="text-ln-accent" />
                    {label}
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-sm text-ln-tertiary font-body">{zh ? '生成邀请码后即可分享' : 'Generate a code to start sharing'}</p>
            )}
          </div>

          {/* Recent invites */}
          {stats && stats.codes.length > 0 && (
            <div className="p-6 rounded-card bg-ln-surface shadow-card">
              <h2 className="text-base font-ui text-ln-text mb-4">{zh ? '邀请记录' : 'Invite History'}</h2>
              {stats.codes.length === 0 ? (
                <p className="text-sm text-ln-tertiary font-body">{zh ? '还没有邀请记录' : 'No invites yet'}</p>
              ) : (
                <div className="space-y-2">
                  {stats.codes.map((c) => (
                    <div
                      key={c.code}
                      className="flex items-center justify-between gap-3 px-4 py-3 rounded-btn bg-ln-bg shadow-border-subtle"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="font-mono text-sm text-ln-text tracking-wider">{c.code}</span>
                        <span className="text-xs text-ln-tertiary font-body truncate">
                          {c.referred_email || (zh ? '等待注册' : 'awaiting signup')}
                        </span>
                      </div>
                      <span
                        className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-body ${
                          c.status === 'claimed'
                            ? 'bg-emerald-400/10 text-emerald-400 shadow-[0_0_0_1px_rgba(52,211,153,0.25)]'
                            : 'bg-amber-400/10 text-amber-400 shadow-[0_0_0_1px_rgba(251,191,36,0.25)]'
                        }`}
                      >
                        {c.status === 'claimed' ? (zh ? '已注册' : 'Claimed') : (zh ? '待处理' : 'Pending')}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
