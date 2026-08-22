'use client'

import Link from 'next/link'
import { ArrowLeft, Share2, Link2, ArrowRight } from 'lucide-react'
import { TwitterIcon, LinkedInIcon } from './BrandIcons'
import { useState } from 'react'

function ShareButtons() {
  const [copied, setCopied] = useState(false)

  const shareUrl = typeof window !== 'undefined' ? window.location.href : ''
  const shareTitle = typeof document !== 'undefined' ? document.title : ''

  const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareTitle)}`
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`

  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-ln-tertiary mr-1">Share:</span>
      <a
        href={twitterUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-ln-hover"
        title="Share on X"
        style={{ background: 'rgba(255,255,255,0.03)' }}
      >
        <TwitterIcon size={14} style={{ color: '#A8A5B8' }} />
      </a>
      <a
        href={linkedinUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-ln-hover"
        title="Share on LinkedIn"
        style={{ background: 'rgba(255,255,255,0.03)' }}
      >
        <LinkedInIcon size={14} style={{ color: '#A8A5B8' }} />
      </a>
      <button
        onClick={copyLink}
        className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-ln-hover relative"
        title="Copy link"
        style={{ background: 'rgba(255,255,255,0.03)' }}
      >
        {copied ? (
          <span className="text-[10px] font-medium" style={{ color: '#6366F1' }}>✓</span>
        ) : (
          <Link2 size={14} style={{ color: '#A8A5B8' }} />
        )}
      </button>
    </div>
  )
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <div className="flex items-center justify-between mb-8">
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-sm text-ln-tertiary hover:text-ln-accent font-ui transition-colors"
          >
            <ArrowLeft size={14} /> 返回博客
          </Link>
          <ShareButtons />
        </div>
        {children}

        {/* Post-footer CTA */}
        <div className="mt-16 pt-8 border-t border-ln-border">
          <div className="p-6 rounded-card text-center" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(99,102,241,0.12)' }}>
            <div className="text-2xl mb-2">⚡</div>
            <h3 className="text-lg font-heading mb-2 font-semibold">
              换 Agent，不换灵魂
            </h3>
            <p className="text-sm text-ln-secondary mb-5 max-w-sm mx-auto">
              3 分钟备份你的 Agent 灵魂 — SOUL、Skills、记忆打包备份，换框架不丢失。
            </p>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90"
              style={{ background: '#4338CA', color: '#fff' }}
            >
              免费开始 <ArrowRight size={16} />
            </Link>
            <p className="text-[11px] text-ln-tertiary mt-3">
              Pro 版享 30 天免费体验 · 无需信用卡
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
