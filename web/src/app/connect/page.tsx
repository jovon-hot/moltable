'use client'

import { useState } from 'react'
import { useLang } from '@/contexts/LanguageContext'
import { Copy, Check, Terminal, Monitor, Box, ArrowRight } from 'lucide-react'

const API_BASE = 'https://api.moltable.ai'

type Platform = 'hermes' | 'claude' | 'cursor' | 'generic'

export default function OnboardingPage() {
  const { t, lang } = useLang()
  const [platform, setPlatform] = useState<Platform>('hermes')
  const [copied, setCopied] = useState('')
  const [apiKey, setApiKey] = useState('')

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(''), 2000)
  }

  const mcpConfig = apiKey ? JSON.stringify({
    mcpServers: {
      moltable: {
        type: "http",
        url: `${API_BASE}/mcp`,
        headers: { "X-API-Key": apiKey },
        description: "Moltable — AI Identity & Memory Layer"
      }
    }
  }, null, 2) : '// 请先输入你的 Moltable API Key'

  const commands: Record<Platform, { label: string; steps: { title: string; code?: string; desc?: string }[] }> = {
    hermes: {
      label: 'Hermes Agent',
      steps: [
        {
          title: lang === 'zh' ? '1. 打开 MCP 配置文件' : '1. Open MCP config file',
          desc: lang === 'zh' ? '在终端中编辑 ~/.hermes/mcp.json' : 'Edit ~/.hermes/mcp.json in terminal',
          code: 'nano ~/.hermes/mcp.json'
        },
        {
          title: lang === 'zh' ? '2. 粘贴配置（如果已有其他服务器，用逗号合并）' : '2. Paste config below (merge with existing mcpServers if any)',
          code: mcpConfig
        },
        {
          title: lang === 'zh' ? '3. 重启 Hermes 或刷新对话' : '3. Restart Hermes or start a new chat',
          code: '/new'
        },
        {
          title: lang === 'zh' ? '4. 验证：在 Hermes 中说' : '4. Verify: ask Hermes',
          desc: lang === 'zh' ? '"用 search_memory 搜索: 我是谁"' : '"use search_memory to find: who am I"'
        }
      ]
    },
    claude: {
      label: 'Claude Code',
      steps: [
        {
          title: lang === 'zh' ? '1. 打开 Claude 配置文件' : '1. Open Claude config',
          desc: lang === 'zh' ? '编辑 ~/.claude/mcp.json' : 'Edit ~/.claude/mcp.json',
          code: 'nano ~/.claude/mcp.json'
        },
        {
          title: lang === 'zh' ? '2. 粘贴配置' : '2. Paste config',
          code: mcpConfig
        },
        {
          title: lang === 'zh' ? '3. 在 Claude Code 中验证' : '3. Verify in Claude Code',
          desc: lang === 'zh' ? '"search user preferences"' : '"search user preferences"'
        }
      ]
    },
    cursor: {
      label: 'Cursor / Cline / Copilot',
      steps: [
        {
          title: lang === 'zh' ? '1. 打开项目设置' : '1. Open project settings',
          desc: lang === 'zh' ? '在 .cursor/mcp.json 或 VS Code 设置中的 MCP 配置区' : 'In .cursor/mcp.json or VS Code settings MCP section',
          code: 'nano .cursor/mcp.json'
        },
        {
          title: lang === 'zh' ? '2. 粘贴配置' : '2. Paste config',
          code: mcpConfig
        },
        {
          title: lang === 'zh' ? '3. 重启编辑器' : '3. Restart your editor',
          desc: lang === 'zh' ? 'Cmd+Q 退出后重新打开，MCP 工具将自动加载' : 'Cmd+Q quit and reopen, MCP tools will auto-load'
        }
      ]
    },
    generic: {
      label: lang === 'zh' ? '其他 MCP 客户端' : 'Other MCP Clients',
      steps: [
        {
          title: lang === 'zh' ? 'MCP JSON-RPC 端点' : 'MCP JSON-RPC endpoint',
          code: `POST ${API_BASE}/mcp
Header: X-API-Key: <your-key>
Content-Type: application/json`
        },
        {
          title: lang === 'zh' ? '工具发现' : 'Tool Discovery',
          code: `${API_BASE}/.well-known/mcp`
        }
      ]
    }
  }

  return (
    <div className="min-h-screen" style={{ background: '#08090a', color: '#f7f8f8' }}>
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 pt-24 pb-16">
        <h1 className="text-3xl sm:text-4xl mb-4" style={{ fontWeight: 590, letterSpacing: '-0.5px' }}>
          {lang === 'zh' ? '30 秒接入 Moltable' : 'Connect in 30 Seconds'}
        </h1>
        <p className="text-base mb-12 max-w-xl" style={{ color: '#8a8f98', lineHeight: 1.7 }}>
          {lang === 'zh'
            ? '你的 AI 助手会通过 MCP 协议自动获取你的身份、偏好和记忆。不必每换个 AI 就重新介绍自己。'
            : 'Your AI assistants get your identity, preferences, and memories via MCP. Stop re-introducing yourself to every new AI.'
          }
        </p>

        {/* API Key Input */}
        <div className="mb-8 p-5 rounded-xl" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
          <label className="text-xs mb-2 block" style={{ color: '#8a8f98', fontWeight: 500 }}>
            {lang === 'zh' ? '你的 Moltable API Key' : 'Your Moltable API Key'}
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="molt_xxxxxxxxxxxx"
              className="flex-1 px-4 py-2.5 rounded-lg text-sm font-mono outline-none transition-all"
              style={{ background: '#08090a', color: '#7170ff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)' }}
              onFocus={e => e.target.style.boxShadow = '0 0 0 1px #7170ff'}
              onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            />
            <a
              href="/register"
              className="px-5 py-2.5 rounded-lg text-sm whitespace-nowrap transition-all hover:opacity-90"
              style={{ background: '#7170ff', color: '#fff', fontWeight: 510, textDecoration: 'none' }}
            >
              {lang === 'zh' ? '免费注册' : 'Sign Up'}
            </a>
          </div>
        </div>

        {/* Platform Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {(Object.keys(commands) as Platform[]).map(p => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className="px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all"
              style={{
                background: platform === p ? '#7170ff' : '#0f1011',
                color: platform === p ? '#fff' : '#8a8f98',
                fontWeight: platform === p ? 510 : 400
              }}
            >
              {commands[p].label}
            </button>
          ))}
        </div>

        {/* Steps */}
        <div className="space-y-6">
          {commands[platform].steps.map((step, i) => (
            <div key={i} className="rounded-xl p-5" style={{ background: '#0f1011', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
              <h3 className="text-sm mb-3" style={{ fontWeight: 590, color: '#f7f8f8' }}>{step.title}</h3>
              {step.code && (
                <div className="relative group">
                  <pre className="p-4 rounded-lg text-sm font-mono overflow-x-auto" style={{ background: '#08090a', color: '#b0b5bd', lineHeight: 1.6 }}>
                    {step.code}
                  </pre>
                  <button
                    onClick={() => handleCopy(step.code!, `step-${i}`)}
                    className="absolute top-3 right-3 p-1.5 rounded-md transition-all"
                    style={{ background: 'rgba(255,255,255,0.06)', color: copied === `step-${i}` ? '#7170ff' : '#8a8f98' }}
                  >
                    {copied === `step-${i}` ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </div>
              )}
              {step.desc && (
                <p className="text-sm mt-2" style={{ color: '#8a8f98' }}>{step.desc}</p>
              )}
            </div>
          ))}
        </div>

        {/* One-liner for registered users */}
        <div className="mt-12 p-5 rounded-xl" style={{ background: 'linear-gradient(135deg, rgba(113,112,255,0.08), rgba(113,112,255,0.02))' }}>
          <h3 className="text-sm mb-3" style={{ fontWeight: 590 }}>
            ⚡ {lang === 'zh' ? '一行命令接入 Hermes（已注册用户）' : 'One-liner for Hermes (existing users)'}
          </h3>
          <div className="relative group">
            <pre className="p-4 rounded-lg text-sm font-mono overflow-x-auto" style={{ background: '#08090a', color: '#7170ff', lineHeight: 1.6 }}>
              {apiKey
                ? `curl -sL moltable.ai/connect.sh | bash -s -- ${apiKey}`
                : 'curl -sL moltable.ai/connect.sh | bash -s -- <你的API-KEY>'}
            </pre>
            <button
              onClick={() => handleCopy(`curl -sL moltable.ai/connect.sh | bash -s -- ${apiKey || '<你的API-KEY>'}`, 'oneline')}
              className="absolute top-3 right-3 p-1.5 rounded-md transition-all"
              style={{ background: 'rgba(255,255,255,0.06)', color: copied === 'oneline' ? '#7170ff' : '#8a8f98' }}
            >
              {copied === 'oneline' ? <Check size={14} /> : <Copy size={14} />}
            </button>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="mt-16 pt-12 pb-24 border-t text-center" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
          <p className="text-lg mb-6" style={{ fontWeight: 500 }}>
            {lang === 'zh' ? '还没注册？' : 'Not registered yet?'}
          </p>
          <a
            href="/register"
            className="inline-flex items-center gap-2 px-8 py-3 rounded-lg text-base transition-all hover:opacity-90"
            style={{ background: '#7170ff', color: '#fff', fontWeight: 510, textDecoration: 'none' }}
          >
            {lang === 'zh' ? '免费开始' : 'Get Started Free'} <ArrowRight size={18} />
          </a>
        </div>
      </div>
    </div>
  )
}
