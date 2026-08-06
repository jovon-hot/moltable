'use client'

import { useEffect, useState } from 'react'
import { createClient, getLocalKey, clearLocalKey } from '@/lib/supabase'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Loader2, Menu, X, LayoutDashboard, Brain, User, Settings, Eye, Bell, Search, Shield } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'
import { apiFetch } from '@/lib/api'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDemo, setIsDemo] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const local = !(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
  const supabase = local ? null : createClient()
  const pathname = usePathname()
  const router = useRouter()
  const { t, lang, setLang } = useLang()
  const d = t.dashboard_ui as any

  useEffect(() => {
    const localKey = getLocalKey()
    if (localKey) {
      // Use Moltable local auth — fetch real user info from /api/auth/me
      apiFetch<{ id: string; email: string; name: string }>('/api/auth/me').then(info => {
        if (info && info.email) {
          setUser({ email: info.email, name: info.name || info.email.split('@')[0], id: info.id })
        } else {
          setUser({ email: d.localUser, id: 'local' })
        }
        setIsDemo(false)
      }).catch(() => {
        setUser({ email: d.localUser, id: 'local' })
      }).finally(() => setLoading(false))
      return
    }
    if (!local && supabase) {
      supabase.auth.getUser().then(({ data }) => {
        if (!data.user) { setUser({ email: d.localUser, id: 'local' }); setIsDemo(true); setLoading(false); return }
        setUser(data.user)
        setLoading(false)
        apiFetch<{ plan?: string }>('/api/auth/me').then(info => {
          if (info?.plan === 'admin') setIsAdmin(true)
        }).catch(() => {})
      })
      return
    }
    setIsDemo(true)
    setLoading(false)
  }, [])

  const handleSignOut = async () => {
    clearLocalKey()
    if (!local && supabase) await supabase.auth.signOut()
    window.location.href = '/'
  }

  const navLinks = [
    { href: '/dashboard', label: d.overview, icon: LayoutDashboard },
    { href: '/dashboard/memories', label: t.dashboard.stats.memories, icon: Brain },
    { href: '/dashboard/personas', label: t.dashboard.stats.personas, icon: User },
    { href: '/dashboard/settings', label: d.settings, icon: Settings },
    ...(isAdmin ? [{ href: '/admin', label: 'Admin', icon: Shield }] : []),
  ]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-ln-bg">
        <Loader2 className="w-6 h-6 animate-spin text-ln-accent" />
      </div>
    )
  }

  const sidebarContent = (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-5 pb-6">
        <Link href="/dashboard" className="inline-flex items-center">
          <img src="/logo-horizontal.svg" alt="Moltable.ai" className="h-6 w-auto" />
        </Link>
      </div>
      <nav role="navigation" aria-label={d.sidebar_arialabel} className="flex-1 px-3 space-y-0.5">
        {navLinks.map(link => {
          const isActive = pathname === link.href
          const Icon = link.icon
          return (
            <Link
              key={link.href}
              href={link.href}
              aria-current={isActive ? 'page' : undefined}
              className={`flex items-center gap-3 px-3 py-2 rounded-btn text-sm transition-all duration-150 ${
                isActive
                  ? 'bg-ln-accent-muted text-ln-accent-hover font-ui shadow-border-accent'
                  : 'text-ln-tertiary font-body hover:bg-ln-hover hover:text-ln-secondary'
              }`}
            >
              <Icon size={16} />
              {link.label}
            </Link>
          )
        })}
      </nav>
      <div className="px-4 py-4 border-t border-ln-border">
        {isDemo ? (
          <div className="text-xs text-ln-tertiary">
            <Link href="/login" className="text-ln-accent font-ui hover:text-ln-accent-hover transition-colors">
              {t.nav.login}
            </Link> {d.signin_sync}
          </div>
        ) : (
          <>
            <div className="text-xs text-ln-tertiary truncate mb-2 font-body">{user?.email}</div>
            <button
              onClick={handleSignOut}
              aria-label={d.signout}
              className="text-xs text-ln-tertiary hover:text-ln-error transition-colors duration-150 font-body"
            >
              {d.signout}
            </button>
          </>
        )}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      {isDemo && (
        <div className="flex items-center justify-center gap-2 py-2 px-4 text-sm bg-ln-accent-muted text-ln-accent-hover font-ui border-b border-ln-border-accent">
          <Eye size={16} />
          🔍 {t.dashboard.demoBanner}
        </div>
      )}

      <nav
        className="h-12 px-4 flex items-center justify-between sticky top-0 z-40 bg-ln-bg/85 backdrop-blur-xl border-b border-ln-border"
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden text-ln-tertiary hover:text-ln-text transition-colors p-1 rounded-btn"
            aria-label={sidebarOpen ? t.common.closeMenu : t.common.openMenu}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
          <Link href="/dashboard" className="flex items-center gap-2">
            <img src="/logo-icon.svg" alt="Moltable.ai" className="h-7 w-7" />
            <span className="text-base font-heading tracking-[-0.3px] text-ln-text">Moltable</span>
          </Link>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ln-tertiary" />
            <input
              placeholder={d.search_placeholder}
              className="w-44 pl-9 pr-3 py-1.5 rounded-btn bg-ln-surface text-ln-text text-xs font-body shadow-border focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary"
              aria-label={t.common.search}
            />
          </div>
          <button
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className="text-xs px-2 py-1 rounded-btn border border-ln-border text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
          >
            {lang === 'zh' ? 'EN' : '中文'}
          </button>
          <button className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-text hover:bg-ln-hover transition-all duration-150" aria-label={d.notifications}>
            <Bell size={16} />
          </button>
          {isDemo ? (
            <Link href="/login" className="text-xs px-3 py-1.5 rounded-btn bg-ln-accent text-white font-ui hover:bg-ln-accent-hover transition-all duration-150">
              {t.nav.login}
            </Link>
          ) : (
            <>
              <span className="text-xs hidden sm:inline truncate max-w-[160px] text-ln-tertiary font-body">
                {user?.email}
              </span>
              <div className="w-7 h-7 rounded-full bg-ln-accent-muted flex items-center justify-center text-xs font-ui text-ln-accent-hover">
                {(user?.email || '?').charAt(0).toUpperCase()}
              </div>
              <button
                onClick={handleSignOut}
                aria-label={d.signout}
                className="text-xs px-2 py-1 rounded-[4px] text-ln-tertiary hover:text-ln-error hover:bg-ln-error/10 transition-all duration-150 font-body"
              >
                {d.signout_short}
              </button>
            </>
          )}
        </div>
      </nav>

      <div className="flex">
        <aside
          role="navigation"
          aria-label={d.sidebar_arialabel}
          className="hidden md:flex flex-col w-52 min-h-[calc(100vh-3rem)] border-r border-ln-border bg-ln-surface flex-shrink-0"
        >
          {sidebarContent}
        </aside>

        {sidebarOpen && (
          <div className="fixed inset-0 z-30 md:hidden bg-black/60 animate-in" onClick={() => setSidebarOpen(false)}>
            <aside
              role="navigation"
              aria-label={d.sidebar_arialabel}
              className="w-60 h-full bg-ln-surface border-r border-ln-border animate-in"
              onClick={e => e.stopPropagation()}
            >
              {sidebarContent}
            </aside>
          </div>
        )}

        <main role="main" className="flex-1 min-h-[calc(100vh-3rem)] bg-ln-bg">
          {children}
        </main>
      </div>
    </div>
  )
}
