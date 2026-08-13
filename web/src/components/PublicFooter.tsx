'use client'

import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'

export default function PublicFooter() {
  const { t } = useLang()

  return (
    <footer className="bg-ln-surface border-t border-ln-border">
      <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-10">
        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.product}</h4>
          <ul className="space-y-3">
            {[
              { href: '/#features', label: t.footer.features },
              { href: '/#pricing', label: t.footer.pricing },
              { href: '/docs', label: t.footer.docs },
            ].map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.resources}</h4>
          <ul className="space-y-3">
            <li>
              <a href="https://github.com/Moltable/moltable" target="_blank" rel="noopener noreferrer"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.github}
              </a>
            </li>
            <li>
              <Link href="/blog" className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.blog}
              </Link>
            </li>
            <li>
              <Link href="/changelog" className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.changelog}
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.legal}</h4>
          <ul className="space-y-3">
            <li>
              <Link href="/privacy" className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.privacy}
              </Link>
            </li>
            <li>
              <Link href="/terms" className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.terms}
              </Link>
            </li>
            <li>
              <Link href="/faq" className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150">
                {t.footer.faq}
              </Link>
            </li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 text-sm border-t border-ln-border-subtle text-ln-quaternary font-body">
        &copy; 2026 {t.footer.copyright}
      </div>
    </footer>
  )
}
