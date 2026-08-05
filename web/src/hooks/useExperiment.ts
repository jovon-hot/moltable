'use client'

import { useEffect, useState, useCallback } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

interface ExperimentConfig {
  id: string
  variants: Record<string, React.ReactNode>
  /** Which variant to show while loading / when experiment is unavailable */
  fallback?: string
}

interface Assignment {
  variant: string
  reason: string
}

/**
 * A/B testing hook — assigns user to a variant and tracks conversions.
 *
 * Usage:
 *   const { variant, content, trackConversion } = useExperiment({
 *     id: 'hero-cta-test',
 *     variants: {
 *       control: <CurrentCTA />,
 *       emoji:   <CTAWithEmoji />,
 *     }
 *   })
 *
 *   // Later, when user clicks:
 *   <button onClick={() => { handleClick(); trackConversion() }}>{content}</button>
 */
export function useExperiment(config: ExperimentConfig) {
  const [variant, setVariant] = useState<string>(config.fallback || Object.keys(config.variants)[0] || 'control')
  const [loading, setLoading] = useState(true)
  const [assigned, setAssigned] = useState(false)

  useEffect(() => {
    // Check localStorage first for persistence across page loads
    const storageKey = `moltable_exp_${config.id}`
    const stored = typeof window !== 'undefined' ? localStorage.getItem(storageKey) : null
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as Assignment
        setVariant(parsed.variant)
        setAssigned(true)
        setLoading(false)
        return
      } catch { /* fall through to API call */ }
    }

    // Assign via API
    let cancelled = false
    async function assign() {
      try {
        const res = await fetch(`${API_BASE}/api/admin/experiments/${config.id}/assign`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
        if (!res.ok) {
          if (!cancelled) {
            // Fallback to control silently
            setLoading(false)
          }
          return
        }
        const data: Assignment = await res.json()
        if (!cancelled) {
          // Validate variant exists in our config
          const finalVariant = config.variants[data.variant] ? data.variant : (config.fallback || 'control')
          setVariant(finalVariant)
          setAssigned(true)
          // Persist assignment
          if (typeof window !== 'undefined') {
            localStorage.setItem(storageKey, JSON.stringify({ variant: finalVariant, reason: data.reason }))
          }
        }
      } catch {
        if (!cancelled) setLoading(false)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    assign()
    return () => { cancelled = true }
  }, [config.id, config.fallback, config.variants])

  const trackConversion = useCallback(async () => {
    if (!assigned) return
    try {
      await fetch(`${API_BASE}/api/admin/experiments/${config.id}/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    } catch {
      // Silently fail — conversion tracking is best-effort
    }
  }, [config.id, assigned])

  const content = config.variants[variant] || config.variants[config.fallback || 'control'] || null

  return {
    variant,
    content,
    loading,
    trackConversion,
  }
}
