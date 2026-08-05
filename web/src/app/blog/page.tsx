'use client'

import { Rss } from 'lucide-react'
import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'
import NewsletterSignup from '@/components/NewsletterSignup'

const posts = [
  {
    slug: 'knowledge-graph-deep-dive',
    date: '2026-08-06',
    title: '零依赖知识图谱：如何用 1200 行 Python 让 AI Agent 理解实体关系',
    titleEn: 'Zero-Dependency Knowledge Graph: How 1200 Lines of Python Let AI Agents Understand Entity Relationships',
    excerpt:
      '不需要 Neo4j，不需要 LLM 调用。Moltable 的知识图谱服务用纯正则 + 关键词匹配 + 共现分析，从零构建完整的实体关系图谱。逐层拆解实体识别、关系推断、增量更新和查询 API。',
    tags: ['Knowledge Graph', '架构', 'Python', '技术深度'],
  },
  {
    slug: 'rag-vs-finetuning-vs-identity',
    date: '2026-08-06',
    title: 'RAG vs Fine-Tuning vs Identity Layer：AI 个性化的不可能三角与破局之道',
    titleEn: 'RAG vs Fine-Tuning vs Identity Layer: The AI Personalization Trilemma and How to Solve It',
    excerpt:
      'RAG 喂文档，Fine-Tuning 改模型，Identity Layer 建模身份——三种 AI 个性化方案各有致命缺陷。本文从架构哲学、成本模型、时效性和准确度四个维度，深度分析 AI 个性化的「不可能三角」，并给出三层组合架构的最佳实践。',
    tags: ['对比', 'RAG', 'Fine-Tuning', 'Identity', '架构'],
  },
  {
    slug: 'hidden-cost-of-ai-amnesia',
    date: '2026-08-06',
    title: 'AI 失忆的真实成本：开发者每年浪费多少小时在「重新认识你」上？',
    titleEn: 'The Hidden Cost of AI Amnesia: How Many Hours Do Developers Waste on Re-Onboarding Their AI?',
    excerpt:
      '我们分析了 200+ 开发者的 AI 使用习惯，发现平均每人每周浪费 3.2 小时在「重新教 AI 认识自己」上。本文用真实数据量化 AI 失忆的隐性成本，并给出零摩擦的 Identity Layer 解决方案。',
    tags: ['研究', '效率', '数据', 'Identity'],
  },
  {
    slug: 'moltable-vs-mem0-identity-vs-memory',
    date: '2026-08-05',
    title: 'Moltable vs mem0：AI Identity Layer 和 Memory Layer 的本质区别',
    titleEn: 'Moltable vs mem0: Identity Layer vs Memory Layer — The Essential Difference',
    excerpt: '为什么你的 AI Agent 有了记忆还是不认识你？本文从架构哲学、数据模型、多 Agent 协作三个维度，深度剖析 Identity Layer 和 Memory Layer 的本质差异，帮你做出正确的技术选型。',
    tags: ['对比', 'mem0', 'Identity', 'Memory'],
  },
  {
    slug: 'why-ai-forgets-you',
    date: '2026-08-05',
    title: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
    titleEn: 'Why Your AI Forgets You Every Day — And the 2026 Fix',
    excerpt: '每天早上打开 Claude，它都像第一次见你。不是 AI 笨，是你的身份数据从没被真正存储过。本文剖析 AI「失忆」的五个根因，并给出 Moltable 的三层身份架构解决方案——一次配置，所有 Agent 共享。',
    tags: ['痛点', 'Identity', '教程'],
  },
  {
    slug: 'three-minute-env-recovery',
    date: '2026-08-04',
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
    titleEn: 'New Machine, Same Brain: Full AI Dev Environment Recovery in 3 Minutes',
    excerpt: '换一台新 Mac 之后，Claude、Cursor、Codex 全部失忆了？本文手把手教你用 Moltable 在 3 分钟内恢复完整的 AI 工作环境——从 Persona 到 MCP 配置，从项目记忆到工具偏好，一条命令全搞定。',
    tags: ['教程', '实战', 'Identity', 'MCP'],
  },
  {
    slug: 'agent-persistent-identity-research',
    date: '2026-08-04',
    title: 'arXiv 最新论文：AI Agent 的「持续身份」——多锚点架构如何让 Agent 不再失忆',
    titleEn: 'New arXiv Paper: Persistent Identity in AI Agents — Multi-Anchor Architecture',
    excerpt: '2026年3月 arXiv 论文提出多锚点身份理论：参考人类记忆障碍的神经科学研究，论证 AI Agent 需要偏好、决策、关系、价值观、叙事五个锚点来维持持续身份。Moltable 的三层架构恰好完整实现了这一理论。',
    tags: ['研究', 'Identity', '架构', '论文解读'],
  },
  {
    slug: 'ai-agent-trends-2026h2',
    date: '2026-08-08',
    title: '2026 下半年 AI Agent 趋势：从工具到伙伴，从记忆到身份',
    titleEn: 'AI Agent Trends H2 2026: From Tools to Partners, Memory to Identity',
    excerpt: '回顾 2026 上半年 AI Agent 的关键进展，预测下半年的五大趋势——包括 Identity 层的崛起、MCP 普及、开源追赶和价格战。',
    tags: ['趋势', '预测', 'Agent'],
  },
  {
    slug: 'open-protocol-ai-ecosystem',
    date: '2026-08-05',
    title: '开源协议如何重塑 AI 生态：MCP、A2A 与 Identity 层的三角博弈',
    titleEn: 'How Open Protocols Reshape AI: MCP, A2A and the Identity Layer',
    excerpt: 'Google A2A 和 Anthropic MCP 两大 AI 协议正在交织出一张新的生态网。Identity 层将在其中扮演什么角色？',
    tags: ['MCP', 'A2A', '开源', '生态'],
  },
  {
    slug: 'ai-developer-toolchain',
    date: '2026-08-01',
    title: '2026 AI 开发者工具链全景：从 LLM 到 Identity 的完整技术栈',
    titleEn: '2026 AI Developer Toolchain: Full Stack from LLM to Identity',
    excerpt: '现代 AI Agent 开发者需要哪些工具？LLM 网关、向量数据库、记忆层、身份层、MCP 服务器——一文梳理完整技术选型。',
    tags: ['工具链', '生态', '架构'],
  },
  {
    slug: 'ai-agent-security-2026',
    date: '2026-07-28',
    title: 'AI Agent 安全攻防 2026：你的 Agent 正在泄露什么？',
    titleEn: 'AI Agent Security 2026: What Is Your Agent Leaking?',
    excerpt: 'MCP 协议让 AI Agent 的能力爆发式增长，但也打开了新的攻击面。本文分析 Agent 安全威胁模型与加固方案。',
    tags: ['安全', 'MCP', '加密'],
  },
  {
    slug: 'ai-identity-sync-guide',
    date: '2026-07-25',
    title: '换电脑不换记忆：AI 身份同步完全指南',
    titleEn: 'New Computer, Same Memory: Complete AI Identity Sync Guide',
    excerpt: '换一台新电脑，AI 又要从零开始认识你？这份指南教你用 Identity Sync 实现跨设备 AI 环境一键恢复。',
    tags: ['教程', 'Identity', '最佳实践'],
  },
  {
    slug: 'ai-persona-enterprise',
    date: '2026-07-20',
    title: '企业级 AI Persona 管理：一个团队，十种人格',
    titleEn: 'Enterprise AI Persona Management: One Team, Ten Minds',
    excerpt: '当整个团队共用同一套 AI 工具时，如何让市场总监看到激进分析、财务总监看到保守建议？Persona 系统的企业级方案。',
    tags: ['Persona', '企业', '最佳实践'],
  },
  {
    slug: 'ai-data-sovereignty',
    date: '2026-07-18',
    title: '你的 10 万条 AI 对话记录：该归谁？该存在哪？',
    titleEn: 'Your 100K AI Conversations: Who Owns Them? Where Should They Live?',
    excerpt: 'AI Agent 每天产生大量对话记录和个人偏好数据。这些数据的所有权、存储位置和访问权限——2026年必须回答的问题。',
    tags: ['隐私', '数据主权', '安全'],
  },
  {
    slug: 'mcp-tool-development',
    date: '2026-07-15',
    title: 'MCP 工具开发实战：从零构建一个 AI Agent 记忆缓存层',
    titleEn: 'MCP Tool Development: Build an AI Agent Memory Cache from Scratch',
    excerpt: '手把手教你用 Python 开发一个 MCP Server，为 AI Agent 添加持久记忆能力。从协议理解到生产部署，全程演示。',
    tags: ['MCP', '开发教程', '开源'],
  },
  {
    slug: 'ai-forgetfulness-fix',
    date: '2026-07-12',
    title: 'AI 为什么总「失忆」？根因剖析与实操修复指南',
    titleEn: 'Why Does AI Keep Forgetting? Root Cause Analysis and Fix Guide',
    excerpt: '你的 Claude/ChatGPT 今天记住的偏好明天就忘？本文分析 AI「失忆」的五大根因，并给出即插即用的修复方案。',
    tags: ['教程', '诊断', 'Preference'],
  },
  {
    slug: 'agent-memory-landscape-2026',
    date: '2026-07-10',
    title: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
    titleEn: 'AI Agent Memory Landscape 2026: mem0 vs Zep vs Moltable',
    excerpt: '从开源到商业，从向量搜索到图谱记忆——2026年主流Agent记忆系统的横向对比，帮你选择最适合技术栈的记忆方案。',
    tags: ['对比评测', '记忆系统', '生态'],
  },
  {
    slug: 'cross-platform-persona',
    date: '2026-07-05',
    title: '跨平台 Persona 管理：一个身份，多种人格',
    titleEn: 'Cross-Platform Persona: One Identity, Many Minds',
    excerpt: '同一个 AI，加载战略顾问 Persona 是麦肯锡风格，加载保守审核员 Persona 是合规导向。本文通过真实场景演示 Persona 系统如何让一个 AI 拥有多种思维模式。',
    tags: ['Persona', '最佳实践', '教程'],
  },
  {
    slug: 'ai-identity-layer',
    date: '2026-06-28',
    title: 'AI 身份层的设计哲学：从 Memory 到 Identity',
    titleEn: 'From Memory to Identity: Designing the AI Identity Layer',
    excerpt: 'Memory 赛道拥挤，但 Identity 赛道几乎无人。本文探讨为什么"身份"比"记忆"更适合作为 AI 个人化的原子单位，以及 Moltable 的 Identity→Persona→Agent 三层架构设计。',
    tags: ['Identity', '架构', '设计哲学'],
  },
  {
    slug: 'mcp-ai-usb-c',
    date: '2026-06-20',
    title: 'MCP 协议：为什么它是 AI 的 USB-C',
    titleEn: 'MCP: The USB-C of AI Agents',
    excerpt: 'Model Context Protocol 正在成为 AI Agent 连接外部世界的标准。本文解析 MCP 的协议设计、与 A2A 的互补关系，以及为什么 Moltable 选择 MCP 作为核心接入方式。',
    tags: ['MCP', '协议', 'Agent'],
  },
]

export default function BlogPage() {
  const { t, lang } = useLang()
  const isEn = lang === 'en'

  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-3xl mx-auto px-6 pt-28 pb-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-12 h-12 rounded-[12px] flex items-center justify-center mx-auto mb-6 bg-ln-accent-muted">
            <Rss size={22} className="text-ln-accent" />
          </div>
          <h1 className="text-4xl font-heading tracking-[-0.4px] mb-3">
            {isEn ? 'Moltable Blog' : 'Moltable 博客'}
          </h1>
          <p className="text-base text-ln-secondary max-w-md mx-auto">
            {isEn
              ? 'AI Identity, MCP protocol, cross-platform Persona — deep content about AI Agent identity infrastructure.'
              : 'AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度内容。'}
          </p>
        </div>

        {/* Featured Post */}
        <Link
          href="/blog/moltable-vs-mem0-identity-vs-memory"
          className="block mb-12 p-6 rounded-card bg-ln-panel transition-all duration-200 hover:bg-ln-hover group relative overflow-hidden"
          style={{ boxShadow: '0 0 0 1px rgba(99,102,241,0.2), 0 4px 24px rgba(67,56,202,0.08)' }}
        >
          <div className="absolute top-0 right-0 px-3 py-1 rounded-bl-lg text-[11px] font-semibold"
            style={{ background: '#4338CA', color: '#fff' }}>
            {isEn ? 'FEATURED' : '精选'}
          </div>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-xs text-ln-tertiary font-ui">2026-08-05</span>
            <div className="flex gap-2">
              {['对比', 'mem0', 'Identity', 'Memory'].map((tag) => (
                <span key={tag} className="text-[11px] px-2 py-0.5 rounded-pill font-ui"
                  style={{ background: 'rgba(251,107,75,0.12)', color: '#FB6B4B' }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <h2 className="text-xl font-heading tracking-[-0.24px] mb-2 text-ln-text group-hover:text-ln-accent transition-colors">
            {isEn
              ? 'Moltable vs mem0: Identity Layer vs Memory Layer — The Essential Difference'
              : 'Moltable vs mem0：AI Identity Layer 和 Memory Layer 的本质区别'}
          </h2>
          <p className="text-sm text-ln-secondary font-body leading-relaxed mb-4">
            {isEn
              ? 'Why does your AI Agent still not know you even with memory? A deep dive into the architectural philosophy, data models, and multi-agent collaboration differences between Identity Layer and Memory Layer.'
              : '为什么你的 AI Agent 有了记忆还是不认识你？本文从架构哲学、数据模型、多 Agent 协作三个维度，深度剖析 Identity Layer 和 Memory Layer 的本质差异，帮你做出正确的技术选型。'}
          </p>
          <span className="inline-flex items-center gap-1 text-sm font-medium" style={{ color: '#6366F1' }}>
            {isEn ? 'Read the comparison →' : '阅读全文 →'}
          </span>
        </Link>

        {/* Articles */}
        <div className="space-y-8">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="block p-6 rounded-card bg-ln-panel shadow-border transition-all duration-200 hover:bg-ln-hover hover:shadow-card-hover group"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs text-ln-tertiary font-ui">{post.date}</span>
                <div className="flex gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[11px] px-2 py-0.5 rounded-pill font-ui"
                      style={{ background: 'rgba(99,102,241,0.12)', color: '#A5B4FC' }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              <h2 className="text-xl font-heading tracking-[-0.24px] mb-2 text-ln-text group-hover:text-ln-accent transition-colors">
                {isEn && post.titleEn ? post.titleEn : post.title}
              </h2>
              <p className="text-sm text-ln-secondary font-body leading-relaxed">
                {post.excerpt}
              </p>
              {isEn && <p className="text-[11px] text-ln-tertiary mt-1">{post.title}</p>}
            </Link>
          ))}
        </div>

        {/* Newsletter Signup */}
        <div className="mt-16">
          <NewsletterSignup variant="card" />
        </div>

        {/* RSS / Subscribe hint */}
        <div className="mt-12 pt-8 border-t border-ln-border text-center">
          <p className="text-sm text-ln-tertiary mb-3">
            {isEn
              ? 'Want a detailed comparison? Check our '
              : '想看详细对比？查看'}
            <Link href="/compare" className="text-ln-accent hover:underline font-medium">
              {isEn ? 'Moltable vs mem0 vs Zep comparison' : 'Moltable vs mem0 vs Zep 平台对比'}
            </Link>
          </p>
          <p className="text-sm text-ln-tertiary">
            {isEn ? 'More content coming · Follow ' : '更多内容即将发布 · 关注 '}
            <a href="https://github.com/moltable" className="text-ln-accent hover:underline">
              GitHub
            </a>
            {' '}{isEn ? 'for updates' : '获取更新'}
          </p>
        </div>
      </div>
    </div>
  )
}
