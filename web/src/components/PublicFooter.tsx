'use client'

import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'

export default function PublicFooter() {
  const { t } = useLang()

  return (
    <footer className="bg-ln-surface border-t border-ln-border">
      <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-10">
        {/* Product */}
        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.product}</h4>
          <ul className="space-y-3">
            {[
              { href: '#features', label: t.nav.features },
              { href: '#pricing', label: t.nav.pricing },
              { href: '/docs', label: t.nav.docs },
            ].map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Resources */}
        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.resources}</h4>
          <ul className="space-y-3">
            <li>
              <a
                href="https://github.com/nousresearch/moltable"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
              >
                GitHub
              </a>
            </li>
            <li>
              <Link
                href="/blog"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
              >
                博客
              </Link>
            </li>
            <li>
              <Link
                href="/blog"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
              >
                更新日志
              </Link>
            </li>
          </ul>
        </div>

        {/* Legal */}
        <div>
          <h4 className="text-sm mb-4 text-ln-text font-ui">{t.footer.legal}</h4>
          <ul className="space-y-3">
            <li>
              <Link
                href="#privacy"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
              >
                隐私政策
              </Link>
            </li>
            <li>
              <Link
                href="#privacy"
                className="text-sm font-body text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
              >
                服务条款
              </Link>
            </li>
          </ul>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="max-w-7xl mx-auto px-6 py-6 text-sm border-t border-ln-border-subtle text-ln-quaternary font-body">
        © 2026 {t.footer.copyright}
      </div>
    </footer>
  )
}
