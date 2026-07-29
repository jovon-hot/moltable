'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function MCPArticle() {
  return (
    <ArticleLayout title="MCP 协议：为什么它是 AI 的 USB-C" date="2026-06-20">
      <p>如果你在 2024 年用过 Claude Desktop，你可能已经间接用过了 MCP（Model Context Protocol）。如果你用过 Cursor、Hermes、或者 Gemini CLI，你大概率也用了它——只是你不知道。</p>

      <h2>MCP 是什么</h2>
      <p>MCP 是 Anthropic 在 2024 年 11 月发布的开源协议，全称 Model Context Protocol。它定义了一套标准，让 AI 模型（LLM）能够安全、结构化地调用外部工具和数据源。</p>
      <p>简单类比：如果说 AI 是手机，MCP 就是 USB-C 接口。在 USB-C 之前，每个设备都有自己的充电口，互不兼容。MCP 之前的 AI 工具调用也是如此——每个 AI 平台都有自己的插件系统、自己的 API 格式、自己的认证方式。</p>
      <p>MCP 改变了这一点。它定义了三个核心概念：</p>
      <ul>
        <li><strong>Tools</strong>：AI 可以调用的外部功能（搜索记忆、保存偏好、查询数据库）</li>
        <li><strong>Resources</strong>：AI 可以读取的外部数据（文件、文档、API 响应）</li>
        <li><strong>Prompts</strong>：预定义的提示模板</li>
      </ul>

      <h2>MCP vs A2A：互补而非竞争</h2>
      <p>很多人把 MCP 和 Google 的 Agent-to-Agent (A2A) 协议放在一起比较，认为它们是竞争关系。实际上它们解决的是不同问题：</p>
      <ul>
        <li><strong>MCP</strong> 解决 Agent-to-Tool 通信：Agent 如何调用工具</li>
        <li><strong>A2A</strong> 解决 Agent-to-Agent 通信：Agent 之间如何协作</li>
      </ul>
      <p>两者互补。未来的 AI 系统会同时使用 MCP（连接工具）和 A2A（连接其他 Agent）。</p>

      <h2>Moltable 为什么选择 MCP</h2>
      <p>Moltable 是 AI 身份层——它不执行任务，不生成内容。它的职责是让 AI Agent 在任何平台上都能加载用户的身份、偏好和记忆。这个定位天然适合 MCP：</p>
      <ul>
        <li>Agent 通过 MCP 连接 Moltable Server</li>
        <li>调用 auto_provision() 一键加载用户完整上下文</li>
        <li>通过 search_memory / save_memory 读写记忆</li>
        <li>通过 list_personas / consult_persona 切换人格</li>
      </ul>
      <p>因为 MCP 是开放标准，任何支持 MCP 的 AI 客户端——Hermes、Claude、Cursor、Gemini CLI——都能直接接入 Moltable。不需要为每个平台写适配代码。</p>

      <h2>未来：Agent 的操作系统</h2>
      <p>如果把 MCP 比作 USB-C，那 MCP Server 就是外设驱动程序——每个 MCP Server 暴露一组工具，Agent 通过标准协议调用它们。Moltable 是这个生态中的一个"驱动"：身份驱动。其他有：文件系统驱动、数据库驱动、浏览器驱动、邮件驱动……</p>
      <p>当足够多的"驱动"存在时，AI Agent 就真正拥有了操作系统的能力——像人类一样，通过统一的接口操作数字世界的各种工具。MCP 就是这个统一接口。</p>
    </ArticleLayout>
  )
}

function ArticleLayout({ title, date, children }: { title: string; date: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <Link
          href="/blog"
          className="inline-flex items-center gap-2 text-sm text-ln-tertiary hover:text-ln-accent font-ui mb-8 transition-colors"
        >
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
