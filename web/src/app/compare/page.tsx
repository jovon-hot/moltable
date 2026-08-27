'use client'

import Link from 'next/link'
import { Check, X, Minus, ArrowRight, Layers, Brain, Shield, Zap, Users, Database, Globe, Code } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'

const comparisonData = {
  zh: {
    hero: {
      title: 'Agent 在线同步平台对比 2026',
      subtitle: 'Moltable vs mem0 vs Zep — 记忆层，还是 Agent 在线同步层？',
      updated: '2026-08-22',
    },
    intro: 'Moltable 与 mem0 / Zep 不是同一赛道：mem0 和 Zep 做的是「记忆层」（存储和检索 AI 的对话记忆），Moltable 做的是「Agent 在线同步层」（一个账号，把你调教的 Agent——身份、记忆、Persona、项目——跨设备、跨 Agent 在线同步，换设备用 auto_provision 一键恢复）。重叠维度有限，本对比仅供技术选型参考。',
    overview: {
      title: '平台概览',
      moltable: {
        name: 'Moltable.ai',
        positioning: 'Agent 在线同步层 — 你的 AI 永远顺手',
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
        { feature: 'Agent 在线同步 (身份/记忆/Persona/项目)', moltable: true, mem0: false, zep: false },
        { feature: '版本管理 (快照 + 回滚)', moltable: true, mem0: false, zep: false },
        { feature: '跨框架迁移 (LLM 翻译, 即将推出)', moltable: true, mem0: false, zep: false },
        { feature: '引用同步 (知识库一并同步)', moltable: true, mem0: false, zep: false },
        { feature: '排除对话流水账 (只同步资产)', moltable: true, mem0: false, zep: false },
        { feature: '语义记忆存储', moltable: true, mem0: true, zep: true },
        { feature: '向量搜索', moltable: true, mem0: true, zep: true },
        { feature: 'MCP Server', moltable: true, mem0: true, zep: true },
        { feature: '多 Agent 支持', moltable: true, mem0: true, zep: true },
        { feature: '加密存储 (传输+静态)', moltable: true, mem0: true, zep: true },
        { feature: '自托管 (Self-host)', moltable: true, mem0: true, zep: true },
        { feature: 'CLI 工具', moltable: true, mem0: true, zep: false },
        { feature: 'Web Dashboard', moltable: true, mem0: true, zep: true },
        { feature: 'DID / 可验证凭证 (即将推出)', moltable: true, mem0: false, zep: false },
      ],
    },
    pricing: {
      title: '定价对比',
      moltable: { free: '1 Agent · 2 Persona · 100 记忆', pro: '5 Agent · 10 Persona · 1万记忆 · 1GB 备份存储', team: '联系销售' },
      mem0: { free: '开源免费', pro: '$249/月', team: '企业定制' },
      zep: { free: '开源免费', pro: '$99/月起', team: '企业定制' },
    },
    architecture: {
      title: '架构对比',
      moltable: 'Profile（本体）→ Soul（化身）→ 凭证（身份证明）三层。以「Agent」为同步单位：身份、记忆、Persona、项目通过 MCP 在线同步，换设备用 auto_provision 一键恢复；文件级备份（快照 + 版本号 + 回滚）作为兜底，DID+VC 给资产签出处，自动排除对话流水账。',
      mem0: 'Memory → User → Agent 三层。以「记忆」为最小单位，专注记忆的存储、检索和管理。Pro 版增加团队协作，但不涉及 Agent 在线同步或跨框架迁移。',
      zep: 'Memory → Graph → User。以「记忆 + 知识图谱」为核心，在记忆之上构建实体关系图。适合需要复杂上下文推理的场景，但学习曲线较陡。',
    },
    strengths: {
      title: '各自优势',
      moltable: [
        '唯一做「Agent 在线同步」的平台——解决「换框架/换电脑，调教成果全丢」的问题',
        '版本管理：快照 + 版本号，改坏了随时回滚到任意历史版本',
        '跨框架迁移：用你自己的 LLM 把 Hermes 的调教成果翻译成 OpenClaw / Claude 版本',
        '引用同步：知识库、内容来源一并同步，工作环境完整还原',
        '只同步资产、排除流水账：实测 39MB 资产 vs 1.2GB 对话日志，压缩比 30 倍',
        'MIT 开源 + DID 可验证身份（即将推出）',
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
        '同时用多个 Agent 框架（Hermes + OpenClaw + Claude）的重度用户',
        '花大量时间调教 AI、担心换机器/换框架就丢的人',
        '需要把调教成果版本化、可回滚的个人/团队',
        '未来需要「可验证身份」给 Agent 签出处的开发者',
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
        '如果你要「你的 AI 永远顺手」——一个账号在线同步、换设备一键恢复、版本化兜底 → 选 Moltable',
        '如果你在构建 AI 产品，需要嵌入「记忆」能力且看重社区生态 → 选 mem0',
        '如果你需要「知识图谱 + 企业级安全性能」→ 选 Zep',
        '如果你既需要记忆、又需要 Agent 在线同步 → Moltable 是唯一选择（它两者都做）',
      ],
    },
    cta: '免费开始同步你的 Agent →',
    footer: '以上对比基于 2026-08-22 各平台公开信息。功能和定价可能随时更新，请以各平台官网为准。',
  },
  en: {
    hero: {
      title: 'Agent Online Sync Platform Comparison 2026',
      subtitle: 'Moltable vs mem0 vs Zep — memory layer, or the online sync layer?',
      updated: '2026-08-22',
    },
    intro: 'Moltable and mem0/Zep are not in the same lane: mem0 and Zep build a "memory layer" (storing and retrieving AI conversation memory), while Moltable is the "online sync layer" (one account that syncs your tuned agent identity, memories, personas, and projects across devices and agents, with auto_provision restoring everything on a new device in one call). Overlap is limited; this comparison is for technical reference only.',
    overview: {
      title: 'Platform Overview',
      moltable: {
        name: 'Moltable.ai',
        positioning: 'Agent Online Sync Layer — Your AI, always in sync',
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
        { feature: 'Online Sync (identity/memory/personas/projects)', moltable: true, mem0: false, zep: false },
        { feature: 'Versioning (snapshot + rollback)', moltable: true, mem0: false, zep: false },
        { feature: 'Cross-Framework Migration (LLM, coming soon)', moltable: true, mem0: false, zep: false },
        { feature: 'Reference Sync (knowledge bases)', moltable: true, mem0: false, zep: false },
        { feature: 'Excludes chat logs (assets only)', moltable: true, mem0: false, zep: false },
        { feature: 'Semantic Memory Storage', moltable: true, mem0: true, zep: true },
        { feature: 'Vector Search', moltable: true, mem0: true, zep: true },
        { feature: 'MCP Server', moltable: true, mem0: true, zep: true },
        { feature: 'Multi-Agent Support', moltable: true, mem0: true, zep: true },
        { feature: 'Encryption (TLS+At-Rest)', moltable: true, mem0: true, zep: true },
        { feature: 'Self-Hosting', moltable: true, mem0: true, zep: true },
        { feature: 'CLI Tool', moltable: true, mem0: true, zep: false },
        { feature: 'Web Dashboard', moltable: true, mem0: true, zep: true },
        { feature: 'DID / Verifiable Credentials (soon)', moltable: true, mem0: false, zep: false },
      ],
    },
    pricing: {
      title: 'Pricing Comparison',
      moltable: { free: '1 Agent · 2 Personas · 100 memories', pro: '5 Agents · 10 Personas · 10K memories · 1GB backup storage', team: 'Contact sales' },
      mem0: { free: 'OSS free', pro: '$249/mo', team: 'Enterprise custom' },
      zep: { free: 'OSS free', pro: 'From $99/mo', team: 'Enterprise custom' },
    },
    architecture: {
      title: 'Architecture Comparison',
      moltable: 'Profile (identity) → Soul (avatar) → Credential (proof) three layers. Agents are the sync unit: identity, memory, personas, and projects sync online via MCP, and auto_provision restores everything on a new device in one call. File-level backup (snapshot + versioning + rollback) is the safety net; DID+VC signs asset provenance, and chat logs are auto-excluded.',
      mem0: 'Memory → User → Agent three layers. Memory as the smallest unit, focused on storage, retrieval, and management. Pro tier adds team collaboration without online agent sync or cross-framework migration.',
      zep: 'Memory → Graph → User. Core is memory + knowledge graph, building entity relationship graphs on top of memories. Suitable for complex context reasoning but has a steeper learning curve.',
    },
    strengths: {
      title: 'Key Strengths',
      moltable: [
        'Only platform doing "online agent sync" — solves "switching framework/machine loses your tuning"',
        'Versioning: snapshot + version number, roll back to any point anytime',
        'Cross-framework migration: use your own LLM to translate a Hermes setup into OpenClaw/Claude',
        'Reference sync: knowledge bases and content sources synced too',
        'Assets-only sync: 39MB assets vs 1.2GB chat logs — 30x compression',
        'MIT open-source + DID verifiable identity (coming soon)',
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
        'Power users running multiple Agent frameworks (Hermes + OpenClaw + Claude)',
        'People who invest heavily in tuning AI and fear losing it when switching machines/frameworks',
        'Individuals/teams who want their tuning versioned and rollback-able',
        'Developers who will need verifiable identity for agent provenance',
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
        'Want "Your AI, always in sync" — one account, cross-device sync, versioned safety net → Choose Moltable',
        'Building AI products, need embeddable memory with strong community → Choose mem0',
        'Need knowledge graph + enterprise security and performance → Choose Zep',
        'Need both memory AND online agent sync → Moltable is the only option (it does both)',
      ],
    },
    cta: 'Start syncing your Agent for free →',
    footer: 'Comparison based on publicly available information as of 2026-08-22. Features and pricing may change; check each platform\'s official website.',
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
