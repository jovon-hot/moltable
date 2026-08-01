'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="换电脑不换记忆：AI 身份同步完全指南" date="2026-07-25">
      <p>换新电脑的兴奋通常在 30 分钟内消退。你打开终端、启动 Claude Desktop、输入第一个问题——然后发现，它完全不认识你。</p>
      <p>你在旧 Mac 上花了三个月"调教"好的 AI——你的代码风格偏好、项目的命名规范、每周五下午的复盘模板——全部归零。AI 又变成了出厂设置。</p>
      <p>这个痛点，2026 年有了系统级的解决方案：<strong>AI 身份同步（Identity Sync）</strong>。</p>

      <h2>传统方案为什么不行</h2>
      <p>大多数人的"同步"方法是这样的：</p>
      <ul>
        <li>把 <code>~/.claude</code> 或 <code>~/.hermes</code> 目录打包拷贝</li>
        <li>手动导出 Prompt 模板</li>
        <li>在新电脑上重写一遍 .cursorrules</li>
      </ul>
      <p>这有三个致命缺陷：</p>
      <ol>
        <li><strong>不跨平台</strong>：Claude 和 Hermes 的配置格式不同，无法互通</li>
        <li><strong>不完整</strong>：你只能同步配置文件，无法同步"AI 在对话中学到的偏好"</li>
        <li><strong>不实时</strong>：你在 Mac 上教会 AI 的东西，不会自动出现在 Windows 上</li>
      </ol>

      <h2>Moltable 的 Identity Sync 方案</h2>
      <p>核心思路：把 AI 对"你是谁"的认知，从客户端剥离出来，存储在一个独立的身份层中。任何 MCP 客户端连上这个身份层，都能加载同样的上下文。</p>

      <h3>架构原理</h3>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`┌─────────────────┐    ┌─────────────────┐
│  Mac + Hermes   │    │  Win + Claude   │
│  auto_provision │    │  auto_provision │
│       │         │    │       │         │
│       ▼         │    │       ▼         │
│  ┌───────────┐  │    │  ┌───────────┐  │
│  │ MCP Client│  │    │  │ MCP Client│  │
│  └─────┬─────┘  │    │  └─────┬─────┘  │
│        │        │    │        │        │
└────────┼────────┘    └────────┼────────┘
         │                     │
         ▼                     ▼
    ┌─────────────────────────────┐
    │     Moltable Identity Layer │
    │  ┌────────┐ ┌────────────┐  │
    │  │Profile │ │ Personas   │  │
    │  ├────────┤ ├────────────┤  │
    │  │Memories│ │Preferences │  │
    │  ├────────┤ ├────────────┤  │
    │  │Projects│ │Rules       │  │
    │  └────────┘ └────────────┘  │
    └─────────────────────────────┘`}
      </pre>

      <h2>实操步骤：十分钟完成跨设备同步</h2>

      <h3>1. 注册并获取 API Key</h3>
      <p>在 Moltable 注册后，你会得到一个 API Key（以 <code>molt_</code> 开头）。这个 Key 就是你的数字身份凭证。</p>

      <h3>2. 在旧电脑上保存偏好</h3>
      <p>在你的日常使用中，当 AI 做对了某件事，显式告诉它保存：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`"记住我偏好用 pnpm 而不是 npm"
"记住我的 TypeScript 项目默认 strict: true"
"记住我每周五下午做周报，模板用 FOST-Standard"`}
      </pre>
      <p>Moltable 会自动将这些偏好保存到 7 个分类中，并建立语义索引。</p>

      <h3>3. 在新电脑上配置 MCP 连接</h3>
      <p>无论你用的是 Hermes、Claude Desktop 还是 Cursor，配置方式都一样：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`{
  "mcpServers": {
    "moltable": {
      "command": "npx",
      "args": ["-y", "@moltable/mcp-server"],
      "env": {
        "MOLTABLE_API_KEY": "molt_your_key_here"
      }
    }
  }
}`}
      </pre>

      <h3>4. 首次连接：自动恢复</h3>
      <p>Agent 启动后会自动调用 <code>auto_provision</code>，加载你的完整上下文。你会发现：</p>
      <ul>
        <li>它在旧电脑上记住的代码风格偏好，新电脑上直接生效</li>
        <li>你的 Persona 配置自动同步（工作 Persona 和个人 Persona 各就各位）</li>
        <li>项目背景知识无需重新解释</li>
      </ul>

      <h3>5. 验证同步</h3>
      <p>在新电脑上问 Agent："你知道我的 Python 项目日志级别偏好是什么吗？" 如果它回答正确，说明 Identity Sync 成功。</p>

      <h2>跨平台实战：Mac → Windows → Linux</h2>
      <p>一个真实工作流：</p>
      <ol>
        <li><strong>办公室 Mac</strong>：用 Claude Desktop + Moltable，积累代码审查偏好</li>
        <li><strong>下班路上</strong>：用手机上的 ChatGPT（通过 MCP 代理连接 Moltable），继续讨论架构</li>
        <li><strong>回家 Windows 台式机</strong>：用 Hermes，自动加载白天积累的上下文</li>
        <li><strong>服务器 Linux</strong>：跑自动化 Agent，使用同一个 Moltable API Key</li>
      </ol>
      <p>四个设备，同一个数字身份。这不再是科幻。</p>

      <h2>高级技巧</h2>
      <ul>
        <li><strong>选择性同步</strong>：使用 Persona 过滤，让工作电脑只加载工作 Persona，家庭电脑只加载个人 Persona</li>
        <li><strong>差异备份</strong>：Moltable 支持按时间范围导出记忆，做增量备份</li>
        <li><strong>团队共享</strong>：项目 Persona 可以分享给团队，新成员加入后一键加载项目上下文</li>
      </ul>
      <p>相关阅读：<Link href="/blog/ai-data-sovereignty" className="text-ln-accent hover:underline">你的 10 万条 AI 对话记录：该归谁？该存在哪？</Link></p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable — 你的 AI 身份，跟着你走</Link></p>
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
