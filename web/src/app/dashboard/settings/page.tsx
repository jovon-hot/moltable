'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { apiFetch, createCheckout } from '@/lib/api'
import { Loader2, Key, Copy, Check, Trash2, Shield, Plus, Eye, EyeOff, Brain, Crown, ArrowUp } from 'lucide-react'

interface ApiKey {
  id: string
  name: string
  key_prefix: string
  created_at: string
  last_used_at?: string
  is_active: boolean
}

interface UsageStats {
  memories: { used: number; limit: number }
  personas: { used: number; limit: number }
  agents: { used: number; limit: number }
  identities: { used: number; limit: number }
  api_keys: { used: number; limit: number }
}

interface UserProfile {
  id: string
  email: string
  name: string
  plan: string
  plan_name: string
  created_at: string
  usage?: { plan: string; plan_name: string; usage: UsageStats }
}

const PLAN_COLORS: Record<string, string> = { free: '#8a8f98', pro: '#7170ff', team: '#22c55e' }

export default function SettingsPage() {
  const { toast } = useToast()
  const [user, setUser] = useState<UserProfile | null>(null)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [newKeyName, setNewKeyName] = useState('')
  const [creating, setCreating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [isDemo, setIsDemo] = useState(false)
  const [upgrading, setUpgrading] = useState(false)
  const [activeTab, setActiveTab] = useState<'profile' | 'keys'>(() => {
    if (typeof window !== 'undefined' && window.location.search.includes('upgrade=pro')) return 'profile'
    return 'profile'
  })

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<any>('/api/auth/me')
      setUser(data)
      if (data.usage) {
        setApiKeys([])
      } else {
        // Old endpoint — try keys separately
        try {
          const keys = await apiFetch<ApiKey[]>('/api/auth/api-keys')
          setApiKeys(Array.isArray(keys) ? keys : [])
        } catch { setApiKeys([]) }
      }
    } catch (err: any) {
      setIsDemo(true)
      setApiKeys([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKey = async () => {
    showDemoToast()
  }

  const handleRevokeKey = async (id: string, name: string) => {
    showDemoToast()
  }

  const showDemoToast = () => {
    toast('演示模式 — 注册后可用', 'info')
  }

  const copyNewKey = () => {
    if (newKey) { navigator.clipboard.writeText(newKey); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  }

  const handleUpgrade = async () => {
    setUpgrading(true)
    try {
      const url = await createCheckout('pro')
      window.location.href = url
    } catch (e: any) {
      toast(e.message || '支付服务暂未开通', 'error')
    } finally {
      setUpgrading(false)
    }
  }

  const renderProgress = (label: string, used: number, limit: number, color: string) => {
    const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0
    const isNearLimit = pct >= 80
    return (
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1" style={{ color: '#b0b5bd' }}>
          <span>{label}</span>
          <span style={{ color: isNearLimit ? '#fbbf24' : '#8a8f98' }}>
            {used} / {limit >= 999999 ? '∞' : limit}
          </span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-full rounded-full transition-all duration-300" style={{ width: `${pct}%`, background: isNearLimit ? '#fbbf24' : color }} />
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#7170ff' }} />
      </div>
    )
  }

  const usage: UsageStats = user?.usage?.usage || {
    memories: { used: 0, limit: 100 },
    personas: { used: 0, limit: 2 },
    agents: { used: 0, limit: 1 },
    identities: { used: 1, limit: 1 },
    api_keys: { used: 0, limit: 10 },
  }

  const isFree = (user?.plan || 'free') === 'free'
  const planColor = PLAN_COLORS[user?.plan || 'free'] || '#8a8f98'

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="text-xl mb-8" style={{ fontWeight: 590, color: '#f7f8f8' }}>设置</h1>

      {/* Tab bar */}
      <div className="flex gap-6 mb-8 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        {[
          { id: 'profile', label: '个人中心' },
          { id: 'keys', label: 'API 密钥' },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id as any)}
            className="pb-3 text-sm font-medium transition-all border-b-2"
            style={{
              color: activeTab === tab.id ? '#f7f8f8' : '#8a8f98',
              borderColor: activeTab === tab.id ? '#7170ff' : 'transparent',
              fontWeight: activeTab === tab.id ? 590 : 400,
            }}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <>
          {/* Plan card */}
          <div className="p-5 rounded-[8px] mb-6" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: `${planColor}20` }}>
                  {isFree ? <Shield size={18} color={planColor} /> : <Crown size={18} color={planColor} />}
                </div>
                <div>
                  <p className="text-sm" style={{ fontWeight: 590, color: '#f7f8f8' }}>
                    {user?.plan_name || '免费版'}
                  </p>
                  <p className="text-xs" style={{ color: '#8a8f98' }}>
                    {isFree ? '试用中 — 功能受限' : '专业版 — 全部功能'}
                  </p>
                </div>
              </div>
              {isFree && (
                <button onClick={handleUpgrade} disabled={upgrading}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-[6px] text-xs font-medium transition-all hover:opacity-90"
                  style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                  <ArrowUp size={14} />
                  {upgrading ? '跳转中...' : '升级 Pro'}
                </button>
              )}
            </div>

            {/* Usage bars */}
            <div className="space-y-0.5">
              {renderProgress('记忆条目', usage.memories.used, usage.memories.limit, planColor)}
              {renderProgress('Persona', usage.personas.used, usage.personas.limit, planColor)}
              {renderProgress('Agent', usage.agents.used, usage.agents.limit, planColor)}
              {renderProgress('AI 身份', usage.identities.used, usage.identities.limit, planColor)}
            </div>
          </div>

          {/* Pro feature teaser for free users */}
          {isFree && (
            <div className="p-5 rounded-[8px] mb-6" style={{ background: 'rgba(113,112,255,0.04)', boxShadow: '0 0 0 1px rgba(113,112,255,0.15)' }}>
              <h3 className="text-sm mb-3" style={{ fontWeight: 590, color: '#7170ff' }}>
                Pro 解锁更多
              </h3>
              <div className="grid grid-cols-2 gap-2 text-xs" style={{ color: '#b0b5bd' }}>
                {['10,000 条记忆（x100）', '10 个 Persona（x5）', '5 个 Agent', '浏览器插件', '优先技术支持', '¥19/月 · 随时取消'].map((f, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <Check size={12} style={{ color: '#7170ff' }} />
                    {f}
                  </div>
                ))}
              </div>
              <button onClick={handleUpgrade} disabled={upgrading}
                className="w-full mt-4 py-2 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
                style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                {upgrading ? '跳转中...' : '¥149/年 · 立即升级'}
              </button>
            </div>
          )}

          {/* Basic info */}
          <div className="p-5 rounded-[8px]" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <h3 className="text-sm mb-4" style={{ fontWeight: 590, color: '#f7f8f8' }}>基本信息</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span style={{ color: '#8a8f98' }}>邮箱</span>
                <span style={{ color: '#f7f8f8' }}>{user?.email || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: '#8a8f98' }}>昵称</span>
                <span style={{ color: '#f7f8f8' }}>{user?.name || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span style={{ color: '#8a8f98' }}>注册时间</span>
                <span style={{ color: '#f7f8f8' }}>{user?.created_at?.split('T')[0] || '—'}</span>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'keys' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm" style={{ fontWeight: 590, color: '#f7f8f8' }}>API 密钥</h2>
            <button onClick={handleCreateKey} disabled={creating || isDemo}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] text-xs font-medium transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
              <Plus size={14} /> 新建密钥
            </button>
          </div>

          {newKey && (
            <div className="p-4 rounded-[8px] mb-4" style={{ background: 'rgba(34,197,94,0.08)', boxShadow: '0 0 0 1px rgba(34,197,94,0.2)' }}>
              <p className="text-xs mb-2" style={{ color: '#22c55e', fontWeight: 590 }}>新密钥已生成，仅显示一次：</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs py-2 px-3 rounded-[4px]" style={{ background: 'rgba(255,255,255,0.04)', color: '#f7f8f8', wordBreak: 'break-all' }}>
                  {newKey}
                </code>
                <button onClick={copyNewKey} className="p-2 rounded-[4px] transition-all" style={{ color: copied ? '#22c55e' : '#8a8f98' }}>
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                </button>
              </div>
            </div>
          )}

          {apiKeys.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: '#8a8f98' }}>
              {isDemo ? '登录后查看 API 密钥' : '暂无密钥，点击上方按钮创建'}
            </p>
          ) : (
            <div className="space-y-2">
              {apiKeys.map(key => (
                <div key={key.id} className="flex items-center justify-between p-3 rounded-[6px]"
                  style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
                  <div>
                    <p className="text-sm" style={{ fontWeight: 510, color: '#f7f8f8' }}>{key.name}</p>
                    <p className="text-xs mt-0.5" style={{ color: '#8a8f98', fontFamily: 'monospace' }}>
                      {key.key_prefix}*** · {key.created_at?.split('T')[0] || '—'}
                    </p>
                  </div>
                  <button onClick={() => handleRevokeKey(key.id, key.name)}
                    className="p-1.5 rounded-[4px] transition-all hover:bg-opacity-10"
                    style={{ color: '#f87171', background: 'rgba(248,113,113,0.06)' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
