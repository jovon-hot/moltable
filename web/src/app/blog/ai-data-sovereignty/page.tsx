'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="你的 10 万条 AI 对话记录：该归谁？该存在哪？" date="2026-07-18">
      <p>打开你的 ChatGPT 历史。往下翻。再往下翻。你会发现你已经和 AI 进行了数千甚至上万轮对话。这些对话里包含你的代码偏好、项目背景、商业决策逻辑、个人价值观——简而言之，你的<strong>数字人格</strong>。</p>
      <p>一个扎心的问题：这些数据归谁？OpenAI 的 ToS 说它们可以用来训练模型。你同意了，但你还有别的选择吗？2026 年，数据主权（Data Sovereignty）在 AI 时代有了全新的含义。</p>

      <h2>AI 对话数据的三种所有权模型</h2>

      <h3>模型一：平台所有（Platform-Owned）</h3>
      <p>ChatGPT、Gemini 等主流平台默认采用这一模型。你的对话数据存储在平台的服务器上，平台拥有使用权。OpenAI 的隐私政策允许使用非 API 用户的对话来改进模型——虽然你可以 opt-out，但默认是 opt-in。</p>
      <p><strong>优势</strong>：零运维，体验极致。你在任何设备登录都能看到历史。</p>
      <p><strong>劣势</strong>：你只有使用权，没有所有权。数据不能迁移。平台可以随时改变政策。如果平台倒闭，数据消失。</p>

      <h3>模型二：本地自托管（Self-Hosted）</h3>
      <p>用 Ollama + Open WebUI 跑本地模型。所有数据在你的硬盘上，物理隔离。</p>
      <p><strong>优势</strong>：绝对隐私。数据物理上不外传。</p>
      <p><strong>劣势</strong>：本地模型的推理能力和 SOTA 云端模型差距仍然明显。你需要自建记忆系统、向量数据库、备份方案。运维成本不低。</p>

      <h3>模型三：联邦身份（Federated Identity）</h3>
      <p>数据存在你选择的地方（自托管或可信第三方），通过标准协议让不同的 AI 客户端访问。这是 Moltable 采用的模型——用户拥有数据，平台提供服务。</p>
      <p><strong>优势</strong>：数据可迁移、可删除、可加密。同时享受云端模型的强大能力。</p>
      <p><strong>劣势</strong>：需要信任第三方。目前尚属新兴模式，生态还在建设中。</p>

      <h2>法律框架：GDPR 与《个人信息保护法》</h2>
      <p>如果你在中国市场使用 AI 工具，2021 年生效的《个人信息保护法》（PIPL）赋予你：</p>
      <ul>
        <li><strong>知情权</strong>：平台必须告知数据用途</li>
        <li><strong>决定权</strong>：你可以限制或拒绝数据处理</li>
        <li><strong>查阅复制权</strong>：你可以要求查看和导出你的数据</li>
        <li><strong>删除权</strong>：你可以要求删除数据</li>
        <li><strong>数据可携带权</strong>：你可以将数据迁移到其他平台</li>
      </ul>
      <p>欧盟的 GDPR 提供了类似甚至更强的保护。但现实是：大多数 AI 平台并没有提供便捷的数据可携带性工具。导出 ChatGPT 对话需要填表申请，导出结果是一个难以解析的 JSON 文件。</p>

      <h2>Moltable 的数据主权方案</h2>
      <p>Moltable 从设计上遵循"用户拥有数据"原则：</p>
      <ul>
        <li><strong>加密存储</strong>：密码使用 scrypt 哈希（OWASP 推荐），敏感数据加密存储</li>
        <li><strong>数据可迁移</strong>：所有记忆支持 API 导出，标准 JSON 格式</li>
        <li><strong>删除权</strong>：一键删除账户，所有关联数据物理清除</li>
        <li><strong>身份可迁移</strong>：你的身份不与 Moltable 绑定——API Key 可以接入任何 MCP 客户端</li>
        <li><strong>最小权限</strong>：API Key 有前缀区分（molt_ vs mol_），不同前缀对应不同权限级别</li>
      </ul>

      <h2>实践建议</h2>
      <p>无论你选择哪个平台，以下三条建议值得采纳：</p>
      <ol>
        <li><strong>定期导出你的 AI 对话</strong>：即使是手动导出也值得做。数据是你的数字资产。</li>
        <li><strong>敏感信息不要输入</strong>：API Key、密码、商业机密——AI 对话不是堡垒。</li>
        <li><strong>使用身份层分离关注</strong>：把"偏好"存储在身份层，而不是某一个 AI 平台。这样你换平台时偏好跟着走。</li>
      </ol>
      <p>数据主权不是一个技术问题，是一个意识问题。2026 年，你的 AI 对话记录比我手机上所有的照片加起来还多。这些数据值得被认真对待。</p>
      <p>相关阅读：<Link href="/blog/ai-forgetfulness-fix" className="text-ln-accent hover:underline">AI 为什么总「失忆」？</Link> · <Link href="/blog/ai-identity-sync-guide" className="text-ln-accent hover:underline">换电脑不换记忆：AI 身份同步完全指南</Link></p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable — 你的数据，你的身份</Link></p>
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
