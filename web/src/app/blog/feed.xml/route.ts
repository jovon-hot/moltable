import { type NextRequest } from 'next/server'
import { getSortedPosts } from '@/data/blog-posts'

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export async function GET(_request: NextRequest) {
  const baseUrl = 'https://www.moltable.ai'
  const now = new Date().toUTCString()

  const posts = getSortedPosts()
  const items = posts
    .map((post) => {
      const url = `${baseUrl}/blog/${post.slug}`
      const pubDate = new Date(post.date + 'T08:00:00+08:00').toUTCString()
      const title = post.titleEn ? `${post.titleEn} / ${post.title}` : post.title
      const categories = post.tags.map((t) => `  <category>${escapeXml(t)}</category>`).join('\n')

      return `  <item>
    <title>${escapeXml(title)}</title>
    <link>${escapeXml(url)}</link>
    <guid isPermaLink="true">${escapeXml(url)}</guid>
    <pubDate>${pubDate}</pubDate>
    <description>${escapeXml(post.excerpt)}</description>
${categories}
  </item>`
    })
    .join('\n')

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Moltable Blog — Your AI, Always in Sync</title>
    <link>${escapeXml(baseUrl)}/blog</link>
    <description>Agent 在线同步、MCP 协议、跨框架迁移 — 你的 AI 永远顺手。关于 AI Agent 在线同步层的深度技术博客。Your AI, always in sync. Deep technical content about the AI Agent online sync layer.</description>
    <language>zh-CN</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="${baseUrl}/blog/feed.xml" rel="self" type="application/rss+xml"/>
${items}
  </channel>
</rss>`

  return new Response(rss, {
    status: 200,
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
