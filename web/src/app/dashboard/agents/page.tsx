'use client'

import { useEffect, useState, useCallback } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import { timeAgo } from '@/lib/timeago'
import { Loader2, Bot, ChevronDown, Trash2, History, RefreshCw, Terminal, Cpu, Sparkles } from 'lucide-react'

// agent_type → 头像颜色/图标，参考 Hermes-Bot-Mode 的 roster 视觉
const AGENT_STYLE: Record<string, { bg: string; text: string; label: string }> = {
  hermes: { bg: 'bg-[rgba(139,92,246,0.15)]', text: 'text-[#a78bfa]', label: 'Hermes' },
  claude: { bg: 'bg-[rgba(245,158,11,0.15)]', text: 'text-[#fbbf24]', label: 'Claude' },
  codex: { bg: 'bg-[rgba(34,211,238,0.15)]', text: 'text-[#22d3ee]', label: 'Codex' },
  openclaw: { bg: 'bg-[rgba(244,114,182,0.15)]', text: 'text-[#f472b6]', label: 'OpenClaw' },
}

interface Source {
  id: string
  agent_type: string
  name: string
  latest_version: number
  created_at?: string
}

interface Snapshot {
  version: number
  file_count: number
  created_at: string
}

interface SourceDetail extends Source {
  snapshots: Snapshot[]
}

export default function AgentsPage() {
  const { toast } = useToast()
  const { t, lang } = useLang()
  const d = t.dashboard_ui as any
  const isEn = lang === 'en'

  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [details, setDetails] = useState<Record<string, SourceDetail>>({})
  const [detailLoading, setDetailLoading] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const fetchSources = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiFetch<{ sources: Source[] }>('/api/backup/sources')
      setSources(Array.isArray(data.sources) ? data.sources : [])
    } catch {
      setSources([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSources()
  }, [fetchSources])

  const toggleDetail = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null)
      return
    }
    setExpandedId(id)
    if (!details[id]) {
      setDetailLoading(id)
      try {
        const detail = await apiFetch<SourceDetail>(`/api/backup/sources/${id}`)
        setDetails(prev => ({ ...prev, [id]: detail }))
      } catch {
        toast(d.agentViewDetails || '加载详情失败', 'error')
      } finally {
        setDetailLoading(null)
      }
    }
  }

  const handleDelete = async (id: string) => {
    const name = sources.find(s => s.id === id)?.name || ''
    if (!window.confirm(`${d.agentDeleteConfirm}\n\n${name}`)) return
    setDeletingId(id)
    try {
      await apiFetch(`/api/backup/sources/${id}`, { method: 'DELETE' })
      toast(d.agentDeleteSuccess, 'success')
      setSources(prev => prev.filter(s => s.id !== id))
      setDetails(prev => { const { [id]: _, ...rest } = prev; return rest })
      if (expandedId === id) setExpandedId(null)
    } catch {
      toast(d.agentDeleteFailed, 'error')
    } finally {
      setDeletingId(null)
    }
  }

  const agentLabel = (type: string) => {
    const key = (type || 'other').toLowerCase()
    if (AGENT_STYLE[key]) return isEn ? key.charAt(0).toUpperCase() + key.slice(1) : AGENT_STYLE[key].label
    return isEn ? 'Agent' : 'Agent'
  }
  const agentStyle = (type: string) => {
    return AGENT_STYLE[(type || 'other').toLowerCase()] || { bg: 'bg-[rgba(148,163,184,0.15)]', text: 'text-[#94a3b8]' }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* 头部 */}
      <div className="mb-6">
        <h1 className="text-xl font-heading tracking-[-0.3px] text-ln-text mb-1 flex items-center gap-2">
          <Bot size={20} className="text-ln-accent" />
          {d.agentsTitle}
        </h1>
        <p className="text-sm text-ln-tertiary font-body">{d.agentsDesc}</p>
      </div>

      {/* 刷新按钮 */}
      <div className="flex justify-end mb-4">
        <button
          onClick={fetchSources}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-btn border border-ln-border text-ln-tertiary hover:text-ln-secondary transition-colors"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          {d.agentRefresh}
        </button>
      </div>

      {/* 加载中 */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-6 h-6 animate-spin text-ln-accent" />
        </div>
      ) : sources.length === 0 ? (
        /* 空状态 */
        <div className="text-center py-16 rounded-xl border border-dashed border-ln-border">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-base font-ui text-ln-text mb-2">{d.agentsEmpty}</h3>
          <p className="text-sm text-ln-tertiary font-body mb-6 max-w-sm mx-auto">{d.agentsEmptyDesc}</p>
          <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-btn bg-ln-raised border border-ln-border font-mono text-xs text-ln-accent-hover">
            <Terminal size={14} />
            {d.agentsInstallCmd}
          </div>
          <div className="mt-4">
            <a href="/docs" className="text-xs text-ln-accent hover:text-ln-accent-hover font-ui">
              {d.agentsInstallBtn} →
            </a>
          </div>
        </div>
      ) : (
        /* Agent 花名册 */
        <div className="space-y-3">
          {sources.map(src => {
            const style = agentStyle(src.agent_type)
            const detail = details[src.id]
            const isExpanded = expandedId === src.id
            return (
              <div
                key={src.id}
                className="rounded-card border border-ln-border bg-ln-surface overflow-hidden transition-all"
              >
                {/* 主行 */}
                <div className="flex items-center gap-4 px-4 py-3.5">
                  {/* 头像 */}
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${style.bg} ${style.text}`}>
                    <Cpu size={18} />
                  </div>
                  {/* 名称 + 类型 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-ui text-ln-text text-sm truncate">{src.name}</span>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
                        {agentLabel(src.agent_type)}
                      </span>
                    </div>
                    <div className="text-xs text-ln-tertiary font-body mt-0.5">
                      {d.agentLatestVersion}: v{src.latest_version || 0}
                      {src.created_at && <> · {timeAgo(src.created_at)}</>}
                    </div>
                  </div>
                  {/* 操作 */}
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => toggleDetail(src.id)}
                      className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-btn text-ln-tertiary hover:text-ln-text hover:bg-ln-hover transition-colors"
                      aria-label={d.agentVersionHistory}
                    >
                      <History size={14} />
                      <ChevronDown size={13} className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                    </button>
                    <button
                      onClick={() => handleDelete(src.id)}
                      disabled={deletingId === src.id}
                      className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-error hover:bg-ln-error/10 transition-colors disabled:opacity-50"
                      aria-label={d.agentDelete}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>

                {/* 版本历史（展开） */}
                {isExpanded && (
                  <div className="border-t border-ln-border px-4 py-3 bg-ln-bg/40">
                    {detailLoading === src.id ? (
                      <div className="flex justify-center py-4">
                        <Loader2 className="w-4 h-4 animate-spin text-ln-accent" />
                      </div>
                    ) : detail && detail.snapshots && detail.snapshots.length > 0 ? (
                      <div className="space-y-1.5">
                        <div className="text-xs font-ui text-ln-secondary mb-2 flex items-center gap-1.5">
                          <Sparkles size={13} className="text-ln-accent" />
                          {d.agentVersionHistory}
                        </div>
                        {detail.snapshots.map(snap => (
                          <div key={snap.version} className="flex items-center gap-3 text-xs py-1.5 px-2 rounded-btn hover:bg-ln-hover">
                            <span className="font-mono text-ln-accent-hover">v{snap.version}</span>
                            <span className="text-ln-tertiary font-body">{d.agentFileCount}: {snap.file_count}</span>
                            <span className="text-ln-tertiary font-body ml-auto">{timeAgo(snap.created_at)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-ln-tertiary font-body py-2 text-center">{d.agentNoVersions}</div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
