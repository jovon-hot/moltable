'use client'

import { useState, useMemo } from 'react'
import { Rss } from 'lucide-react'
import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'
import NewsletterSignup from '@/components/NewsletterSignup'
import { getSortedPosts, getAllTags, getPostsByTag } from '@/data/blog-posts'

export default function BlogPage() {
  const { t, lang } = useLang()
  const isEn = lang === 'en'
  const [activeTag, setActiveTag] = useState<string | null>(null)

  const allPosts = useMemo(() => getSortedPosts(), [])
  const allTags = useMemo(() => getAllTags(), [])
  const filteredPosts = useMemo(
    () => (activeTag ? getPostsByTag(activeTag) : allPosts),
    [activeTag, allPosts]
  )

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-3xl mx-auto px-6 pt-28 pb-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-12 h-12 rounded-[12px] flex items-center justify-center mx-auto mb-6 bg-ln-accent-muted">
            <Rss size={22} className="text-ln-accent" />
          </div>
          <h1 className="text-4xl font-heading tracking-[-0.4px] mb-3">
            {isEn ? 'Moltable Blog' : 'Moltable 博客'}
          </h1>
          <p className="text-base text-ln-secondary max-w-md mx-auto">
            {isEn
              ? 'AI Identity, MCP protocol, cross-platform Persona — deep content about AI Agent identity infrastructure.'
              : 'AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度内容。'}
          </p>
        </div>

        {/* Tag Filter */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          <button
            onClick={() => setActiveTag(null)}
            className={`text-xs px-3 py-1.5 rounded-full font-ui transition-all ${
              activeTag === null
                ? 'text-white'
                : 'text-ln-tertiary hover:text-ln-secondary'
            }`}
            style={
              activeTag === null
                ? { background: '#4338CA' }
                : { background: 'rgba(255,255,255,0.05)' }
            }
          >
            {isEn ? 'All' : '全部'}
            <span className="ml-1.5 opacity-60">{allPosts.length}</span>
          </button>
          {allTags.slice(0, 12).map((tag) => {
            const count = getPostsByTag(tag).length
            return (
              <button
                key={tag}
                onClick={() => setActiveTag(activeTag === tag ? null : tag)}
                className={`text-xs px-3 py-1.5 rounded-full font-ui transition-all ${
                  activeTag === tag
                    ? 'text-white'
                    : 'text-ln-tertiary hover:text-ln-secondary'
                }`}
                style={
                  activeTag === tag
                    ? { background: '#4338CA' }
                    : { background: 'rgba(255,255,255,0.05)' }
                }
              >
                {tag}
                <span className="ml-1.5 opacity-60">{count}</span>
              </button>
            )
          })}
        </div>

        {/* Filtered count indicator */}
        {activeTag && (
          <p className="text-center text-sm text-ln-tertiary mb-8">
            {isEn
              ? `${filteredPosts.length} post${filteredPosts.length !== 1 ? 's' : ''} tagged "${activeTag}"`
              : `标签 "${activeTag}" 共 ${filteredPosts.length} 篇文章`}
            {' · '}
            <button onClick={() => setActiveTag(null)} className="text-ln-accent hover:underline">
              {isEn ? 'Show all' : '显示全部'}
            </button>
          </p>
        )}

        {/* Posts */}
        <div className="space-y-8">
          {filteredPosts.map((post, i) => {
            const isFeatured = i === 0 && !activeTag
            return (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className={`block p-6 rounded-card transition-all duration-200 hover:bg-ln-hover group ${
                  isFeatured ? 'bg-ln-panel' : 'bg-ln-panel'
                }`}
                style={
                  isFeatured
                    ? {
                        boxShadow:
                          '0 0 0 1px rgba(99,102,241,0.2), 0 4px 24px rgba(67,56,202,0.08)',
                        position: 'relative',
                        overflow: 'hidden',
                      }
                    : { boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }
                }
              >
                {isFeatured && (
                  <div
                    className="absolute top-0 right-0 px-3 py-1 rounded-bl-lg text-[11px] font-semibold"
                    style={{ background: '#4338CA', color: '#fff' }}
                  >
                    {isEn ? 'FEATURED' : '精选'}
                  </div>
                )}
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs text-ln-tertiary font-ui">{post.date}</span>
                  <div className="flex gap-2">
                    {post.tags.map((tag) => (
                      <span
                        key={tag}
                        className={`text-[11px] px-2 py-0.5 rounded-pill font-ui cursor-pointer transition-all ${
                          activeTag === tag ? 'ring-1 ring-[#6366F1]' : ''
                        }`}
                        style={{
                          background:
                            activeTag === tag
                              ? 'rgba(99,102,241,0.2)'
                              : isFeatured
                                ? 'rgba(251,107,75,0.12)'
                                : 'rgba(99,102,241,0.12)',
                          color: activeTag === tag ? '#C7D2FE' : isFeatured ? '#FB6B4B' : '#A5B4FC',
                        }}
                        onClick={(e) => {
                          e.preventDefault()
                          setActiveTag(activeTag === tag ? null : tag)
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <h2 className="text-xl font-heading tracking-[-0.24px] mb-2 text-ln-text group-hover:text-ln-accent transition-colors">
                  {isEn && post.titleEn ? post.titleEn : post.title}
                </h2>
                <p className="text-sm text-ln-secondary font-body leading-relaxed">
                  {post.excerpt}
                </p>
                {isEn && post.title !== post.titleEn && post.titleEn && (
                  <p className="text-[11px] text-ln-tertiary mt-1">{post.title}</p>
                )}
              </Link>
            )
          })}
        </div>

        {/* Empty state */}
        {filteredPosts.length === 0 && (
          <div className="text-center py-16">
            <p className="text-ln-tertiary">
              {isEn ? 'No posts found for this tag.' : '没有找到该标签的文章。'}
            </p>
          </div>
        )}

        {/* Newsletter Signup */}
        <div className="mt-16">
          <NewsletterSignup variant="card" />
        </div>

        {/* RSS / Subscribe hint */}
        <div className="mt-12 pt-8 border-t border-ln-border text-center">
          <p className="text-sm text-ln-tertiary mb-3">
            {isEn ? 'Want a detailed comparison? Check our ' : '想看详细对比？查看'}
            <Link href="/compare" className="text-ln-accent hover:underline font-medium">
              {isEn ? 'Moltable vs mem0 vs Zep comparison' : 'Moltable vs mem0 vs Zep 平台对比'}
            </Link>
          </p>
          <p className="text-sm text-ln-tertiary">
            {isEn ? 'More content coming · Follow ' : '更多内容即将发布 · 关注 '}
            <a href="https://github.com/Moltable" className="text-ln-accent hover:underline">
              GitHub
            </a>
            {' '}{isEn ? 'for updates' : '获取更新'}
          </p>
        </div>
      </div>
    </div>
  )
}
