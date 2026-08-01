'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable" date="2026-07-10">
      <p>如果你在 2025 年构建过 AI Agent，你一定遇到过这个问题：Agent 聊完就忘。今天告诉它你的 API Key 前缀是 <code>molt_</code>，明天它就不记得了。记忆系统——Agent Memory——是 2026 年 AI 基础设施最热的赛道之一。</p>
      <p>但选哪个？mem0 还是 Zep？Cognee 还是 Letta？还是专做身份层的 Moltable？这篇文章从架构、定价、MCP 支持和中文适配四个维度，做一次完整的横向对比。</p>

      <h2>为什么 Agent 需要记忆系统</h2>
      <p>LLM 本质上是无状态的。每次 API 调用都是一张白纸。要让 Agent 拥有"长期记忆"，需要外挂一个存储层：</p>
      <ul>
        <li><strong>短期记忆</strong>：对话窗口内的上下文（受 token 限制）</li>
        <li><strong>长期记忆</strong>：跨会话持久化的偏好、事实、决策</li>
        <li><strong>语义记忆</strong>：向量化的知识检索（RAG 的基础）</li>
        <li><strong>身份记忆</strong>："我是谁、我喜欢什么、我做过什么"</li>
      </ul>
      <p>大多数记忆系统只做前三种。Moltable 专攻第四种。</p>

      <h2>五大记忆系统横向对比</h2>

      <h3>mem0（62K ★ GitHub，$249/月 Pro）</h3>
      <p>mem0 是当前最流行的开源记忆层。核心是向量搜索 + 图数据库的混合架构。它自动从对话中提取实体和关系，存储为结构化记忆。优势是社区庞大、文档完善、支持多种 LLM。劣势：Pro 版 $249/月对个人开发者不友好；中文支持一般，分词和语义理解依赖底层模型。</p>

      <h3>Zep（$125-375/月 Enterprise）</h3>
      <p>Zep 定位企业级。支持 SOC2、GDPR 合规，提供事实提取、摘要生成、时间线重建。架构上与 mem0 类似但更偏向对话历史的时序存储。适合医疗、金融等强合规场景。劣势：价格更高，开源版本功能受限；MCP 支持目前仅在企业版。</p>

      <h3>Cognee（29.6K ★）</h3>
      <p>Cognee 走图谱路线——用 Neo4j 或 NetworkX 构建知识图谱，适合需要深度推理的场景（如法律分析、科研文献综述）。优势是可解释性强，每一个记忆都有明确的图关系。劣势：图谱构建慢，实时查询延迟高；不适合高频读写的 Agent 场景。</p>

      <h3>Letta（$20/月）</h3>
      <p>Letta（前 MemGPT）是最早探索"操作系统式记忆管理"的项目。它让 LLM 自主管理自己的上下文窗口——类似操作系统的虚拟内存分页。$20/月的定价非常友好，但功能相对单一：主要做对话历史的智能压缩和检索。</p>

      <h3>Moltable（Free Tier 可用）</h3>
      <p>Moltable 不做通用记忆，专攻<strong>身份层</strong>。它把记忆分为 7 个类别（preference、decision、fact、project、insight、task、relationship），并引入 Persona 概念——同一用户可以有多个"人格"，每个 Persona 加载不同的记忆子集和系统提示。MCP 原生支持，任何 MCP 客户端都能直连。中文是一等公民。</p>

      <h2>架构对比一览</h2>
      <table className="w-full text-sm my-6 border-collapse">
        <thead>
          <tr className="border-b border-ln-border">
            <th className="text-left py-2 pr-4">系统</th>
            <th className="text-left py-2 pr-4">记忆架构</th>
            <th className="text-left py-2 pr-4">MCP 支持</th>
            <th className="text-left py-2 pr-4">中文</th>
            <th className="text-left py-2">起步价</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">mem0</td>
            <td className="py-2 pr-4">向量 + 图</td>
            <td className="py-2 pr-4">✅</td>
            <td className="py-2 pr-4">一般</td>
            <td className="py-2">$249/月</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">Zep</td>
            <td className="py-2 pr-4">向量 + 时序</td>
            <td className="py-2 pr-4">企业版</td>
            <td className="py-2 pr-4">一般</td>
            <td className="py-2">$125/月</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">Cognee</td>
            <td className="py-2 pr-4">知识图谱</td>
            <td className="py-2 pr-4">❌</td>
            <td className="py-2 pr-4">一般</td>
            <td className="py-2">免费开源</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">Letta</td>
            <td className="py-2 pr-4">虚拟内存</td>
            <td className="py-2 pr-4">❌</td>
            <td className="py-2 pr-4">一般</td>
            <td className="py-2">$20/月</td>
          </tr>
          <tr>
            <td className="py-2 pr-4"><strong>Moltable</strong></td>
            <td className="py-2 pr-4">身份层</td>
            <td className="py-2 pr-4">✅ 原生</td>
            <td className="py-2 pr-4">一等公民</td>
            <td className="py-2">免费起步</td>
          </tr>
        </tbody>
      </table>

      <h2>选型建议</h2>
      <ul>
        <li><strong>通用记忆 → mem0</strong>：社区最大，生态最成熟，适合大多数场景</li>
        <li><strong>企业合规 → Zep</strong>：SOC2、GDPR、审计日志，合规团队的最爱</li>
        <li><strong>深度推理 → Cognee</strong>：图结构让关系推理变得直观</li>
        <li><strong>轻量记忆 → Letta</strong>：$20/月，个人开发者友好</li>
        <li><strong>身份层 → Moltable</strong>：如果你关心的是"AI 记住我是谁"而不是"AI 记住某段对话"，Moltable 是目前唯一的选择</li>
      </ul>
      <p>更妙的是，Moltable 可以和 mem0 或 Zep 组合使用——Moltable 管身份，mem0 管通用记忆，各司其职。</p>

      <h2>一个实际例子</h2>
      <p>假设你是 FOST 集团的 CTO，用一个 Agent 做代码审查，另一个做市场分析。你希望代码审查的 Agent 很严格、用英文术语；市场分析的 Agent 很激进、用中文写文案。mem0 做不到这点——它会把你所有偏好混在一起。Moltable 的 Persona 系统可以：创建两个 Persona，各自加载不同的 system prompt 和记忆子集，Agent 连接时指定 persona_id 即可。</p>
      <p>这就是"记忆"和"身份"的区别：记忆是数据，身份是视角。</p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">体验 Moltable 身份层 — 90 天免费试用</Link></p>
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
