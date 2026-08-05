'use client'

import { useEffect, useState, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'
import { Copy, Check, Twitter, Download, Loader2 } from 'lucide-react'
import { Suspense } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

function ShareCard() {
  const { t, lang } = useLang()
  const searchParams = useSearchParams()
  const key = searchParams.get('key') || ''
  const [stats, setStats] = useState({ memories: 0, personas: 0, agents: 0, projects: 0 })
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [imageUrl, setImageUrl] = useState('')
  const [imageLoading, setImageLoading] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    if (!key) return
    loadStats()
  }, [key])

  const loadStats = async () => {
    try {
      const [mem, pers, prov] = await Promise.all([
        apiFetch<{ total: number }>('/api/memories/stats', { headers: { 'X-API-Key': key } }).catch(() => ({ total: 0 })),
        apiFetch<any[]>('/api/personas', { headers: { 'X-API-Key': key } }).catch(() => []),
        apiFetch<any>(`/api/agents/auto_provision`, {
          method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'auto_provision', params: {} }),
          headers: { 'X-API-Key': key }
        }).catch(() => ({})),
      ])
      const provision = prov?.result || prov || {}
      setStats({
        memories: mem?.total || 0,
        personas: Array.isArray(pers) ? pers.length : 0,
        agents: provision?.memory_count || provision?.available_personas?.length || 0,
        projects: provision?.active_projects?.length || 0,
      })
    } catch { /* fallback to demo stats */ }
    setLoading(false)
  }

  // Generate share image via canvas
  const generateImage = () => {
    setImageLoading(true)
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = 1200
    canvas.height = 630

    // Background
    const bg = ctx.createLinearGradient(0, 0, 1200, 630)
    bg.addColorStop(0, '#0D0D14')
    bg.addColorStop(1, '#14141E')
    ctx.fillStyle = bg
    ctx.fillRect(0, 0, 1200, 630)

    // Green accent border
    ctx.strokeStyle = '#4338CA'
    ctx.lineWidth = 3
    ctx.strokeRect(20, 20, 1160, 590)

    // Logo area
    ctx.fillStyle = '#4338CA'
    ctx.font = 'bold 48px Geist, system-ui, sans-serif'
    ctx.fillText('Moltable', 80, 120)

    // Tagline
    ctx.fillStyle = '#888888'
    ctx.font = '28px Inter, system-ui, sans-serif'
    ctx.fillText(lang === 'zh' ? 'AI 身份同步 · 让 AI 认识你' : 'AI Identity Sync · Your AI Knows You', 80, 170)

    // Stats grid
    const statsData = [
      { label: lang === 'zh' ? '记忆' : 'Memories', value: stats.memories },
      { label: lang === 'zh' ? '人格' : 'Personas', value: stats.personas },
      { label: lang === 'zh' ? 'Agent' : 'Agents', value: stats.agents },
      { label: lang === 'zh' ? '项目' : 'Projects', value: stats.projects },
    ]

    const startX = 80
    const startY = 260
    const boxW = 240
    const boxH = 180
    const gap = 30

    statsData.forEach((s, i) => {
      const x = startX + i * (boxW + gap)
      const y = startY

      // Box
      ctx.fillStyle = 'rgba(67,56,202,0.08)'
      ctx.fillRect(x, y, boxW, boxH)
      ctx.strokeStyle = 'rgba(67,56,202,0.2)'
      ctx.lineWidth = 1
      ctx.strokeRect(x, y, boxW, boxH)

      // Value
      ctx.fillStyle = '#ffffff'
      ctx.font = 'bold 56px Inter, system-ui, sans-serif'
      ctx.fillText(String(s.value), x + boxW / 2 - 20, y + 80)

      // Label
      ctx.fillStyle = '#888888'
      ctx.font = '20px Inter, system-ui, sans-serif'
      ctx.fillText(s.label, x + boxW / 2 - 20, y + 130)
    })

    // Footer
    ctx.fillStyle = '#5a5f68'
    ctx.font = '18px Inter, system-ui, sans-serif'
    ctx.fillText('moltable.ai', 80, 560)

    const url = canvas.toDataURL('image/png')
    setImageUrl(url)
    setImageLoading(false)
  }

  const shareText = `My AIs now share memories across platforms.\n🧠 ${stats.memories} memories · ${stats.personas} personas · ${stats.agents} agents\n\nmoltable.ai`

  const handleCopy = () => {
    navigator.clipboard.writeText(shareText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleTweet = () => {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`)
  }

  const handleDownload = () => {
    if (!imageUrl) return
    const a = document.createElement('a')
    a.href = imageUrl
    a.download = 'moltable-share.png'
    a.click()
  }

  if (!key) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0D0D14', color: '#ffffff' }}>
        <p style={{ color: '#888888' }}>{lang === 'zh' ? '需要 API Key 才能生成分享卡片' : 'API Key required to generate share card'}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{ background: '#0D0D14', color: '#ffffff' }}>
      <div className="max-w-2xl mx-auto px-6 pt-20 pb-24">
        <h1 className="text-2xl mb-2" style={{ fontWeight: 590 }}>
          {lang === 'zh' ? '🔥 分享你的 Moltable' : '🔥 Share Your Moltable'}
        </h1>
        <p className="text-sm mb-8" style={{ color: '#888888' }}>
          {lang === 'zh' ? '炫耀你的 AI 同步成果' : 'Show off your AI sync setup'}
        </p>

        {loading ? (
          <div className="flex items-center gap-2" style={{ color: '#888888' }}>
            <Loader2 size={16} className="animate-spin" />
            {lang === 'zh' ? '加载中...' : 'Loading...'}
          </div>
        ) : (
          <>
            {/* Share preview card */}
            <div className="mb-8 p-6 rounded-xl" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                  { label: lang === 'zh' ? '记忆' : 'Memories', value: stats.memories },
                  { label: lang === 'zh' ? '人格' : 'Personas', value: stats.personas },
                  { label: lang === 'zh' ? 'Agent' : 'Agents', value: stats.agents },
                  { label: lang === 'zh' ? '项目' : 'Projects', value: stats.projects },
                ].map((s, i) => (
                  <div key={i} className="text-center p-3 rounded-lg" style={{ background: 'rgba(67,56,202,0.06)' }}>
                    <div className="text-lg mb-1" style={{ fontWeight: 590, color: '#4338CA' }}>{s.value}</div>
                    <div className="text-xs" style={{ color: '#888888' }}>{s.label}</div>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-lg text-sm font-mono" style={{ background: '#0D0D14', color: '#cccccc', lineHeight: 1.6 }}>
                {shareText.split('\n').map((line, i) => (
                  <div key={i}>{line}</div>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex flex-wrap gap-3">
              <button onClick={handleCopy}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm transition-all"
                style={{ background: copied ? '#34d399' : '#4338CA', color: '#fff', fontWeight: 510 }}>
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? (lang === 'zh' ? '已复制' : 'Copied') : (lang === 'zh' ? '复制文案' : 'Copy Text')}
              </button>
              <button onClick={handleTweet}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm transition-all"
                style={{ background: 'rgba(255,255,255,0.06)', color: '#ffffff', fontWeight: 510 }}>
                <Twitter size={16} />
                {lang === 'zh' ? '发推文' : 'Tweet'}
              </button>
              <button onClick={() => generateImage()}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm transition-all"
                style={{ background: 'rgba(255,255,255,0.06)', color: '#ffffff', fontWeight: 510 }}>
                {imageLoading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
                {lang === 'zh' ? '生成图片' : 'Generate Image'}
              </button>
            </div>

            {/* Generated image preview */}
            {imageUrl && (
              <div className="mt-8">
                <img ref={imgRef} src={imageUrl} alt="Share card" className="w-full rounded-lg" style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.5)' }} />
                <button onClick={handleDownload}
                  className="mt-4 w-full py-2.5 rounded-lg text-sm transition-all"
                  style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
                  <Download size={16} className="inline mr-2" />
                  {lang === 'zh' ? '下载图片' : 'Download Image'}
                </button>
              </div>
            )}
          </>
        )}

        {/* Hidden canvas for image generation */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  )
}

export default function SharePage() {
  return <Suspense fallback={<div />}><ShareCard /></Suspense>
}
