import { type MetadataRoute } from 'next'
import fs from 'fs'
import path from 'path'

const BASE_URL = 'https://www.moltable.ai'

// Static pages with their priorities
const staticPages: { url: string; priority: number; changefreq?: MetadataRoute.Sitemap[number]['changeFrequency'] }[] = [
  { url: '/', priority: 1.0 },
  { url: '/connect', priority: 0.9 },
  { url: '/docs', priority: 0.9 },
  { url: '/pricing', priority: 0.9 },
  { url: '/blog', priority: 0.8 },
  { url: '/compare', priority: 0.9 },
  { url: '/signup', priority: 0.8 },
  { url: '/changelog', priority: 0.8 },
  { url: '/tools', priority: 0.8 },
  { url: '/about', priority: 0.7 },
  { url: '/faq', priority: 0.7, changefreq: 'monthly' as const },
  { url: '/privacy', priority: 0.3 },
  { url: '/terms', priority: 0.3 },
]

function discoverBlogPosts(): { slug: string; date: string }[] {
  const blogDir = path.join(process.cwd(), 'src/app/blog')
  const posts: { slug: string; date: string }[] = []

  try {
    const entries = fs.readdirSync(blogDir, { withFileTypes: true })
    for (const entry of entries) {
      if (!entry.isDirectory()) continue
      // Skip special dirs
      if (entry.name.startsWith('_') || entry.name === 'feed.xml') continue

      const mdxPath = path.join(blogDir, entry.name, 'page.mdx')
      if (!fs.existsSync(mdxPath)) continue

      try {
        const content = fs.readFileSync(mdxPath, 'utf-8')
        // Extract date from meta export: date: '2026-08-06'
        const dateMatch = content.match(/date:\s*['"](\d{4}-\d{2}-\d{2})['"]/)
        if (dateMatch) {
          posts.push({ slug: entry.name, date: dateMatch[1] })
        } else {
          // Fallback: use file modification time
          const stat = fs.statSync(mdxPath)
          posts.push({ slug: entry.name, date: stat.mtime.toISOString().split('T')[0] })
        }
      } catch {
        // Skip unreadable files
      }
    }
  } catch {
    // Blog dir not found, return empty
  }

  return posts
}

export default function sitemap(): MetadataRoute.Sitemap {
  const today = new Date().toISOString().split('T')[0]
  const entries: MetadataRoute.Sitemap = []

  // Static pages
  for (const page of staticPages) {
    entries.push({
      url: `${BASE_URL}${page.url}`,
      lastModified: today,
      changeFrequency: page.changefreq || 'weekly',
      priority: page.priority,
    })
  }

  // Blog posts — auto-discovered from filesystem
  const blogPosts = discoverBlogPosts()
  for (const post of blogPosts) {
    const ageInDays = Math.floor(
      (new Date().getTime() - new Date(post.date).getTime()) / (1000 * 60 * 60 * 24)
    )
    // Newer posts get higher priority
    const priority = ageInDays <= 7 ? 0.9 : ageInDays <= 30 ? 0.8 : 0.7

    entries.push({
      url: `${BASE_URL}/blog/${post.slug}`,
      lastModified: post.date,
      changeFrequency: 'weekly' as const,
      priority,
    })
  }

  return entries
}
