'use client'

import { useEffect, useState } from 'react'
import { createClient, getLocalKey, clearLocalKey } from '@/lib/supabase'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Loader2, Menu, X, LayoutDashboard, Brain, User, Settings, Eye, Bell, Search } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDemo, setIsDemo] = useState(false)
  const local = !(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
  const supabase = local ? null : createClient()
  const pathname = usePathname()
  const router = useRouter()
  const { t, lang, setLang } = useLang()

  useEffect(() => {
    if (local) {
      const localKey = getLocalKey()
      if (localKey) {
        setUser({ email: '本地用户', id: 'local' })
        setIsDemo(false)
      } else {
        setIsDemo(true)
      }
      setLoading(false)
      return
    }
    supabase!.auth.getUser().then(({ data }) => {
      if (!data.user) {
        // 本地模式：检查 localStorage
        const localKey = getLocalKey()
        if (localKey) {
          setUser({ email: '本地用户', id: 'local' })
          setIsDemo(false)
        } else {
          setIsDemo(true)
        }
        setLoading(false)
        return
      }
      setUser(data.user)
      setLoading(false)
    })
  }, [])

  const handleSignOut = async () => {
    clearLocalKey()
    if (!local && supabase) await supabase.auth.signOut()
    window.location.href = '/'
  }

  const navLinks = [
    { href: '/dashboard', label: '概览', icon: LayoutDashboard },
    { href: '/dashboard/memories', label: t.dashboard.stats.memories, icon: Brain },
    { href: '/dashboard/personas', label: t.dashboard.stats.personas, icon: User },
    { href: '/dashboard/settings', label: '设置', icon: Settings },
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
        <Link
          href="/dashboard"
          className="text-lg inline-flex items-center gap-2 font-heading tracking-[-0.3px] text-ln-text"
        >
          <span className="w-2 h-2 rounded-full bg-ln-accent inline-block" />
          Moltable
        </Link>
      </div>
      <nav role="navigation" aria-label="主导航" className="flex-1 px-3 space-y-0.5">
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
            </Link> 以同步数据
          </div>
        ) : (
          <>
            <div className="text-xs text-ln-tertiary truncate mb-2 font-body">{user?.email}</div>
            <button
              onClick={handleSignOut}
              aria-label="退出登录"
              className="text-xs text-ln-tertiary hover:text-ln-error transition-colors duration-150 font-body"
            >
              退出登录
            </button>
          </>
        )}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      {/* Demo mode banner */}
      {isDemo && (
        <div className="flex items-center justify-center gap-2 py-2 px-4 text-sm bg-ln-accent-muted text-ln-accent-hover font-ui border-b border-ln-border-accent">
          <Eye size={16} />
          🔍 {t.dashboard.demoBanner}
        </div>
      )}

      {/* Top nav bar */}
      <nav
        className="h-12 px-4 flex items-center justify-between sticky top-0 z-40 bg-ln-bg/85 backdrop-blur-xl border-b border-ln-border"
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden text-ln-tertiary hover:text-ln-text transition-colors p-1 rounded-btn"
            aria-label={sidebarOpen ? '关闭菜单' : '打开菜单'}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
          <Link
            href="/dashboard"
            className="text-base flex items-center gap-2 font-heading tracking-[-0.3px] text-ln-text"
          >
            <span className="w-[7px] h-[7px] rounded-full bg-ln-accent inline-block" />
            Moltable
          </Link>
        </div>
        <div className="flex items-center gap-3">
          {/* Search bar (desktop) */}
          <div className="hidden sm:flex relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ln-tertiary" />
            <input
              placeholder={t.common.search}
              className="w-44 pl-9 pr-3 py-1.5 rounded-btn bg-ln-surface text-ln-text text-xs font-body shadow-border focus:shadow-border-accent outline-none transition-all placeholder:text-ln-tertiary"
              aria-label={t.common.search}
            />
          </div>
          {/* Language Switch */}
          <button
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className="text-xs px-2 py-1 rounded-btn border border-ln-border text-ln-tertiary hover:text-ln-secondary transition-colors duration-150"
          >
            {lang === 'zh' ? 'EN' : '中文'}
          </button>
          {/* Notification icon */}
          <button className="p-1.5 rounded-btn text-ln-tertiary hover:text-ln-text hover:bg-ln-hover transition-all duration-150" aria-label="通知">
            <Bell size={16} />
          </button>
          {isDemo ? (
            <Link
              href="/login"
              className="text-xs px-3 py-1.5 rounded-btn bg-ln-accent text-white font-ui hover:bg-ln-accent-hover transition-all duration-150"
            >
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
                aria-label="退出登录"
                className="text-xs px-2 py-1 rounded-[4px] text-ln-tertiary hover:text-ln-error hover:bg-ln-error/10 transition-all duration-150 font-body"
              >
                退出
              </button>
            </>
          )}
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar (desktop) */}
        <aside
          role="navigation"
          aria-label="主导航"
          className="hidden md:flex flex-col w-52 min-h-[calc(100vh-3rem)] border-r border-ln-border bg-ln-surface flex-shrink-0"
        >
          {sidebarContent}
        </aside>

        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 md:hidden bg-black/60 animate-in"
            onClick={() => setSidebarOpen(false)}
          >
            <aside
              role="navigation"
              aria-label="主导航"
              className="w-60 h-full bg-ln-surface border-r border-ln-border animate-in"
              onClick={e => e.stopPropagation()}
            >
              {sidebarContent}
            </aside>
          </div>
        )}

        {/* Main content */}
        <main role="main" className="flex-1 min-h-[calc(100vh-3rem)] bg-ln-bg">
          {children}
        </main>
      </div>
    </div>
  )
}
