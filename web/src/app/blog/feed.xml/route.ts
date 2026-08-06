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
    <title>Moltable Blog — AI Identity &amp; Agent Infrastructure</title>
    <link>${escapeXml(baseUrl)}/blog</link>
    <description>AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度技术博客。Deep technical content about AI Agent identity infrastructure.</description>
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
