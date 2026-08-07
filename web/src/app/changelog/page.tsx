import fs from 'fs'
import path from 'path'
import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Changelog — Moltable',
  description:
    'Track every Moltable update — new features, security fixes, growth improvements, and performance optimizations. We ship nightly.',
  alternates: { canonical: 'https://www.moltable.ai/changelog' },
}

// Read CHANGELOG.md from project root
function getChangelogHtml(): string {
  try {
    const changelogPath = path.join(process.cwd(), '..', 'CHANGELOG.md')
    const raw = fs.readFileSync(changelogPath, 'utf-8')

    // Simple markdown → HTML conversion for h2, h3, lists, bold, code
    const lines = raw.split('\n')
    let html = ''
    let inList = false

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i]

      // Skip the top-level "# Changelog" heading (we'll render our own)
      if (line.startsWith('# Changelog') && i === 0) continue
      // Skip the blank line after the removed heading
      if (i === 1 && line.trim() === '') continue

      // H2: ## 2026-...
      if (line.startsWith('## ')) {
        if (inList) { html += '</ul>\n'; inList = false }
        html += `<h2 class="text-xl font-heading tracking-[-0.3px] mt-12 mb-4 pb-2" style="border-bottom: 1px solid rgba(255,255,255,0.06)">${escapeHtml(line.slice(3))}</h2>\n`
        continue
      }

      // H3: ### ...
      if (line.startsWith('### ')) {
        if (inList) { html += '</ul>\n'; inList = false }
        html += `<h3 class="text-base font-semibold mt-6 mb-2" style="color: #A5B4FC">${escapeHtml(line.slice(4))}</h3>\n`
        continue
      }

      // List items: - **text** or - text
      if (line.startsWith('- ')) {
        if (!inList) { html += '<ul class="space-y-1.5 ml-4">\n'; inList = true }
        let content = line.slice(2)
        content = content.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>')
        content = content.replace(/`([^`]+)`/g, '<code class="text-xs px-1 py-0.5 rounded font-mono" style="background: rgba(99,102,241,0.12); color: #A5B4FC">$1</code>')
        content = content.replace(/✅/g, '<span style="color: #22C55E">✅</span>')
        content = content.replace(/❌/g, '<span style="color: #EF4444">❌</span>')
        content = content.replace(/⚠️/g, '<span style="color: #F59E0B">⚠️</span>')
        content = content.replace(/🆕/g, '<span>🆕</span>')
        content = content.replace(/🔧/g, '<span>🔧</span>')
        content = content.replace(/🔴/g, '<span>🔴</span>')
        content = content.replace(/🔍/g, '<span>🔍</span>')
        content = content.replace(/📝/g, '<span>📝</span>')
        content = content.replace(/📊/g, '<span>📊</span>')
        content = content.replace(/📅/g, '<span>📅</span>')
        content = content.replace(/📤/g, '<span>📤</span>')
        content = content.replace(/🐦/g, '<span>🐦</span>')
        content = content.replace(/🎯/g, '<span>🎯</span>')
        content = content.replace(/🛠️/g, '<span>🛠️</span>')
        content = content.replace(/💬/g, '<span>💬</span>')
        content = content.replace(/📧/g, '<span>📧</span>')
        content = content.replace(/🧪/g, '<span>🧪</span>')
        content = content.replace(/🚨/g, '<span>🚨</span>')
        content = content.replace(/🟢/g, '<span>🟢</span>')
        content = content.replace(/🟡/g, '<span>🟡</span>')
        content = content.replace(/⚪/g, '<span>⚪</span>')
        content = content.replace(/📋/g, '<span>📋</span>')
        content = content.replace(/🧹/g, '<span>🧹</span>')
        content = content.replace(/📈/g, '<span>📈</span>')
        content = content.replace(/⭐/g, '<span>⭐</span>')
        content = content.replace(/👥/g, '<span>👥</span>')
        content = content.replace(/🔻/g, '<span>🔻</span>')
        html += `<li class="text-sm leading-relaxed" style="color: #A8A5B8">${content}</li>\n`
        continue
      }

      // Blank line
      if (line.trim() === '') {
        if (inList) { html += '</ul>\n'; inList = false }
        continue
      }

      // Any other non-empty line — treat as paragraph
      if (line.trim()) {
        if (inList) { html += '</ul>\n'; inList = false }
        html += `<p class="text-sm" style="color: #85829E">${escapeHtml(line)}</p>\n`
      }
    }

    if (inList) html += '</ul>\n'
    return html
  } catch {
    return '<p class="text-ln-tertiary">Changelog unavailable.</p>'
  }
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export default function ChangelogPage() {
  const html = getChangelogHtml()

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-28 pb-20">
        {/* Header */}
        <div className="mb-12">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-ln-tertiary hover:text-ln-secondary transition-colors mb-6"
          >
            ← Moltable
          </Link>
          <h1 className="text-4xl font-heading tracking-[-0.4px] mb-3">Changelog</h1>
          <p className="text-ln-secondary text-sm">
            Every update, every night. We ship continuously — new features, security patches, and
            growth improvements.
          </p>
          <div className="flex items-center gap-4 mt-4">
            <a
              href="https://github.com/Moltable/moltable"
              className="text-xs text-ln-accent hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub →
            </a>
            <a
              href="/blog/feed.xml"
              className="text-xs text-ln-accent hover:underline"
            >
              RSS Feed →
            </a>
          </div>
        </div>

        {/* Changelog content */}
        <div dangerouslySetInnerHTML={{ __html: html }} />

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-ln-border text-center">
          <p className="text-xs text-ln-tertiary">
            Moltable is open source.{' '}
            <a
              href="https://github.com/Moltable/moltable"
              className="text-ln-accent hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Star us on GitHub
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
