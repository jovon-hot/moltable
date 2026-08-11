'use client'

import Link from 'next/link'
import { Check, X, Minus, ArrowRight, Layers, Brain, Shield, Zap, Users, Database, Globe, Code } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

const comparisonData = {
  zh: {
    hero: {
      title: 'AI Agent 记忆与身份平台对比 2026',
      subtitle: 'Moltable vs mem0 vs Zep — 谁才是 Agent 基础设施的最佳选择？',
      updated: '2026-08-06',
    },
    intro: '随着 AI Agent 生态爆发式增长，记忆/身份基础设施赛道也进入了白热化竞争。本文从架构、功能、定价、生态、开源五个维度，对三大主流平台进行全面对比，帮助开发者和团队做出最佳技术选型。',
    overview: {
      title: '平台概览',
      moltable: {
        name: 'Moltable.ai',
        positioning: 'AI Identity Layer — 跨平台身份同步',
        founded: '2026',
        license: 'MIT',
        protocol: 'MCP Native',
        lang: 'Python + TypeScript',
      },
      mem0: {
        name: 'mem0',
        positioning: 'Universal Memory Layer',
        founded: '2024',
        license: 'Apache 2.0 (OSS) / Proprietary (Pro)',
        protocol: 'MCP + REST API',
        lang: 'Python + TypeScript',
      },
      zep: {
        name: 'Zep',
        positioning: 'Memory for AI Agents',
        founded: '2023',
        license: 'Apache 2.0 (OSS) / Proprietary (Cloud)',
        protocol: 'REST + gRPC',
        lang: 'Go + Python SDK',
      },
    },
    features: {
      title: '功能对比',
      rows: [
        { feature: '跨平台 Identity Sync', moltable: true, mem0: false, zep: false },
        { feature: '多 Persona 管理', moltable: true, mem0: false, zep: false },
        { feature: 'Agent 自动配给 (Provision)', moltable: true, mem0: false, zep: false },
        { feature: '语义记忆存储', moltable: true, mem0: true, zep: true },
        { feature: '向量搜索', moltable: true, mem0: true, zep: true },
        { feature: '时间衰减记忆', moltable: true, mem0: true, zep: false },
        { feature: '时间记忆时间线', moltable: true, mem0: false, zep: true },
        { feature: '记忆去重', moltable: true, mem0: true, zep: false },
        { feature: '记忆健康评分', moltable: true, mem0: false, zep: false },
        { feature: '图记忆 / 知识图谱', moltable: false, mem0: true, zep: true },
        { feature: 'MCP Server', moltable: true, mem0: true, zep: true },
        { feature: '多 Agent 支持', moltable: true, mem0: true, zep: true },
        { feature: '加密存储 (传输+静态)', moltable: true, mem0: true, zep: true },
        { feature: '自托管 (Self-host)', moltable: true, mem0: true, zep: true },
        { feature: 'DID / 可验证凭证', moltable: true, mem0: false, zep: false },
        { feature: 'CLI 工具', moltable: true, mem0: true, zep: false },
        { feature: 'Web Dashboard', moltable: true, mem0: true, zep: true },
      ],
    },
    pricing: {
      title: '定价对比',
      moltable: { free: '100 条记忆 / 2 Persona', pro: '90 天免费试用', team: '联系销售' },
      mem0: { free: '开源免费', pro: '$249/月', team: '企业定制' },
      zep: { free: '开源免费', pro: '$99/月起', team: '企业定制' },
    },
    architecture: {
      title: '架构对比',
      moltable: 'Identity → Persona → Agent 三层架构。以「身份」为原子单位，Persona 提供多角色切换，Agent 层负责 MCP 协议分发。加密存储（TLS 传输 + 数据库静态加密），数据完全由用户控制。',
      mem0: 'Memory → User → Agent 三层。以「记忆」为最小单位，专注记忆的存储、检索和管理。Pro 版增加团队协作，但不涉及身份和 Persona 概念。',
      zep: 'Memory → Graph → User。以「记忆 + 知识图谱」为核心，在记忆之上构建实体关系图。适合需要复杂上下文推理的场景，但学习曲线较陡。',
    },
    strengths: {
      title: '各自优势',
      moltable: [
        '唯一提供「身份层」的平台，解决「Agent 不认识你」的根本问题',
        '跨设备同步：换电脑 3 分钟恢复完整 AI 环境',
        'MCP Native 设计，零配置接入主流 Agent',
        'MIT 开源 + 90 天免费试用',
        '支持 DID 去中心化身份，未来可扩展至 Web3',
        '时间记忆时间线 — 追踪事实随时间的变化，支持振荡/渐变/突变模式检测',
        '记忆健康评分 — 四维评分（新鲜度/完整性/去重/矛盾检测）与自动清理',
      ],
      mem0: [
        '62K+ GitHub Stars，最大的 AI Memory OSS 社区',
        '丰富的 Agent 插件生态（Claude, Cursor, Codex, n8n）',
        '双语言 SDK（Python + TypeScript）',
        'YC 背书，企业级支持',
        'Mintlify 驱动的优质文档站',
      ],
      zep: [
        '唯一内置知识图谱的 Memory 平台',
        'Go 语言实现，高性能',
        '支持 gRPC 协议，适合高吞吐场景',
        '丰富的企业级功能（SSO, RBAC, Audit Log）',
        '最早的 Agent Memory 产品之一（2023 年）',
      ],
    },
    usecases: {
      title: '推荐场景',
      moltable: [
        '个人开发者 / AI 重度用户：需要跨设备、跨 Agent 保持 AI 记忆',
        '多 Agent 工作流：Claude + Cursor + Codex 同时协作',
        '注重隐私和数据主权：需要加密存储、自托管',
        'AI 身份基础设施：构建基于 Identity 的应用',
      ],
      mem0: [
        '构建 AI 应用的开发者：需要在产品中嵌入记忆能力',
        '开源优先的团队：需要最大的社区和生态支持',
        '已有明确用户系统的产品：只需记忆存储和检索',
        '需要企业级 SLA 和商业支持的项目',
      ],
      zep: [
        '需要知识图谱推理的复杂应用',
        '高吞吐、低延迟的实时记忆系统',
        '已有成熟基础设施的大中型企业',
        '需要 SSO、RBAC、审计日志等企业安全功能',
      ],
    },
    verdict: {
      title: '如何选择？',
      lines: [
        '如果你是个人开发者或 AI 重度用户，想要「换电脑不换记忆」的体验 → 选 Moltable',
        '如果你在构建 AI 产品，需要嵌入记忆能力且看重社区生态 → 选 mem0',
        '如果你需要知识图谱 + 企业级安全和性能 → 选 Zep',
        '如果你既需要记忆又需要身份层 → Moltable 是唯一选择',
      ],
    },
    cta: '免费开始使用 Moltable →',
    footer: '以上对比基于 2026-08-06 各平台公开信息。功能和定价可能随时更新，请以各平台官网为准。',
  },
  en: {
    hero: {
      title: 'AI Agent Memory & Identity Platform Comparison 2026',
      subtitle: 'Moltable vs mem0 vs Zep — Which is the best infrastructure for AI Agents?',
      updated: '2026-08-06',
    },
    intro: 'As the AI Agent ecosystem explodes, the memory/identity infrastructure space is heating up. This article provides a comprehensive comparison across architecture, features, pricing, ecosystem, and open-source commitment to help you make the right technology choice.',
    overview: {
      title: 'Platform Overview',
      moltable: {
        name: 'Moltable.ai',
        positioning: 'AI Identity Layer — Cross-platform identity sync',
        founded: '2026',
        license: 'MIT',
        protocol: 'MCP Native',
        lang: 'Python + TypeScript',
      },
      mem0: {
        name: 'mem0',
        positioning: 'Universal Memory Layer',
        founded: '2024',
        license: 'Apache 2.0 (OSS) / Proprietary (Pro)',
        protocol: 'MCP + REST API',
        lang: 'Python + TypeScript',
      },
      zep: {
        name: 'Zep',
        positioning: 'Memory for AI Agents',
        founded: '2023',
        license: 'Apache 2.0 (OSS) / Proprietary (Cloud)',
        protocol: 'REST + gRPC',
        lang: 'Go + Python SDK',
      },
    },
    features: {
      title: 'Feature Comparison',
      rows: [
        { feature: 'Cross-platform Identity Sync', moltable: true, mem0: false, zep: false },
        { feature: 'Multi-Persona Management', moltable: true, mem0: false, zep: false },
        { feature: 'Agent Auto-Provisioning', moltable: true, mem0: false, zep: false },
        { feature: 'Semantic Memory Storage', moltable: true, mem0: true, zep: true },
        { feature: 'Vector Search', moltable: true, mem0: true, zep: true },
        { feature: 'Time-Decay Memory', moltable: true, mem0: true, zep: false },
        { feature: 'Temporal Memory Timeline', moltable: true, mem0: false, zep: true },
        { feature: 'Memory Deduplication', moltable: true, mem0: true, zep: false },
        { feature: 'Memory Health Scoring', moltable: true, mem0: false, zep: false },
        { feature: 'Graph Memory / Knowledge Graph', moltable: false, mem0: true, zep: true },
        { feature: 'MCP Server', moltable: true, mem0: true, zep: true },
        { feature: 'Multi-Agent Support', moltable: true, mem0: true, zep: true },
        { feature: 'Encryption (TLS+At-Rest)', moltable: true, mem0: true, zep: true },
        { feature: 'Self-Hosting', moltable: true, mem0: true, zep: true },
        { feature: 'DID / Verifiable Credentials', moltable: true, mem0: false, zep: false },
        { feature: 'CLI Tool', moltable: true, mem0: true, zep: false },
        { feature: 'Web Dashboard', moltable: true, mem0: true, zep: true },
      ],
    },
    pricing: {
      title: 'Pricing Comparison',
      moltable: { free: '100 memories / 2 Personas', pro: '90-day free trial', team: 'Contact sales' },
      mem0: { free: 'OSS free', pro: '$249/mo', team: 'Enterprise custom' },
      zep: { free: 'OSS free', pro: 'From $99/mo', team: 'Enterprise custom' },
    },
    architecture: {
      title: 'Architecture Comparison',
      moltable: 'Identity → Persona → Agent three-layer architecture. Identity as the atomic unit, Persona for multi-role switching, Agent layer for MCP protocol distribution. Encrypted storage (TLS transit + DB at-rest), full user data control.',
      mem0: 'Memory → User → Agent three layers. Memory as the smallest unit, focused on storage, retrieval, and management. Pro tier adds team collaboration without Identity/Persona concepts.',
      zep: 'Memory → Graph → User. Core is memory + knowledge graph, building entity relationship graphs on top of memories. Suitable for complex context reasoning but has a steeper learning curve.',
    },
    strengths: {
      title: 'Key Strengths',
      moltable: [
        'Only platform with an Identity Layer — solves the "Agent doesn\'t know you" problem',
        'Cross-device sync: restore full AI environment in 3 minutes',
        'MCP Native design, zero-config integration with major Agents',
        'MIT open-source + 90-day free trial',
        'DID-based decentralized identity, future-ready for Web3',
        'Temporal Memory Timeline — track fact changes over time with oscillation/gradual/rapid change pattern detection',
        'Memory Health Scoring — four-dimensional scoring (freshness/completeness/duplication/contradiction) with auto-cleanup',
      ],
      mem0: [
        '62K+ GitHub Stars, largest AI Memory OSS community',
        'Rich Agent plugin ecosystem (Claude, Cursor, Codex, n8n)',
        'Dual-language SDK (Python + TypeScript)',
        'YC-backed, enterprise-grade support',
        'Excellent Mintlify-powered documentation',
      ],
      zep: [
        'Only platform with built-in knowledge graph',
        'Go implementation, high performance',
        'gRPC support for high-throughput scenarios',
        'Rich enterprise features (SSO, RBAC, Audit Log)',
        'One of the earliest Agent Memory products (2023)',
      ],
    },
    usecases: {
      title: 'Recommended Use Cases',
      moltable: [
        'Individual developers / AI power users: need cross-device, cross-Agent memory persistence',
        'Multi-Agent workflows: Claude + Cursor + Codex collaborating simultaneously',
        'Privacy-conscious: need encrypted storage and self-hosting',
        'AI Identity infrastructure: building Identity-based applications',
      ],
      mem0: [
        'Developers building AI products: need to embed memory capabilities',
        'Open-source-first teams: value community and ecosystem',
        'Products with existing user systems: just need memory storage/retrieval',
        'Projects needing enterprise SLA and commercial support',
      ],
      zep: [
        'Complex applications needing knowledge graph reasoning',
        'High-throughput, low-latency real-time memory systems',
        'Mid-to-large enterprises with established infrastructure',
        'Need SSO, RBAC, audit logging, and enterprise security features',
      ],
    },
    verdict: {
      title: 'How to Choose?',
      lines: [
        'Individual dev or AI power user wanting "new machine, same memory" → Choose Moltable',
        'Building AI products, need embeddable memory with strong community → Choose mem0',
        'Need knowledge graph + enterprise security and performance → Choose Zep',
        'Need both memory AND identity layer → Moltable is the only option',
      ],
    },
    cta: 'Start Free with Moltable →',
    footer: 'Comparison based on publicly available information as of 2026-08-06. Features and pricing may change; check each platform\'s official website.',
  },
}

export default function ComparePage() {
  const { lang } = useLang()
  const d = comparisonData[lang === 'en' ? 'en' : 'zh']

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-28 pb-12 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-6"
          style={{ background: 'rgba(67,56,202,0.1)', color: '#9d9cff' }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#4338CA' }} />
          {lang === 'en' ? 'Comprehensive Comparison' : '全面对比'}
        </div>
        <h1 className="text-3xl md:text-4xl font-heading tracking-[-0.4px] mb-4 font-bold">
          {d.hero.title}
        </h1>
        <p className="text-lg text-ln-secondary mb-6">{d.hero.subtitle}</p>
        <p className="text-sm text-ln-tertiary max-w-2xl mx-auto leading-relaxed">{d.intro}</p>
        <p className="text-xs text-ln-tertiary mt-4">
          {lang === 'en' ? 'Last updated: ' : '最后更新：'}{d.hero.updated}
        </p>
      </section>

      {/* Platform Overview Cards */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.overview.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(['moltable', 'mem0', 'zep'] as const).map((key) => {
            const p = d.overview[key]
            const isMoltable = key === 'moltable'
            return (
              <div key={key} className="p-6 rounded-card bg-ln-panel relative"
                style={{
                  boxShadow: isMoltable
                    ? '0 0 0 1px #4338CA, 0 4px 24px rgba(67,56,202,0.12)'
                    : '0 0 0 1px rgba(255,255,255,0.06)',
                }}>
                {isMoltable && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-xs font-medium"
                    style={{ background: '#4338CA', color: '#fff' }}>
                    {lang === 'en' ? 'RECOMMENDED' : '推荐'}
                  </div>
                )}
                <h3 className="text-lg font-heading mb-3 font-semibold">{p.name}</h3>
                <p className="text-sm text-ln-accent mb-4">{p.positioning}</p>
                <div className="space-y-2 text-xs text-ln-secondary">
                  <div className="flex justify-between"><span className="text-ln-tertiary">{lang === 'en' ? 'Founded' : '成立'}</span><span>{p.founded}</span></div>
                  <div className="flex justify-between"><span className="text-ln-tertiary">{lang === 'en' ? 'License' : '许可'}</span><span>{p.license}</span></div>
                  <div className="flex justify-between"><span className="text-ln-tertiary">{lang === 'en' ? 'Protocol' : '协议'}</span><span>{p.protocol}</span></div>
                  <div className="flex justify-between"><span className="text-ln-tertiary">{lang === 'en' ? 'SDK' : '语言'}</span><span>{p.lang}</span></div>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.features.title}</h2>
        <div className="overflow-x-auto rounded-card bg-ln-panel" style={{ boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ln-border">
                <th className="text-left p-4 text-ln-secondary font-medium">{lang === 'en' ? 'Feature' : '功能'}</th>
                <th className="p-4 text-center font-medium" style={{ color: '#9d9cff' }}>Moltable</th>
                <th className="p-4 text-center text-ln-secondary font-medium">mem0</th>
                <th className="p-4 text-center text-ln-secondary font-medium">Zep</th>
              </tr>
            </thead>
            <tbody>
              {d.features.rows.map((row, i) => (
                <tr key={i} className="border-b border-ln-border hover:bg-ln-hover transition-colors">
                  <td className="p-4 text-ln-secondary">{row.feature}</td>
                  <td className="p-4 text-center">
                    {row.moltable ? <Check size={16} style={{ color: '#6366F1' }} /> : row.moltable === false ? <X size={16} style={{ color: '#FB6B4B' }} /> : <Minus size={16} className="text-ln-tertiary" />}
                  </td>
                  <td className="p-4 text-center">
                    {row.mem0 ? <Check size={16} style={{ color: '#818CF8' }} /> : row.mem0 === false ? <X size={16} style={{ color: '#FB6B4B', opacity: 0.6 }} /> : <Minus size={16} className="text-ln-tertiary" />}
                  </td>
                  <td className="p-4 text-center">
                    {row.zep ? <Check size={16} style={{ color: '#818CF8' }} /> : row.zep === false ? <X size={16} style={{ color: '#FB6B4B', opacity: 0.6 }} /> : <Minus size={16} className="text-ln-tertiary" />}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.architecture.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(['moltable', 'mem0', 'zep'] as const).map((key) => {
            const isMoltable = key === 'moltable'
            return (
              <div key={key} className="p-6 rounded-card bg-ln-panel"
                style={{ boxShadow: isMoltable ? '0 0 0 1px #4338CA' : '0 0 0 1px rgba(255,255,255,0.06)' }}>
                <h3 className="text-base font-heading mb-3 font-semibold" style={isMoltable ? { color: '#9d9cff' } : {}}>
                  {d.overview[key].name}
                </h3>
                <p className="text-sm text-ln-secondary leading-relaxed">{d.architecture[key]}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.pricing.title}</h2>
        <div className="overflow-x-auto rounded-card bg-ln-panel" style={{ boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ln-border">
                <th className="text-left p-4 text-ln-secondary font-medium">{lang === 'en' ? 'Tier' : '层级'}</th>
                <th className="p-4 text-center font-medium" style={{ color: '#9d9cff' }}>Moltable</th>
                <th className="p-4 text-center text-ln-secondary font-medium">mem0</th>
                <th className="p-4 text-center text-ln-secondary font-medium">Zep</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-ln-border">
                <td className="p-4 text-ln-secondary">{lang === 'en' ? 'Free' : '免费'}</td>
                <td className="p-4 text-center">{d.pricing.moltable.free}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.mem0.free}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.zep.free}</td>
              </tr>
              <tr className="border-b border-ln-border">
                <td className="p-4 text-ln-secondary">Pro</td>
                <td className="p-4 text-center">{d.pricing.moltable.pro}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.mem0.pro}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.zep.pro}</td>
              </tr>
              <tr>
                <td className="p-4 text-ln-secondary">{lang === 'en' ? 'Team / Enterprise' : '团队 / 企业'}</td>
                <td className="p-4 text-center">{d.pricing.moltable.team}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.mem0.team}</td>
                <td className="p-4 text-center text-ln-secondary">{d.pricing.zep.team}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Strengths */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.strengths.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(['moltable', 'mem0', 'zep'] as const).map((key) => {
            const isMoltable = key === 'moltable'
            const items = d.strengths[key]
            return (
              <div key={key} className="p-6 rounded-card bg-ln-panel"
                style={{ boxShadow: isMoltable ? '0 0 0 1px #4338CA' : '0 0 0 1px rgba(255,255,255,0.06)' }}>
                <h3 className="text-base font-heading mb-4 font-semibold" style={isMoltable ? { color: '#9d9cff' } : {}}>
                  {d.overview[key].name}
                </h3>
                <ul className="space-y-2">
                  {items.map((item: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-ln-secondary">
                      <Check size={14} className="text-indigo-400 mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>
      </section>

      {/* Use Cases */}
      <section className="max-w-5xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.usecases.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(['moltable', 'mem0', 'zep'] as const).map((key) => {
            const isMoltable = key === 'moltable'
            const items = d.usecases[key]
            return (
              <div key={key} className="p-6 rounded-card bg-ln-panel"
                style={{ boxShadow: isMoltable ? '0 0 0 1px #4338CA' : '0 0 0 1px rgba(255,255,255,0.06)' }}>
                <h3 className="text-base font-heading mb-4 font-semibold" style={isMoltable ? { color: '#9d9cff' } : {}}>
                  {d.overview[key].name}
                </h3>
                <ul className="space-y-2">
                  {items.map((item: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-ln-secondary">
                      <ArrowRight size={14} className="text-ln-accent mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>
      </section>

      {/* Verdict */}
      <section className="max-w-3xl mx-auto px-6 pb-12">
        <h2 className="text-xl font-heading mb-6 text-center font-semibold">{d.verdict.title}</h2>
        <div className="p-6 rounded-card bg-ln-panel" style={{ boxShadow: '0 0 0 1px rgba(67,56,202,0.3)' }}>
          <ul className="space-y-3">
            {d.verdict.lines.map((line, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-ln-secondary">
                <span className="w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0 mt-0.5 font-bold"
                  style={{ background: 'rgba(67,56,202,0.15)', color: '#4338CA' }}>{i + 1}</span>
                {line}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-3xl mx-auto px-6 pb-16 text-center">
        <Link href="/register"
          className="inline-flex items-center gap-2 px-8 py-3 rounded-lg text-base font-medium transition-all hover:opacity-90"
          style={{ background: '#4338CA', color: '#fff' }}>
          {d.cta} <ArrowRight size={18} />
        </Link>
        <p className="text-xs text-ln-tertiary mt-4">{d.footer}</p>
      </section>
    </div>
  )
}
