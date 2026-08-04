'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="arXiv 最新论文：AI Agent 的「持续身份」——多锚点架构如何让 Agent 不再失忆" date="2026-08-04">
      <p>2026年3月，一篇发表在 arXiv 上的论文引发了 AI Agent 社区的热议：<strong>《Persistent Identity in AI Agents: A Multi-Anchor Architecture》</strong>（arXiv 2604.09588）。</p>
      <p>这篇论文提出了一个核心洞察：<strong>人类能在严重记忆损伤后仍然保持身份认同，因为身份不是存储在大脑的某一个区域，而是分布式地锚定在多个系统中</strong>——偏好、价值观、决策模式、人际关系、自我叙事。</p>
      <p>这个来自神经科学的启发，正在重塑 AI Agent 记忆系统的设计方向。而 Moltable 的 Identity→Persona→Agent 三层架构，恰好与论文提出的多锚点理论不谋而合。</p>

      <h2>论文核心发现：五个身份锚点</h2>
      <p>论文通过分析人类记忆障碍的神经科学案例（如 Clive Wearing、HM 患者），提炼出维持身份认同的五个关键锚点：</p>

      <h3>锚点一：偏好锚定（Preference Anchoring）</h3>
      <p>即使失忆患者不记得过去的经历，他们仍然知道自己喜欢什么音乐、讨厌什么食物。这些偏好深植于基底神经节，独立于海马体的情景记忆系统。</p>
      <p><strong>对 AI Agent 的启示</strong>：偏好应该是记忆系统中最基础的存储单元，不依赖上下文窗口。你的 Agent 应该"天生"知道你用 TypeScript 而非 Python，用 tabs 而非 spaces——这些不需要每次重新声明。</p>

      <h3>锚点二：决策轨迹（Decision History）</h3>
      <p>身份不仅取决于"你是谁"，还取决于"你做过什么选择"。失忆患者虽然忘了事件本身，但保留了做决定的<strong>模式</strong>。</p>
      <p><strong>对 AI Agent 的启示</strong>：Agent 应该记录用户的决策历史，并从中提取决策模式。例如："用户在过去 10 次技术选型中 8 次选择了 Railway 部署"。</p>

      <h3>锚点三：关系网络（Relational Mapping）</h3>
      <p>人类身份很大程度上由社会关系定义——你是某人的父母、同事、朋友。这些关系网络即使在情景记忆受损后也能保留。</p>
      <p><strong>对 AI Agent 的启示</strong>：Agent 应该维护一个项目关系图——哪些文件属于哪个项目、哪些 API Key 对应哪个服务、哪些 Persona 用于什么场景。</p>

      <h3>锚点四：价值观编码（Value Encoding）</h3>
      <p>价值观是最稳定的身份锚点。论文指出，即使在严重痴呆症患者中，核心价值观（如诚实、家庭优先）仍然可以通过行为观察到。</p>
      <p><strong>对 AI Agent 的启示</strong>：Agent 应该从用户的反馈中提取行为规则。例如："用户总是要求在代码审查中优先指出安全问题"→ 这是一条高优先级的行为规则。</p>

      <h3>锚点五：叙事连续性（Narrative Continuity）</h3>
      <p>人类通过讲述关于自己的故事来维持身份。这些故事提供了时间上的连续性——"我是谁"依赖于"我曾经是谁"的故事。</p>
      <p><strong>对 AI Agent 的启示</strong>：Agent 应该维护一个项目时间线——关键决策、重要里程碑、技术债务的来历。这不仅是记忆，更是可以传递给新 Agent 的知识遗产。</p>

      <h2>Moltable 如何实现多锚点架构</h2>
      <p>论文的理论很美，但实现起来需要工程架构。Moltable 的 Identity 层恰好映射了这五个锚点：</p>

      <table className="w-full text-xs my-6 border-collapse">
        <thead>
          <tr style={{ background: 'rgba(113,112,255,0.12)' }}>
            <th className="p-3 text-left font-medium">论文锚点</th>
            <th className="p-3 text-left font-medium">Moltable 实现</th>
            <th className="p-3 text-left font-medium">对应工具</th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">偏好锚定</td>
            <td className="p-3">User Preferences Store (7 种分类)</td>
            <td className="p-3"><code>save_memory</code> → <code>search_memory</code></td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">决策轨迹</td>
            <td className="p-3">Decision Log + Pattern Extraction</td>
            <td className="p-3"><code>auto_provision</code> 的 rules 字段</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">关系网络</td>
            <td className="p-3">Project Environment Map</td>
            <td className="p-3"><code>knowledge_bases</code> + <code>tools</code></td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">价值观编码</td>
            <td className="p-3">Behavior Rules (Persona 级)</td>
            <td className="p-3">Persona 的 <code>rules</code> 字段</td>
          </tr>
          <tr>
            <td className="p-3">叙事连续性</td>
            <td className="p-3">Project Timeline + Agent Memory</td>
            <td className="p-3"><code>auto_provision</code> 的 context 字段</td>
          </tr>
        </tbody>
      </table>

      <h2>实战：用五个锚点武装你的 Agent</h2>
      <p>以下是一个完整的配置示例，展示如何通过 Moltable 的 MCP 工具实现多锚点身份：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`// Agent 启动时，auto_provision 返回的完整上下文
const identity = await moltable.auto_provision()

// 锚点1: 偏好
console.log(identity.profile.preferences)
// { language: "TypeScript", deploy: "Railway", 
//   indent: "tabs", test_framework: "vitest" }

// 锚点2: 决策轨迹
console.log(identity.profile.rules)
// ["代码审查时优先报告安全问题",
//  "新项目默认使用 Railway + PostgreSQL",
//  "日志级别默认 WARNING，生产环境 ERROR"]

// 锚点3: 关系网络
console.log(identity.knowledge_bases)
// [{ name: "myapp", type: "project",
//    tools: ["railway-deploy", "prisma-migrate"] },
//  { name: "blog", type: "project",
//    tools: ["vercel-deploy", "mdx-build"] }]

// 锚点4: 价值观编码
console.log(identity.active_persona.rules)
// ["用中文回复技术问题",
//  "代码建议要包含错误处理",
//  "架构决策给出 trade-off 分析"]

// 锚点5: 叙事连续性
console.log(identity.context)
// "用户正在开发一个 Next.js + Prisma 的全栈应用。
//  上周完成了用户认证模块，本周计划实现权限系统。
//  之前踩过的坑：Prisma migration 在 Railway 上需要
//  设置 DATABASE_URL 环境变量。"`}
      </pre>

      <h2>为什么这个研究方向很重要</h2>
      <p>2026年，AI Agent 赛道正在从"能做多少事"转向"能记多少东西"。mem0 从记忆切入拿下了 62K GitHub Stars，但记忆只是身份的一个子集。</p>
      <p>论文作者的核心论点是：<strong>记忆不等于身份，身份需要通过多个锚点来维持</strong>。这意味着，仅仅给 Agent 加一个向量数据库是不够的——你需要一个完整的身份基础设施。</p>
      <p>Moltable 从第一天起就按照这个理念设计。不是"更好的记忆"，而是"完整的身份"——跨越 Agent、平台、设备的持续自我认知。</p>

      <blockquote className="border-l-2 border-ln-accent pl-4 my-6 text-sm text-ln-secondary italic">
        "Identity is not stored in a single location. It is distributed across preferences, values, decisions, relationships, and the stories we tell about ourselves."<br/>
        — Persistent Identity in AI Agents, arXiv 2604.09588 (2026)
      </blockquote>

      <p>👉 <Link href="/register" className="text-ln-accent hover:underline">免费体验 Moltable — 给你的 AI Agent 一个不会丢失的身份</Link></p>
      <p className="text-xs text-ln-tertiary mt-6">
        参考文献：Persistent Identity in AI Agents: A Multi-Anchor Architecture (arXiv 2604.09588, March 2026)
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
