'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="开源协议如何重塑 AI 生态：MCP、A2A 与 Identity 层的三角博弈" date="2026-08-05">
      <p>2024 年 11 月，Anthropic 发布了 MCP。2025 年 4 月，Google 发布了 A2A。两个协议，两个公司，两套哲学——但目标一致：让 AI Agent 能连接更大的世界。</p>
      <p>到了 2026 年中，这场博弈有了第三个变量：<strong>Identity 层</strong>。它不属于任何大公司，但可能成为连接 MCP 和 A2A 的桥梁。</p>

      <h2>MCP：Agent-to-Tool 的标准</h2>
      <p>MCP（Model Context Protocol）在 2025 年 5 月被 Linux 基金会接纳，从 Anthropic 的"公司项目"变成了"社区标准"。目前 25K+ GitHub Stars，生态中有超过 500 个 MCP Server。</p>
      <p>核心设计哲学：</p>
      <ul>
        <li><strong>极简主义</strong>：只有三个核心概念（Tools、Resources、Prompts）</li>
        <li><strong>工具优先</strong>：MCP 的场景是 Agent 调用工具，不是 Agent 之间聊天</li>
        <li><strong>JSON-RPC 2.0</strong>：成熟的传输协议，无需重新造轮子</li>
        <li><strong>Stdio + SSE</strong>：本地和远程两种传输模式，覆盖所有场景</li>
      </ul>
      <p>支持 MCP 的客户端越来越多了：Claude Desktop、Hermes、Cursor、Zed、Continue.dev、Gemini CLI……MCP 正在成为 AI 工具调用的"事实标准"。</p>

      <h2>A2A：Agent-to-Agent 的蓝图</h2>
      <p>Google 的 Agent-to-Agent (A2A) 协议走的是另一条路。它的场景是：多个 AI Agent 之间互相通信、协作、委托任务。比如：</p>
      <ul>
        <li>你让一个"研究 Agent"去调研竞争对手</li>
        <li>研究 Agent 发现需要市场数据 → 委托"数据分析 Agent"</li>
        <li>数据分析 Agent 发现需要可视化 → 委托"图表 Agent"</li>
        <li>最终结果由研究 Agent 汇总后呈现给你</li>
      </ul>
      <p>A2A 的关键设计：</p>
      <ul>
        <li><strong>Agent Card</strong>：每个 Agent 有一个 JSON 描述文件（能力、端点、认证方式）</li>
        <li><strong>Task 模型</strong>：长任务异步执行，支持状态查询和结果回调</li>
        <li><strong>多模态</strong>：支持文本、图片、音视频传递</li>
      </ul>

      <h2>MCP vs A2A：不是竞争，是互补</h2>
      <p>很多人把两者对立起来，但实际场景中它们是互补的：</p>
      <ul>
        <li><strong>MCP</strong>：Agent → 工具。类似 API 调用。</li>
        <li><strong>A2A</strong>：Agent → Agent。类似微服务通信。</li>
      </ul>
      <p>一个完整的 AI 系统会同时使用两者：用 MCP 调用工具（搜索记忆、查询数据库、发送邮件），用 A2A 协调多个 Agent（分工、委托、汇总）。</p>

      <h2>缺失的一环：Identity 层</h2>
      <p>但这里有一个问题：当 Agent 通过 MCP 调用工具、通过 A2A 委托其他 Agent 时，<strong>它以什么身份操作</strong>？</p>
      <p>如果没有统一的身份层：</p>
      <ul>
        <li>Agent A 通过 MCP 调用搜索工具 → 用的是"匿名用户"的权限</li>
        <li>Agent B 通过 A2A 接收任务 → 不知道委托人是谁、有什么偏好、有什么限制</li>
        <li>两个 Agent 看到同一份数据 → 因为没有 Persona，给出雷同的分析</li>
      </ul>
      <p>Identity 层填补了这个空白：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`┌──────────────────────────────────────────┐
│              Identity Layer               │
│   ┌────────┐ ┌──────────┐ ┌───────────┐  │
│   │Profile │ │Personas  │ │ Memories  │  │
│   │(我是谁)│ │(我的视角)│ │(我知道什么)│  │
│   └────────┘ └──────────┘ └───────────┘  │
│                    │                      │
│          ┌─────────┴─────────┐            │
│          ▼                   ▼            │
│   ┌────────────┐    ┌────────────┐        │
│   │ MCP Tools  │    │ A2A Agents │        │
│   │ (调什么工具)│    │ (委托谁)    │        │
│   └────────────┘    └────────────┘        │
│          │                   │            │
│          └─────────┬─────────┘            │
│                    ▼                      │
│         一致的行为、一致的权限、一致的记忆   │
└──────────────────────────────────────────┘`}
      </pre>

      <h2>Moltable 的赌注：Identity as Protocol</h2>
      <p>Moltable 的核心赌注是：<strong>在 MCP + A2A 的生态中，Identity 层会成为第三个基础协议</strong>。理由：</p>
      <ol>
        <li><strong>MCP 解决了"能做什么"</strong>（Capabilities），但没有解决"以什么身份做"</li>
        <li><strong>A2A 解决了"怎么协作"</strong>（Coordination），但没有解决"协作时需要知道什么上下文"</li>
        <li><strong>Identity 解决"我是谁"</strong>（Who am I）和"我应该怎么做"（How should I behave）</li>
      </ol>
      <p>这三者构成了 AI Agent 的完整三角：</p>
      <ul>
        <li>MCP = Agent 的手（Tools）</li>
        <li>A2A = Agent 的嘴（Communication）</li>
        <li>Identity = Agent 的脑（Personality + Memory）</li>
      </ul>

      <h2>未来猜想：MCP + A2A + Identity 的融合</h2>
      <p>展望 2027 年，我预测会出现以下融合趋势：</p>
      <ul>
        <li>MCP 的 <code>tools/call</code> 中会增加 <code>identity_id</code> 参数，让工具调用带上身份上下文</li>
        <li>A2A 的 Agent Card 中会增加 <code>identity_provider</code> 字段，指向 Moltable 等身份服务</li>
        <li>身份层的 <code>auto_provision</code> 会成为 Agent 启动的标准初始化步骤</li>
        <li>出现"MCP Identity Server"标准——让身份层以 MCP 协议本身的方式提供</li>
      </ul>
      <p>开源协议的竞争不是零和博弈。MCP 不会杀死 A2A，A2A 也不会取代 MCP。真正有价值的问题是：当 Agent 有了手（MCP）和嘴（A2A），谁来给它一个大脑和记忆？</p>
      <p>相关阅读：<Link href="/blog/mcp-ai-usb-c" className="text-ln-accent hover:underline">MCP 协议：为什么它是 AI 的 USB-C</Link> · <Link href="/blog/ai-agent-trends-2026h2" className="text-ln-accent hover:underline">2026 下半年 AI Agent 趋势</Link></p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable — AI Identity Protocol</Link></p>
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
