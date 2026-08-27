import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '常见问题 — Moltable',
  description:
    '关于 Agent 在线同步、跨框架迁移、MCP 协议的常见问题。Moltable 使用指南与定价说明。',
}

const faqs = [
  {
    q: 'Moltable 是什么？',
    a: 'Moltable 是 Agent 在线同步层。一个账号，你调教 AI 的身份、记忆、Persona 和项目跨设备、跨 Agent 在线同步；换设备用 auto_provision 一键恢复，另提供文件级备份（快照 + 回滚）兜底。',
  },
  {
    q: '和 ChatGPT Memory、Mem0 有什么区别？',
    a: 'ChatGPT Memory 只在一个产品里生效。Mem0 是开发者记忆库。Moltable 做的是「Agent 在线同步」——不只存记忆，还把你的身份、Persona、项目和 MCP 配置跨 Agent 同步，并支持跨框架迁移。',
  },
  {
    q: '需要付费吗？',
    a: 'Free 版包含 1 个 Agent、2 个 Persona、100 条记忆。Pro 版解锁 5 个 Agent、10 个 Persona、1 万条记忆和 1GB 备份存储，Ultra 版解锁无限 Agent、无限 Persona、5 万条记忆和 10GB 备份存储。跨框架迁移和 DID+VC 可验证身份即将推出。',
  },
  {
    q: '支持哪些 AI Agent？',
    a: '支持 Hermes、OpenClaw、Claude Code、Codex、Cursor 等主流 Agent 框架。通过 MCP 协议接入即自动同步，文件级备份 CLI 一条命令完成。',
  },
  {
    q: '我的数据安全吗？',
    a: '所有数据在传输中加密（TLS 1.3），API Key 使用哈希存储。你的数据永远不会被用来训练 AI 模型。随时可以导出或删除全部数据。',
  },
  {
    q: '什么是「灵魂资产」？',
    a: '你调教 AI 的成果：SOUL 文件（人格定义）、Skills（技能）、MCP 配置、记忆。这些是真正值钱的资产，区别于对话流水账——Moltable 让它们跨设备、跨 Agent 在线同步。',
  },
  {
    q: 'MCP 是什么？',
    a: 'MCP（Model Context Protocol）是 AI 工具调用的开放协议。就像 USB-C 统一了物理连接，MCP 统一了 AI 与外部工具的通信方式。',
  },
  {
    q: '怎么让我的 Agent 跨设备同步？',
    a: '通过 MCP 接入即自动同步：Agent 启动时调用 auto_provision 一键加载你的身份、记忆与 Persona。需要文件级兜底时：moltable backup init 生成配置 → moltable backup push 上传快照。详细步骤见 /connect 页面。',
  },
  {
    q: '数据存在哪里？',
    a: '数据存储在 Supabase（PostgreSQL）上，文件级备份按 SHA-256 内容寻址去重，只打包调教资产，自动排除对话流水账。',
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
