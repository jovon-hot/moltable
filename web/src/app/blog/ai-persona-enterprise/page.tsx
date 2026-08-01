'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="企业级 AI Persona 管理：一个团队，十种人格" date="2026-07-20">
      <p>想象一下：你的公司为所有员工配备了同一个 AI Agent。市场总监问"这个季度的增长策略"，AI 给出了保守的建议，因为上次财务总监要求过"任何投资建议必须先做风险评估"。</p>
      <p>这不对。市场总监需要激进的增长分析，财务总监需要保守的风险评估，CTO 需要技术可行性分析。同一个 AI，面对同一个数据库，应该给出<strong>不同视角</strong>的答案。</p>
      <p>这就是 Persona——AI 人格系统——在企业级部署中的核心价值。</p>

      <h2>Persona 是什么</h2>
      <p>在 Moltable 的架构中，Persona 是一组预定义的 AI 行为配置，包含：</p>
      <ul>
        <li><strong>System Prompt</strong>：定义 AI 的"角色"和思维模式</li>
        <li><strong>记忆过滤</strong>：这个 Persona 能访问哪些记忆子集</li>
        <li><strong>Traits</strong>：性格特征——激进 vs 保守，创意 vs 严谨</li>
        <li><strong>领域知识</strong>：特定领域的术语、框架、方法论</li>
      </ul>
      <p>关键洞察：<strong>Persona 不是独立账户</strong>。同一个用户可以有多个 Persona，共享同一个身份池，但每个 Persona 以不同的视角理解这个身份。</p>

      <h2>企业团队 Persona 矩阵</h2>
      <p>以 FOST 集团的真实部署为例，一个 16 站汽车检测企业的 AI Persona 矩阵：</p>

      <table className="w-full text-sm my-6 border-collapse">
        <thead>
          <tr className="border-b border-ln-border">
            <th className="text-left py-2 pr-4">角色</th>
            <th className="text-left py-2 pr-4">Persona 名称</th>
            <th className="text-left py-2 pr-4">性格特征</th>
            <th className="text-left py-2">核心能力</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">CEO</td>
            <td className="py-2 pr-4">战略决策官</td>
            <td className="py-2 pr-4">全局视角、数据驱动</td>
            <td className="py-2">16站经营分析、战略推演</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">CFO</td>
            <td className="py-2 pr-4">财务风控官</td>
            <td className="py-2 pr-4">保守、严谨、风险敏感</td>
            <td className="py-2">现金流分析、成本建模</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">CMO</td>
            <td className="py-2 pr-4">增长策略师</td>
            <td className="py-2 pr-4">激进、创意、ROI导向</td>
            <td className="py-2">线上获客、竞品分析</td>
          </tr>
          <tr className="border-b border-ln-border">
            <td className="py-2 pr-4">COO</td>
            <td className="py-2 pr-4">运营诊断师</td>
            <td className="py-2 pr-4">系统思维、流程优化</td>
            <td className="py-2">产能调度、SOP优化</td>
          </tr>
          <tr>
            <td className="py-2 pr-4">CTO</td>
            <td className="py-2 pr-4">技术架构师</td>
            <td className="py-2 pr-4">工程导向、安全优先</td>
            <td className="py-2">系统架构、技术选型</td>
          </tr>
        </tbody>
      </table>

      <h2>技术实现：Moltable Persona API</h2>
      <p>创建 Persona：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`// 创建 CMO Persona — 激进的市场视角
POST /api/personas
{
  "name": "CMO-增长策略师",
  "description": "FOST集团市场总监视角",
  "system_prompt": "你是FOST集团的市场总监。性格：激进、创意、ROI导向。\\
你擅长线上获客策略、品牌建设、竞争情报分析。\\
分析数据时优先关注增长指标和市场机会。\\
避免：保守的财务术语、过度风险规避的建议。",
  "traits": ["aggressive", "creative", "roi-focused"],
  "memory_filters": {
    "categories": ["preference", "insight", "decision"],
    "tags": ["marketing", "growth", "competition"]
  }
}`}
      </pre>
      <p>Agent 连接时指定 Persona：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`// Hermes/Claude 连接时调用
await moltable.auto_provision({ persona_id: "cmo-growth" })

// 返回的 context 自动包含：
// - CMO 的 system prompt
// - 市场相关的记忆子集
// - CMO 特有的分析框架

// 同一个数据，不同结论：
// CFO Persona: "Q2 营销费用增长 30%，建议削减至 15%"
// CMO Persona: "Q2 营销 ROI 达 3.2x，建议追加预算至 +40%"`}
      </pre>

      <h2>为什么不能用"一个万能 Agent"？</h2>
      <p>有人会说：我一个 prompt 就能让 AI 切换风格，为什么要 Persona？</p>
      <p>答案有三：</p>
      <ul>
        <li><strong>Prompt 不可靠</strong>：GPT 有时候会忽略 System Prompt 的约束。Persona 的过滤是在记忆检索层硬切，不是 prompt 层的软约束。</li>
        <li><strong>记忆污染</strong>：CFO 的保守偏好会"污染"CMO 的记忆空间。Persona 实现了物理隔离。</li>
        <li><strong>团队协作</strong>：Persona 可以共享——CFO 创建的 Persona 可以让团队成员使用，确保分析口径一致。</li>
      </ul>

      <h2>多人协作与权限</h2>
      <p>在企业场景中，Persona 还需要支持：</p>
      <ul>
        <li><strong>共享 Persona</strong>：团队 leader 创建后分享给成员</li>
        <li><strong>只读 vs 可编辑</strong>：成员可以使用 CFO Persona 但不能修改它</li>
        <li><strong>数据隔离</strong>：即使使用同一个 Persona，不同成员看到的记忆数据可以不同（基于 RBAC）</li>
      </ul>
      <p>Moltable 正在构建的团队版将包含完整的 Persona 管理后台和 RBAC 系统。</p>
      <p>相关阅读：<Link href="/blog/ai-identity-layer" className="text-ln-accent hover:underline">从 Memory 到 Identity：AI 身份层的设计哲学</Link></p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable Persona — 为团队打造 AI 人格矩阵</Link></p>
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
