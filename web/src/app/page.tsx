'use client'

import Link from 'next/link'
import NewsletterSignup from '@/components/NewsletterSignup'
import SocialProof from '@/components/SocialProof'
import { useEffect } from 'react'
import { Layers, Zap, Users, Brain, Shield, Code, Check, ArrowRight, GitBranch, Download, Trash2, Mail } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

const featureIcons = [Layers, Zap, Users, Brain, Shield, Code]
const aboutLayerIcons = [Shield, Users, Layers]
const privacyIcons = [Shield, Download, Trash2, Mail]

export default function LandingPage() {
  const { t, lang } = useLang()
  const p = t.pricing as any
  const pricingFeatures = (t.pricing as any).features || {}

  useEffect(() => {
    if (window.location.hash) {
      const el = document.getElementById(window.location.hash.slice(1))
      if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 100)
    }
  }, [])

  const pricingPlans = [
    { name: p.free.name, price: p.free.price, period: '', desc: p.free.desc, cta: p.free.cta, href: '/register', features: pricingFeatures.free || [] },
    { name: p.pro.name, price: p.pro.priceMonthly, period: '', desc: p.pro.desc, cta: p.pro.cta, badge: p.pro.badge, accent: true, features: pricingFeatures.pro || [] },
    { name: p.team.name, price: p.team.price, period: '', desc: p.team.descShort || p.team.desc, cta: p.team.cta, href: 'mailto:hi@moltable.ai', features: pricingFeatures.team || [] },
  ]

  return (
    <div className="min-h-screen" style={{ background: '#0D0D14', color: '#F5F4F8' }}>
      
      {/* ── Hero ── */}
      <section className="relative px-6 pt-28 pb-24 max-w-4xl mx-auto text-center overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[700px] pointer-events-none"
          style={{ background: 'radial-gradient(circle at 45% 30%, rgba(99,102,241,0.08), transparent 55%), radial-gradient(circle at 60% 40%, rgba(251,107,75,0.04), transparent 55%)' }} />
        
        {/* Pill badge */}
        <div className="relative inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs mb-8"
          style={{ background: 'rgba(99,102,241,0.1)', color: '#A5B4FC', border: '1px solid rgba(99,102,241,0.12)' }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#6366F1' }} />
          {t.hero.tagline}
        </div>

        <h1 className="relative text-5xl md:text-6xl font-extrabold mb-5 leading-tight" 
          style={{ letterSpacing: '-1.5px', fontWeight: 800 }}>
          <span style={{ color: '#F5F4F8' }}>AI meets </span>
          <span style={{ color: '#FB6B4B' }}>Identity</span>
        </h1>
        <p className="relative text-lg mb-2" style={{ color: '#A8A5B8' }}>
          {t.hero.subtitle}
        </p>
        <p className="relative text-sm mb-10" style={{ color: '#85829E' }}>
          {t.hero.desc}
        </p>
        <div className="relative flex items-center justify-center gap-3">
          <Link href="/register" className="px-7 py-3 rounded-lg text-sm font-semibold transition-all duration-200 hover:-translate-y-0.5"
            style={{ background: '#4338CA', color: '#fff', boxShadow: '0 0 0 1px rgba(99,102,241,0.3)' }}>
            {(t.hero as any).heroCta}
          </Link>
          <Link href="/login" className="px-7 py-3 rounded-lg text-sm font-semibold transition-all duration-200 hover:bg-white/5"
            style={{ background: 'rgba(255,255,255,0.04)', color: '#A8A5B8', border: '1px solid rgba(255,255,255,0.08)' }}>
            {t.nav.login}
          </Link>
        </div>
        <p className="relative mt-4 text-xs" style={{ color: '#6E6B80' }}>{(t.hero as any).trust}</p>
        <p className="relative mt-1 text-xs" style={{ color: '#6366F1' }}>{(t.hero as any).trust2}</p>
        <div className="relative mt-4">
          <SocialProof />
        </div>
        <a href="#pricing" className="relative inline-block mt-6 text-xs transition-all hover:opacity-80" 
          style={{ color: '#4338CA' }}>
          {(t.hero as any).seeHow || 'See pricing →'}
        </a>
      </section>

      {/* Gradient divider */}
      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.5 }} />
      </div>

      {/* ── Features ── */}
      <section id="features" className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-4 font-bold" style={{ letterSpacing: '-0.3px' }}>{t.features.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
          {t.features.items.map((f: any, i: number) => {
            const Icon = featureIcons[i]
            const iconColors = ['#6366F1', '#FB6B4B', '#6366F1', '#FB6B4B', '#6366F1', '#FB6B4B']
            const iconBgs = ['rgba(99,102,241,0.12)', 'rgba(251,107,75,0.1)', 'rgba(99,102,241,0.12)', 'rgba(251,107,75,0.1)', 'rgba(99,102,241,0.12)', 'rgba(251,107,75,0.1)']
            return (
              <div key={i} className="p-6 rounded-xl transition-all duration-300 hover:-translate-y-1 group"
                style={{ background: '#14141E', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                  style={{ background: iconBgs[i] }}>
                  <Icon size={20} style={{ color: iconColors[i] }} />
                </div>
                <h3 className="text-base mb-2 font-semibold">{f.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#85829E' }}>{f.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Persona Demo ── */}
      <section id="persona-demo" className="px-6 py-20 max-w-5xl mx-auto">
        {(() => {
          const pd: any = t.personaDemo
          return (
            <>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-4"
                style={{ background: 'rgba(99,102,241,0.1)', color: '#A5B4FC' }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#6366F1' }} />
                {pd.badge}
              </div>
              <h2 className="text-2xl text-center mb-3 font-bold">{pd.title}</h2>
              <p className="text-sm text-center mb-10" style={{ color: '#85829E' }}>{pd.subtitle}</p>
              <div className="flex flex-col items-center mb-10">
                <div className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm"
                  style={{ background: '#14141E', border: '1px solid rgba(99,102,241,0.25)' }}>
                  <span className="text-xs font-bold px-1.5 py-0.5 rounded" style={{ background: '#4338CA', color: '#fff' }}>Q</span>
                  <span style={{ color: '#F5F4F8' }}>{pd.question}</span>
                </div>
                <span className="text-xs mt-3" style={{ color: '#6E6B80' }}>{pd.questionHint}</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                <div className="p-6 rounded-xl transition-all duration-200"
                  style={{ background: '#14141E', border: '1px solid rgba(99,102,241,0.18)' }}>
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <h3 className="text-base font-semibold" style={{ color: '#A5B4FC' }}>{pd.left.name}</h3>
                    <span className="text-xs px-2.5 py-1 rounded-full" style={{ background: 'rgba(99,102,241,0.12)', color: '#6366F1' }}>{pd.left.role}</span>
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#6E6B80' }}>{pd.traitsLabel}</p>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {pd.left.traits.map((tr: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-md" style={{ background: 'rgba(255,255,255,0.05)', color: '#ccc' }}>{tr}</span>
                    ))}
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#6E6B80' }}>{pd.promptLabel}</p>
                  <div className="text-xs leading-relaxed mb-4 p-3 rounded-lg font-mono"
                    style={{ background: 'rgba(255,255,255,0.02)', color: '#85829E', border: '1px solid rgba(255,255,255,0.04)' }}>
                    {pd.left.prompt}
                  </div>
                  <div className="text-sm leading-relaxed p-4 rounded-lg"
                    style={{ background: 'rgba(99,102,241,0.06)', color: '#F5F4F8' }}>
                    {pd.left.reply}
                  </div>
                </div>
                <div className="p-6 rounded-xl transition-all duration-200"
                  style={{ background: '#14141E', border: '1px solid rgba(248,113,113,0.18)' }}>
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <h3 className="text-base font-semibold" style={{ color: '#FCA5A5' }}>{pd.right.name}</h3>
                    <span className="text-xs px-2.5 py-1 rounded-full" style={{ background: 'rgba(248,113,113,0.12)', color: '#F87171' }}>{pd.right.role}</span>
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#6E6B80' }}>{pd.traitsLabel}</p>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {pd.right.traits.map((tr: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-md" style={{ background: 'rgba(255,255,255,0.05)', color: '#ccc' }}>{tr}</span>
                    ))}
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#6E6B80' }}>{pd.promptLabel}</p>
                  <div className="text-xs leading-relaxed mb-4 p-3 rounded-lg font-mono"
                    style={{ background: 'rgba(255,255,255,0.02)', color: '#85829E', border: '1px solid rgba(255,255,255,0.04)' }}>
                    {pd.right.prompt}
                  </div>
                  <div className="text-sm leading-relaxed p-4 rounded-lg"
                    style={{ background: 'rgba(248,113,113,0.06)', color: '#F5F4F8' }}>
                    {pd.right.reply}
                  </div>
                </div>
              </div>
              <p className="text-xs text-center mt-8" style={{ color: '#6E6B80' }}>{pd.note}</p>
            </>
          )
        })()}
      </section>

      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.4 }} />
      </div>

      {/* ── Pricing ── */}
      <section id="pricing" className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-3 font-bold">{p.title}</h2>
        <p className="text-sm text-center mb-10" style={{ color: '#85829E' }}>{p.subtitle}</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {pricingPlans.map((plan, i) => (
            <div key={i} className={`p-6 rounded-xl flex flex-col relative transition-all duration-300 hover:-translate-y-1 ${plan.accent ? 'md:-mt-2 md:mb-2' : ''}`}
              style={{ background: '#14141E', border: plan.accent ? '1px solid rgba(99,102,241,0.25)' : '1px solid rgba(255,255,255,0.06)', boxShadow: plan.accent ? '0 4px 30px rgba(67,56,202,0.1)' : 'none' }}>
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-xs font-semibold"
                  style={{ background: '#4338CA', color: '#fff' }}>{plan.badge}</div>
              )}
              <h3 className="text-lg mb-1 font-semibold">{plan.name}</h3>
              <div className="mb-1"><span className="text-3xl font-bold">{plan.price}</span>{plan.period && <span className="text-sm ml-1" style={{ color: '#85829E' }}>{plan.period}</span>}</div>
              <div className="mb-4" />
              <p className="text-xs mb-5 flex-1 leading-relaxed" style={{ color: '#85829E' }}>{plan.desc}</p>
              <ul className="mb-5 space-y-2">
                {plan.features.map((f: string, j: number) => (
                  <li key={j} className="flex items-start gap-2 text-xs" style={{ color: '#ccc' }}>
                    <Check size={14} style={{ color: '#6366F1', marginTop: 1, flexShrink: 0 }} />{f}
                  </li>
                ))}
              </ul>
              {plan.accent ? (
                <Link href="/register" className="block w-full text-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90"
                  style={{ background: '#4338CA', color: '#fff' }}>
                  {lang === 'zh' ? 'Pro · 90天免费体验' : 'Pro · 90-Day Free Trial'}
                </Link>
              ) : (
                <Link href={plan.href || '#'} className="block w-full text-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all hover:bg-white/5"
                  style={{ background: 'rgba(255,255,255,0.04)', color: '#F5F4F8', border: '1px solid rgba(255,255,255,0.08)' }}>
                  {plan.cta}
                </Link>
              )}
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.4 }} />
      </div>

      {/* ── How it works ── */}
      <section className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12 font-bold">{t.how.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {t.how.steps.map((step: any, i: number) => (
            <div key={i} className="text-center p-6">
              <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4 text-sm font-bold"
                style={{ background: 'rgba(99,102,241,0.12)', color: '#6366F1' }}>{i + 1}</div>
              <h3 className="text-base mb-2 font-semibold">{step.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#85829E' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.4 }} />
      </div>

      {/* ── About ── */}
      <section id="about" className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-3 font-bold">{t.about.mission}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {t.about.architecture.layers.map((layer: any, i: number) => {
            const Icon = aboutLayerIcons[i]
            return (
              <div key={i} className="p-6 rounded-xl text-center transition-all duration-200 hover:-translate-y-1"
                style={{ background: '#14141E', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Icon size={24} style={{ color: '#6366F1', margin: '0 auto 12px' }} />
                <h4 className="text-sm mb-2 font-semibold">{layer.name}</h4>
                <p className="text-xs" style={{ color: '#85829E' }}>{layer.desc}</p>
              </div>
            )
          })}
        </div>
        <p className="text-sm text-center mt-10" style={{ color: '#85829E' }}>{t.about.opensource}</p>
        <div className="text-center mt-4">
          <Link href="https://github.com/Moltable"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:bg-white/5"
            style={{ background: 'rgba(255,255,255,0.04)', color: '#A8A5B8', border: '1px solid rgba(255,255,255,0.08)' }}>
            <GitBranch size={14} /> {t.about.github}
          </Link>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.4 }} />
      </div>

      {/* ── Privacy ── */}
      <section className="px-6 py-20 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12 font-bold">{t.privacy.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          {t.privacy.items.map((item: any, i: number) => {
            const Icon = privacyIcons[i]
            return (
              <div key={i} className="p-5 rounded-xl text-center transition-all duration-200 hover:-translate-y-1"
                style={{ background: '#14141E', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Icon size={22} style={{ color: '#6366F1', margin: '0 auto 12px' }} />
                <h3 className="text-sm mb-2 font-semibold">{item.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: '#85829E' }}>{item.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px" style={{ background: 'linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)', opacity: 0.4 }} />
      </div>

      {/* ── Newsletter ── */}
      <section className="px-6 py-20 max-w-lg mx-auto">
        <NewsletterSignup variant="card" />
      </section>

      {/* Footer spacer */}
      <div className="h-16" />
    </div>
  )
}
