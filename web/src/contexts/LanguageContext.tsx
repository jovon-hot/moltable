'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { Lang, translations } from '@/lib/i18n'

type T = typeof translations.zh

const LanguageContext = createContext<{ lang: Lang; t: T; setLang: (l: Lang) => void } | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>('zh')

  useEffect(() => {
    const saved = localStorage.getItem('moltable-lang') as Lang
    if (saved === 'zh' || saved === 'en') setLangState(saved)
  }, [])

  const setLang = (l: Lang) => {
    setLangState(l)
    localStorage.setItem('moltable-lang', l)
    document.documentElement.lang = l
  }

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  return <LanguageContext.Provider value={{ lang, t: translations[lang] as T, setLang }}>{children}</LanguageContext.Provider>
}

export function useLang() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLang must be used within LanguageProvider')
  return ctx
}
