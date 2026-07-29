'use client'

import { Rss } from 'lucide-react'
import Link from 'next/link'

const posts = [
  {
    slug: 'mcp-ai-usb-c',
    date: '2026-06-20',
    title: 'MCP 协议：为什么它是 AI 的 USB-C',
    titleEn: 'MCP: The USB-C of AI Agents',
    excerpt: 'Model Context Protocol 正在成为 AI Agent 连接外部世界的标准。本文解析 MCP 的协议设计、与 A2A 的互补关系，以及为什么 Moltable 选择 MCP 作为核心接入方式。',
    tags: ['MCP', '协议', 'Agent'],
  },
  {
    slug: 'ai-identity-layer',
    date: '2026-06-28',
    title: 'AI 身份层的设计哲学：从 Memory 到 Identity',
    titleEn: 'From Memory to Identity: Designing the AI Identity Layer',
    excerpt: 'Memory 赛道拥挤，但 Identity 赛道几乎无人。本文探讨为什么"身份"比"记忆"更适合作为 AI 个人化的原子单位，以及 Moltable 的 Identity→Persona→Agent 三层架构设计。',
    tags: ['Identity', '架构', '设计哲学'],
  },
  {
    slug: 'cross-platform-persona',
    date: '2026-07-05',
    title: '跨平台 Persona 管理：一个身份，多种人格',
    titleEn: 'Cross-Platform Persona: One Identity, Many Minds',
    excerpt: '同一个 AI，加载战略顾问 Persona 是麦肯锡风格，加载保守审核员 Persona 是合规导向。本文通过真实场景演示 Persona 系统如何让一个 AI 拥有多种思维模式。',
    tags: ['Persona', '最佳实践', '教程'],
  },
]

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-3xl mx-auto px-6 pt-28 pb-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-12 h-12 rounded-[12px] flex items-center justify-center mx-auto mb-6 bg-ln-accent-muted">
            <Rss size={22} className="text-ln-accent" />
          </div>
          <h1 className="text-4xl font-heading tracking-[-0.4px] mb-3">
            Moltable 博客
          </h1>
          <p className="text-base text-ln-secondary max-w-md mx-auto">
            AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度内容。
          </p>
        </div>

        {/* Articles */}
        <div className="space-y-8">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="block p-6 rounded-card bg-ln-panel shadow-border transition-all duration-200 hover:bg-ln-hover hover:shadow-card-hover group"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs text-ln-tertiary font-ui">{post.date}</span>
                <div className="flex gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[11px] px-2 py-0.5 rounded-pill font-ui"
                      style={{ background: 'rgba(113,112,255,0.12)', color: '#828fff' }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <h2 className="text-xl font-heading tracking-[-0.24px] mb-2 text-ln-text group-hover:text-ln-accent transition-colors">
                {post.title}
              </h2>
              <p className="text-sm text-ln-secondary font-body leading-relaxed">
                {post.excerpt}
              </p>
            </Link>
          ))}
        </div>

        {/* RSS / Subscribe hint */}
        <div className="mt-16 pt-8 border-t border-ln-border text-center">
          <p className="text-sm text-ln-tertiary">
            更多内容即将发布 · 关注{' '}
            <a href="https://github.com/moltable" className="text-ln-accent hover:underline">
              GitHub
            </a>
            {' '}获取更新
          </p>
        </div>
      </div>
    </div>
  )
}
