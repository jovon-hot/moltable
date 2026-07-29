'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function PersonaArticle() {
  return (
    <ArticleLayout title="跨平台 Persona 管理：一个身份，多种人格" date="2026-07-05">
      <p>想象一个场景：你是创业者，今天要做两个决策。第一个是"是否进入东南亚市场"——需要激进的分析师视角，先看机会再看风险。第二个是"审核供应商合同"——需要保守的审核员视角，逐项检查、红线标注。</p>
      <p>如果只有一个 AI，它要么激进要么保守，无法同时满足两种需求。这就是 Persona 系统要解决的问题。</p>

      <h2>Persona 不是 Prompt 模板</h2>
      <p>很多人以为 Persona 就是一个预设的 System Prompt——"你是一个战略顾问，请用麦肯锡方法分析"。这只是表面。</p>
      <p>Moltable 的 Persona 系统比单纯的 Prompt 模板多三层：</p>
      <ol>
        <li><strong>共享记忆</strong>：所有 Persona 共享同一套用户记忆。战略顾问和保守审核员都"知道"用户是 FOST 集团的 CEO、偏好数据驱动的报告、当前在做月度经营分析。但它们的输出完全不同。</li>
        <li><strong>人格持久化</strong>：Persona 不是即抛的。创建的 Persona 跨会话、跨 AI 平台存在。你在 Hermes 里用了"战略顾问"，下次在 Claude 里也能加载同一个 Persona。</li>
        <li><strong>自我进化</strong>：Persona 有版本历史（Git 式）。每次调整 traits 或 system_prompt，旧版本保留。你可以回到 v1，也可以 fork 出实验版本。</li>
      </ol>

      <h2>实战：创建两个 Persona</h2>
      <p>在 Moltable Dashboard 的 Persona 页，创建一个 Persona 只需三步：</p>
      <ol>
        <li><strong>命名</strong>：如"战略顾问"</li>
        <li><strong>定义 System Prompt</strong>：描述思维模式和分析框架</li>
        <li><strong>设置 Traits</strong>：结构化的行为标签（如 style: "麦肯锡", risk: "激进"）</li>
      </ol>

      <p>创建完成后，Agent 可以通过 MCP 工具随时切换：</p>
      <ul>
        <li><code>list_personas()</code> — 列出所有可用 Persona</li>
        <li><code>match_persona("如何进入东南亚市场？")</code> — 自动推荐最匹配的 Persona</li>
        <li><code>consult_persona("战略顾问", "分析东南亚市场")</code> — 用指定 Persona 回答问题</li>
        <li><code>compare_personas("这个问题", ["战略顾问", "保守审核员"])</code> — 多 Persona 同时回答并对比</li>
      </ul>

      <h2>实际效果：同一问题，两种视角</h2>
      <p>以"是否进入东南亚市场"为例：</p>
      <div className="grid md:grid-cols-2 gap-4 my-6">
        <div className="p-4 rounded-card bg-ln-panel shadow-border text-sm">
          <h4 className="font-heading text-ln-accent mb-2">战略顾问的视角</h4>
          <p className="text-ln-secondary leading-relaxed">
            东南亚 6.5 亿人口，电商渗透率从 2022 年的 5% 增长到 2026 年的 20%+
            ——这是一个每年翻倍的市场。建议先用轻资产模式在新加坡设立总部，
            用 Lazada/Shopee 平台验证 PMF，3 个月内跑通后再自建团队。
          </p>
        </div>
        <div className="p-4 rounded-card bg-ln-panel shadow-border text-sm">
          <h4 className="font-heading text-red-400 mb-2">保守审核员的视角</h4>
          <p className="text-ln-secondary leading-relaxed">
            ⚠️ 6 个风险点需要先解决：① 印尼对外资电商的新规（PP No.80/2023）
            要求本地合资且外方持股不超过 49%；② 物流基础设施不均衡；
            ③ 汇率波动风险（印尼盾 2024 年贬值 8%）；④……建议先做 6 个月试点。
          </p>
        </div>
      </div>
      <p>这两个回答同时存在。用户不需要在两个 AI 之间切换——同一个 AI，两套思维，一次对比。</p>

      <h2>跨平台：一次创建，到处使用</h2>
      <p>Persona 存储在 Moltable 云端。你在 Hermes 里创建的"战略顾问"，在 Claude Desktop 里也能加载。因为 Moltable 通过 MCP 协议暴露 Persona 数据，任何支持 MCP 的 AI 客户端都能调用。</p>
      <p>这解决了 AI 时代最棘手的问题之一：数据孤岛。你的 ChatGPT 有你的对话历史，你的 Claude 有你的偏好，你的 Hermes 有你的项目记忆——但它们是分离的。Persona 系统让它们共享同一个身份定义。</p>
      <p>目前支持 Hermes、Claude Desktop、Cursor。浏览器插件支持 ChatGPT 和 Gemini（通过注入侧边栏）。</p>

      <h2>未来：Persona Marketplace</h2>
      <p>Phase 3 规划中的 Persona Marketplace 将允许用户分享、交易 Persona。一个好的 Persona——比如"科技 IPO 路演顾问"——包含了特定领域的思维框架和沟通风格，是有价值的数字资产。</p>
      <p>想象一个场景：你需要做 SEO 优化。"SEO 专家"这个 Persona 已经在 Marketplace 上有 5000+ 用户验证过——你直接加载，不需要自己定义。</p>
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
