'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Book, Terminal, Server, Users, Code, GitBranch,
  HelpCircle, ChevronRight, Copy, Check, Zap,
  Database, Search, Tag, UserPlus, UserCheck,
  Shuffle, Archive, Heart, Layout,
} from 'lucide-react'

// Dynamic API host — respects NEXT_PUBLIC_API_URL env var, falls back to production URL
const API_HOST = typeof window !== 'undefined'
  ? (process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.io')
  : 'https://api.moltable.io'

// ─── Sidebar Navigation ───────────────────────────────────────────

interface SidebarItem {
  id: string
  label: string
  icon: React.ElementType
  children?: { id: string; label: string; badge?: string }[]
}

const sidebarItems: SidebarItem[] = [
  { id: 'quickstart', label: '快速开始', icon: Zap },
  { id: 'installation', label: '安装与配置', icon: Terminal },
  { id: 'hermes', label: 'Hermes Agent 接入', icon: Server },
  { id: 'claude', label: 'Claude Desktop 接入', icon: Users },
  {
    id: 'api', label: 'API 参考', icon: Code,
    children: [
      { id: 'api-auto_provision', label: 'auto_provision' },
      { id: 'api-save_memory', label: 'save_memory' },
      { id: 'api-search_memory', label: 'search_memory' },
      { id: 'api-update_memory', label: 'update_memory' },
      { id: 'api-list_personas', label: 'list_personas' },
      { id: 'api-get_persona', label: 'get_persona' },
      { id: 'api-list_projects', label: 'list_projects' },
      { id: 'api-get_project', label: 'get_project' },
      { id: 'api-create_project', label: 'create_project' },
      { id: 'api-update_project', label: 'update_project' },
      { id: 'api-archive_memory', label: 'archive_memory' },
      { id: 'api-ping', label: 'ping' },
      { id: 'api-compare_personas', label: 'compare_personas', badge: '已迁移至 Agent 端' },
      { id: 'api-match_persona', label: 'match_persona', badge: '已迁移至 Agent 端' },
    ],
  },
  { id: 'mcp', label: 'MCP 协议', icon: GitBranch },
  { id: 'faq', label: '常见问题', icon: HelpCircle },
]

// ─── API Tool Data ────────────────────────────────────────────────

interface ParamDef {
  name: string
  type: string
  required: boolean
  description: string
}

interface ToolDef {
  id: string
  name: string
  description: string
  params: ParamDef[]
  curlExample: string
  responseExample: string
  migrated?: boolean
}

const apiTools: ToolDef[] = [
  {
    id: 'auto_provision',
    name: 'auto_provision',
    description:
      '一键获取用户完整上下文。Agent 连接 Moltable 后应优先调用此工具，返回用户画像、行为规则、可用 Persona、活跃项目、核心知识。',
    params: [
      {
        name: 'persona_id',
        type: 'string',
        required: false,
        description: '可选的 Persona ID，用于指定配置视角',
      },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_provision","arguments":{}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"user_profile\\": {\\n    \\"name\\": \\"用户昵称\\",\\n    \\"bio\\": \\"个人简介\\",\\n    \\"behavior_rules\\": [\\n      \\"偏好简洁回复\\",\\n      \\"数据驱动决策\\"\\n    ]\\n  },\\n  \\"personas\\": [...],\\n  \\"active_projects\\": [...],\\n  \\"recent_decisions\\": [...]\\n}"
    }]
  }
}`
  },
  {
    id: 'save_memory',
    name: 'save_memory',
    description:
      '保存一条新记忆。如检测到语义冲突（相似度 > 0.9），返回已有条目供确认。',
    params: [
      { name: 'content', type: 'string', required: true, description: '记忆内容' },
      { name: 'category', type: 'string', required: false, description: '类别: preference / decision / fact / project / insight / task / relationship（默认 fact）' },
      { name: 'source', type: 'string', required: false, description: '来源标识：hermes / claude / chatgpt / manual / agent（默认 agent）' },
      { name: 'confidence', type: 'number', required: false, description: '置信度 0.0 - 1.0（默认 1.0）' },
      { name: 'tags', type: 'string[]', required: false, description: '标签列表' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"save_memory","arguments":{"content":"用户偏好数据驱动的报告","category":"preference","tags":["数据分析","报告"]}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"saved\\": true,\\n  \\"id\\": \\"a1b2c3d4-...\\"\\n}"
    }]
  }
}

// 冲突时:
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"saved\\": false,\\n  \\"conflict\\": true,\\n  \\"existing\\": [{\\"content\\": \\"用户偏好...\\", \\"similarity\\": 0.95}],\\n  \\"message\\": \\"发现相似记忆，使用 force=true 强制保存覆盖\\"\\n}"
    }]
  }
}`
  },
  {
    id: 'search_memory',
    name: 'search_memory',
    description:
      '语义搜索用户记忆。传入自然语言查询，返回最相关的记忆条目。',
    params: [
      { name: 'query', type: 'string', required: true, description: '搜索内容（自然语言查询）' },
      { name: 'top_k', type: 'integer', required: false, description: '返回结果数量 1-50（默认 5）' },
      { name: 'category', type: 'string', required: false, description: '可选过滤类别：preference / decision / fact / project / insight / task / relationship' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_memory","arguments":{"query":"用户对数据可视化的偏好","top_k":3,"category":"preference"}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"query\\": \\"用户对数据可视化的偏好\\",\\n  \\"results\\": [\\n    {\\n      \\"id\\": \\"mem_001\\",\\n      \\"content\\": \\"用户偏好使用交互式图表展示数据\\",\\n      \\"category\\": \\"preference\\",\\n      \\"source\\": \\"agent\\",\\n      \\"relevance\\": 0.92\\n    }\\n  ]\\n}"
    }]
  }
}`
  },
  {
    id: 'list_personas',
    name: 'list_personas',
    description:
      '列出用户的所有可用 Persona（人格配置），返回名称、类型、描述等摘要信息。',
    params: [],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"list_personas","arguments":{}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"personas\\": [\\n    {\\n      \\"id\\": \\"ps_001\\",\\n      \\"name\\": \\"战略顾问\\",\\n      \\"type\\": \\"professional\\",\\n      \\"description\\": \\"提供高屋建瓴的战略分析和建议\\",\\n      \\"traits\\": {\\"思维模式\\": \\"第一性原理\\", \\"沟通风格\\": \\"结构化\\"}\\n    }\\n  ]\\n}"
    }]
  }
}`
  },
  {
    id: 'get_persona',
    name: 'get_persona',
    description:
      '获取指定 Persona 的完整配置，包括 system_prompt、traits 等全部细节。',
    params: [
      { name: 'persona_id', type: 'string', required: true, description: 'Persona ID' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_persona","arguments":{"persona_id":"ps_001"}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"id\\": \\"ps_001\\",\\n  \\"name\\": \\"战略顾问\\",\\n  \\"type\\": \\"professional\\",\\n  \\"description\\": \\"提供高屋建瓴的战略分析和建议\\",\\n  \\"system_prompt\\": \\"你是一位经验丰富的战略顾问...\\",\\n  \\"traits\\": {\\"思维模式\\": \\"第一性原理\\", \\"沟通风格\\": \\"结构化\\"},\\n  \\"is_active\\": true\\n}"
    }]
  }
}`
  },
  {
    id: 'list_projects',
    name: 'list_projects',
    description:
      '列出用户的所有项目，含 knowledge_bases（知识库连接信息）和 tools（工具/MCP 服务器配置）。Agent 据此建立工作环境。',
    params: [],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: *** \\
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"list_projects","arguments":{}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"projects\": [\n    {\n      \"id\": \"pj_001\",\n      \"name\": \"数据分析项目\",\n      \"description\": \"公司的数据分析平台\",\n      \"is_active\": true,\n      \"knowledge_bases\": [...],\n      \"tools\": [...]\n    }\n  ]\n}"
    }]
  }
}`
  },
  {
    id: 'get_project',
    name: 'get_project',
    description:
      '获取单个项目的完整环境配置，含 knowledge_bases 和 tools。',
    params: [
      { name: 'project_id', type: 'string', required: true, description: '项目 ID' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: *** \\
  -d '{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"get_project","arguments":{"project_id":"pj_001"}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"id\": \"pj_001\",\n  \"name\": \"数据分析项目\",\n  \"description\": \"公司的数据分析平台\",\n  \"knowledge_bases\": [...],\n  \"tools\": [...]\n}"
    }]
  }
}`
  },
  {
    id: 'create_project',
    name: 'create_project',
    description:
      '创建新项目，含 knowledge_bases（如 PostgreSQL/Obsidian/Superset 连接）和 tools（如 MCP 服务器/Hermes Skill）。',
    params: [
      { name: 'name', type: 'string', required: true, description: '项目名称' },
      { name: 'description', type: 'string', required: false, description: '项目描述' },
      { name: 'persona_id', type: 'string', required: false, description: '关联的 Persona ID' },
      { name: 'knowledge_bases', type: 'array', required: false, description: '知识库列表，每项含 type/label/host/port/database/path/url 等' },
      { name: 'tools', type: 'array', required: false, description: '工具列表，每项含 type/name/url 等' },
      { name: 'is_active', type: 'boolean', required: false, description: '是否为活跃项目' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: *** \\
  -d '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"create_project","arguments":{"name":"新项目","description":"一个数据分析项目","is_active":true}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"created\": true,\n  \"id\": \"pj_002\",\n  \"name\": \"新项目\"\n}"
    }]
  }
}`
  },
  {
    id: 'update_project',
    name: 'update_project',
    description:
      '更新项目环境配置。',
    params: [
      { name: 'project_id', type: 'string', required: true, description: '项目 ID' },
      { name: 'name', type: 'string', required: false, description: '新名称' },
      { name: 'description', type: 'string', required: false, description: '新描述' },
      { name: 'persona_id', type: 'string', required: false, description: '关联 Persona ID' },
      { name: 'knowledge_bases', type: 'array', required: false, description: '新知识库配置' },
      { name: 'tools', type: 'array', required: false, description: '新工具配置' },
      { name: 'is_active', type: 'boolean', required: false, description: '是否活跃' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: *** \\
  -d '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"update_project","arguments":{"project_id":"pj_001","name":"更新后的项目名"}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"updated\": true,\n  \"id\": \"pj_001\"\n}"
    }]
  }
}`
  },
  {
    id: 'archive_memory',
    name: 'archive_memory',
    description:
      '归档记忆（软删除）。归档后的记忆不会出现在搜索和列表中，但数据保留在数据库中。',
    params: [
      { name: 'memory_id', type: 'string', required: true, description: '要归档的记忆 ID' },
    ],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"archive_memory","arguments":{"memory_id":"mem_001"}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"status\\": \\"archived\\",\\n  \\"memory_id\\": \\"mem_001\\"\\n}"
    }]
  }
}`
  },
  {
    id: 'ping',
    name: 'ping',
    description:
      '心跳检测 — 检查服务是否正常运行。不需要 API Key。',
    params: [],
    curlExample: `curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"ping","arguments":{}}}'`,
    responseExample: `{
  "jsonrpc": "2.0",
  "id": 12,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\\n  \\"status\\": \\"ok\\",\\n  \\"version\\": \\"0.1.0\\",\\n  \\"timestamp\\": \\"2025-07-07T12:00:00Z\\"\\n}"
    }]
  }
}`
  },
  {
    id: 'compare_personas',
    name: 'compare_personas',
    migrated: true,
    description:
      '（已迁移）让多个 Persona 对同一问题分别回答并对比。例如 compare_personas("是否进入东南亚市场？", ["战略顾问", "保守审核员"])。',
    params: [],
    curlExample: '',
    responseExample: '',
  },
  {
    id: 'match_persona',
    name: 'match_persona',
    migrated: true,
    description:
      '（已迁移）根据问题自动推荐最匹配的 Persona。例如 match_persona("如何制定增长战略？") 会返回匹配度最高的 Persona。',
    params: [],
    curlExample: '',
    responseExample: '',
  },
]

// ─── FAQ Data ─────────────────────────────────────────────────────

interface FAQItem {
  q: string
  a: string
}

const faqItems: FAQItem[] = [
  {
    q: 'Moltable 和 ChatGPT Memory 有什么区别？',
    a: 'ChatGPT Memory 仅在 OpenAI 生态内生效。Moltable 是跨 AI 的身份层——一次配置，Hermes、Claude、ChatGPT 和你未来使用的任何 MCP 兼容 Agent 都能共享同一套身份、偏好和记忆。此外，Moltable 提供 Persona 系统（多角色视角）、批量记忆管理和完整的数据导出/删除功能。',
  },
  {
    q: '我的数据存在哪里？安全吗？',
    a: '您的数据存储在 Moltable 托管的 Supabase 数据库（PostgreSQL）中，传输全程使用 HTTPS 加密，API Key 通过 SHA-256 哈希存储。我们不会将您的数据用于模型训练。您随时可以在控制面板中导出或删除全部数据。详细条款见《隐私政策》。',
  },
  {
    q: '支持哪些 AI 平台？',
    a: '任何支持 MCP（Model Context Protocol）标准的 AI Agent 都可以接入 Moltable，包括：Hermes Agent（原生推荐）、Claude Desktop App（通过 MCP 配置）、及任何实现了 MCP 客户端规范的工具。MCP 是 Anthropic 发起的开放标准，正在被越来越多的 AI 平台采纳。',
  },
  {
    q: '免费版有什么限制？',
    a: '免费版包含：1 个 Identity、2 个 Persona、最多 500 条记忆、基础 MCP 工具访问。Pro 版（¥15/月）解锁无限记忆、最多 10 个 Persona、浏览器插件和优先支持。',
  },
  {
    q: '如何贡献代码？',
    a: 'Moltable 是开源项目。请访问 GitHub 仓库，Fork 后提交 Pull Request。代码风格：Python 后端使用 FastAPI + PEP 8，前端使用 Next.js + Tailwind CSS + TypeScript。提交前请确保测试通过：pytest server/tests/。',
  },
  {
    q: '什么是 Persona？我该创建几个？',
    a: 'Persona 是 AI 的"角色人格"——包含自定义的 system prompt 和 traits（特质）。例如你可以创建"战略顾问"用于工作分析、"创意伙伴"用于头脑风暴、"审核员"用于代码审查。我们建议从 2-3 个核心角色开始，在使用过程中逐步完善。',
  },
  {
    q: '记忆冲突是什么？怎么处理？',
    a: '当新记忆与已有记忆的语义相似度超过 0.9 时，系统会标记为冲突并返回已有条目，而不是自动覆盖。这让您有机会确认：是添加新信息（强制保存），还是发现重复。在 save_memory 中设置 force=true 可跳过冲突检测直接覆盖。',
  },
]

// ─── Copy button component ───────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }}
      className="absolute top-3 right-3 p-1.5 rounded-btn text-ln-quaternary hover:text-ln-secondary hover:bg-ln-hover transition-all"
      aria-label="复制代码"
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  )
}

// ─── Code block component ────────────────────────────────────────

function CodeBlock({ label, code }: { label?: string; code: string }) {
  return (
    <div className="relative group rounded-card overflow-hidden shadow-border my-4">
      {label && (
        <div className="bg-ln-raised px-4 py-2 text-xs text-ln-tertiary font-ui border-b border-ln-border-subtle flex items-center gap-2">
          <Code size={12} className="text-ln-accent" />
          {label}
        </div>
      )}
      <pre className="px-4 py-3.5 text-sm leading-relaxed overflow-x-auto font-mono text-ln-secondary"
        style={{ backgroundColor: '#0a0b0c' }}
      >
        <code>{code}</code>
      </pre>
      <CopyButton text={code} />
    </div>
  )
}

// ─── Parameter table component ───────────────────────────────────

function ParamTable({ params }: { params: ParamDef[] }) {
  if (params.length === 0) {
    return (
      <p className="text-sm text-ln-tertiary font-body italic mb-4">此工具无需参数。</p>
    )
  }
  return (
    <div className="overflow-hidden rounded-card shadow-border mb-4">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-ln-border-subtle bg-ln-raised/60">
            <th className="py-[10px] px-4 text-left font-ui text-ln-secondary w-[120px]">参数</th>
            <th className="py-[10px] px-4 text-left font-ui text-ln-secondary w-[90px]">类型</th>
            <th className="py-[10px] px-4 text-left font-ui text-ln-secondary w-[60px]">必填</th>
            <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">说明</th>
          </tr>
        </thead>
        <tbody>
          {params.map((p) => (
            <tr key={p.name} className="border-b border-ln-border-subtle last:border-b-0">
              <td className="py-[10px] px-4 font-mono text-[13px] text-ln-accent-hover">{p.name}</td>
              <td className="py-[10px] px-4 text-ln-tertiary font-mono text-[12px]">{p.type}</td>
              <td className="py-[10px] px-4">
                {p.required ? (
                  <span className="text-ln-success text-xs font-ui">✅</span>
                ) : (
                  <span className="text-ln-quaternary text-xs">—</span>
                )}
              </td>
              <td className="py-[10px] px-4 text-ln-tertiary font-body">{p.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Section separator ───────────────────────────────────────────

function SectionSeparator() {
  return <hr className="border-ln-border-subtle my-10" />
}

// ─── Main Page Component ─────────────────────────────────────────

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('quickstart')
  const [activeApiTool, setActiveApiTool] = useState('auto_provision')
  const contentRef = useRef<HTMLDivElement>(null)

  // Intersection Observer for active section highlighting
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const id = entry.target.getAttribute('data-section')
            if (id) {
              setActiveSection(id)
              if (id.startsWith('api-')) {
                const toolName = id.replace('api-', '')
                setActiveApiTool(toolName)
              }
            }
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px' }
    )

    const sections = contentRef.current?.querySelectorAll('[data-section]')
    sections?.forEach((s) => observer.observe(s))
    return () => observer.disconnect()
  }, [])

  const isApiActive = activeSection === 'api' || activeSection.startsWith('api-')
  const effectiveSection = activeSection.startsWith('api-') ? 'api' : activeSection

  // Determine if a sidebar item or child is active
  const isActive = (id: string) => activeSection === id
  const isChildActive = (id: string) => activeSection === id

  // ── Scroll to section ──
  const scrollTo = (id: string) => {
    setActiveSection(id)
    if (id.startsWith('api-')) {
      setActiveApiTool(id.replace('api-', ''))
    }
    const el = document.querySelector(`[data-section="${id}"]`)
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)]">
      {/* ── Sidebar ── */}
      <aside className="hidden md:block w-[240px] flex-shrink-0 border-r border-ln-border-subtle self-start sticky top-14 max-h-[calc(100vh-3.5rem)] overflow-y-auto">
        <div className="px-3 py-6">
          <div className="flex items-center gap-2 mb-5 px-3">
            <Book size={16} className="text-ln-accent" />
            <span className="text-sm font-heading text-ln-text tracking-[-0.2px]">开发者文档</span>
          </div>
          <nav className="flex flex-col gap-0.5">
            {sidebarItems.map((item) => {
              const ItemIcon = item.icon
              const isItemActive = item.id === effectiveSection && !item.id.startsWith('api-')
              return (
                <div key={item.id}>
                  <button
                    onClick={() => scrollTo(item.id)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-btn text-sm transition-all duration-150 w-full text-left ${
                      isItemActive
                        ? 'bg-ln-accent-muted text-ln-accent-hover font-ui shadow-border-accent'
                        : 'text-ln-secondary font-body hover:bg-ln-hover'
                    }`}
                  >
                    <ItemIcon size={14} className="flex-shrink-0" />
                    <span>{item.label}</span>
                  </button>
                  {/* Sub-items for API section */}
                  {item.children && (
                    <div className="ml-4 mt-0.5 flex flex-col gap-0.5 border-l border-ln-border-subtle pl-2">
                      {item.children.map((child) => (
                        <button
                          key={child.id}
                          onClick={() => scrollTo(child.id)}
                          className={`text-xs py-1.5 px-2 rounded-btn text-left transition-all duration-150 ${
                            isChildActive(child.id)
                              ? 'text-ln-accent-hover font-ui bg-ln-accent-muted/50'
                              : 'text-ln-quaternary font-body hover:text-ln-tertiary hover:bg-ln-hover'
                          }`}
                        >
                          {child.label}
                          {child.badge && (
                            <span className="ml-1.5 text-[10px] px-1 py-0.5 rounded bg-ln-accent-muted/60 text-ln-accent-hover font-ui flex-shrink-0">{child.badge}</span>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* ── Content Area ── */}
      <div ref={contentRef} className="flex-1 min-w-0">
        <div className="max-w-3xl mx-auto px-6 py-10 md:py-14">

          {/* ── Mobile section selector ── */}
          <div className="md:hidden mb-6">
            <select
              value={activeSection}
              onChange={(e) => {
                const val = e.target.value
                setActiveSection(val)
                scrollTo(val)
              }}
              className="w-full px-3 py-2.5 rounded-btn bg-ln-surface text-ln-text text-sm font-ui shadow-border outline-none focus:shadow-border-accent"
            >
              {sidebarItems.map((item) => (
                <option key={item.id} value={item.id}>{item.label}</option>
              ))}
            </select>
          </div>

          {/* ════════════════════════════════════════════════════════
                     QUICK START
                     ════════════════════════════════════════════════════════ */}
          <section data-section="quickstart">
            <h1 className="text-3xl font-heading tracking-[-0.4px] text-ln-text mb-6">快速开始</h1>
            <div className="space-y-6 text-base leading-relaxed text-ln-secondary font-body">
              <p className="text-ln-text font-ui text-lg">三步完成 Moltable 接入，在任何 AI 中加载你的身份。</p>

              <div className="space-y-5">
                <div className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-ln-accent-muted text-ln-accent-hover flex items-center justify-center text-sm font-ui">1</span>
                  <div>
                    <h3 className="font-ui text-ln-text mb-1">注册 Moltable 账号</h3>
                    <p>访问 <a href="/register" className="text-ln-accent-hover hover:underline">moltable.ai/register</a> 完成注册，30 秒即可完成。</p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-ln-accent-muted text-ln-accent-hover flex items-center justify-center text-sm font-ui">2</span>
                  <div>
                    <h3 className="font-ui text-ln-text mb-1">获取 API Key</h3>
                    <p>登录控制面板，在 <strong>设置 → API Keys</strong> 中生成一个 Key。</p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-ln-accent-muted text-ln-accent-hover flex items-center justify-center text-sm font-ui">3</span>
                  <div>
                    <h3 className="font-ui text-ln-text mb-1">配置 AI Agent 并调用 auto_provision</h3>
                    <p>将 API Key 配置到你的 AI Agent 中，首次连接时调用 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">auto_provision</code> 工具，AI 自动加载你的身份、Persona 和记忆。</p>
                  </div>
                </div>
              </div>

              <SectionSeparator />

              <h2 className="text-xl font-heading text-ln-text tracking-[-0.3px]">尝试验证：调用 auto_provision</h2>
              <p>以下 curl 命令演示如何通过 MCP JSON-RPC 协议调用 auto_provision：</p>
              <CodeBlock
                label="curl — auto_provision"
                code={`curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"auto_provision","arguments":{}}}'`}
              />
              <p>成功时返回用户画像、行为规则、Persona 列表、活跃项目等完整上下文。</p>
            </div>
          </section>

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     INSTALLATION
                     ════════════════════════════════════════════════════════ */}
          <section data-section="installation">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">安装与配置</h2>

            <div className="space-y-6 text-base leading-relaxed text-ln-secondary font-body">
              <h3 className="text-lg font-ui text-ln-text">后端依赖</h3>
              <p>Moltable 后端使用 Python + FastAPI。推荐使用 Python 3.10+：</p>
              <CodeBlock label="pip 安装" code={`pip install -r requirements.txt

# 或直接安装核心依赖:
pip install fastapi uvicorn supabase httpx openai slowapi pydantic`} />

              <h3 className="text-lg font-ui text-ln-text mt-6">环境变量配置</h3>
              <p>复制 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">.env.example</code> 并填写：</p>
              <CodeBlock label=".env" code={`SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
DEEPSEEK_API_KEY=sk-your-deepseek-key  # 可选，咨询功能需要
MOLTABLE_API_KEY=your-admin-key`} />

              <h3 className="text-lg font-ui text-ln-text mt-6">Docker 部署</h3>
              <CodeBlock label="docker-compose.yml" code={`version: '3.8'
services:
  moltable:
    build: ./server
    ports:
      - "8642:8642"
    env_file: .env
    restart: unless-stopped`} />
              <CodeBlock label="启动" code={`docker-compose up -d
# 服务运行在 ${API_HOST}`} />
            </div>
          </section>

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     HERMES AGENT
                     ════════════════════════════════════════════════════════ */}
          <section data-section="hermes">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">Hermes Agent 接入</h2>

            <div className="space-y-6 text-base leading-relaxed text-ln-secondary font-body">
              <p>Hermes Agent 原生支持 Moltable 身份层。通过 Skill 机制一键加载。</p>

              <h3 className="text-lg font-ui text-ln-text">步骤 1：安装 Hermes Agent</h3>
              <CodeBlock label="npm 安装" code={`npm install -g hermes-agent`} />

              <h3 className="text-lg font-ui text-ln-text">步骤 2：配置 API Key</h3>
              <p>将你的 Moltable API Key 设置为环境变量：</p>
              <CodeBlock label="环境变量" code={`export MOLTABLE_API_KEY="mt_YOUR_API_KEY_HERE"`} />

              <h3 className="text-lg font-ui text-ln-text">步骤 3：加载 Moltable Skill</h3>
              <p>Hermes Agent 提供了官方 Moltable Skill。Skill 文件位于 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">~/.hermes/skills/moltable/</code>，包含自动配置逻辑：</p>
              <CodeBlock label="auto_provision 模式" code={`# 启动时自动加载 Moltable 身份
hermes --mcp-auto-provision moltable`} />

              <p className="text-ln-quaternary text-sm italic">当 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">MOLTABLE_API_KEY</code> 环境变量存在时，Hermes 会在启动时自动调用 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">auto_provision</code> 加载你的完整身份。</p>
            </div>
          </section>

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     CLAUDE DESKTOP
                     ════════════════════════════════════════════════════════ */}
          <section data-section="claude">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">Claude Desktop 接入</h2>

            <div className="space-y-6 text-base leading-relaxed text-ln-secondary font-body">
              <p>Claude Desktop App 支持通过 MCP 协议接入 Moltable。只需编辑配置文件。</p>

              <h3 className="text-lg font-ui text-ln-text">配置 claude_desktop_config.json</h3>
              <p>找到 Claude Desktop 的配置文件并添加 MCP Server 配置：</p>

              <div className="bg-ln-raised rounded-card p-3 mb-2 text-sm text-ln-quaternary font-mono border border-ln-border-subtle">
                macOS: ~/Library/Application Support/Claude/claude_desktop_config.json<br />
                Windows: %APPDATA%\Claude\claude_desktop_config.json
              </div>

              <CodeBlock
                label="claude_desktop_config.json"
                code={`{
  "mcpServers": {
    "moltable": {
      "command": "npx",
      "args": [
        "-y",
        "@moltable/mcp-server",
        "--api-key",
        "<YOUR_API_KEY>"
      ]
    }
  }
}`} />

              <h3 className="text-lg font-ui text-ln-text">验证连接</h3>
              <ol className="list-decimal ml-5 space-y-2">
                <li>保存配置文件后 <strong>重启 Claude Desktop</strong></li>
                <li>在对话中输入：<em>"加载我的 Moltable 身份"</em></li>
                <li>Claude 将自动调用 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">auto_provision</code> 工具加载你的身份信息</li>
              </ol>
            </div>
          </section>

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     API REFERENCE
                     ════════════════════════════════════════════════════════ */}
          <section data-section="api">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">API 参考</h2>
            <p className="text-ln-secondary font-body mb-8">
              Moltable 提供 MCP JSON-RPC 2.0 接口，共 <strong className="text-ln-text">{apiTools.filter((t) => !t.migrated).length}</strong> 个工具，另有 {apiTools.filter((t) => t.migrated).length} 个已迁移至 Agent 端。所有请求通过 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">POST /mcp</code> 端点发送。
            </p>

            <div className="mb-8 flex flex-wrap gap-2">
              {apiTools.map((tool) => (
                <button
                  key={tool.id}
                  onClick={() => scrollTo(`api-${tool.id}`)}
                  className={`text-xs px-2.5 py-1.5 rounded-btn font-mono transition-all ${
                    activeApiTool === tool.id
                      ? 'bg-ln-accent-muted text-ln-accent-hover shadow-border-accent'
                      : 'bg-ln-raised text-ln-tertiary hover:text-ln-secondary hover:bg-ln-hover'
                  }`}
                >
                  {tool.name}
                  {tool.migrated && <span className="ml-1 text-[10px] opacity-70">· 迁移</span>}
                </button>
              ))}
            </div>
          </section>

          {/* ── API Tool Sections ── */}
          {apiTools.map((tool, index) => (
            <div key={tool.id}>
              <SectionSeparator />
              <section data-section={`api-${tool.id}`}>
                <div className="flex items-center gap-2 mb-2">
                  <Code size={16} className="text-ln-accent flex-shrink-0" />
                  <h3 className="text-lg font-mono font-ui text-ln-text tracking-[-0.2px]">
                    {tool.name}
                  </h3>
                </div>
                <p className="text-ln-secondary font-body mb-4">{tool.description}</p>

                {tool.migrated ? (
                  <div className="mb-4 p-4 rounded-card bg-ln-accent-muted/40 border border-ln-border-subtle">
                    <p className="text-sm font-ui text-ln-accent-hover mb-1">⚠️ 已迁移至 Agent 端</p>
                    <p className="text-xs text-ln-tertiary font-body leading-relaxed">
                      该工具不再由 Moltable 服务端提供（2026-08-01 起从 MCP 工具列表中移除）。服务端不做 LLM 推理，人格匹配与多视角对比改由 Agent 端完成——Agent 读取 list_personas / get_persona 返回的 traits 与 system_prompt 后自行判断与生成。因此不会出现在 tools/list 中，直接调用会返回 -32601 方法不存在。
                    </p>
                  </div>
                ) : (
                  <>
                <h4 className="text-sm font-ui text-ln-text mb-2">参数</h4>
                <ParamTable params={tool.params} />

                <h4 className="text-sm font-ui text-ln-text mb-2">请求示例</h4>
                <CodeBlock label="curl" code={tool.curlExample} />

                <h4 className="text-sm font-ui text-ln-text mb-2">响应示例</h4>
                <CodeBlock
                  label="Response (JSON-RPC 2.0)"
                  code={tool.responseExample}
                />
                  </>
                )}
              </section>
            </div>
          ))}

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     MCP PROTOCOL
                     ════════════════════════════════════════════════════════ */}
          <section data-section="mcp">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">MCP 协议</h2>

            <div className="space-y-6 text-base leading-relaxed text-ln-secondary font-body">
              <p>Moltable 基于 <strong className="text-ln-text">MCP (Model Context Protocol) 2024-11-05</strong> 开放标准构建，使用 JSON-RPC 2.0 作为通信协议。</p>

              <h3 className="text-lg font-ui text-ln-text">JSON-RPC 2.0 规范</h3>
              <p>所有请求和响应遵循 JSON-RPC 2.0 规范：</p>
              <CodeBlock label="请求格式" code={`{
  "jsonrpc": "2.0",        // 固定版本号
  "id": 1,                 // 请求 ID（支持数字/字符串）
  "method": "tools/call",  // 方法名
  "params": {
    "name": "tool_name",   // 工具名
    "arguments": { ... }   // 工具参数
  }
}`} />
              <CodeBlock label="成功响应" code={`{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "..." }
    ]
  }
}`} />
              <CodeBlock label="错误响应" code={`{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "认证失败",
    "data": { "details": "API Key 无效" }
  }
}`} />

              <h3 className="text-lg font-ui text-ln-text">发现端点</h3>
              <p>MCP 规范定义了 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">.well-known</code> 发现端点：</p>
              <CodeBlock label="GET /.well-known/mcp" code={`curl ${API_HOST}/.well-known/mcp`} />
              <CodeBlock label="响应" code={`{
  "schemaVersion": "2024-11-05",
  "server": {
    "name": "moltable",
    "version": "0.1.0",
    "description": "Moltable — AI Identity Layer"
  },
  "capabilities": {
    "tools": {
      "total": 12,
      "tools": [
        { "name": "auto_provision", "description": "..." },
        ...
      ]
    }
  },
  "endpoints": {
    "jsonrpc": "/mcp",
    "transport": "http"
  },
  "authentication": {
    "type": "api-key",
    "header": "X-API-Key"
  }
}`} />

              <h3 className="text-lg font-ui text-ln-text">认证方式</h3>
              <p>所有 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">tools/list</code> 和 <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">tools/call</code> 请求需要在请求头中携带 API Key：</p>
              <CodeBlock label="认证 Header" code={`X-API-Key: mt_YOUR_API_KEY_HERE`} />
              <p>
                <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">ping</code> 不需要认证。
                <code className="text-ln-accent-hover bg-ln-raised px-1.5 py-0.5 rounded text-[13px] font-mono">initialize</code> 需要 API Key 认证（与标准 MCP 不同，出于安全考虑）。
              </p>

              <h3 className="text-lg font-ui text-ln-text">支持的方法</h3>
              <div className="overflow-hidden rounded-card shadow-border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-ln-border-subtle bg-ln-raised/60">
                      <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">方法</th>
                      <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">说明</th>
                      <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">需要认证</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ['initialize', 'MCP 协议初始化', '是（安全设计）'],
                      ['ping', '心跳检测', '否'],
                      ['tools/list', '列出所有可用工具', '是'],
                      ['tools/call', '调用指定工具', '是'],
                    ].map(([method, desc, auth]) => (
                      <tr key={method} className="border-b border-ln-border-subtle last:border-b-0">
                        <td className="py-[10px] px-4 font-mono text-[13px] text-ln-accent-hover">{method}</td>
                        <td className="py-[10px] px-4 text-ln-tertiary font-body">{desc}</td>
                        <td className="py-[10px] px-4 text-ln-tertiary">{auth}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <h3 className="text-lg font-ui text-ln-text">批量请求</h3>
              <p>MCP 端点支持发送 JSON 数组进行批量请求：</p>
              <CodeBlock label="批量请求" code={`curl -X POST ${API_HOST}/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '[
    {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"save_memory","arguments":{"content":"批量测试1","category":"fact"}}},
    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"save_memory","arguments":{"content":"批量测试2","category":"fact"}}}
  ]'`} />
              <p>响应顺序与请求顺序一致。</p>

              <h3 className="text-lg font-ui text-ln-text">错误码</h3>
              <div className="overflow-hidden rounded-card shadow-border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-ln-border-subtle bg-ln-raised/60">
                      <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">Code</th>
                      <th className="py-[10px] px-4 text-left font-ui text-ln-secondary">含义</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ['-32700', '解析错误 — JSON 格式无效'],
                      ['-32600', '无效请求 — 不符合 JSON-RPC 2.0 规范'],
                      ['-32601', '方法不存在'],
                      ['-32602', '参数无效 — 缺少必填参数或类型错误'],
                      ['-32603', '内部错误'],
                      ['-32000', '工具调用错误'],
                      ['-32001', '认证失败 — API Key 无效或已吊销'],
                      ['-32002', '服务未初始化'],
                    ].map(([code, desc]) => (
                      <tr key={code} className="border-b border-ln-border-subtle last:border-b-0">
                        <td className="py-[10px] px-4 font-mono text-[13px] text-ln-error">{code}</td>
                        <td className="py-[10px] px-4 text-ln-tertiary font-body">{desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <SectionSeparator />

          {/* ════════════════════════════════════════════════════════
                     FAQ
                     ════════════════════════════════════════════════════════ */}
          <section data-section="faq">
            <h2 className="text-2xl font-heading tracking-[-0.3px] text-ln-text mb-6">常见问题</h2>

            <div className="space-y-0">
              {faqItems.map((item, i) => (
                <details
                  key={i}
                  className="group border-b border-ln-border-subtle last:border-b-0 py-4 open:pb-6"
                >
                  <summary className="flex items-center justify-between cursor-pointer list-none text-ln-text font-ui text-base">
                    <span className="pr-4">{item.q}</span>
                    <ChevronRight size={16} className="text-ln-quaternary flex-shrink-0 transition-transform group-open:rotate-90" />
                  </summary>
                  <div className="mt-3 text-sm text-ln-secondary font-body leading-relaxed pl-0">
                    {item.a}
                  </div>
                </details>
              ))}
            </div>
          </section>

          {/* ── Footer spacing ── */}
          <div className="h-12" />
        </div>
      </div>
    </div>
  )
}
