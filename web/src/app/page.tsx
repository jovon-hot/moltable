'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Layers, Zap, Users, Brain, Shield, Code, Check, ArrowRight, GitBranch, Download, Trash2, Mail } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'
import { createCheckout } from '@/lib/api'

const featureIcons = [Layers, Zap, Users, Brain, Shield, Code]
const aboutLayerIcons = [Shield, Users, Layers]
const privacyIcons = [Shield, Download, Trash2, Mail]

export default function LandingPage() {
  const { t } = useLang()
  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [checkoutError, setCheckoutError] = useState('')
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly')

  const handleProCheckout = async () => {
    setCheckoutLoading(true)
    setCheckoutError('')
    try {
      const checkoutUrl = await createCheckout('pro')
      window.location.href = checkoutUrl
    } catch (e: any) {
      if (e.message.includes('Login required')) {
        window.location.href = '/register'
        return
      }
      setCheckoutError(e.message || 'Checkout failed')
      setCheckoutLoading(false)
    }
  }

  useEffect(() => {
    if (window.location.hash) {
      const el = document.getElementById(window.location.hash.slice(1))
      if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 100)
    }
  }, [])

  const pricingPlans = [
    {
      name: t.pricing.free.name, 
      price: t.pricing.free.price, 
      period: '',
      desc: t.pricing.free.desc,
      cta: t.pricing.free.cta, 
      href: '/register',
      features: ['1 个 AI 身份', '2 个 Persona', '100 条记忆', '1 个 Agent', '基础 MCP 工具'],
    },
    {
      name: t.pricing.pro.name, 
      price: billingCycle === 'yearly' ? (t.pricing.pro as any).priceYearlyMonthly : t.pricing.pro.price,
      period: billingCycle === 'yearly' ? '' : '',
      yearPrice: (t.pricing.pro as any).priceYearly,
      desc: billingCycle === 'yearly' ? (t.pricing.pro as any).descShort : t.pricing.pro.desc,
      cta: billingCycle === 'yearly' ? (t.pricing.pro as any).ctaYearly : t.pricing.pro.cta,
      badge: (t.pricing.pro as any).badge,
      accent: true,
      features: ['3 个 AI 身份', '10 个 Persona', '10,000 条记忆', '5 个 Agent', '浏览器插件', '优先支持'],
    },
    {
      name: t.pricing.team.name, 
      price: t.pricing.team.price, 
      period: '',
      desc: (t.pricing.team as any).descShort || t.pricing.team.desc,
      cta: t.pricing.team.cta, 
      href: 'mailto:hi@moltable.ai',
      features: ['10 个 AI 身份', '无限 Persona', '50,000 条记忆', '团队记忆库', '共享 Persona', '管理面板'],
    },
  ]

  return (
    <div className="min-h-screen" style={{ background: '#08090a', color: '#f7f8f8' }}>
      {/* Hero */}
      <section className="relative px-6 pt-24 pb-20 max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-6" 
          style={{ background: 'rgba(113,112,255,0.1)', color: '#9d9cff' }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#7170ff' }} />
          DID+VC · 开源 MIT
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight" style={{ fontWeight: 590, letterSpacing: '-0.5px' }}>
          你的 AI 为什么每次<br />都要重新认识你？
        </h1>
        <p className="text-lg mb-3" style={{ color: '#8a8f98' }}>
          一次注册，所有 AI 都认识你。
        </p>
        <p className="text-sm mb-8" style={{ color: '#5a5f68' }}>
          加载 Moltable Skill → Hermes / Claude / ChatGPT / Cursor / OpenClaw 全通
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/register" className="px-6 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
            {t.pricing.free.cta}
          </Link>
          <Link href="/login" className="px-6 py-2.5 rounded-[6px] text-sm font-medium transition-all hover:opacity-90"
            style={{ background: 'rgba(255,255,255,0.06)', color: '#f7f8f8', fontWeight: 510 }}>
            登录
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-12" style={{ fontWeight: 590 }}>核心能力</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: Layers, title: '跨 AI 身份', desc: '一个身份通用于 Hermes、Claude、ChatGPT、Cursor 等所有支持 MCP 的 AI 助手。' },
            { icon: Zap, title: '自动配置', desc: '接入即完成。Agent 自动加载你的记忆、Persona 和规则，无需人工配置。' },
            { icon: Users, title: '多 Persona', desc: '工作、生活、学习 — 不同场景切换不同人格，各自独立的记忆和偏好。' },
            { icon: Brain, title: '渐进记忆', desc: 'AI 在工作中学到的偏好自动积累。用得越久，AI 越懂你。' },
            { icon: Shield, title: '你拥有数据', desc: '随时随地导出或删除全部数据。我们永远不会用你的数据训练模型。' },
            { icon: Code, title: '开放协议', desc: '基于 MCP 和 DID+VC 开放标准。任何 AI 都可以接入，不锁定平台。' },
          ].map((f, i) => {
            const Icon = f.icon
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

      <hr style={{ borderColor: 'rgba(255,255,255,0.06)' }} />

      {/* Pricing — Bait Design */}
      <section id="pricing" className="px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-2xl text-center mb-3" style={{ fontWeight: 590 }}>{t.pricing.title}</h2>
        <p className="text-sm text-center mb-8" style={{ color: '#8a8f98' }}>
          免费开始，按需升级。7 天无理由退款。
        </p>

        {/* Billing cycle toggle */}
        <div className="flex justify-center mb-10">
          <div className="flex items-center gap-1 p-1 rounded-[6px]" style={{ background: '#0f1011' }}>
            <button onClick={() => setBillingCycle('monthly')}
              className="px-4 py-1.5 rounded-[4px] text-xs font-medium transition-all"
              style={{ 
                background: billingCycle === 'monthly' ? '#7170ff' : 'transparent',
                color: billingCycle === 'monthly' ? '#fff' : '#8a8f98',
              }}>
              月付
            </button>
            <button onClick={() => setBillingCycle('yearly')}
              className="px-4 py-1.5 rounded-[4px] text-xs font-medium transition-all flex items-center gap-1.5"
              style={{ 
                background: billingCycle === 'yearly' ? '#7170ff' : 'transparent',
                color: billingCycle === 'yearly' ? '#fff' : '#8a8f98',
              }}>
              年付 <span style={{ color: billingCycle === 'yearly' ? '#c4ff6b' : '#7170ff', fontSize: 10 }}>省 35%</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {pricingPlans.map((p, i) => (
            <div key={i}
              className={`p-6 rounded-[8px] flex flex-col relative transition-all duration-200 ${
                p.accent ? 'md:-mt-2 md:mb-2' : ''
              }`}
              style={{ 
                background: '#0f1011', 
                boxShadow: p.accent 
                  ? '0 0 0 1px #7170ff, 0 4px 24px rgba(113,112,255,0.15)' 
                  : '0 0 0 1px rgba(255,255,255,0.06)',
              }}
            >
              {p.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-xs font-medium"
                  style={{ background: '#7170ff', color: '#fff' }}>
                  {p.badge}
                </div>
              )}
              <h3 className="text-lg mb-1" style={{ fontWeight: 590 }}>{p.name}</h3>
              <div className="mb-1">
                <span className="text-3xl" style={{ fontWeight: 590 }}>{p.price}</span>
                {p.period && <span className="text-sm" style={{ color: '#8a8f98' }}>{p.period}</span>}
              </div>
              {p.yearPrice && (
                <p className="text-xs mb-4" style={{ color: '#7170ff' }}>{p.yearPrice}</p>
              )}
              {!p.yearPrice && <div className="mb-4" />}
              <p className="text-xs mb-5 flex-1 leading-relaxed" style={{ color: '#8a8f98' }}>{p.desc}</p>

              {/* Feature list */}
              <ul className="mb-5 space-y-2">
                {p.features.map((f, j) => (
                  <li key={j} className="flex items-start gap-2 text-xs" style={{ color: '#b0b5bd' }}>
                    <Check size={14} style={{ color: '#7170ff', marginTop: 1, flexShrink: 0 }} />
                    {f}
                  </li>
                ))}
              </ul>

              {p.accent ? (
                <div>
                  <button onClick={handleProCheckout} disabled={checkoutLoading}
                    className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150 disabled:opacity-50"
                    style={{ background: '#7170ff', color: '#fff', fontWeight: 510 }}>
                    {checkoutLoading ? '跳转中...' : p.cta}
                  </button>
                  {checkoutError && (
                    <p className="text-xs mt-2 text-center" style={{ color: '#f87171' }}>{checkoutError}</p>
                  )}
                </div>
              ) : (
                <Link href={p.href || '#'}
                  className="block w-full text-center px-4 py-2.5 rounded-[6px] text-sm font-medium transition-all duration-150"
                  style={{ background: 'rgba(255,255,255,0.06)', color: '#f7f8f8', fontWeight: 510 }}>
                  {p.cta}
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
          <GitBranch size={14} /> GitHub → 查看源码
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

      {/* Footer */}
      <footer className="px-6 py-12 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        <div className="max-w-5xl mx-auto grid grid-cols-3 gap-8">
          <div>
            <h4 className="text-xs mb-3" style={{ color: '#8a8f98', fontWeight: 590 }}>{t.footer.product}</h4>
            <ul className="space-y-2">
              <li><Link href="/#features" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>功能</Link></li>
              <li><Link href="/#pricing" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>定价</Link></li>
              <li><Link href="/docs" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>文档</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs mb-3" style={{ color: '#8a8f98', fontWeight: 590 }}>{t.footer.resources}</h4>
            <ul className="space-y-2">
              <li><a href="https://github.com/moltable/moltable" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>GitHub</a></li>
              <li><Link href="/blog" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>博客</Link></li>
              <li><Link href="/docs" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>更新日志</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-xs mb-3" style={{ color: '#8a8f98', fontWeight: 590 }}>{t.footer.legal}</h4>
            <ul className="space-y-2">
              <li><Link href="/privacy" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>隐私政策</Link></li>
              <li><a href="#" className="text-xs hover:underline" style={{ color: '#5a5f68' }}>服务条款</a></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  )
}
