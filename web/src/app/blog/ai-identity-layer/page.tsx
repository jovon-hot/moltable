'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function IdentityArticle() {
  return (
    <ArticleLayout title="AI 身份层的设计哲学：从 Memory 到 Identity" date="2026-06-28">
      <p>2025-2026 年，AI Memory 赛道出现了至少 10 个开源项目：mem0 (58K⭐)、Engram (4.4K⭐)、Nocturne (1.2K⭐)、Wax、Stash、Mnemon……它们都在做同一件事：让 AI 记住更多。</p>
      <p>但"记住更多"是否真的解决了用户的核心问题？</p>

      <h2>Memory 的问题</h2>
      <p>记忆系统有两个根本性的局限：</p>
      <ol>
        <li><strong>记忆是碎片化的</strong>：100 条偏好、50 条事实、200 条决策——它们之间没有层级关系。Agent 无法区分"用户喜欢表格"和"用户是 FOST 集团的 CEO"哪个更重要。</li>
        <li><strong>记忆是被动的</strong>：Agent 需要先 search 才能获取记忆。如果 Agent 不知道要搜什么，记忆就形同虚设。</li>
      </ol>
      <p>这就像给了你一个无限容量的硬盘，但没有文件系统。数据都在，但你找不到。</p>

      <h2>Identity 的解法</h2>
      <p>Moltable 选择了一个不同的入口：不是"让 AI 记住更多"，而是"让 AI 知道你是谁"。</p>
      <p>Identity 和 Memory 的区别在于：</p>
      <ul>
        <li><strong>Memory</strong> 是被动的：Agent 需要主动搜索</li>
        <li><strong>Identity</strong> 是主动的：Agent 在连接时就加载</li>
      </ul>
      <p>这对应到 Moltable 的 auto_provision() —— Agent 连接时一次性获取：用户画像（姓名/时区/语言）、行为规则（报告用表格、结论先行）、活跃项目、可用 Persona、最近决策。</p>
      <p>不需要搜索。不需要猜测。Agent 从一开始就以完整的上下文工作。</p>

      <h2>三层架构：Identity → Persona → Agent</h2>
      <p>这是 Moltable 最核心的设计决策——竞品中没有任何项目做这个分层：</p>
      <ul>
        <li><strong>Identity（身份）</strong>：用户本人。唯一、不可复制。拥有所有数据的所有权。</li>
        <li><strong>Persona（人格）</strong>：行为模式。用户可以创建多个 Persona（战略顾问、保守审核员、创意伙伴），共享同一套 Memory，但输出风格完全不同。</li>
        <li><strong>Agent（执行体）</strong>：工具调用能力。PPT 生成器、数据分析器。不拥有人格，纯执行。</li>
      </ul>
      <p>这个架构的关键洞察是：同一个人的 Identity 是稳定的，但面对不同场景需要不同的 Persona。做战略决策时需要激进的分析师，审核合同时需要保守的审核员。两个 Persona 共享所有记忆，但输出不同——就像同一个人的左右脑。</p>

      <h2>为什么竞品不做</h2>
      <p>不是想不到，而是定位决定的。mem0 定位"通用记忆层"——适合任何 AI 应用插入记忆功能。这个定位天然偏向碎片化（每条记忆独立存储），不适合结构化分层。</p>
      <p>Moltable 定位"身份层"——只服务 AI Agent 和 AI 重度用户。这个窄定位允许我们做深：不仅是记忆，更是身份、人格、决策链的完整体系。</p>

      <h2>Identity 是 AI 时代的个人数据主权</h2>
      <p>每一次对话中，AI 都在了解你——你的偏好、你的工作、你的决策模式。这些数据目前散落在 ChatGPT、Claude、Hermes 各自的封闭记忆系统中。</p>
      <p>Moltable 要做的是让这些数据回到你手中。不是你为 AI 提供数据，而是 AI 为你加载身份。</p>
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
