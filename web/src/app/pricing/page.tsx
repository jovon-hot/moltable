'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Check } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'
import { getPlans } from '@/lib/api'

type Period = 'monthly' | 'quarterly' | 'yearly'

export default function PricingPage() {
  const { t, lang } = useLang()
  const p = t.pricing as any
  const pricingFeatures = p.features || {}
  const [plansData, setPlans] = useState<any>(null)
  const [period, setPeriod] = useState<Period>('monthly')

  useEffect(() => {
    getPlans().then(setPlans).catch(() => {})
  }, [])

  // Stripe 已接入(mode=paid)时显示真实 USD 价格;未接入回退到静态文案
  const paid = plansData?.mode === 'paid'
  const hasQuarterly = paid && (plansData.pro?.price_quarterly || 0) > 0

  const periods = ([
    { id: 'monthly', label: lang === 'zh' ? '月付' : 'Monthly' },
    { id: 'quarterly', label: lang === 'zh' ? '季付' : 'Quarterly' },
    { id: 'yearly', label: lang === 'zh' ? '年付' : 'Yearly' },
  ] as const).filter(x => x.id !== 'quarterly' || hasQuarterly)

  const fmt = (amount: number, p: Period) => {
    const suffix = lang === 'zh'
      ? { monthly: '/月', quarterly: '/季', yearly: '/年' } as const
      : { monthly: '/mo', quarterly: '/qtr', yearly: '/yr' } as const
    return `$${amount.toFixed(0)}${suffix[p]}`
  }

  const priceOf = (key: 'pro' | 'team') => {
    if (!paid) return null
    const d = plansData[key]
    if (period === 'quarterly' && hasQuarterly) return d.price_quarterly
    if (period === 'yearly') return d.price_yearly
    return d.price_monthly
  }

  const plans = [
    {
      name: plansData?.free?.name || p.free.name,
      price: '$0',
      desc: p.free.desc,
      cta: p.free.cta,
      href: '/register',
      features: plansData?.free?.features || pricingFeatures.free || [],
    },
    {
      name: plansData?.pro?.name || p.pro.name,
      price: paid ? fmt(priceOf('pro') ?? 0, period) : p.pro.priceMonthly,
      desc: p.pro.desc,
      cta: p.pro.cta,
      badge: p.pro.badge,
      accent: true,
      href: '/register?plan=pro',
      features: plansData?.pro?.features || pricingFeatures.pro || [],
    },
    {
      name: plansData?.team?.name || p.team.name,
      price: paid ? fmt(priceOf('team') ?? 0, period) : p.team.price,
      desc: p.team.descShort || p.team.desc,
      cta: p.team.cta,
      href: 'mailto:hi@moltable.ai',
      features: plansData?.team?.features || pricingFeatures.team || [],
    },
  ]

  return (
    <div className="min-h-screen" style={{ background: '#0D0D14', color: '#ffffff' }}>
      <section className="px-6 pt-24 pb-20 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl mb-3" style={{ fontWeight: 590, letterSpacing: '-0.3px' }}>
            {p.title}
          </h1>
          <p className="text-sm" style={{ color: '#888888' }}>
            {p.subtitle}
          </p>
        </div>

        {paid && periods.length > 1 && (
          <div className="flex justify-center mb-8">
            <div className="inline-flex rounded-[8px] p-1" style={{ background: 'rgba(255,255,255,0.04)' }}>
              {periods.map(x => (
                <button key={x.id} onClick={() => setPeriod(x.id)}
                  className="px-5 py-2 rounded-[6px] text-sm font-medium transition-all"
                  style={{
                    background: period === x.id ? '#4338CA' : 'transparent',
                    color: period === x.id ? '#fff' : '#888888',
                    fontWeight: period === x.id ? 590 : 400,
                  }}>
                  {x.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {plans.map((plan, i) => (
            <div key={i}
              className={`p-6 rounded-[8px] flex flex-col relative transition-all duration-200 ${plan.accent ? 'md:-mt-2 md:mb-2' : ''}`}
              style={{
                background: '#14141E',
                boxShadow: plan.accent
                  ? '0 0 0 1px #4338CA, 0 4px 24px rgba(67,56,202,0.15)'
                  : '0 0 0 1px rgba(255,255,255,0.06)',
              }}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-xs font-medium"
                  style={{ background: '#4338CA', color: '#fff' }}>
                  {plan.badge}
                </div>
              )}
              <h3 className="text-lg mb-1" style={{ fontWeight: 590 }}>{plan.name}</h3>
              <div className="mb-4">
                <span className="text-3xl" style={{ fontWeight: 590 }}>{plan.price}</span>
              </div>
              <p className="text-xs mb-5 flex-1 leading-relaxed" style={{ color: '#888888' }}>{plan.desc}</p>

              <ul className="mb-5 space-y-2">
                {plan.features.map((f: string, j: number) => (
                  <li key={j} className="flex items-start gap-2 text-xs" style={{ color: '#cccccc' }}>
                    <Check size={14} style={{ color: '#4338CA', marginTop: 1, flexShrink: 0 }} />
                    {f}
                  </li>
                ))}
              </ul>

              <Link href={plan.href}
                className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150"
                style={{
                  background: plan.accent ? '#4338CA' : 'rgba(255,255,255,0.06)',
                  color: plan.accent ? '#fff' : '#ffffff',
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
