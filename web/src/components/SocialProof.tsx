'use client'

import { useEffect, useState } from 'react'
import { Star, Users, Mail } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

interface SocialStats {
  githubStars: number | null
  subscribers: number | null
}

/**
 * Social proof bar — shows GitHub stars + newsletter subscribers.
 * Fetches data from GitHub API and Moltable newsletter endpoint.
 * Designed for the landing page hero/pricing area.
 */
export default function SocialProof() {
  const { lang } = useLang()
  const isEn = lang === 'en'
  const [stats, setStats] = useState<SocialStats>({ githubStars: null, subscribers: null })
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function fetchStats() {
      const result: SocialStats = { githubStars: null, subscribers: null }

      // Fetch GitHub stars
      try {
        const ghRes = await fetch('https://api.github.com/repos/moltable/moltable', {
          headers: { Accept: 'application/vnd.github.v3+json' },
        })
        if (ghRes.ok) {
          const ghData = await ghRes.json()
          result.githubStars = ghData.stargazers_count ?? null
        }
      } catch { /* leave as null */ }

      // Fetch newsletter subscribers
      try {
        const nlRes = await fetch('https://api.moltable.ai/api/newsletter/count')
        if (nlRes.ok) {
          const nlData = await nlRes.json()
          result.subscribers = nlData.total ?? null
        }
      } catch { /* leave as null */ }

      if (!cancelled) {
        setStats(result)
        setError(result.githubStars === null && result.subscribers === null)
      }
    }

    fetchStats()
    return () => { cancelled = true }
  }, [])

  // Don't render if both stats are unavailable
  if (error || (stats.githubStars === null && stats.subscribers === null)) {
    return null
  }

  const items: { icon: React.ReactNode; value: string; label: string; labelEn: string }[] = []

  if (stats.githubStars !== null) {
    const formatted = stats.githubStars >= 1000
      ? `${(stats.githubStars / 1000).toFixed(1)}k`
      : String(stats.githubStars)
    items.push({
      icon: <Star size={14} style={{ color: '#F59E0B' }} />,
      value: formatted,
      label: 'GitHub Stars',
      labelEn: 'GitHub Stars',
    })
  }

  if (stats.subscribers !== null) {
    items.push({
      icon: <Mail size={14} style={{ color: '#6366F1' }} />,
      value: String(stats.subscribers),
      label: '订阅者',
      labelEn: 'Subscribers',
    })
  }

  if (items.length === 0) return null

  return (
    <div className="flex items-center justify-center gap-6 flex-wrap">
      {items.map((item, i) => (
        <div key={i} className="flex items-center gap-2">
          {item.icon}
          <span className="text-sm font-semibold" style={{ color: '#F5F4F8' }}>{item.value}</span>
          <span className="text-xs" style={{ color: '#6E6B80' }}>
            {isEn ? item.labelEn : item.label}
          </span>
        </div>
      ))}
    </div>
  )
}
