import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import RelatedPosts from '@/components/RelatedPosts'

export interface ArticleMeta {
  title: string
  date: string
  description?: string
  tags?: string[]
  slug?: string
  authorName?: string
}

function BlogJsonLd({ meta }: { meta: ArticleMeta }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: meta.title,
    description: meta.description || '',
    datePublished: meta.date,
    author: {
      '@type': 'Organization',
      name: meta.authorName || 'Moltable Team',
      url: 'https://www.moltable.ai',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Moltable',
      url: 'https://www.moltable.ai',
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': meta.slug ? `https://www.moltable.ai/blog/${meta.slug}` : 'https://www.moltable.ai/blog',
    },
    keywords: meta.tags?.join(', ') || '',
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}

export default function ArticleLayout({
  meta,
  children,
}: {
  meta: ArticleMeta
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen" style={{ background: '#0D0D14', color: '#F5F4F8' }}>
      <BlogJsonLd meta={meta} />
      <article className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <Link
          href="/blog"
          className="inline-flex items-center gap-2 text-sm mb-8 font-medium"
          style={{ color: '#85829E' }}
        >
          <ArrowLeft size={14} /> 返回博客
        </Link>
        <h1
          className="text-3xl mb-3"
          style={{ fontWeight: 600, letterSpacing: '-0.4px', color: '#F5F4F8' }}
        >
          {meta.title}
        </h1>
        <p className="text-sm mb-2 font-medium" style={{ color: '#6E6B80' }}>
          {meta.date}
        </p>
        {meta.tags && (
          <div className="flex flex-wrap gap-2 mb-8">
            {meta.tags.map((tag) => (
              <span
                key={tag}
                className="text-[11px] px-2 py-0.5 rounded-full font-medium"
                style={{
                  background: 'rgba(99,102,241,0.12)',
                  color: '#A5B4FC',
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        <div className="prose-custom">{children}</div>
        {meta.tags && meta.slug && (
          <RelatedPosts currentSlug={meta.slug} currentTags={meta.tags} />
        )}
      </article>
    </div>
  )
}
