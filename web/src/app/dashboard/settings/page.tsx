'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch, activateTrial } from '@/lib/api'
import { Loader2, Key, Copy, Check, Trash2, Shield, Plus, Eye, EyeOff, Brain, Crown, ArrowUp, RefreshCw } from 'lucide-react'

interface ApiKey { id: string; name: string; key_prefix: string; created_at: string; last_used_at?: string; is_active: boolean }
interface UsageStats { memories: { used: number; limit: number }; personas: { used: number; limit: number }; agents: { used: number; limit: number }; identities: { used: number; limit: number }; api_keys: { used: number; limit: number } }
interface UserProfile { id: string; email: string; name: string; plan: string; plan_name: string; created_at: string; usage?: { plan: string; plan_name: string; usage: UsageStats } }

const PLAN_COLORS: Record<string, string> = { free: '#8a8f98', pro: '#7170ff', team: '#22c55e' }

export default function SettingsPage() {
  const { toast } = useToast()
  const { t, lang } = useLang()
  const d = t.dashboard_ui as any
  const [user, setUser] = useState<UserProfile | null>(null)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [newKeyName, setNewKeyName] = useState('')
  const [creating, setCreating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [isDemo, setIsDemo] = useState(false)
  const [upgrading, setUpgrading] = useState(false)
  const [activeTab, setActiveTab] = useState<'profile' | 'keys' | 'sync'>('profile')
  const [syncCode, setSyncCode] = useState<string | null>(null)
  const [syncCopied, setSyncCopied] = useState(false)
  const [syncLoading, setSyncLoading] = useState(false)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<any>('/api/auth/me')
      setUser(data)
      try { const keys = await apiFetch<ApiKey[]>('/api/auth/api-keys'); setApiKeys(Array.isArray(keys) ? keys : []) }
      catch { setApiKeys([]) }
    } catch (err: any) { setIsDemo(true); setApiKeys([]) }
    finally { setLoading(false) }
  }

  const handleCreateKey = async () => { showDemoToast() }
  const handleRevokeKey = async (id: string, name: string) => { showDemoToast() }
  const showDemoToast = () => toast(lang === 'zh' ? '演示模式 — 注册后可用' : 'Demo mode — sign up to use', 'info')
  const copyNewKey = () => { if (newKey) { navigator.clipboard.writeText(newKey); setCopied(true); setTimeout(() => setCopied(false), 2000) } }

  const generateSyncCode = async () => {
    setSyncLoading(true)
    try {
      const data = await apiFetch<{ sync_code: string }>('/api/auth/sync-code')
      setSyncCode(data.sync_code)
    } catch {
      toast(lang === 'zh' ? '生成失败，请重试' : 'Generation failed, retry', 'error')
    }
    finally { setSyncLoading(false) }
  }

  const copySyncCode = () => {
    if (syncCode) { navigator.clipboard.writeText(syncCode); setSyncCopied(true); setTimeout(() => setSyncCopied(false), 2000) }
  }

  const handleUpgrade = async () => {
    setUpgrading(true)
    try { await activateTrial('pro'); toast(lang === 'zh' ? 'Pro 体验已激活！90 天免费使用' : 'Pro trial activated! 90 days free.', 'success') }
    catch (e: any) { toast(e.message || (lang === 'zh' ? '激活失败，请重试' : 'Activation failed, please retry'), 'error') }
    finally { setUpgrading(false) }
  }

  const renderProgress = (label: string, used: number, limit: number, color: string) => {
    const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0
    const isNearLimit = pct >= 80
    return (
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1" style={{ color: '#b0b5bd' }}>
          <span>{label}</span>
          <span style={{ color: isNearLimit ? '#fbbf24' : '#8a8f98' }}>{used} / {limit >= 999999 ? '∞' : limit}</span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-full rounded-full transition-all duration-300" style={{ width: `${pct}%`, background: isNearLimit ? '#fbbf24' : color }} />
        </div>
      </div>
    )
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#7170ff' }} /></div>
  }

  const usage: UsageStats = user?.usage?.usage || { memories: { used: 0, limit: 100 }, personas: { used: 0, limit: 2 }, agents: { used: 0, limit: 1 }, identities: { used: 1, limit: 1 }, api_keys: { used: 0, limit: 10 } }
  const isFree = (user?.plan || 'free') === 'free'
  const planColor = PLAN_COLORS[user?.plan || 'free'] || '#8a8f98'
  const proFeatures = [d.proFeature1, d.proFeature2, d.proFeature3, d.proFeature4, d.proFeature5, d.proFeature6]

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="text-xl mb-8" style={{ fontWeight: 590, color: '#f7f8f8' }}>{d.settingsPageTitle}</h1>

      <div className="flex gap-6 mb-8 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        {[
          { id: 'profile', label: d.tabProfile },
          { id: 'keys', label: d.tabAPIKeys },
          { id: 'sync', label: d.tabSync || (lang === 'zh' ? '同步码' : 'Sync') },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id as any)}
            className="pb-3 text-sm font-medium transition-all border-b-2"
            style={{ color: activeTab === tab.id ? '#f7f8f8' : '#8a8f98', borderColor: activeTab === tab.id ? '#7170ff' : 'transparent', fontWeight: activeTab === tab.id ? 590 : 400 }}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <>
          <div className="p-5 rounded-[8px] mb-6" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: `${planColor}20` }}>
                  {isFree ? <Shield size={18} color={planColor} /> : <Crown size={18} color={planColor} />}
                </div>
                <div>
                  <p className="text-sm" style={{ fontWeight: 590, color: '#f7f8f8' }}>{user?.plan_name || d.freePlan}</p>
                  <p className="text-xs" style={{ color: '#8a8f98' }}>{isFree ? d.onTrial : d.proPlan}</p>
                </div>
              </div>
              {isFree && (
                <button onClick={handleUpgrade} disabled={upgrading}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-[6px] text-xs font-medium transition-all hover:opacity-90"
                  style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                  <ArrowUp size={14} /> {upgrading ? d.upgrading : d.upgradePro}
                </button>
              )}
            </div>
            <div className="space-y-0.5">
              {renderProgress(d.usage_memories, usage.memories.used, usage.memories.limit, planColor)}
              {renderProgress(d.usage_personas, usage.personas.used, usage.personas.limit, planColor)}
              {renderProgress(d.usage_agents, usage.agents.used, usage.agents.limit, planColor)}
              {renderProgress(d.usage_identities, usage.identities.used, usage.identities.limit, planColor)}
            </div>
          </div>

          {isFree && (
            <div className="p-5 rounded-[8px] mb-6" style={{ background: 'rgba(113,112,255,0.04)', boxShadow: '0 0 0 1px rgba(113,112,255,0.15)' }}>
              <h3 className="text-sm mb-3" style={{ fontWeight: 590, color: '#7170ff' }}>{d.proUnlock}</h3>
              <div className="grid grid-cols-2 gap-2 text-xs" style={{ color: '#b0b5bd' }}>
                {proFeatures.map((f: string, i: number) => (<div key={i} className="flex items-center gap-2"><Check size={12} style={{ color: '#7170ff' }} />{f}</div>))}
              </div>
              <button onClick={handleUpgrade} disabled={upgrading}
                className="w-full mt-4 py-2 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
                style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                {upgrading ? d.upgrading : d.y149year}
              </button>
            </div>
          )}

          <div className="p-5 rounded-[8px]" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <h3 className="text-sm mb-4" style={{ fontWeight: 590, color: '#f7f8f8' }}>{d.basicInfo}</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span style={{ color: '#8a8f98' }}>{d.email}</span><span style={{ color: '#f7f8f8' }}>{user?.email || '—'}</span></div>
              <div className="flex justify-between"><span style={{ color: '#8a8f98' }}>{d.nickname}</span><span style={{ color: '#f7f8f8' }}>{user?.name || '—'}</span></div>
              <div className="flex justify-between"><span style={{ color: '#8a8f98' }}>{d.registeredAt}</span><span style={{ color: '#f7f8f8' }}>{user?.created_at?.split('T')[0] || '—'}</span></div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'keys' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm" style={{ fontWeight: 590, color: '#f7f8f8' }}>API {lang === 'zh' ? '密钥' : 'Keys'}</h2>
            <button onClick={handleCreateKey} disabled={creating || isDemo}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] text-xs font-medium transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
              <Plus size={14} /> {d.createKey}
            </button>
          </div>

          {newKey && (
            <div className="p-4 rounded-[8px] mb-4" style={{ background: 'rgba(34,197,94,0.08)', boxShadow: '0 0 0 1px rgba(34,197,94,0.2)' }}>
              <p className="text-xs mb-2" style={{ color: '#22c55e', fontWeight: 590 }}>{d.newKeyCreated}</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs py-2 px-3 rounded-[4px]" style={{ background: 'rgba(255,255,255,0.04)', color: '#f7f8f8', wordBreak: 'break-all' }}>{newKey}</code>
                <button onClick={copyNewKey} className="p-2 rounded-[4px] transition-all" style={{ color: copied ? '#22c55e' : '#8a8f98' }}>{copied ? <Check size={16} /> : <Copy size={16} />}</button>
              </div>
            </div>
          )}

          {apiKeys.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: '#8a8f98' }}>{isDemo ? d.loginToView : d.noKeysYet}</p>
          ) : (
            <div className="space-y-2">
              {apiKeys.map(key => (
                <div key={key.id} className="flex items-center justify-between p-3 rounded-[6px]" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
                  <div>
                    <p className="text-sm" style={{ fontWeight: 510, color: '#f7f8f8' }}>{key.name}</p>
                    <p className="text-xs mt-0.5" style={{ color: '#8a8f98', fontFamily: 'monospace' }}>{key.key_prefix}*** · {key.created_at?.split('T')[0] || '—'}</p>
                  </div>
                  <button onClick={() => handleRevokeKey(key.id, key.name)}
                    className="p-1.5 rounded-[4px] transition-all hover:bg-opacity-10" style={{ color: '#f87171', background: 'rgba(248,113,113,0.06)' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'sync' && (
        <div>
          <h2 className="text-sm mb-4" style={{ fontWeight: 590, color: '#f7f8f8' }}>
            {d.syncCodeTitle || (lang === 'zh' ? '换电脑 / 换 Agent' : 'Switch Device / Agent')}
          </h2>

          <div className="p-5 rounded-[8px] mb-4" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <p className="text-xs mb-4" style={{ color: '#8a8f98', lineHeight: 1.6 }}>
              {d.syncCodeDesc || (lang === 'zh'
                ? '复制这段同步码，发给新 Agent，即可恢复你的全部记忆和 Persona。'
                : 'Copy this code and send it to your new Agent to restore all memories and personas.')}
            </p>

            {syncCode ? (
              <>
                <div className="flex items-center gap-2 mb-3">
                  <code className="flex-1 text-sm py-2.5 px-4 rounded-[6px]" style={{
                    background: 'rgba(113,112,255,0.08)', color: '#7170ff',
                    fontFamily: 'monospace', wordBreak: 'break-all', fontWeight: 510,
                  }}>{syncCode}</code>
                  <button onClick={copySyncCode}
                    className="p-2 rounded-[6px] transition-all"
                    style={{ color: syncCopied ? '#22c55e' : '#8a8f98', background: syncCopied ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.04)' }}>
                    {syncCopied ? <Check size={18} /> : <Copy size={18} />}
                  </button>
                </div>
                <p className="text-xs" style={{ color: '#fbbf24' }}>
                  ⚠️ {d.syncCodeWarning || (lang === 'zh' ? '一次性使用，用后自动失效。' : 'One-time use. Invalid after use.')}
                </p>
              </>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: '#8a8f98' }}>
                {d.syncCodeEmpty || (lang === 'zh' ? '点击下方按钮生成同步码' : 'Click the button below to generate a sync code')}
              </p>
            )}
          </div>

          <button onClick={generateSyncCode} disabled={syncLoading}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
            {syncLoading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
            {syncCode ? (d.syncCodeRegenerate || (lang === 'zh' ? '重新生成' : 'Regenerate')) : (d.syncCodeGenerate || (lang === 'zh' ? '生成同步码' : 'Generate Sync Code'))}
          </button>

          <p className="text-xs mt-3 text-center" style={{ color: '#62666d' }}>
            {d.syncCodeGenerating || (lang === 'zh' ? '生成后请立即复制保存' : 'Copy and save immediately after generation')}
          </p>
        </div>
      )}
    </div>
  )
}
