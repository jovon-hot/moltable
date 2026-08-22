'use client'

import { useEffect, useState } from 'react'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import Link from 'next/link'
import { Loader2, Brain, User, ArrowRight, Zap, Clock, Layers, AlertTriangle, RefreshCw } from 'lucide-react'

interface PlanInfo {
  plan: 'free' | 'pro'
}

export default function DashboardPage() {
  const { t, lang } = useLang()
  const d = t.dashboard as any
  const ui = t.dashboard_ui as any
  const [stats, setStats] = useState({ total_memories: 0, total_personas: 0, total_projects: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [plan, setPlan] = useState<PlanInfo>({ plan: 'free' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [memStats, personas, userInfo] = await Promise.all([
        apiFetch<{ total: number; by_category?: Record<string, number> }>('/api/memories/stats').catch(() => null),
        apiFetch<any[]>('/api/personas').catch(() => null),
        apiFetch<{ id: string; email: string; name: string; plan?: string; trial_end?: string; trial_days_left?: number }>('/api/auth/me').catch(() => null),
      ])

      if (memStats === null && personas === null && userInfo === null) {
        setError(true)
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
        setPlan({ plan: userPlan as PlanInfo['plan'] })
      }
    } catch (err: any) {
      setError(true)
      setStats({ total_memories: 0, total_personas: 0, total_projects: 0 })
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: ui.statsMemoryCount, value: stats.total_memories, icon: Brain, href: '/dashboard/memories', color: '#4338CA' },
    { label: ui.statsPersonaCount, value: stats.total_personas, icon: User, href: '/dashboard/personas', color: '#4ade80' },
    { label: ui.statsProjectCount, value: stats.total_projects, icon: Layers, href: '/dashboard', color: '#60a5fa' },
  ]

  const planCard = {
    icon: plan.plan === 'free' ? Clock : Zap,
    color: plan.plan === 'free' ? '#888888' : '#4338CA',
  }

  const getPlanLabel = (): string => {
    switch (plan.plan) {
      case 'free': return ui.planFree as string
      case 'pro': return ui.planPro as string
      default: return plan.plan
    }
  }

  const getPlanSubLabel = (): string => {
    if (plan.plan === 'free') return ui.upgradePro as string
    if (plan.plan === 'pro') return ui.planPro as string
    return ''
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      {/* Error state */}
      {error && (
        <div className="mb-8 p-5 rounded-card bg-ln-warning/10 shadow-[0_0_0_1px_rgba(234,179,8,0.2)]">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 mt-0.5 w-8 h-8 rounded-full bg-ln-warning flex items-center justify-center">
              <AlertTriangle size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-heading text-ln-text mb-1">{lang === 'zh' ? '无法加载数据' : 'Unable to load data'}</h3>
              <p className="text-sm text-ln-secondary mb-3">
                {lang === 'zh' ? '请检查网络连接后重试。' : 'Please check your connection and try again.'}
              </p>
              <button onClick={loadData}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all">
                <RefreshCw size={14} /> {lang === 'zh' ? '重试' : 'Retry'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Page header */}
      <div className="mb-10">
        <h1 className="text-2xl mb-1 font-heading tracking-[-0.3px] text-ln-text">
          {lang === 'zh' ? '欢迎回来' : 'Welcome Back'}
        </h1>
        <p className="text-sm text-ln-tertiary font-body">
          {lang === 'zh' ? '管理你的 Agent 灵魂资产与备份源' : 'Manage your Agent soul assets and backup sources'}
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
