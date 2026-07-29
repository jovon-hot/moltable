'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import Link from 'next/link'
import { Loader2, Brain, User, Key, ArrowRight, Check } from 'lucide-react'

const DEMO_STATS = { memories: 128, personas: 3, projects: 5, decisions: 42 }

export default function DashboardPage() {
  const { toast } = useToast()
  const { t } = useLang()
  const [stats, setStats] = useState({ memories: 0, personas: 0 })
  const [loading, setLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [memories, personas] = await Promise.all([
        apiFetch<any[]>('/api/memories/?limit=1').catch(() => null),
        apiFetch<any[]>('/api/personas/').catch(() => null),
      ])

      if (memories === null && personas === null) {
        setIsDemo(true)
        setStats({ memories: DEMO_STATS.memories, personas: DEMO_STATS.personas })
        setLoading(false)
        return
      }

      let memCount = Array.isArray(memories) ? memories.length : 0
      if (memCount <= 1) {
        const all = await apiFetch<any[]>('/api/memories/?limit=10000').catch(() => memories)
        memCount = Array.isArray(all) ? all.length : memCount
      }
      const persCount = Array.isArray(personas) ? personas.length : 0
      setStats({ memories: memCount, personas: persCount })
    } catch (err: any) {
      setIsDemo(true)
      setStats({ memories: DEMO_STATS.memories, personas: DEMO_STATS.personas })
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: t.dashboard.stats.memories, value: stats.memories, icon: Brain, href: '/dashboard/memories' },
    { label: t.dashboard.stats.personas, value: stats.personas, icon: User, href: '/dashboard/personas' },
    { label: t.dashboard.stats.projects, value: DEMO_STATS.projects, icon: Key, href: '/dashboard/memories' },
    { label: t.dashboard.stats.decisions, value: DEMO_STATS.decisions, icon: Brain, href: '/dashboard/memories' },
  ]

  const onboardingSteps = [
    { step: 1, title: t.dashboard.step1, desc: '在设置页面生成你的 API Key' },
    { step: 2, title: t.dashboard.step2, desc: '在 Hermes / Claude 中加载 Moltable Skill' },
    { step: 3, title: t.dashboard.step3, desc: 'AI 自动认识你，开始积累记忆' },
  ]

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      {/* Registration CTA for demo users */}
      {isDemo && (
        <div className="mb-8 p-5 rounded-card bg-ln-accent-muted shadow-accent-glow border border-ln-accent/20">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 mt-0.5 w-8 h-8 rounded-full bg-ln-accent flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-base font-heading text-ln-text mb-1">正在演示模式 — 注册后开始使用</h3>
              <p className="text-sm text-ln-secondary mb-3">
                注册后你的 AI Agent 可以记住所有对话，跨设备同步偏好和记忆。当前显示的是演示数据。
              </p>
              <Link href="/register" 
                className="inline-flex items-center gap-2 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all">
                立即注册 <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Page header */}
      <div className="mb-10">
        <h1 className="text-2xl mb-1 font-heading tracking-[-0.3px] text-ln-text">
          {isDemo ? 'Moltable Dashboard' : '欢迎回来'}
        </h1>
        <p className="text-sm text-ln-tertiary font-body">
          {isDemo ? (
            <>演示数据 — <Link href="/login" className="text-ln-accent hover:text-ln-accent-hover transition-colors font-ui">注册后</Link> 开始使用</>
          ) : (
            '管理你的 AI 身份、记忆和 Persona'
          )}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
        {statCards.map((s, i) => (
          <Link
            key={i}
            href={s.href}
            className="group p-5 rounded-card bg-ln-surface shadow-card transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-8 h-8 rounded-btn bg-ln-accent-muted flex items-center justify-center">
                <s.icon size={16} className="text-ln-accent" />
              </div>
            </div>
            <div className="text-2xl mb-1 font-heading text-ln-text">
              {loading ? <Loader2 className="w-5 h-5 animate-spin inline text-ln-accent" /> : s.value}
            </div>
            <div className="text-xs text-ln-tertiary font-body flex items-center gap-1 transition-colors group-hover:text-ln-secondary">
              {s.label}
              <ArrowRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </Link>
        ))}
      </div>

      {/* Onboarding guide for first-time users */}
      {(stats.memories === 0 && stats.personas === 0 && !isDemo) && (
        <div className="mb-8 p-6 rounded-card bg-ln-surface shadow-accent-glow">
          <h3 className="text-lg mb-4 font-heading text-ln-text">🚀 {t.dashboard.quickStart}</h3>
          <div className="space-y-3">
            {onboardingSteps.map(s => (
              <div key={s.step} className="flex items-start gap-3">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-ln-accent-muted flex items-center justify-center">
                  <Check size={14} className="text-ln-accent" />
                </div>
                <div>
                  <p className="text-sm font-ui text-ln-text">{s.title}</p>
                  <p className="text-xs mt-0.5 text-ln-tertiary font-body">
                    {s.step === 1 ? (
                      <>
                        {s.desc} — <Link href="/dashboard/settings" className="text-ln-accent hover:text-ln-accent-hover transition-colors">前往设置 →</Link>
                      </>
                    ) : s.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Start / API Integration */}
      <div className="p-8 rounded-panel bg-ln-surface shadow-accent-glow transition-all duration-200">
        <h2 className="text-lg mb-2 flex items-center gap-2 font-heading text-ln-text">
          🚀 {t.dashboard.quickStart}
        </h2>
        <p className="text-sm mb-6 text-ln-secondary font-body leading-relaxed">
          在任何支持 MCP 的 AI Agent 中加载 Moltable Skill，AI 自动认识你。
        </p>

        {/* Code display */}
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
          {t.dashboard.getKey}
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  )
}
