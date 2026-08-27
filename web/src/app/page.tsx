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
  const { t } = useLang()
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
    { name: p.ultra.name, price: p.ultra.priceMonthly, period: '', desc: p.ultra.descShort || p.ultra.desc, cta: p.ultra.cta, href: '/register?plan=pro', features: pricingFeatures.ultra || [] },
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
          {t.hero.title}
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
          <a href="#how" className="px-7 py-3 rounded-lg text-sm font-semibold transition-all duration-200 hover:bg-white/5"
            style={{ background: 'rgba(255,255,255,0.04)', color: '#A8A5B8', border: '1px solid rgba(255,255,255,0.08)' }}>
            {(t.hero as any).howCta}
          </a>
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
                  {plan.cta}
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
      <section id="how" className="px-6 py-20 max-w-5xl mx-auto">
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
          <Link href="https://github.com/jovon-hot/moltable"
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
        <div className="flex flex-wrap justify-center gap-5">
          {t.privacy.items.map((item: any, i: number) => {
            const Icon = privacyIcons[i]
            return (
              <div key={i} className="p-5 rounded-xl text-center transition-all duration-200 hover:-translate-y-1 w-full md:w-64"
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
