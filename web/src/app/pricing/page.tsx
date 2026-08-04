'use client'

import Link from 'next/link'
import { Check } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

export default function PricingPage() {
  const { t, lang } = useLang()
  const p = t.pricing as any
  const pricingFeatures = p.features || {}

  const plans = [
    {
      name: p.free.name,
      price: p.free.price,
      desc: p.free.desc,
      cta: p.free.cta,
      href: '/register',
      features: pricingFeatures.free || [],
    },
    {
      name: p.pro.name,
      price: p.pro.priceMonthly,
      desc: p.pro.desc,
      cta: lang === 'zh' ? 'Pro · 90天免费体验' : 'Pro · 90-Day Free Trial',
      badge: p.pro.badge,
      accent: true,
      href: '/register?plan=pro',
      features: pricingFeatures.pro || [],
    },
    {
      name: p.team.name,
      price: p.team.price,
      desc: p.team.descShort || p.team.desc,
      cta: p.team.cta,
      href: 'mailto:hi@moltable.ai',
      features: pricingFeatures.team || [],
    },
  ]

  return (
    <div className="min-h-screen" style={{ background: '#08090a', color: '#f7f8f8' }}>
      <section className="px-6 pt-24 pb-20 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl mb-3" style={{ fontWeight: 590, letterSpacing: '-0.3px' }}>
            {p.title}
          </h1>
          <p className="text-sm" style={{ color: '#8a8f98' }}>
            {p.subtitle}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {plans.map((plan, i) => (
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
              <div className="mb-4">
                <span className="text-3xl" style={{ fontWeight: 590 }}>{plan.price}</span>
              </div>
              <p className="text-xs mb-5 flex-1 leading-relaxed" style={{ color: '#8a8f98' }}>{plan.desc}</p>

              <ul className="mb-5 space-y-2">
                {plan.features.map((f: string, j: number) => (
                  <li key={j} className="flex items-start gap-2 text-xs" style={{ color: '#b0b5bd' }}>
                    <Check size={14} style={{ color: '#7170ff', marginTop: 1, flexShrink: 0 }} />
                    {f}
                  </li>
                ))}
              </ul>

              <Link href={plan.href}
                className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150"
                style={{
                  background: plan.accent ? '#7170ff' : 'rgba(255,255,255,0.06)',
                  color: plan.accent ? '#fff' : '#f7f8f8',
                  fontWeight: 510,
                }}>
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
