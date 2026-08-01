'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="2026 AI 开发者工具链全景：从 LLM 到 Identity 的完整技术栈" date="2026-08-01">
      <p>2024 年，AI 开发者的工具箱里只有两样东西：OpenAI API Key 和 LangChain。到了 2026 年，技术栈已经发展成一个多层架构——每一层都有多个竞争者，选型比两年前复杂了十倍。</p>
      <p>这篇文章梳理现代 AI Agent 开发的完整技术栈，帮你做出明智的选型决策。</p>

      <h2>全景架构：六层技术栈</h2>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`┌─────────────────────────────────────────┐
│  第6层: MCP Tools（工具层）              │
│  文件系统 | 数据库 | 浏览器 | 邮件 | ... │
├─────────────────────────────────────────┤
│  第5层: Identity & Memory（身份层）      │
│  Moltable | mem0 | Zep | Cognee          │
├─────────────────────────────────────────┤
│  第4层: Vector DB（向量存储层）          │
│  pgvector | Pinecone | Weaviate | Qdrant │
├─────────────────────────────────────────┤
│  第3层: Orchestration（编排层）          │
│  LangChain | CrewAI | AutoGen | Dify     │
├─────────────────────────────────────────┤
│  第2层: LLM Gateway（网关层）            │
│  LiteLLM | Portkey | Helicone            │
├─────────────────────────────────────────┤
│  第1层: LLM（模型层）                    │
│  Claude | GPT | DeepSeek | Qwen | Gemini │
└─────────────────────────────────────────┘`}
      </pre>

      <h2>第1层：LLM 模型层</h2>
      <p>2026 年的模型格局是"两超多强"：</p>
      <ul>
        <li><strong>Claude 4 (Anthropic)</strong>：代码和推理能力领先，MCP 的原生支持者</li>
        <li><strong>GPT-5 (OpenAI)</strong>：多模态最强，生态最成熟</li>
        <li><strong>DeepSeek v4</strong>：中文能力第一，性价比最高（API 价格仅为 Claude 的 1/10）</li>
        <li><strong>Qwen 3 (阿里)</strong>：开源模型中的综合实力派，128K 上下文</li>
        <li><strong>Gemini 2.5 (Google)</strong>：A2A 协议主导者，企业生态整合</li>
      </ul>
      <p>选型建议：中文场景优先 DeepSeek v4；代码和复杂推理优先 Claude；成本敏感选 Qwen 3 开源自部署。</p>

      <h2>第2层：LLM 网关层</h2>
      <p>当你用了多个模型后，需要一个统一接口来管理 API Key、做负载均衡、记录日志：</p>
      <ul>
        <li><strong>LiteLLM</strong>：开源，支持 100+ LLM 提供商，OpenAI 兼容格式</li>
        <li><strong>Portkey</strong>：托管网关，内置缓存、回退、A/B 测试</li>
        <li><strong>Helicone</strong>：专注于日志和可观测性</li>
      </ul>
      <p>如果你刚开始构建多模型应用，LiteLLM 是默认选择。</p>

      <h2>第3层：编排层</h2>
      <p>单个 LLM 调用很简单，但多步推理、多 Agent 协作需要编排：</p>
      <ul>
        <li><strong>LangChain</strong>：最大的社区，但抽象层太重，2026 年趋势是 LangGraph（状态图编排）</li>
        <li><strong>CrewAI</strong>：角色化多 Agent 协作，定义 Role → Task → Crew 三层抽象</li>
        <li><strong>AutoGen (Microsoft)</strong>：对话式多 Agent，适合研究场景</li>
        <li><strong>Dify</strong>：低代码 AI 应用平台，中国市场占有率第一</li>
      </ul>
      <p>选型建议：多 Agent 协作选 CrewAI；复杂工作流选 LangGraph；低代码/非技术团队选 Dify。</p>

      <h2>第4层：向量数据库</h2>
      <p>RAG（检索增强生成）的底层存储：</p>
      <ul>
        <li><strong>pgvector (PostgreSQL 扩展)</strong>：如果你已经在用 PG，直接加扩展，最省事</li>
        <li><strong>Pinecone</strong>：托管向量数据库，性能和易用性最好，但贵</li>
        <li><strong>Qdrant</strong>：开源且高性能，Rust 写的，适合自托管</li>
        <li><strong>Weaviate</strong>：混合搜索（向量 + 关键词），自带 AI 模块</li>
      </ul>
      <p>选型建议：已有 PG 的团队用 pgvector；需要极致性能选 Qdrant；不想运维选 Pinecone。</p>

      <h2>第5层：身份 & 记忆层 ⭐</h2>
      <p>这是 2026 年最被低估的一层。大多数开发者花了 90% 的精力在模型和编排上，却忽略了：<strong>Agent 如果不记得用户是谁，再强的推理能力也只能做一次性的任务</strong>。</p>
      <p>主流的身份和记忆方案已在 <Link href="/blog/agent-memory-landscape-2026" className="text-ln-accent hover:underline">记忆系统全景对比</Link> 中详细分析，这里做个速览：</p>
      <ul>
        <li><strong>Moltable</strong>：专攻身份层。Persona 系统 + 分类记忆 + MCP 原生 + 中文一等公民</li>
        <li><strong>mem0</strong>：通用记忆层。向量 + 图架构。社区最大但 Pro 版 $249/月</li>
        <li><strong>Zep</strong>：企业级记忆。SOC2 合规，适合强监管行业</li>
      </ul>
      <p>Moltable 的独特价值在于<strong>身份</strong>而非<strong>记忆</strong>——它会记住"你是谁"（偏好、角色、行为规则），而不仅仅是"你说了什么"（对话记录）。这两者互补。</p>

      <h2>第6层：MCP 工具层</h2>
      <p>这是 Agent 的"手和脚"——让 Agent 执行实际操作：</p>
      <ul>
        <li><strong>文件系统</strong>：读写本地文件</li>
        <li><strong>数据库</strong>：查询 PostgreSQL、MongoDB</li>
        <li><strong>浏览器</strong>：Puppeteer/Browserbase 驱动</li>
        <li><strong>邮件/日历</strong>：Gmail、Outlook 集成</li>
        <li><strong>GitHub</strong>：代码仓库操作</li>
        <li><strong>Slack/企微</strong>：消息发送</li>
      </ul>
      <p>MCP 协议让这些工具的接入变成标准化的"即插即用"。未来会有更多工具以 MCP Server 的形式发布。</p>

      <h2>Moltable 在技术栈中的位置</h2>
      <p>Moltable 定位在第5层——身份 & 记忆层。但它不是孤立的：</p>
      <ul>
        <li><strong>向下</strong>：通过 MCP 协议与编排层（LangChain/CrewAI）和 Gateway 层互联</li>
        <li><strong>向上</strong>：存储的记忆和 Persona 影响 Agent 如何使用第6层的工具</li>
        <li><strong>横向</strong>：与 mem0 / Zep 互补——Moltable 管身份，它们管通用记忆</li>
      </ul>
      <p>完整的 AI 技术栈，身份层是不可或缺的一块拼图。2026 年，这块拼图终于被认真对待了。</p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable — 为你的技术栈补上身份层</Link></p>
    </ArticleLayout>
  )
}

function ArticleLayout({ title, date, children }: { title: string; date: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-ln-tertiary hover:text-ln-accent font-ui mb-8 transition-colors">
          <ArrowLeft size={14} /> 返回博客
        </Link>
        <h1 className="text-3xl font-heading tracking-[-0.4px] mb-3">{title}</h1>
        <p className="text-sm text-ln-tertiary mb-10 font-ui">{date}</p>
        <div className="prose prose-invert prose-sm max-w-none prose-headings:font-heading prose-headings:tracking-[-0.24px] prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-4 prose-p:text-ln-secondary prose-p:leading-relaxed prose-li:text-ln-secondary prose-strong:text-ln-text">
          {children}
        </div>
      </div>
    </div>
  )
}
