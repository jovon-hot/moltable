'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch, activateTrial } from '@/lib/api'
import Link from 'next/link'
import { Loader2, Brain, User, ArrowRight, Zap, Sparkles, Clock, Layers } from 'lucide-react'

const DEMO_STATS = { memories: 128, personas: 3, projects: 5, decisions: 42 }

interface PlanInfo {
  plan: 'free' | 'pro' | 'trialing' | 'expired'
  trial_end?: string
  trial_days_left?: number
}

export default function DashboardPage() {
  const { toast } = useToast()
  const { t, lang } = useLang()
  const d = t.dashboard as any
  const ui = t.dashboard_ui as any
  const [stats, setStats] = useState({ total_memories: 0, total_personas: 0, total_projects: 0 })
  const [loading, setLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)
  const [plan, setPlan] = useState<PlanInfo>({ plan: 'free' })
  const [activating, setActivating] = useState(false)
  const [showBanner, setShowBanner] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [memStats, personas, userInfo] = await Promise.all([
        apiFetch<{ total: number; by_category?: Record<string, number> }>('/api/memories/stats').catch(() => null),
        apiFetch<any[]>('/api/personas/').catch(() => null),
        apiFetch<{ id: string; email: string; name: string; plan?: string; trial_end?: string; trial_days_left?: number }>('/api/auth/me').catch(() => null),
      ])

      if (memStats === null && personas === null && userInfo === null) {
        setIsDemo(true)
        setLoading(false)
        return
      }

      const memCount = memStats?.total ?? 0
      const persCount = Array.isArray(personas) ? personas.length : 0

      setStats({
        total_memories: memCount,
        total_personas: persCount,
        total_projects: 0,
      })

      // Parse plan info from user
      if (userInfo) {
        const userPlan = userInfo.plan || 'free'
        setPlan({
          plan: userPlan as PlanInfo['plan'],
          trial_end: userInfo.trial_end,
          trial_days_left: userInfo.trial_days_left,
        })
        if (userPlan === 'pro' || userPlan === 'trialing') {
          setShowBanner(false)
        }
      }
    } catch (err: any) {
      setIsDemo(true)
      setStats({ total_memories: 128, total_personas: 3, total_projects: 5 })
    } finally {
      setLoading(false)
    }
  }

  const handleActivate = async () => {
    setActivating(true)
    try {
      const result = await activateTrial('pro')
      toast(ui.trialActivated as string, 'success')
      setPlan({
        plan: 'trialing',
        trial_end: result.expires_at,
        trial_days_left: 90,
      })
      setShowBanner(false)
      // Reload stats to refresh
      await loadData()
    } catch (err: any) {
      toast(err?.message || 'Activation failed', 'error')
    } finally {
      setActivating(false)
    }
  }

  const statCards = [
    { label: ui.statsMemoryCount, value: stats.total_memories, icon: Brain, href: '/dashboard/memories', color: '#00e040' },
    { label: ui.statsPersonaCount, value: stats.total_personas, icon: User, href: '/dashboard/personas', color: '#4ade80' },
    { label: ui.statsProjectCount, value: stats.total_projects, icon: Layers, href: '/dashboard', color: '#60a5fa' },
  ]

  const planCard = {
    icon: plan.plan === 'free' ? Clock : plan.plan === 'trialing' ? Sparkles : Zap,
    color: plan.plan === 'free' ? '#888888' : '#00e040',
  }

  const getPlanLabel = (): string => {
    switch (plan.plan) {
      case 'free': return ui.planFree as string
      case 'pro': return ui.planPro as string
      case 'trialing': return ui.planTrialing as string
      case 'expired': return ui.planExpired as string
      default: return plan.plan
    }
  }

  const getPlanSubLabel = (): string => {
    if (plan.plan === 'trialing' && plan.trial_days_left !== undefined) {
      return (ui.trialDaysLeft as string).replace('{days}', String(plan.trial_days_left))
    }
    if (plan.plan === 'free') return ui.activatePro as string
    if (plan.plan === 'pro') return ui.planPro as string
    return ''
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      {/* Trial Activation Banner */}
      {!isDemo && !loading && plan.plan === 'free' && showBanner && (
        <div className="mb-8 p-5 rounded-panel bg-ln-surface shadow-accent-glow border border-ln-accent/30 animate-in">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 mt-0.5 w-10 h-10 rounded-full bg-gradient-to-br from-ln-accent to-ln-accent-hover flex items-center justify-center">
              <Sparkles size={20} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-heading text-ln-text mb-1">{ui.trialBanner as string}</h3>
              <p className="text-sm text-ln-secondary mb-3 font-body">
                {ui.trialBannerSub as string}
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleActivate}
                  disabled={activating}
                  className="inline-flex items-center gap-2 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {activating ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
                  {activating ? (ui.trialActivating as string) : (ui.trialBannerCta as string)}
                </button>
                <button
                  onClick={() => setShowBanner(false)}
                  className="text-xs text-ln-tertiary hover:text-ln-secondary transition-colors font-body"
                >
                  {ui.cancelBtn as string}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active trial banner */}
      {!isDemo && !loading && plan.plan === 'trialing' && plan.trial_days_left !== undefined && (
        <div className="mb-8 px-4 py-3 rounded-card bg-ln-accent-muted text-ln-accent-hover text-sm font-body shadow-border-accent animate-in flex items-center gap-2">
          <Sparkles size={16} />
          <span>{ui.trialActive as string}</span>
          <span className="text-ln-secondary">·</span>
          <span>{(ui.trialDaysLeft as string).replace('{days}', String(plan.trial_days_left))}</span>
        </div>
      )}

      {/* Expired trial banner */}
      {!isDemo && !loading && plan.plan === 'expired' && (
        <div className="mb-8 px-4 py-3 rounded-card bg-ln-warning/10 text-ln-warning text-sm font-body shadow-[0_0_0_1px_rgba(234,179,8,0.2)] animate-in flex items-center gap-2">
          <Clock size={16} />
          <span>{ui.trialExpired as string}</span>
        </div>
      )}

      {/* Registration CTA for demo users */}
      {isDemo && (
        <div className="mb-8 p-5 rounded-card bg-ln-accent-muted shadow-accent-glow border border-ln-accent/20">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 mt-0.5 w-8 h-8 rounded-full bg-ln-accent flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-heading text-ln-text mb-1">{d.demoBanner}</h3>
              <p className="text-sm text-ln-secondary mb-3">
                {lang === 'zh' ? '注册后你的 AI Agent 可以记住所有对话，跨设备同步偏好和记忆。当前显示的是演示数据。' : 'After registering, your AI Agent remembers every conversation and syncs preferences across devices. Currently showing demo data.'}
              </p>
              <Link href="/register" 
                className="inline-flex items-center gap-2 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all">
                {lang === 'zh' ? '立即注册' : 'Sign Up Now'} <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Page header */}
      <div className="mb-10">
        <h1 className="text-2xl mb-1 font-heading tracking-[-0.3px] text-ln-text">
          {isDemo ? 'Moltable Dashboard' : lang === 'zh' ? '欢迎回来' : 'Welcome Back'}
        </h1>
        <p className="text-sm text-ln-tertiary font-body">
          {isDemo ? (
            <>{lang === 'zh' ? '演示数据 — ' : 'Demo data — '}<Link href="/login" className="text-ln-accent hover:text-ln-accent-hover transition-colors font-ui">{lang === 'zh' ? '注册后' : 'Sign in'}</Link> {lang === 'zh' ? '开始使用' : 'to get started'}</>
          ) : (
            lang === 'zh' ? '管理你的 AI 身份、记忆和 Persona' : 'Manage your AI identity, memories and personas'
          )}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="mb-3">
        <h2 className="text-sm font-ui text-ln-tertiary mb-3 tracking-wide uppercase">{ui.statsTitle as string}</h2>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
        {statCards.map((s, i) => (
          <Link
            key={i}
            href={s.href}
            className="group p-5 rounded-card bg-ln-surface shadow-card transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-8 h-8 rounded-btn flex items-center justify-center" style={{ background: `${s.color}18` }}>
                <s.icon size={16} style={{ color: s.color }} />
              </div>
            </div>
            <div className="text-2xl mb-1 font-heading text-ln-text">
              {loading ? <Loader2 className="w-5 h-5 animate-spin inline text-ln-accent" /> : (s.value ?? 0)}
            </div>
            <div className="text-xs text-ln-tertiary font-body flex items-center gap-1 transition-colors group-hover:text-ln-secondary">
              {s.label}
              <ArrowRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </Link>
        ))}

        {/* Plan Status Card */}
        <div
          className="group p-5 rounded-card bg-ln-surface shadow-card transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-8 h-8 rounded-btn flex items-center justify-center" style={{ background: `${planCard.color}18` }}>
              <planCard.icon size={16} style={{ color: planCard.color }} />
            </div>
          </div>
          <div className="text-lg mb-1 font-heading text-ln-text">
            {loading ? <Loader2 className="w-5 h-5 animate-spin inline text-ln-accent" /> : getPlanLabel()}
          </div>
          <div className="text-xs text-ln-tertiary font-body">
            {loading ? '' : getPlanSubLabel()}
          </div>
        </div>
      </div>

      {/* Quick Start / API Integration */}
      <div className="p-8 rounded-panel bg-ln-surface shadow-accent-glow transition-all duration-200">
        <h2 className="text-lg mb-2 flex items-center gap-2 font-heading text-ln-text">
          🚀 {d.quickStart}
        </h2>
        <p className="text-sm mb-6 text-ln-secondary font-body leading-relaxed">
          {lang === 'zh' ? '在任何支持 MCP 的 AI Agent 中加载 Moltable Skill，AI 自动认识你。' : 'Load the Moltable Skill in any MCP-compatible AI Agent — your AI knows you instantly.'}
        </p>

        <div className="rounded-card bg-ln-bg shadow-border p-4 text-sm font-mono text-ln-secondary">
          <p className="text-xs mb-2 text-ln-tertiary font-body"># Hermes</p>
          <p className="text-ln-accent-hover">/skill moltable</p>
          <p className="text-xs mt-4 mb-2 text-ln-tertiary font-body"># Claude Desktop</p>
          <p className="text-ln-success">claude mcp add moltable -- stdio python3 mcp_server.py</p>
        </div>

        <Link
          href="/dashboard/settings"
          className="inline-flex items-center gap-2 mt-6 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150"
        >
          {d.getKey}
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  )
}
