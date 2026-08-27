'use client'

import Link from 'next/link'
import { useLang } from '@/contexts/LanguageContext'

interface BlogPost {
  slug: string
  date: string
  title: string
  titleEn?: string
  excerpt: string
  tags: string[]
}

// Shared blog posts data — also used by blog/page.tsx
const posts: BlogPost[] = [
  {
    slug: 'knowledge-graph-deep-dive',
    date: '2026-08-06',
    title: '零依赖知识图谱：如何用 1200 行 Python 让 AI Agent 理解实体关系',
    titleEn: 'Zero-Dependency Knowledge Graph: How 1200 Lines of Python Let AI Agents Understand Entity Relationships',
    excerpt: '不需要 Neo4j，不需要 LLM 调用。Moltable 的知识图谱服务用纯正则 + 关键词匹配 + 共现分析，从零构建完整的实体关系图谱。',
    tags: ['Knowledge Graph', '架构', 'Python', '技术深度'],
  },
  {
    slug: 'rag-vs-finetuning-vs-identity',
    date: '2026-08-06',
    title: 'RAG vs Fine-Tuning vs 在线同步：AI 个性化的不可能三角与破局之道',
    titleEn: 'RAG vs Fine-Tuning vs Online Sync: The AI Personalization Trilemma',
    excerpt: 'RAG 喂文档，Fine-Tuning 改模型，在线同步兜底——三种 AI 个性化方案各有边界。',
    tags: ['对比', 'RAG', 'Fine-Tuning', 'Identity', '架构'],
  },
  {
    slug: 'hidden-cost-of-ai-amnesia',
    date: '2026-08-06',
    title: 'AI 失忆的真实成本：开发者每年浪费多少小时在「重新认识你」上？',
    titleEn: 'The Hidden Cost of AI Amnesia: How Many Hours Do Developers Waste on Re-Onboarding Their AI?',
    excerpt: '我们分析了 200+ 开发者的 AI 使用习惯，发现平均每人每周浪费 3.2 小时在「重新教 AI 认识自己」上。',
    tags: ['研究', '效率', '数据', 'Identity'],
  },
  {
    slug: 'moltable-vs-mem0-identity-vs-memory',
    date: '2026-08-05',
    title: 'Moltable vs mem0：在线同步和记忆层的本质区别',
    titleEn: 'Moltable vs mem0: Online Sync vs Memory Layer — The Essential Difference',
    excerpt: '为什么你的 AI Agent 有了记忆，换台电脑还是全丢？深度剖析 Agent 在线同步和记忆层的本质差异。',
    tags: ['对比', 'mem0', 'Identity', 'Memory'],
  },
  {
    slug: 'why-ai-forgets-you',
    date: '2026-08-05',
    title: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
    titleEn: 'Why Your AI Forgets You Every Day — And the 2026 Fix',
    excerpt: '每天早上打开 Claude，它都像第一次见你。不是 AI 笨，是你的调教成果从没被真正同步过。',
    tags: ['痛点', 'Identity', '教程'],
  },
  {
    slug: 'three-minute-env-recovery',
    date: '2026-08-04',
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
    titleEn: 'New Machine, Same Brain: Full AI Dev Environment Recovery in 3 Minutes',
    excerpt: '换一台新 Mac 之后，Claude、Cursor、Codex 全部失忆了？一条命令全搞定。',
    tags: ['教程', '实战', 'Identity', 'MCP'],
  },
  {
    slug: 'agent-persistent-identity-research',
    date: '2026-08-04',
    title: 'arXiv 最新论文：AI Agent 的「持续身份」——多锚点架构如何让 Agent 不再失忆',
    titleEn: 'New arXiv Paper: Persistent Identity in AI Agents — Multi-Anchor Architecture',
    excerpt: '2026年3月 arXiv 论文提出多锚点身份理论：AI Agent 需要偏好、决策、关系、价值观、叙事五个锚点。',
    tags: ['研究', 'Identity', '架构', '论文解读'],
  },
  {
    slug: 'agent-memory-landscape-2026',
    date: '2026-07-10',
    title: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
    titleEn: 'AI Agent Memory Landscape 2026: mem0 vs Zep vs Moltable',
    excerpt: '从开源到商业，从向量搜索到图谱记忆——2026年主流Agent记忆系统的横向对比。',
    tags: ['对比评测', '记忆系统', '生态'],
  },
  {
    slug: 'open-protocol-ai-ecosystem',
    date: '2026-08-05',
    title: '开源协议如何重塑 AI 生态：MCP、A2A 与在线同步层',
    titleEn: 'How Open Protocols Reshape AI: MCP, A2A and the Online Sync Layer',
    excerpt: 'Google A2A 和 Anthropic MCP 两大 AI 协议正在交织出一张新的生态网。',
    tags: ['MCP', 'A2A', '开源', '生态'],
  },
  {
    slug: 'ai-developer-toolchain',
    date: '2026-08-01',
    title: '2026 AI 开发者工具链全景：从 LLM 到在线同步的完整技术栈',
    titleEn: '2026 AI Developer Toolchain: Full Stack from LLM to Online Sync',
    excerpt: '现代 AI Agent 开发者需要哪些工具？LLM 网关、向量数据库、记忆层、Agent 在线同步层、MCP 服务器。',
    tags: ['工具链', '生态', '架构'],
  },
  {
    slug: 'ai-agent-security-2026',
    date: '2026-07-28',
    title: 'AI Agent 安全攻防 2026：你的 Agent 正在泄露什么？',
    titleEn: 'AI Agent Security 2026: What Is Your Agent Leaking?',
    excerpt: 'MCP 协议让 AI Agent 的能力爆发式增长，但也打开了新的攻击面。',
    tags: ['安全', 'MCP', '加密'],
  },
  {
    slug: 'ai-identity-sync-guide',
    date: '2026-07-25',
    title: '换电脑不换顺手：Agent 在线同步完全指南',
    titleEn: 'New Computer, Same AI: The Complete Agent Online Sync Guide',
    excerpt: '换一台新电脑，AI 又要从零开始认识你？这份指南教你用 Moltable 在线同步 + auto_provision 实现跨设备 AI 环境一键恢复。',
    tags: ['教程', 'Identity', '最佳实践'],
  },
  {
    slug: 'ai-persona-enterprise',
    date: '2026-07-20',
    title: '企业级 Agent 化身管理：一个团队，十种人格',
    titleEn: 'Enterprise Agent Personas: One Team, Ten Minds — Always in Sync',
    excerpt: '当整个团队共用同一套 AI 工具时，如何让市场总监看到激进分析、财务总监看到保守建议？',
    tags: ['Persona', '企业', '最佳实践'],
  },
  {
    slug: 'ai-data-sovereignty',
    date: '2026-07-18',
    title: '你的 10 万条 AI 对话记录：该归谁？该存在哪？',
    titleEn: 'Your 100K AI Conversations: Who Owns Them? Where Should They Live?',
    excerpt: 'AI Agent 每天产生大量对话记录和个人偏好数据。这些数据的所有权、存储位置和访问权限。',
    tags: ['隐私', '数据主权', '安全'],
  },
  {
    slug: 'mcp-tool-development',
    date: '2026-07-15',
    title: 'MCP 工具开发实战：从零构建一个 AI Agent 记忆缓存层',
    titleEn: 'MCP Tool Development: Build an AI Agent Memory Cache from Scratch',
    excerpt: '手把手教你用 Python 开发一个 MCP Server，为 AI Agent 添加持久记忆能力。',
    tags: ['MCP', '开发教程', '开源'],
  },
  {
    slug: 'ai-forgetfulness-fix',
    date: '2026-07-12',
    title: 'AI 为什么总「失忆」？根因剖析与实操修复指南',
    titleEn: 'Why Does AI Keep Forgetting? Root Cause Analysis and Fix Guide',
    excerpt: '你的 Claude/ChatGPT 今天记住的偏好明天就忘？本文分析 AI「失忆」的五大根因。',
    tags: ['教程', '诊断', 'Preference'],
  },
  {
    slug: 'cross-platform-persona',
    date: '2026-07-05',
    title: '跨平台化身同步：一个身份，多种人格',
    titleEn: 'Cross-Platform Personas: One Identity, Many Minds — Always in Sync',
    excerpt: '同一个 AI，加载战略顾问 Persona 是麦肯锡风格，加载保守审核员 Persona 是合规导向。',
    tags: ['Persona', '最佳实践', '教程'],
  },
  {
    slug: 'ai-identity-layer',
    date: '2026-06-28',
    title: 'AI 在线同步层的设计哲学：从 Memory 到 Sync',
    titleEn: 'From Memory to Sync: Designing the Agent Online Sync Layer',
    excerpt: 'Memory 赛道拥挤，但「同步」赛道几乎无人。',
    tags: ['Identity', '架构', '设计哲学'],
  },
  {
    slug: 'mcp-ai-usb-c',
    date: '2026-06-20',
    title: 'MCP 协议：为什么它是 AI 的 USB-C',
    titleEn: 'MCP: The USB-C of AI Agents',
    excerpt: 'Model Context Protocol 正在成为 AI Agent 连接外部世界的标准。',
    tags: ['MCP', '协议', 'Agent'],
  },
]

interface RelatedPostsProps {
  currentSlug: string
  currentTags: string[]
  maxPosts?: number
}

export default function RelatedPosts({ currentSlug, currentTags, maxPosts = 3 }: RelatedPostsProps) {
  const { lang } = useLang()
  const isEn = lang === 'en'

  // Score each post by how many tags overlap with current post
  const scored = posts
    .filter((p) => p.slug !== currentSlug)
    .map((p) => {
      const overlap = p.tags.filter((t) => currentTags.includes(t)).length
      // Bonus for recency (newer posts score higher)
      const recencyBonus = p.date >= '2026-08-01' ? 0.5 : 0
      return { ...p, score: overlap + recencyBonus }
    })
    .filter((p) => p.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxPosts)

  if (scored.length === 0) return null

  return (
    <div className="mt-16 pt-8" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <h3 className="text-sm font-semibold mb-5" style={{ color: '#6E6B80', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
        {isEn ? 'Related Articles' : '相关文章'}
      </h3>
      <div className="grid grid-cols-1 gap-4">
        {scored.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="block p-4 rounded-lg transition-all duration-200 hover:-translate-y-0.5"
            style={{ background: '#14141E', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-medium" style={{ color: '#6366F1' }}>
                {post.date}
              </span>
              {post.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(99,102,241,0.1)', color: '#A5B4FC' }}
                >
                  {tag}
                </span>
              ))}
            </div>
            <h4 className="text-sm font-semibold leading-snug" style={{ color: '#F5F4F8' }}>
              {isEn && post.titleEn ? post.titleEn : post.title}
            </h4>
            <p className="text-xs mt-1.5 leading-relaxed line-clamp-2" style={{ color: '#85829E' }}>
              {post.excerpt}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}
