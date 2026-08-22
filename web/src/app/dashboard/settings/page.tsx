'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch, createCheckout, createPortal, getSubscription } from '@/lib/api'
import { Loader2, Key, Copy, Check, Trash2, Shield, Plus, Eye, EyeOff, Brain, Crown, ArrowUp, RefreshCw, CreditCard } from 'lucide-react'

interface ApiKey { id: string; name: string; key_prefix: string; created_at: string; last_used_at?: string; is_active: boolean }
interface UsageStats { backup_sources: { used: number; limit: number }; storage_gb: { used: number; limit: number }; memories: { used: number; limit: number }; personas: { used: number; limit: number }; agents: { used: number; limit: number }; identities: { used: number; limit: number }; api_keys: { used: number; limit: number } }
interface UserProfile { id: string; email: string; name: string; plan: string; plan_name: string; created_at: string; usage?: { plan: string; plan_name: string; usage: UsageStats } }

const PLAN_COLORS: Record<string, string> = { free: '#888888', pro: '#4338CA', team: '#22c55e' }

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
  const [error, setError] = useState(false)
  const [upgrading, setUpgrading] = useState(false)
  const [activeTab, setActiveTab] = useState<'profile' | 'keys' | 'sync' | 'billing'>('profile')
  const [sub, setSub] = useState<{ plan: string; plan_name?: string; status?: string } | null>(null)
  const [subLoading, setSubLoading] = useState(false)
  const [managing, setManaging] = useState(false)
  const [syncCode, setSyncCode] = useState<string | null>(null)
  const [syncCopied, setSyncCopied] = useState(false)
  const [syncLoading, setSyncLoading] = useState(false)
  const [restoreCode, setRestoreCode] = useState('')
  const [restoreLoading, setRestoreLoading] = useState(false)
  const [restoreKey, setRestoreKey] = useState<string | null>(null)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<any>('/api/auth/me')
      setUser(data)
      try { const keys = await apiFetch<ApiKey[]>('/api/auth/api-keys'); setApiKeys(Array.isArray(keys) ? keys : []) }
      catch { setApiKeys([]) }
    } catch (err: any) { setError(true); setApiKeys([]) }
    finally { setLoading(false) }
  }

  const handleCreateKey = async () => {
    setCreating(true)
    try {
      const name = newKeyName.trim() || `Key ${apiKeys.length + 1}`
      const data = await apiFetch<{ key: string; name: string }>('/api/auth/api-keys', {
        method: 'POST',
        body: JSON.stringify({ name }),
      })
      setNewKey(data.key)
      setNewKeyName('')
      // Reload key list
      const keys = await apiFetch<ApiKey[]>('/api/auth/api-keys')
      setApiKeys(Array.isArray(keys) ? keys : [])
      toast(lang === 'zh' ? '密钥已创建' : 'Key created', 'success')
    } catch (err: any) {
      toast(err.message || (lang === 'zh' ? '创建失败' : 'Creation failed'), 'error')
    }
    finally { setCreating(false) }
  }
  const handleRevokeKey = async (id: string, name: string) => {
    try {
      await apiFetch(`/api/auth/api-keys/${id}`, { method: 'DELETE' })
      setApiKeys(prev => prev.filter(k => k.id !== id))
      toast((lang === 'zh' ? '已吊销: ' : 'Revoked: ') + name, 'info')
    } catch (err: any) {
      toast(err.message || (lang === 'zh' ? '吊销失败' : 'Revoke failed'), 'error')
    }
  }
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

  const restoreFromSyncCode = async () => {
    if (!restoreCode.trim()) { toast(lang === 'zh' ? '请输入同步码' : 'Enter a sync code', 'error'); return }
    setRestoreLoading(true)
    try {
      const data = await apiFetch<{ api_key: string }>('/api/auth/sync', {
        method: 'POST',
        body: JSON.stringify({ sync_code: restoreCode.trim() }),
      })
      setRestoreKey(data.api_key)
      toast(lang === 'zh' ? '恢复成功' : 'Restored', 'success')
    } catch (err: any) {
      toast(err.message || (lang === 'zh' ? '恢复失败' : 'Restore failed'), 'error')
    } finally { setRestoreLoading(false) }
  }

  const handleUpgrade = async () => {
    setUpgrading(true)
    try { await createCheckout('pro', 'monthly') }
    catch (e: any) { toast(e.message || (lang === 'zh' ? '跳转支付失败，请重试' : 'Checkout failed, please retry'), 'error') }
    finally { setUpgrading(false) }
  }

  const loadSubscription = async () => {
    setSubLoading(true)
    try {
      const data = await getSubscription()
      setSub(data)
    } catch {
      setSub(null)
    } finally {
      setSubLoading(false)
    }
  }

  const handleManage = async () => {
    setManaging(true)
    try { await createPortal() }
    catch (e: any) { toast(e.message || (lang === 'zh' ? '跳转订阅管理失败' : 'Failed to open portal'), 'error') }
    finally { setManaging(false) }
  }

  const renderProgress = (label: string, used: number, limit: number, color: string) => {
    const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0
    const isNearLimit = pct >= 80
    return (
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1" style={{ color: '#cccccc' }}>
          <span>{label}</span>
          <span style={{ color: isNearLimit ? '#fbbf24' : '#888888' }}>{used} / {limit < 0 || limit >= 999999 ? '∞' : limit}</span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
          <div className="h-full rounded-full transition-all duration-300" style={{ width: `${pct}%`, background: isNearLimit ? '#fbbf24' : color }} />
        </div>
      </div>
    )
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><Loader2 className="w-6 h-6 animate-spin" style={{ color: '#4338CA' }} /></div>
  }

  const usage: UsageStats = user?.usage?.usage || { backup_sources: { used: 0, limit: 10 }, storage_gb: { used: 0, limit: 2 }, memories: { used: 0, limit: 100 }, personas: { used: 0, limit: 2 }, agents: { used: 0, limit: 1 }, identities: { used: 1, limit: 1 }, api_keys: { used: 0, limit: 10 } }
  const isFree = (user?.plan || 'free') === 'free'
  const planColor = PLAN_COLORS[user?.plan || 'free'] || '#888888'
  const proFeatures = [d.proFeature1, d.proFeature2, d.proFeature3, d.proFeature4, d.proFeature5, d.proFeature6]

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="text-xl mb-8" style={{ fontWeight: 590, color: '#ffffff' }}>{d.settingsPageTitle}</h1>

      <div className="flex gap-6 mb-8 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        {[
          { id: 'profile', label: d.tabProfile },
          { id: 'keys', label: d.tabAPIKeys },
          { id: 'sync', label: d.tabSync || (lang === 'zh' ? '同步码' : 'Sync') },
          { id: 'billing', label: d.tabBilling },
        ].map(tab => (
          <button key={tab.id} onClick={() => { setActiveTab(tab.id as any); if (tab.id === 'billing' && !sub) loadSubscription() }}
            className="pb-3 text-sm font-medium transition-all border-b-2"
            style={{ color: activeTab === tab.id ? '#ffffff' : '#888888', borderColor: activeTab === tab.id ? '#4338CA' : 'transparent', fontWeight: activeTab === tab.id ? 590 : 400 }}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <>
          <div className="p-5 rounded-[8px] mb-6" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: `${planColor}20` }}>
                  {isFree ? <Shield size={18} color={planColor} /> : <Crown size={18} color={planColor} />}
                </div>
                <div>
                  <p className="text-sm" style={{ fontWeight: 590, color: '#ffffff' }}>{user?.plan_name || d.freePlan}</p>
                  <p className="text-xs" style={{ color: '#888888' }}>{isFree ? d.onTrial : d.proPlan}</p>
                </div>
              </div>
              {isFree && (
                <button onClick={handleUpgrade} disabled={upgrading}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-[6px] text-xs font-medium transition-all hover:opacity-90"
                  style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                  <ArrowUp size={14} /> {upgrading ? d.upgrading : d.upgradePro}
                </button>
              )}
            </div>
            <div className="space-y-0.5">
              {renderProgress(d.usage_backup_sources, usage.backup_sources.used, usage.backup_sources.limit, planColor)}
              {renderProgress(d.usage_storage, usage.storage_gb.used, usage.storage_gb.limit, planColor)}
            </div>
          </div>

          {isFree && (
            <div className="p-5 rounded-[8px] mb-6" style={{ background: 'rgba(67,56,202,0.04)', boxShadow: '0 0 0 1px rgba(67,56,202,0.15)' }}>
              <h3 className="text-sm mb-3" style={{ fontWeight: 590, color: '#4338CA' }}>{d.proUnlock}</h3>
              <div className="grid grid-cols-2 gap-2 text-xs" style={{ color: '#cccccc' }}>
                {proFeatures.map((f: string, i: number) => (<div key={i} className="flex items-center gap-2"><Check size={12} style={{ color: '#4338CA' }} />{f}</div>))}
              </div>
              <button onClick={handleUpgrade} disabled={upgrading}
                className="w-full mt-4 py-2 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
                style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                {upgrading ? d.upgrading : d.y149year}
              </button>
            </div>
          )}

          <div className="p-5 rounded-[8px]" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <h3 className="text-sm mb-4" style={{ fontWeight: 590, color: '#ffffff' }}>{d.basicInfo}</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span style={{ color: '#888888' }}>{d.email}</span><span style={{ color: '#ffffff' }}>{user?.email || '—'}</span></div>
              <div className="flex justify-between"><span style={{ color: '#888888' }}>{d.nickname}</span><span style={{ color: '#ffffff' }}>{user?.name || '—'}</span></div>
              <div className="flex justify-between"><span style={{ color: '#888888' }}>{d.registeredAt}</span><span style={{ color: '#ffffff' }}>{user?.created_at?.split('T')[0] || '—'}</span></div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'keys' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm" style={{ fontWeight: 590, color: '#ffffff' }}>API {lang === 'zh' ? '密钥' : 'Keys'}</h2>
            <button onClick={handleCreateKey} disabled={creating}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] text-xs font-medium transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
              <Plus size={14} /> {d.createKey}
            </button>
          </div>

          {newKey && (
            <div className="p-4 rounded-[8px] mb-4" style={{ background: 'rgba(34,197,94,0.08)', boxShadow: '0 0 0 1px rgba(34,197,94,0.2)' }}>
              <p className="text-xs mb-2" style={{ color: '#22c55e', fontWeight: 590 }}>{d.newKeyCreated}</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs py-2 px-3 rounded-[4px]" style={{ background: 'rgba(255,255,255,0.04)', color: '#ffffff', wordBreak: 'break-all' }}>{newKey}</code>
                <button onClick={copyNewKey} className="p-2 rounded-[4px] transition-all" style={{ color: copied ? '#22c55e' : '#888888' }}>{copied ? <Check size={16} /> : <Copy size={16} />}</button>
              </div>
            </div>
          )}

          {apiKeys.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: '#888888' }}>{error ? (lang === 'zh' ? '加载失败，请重试' : 'Failed to load, please retry') : d.noKeysYet}</p>
          ) : (
            <div className="space-y-2">
              {apiKeys.map(key => (
                <div key={key.id} className="flex items-center justify-between p-3 rounded-[6px]" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
                  <div>
                    <p className="text-sm" style={{ fontWeight: 510, color: '#ffffff' }}>{key.name}</p>
                    <p className="text-xs mt-0.5" style={{ color: '#888888', fontFamily: 'monospace' }}>{key.key_prefix}*** · {key.created_at?.split('T')[0] || '—'}</p>
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
          <h2 className="text-sm mb-4" style={{ fontWeight: 590, color: '#ffffff' }}>
            {d.syncCodeTitle || (lang === 'zh' ? '换电脑 / 换 Agent' : 'Switch Device / Agent')}
          </h2>

          <div className="p-5 rounded-[8px] mb-4" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <p className="text-xs mb-4" style={{ color: '#888888', lineHeight: 1.6 }}>
              {d.syncCodeDesc || (lang === 'zh'
                ? '复制这段同步码，发给新 Agent，即可恢复你的全部记忆和 Persona。'
                : 'Copy this code and send it to your new Agent to restore all memories and personas.')}
            </p>

            {syncCode ? (
              <>
                <div className="flex items-center gap-2 mb-3">
                  <code className="flex-1 text-sm py-2.5 px-4 rounded-[6px]" style={{
                    background: 'rgba(67,56,202,0.08)', color: '#4338CA',
                    fontFamily: 'monospace', wordBreak: 'break-all', fontWeight: 510,
                  }}>{syncCode}</code>
                  <button onClick={copySyncCode}
                    className="p-2 rounded-[6px] transition-all"
                    style={{ color: syncCopied ? '#22c55e' : '#888888', background: syncCopied ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.04)' }}>
                    {syncCopied ? <Check size={18} /> : <Copy size={18} />}
                  </button>
                </div>
                <p className="text-xs" style={{ color: '#fbbf24' }}>
                  ⚠️ {d.syncCodeWarning || (lang === 'zh' ? '一次性使用，用后自动失效。' : 'One-time use. Invalid after use.')}
                </p>
              </>
            ) : (
              <p className="text-sm text-center py-4" style={{ color: '#888888' }}>
                {d.syncCodeEmpty || (lang === 'zh' ? '点击下方按钮生成同步码' : 'Click the button below to generate a sync code')}
              </p>
            )}
          </div>

          <button onClick={generateSyncCode} disabled={syncLoading}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50"
            style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
            {syncLoading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
            {syncCode ? (d.syncCodeRegenerate || (lang === 'zh' ? '重新生成' : 'Regenerate')) : (d.syncCodeGenerate || (lang === 'zh' ? '生成同步码' : 'Generate Sync Code'))}
          </button>

          <div className="p-5 rounded-[8px] mt-5" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
            <h3 className="text-sm mb-2" style={{ fontWeight: 590, color: '#ffffff' }}>从同步码恢复</h3>
            <p className="text-xs mb-3" style={{ color: '#888888', lineHeight: 1.6 }}>新电脑 / 新 Agent?输入同步码,恢复全部记忆与身份。</p>
            <div className="flex gap-2 mb-3">
              <input value={restoreCode} onChange={(e) => setRestoreCode(e.target.value)}
                placeholder="molt_sync_xxx"
                className="flex-1 text-sm py-2.5 px-4 rounded-[6px]"
                style={{ background: 'rgba(255,255,255,0.04)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)', fontFamily: 'monospace', outline: 'none' }} />
              <button onClick={restoreFromSyncCode} disabled={restoreLoading}
                className="px-4 py-2 rounded-[6px] text-xs font-medium transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                {restoreLoading ? <Loader2 size={16} className="animate-spin" /> : (lang === 'zh' ? '恢复' : 'Restore')}
              </button>
            </div>
            {restoreKey && (
              <div className="p-3 rounded-[6px]" style={{ background: 'rgba(34,197,94,0.08)' }}>
                <p className="text-xs mb-1" style={{ color: '#22c55e' }}>✅ 恢复成功,你的新 API Key:</p>
                <code className="block text-sm py-2 px-3 rounded-[4px]" style={{ background: 'rgba(0,0,0,0.3)', color: '#22c55e', fontFamily: 'monospace', wordBreak: 'break-all' }}>{restoreKey}</code>
                <p className="text-xs mt-1" style={{ color: '#888888' }}>请复制保存,之后用它重新接入。</p>
              </div>
            )}
          </div>

          <p className="text-xs mt-3 text-center" style={{ color: '#62666d' }}>
            {d.syncCodeGenerating || (lang === 'zh' ? '生成后请立即复制保存' : 'Copy and save immediately after generation')}
          </p>
        </div>
      )}

      {activeTab === 'billing' && (
        <div>
          <h2 className="text-sm mb-4" style={{ fontWeight: 590, color: '#ffffff' }}>{d.tabBilling}</h2>

          {subLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-6 h-6 animate-spin" style={{ color: '#4338CA' }} />
            </div>
          ) : (
            <>
              {/* 当前计划卡片 */}
              <div className="p-5 rounded-[8px] mb-4" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: `${planColor}20` }}>
                      {isFree ? <Shield size={18} color={planColor} /> : <Crown size={18} color={planColor} />}
                    </div>
                    <div>
                      <p className="text-sm" style={{ fontWeight: 590, color: '#ffffff' }}>
                        {isFree ? d.subscriptionFree : (sub?.plan === 'team' ? d.subscriptionTeam : d.subscriptionPro)}
                      </p>
                      <p className="text-xs" style={{ color: '#888888' }}>
                        {isFree
                          ? d.subscriptionUpgradeDesc
                          : (sub?.status === 'trialing' ? d.trialActive : d.proPlan)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* 操作按钮 */}
              {isFree ? (
                <button onClick={handleUpgrade} disabled={upgrading}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50"
                  style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                  {upgrading ? <Loader2 size={16} className="animate-spin" /> : <ArrowUp size={16} />}
                  {upgrading ? d.upgrading : d.upgradePro}
                </button>
              ) : (
                <>
                  <button onClick={handleManage} disabled={managing}
                    className="w-full flex items-center justify-center gap-2 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90 disabled:opacity-50"
                    style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                    {managing ? <Loader2 size={16} className="animate-spin" /> : <CreditCard size={16} />}
                    {d.subscriptionManage}
                  </button>
                  <p className="text-xs mt-3 text-center" style={{ color: '#888888', lineHeight: 1.6 }}>
                    {d.subscriptionManageDesc}
                  </p>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
