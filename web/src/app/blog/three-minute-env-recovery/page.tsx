'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南" date="2026-08-04">
      <p><strong>你换了一台新 Mac。系统迁移很顺利——文件、应用、设置全过来了。你打开 Claude Desktop，准备继续昨天没调完的 bug。</strong></p>
      <p><strong>Claude 说："Hello! How can I help you today?"</strong></p>
      <p>它不记得你了。</p>
      <p>这不是软件 bug，这是 AI Agent 行业最大的体验断层：<strong>每一台新设备，都是一次身份重置。</strong></p>
      <p>Moltable 的目标就是消除这个断层。本文是一个完整实战指南：从安装到恢复，从单机到多 Agent 同步，一步不落。</p>

      <h2>先看效果：3 分钟恢复了什么？</h2>
      <p>用 Moltable 做完一次同步后，你换到任何新电脑，以下内容全部就位：</p>

      <table className="w-full text-xs my-6 border-collapse">
        <thead>
          <tr style={{ background: 'rgba(113,112,255,0.12)' }}>
            <th className="p-3 text-left font-medium">恢复项</th>
            <th className="p-3 text-left font-medium">具体内容</th>
            <th className="p-3 text-left font-medium">无 Moltable 的替代方案</th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">Persona</td>
            <td className="p-3">代码审查员/战略顾问/写作教练等自定义人格</td>
            <td className="p-3">手动重写 prompt，每个 Agent 各写一遍</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">偏好记忆</td>
            <td className="p-3">"TypeScript、tab 缩进、部署到 Railway"</td>
            <td className="p-3">每次对话重新陈述</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">项目上下文</td>
            <td className="p-3">项目路径、技术栈、关键决策记录</td>
            <td className="p-3">新会话里一点点"教"</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">MCP 配置</td>
            <td className="p-3">所有 MCP Server 的 URL + API Key</td>
            <td className="p-3">逐个手动配置 JSON</td>
          </tr>
          <tr>
            <td className="p-3">工具偏好</td>
            <td className="p-3">常用工具列表、搜索习惯</td>
            <td className="p-3">Agent 随机选择，效率减半</td>
          </tr>
        </tbody>
      </table>

      <h2>第一步：注册并获取 API Key</h2>
      <p>去 <Link href="/register" className="text-ln-accent hover:underline">moltable.ai/register</Link> 注册，30 秒完成。你会得到一个 <code>molt_</code> 开头的 API Key。</p>
      <p><strong>Free 套餐就够用</strong>——100 条记忆、2 个 Persona、1 个主机发现。日常开发完全覆盖。</p>

      <h2>第二步：在第一台电脑上"播种"</h2>
      <p>在你现有的主力机上，用 Claude Desktop 给 Moltable "喂"一遍你的偏好：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`你：帮我记录我的开发偏好。

Claude 调用 moltable 工具...

记录完成：
✅ 语言偏好：TypeScript > Python > Go
✅ 代码风格：Prettier 默认配置、tab 缩进
✅ 部署目标：Railway（主）、Vercel（前端）
✅ 项目路径：~/work/my-saas/
✅ 技术栈：Next.js 14 + Prisma + PostgreSQL + Redis`}
      </pre>

      <p>这些记忆会永久存储在 Moltable 的向量数据库中，跨设备、跨 Agent 同步。</p>

      <h2>第三步：在新电脑上一键恢复</h2>
      <p>换到新 Mac 之后，你只需要一行命令：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# 一条命令接入 Claude Desktop
npx @moltable/connect claude --api-key molt_k7xq9p2v_xxxxx`}
      </pre>

      <p>这条命令自动完成：读取现有配置 → 备份原配置 → 写入 Moltable Server → 验证 API Key → 打印指引。<strong>不需要手动编辑任何 JSON。</strong></p>

      <p>同样适配其他 Agent：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`npx @moltable/connect cursor --api-key <your-key>
npx @moltable/connect hermes --api-key <your-key>`}
      </pre>

      <h2>第四步：验证恢复效果</h2>
      <p>接入后，打开 Claude Desktop，试试这些对话：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`你：我现在是什么技术栈？

Claude（通过 Moltable）：
根据你的偏好记录：
- 语言：TypeScript（主要）、Python、Go
- 框架：Next.js 14 + Prisma
- 数据库：PostgreSQL（Supabase）
- 部署：Railway + Vercel`}
      </pre>

      <h2>原理：Moltable 的身份三层架构</h2>
      <p>为什么 3 分钟能恢复这么多东西？因为 Moltable 不存对话，存的是<strong>结构化身份数据</strong>：</p>

      <div className="space-y-3 my-4">
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Identity Layer（你是谁）</h3>
          <p className="text-sm text-ln-secondary">email、设备指纹、API Key 绑定</p>
        </div>
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Persona Layer（你怎么想）</h3>
          <p className="text-sm text-ln-secondary">角色特征、回答风格、模型偏好</p>
        </div>
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Memory Layer（你知道什么）</h3>
          <p className="text-sm text-ln-secondary">偏好、项目上下文、工具配置</p>
        </div>
      </div>

      <p>换设备时，Agent 通过 MCP 协议调用 <code>auto_provision</code> 工具，一次性拉取三层数据。这就是"3 分钟"的来源——不是魔法，是协议设计。</p>

      <h2>进阶：跨 Agent 同步</h2>
      <p>Moltable 的真正威力在于<strong>一次配置，所有 Agent 共享</strong>。</p>
      <p>场景：你用 Claude 做架构设计、Cursor 写代码、Codex 做 code review。</p>
      <p><strong>有 Moltable</strong>：Claude 建议 Redis Streams 架构 → 写入记忆 → Cursor 自动读取并生成代码 → Codex 按架构规范审查。<strong>三个 Agent，一个大脑。</strong></p>

      <h2>常见问题</h2>
      <h3>Q: 我的 API Key 安全吗？</h3>
      <p>Moltable 使用端到端加密。API Key 存储用 PBKDF2-HMAC-SHA256 加盐哈希（10 万次迭代），敏感配置加密后落盘。</p>

      <h3>Q: 能自托管吗？</h3>
      <p>能。Moltable 是 MIT 开源协议。Clone 仓库 → pip install → python main.py，3 条命令跑起来。</p>

      <h3>Q: 免费版够用吗？</h3>
      <p>对于个人开发者，Free 套餐（100 条记忆、2 个 Persona）足够日常开发。跨项目、团队协作需要 Pro（¥19/月，10,000 条记忆）。</p>

      <h2>即刻开始</h2>
      <p>换电脑是必然的。让 AI 失忆，不是必然的。</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# 30 秒注册
open https://moltable.ai/register

# 60 秒接入 Claude Desktop
npx @moltable/connect claude --api-key <your-key>

# 3 分钟恢复全部 AI 环境
# 然后继续写代码，就像什么都没发生一样。`}
      </pre>

      <p>👉 <Link href="/register" className="text-ln-accent hover:underline">免费注册 Moltable — 让你的 AI 永远认识你</Link></p>
      <p className="text-xs text-ln-tertiary mt-6">
        GitHub: <a href="https://github.com/jovon-hot/moltable" className="text-ln-accent hover:underline">jovon-hot/moltable</a> · MIT License
      </p>
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
