'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="AI 为什么总「失忆」？根因剖析与实操修复指南" date="2026-07-12">
      <p>情景你肯定不陌生：昨天花了半小时跟 Claude 调好了一个 Python 脚本的错误处理风格，今天打开新会话，它又用回默认风格了。你叹了口气，重新解释了一遍你的偏好——"用 try/except 包裹，错误信息用中文，日志级别用 WARNING"。</p>
      <p>这就是 AI「失忆」——Agent 在跨会话中无法保持用户偏好。本文剖析五个根因，并给出即插即用的修复方案。</p>

      <h2>五大根因</h2>

      <h3>1. LLM 天生无状态</h3>
      <p>这是一个设计选择，不是 bug。GPT、Claude、DeepSeek 都是无状态的——每次 API 调用都是一个独立的推理任务。模型的权重是固定的，它不"记得"任何历史。上下文窗口内的内容只是被编码为 token 输入，窗口一关闭，一切归零。</p>

      <h3>2. 会话上下文隔离</h3>
      <p>Claude Desktop 和 ChatGPT 的每个会话是独立沙箱。你可以在一个会话里教会 Agent 你的偏好，但这些偏好存储在客户端的对话历史中，不会传递到新会话。即使同一个平台，不同会话之间的 Agent 也是"陌生人"。</p>

      <h3>3. 缺少共享身份层</h3>
      <p>这是最根本的问题。你使用 Claude 写代码、用 ChatGPT 做研究、用 Hermes 管理日程——三个 Agent 各自独立，"你的偏好"被分散在三个孤岛中。没有一个统一的身份层来汇总和同步这些偏好。</p>

      <h3>4. 跨平台的记忆碎片化</h3>
      <p>即使某个平台有记忆功能（如 ChatGPT 的 Memory），它也只存在于那个平台。你在 ChatGPT 里告诉它的偏好，Claude 永远不知道。你给了 Claude 一个详细的项目背景，Cursor 的 Agent 对此一无所知。</p>

      <h3>5. 缺少自动配置（Auto-Provision）</h3>
      <p>即使你设置了记忆系统，Agent 每次启动时不知道应该加载什么。它需要你显式告诉它"去查我的偏好"。而人类助手不这样工作——一个好的助理会<strong>自动</strong>了解你的偏好，不需要你每次提醒。</p>

      <h2>修复方案：三步建立持久记忆</h2>

      <h3>第一步：搭建 MCP 记忆服务器</h3>
      <p>以 Moltable 为例，注册后在 Hermes 或 Claude 中配置 MCP 连接：</p>
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
      <p>重启 Agent 后，它就能调用 <code>search_memory</code> 和 <code>save_memory</code> 两个基础工具了。</p>

      <h3>第二步：启用自动配置（auto_provision）</h3>
      <p>这在 Moltable 中是一个关键的 MCP 工具：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`// Agent 启动时自动调用
const context = await moltable.auto_provision()
// 返回：用户画像、行为规则、可用Persona、活跃项目、核心知识
console.log(context.profile.rules)
// ["代码审查时总是用中文注释", "错误处理用try/except", ...]`}
      </pre>
      <p><code>auto_provision</code> 相当于"一键恢复"——Agent 启动时自动加载你的完整上下文，就像人类助理上班后先翻阅你的工作手册。</p>

      <h3>第三步：养成良好的记忆保存习惯</h3>
      <p>当你发现 Agent 做对了一件事，显式告诉它保存：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`// 每次做对就保存
"记住：我的 Python 项目日志级别默认用 WARNING"
→ Agent 调用 save_memory({
    content: "用户 Python 项目日志级别默认用 WARNING",
    category: "preference",
    tags: ["python", "logging"]
  })`}
      </pre>
      <p>关键原则：<strong>做对就保存，做错就纠正</strong>。不要让 Agent 自己去判断什么该记——人类助理也不会随便帮你记录无关紧要的细节。</p>

      <h2>对比：修复前 vs 修复后</h2>
      <ul>
        <li><strong>修复前</strong>：每次新会话 → Agent 从头开始 → 你重复偏好 → 浪费 5-10 分钟</li>
        <li><strong>修复后</strong>：新会话 → auto_provision 加载上下文 → Agent 直接按你的偏好工作 → 零摩擦</li>
      </ul>
      <p>一个真实案例：FOST 集团的 CEO 每天用 Agent 处理 10+ 个任务，修复前平均每天浪费 30 分钟在"重新教会 Agent"。接入 Moltable 的 auto_provision 后，这个时间降为零。按一年 250 个工作日计算，节省了 125 小时——相当于三个工作周。</p>

      <h2>进阶技巧</h2>
      <ul>
        <li><strong>Persona 隔离</strong>：工作和个人偏好分开存储。工作 Persona 加载代码规范，个人 Persona 加载旅行偏好。互不干扰。</li>
        <li><strong>记忆分类</strong>：Moltable 的 7 种分类（preference/decision/fact/project/insight/task/relationship）让检索更精准。</li>
        <li><strong>定期审查</strong>：每季度清理一次过时记忆——你 2024 年的 Python 版本偏好可能已经不适用了。</li>
      </ul>
      <p>AI 失忆不是技术问题，是架构问题。一旦你有了身份层，Agent 就不再是金鱼。</p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">开始使用 Moltable — 让 AI 永远记住你是谁</Link></p>
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
