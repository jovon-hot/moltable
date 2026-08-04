import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <Link
          href="/blog"
          className="inline-flex items-center gap-2 text-sm text-ln-tertiary hover:text-ln-accent font-ui mb-8 transition-colors"
        >
          <ArrowLeft size={14} /> 返回博客
        </Link>
        {children}
      </div>
    </div>
  )
}
