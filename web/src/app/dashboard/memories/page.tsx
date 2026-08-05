'use client'

import { useEffect, useState, useCallback } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import { timeAgo } from '@/lib/timeago'
import { Loader2, Search, Plus, ChevronDown, Edit2, Save, X, Trash2, Archive, Clock, Tag, Layers, Sparkles } from 'lucide-react'

const CAT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  preference: { bg: 'bg-[rgba(250,204,21,0.08)]', text: 'text-[#eab308]', border: 'shadow-[0_0_0_1px_rgba(250,204,21,0.2)]' },
  decision: { bg: 'bg-[rgba(74,222,128,0.08)]', text: 'text-[#4ade80]', border: 'shadow-[0_0_0_1px_rgba(74,222,128,0.2)]' },
  fact: { bg: 'bg-[rgba(96,165,250,0.08)]', text: 'text-[#60a5fa]', border: 'shadow-[0_0_0_1px_rgba(96,165,250,0.2)]' },
  project: { bg: 'bg-[rgba(129,140,248,0.08)]', text: 'text-[#818cf8]', border: 'shadow-[0_0_0_1px_rgba(129,140,248,0.2)]' },
}

const DEMO_MEMORIES = [
  { id: 'demo-1', content: '用户偏好使用深色主题，所有界面保持暗色设计', category: 'preference', source: 'demo', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 'demo-2', content: '用户对性能敏感，API 响应时间需控制在 200ms 以内', category: 'fact', source: 'demo', created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: 'demo-3', content: '决定采用 Next.js App Router 架构构建前端', category: 'decision', source: 'demo', created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: 'demo-4', content: '记忆管理模块是本项目核心功能，需要完善的搜索和分类', category: 'project', source: 'demo', created_at: new Date(Date.now() - 259200000).toISOString() },
  { id: 'demo-5', content: '用户希望 Persona 支持构建体和映射体两种类型', category: 'preference', source: 'demo', created_at: new Date(Date.now() - 345600000).toISOString() },
]

const PAGE_SIZE = 20

export default function MemoriesPage() {
  const { toast } = useToast()
  const { t, lang } = useLang()
  const d = t.dashboard_ui as any

  const CATEGORIES = [
    { value: '', label: d.category_all },
    { value: 'fact', label: d.category_fact },
    { value: 'preference', label: d.category_preference },
    { value: 'decision', label: d.category_decision },
    { value: 'project', label: d.category_project },
  ]

  const [memories, setMemories] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [isDemo, setIsDemo] = useState(false)
  const [newContent, setNewContent] = useState('')
  const [newCategory, setNewCategory] = useState('fact')
  const [adding, setAdding] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [timeDecay, setTimeDecay] = useState(false)
  const [showConsolidate, setShowConsolidate] = useState(false)
  const [duplicateGroups, setDuplicateGroups] = useState<any[]>([])
  const [dupLoading, setDupLoading] = useState(false)
  const [selectedForConsolidation, setSelectedForConsolidation] = useState<Set<string>>(new Set())
  const [consolidating, setConsolidating] = useState(false)
  const [consolidateStrategy, setConsolidateStrategy] = useState('merge')

  const showDemoToast = () => toast(lang === 'zh' ? '演示模式下不可用 — 注册后开始使用' : 'Not available in demo — sign up to get started', 'info')

  const fetchMemories = useCallback(async (query?: string, cat?: string, off?: number, append = false) => {
    setLoading(true)
    try {
      let url = `/api/memories?limit=${PAGE_SIZE}`
      if (cat) url += `&category=${cat}`
      if (off) url += `&offset=${off}`
      if (query) {
        url = `/api/memories/search?q=${encodeURIComponent(query)}&top_k=${PAGE_SIZE}`
        if (timeDecay) url += '&time_decay=true'
        const data = await apiFetch<{ results: any[] }>(url)
        const results = data.results || data
        setMemories(Array.isArray(results) ? results : [])
        setHasMore(false)
      } else {
        const data = await apiFetch<any[]>(url)
        const list = Array.isArray(data) ? data : []
        if (append) { setMemories(prev => [...prev, ...list]) } else { setMemories(list) }
        setHasMore(list.length >= PAGE_SIZE)
      }
    } catch (err: any) {
      setIsDemo(true)
      setMemories(DEMO_MEMORIES)
      setHasMore(false)
    } finally { setLoading(false) }
  }, [toast, timeDecay])

  useEffect(() => { fetchMemories() }, [])

  const handleSearch = () => {
    if (isDemo) { showDemoToast(); return }
    setOffset(0); fetchMemories(search || undefined, category)
  }
  const handleLoadMore = () => {
    if (isDemo) { showDemoToast(); return }
    const newOff = offset + PAGE_SIZE; setOffset(newOff)
    fetchMemories(search || undefined, category, newOff, true)
  }

  // ── Duplicate Detection ──────────────────────────
  const fetchDuplicates = async () => {
    if (isDemo) { showDemoToast(); return }
    setDupLoading(true)
    try {
      const data = await apiFetch<{ groups: any[] }>('/api/memories/duplicates')
      setDuplicateGroups(data.groups || [])
      setShowConsolidate(true)
    } catch (err: any) {
      toast(err?.message || 'Failed to check duplicates', 'error')
    } finally { setDupLoading(false) }
  }

  const toggleConsolidationSelect = (id: string) => {
    setSelectedForConsolidation(prev => {
      const next = new Set(prev)
      if (next.has(id)) { next.delete(id); } else { next.add(id); }
      return next
    })
  }

  const handleConsolidate = async () => {
    if (isDemo) { showDemoToast(); return }
    const ids = Array.from(selectedForConsolidation)
    if (ids.length < 2) { toast(d.dashboard_ui?.consolidateBtn?.replace('{count}', String(0)) || 'Need at least 2', 'error'); return }
    setConsolidating(true)
    try {
      const data = await apiFetch<{ consolidated: any; archived_count: number }>('/api/memories/consolidate', {
        method: 'POST',
        body: JSON.stringify({ memory_ids: ids, strategy: consolidateStrategy }),
      })
      toast(d.consolidateSuccess as string, 'success')
      setSelectedForConsolidation(new Set())
      setShowConsolidate(false)
      // Refresh memories
      setOffset(0)
      await fetchMemories(search || undefined, category)
    } catch (err: any) {
      toast(err?.message || (d.consolidateFailed as string), 'error')
    } finally { setConsolidating(false) }
  }
  const handleSave = async () => {
    if (isDemo) { showDemoToast(); return }
    if (!newContent.trim()) return
    setAdding(true)
    try {
      await apiFetch('/api/memories', {
        method: 'POST',
        body: JSON.stringify({ content: newContent.trim(), category: newCategory, source: 'manual' }),
      })
      toast(d.memoryCreated as string, 'success')
      setNewContent(''); setShowAddForm(false); setOffset(0)
      await fetchMemories(search || undefined, category)
    } catch (err: any) {
      toast(err?.message || 'Failed to create memory', 'error')
    } finally { setAdding(false) }
  }
  const handleDelete = async (id: string) => {
    if (isDemo) { showDemoToast(); return }
    try {
      await apiFetch(`/api/memories/${id}`, { method: 'DELETE' })
      toast(d.memoryDeleted as string, 'success')
      setMemories(prev => prev.filter(m => m.id !== id))
    } catch (err: any) {
      toast(err?.message || 'Failed to delete memory', 'error')
    }
  }
  const handleArchive = async (id: string) => {
    if (isDemo) { showDemoToast(); return }
    try {
      await apiFetch(`/api/memories/${id}/archive`, { method: 'POST' })
      toast(d.memoryArchived as string, 'success')
      setMemories(prev => prev.filter(m => m.id !== id))
    } catch (err: any) {
      toast(err?.message || 'Failed to archive memory', 'error')
    }
  }
  const startEdit = (m: any) => { if (isDemo) { showDemoToast(); return }; setEditingId(m.id); setEditContent(m.content) }
  const cancelEdit = () => { setEditingId(null); setEditContent('') }
  const saveEdit = async (id: string) => {
    if (isDemo) { showDemoToast(); return }
    if (!editContent.trim()) return
    try {
      await apiFetch(`/api/memories/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ content: editContent.trim() }),
      })
      toast(d.memoryUpdated as string, 'success')
      setMemories(prev => prev.map(m => m.id === id ? { ...m, content: editContent.trim() } : m))
      setEditingId(null)
    } catch (err: any) {
      toast(err?.message || 'Failed to update memory', 'error')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-heading tracking-[-0.3px] text-ln-text">{d.memoryMgmt}</h1>
          <p className="text-sm text-ln-tertiary font-body mt-1">{d.memoryDesc}</p>
        </div>
        <button onClick={() => { if (isDemo) { showDemoToast(); return }; setShowAddForm(!showAddForm) }}
          className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-sm font-ui transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover">
          <Plus size={15} /> {d.addMemory}
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ln-tertiary" />
            <input placeholder={d.searchMemory} value={search} onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()} aria-label={d.searchAria}
              className="w-full pl-9 pr-4 py-2 rounded-btn bg-ln-surface text-ln-text text-sm font-body shadow-border focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
          </div>
          <button onClick={handleSearch}
            className="px-4 py-2 rounded-btn text-sm font-ui bg-ln-btn-bg text-ln-secondary shadow-border transition-all duration-150 hover:bg-ln-hover">
            {d.searchBtn}
          </button>
        </div>
        <select value={category} onChange={e => { if (isDemo) { showDemoToast(); return }; setCategory(e.target.value); setOffset(0); fetchMemories(search || undefined, e.target.value) }}
          className="px-3 py-2 rounded-btn text-sm font-body bg-ln-surface text-ln-secondary shadow-border outline-none focus:shadow-border-accent transition-all">
          {CATEGORIES.map(c => (<option key={c.value} value={c.value}>{c.label}</option>))}
        </select>
      </div>

      {!isDemo && (<div className="flex items-center gap-3 mb-4">
        <label className="flex items-center gap-2 text-xs text-ln-tertiary font-ui cursor-pointer select-none">
          <input type="checkbox" checked={timeDecay} onChange={e => setTimeDecay(e.target.checked)}
            className="w-3.5 h-3.5 rounded border-ln-tertiary accent-ln-accent" />
          <Clock size={12} /> {d.timeDecayToggle}
        </label>
        <button onClick={fetchDuplicates} disabled={dupLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-btn text-xs font-ui bg-ln-btn-bg text-ln-secondary shadow-border transition-all duration-150 hover:bg-ln-hover disabled:opacity-50">
          {dupLoading ? <Loader2 size={11} className="animate-spin" /> : <Layers size={11} />}
          {d.consolidateTitle}
        </button>
      </div>)}

      {showConsolidate && (
        <div className="mb-6 p-5 rounded-card bg-ln-surface shadow-card animate-in">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-heading text-ln-text flex items-center gap-2">
                <Sparkles size={14} className="text-ln-accent" /> {d.consolidateTitle}
              </h3>
              <p className="text-xs text-ln-tertiary mt-1">
                {duplicateGroups.length > 0
                  ? `${duplicateGroups.length} ${d.duplicatesFound}`
                  : d.noDuplicates}
              </p>
            </div>
            <button onClick={() => { setShowConsolidate(false); setSelectedForConsolidation(new Set()) }}
              className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-secondary transition-colors">
              <X size={14} />
            </button>
          </div>

          {duplicateGroups.length > 0 && (
            <>
              <div className="flex items-center gap-3 mb-3">
                <label className="flex items-center gap-1.5 text-xs text-ln-tertiary font-ui">
                  {d.consolidateStrategy}:
                </label>
                <select value={consolidateStrategy} onChange={e => setConsolidateStrategy(e.target.value)}
                  className="px-2.5 py-1 rounded-btn text-xs font-body bg-ln-bg text-ln-secondary shadow-border-subtle outline-none">
                  <option value="merge">{d.consolidateMerge}</option>
                  <option value="summarize">{d.consolidateSummarize}</option>
                  <option value="deduplicate">{d.consolidateDeduplicate}</option>
                </select>
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto mb-3">
                {duplicateGroups.slice(0, 10).map((group, gi) => (
                  <div key={gi} className="p-3 rounded-btn bg-ln-bg border border-dashed border-ln-border/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-ln-accent font-ui">{group.count} {d.duplicatesFound}</span>
                      <span className="text-xs text-ln-tertiary">
                        {(group.avg_similarity * 100).toFixed(0)}% {d.matchPercent}
                      </span>
                    </div>
                    <div className="space-y-1.5">
                      {[group.representative, ...group.duplicates].map((m: any) => (
                        <label key={m.id}
                          className="flex items-start gap-2 px-2 py-1 rounded text-xs cursor-pointer hover:bg-ln-surface transition-colors">
                          <input type="checkbox"
                            checked={selectedForConsolidation.has(m.id)}
                            onChange={() => toggleConsolidationSelect(m.id)}
                            className="mt-0.5 w-3 h-3 rounded accent-ln-accent" />
                          <span className="text-ln-text leading-relaxed line-clamp-2">{m.content}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-ln-border/10">
                <button onClick={() => {
                  if (selectedForConsolidation.size === 0) {
                    const allIds = duplicateGroups.flatMap(g => [g.representative.id, ...g.duplicates.map((d: any) => d.id)])
                    setSelectedForConsolidation(new Set(allIds))
                  } else {
                    setSelectedForConsolidation(new Set())
                  }
                }} className="text-xs text-ln-accent hover:underline font-ui">
                  {d.selectAll}
                </button>
                <button onClick={handleConsolidate}
                  disabled={consolidating || selectedForConsolidation.size < 2}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150">
                  {consolidating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                  {consolidating ? d.consolidating : ((d.consolidateBtn as string).replace('{count}', String(selectedForConsolidation.size)))}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {showAddForm && (
        <div className="flex flex-col sm:flex-row gap-2 mb-6 p-4 rounded-card bg-ln-surface shadow-card animate-in">
          <input placeholder={d.newMemoryPlaceholder} value={newContent} onChange={e => setNewContent(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSave()} aria-label={d.newMemoryAria}
            className="flex-1 px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-subtle focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
          <div className="flex gap-2">
            <select value={newCategory} onChange={e => setNewCategory(e.target.value)}
              className="px-3 py-2 rounded-btn text-sm font-body bg-ln-bg text-ln-secondary shadow-border-subtle outline-none focus:shadow-border-accent">
              {CATEGORIES.filter(c => c.value).map(c => (<option key={c.value} value={c.value}>{c.label}</option>))}
            </select>
            <button onClick={handleSave} disabled={adding || !newContent.trim()}
              className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-sm font-ui disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover">
              {adding ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
              {isDemo ? d.demoMode : d.addBtn}
            </button>
            <button onClick={() => { setShowAddForm(false); setNewContent('') }}
              className="px-3 py-2 rounded-btn text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors">
              <X size={14} />
            </button>
          </div>
        </div>
      )}

      {isDemo && (
        <div className="mb-6 px-4 py-3 rounded-card bg-ln-accent-muted text-ln-accent-hover text-sm font-body shadow-border-accent animate-in">
          🔍 {d.memory_demo_notice}
        </div>
      )}

      {loading && memories.length === 0 ? (
        <div className="flex items-center justify-center py-20" aria-busy="true">
          <Loader2 className="w-6 h-6 animate-spin text-ln-accent" />
        </div>
      ) : memories.length === 0 ? (
        <div className="text-center py-20 rounded-card shadow-[0_0_0_1px_dashed_rgba(255,255,255,0.08)]">
          <div className="w-12 h-12 rounded-panel bg-ln-surface mx-auto mb-4 flex items-center justify-center">
            <Tag size={20} className="text-ln-tertiary" />
          </div>
          <p className="text-base mb-2 text-ln-text font-ui">{d.noMemories}</p>
          <p className="text-sm mb-6 text-ln-tertiary font-body">{d.noMemoriesDesc}</p>
          <button onClick={() => { if (!isDemo) setShowAddForm(true) }}
            className="inline-flex items-center gap-1.5 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150">
            <Plus size={15} /> {d.addFirstMemory}
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {memories.map((m: any) => {
            const isEditing = editingId === m.id
            const catColor = CAT_COLORS[m.category]
            return (
              <div key={m.id} className={`group p-4 rounded-card bg-ln-surface transition-all duration-200 ${isEditing ? 'shadow-accent-glow' : 'shadow-card hover:shadow-card-hover'}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className={`flex-shrink-0 w-1 h-full min-h-[3rem] rounded-full mt-0.5 ${
                    m.category === 'preference' ? 'bg-[#eab308]' : m.category === 'decision' ? 'bg-[#4ade80]' : m.category === 'fact' ? 'bg-[#60a5fa]' : m.category === 'project' ? 'bg-[#818cf8]' : 'bg-ln-tertiary'}`} />
                  <div className="flex-1 min-w-0">
                    {isEditing ? (
                      <div className="space-y-2">
                        <textarea value={editContent} onChange={e => setEditContent(e.target.value)} rows={3}
                          className="w-full px-3 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-accent outline-none resize-y animate-in" autoFocus />
                        <div className="flex gap-2">
                          <button onClick={() => saveEdit(m.id)}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-btn text-xs font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150">
                            <Save size={12} /> {d.saveBtn}</button>
                          <button onClick={cancelEdit}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-btn text-xs font-body bg-ln-btn-bg text-ln-secondary shadow-border hover:bg-ln-hover transition-all duration-150">
                            <X size={12} /> {d.cancelBtn}</button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm font-body text-ln-text leading-relaxed">{m.content}</p>
                        <div className="flex flex-wrap items-center gap-2 mt-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${catColor ? `${catColor.bg} ${catColor.text} ${catColor.border}` : 'bg-ln-btn-bg text-ln-tertiary shadow-border-subtle'}`}>
                            {m.category}</span>
                          {m.source && <span className="text-xs px-2 py-0.5 rounded-full bg-ln-btn-bg text-ln-tertiary shadow-border-subtle">{m.source}</span>}
                          {(m.similarity !== undefined) && <span className="text-xs px-2 py-0.5 rounded-full bg-ln-accent-muted text-ln-accent-hover shadow-border-accent">{Math.round(m.similarity * 100)}{d.matchPercent}</span>}
                          {(m.relevance !== undefined) && <span className="text-xs px-2 py-0.5 rounded-full bg-ln-accent-muted text-ln-accent-hover shadow-border-accent">{Math.round(m.relevance * 100)}{d.matchPercent}</span>}
                          <span className="text-xs flex items-center gap-1 ml-auto text-ln-tertiary font-body">
                            <Clock size={10} /> {m.created_at ? timeAgo(m.created_at) : ''}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                  {!isEditing && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                      <button onClick={() => startEdit(m)}
                        className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-accent-hover hover:bg-ln-accent-muted transition-all duration-150" aria-label={d.editAria}>
                        <Edit2 size={13} /></button>
                      <button onClick={() => { if (window.confirm(d.confirmArchive as string)) handleArchive(m.id) }}
                        className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-warning hover:bg-ln-warning/10 transition-all duration-150" aria-label={d.archiveMemory as string}>
                        <Archive size={13} /></button>
                      <button onClick={() => { if (window.confirm(d.deleteConfirm as string)) handleDelete(m.id) }}
                        className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-error hover:bg-ln-error/10 transition-all duration-150" aria-label={d.deleteAria}>
                        <Trash2 size={13} /></button>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
          {hasMore && (
            <div className="text-center pt-4 pb-8">
              <button onClick={handleLoadMore} disabled={loading}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-btn text-sm font-ui bg-ln-btn-bg text-ln-secondary shadow-border transition-all duration-150 hover:bg-ln-hover disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? <Loader2 size={14} className="animate-spin" /> : <ChevronDown size={14} />}
                {d.loadMore}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
