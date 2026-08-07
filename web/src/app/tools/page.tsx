import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Tools — Moltable',
  description: 'Open-source tools for AI agents and knowledge management — deploy your personal knowledge base in one command.',
  alternates: { canonical: 'https://www.moltable.ai/tools' },
}

const tools = [
  {
    name: 'ailib Knowledge Base',
    description:
      '一键部署个人AI知识库。结构化目录 + x-core操作系统 + 证据驱动认知流水线。AI 在对话中自动提取你的思维模式、标记候选、碎片化验证后吸收为个人操作系统。',
    features: [
      '10 个标准目录：原始资料 → 实体 → 情报 → 报告 → 认知层 → 操作系统',
      'x-core：存储内化的原则、框架、决策模式和身份锚点',
      '认知流水线：提取 → 证据驱动候选 → 碎片化验证 → 闭环激活',
      '三条铁律：用过 · 记得 · 复用',
    ],
    github: 'https://github.com/Moltable/moltable/tree/main/tools/ailib-knowledge-base',
    download: 'https://raw.githubusercontent.com/Moltable/moltable/main/tools/ailib-knowledge-base/SKILL.md',
    install: '放到 ~/.hermes/skills/ailib-knowledge-base/SKILL.md，对 Hermes 说"建知识库"',
  },
]

export default function ToolsPage() {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-28 pb-20">
        {/* Header */}
        <div className="mb-12">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-ln-tertiary hover:text-ln-secondary transition-colors mb-6"
          >
            ← Moltable
          </Link>
          <h1 className="text-4xl font-heading tracking-[-0.4px] mb-3">Tools</h1>
          <p className="text-ln-secondary text-sm">
            Open-source tools for AI agents and knowledge management. Deploy in one command.
          </p>
        </div>

        {/* Tools List */}
        <div className="space-y-8">
          {tools.map((tool) => (
            <div
              key={tool.name}
              className="rounded-2xl border border-ln-border p-6 hover:border-ln-accent/30 transition-colors"
            >
              <h2 className="text-xl font-heading tracking-[-0.3px] mb-2">{tool.name}</h2>
              <p className="text-ln-secondary text-sm mb-4">{tool.description}</p>

              {/* Features */}
              <ul className="space-y-1.5 mb-5">
                {tool.features.map((f) => (
                  <li key={f} className="text-xs text-ln-tertiary flex items-start gap-2">
                    <span className="text-ln-accent mt-0.5 shrink-0">▸</span>
                    {f}
                  </li>
                ))}
              </ul>

              {/* Install */}
              <div className="bg-ln-surface rounded-lg p-3 mb-4">
                <p className="text-xs text-ln-tertiary mb-1">Install</p>
                <code className="text-xs text-ln-secondary font-mono break-all">
                  {tool.install}
                </code>
              </div>

              {/* Links */}
              <div className="flex items-center gap-4">
                <a
                  href={tool.github}
                  className="text-xs text-ln-accent hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub →
                </a>
                <a
                  href={tool.download}
                  className="text-xs text-ln-accent hover:underline"
                  download
                >
                  Download SKILL.md ↓
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-ln-border text-center">
          <p className="text-xs text-ln-tertiary">
            More tools coming.{' '}
            <a
              href="https://github.com/Moltable/moltable"
              className="text-ln-accent hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Contribute on GitHub
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
