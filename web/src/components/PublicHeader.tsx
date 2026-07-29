'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

export default function PublicHeader() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { t, lang, setLang } = useLang()
  const pathname = usePathname()
  const router = useRouter()

  const navLinks = [
    { href: '#features', label: t.nav.features },
    { href: '#pricing', label: t.nav.pricing },
    { href: '/docs', label: t.nav.docs },
    { href: '#about', label: t.nav.about },
  ]

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith('#')) {
      e.preventDefault()
      // If not on home page, navigate there first
      if (pathname !== '/') {
        router.push('/' + href)
        setMobileOpen(false)
        return
      }
      const id = href.slice(1)
      const el = document.getElementById(id)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
      setMobileOpen(false)
    }
  }

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
        scrolled
          ? 'bg-ln-bg/85 backdrop-blur-xl border-b border-ln-border-subtle'
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-heading text-lg text-ln-text tracking-[-0.3px]">
          <span className="w-2 h-2 rounded-full bg-ln-accent inline-block" />
          Moltable
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={(e) => handleAnchorClick(e, link.href)}
              className="text-sm font-ui transition-colors duration-150 text-ln-tertiary hover:text-ln-secondary"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/login"
            className="px-4 py-2 text-sm rounded-btn font-ui text-ln-secondary hover:bg-ln-hover transition-all duration-150"
          >
            {t.nav.login}
          </Link>
          <Link
            href="/register"
            className="px-5 py-2 text-sm rounded-btn font-ui bg-ln-accent text-white hover:bg-ln-accent-hover transition-all duration-150"
          >
            {t.nav.start}
          </Link>
          {/* Language Switch */}
          <button
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className="text-xs px-2 py-1 rounded-btn border border-ln-border text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
          >
            {lang === 'zh' ? 'EN' : '中文'}
          </button>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="md:hidden p-2 rounded-btn text-ln-secondary hover:bg-ln-hover transition-colors"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label={mobileOpen ? t.common?.closeMenu ?? '关闭菜单' : t.common?.openMenu ?? '打开菜单'}
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="md:hidden border-t border-ln-border bg-ln-surface animate-in">
          <nav className="px-6 py-4 flex flex-col gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={(e) => handleAnchorClick(e, link.href)}
                className="px-3 py-2.5 rounded-btn text-sm font-ui transition-colors duration-150 text-ln-secondary hover:bg-ln-hover"
              >
                {link.label}
              </Link>
            ))}
            <hr className="border-ln-border-subtle my-2" />
            <Link
              href="/login"
              onClick={() => setMobileOpen(false)}
              className="px-3 py-2.5 rounded-btn text-sm font-ui text-ln-secondary"
            >
              {t.nav.login}
            </Link>
            <Link
              href="/register"
              onClick={() => setMobileOpen(false)}
              className="px-3 py-2.5 rounded-btn text-sm font-ui bg-ln-accent text-white text-center"
            >
              {t.nav.start}
            </Link>
          </nav>
          {/* Mobile Language Switch */}
          <div className="px-6 pb-4">
            <button
              onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
              className="text-xs px-2 py-1 rounded-btn border border-ln-border text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
            >
              {lang === 'zh' ? 'EN' : '中文'}
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
