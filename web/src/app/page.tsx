'use client'

import Link from 'next/link'
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
    {
      name: p.free.name,
      price: p.free.price,
      period: '',
      desc: p.free.desc,
      cta: p.free.cta,
      href: '/register',
      features: pricingFeatures.free || [],
    },
    {
      name: p.pro.name,
      price: p.pro.priceMonthly,
      period: '',
      desc: p.pro.desc,
      cta: p.pro.cta,
      badge: p.pro.badge,
      accent: true,
      features: pricingFeatures.pro || [],
    },
    {
      name: p.team.name,
      price: p.team.price,
      period: '',
      desc: p.team.descShort || p.team.desc,
      cta: p.team.cta,
      href: 'mailto:hi@moltable.ai',
      features: pricingFeatures.team || [],
    },
  ]

  return (
    <div className="min-h-screen" style={{ background: '#08090a', color: '#f7f8f8' }}>
      {/* Hero */}
      <section className="relative px-6 pt-24 pb-20 max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-6" 
          style={{ background: 'rgba(113,112,255,0.1)', color: '#9d9cff' }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#7170ff' }} />
          {t.hero.tagline}
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight" style={{ fontWeight: 590, letterSpacing: '-0.5px' }}>
          {t.hero.title}
        </h1>
        <p className="text-lg mb-3" style={{ color: '#8a8f98' }}>
          {t.hero.subtitle}
        </p>
        <p className="text-sm mb-8" style={{ color: '#5a5f68' }}>
          {t.hero.desc}
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/register" className="px-6 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
            {t.pricing.free.cta}
          </Link>
          <Link href="/login" className="px-6 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
            style={{ background: 'rgba(255,255,255,0.06)', color: '#f7f8f8', fontWeight: 510 }}>
            {t.nav.login}
          </Link>
        </div>
        <p className="mt-3 text-xs" style={{ color: '#5a5f68' }}>{(t.hero as any).trust}</p>
        <a href="#persona-demo" className="inline-block mt-4 text-xs transition-all hover:opacity-80"
          style={{ color: '#828fff' }}>
          {(t.hero as any).seeHow}
        </a>
      </section>

      {/* Features */}
      <section className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12" style={{ fontWeight: 590 }}>{t.features.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {t.features.items.map((f: any, i: number) => {
            const Icon = featureIcons[i]
            return (
              <div key={i} className="p-6 rounded-[8px] transition-all duration-200"
                style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
                <Icon size={24} style={{ color: '#7170ff', marginBottom: 12 }} />
                <h3 className="text-base mb-2" style={{ fontWeight: 590 }}>{f.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#8a8f98' }}>{f.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Persona Demo */}
      <section id="persona-demo" className="px-6 py-16 max-w-5xl mx-auto">
        {(() => {
          const pd: any = t.personaDemo
          return (
            <>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-4"
                style={{ background: 'rgba(113,112,255,0.1)', color: '#9d9cff' }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#7170ff' }} />
                {pd.badge}
              </div>
              <h2 className="text-2xl text-center mb-3" style={{ fontWeight: 590 }}>{pd.title}</h2>
              <p className="text-sm text-center mb-10" style={{ color: '#8a8f98' }}>{pd.subtitle}</p>

              {/* Question bubble */}
              <div className="flex flex-col items-center mb-10">
                <div className="inline-flex items-center gap-2 px-5 py-3 rounded-[10px] text-sm"
                  style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(113,112,255,0.35)' }}>
                  <span className="text-xs font-bold px-1.5 py-0.5 rounded" style={{ background: '#7170ff', color: '#fff' }}>Q</span>
                  <span style={{ color: '#f7f8f8' }}>{pd.question}</span>
                </div>
                <span className="text-xs mt-3" style={{ color: '#5a5f68' }}>{pd.questionHint}</span>
              </div>

              {/* Two-column comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">

                {/* Left — Strategic Advisor */}
                <div className="p-6 rounded-[8px] transition-all duration-200"
                  style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(113,112,255,0.28)' }}>
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <h3 className="text-base" style={{ fontWeight: 590, color: '#9d9cff' }}>{pd.left.name}</h3>
                    <span className="text-xs px-2.5 py-1 rounded-full flex-shrink-0"
                      style={{ background: 'rgba(113,112,255,0.12)', color: '#7170ff' }}>{pd.left.role}</span>
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#5a5f68' }}>{pd.traitsLabel}</p>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {pd.left.traits.map((tr: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-[4px]"
                        style={{ background: 'rgba(255,255,255,0.06)', color: '#b0b5bd' }}>{tr}</span>
                    ))}
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#5a5f68' }}>{pd.promptLabel}</p>
                  <div className="text-xs leading-relaxed mb-4 p-3 rounded-[6px] font-mono"
                    style={{ background: 'rgba(255,255,255,0.03)', color: '#8a8f98', boxShadow: '0 0 0 1px rgba(255,255,255,0.05)' }}>
                    {pd.left.prompt}
                  </div>
                  <div className="text-sm leading-relaxed p-4 rounded-[8px]"
                    style={{ background: 'rgba(113,112,255,0.07)', color: '#f7f8f8' }}>
                    {pd.left.reply}
                  </div>
                </div>

                {/* Right — Conservative Auditor */}
                <div className="p-6 rounded-[8px] transition-all duration-200"
                  style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(248,113,113,0.25)' }}>
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <h3 className="text-base" style={{ fontWeight: 590, color: '#f87171' }}>{pd.right.name}</h3>
                    <span className="text-xs px-2.5 py-1 rounded-full flex-shrink-0"
                      style={{ background: 'rgba(248,113,113,0.12)', color: '#f87171' }}>{pd.right.role}</span>
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#5a5f68' }}>{pd.traitsLabel}</p>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {pd.right.traits.map((tr: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-[4px]"
                        style={{ background: 'rgba(255,255,255,0.06)', color: '#b0b5bd' }}>{tr}</span>
                    ))}
                  </div>
                  <p className="text-xs mb-2" style={{ color: '#5a5f68' }}>{pd.promptLabel}</p>
                  <div className="text-xs leading-relaxed mb-4 p-3 rounded-[6px] font-mono"
                    style={{ background: 'rgba(255,255,255,0.03)', color: '#8a8f98', boxShadow: '0 0 0 1px rgba(255,255,255,0.05)' }}>
                    {pd.right.prompt}
                  </div>
                  <div className="text-sm leading-relaxed p-4 rounded-[8px]"
                    style={{ background: 'rgba(248,113,113,0.07)', color: '#f7f8f8' }}>
                    {pd.right.reply}
                  </div>
                </div>
              </div>

              <p className="text-xs text-center mt-8" style={{ color: '#5a5f68' }}>{pd.note}</p>
            </>
          )
        })()}
      </section>

      <hr style={{ borderColor: 'rgba(255,255,255,0.06)' }} />

      {/* Pricing */}
      <section id="pricing" className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-3" style={{ fontWeight: 590 }}>{p.title}</h2>
        <p className="text-sm text-center mb-8" style={{ color: '#8a8f98' }}>
          {p.subtitle}
        </p>

        {/* Pricing cards */}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {pricingPlans.map((plan, i) => (
            <div key={i}
              className={`p-6 rounded-[8px] flex flex-col relative transition-all duration-200 ${plan.accent ? 'md:-mt-2 md:mb-2' : ''}`}
              style={{ 
                background: '#0f1011', 
                boxShadow: plan.accent 
                  ? '0 0 0 1px #7170ff, 0 4px 24px rgba(113,112,255,0.15)' 
                  : '0 0 0 1px rgba(255,255,255,0.06)',
              }}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-xs font-medium"
                  style={{ background: '#7170ff', color: '#fff' }}>
                  {plan.badge}
                </div>
              )}
              <h3 className="text-lg mb-1" style={{ fontWeight: 590 }}>{plan.name}</h3>
              <div className="mb-1">
                <span className="text-3xl" style={{ fontWeight: 590 }}>{plan.price}</span>
                {plan.period && <span className="text-sm" style={{ color: '#8a8f98' }}>{plan.period}</span>}
              </div>
              <div className="mb-4" />
              <p className="text-xs mb-5 flex-1 leading-relaxed" style={{ color: '#8a8f98' }}>{plan.desc}</p>

              <ul className="mb-5 space-y-2">
                {plan.features.map((f: string, j: number) => (
                  <li key={j} className="flex items-start gap-2 text-xs" style={{ color: '#b0b5bd' }}>
                    <Check size={14} style={{ color: '#7170ff', marginTop: 1, flexShrink: 0 }} />
                    {f}
                  </li>
                ))}
              </ul>

              {plan.accent ? (
                <Link href="/register"
                  className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150"
                  style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                  {lang === 'zh' ? 'Pro · 90天免费体验' : 'Pro · 90-Day Free Trial'}
                </Link>
              ) : (
                <Link href={plan.href || '#'}
                  className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150"
                  style={{ background: 'rgba(255,255,255,0.06)', color: '#f7f8f8', fontWeight: 510 }}>
                  {plan.cta}
                </Link>
              )}
            </div>
          ))}
        </div>
      </section>

      <hr style={{ borderColor: 'rgba(255,255,255,0.06)' }} />

      {/* How it works */}
      <section className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12" style={{ fontWeight: 590 }}>{t.how.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {t.how.steps.map((step, i) => (
            <div key={i} className="text-center p-6">
              <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4 text-sm font-bold"
                style={{ background: 'rgba(113,112,255,0.12)', color: '#7170ff' }}>
                {i + 1}
              </div>
              <h3 className="text-base mb-2" style={{ fontWeight: 590 }}>{step.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#8a8f98' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <hr style={{ borderColor: 'rgba(255,255,255,0.06)' }} />

      {/* About */}
      <section id="about" className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-3" style={{ fontWeight: 590 }}>{t.about.mission}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {t.about.architecture.layers.map((layer, i) => {
            const Icon = aboutLayerIcons[i]
            return (
              <div key={i} className="p-6 rounded-[8px] text-center" style={{ background: '#0f1011' }}>
                <Icon size={24} style={{ color: '#7170ff', margin: '0 auto 12px' }} />
                <h4 className="text-sm mb-2" style={{ fontWeight: 590 }}>{layer.name}</h4>
                <p className="text-xs" style={{ color: '#8a8f98' }}>{layer.desc}</p>
              </div>
            )
          })}
        </div>
        <p className="text-sm text-center mt-10" style={{ color: '#8a8f98' }}>{t.about.opensource}</p>
        <Link href="https://github.com/moltable/moltable" 
          className="inline-flex items-center gap-2 mx-auto mt-4 px-4 py-2 rounded-[6px] text-sm font-medium transition-all"
          style={{ background: 'rgba(255,255,255,0.06)', color: '#f7f8f8', display: 'inline-flex' }}>
          <GitBranch size={14} /> {t.about.github}
        </Link>
      </section>

      <hr style={{ borderColor: 'rgba(255,255,255,0.06)' }} />

      {/* Privacy */}
      <section className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12" style={{ fontWeight: 590 }}>{t.privacy.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {t.privacy.items.map((item, i) => {
            const Icon = privacyIcons[i]
            return (
              <div key={i} className="p-5 rounded-[8px] text-center" style={{ background: '#0f1011' }}>
                <Icon size={22} style={{ color: '#7170ff', margin: '0 auto 12px' }} />
                <h3 className="text-sm mb-2" style={{ fontWeight: 590 }}>{item.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: '#8a8f98' }}>{item.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

    </div>
  )
}
