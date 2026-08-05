'use client'

import { useEffect, useState } from 'react'
import { useToast } from '@/contexts/ToastContext'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import { Loader2, Plus, ChevronDown, ChevronUp, Edit2, Trash2, X, Save, User, Users } from 'lucide-react'

const DEMO_PERSONAS = [
  { id: 'demo-p1', name: '战略顾问', description: '擅长宏观分析、战略规划和决策制定的 AI 人格，以结构化思维著称。', system_prompt: '你是一位经验丰富的战略顾问。分析问题时要考虑长远影响，提供结构化的建议。始终保持客观、理性。', type: 'constructed', traits: { 分析能力: 95, 战略思维: 90, 沟通: 85 }, created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: 'demo-p2', name: '创意伙伴', description: '富有创造力和想象力的 AI 人格，适合头脑风暴和创意写作。', system_prompt: '你是一位充满创意的合作伙伴。鼓励发散思维，大胆提出新颖想法。不要被常规思维限制。', type: 'constructed', traits: { 创造力: 98, 想象力: 92, 表达: 88 }, created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: 'demo-p3', name: '代码审查官', description: '严谨的代码审阅者，关注代码质量、安全性和最佳实践。', system_prompt: '你是一位资深代码审查官。严格检查代码质量、安全漏洞和性能问题。提出改进建议时要具体、可操作。', type: 'mirrored', traits: { 严谨: 96, 技术深度: 93, 耐心: 80 }, created_at: new Date(Date.now() - 259200000).toISOString() },
]

export default function PersonasPage() {
  const { toast } = useToast()
  const { t, lang } = useLang()
  const d = t.dashboard_ui as any
  const [personas, setPersonas] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', system_prompt: '', type: 'constructed' })
  const [creating, setCreating] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingPersona, setEditingPersona] = useState<any | null>(null)
  const [editForm, setEditForm] = useState({ name: '', description: '', system_prompt: '', type: 'constructed' })
  const [saving, setSaving] = useState(false)

  const showDemoToast = () => toast(lang === 'zh' ? '演示模式下不可用 — 注册后开始使用' : 'Not available in demo — sign up to get started', 'info')

  useEffect(() => { fetchPersonas() }, [])

  const fetchPersonas = async () => {
    setLoading(true)
    try { const data = await apiFetch<any[]>('/api/personas'); setPersonas(Array.isArray(data) ? data : []) }
    catch (err: any) { setPersonas([]); setIsDemo(false) }
    finally { setLoading(false) }
  }

  const handleCreate = async () => { showDemoToast() }
  const startEdit = (p: any) => { if (isDemo) { showDemoToast(); return }; setEditingPersona(p); setEditForm({ name: p.name, description: p.description || '', system_prompt: p.system_prompt || '', type: p.type }) }
  const handleUpdate = async () => { showDemoToast() }
  const handleDelete = async (id: string, name: string) => { showDemoToast() }
  const typeLabel = (tp: string) => tp === 'constructed' ? d.persona_type_constructed : d.persona_type_mirrored

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-2xl font-heading tracking-[-0.3px] text-ln-text">Persona</h1>
          <p className="text-sm text-ln-tertiary font-body mt-1">{d.personaPageTitle}</p>
        </div>
        <button onClick={() => { if (isDemo) { showDemoToast(); return }; setShowCreate(!showCreate) }}
          className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-sm font-ui transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover">
          <Plus size={15} /> {isDemo ? d.demoMode : d.createPersona}
        </button>
      </div>

      {isDemo && (
        <div className="mb-6 px-4 py-3 rounded-card bg-ln-accent-muted text-ln-accent-hover text-sm font-body shadow-border-accent animate-in">
          🔍 {d.persona_demo_notice}
        </div>
      )}

      {showCreate && (
        <div className="p-5 rounded-card bg-ln-surface shadow-card mb-8 space-y-3 animate-in">
          <input placeholder={d.personaNamePlaceholder} value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-subtle focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
          <input placeholder={d.personaBriefPlaceholder} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
            className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-subtle focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
          <textarea placeholder={d.personaSPromptPlaceholder} value={form.system_prompt} onChange={e => setForm({ ...form, system_prompt: e.target.value })} rows={4}
            className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body font-mono shadow-border-subtle focus:shadow-border-accent outline-none resize-y transition-all placeholder:text-ln-tertiary" />
          <select value={form.type} onChange={e => setForm({ ...form, type: e.target.value })}
            className="px-4 py-2 rounded-btn text-sm font-body bg-ln-bg text-ln-secondary shadow-border-subtle outline-none focus:shadow-border-accent">
            <option value="constructed">{d.persona_type_constructed}</option>
            <option value="mirrored">{d.persona_type_mirrored}</option>
          </select>
          <div className="flex gap-3">
            <button onClick={handleCreate} disabled={creating || !form.name.trim()}
              className="flex items-center gap-1.5 px-5 py-2 rounded-btn text-sm font-ui disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover">
              {creating ? <Loader2 size={14} className="animate-spin" /> : null} {d.addBtn}
            </button>
            <button onClick={() => setShowCreate(false)}
              className="px-5 py-2 rounded-btn text-sm font-body bg-ln-btn-bg text-ln-secondary shadow-border hover:bg-ln-hover transition-all duration-150">
              {d.cancelBtn}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin text-ln-accent" /></div>
      ) : personas.length === 0 ? (
        <div className="text-center py-20 rounded-card shadow-[0_0_0_1px_dashed_rgba(255,255,255,0.08)]">
          <div className="w-12 h-12 rounded-panel bg-ln-surface mx-auto mb-4 flex items-center justify-center"><Users size={20} className="text-ln-tertiary" /></div>
          <p className="text-base mb-2 text-ln-text font-ui">{d.noPersonasYet}</p>
          <p className="text-sm mb-6 text-ln-tertiary font-body">{d.noPersonasDesc}</p>
          <button onClick={() => { if (isDemo) { showDemoToast(); return }; setShowCreate(true) }}
            className="inline-flex items-center gap-1.5 px-5 py-2 rounded-btn text-sm font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150">
            <Plus size={15} /> {d.createFirstPersona}
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-3">
          {personas.map((p: any) => {
            const isExpanded = expandedId === p.id
            return (
              <div key={p.id} className="p-5 rounded-card bg-ln-surface shadow-card transition-all duration-200 hover:shadow-card-hover">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-btn bg-ln-accent-muted flex items-center justify-center flex-shrink-0"><User size={18} className="text-ln-accent" /></div>
                    <div className="min-w-0">
                      <h3 className="text-base font-ui text-ln-text truncate">{p.name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-ln-btn-bg text-ln-tertiary shadow-border-subtle font-body">{typeLabel(p.type)}</span>
                    </div>
                  </div>
                  <button onClick={() => setExpandedId(isExpanded ? null : p.id)}
                    className="flex-shrink-0 p-1 rounded-btn text-ln-tertiary hover:text-ln-text hover:bg-ln-hover transition-all duration-150"
                    aria-label={isExpanded ? d.collapseAria : d.expandAria}>
                    {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                  </button>
                </div>
                {p.description && <p className={`text-sm mb-3 text-ln-tertiary font-body ${isExpanded ? '' : 'line-clamp-2'}`}>{p.description}</p>}
                {p.traits && typeof p.traits === 'object' && Object.keys(p.traits).length > 0 && !isExpanded && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {Object.entries(p.traits).slice(0, 3).map(([k, v]) => (<span key={k} className="text-xs px-2 py-0.5 rounded-full bg-ln-btn-bg text-ln-tertiary shadow-border-subtle font-body">{k}: {String(v)}</span>))}
                    {Object.keys(p.traits).length > 3 && <span className="text-xs text-ln-tertiary font-body">+{Object.keys(p.traits).length - 3}</span>}
                  </div>
                )}
                {isExpanded && (
                  <div className="space-y-3 mt-3 pt-3 border-t border-ln-border animate-in">
                    {p.system_prompt && (
                      <div>
                        <p className="text-xs mb-1 text-ln-tertiary font-ui">System Prompt</p>
                        <pre className="text-xs rounded-card bg-ln-bg shadow-border p-3 overflow-x-auto max-h-48 leading-relaxed text-ln-secondary font-mono">{p.system_prompt}</pre>
                      </div>
                    )}
                    {p.traits && typeof p.traits === 'object' && Object.keys(p.traits).length > 0 && (
                      <div>
                        <p className="text-xs mb-1 text-ln-tertiary font-ui">Traits</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(p.traits).map(([k, v]) => (<span key={k} className="text-xs px-2 py-1 rounded-btn bg-ln-btn-bg text-ln-secondary shadow-border font-body">{k}: <span className="text-ln-text">{String(v)}</span></span>))}
                        </div>
                      </div>
                    )}
                    <div className="flex gap-2 pt-2">
                      <button onClick={() => startEdit(p)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-btn text-xs font-ui bg-ln-btn-bg text-ln-secondary shadow-border hover:bg-ln-hover transition-all duration-150">
                        <Edit2 size={11} /> {d.editAria}</button>
                      <button onClick={() => handleDelete(p.id, p.name)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-btn text-xs font-body text-ln-error bg-ln-error/10 shadow-[0_0_0_1px_rgba(248,113,113,0.2)] hover:bg-ln-error/20 transition-all duration-150">
                        <Trash2 size={11} /> {d.deleteAria}</button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {editingPersona && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 animate-in p-4" onClick={() => setEditingPersona(null)}>
          <div className="w-full max-w-lg p-6 rounded-panel bg-ln-surface shadow-card animate-in" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-heading text-ln-text">{d.editPersona}</h3>
              <button onClick={() => setEditingPersona(null)}
                className="p-1 rounded-btn text-ln-tertiary hover:text-ln-text hover:bg-ln-hover transition-all" aria-label={d.closeAria}>
                <X size={16} />
              </button>
            </div>
            <div className="space-y-3">
              <input placeholder={d.namePlaceholder} value={editForm.name} onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-subtle focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
              <input placeholder={d.personaBriefPlaceholder} value={editForm.description} onChange={e => setEditForm({ ...editForm, description: e.target.value })}
                className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body shadow-border-subtle focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary" />
              <textarea placeholder="System Prompt" value={editForm.system_prompt} onChange={e => setEditForm({ ...editForm, system_prompt: e.target.value })} rows={6}
                className="w-full px-4 py-2 rounded-btn bg-ln-bg text-ln-text text-sm font-body font-mono shadow-border-subtle focus:shadow-border-accent outline-none resize-y transition-all placeholder:text-ln-tertiary" />
              <select value={editForm.type} onChange={e => setEditForm({ ...editForm, type: e.target.value })}
                className="px-4 py-2 rounded-btn text-sm font-body bg-ln-bg text-ln-secondary shadow-border-subtle outline-none focus:shadow-border-accent">
                <option value="constructed">{d.persona_type_constructed}</option>
                <option value="mirrored">{d.persona_type_mirrored}</option>
              </select>
              <div className="flex gap-2 pt-2">
                <button onClick={handleUpdate} disabled={saving}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-btn text-xs font-ui disabled:opacity-50 transition-all duration-150 bg-ln-accent text-white hover:bg-ln-accent-hover">
                  {saving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />} {d.saveBtn}</button>
                <button onClick={() => setEditingPersona(null)}
                  className="flex items-center gap-1 px-4 py-2 rounded-btn text-xs font-body bg-ln-btn-bg text-ln-secondary shadow-border hover:bg-ln-hover transition-all duration-150">
                  <X size={12} /> {d.cancelBtn}</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
