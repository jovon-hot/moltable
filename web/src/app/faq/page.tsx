import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '常见问题 — Moltable',
  description:
    '关于 AI 身份同步、MCP 协议、跨平台 Agent 记忆管理的常见问题。Moltable 使用指南与定价说明。',
}

const faqs = [
  {
    q: 'Moltable 是什么？',
    a: 'Moltable 是 AI 身份同步层。你注册一次，所有 AI Agent（Hermes、Claude、ChatGPT、Cursor 等）自动认识你的偏好、记忆和 Persona。换电脑后 3 分钟恢复完整 AI 环境。',
  },
  {
    q: '和 ChatGPT Memory、Mem0 有什么区别？',
    a: 'ChatGPT Memory 只在一个产品里生效。Mem0 是开发者库。Moltable 是独立的身份层——你的记忆和偏好统一管理，所有 AI Agent 共享同步。你不用在每个 AI 里重复告诉它你是谁。',
  },
  {
    q: '需要付费吗？',
    a: '90 天免费试用。所有新用户注册即享 Pro 体验（10,000 条记忆、无限 Persona、多 Agent 支持）。此后 ¥19/月 或 ¥149/年。',
  },
  {
    q: '支持哪些 AI Agent？',
    a: '所有支持 MCP 协议的 AI Agent 都可以接入：Hermes Agent、Claude Code (Desktop)、Cursor、Cline、OpenClaw、以及任何自定义 MCP 客户端。14 个 MCP 工具开箱即用。',
  },
  {
    q: '我的数据安全吗？',
    a: '所有记忆在传输中加密（TLS 1.3），API Key 使用 scrypt 哈希存储。你的数据永远不会被用来训练 AI 模型。随时可以导出或删除全部数据。',
  },
  {
    q: '什么是 Persona？',
    a: 'Persona 是你在不同场景下的人格配置——比如"工作中严谨的工程师"和"周末轻松的朋友"。每个 Persona 有独立的记忆空间和偏好，Agent 按当前 Persona 调整行为。',
  },
  {
    q: 'MCP 是什么？',
    a: 'MCP（Model Context Protocol）是 Anthropic 开源的 AI 工具调用协议。就像 USB-C 统一了物理连接，MCP 统一了 AI 与外部工具的通信方式。Moltable 通过 MCP 让你的 Agent 直接读写你的记忆。',
  },
  {
    q: '怎么接入？',
    a: '注册获得 API Key → 在 AI Agent 配置中加载 Moltable MCP Server → 输入 Key。30 秒完成。详细步骤见 /connect 页面。',
  },
  {
    q: '数据存在哪里？',
    a: '数据存储在 Supabase（PostgreSQL + pgvector）上，运行在 AWS 上。你的记忆向量化后支持语义搜索。',
  },
  {
    q: '可以删除账号吗？',
    a: '可以。Dashboard Settings 中一键删除账号及全部关联数据。不留痕迹。',
  },
]

export default function FAQPage() {
  return (
    <div
      className="min-h-screen px-6 py-24 max-w-3xl mx-auto"
      style={{ background: '#0D0D14', color: '#ffffff' }}
    >
      <h1 className="text-2xl mb-4" style={{ fontWeight: 590 }}>
        常见问题
      </h1>
      <p className="text-sm mb-10" style={{ color: '#888888' }}>
        关于 Moltable 的常见问题。如果找不到答案，请访问 /docs 或发邮件至 hi@moltable.ai。
      </p>

      <div className="space-y-6">
        {faqs.map((faq, i) => (
          <div
            key={i}
            className="p-5 rounded-lg"
            style={{ background: '#14141E' }}
          >
            <h2
              className="text-base mb-2"
              style={{ fontWeight: 590, color: '#4338CA' }}
            >
              {faq.q}
            </h2>
            <p className="text-sm leading-relaxed" style={{ color: '#cccccc' }}>
              {faq.a}
            </p>
          </div>
        ))}
      </div>

      {/* FAQPage Schema for AI search engines */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: faqs.map((f) => ({
              '@type': 'Question',
              name: f.q,
              acceptedAnswer: { '@type': 'Answer', text: f.a },
            })),
          }),
        }}
      />
    </div>
  )
}
