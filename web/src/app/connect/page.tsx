'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { useLang } from '@/contexts/LanguageContext'
import { Copy, Check, ArrowRight, Loader2, RotateCcw, Sparkles, Zap } from 'lucide-react'
import { useSearchParams } from 'next/navigation'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

type Platform = 'hermes' | 'claude' | 'cursor' | 'generic'

type KeyStatus =
  | { state: 'idle' }
  | { state: 'checking' }
  | { state: 'valid'; user: { name?: string; email?: string } }
  | { state: 'invalid'; message: string }
  | { state: 'error'; message: string }

export default function OnboardingPage() {
  const { t, lang } = useLang()
  const searchParams = useSearchParams()
  const [platform, setPlatform] = useState<Platform>('hermes')
  const [copied, setCopied] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [keyStatus, setKeyStatus] = useState<KeyStatus>({ state: 'idle' })
  const isNewUser = searchParams.get('new') === 'true'
  const planFromUrl = searchParams.get('plan') || ''

  // ── Auto-activate trial for Pro signups ──
  const activateTrialIfPro = async (key: string) => {
    if (planFromUrl !== 'pro') return
    try {
      await fetch(`${API_BASE}/api/billing/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
        body: JSON.stringify({ plan: 'pro', accept_terms: true }),
      })
    } catch { /* silent */ }
  }

  // ── API Key validation (also callable from useEffect) ──
  const validateKeyStatic = useCallback(async (key: string) => {
    const controller = new AbortController()
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { 'X-API-Key': key },
        signal: controller.signal,
      })
      if (res.ok) {
        const data = await res.json().catch(() => ({}))
        setKeyStatus({ state: 'valid', user: { name: data?.name, email: data?.email } })
      } else {
        setKeyStatus({ state: 'invalid', message: '' })
      }
    } catch {
      setKeyStatus({ state: 'error', message: '' })
    }
  }, [])

  // Pre-fill key from URL param
  useEffect(() => {
    const keyFromUrl = searchParams.get('key')
    if (keyFromUrl) {
      setApiKey(keyFromUrl)
      validateKeyStatic(keyFromUrl)
      activateTrialIfPro(keyFromUrl)
    }
  }, [searchParams, validateKeyStatic])

  // ── API Key 实时验证 ──────────────────────────────
  const seqRef = useRef(0)                       // guards against stale responses
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const controllerRef = useRef<AbortController | null>(null)

  const validateKey = useCallback(async (raw: string) => {
    const key = raw.trim()
    if (key.length <= 20) {
      setKeyStatus({ state: 'idle' })
      return
    }
    const seq = ++seqRef.current
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller
    setKeyStatus({ state: 'checking' })
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { 'X-API-Key': key },
        signal: controller.signal,
      })
      if (seq !== seqRef.current) return // a newer check superseded this one
      if (res.ok) {
        const data = await res.json().catch(() => ({}))
        setKeyStatus({ state: 'valid', user: { name: data?.name, email: data?.email } })
      } else {
        const body = await res.json().catch(() => null)
        const detail = body && typeof body.detail === 'string' ? body.detail : ''
        setKeyStatus({ state: 'invalid', message: detail })
      }
    } catch (err) {
      if ((err as Error)?.name === 'AbortError') return
      if (seq !== seqRef.current) return
      setKeyStatus({
        state: 'error',
        message: lang === 'zh' ? '网络错误，请重试' : 'Network error, please retry',
      })
    }
  }, [lang])

  const handleApiKeyChange = (value: string) => {
    setApiKey(value)
    if (timerRef.current) clearTimeout(timerRef.current)
    const key = value.trim()
    if (key.length <= 20) {
      seqRef.current++           // invalidate any in-flight check
      controllerRef.current?.abort()
      setKeyStatus({ state: 'idle' })
      return
    }
    // debounce: only fire once the user pauses typing/pasting
    timerRef.current = setTimeout(() => validateKey(value), 400)
  }

  const retryValidate = () => {
    if (timerRef.current) clearTimeout(timerRef.current)
    validateKey(apiKey)
  }

  useEffect(() => {
    return () => {
      controllerRef.current?.abort()
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [])

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
Header: X-API-Key: ***
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
    <div className="min-h-screen" style={{ background: '#0D0D14', color: '#ffffff' }}>
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 pt-24 pb-16">
        {/* 🪄 Magic moment banner for new users */}
        {isNewUser && (
          <div className="mb-10 p-5 rounded-xl animate-in" style={{ background: 'linear-gradient(135deg, rgba(67,56,202,0.15), rgba(67,56,202,0.04))', boxShadow: '0 0 0 1px rgba(67,56,202,0.2)' }}>
            <div className="flex items-start gap-3">
              <Sparkles size={22} style={{ color: '#4338CA', marginTop: 2 }} />
              <div>
                <h2 className="text-lg mb-1" style={{ fontWeight: 600, color: '#ffffff' }}>
                  {lang === 'zh' ? '🎉 注册成功！你的 AI 即将认识你' : '🎉 Registered! Your AI Is About to Know You'}
                </h2>
                <p className="text-sm mb-0" style={{ color: '#888888', lineHeight: 1.6 }}>
                  {lang === 'zh'
                    ? '下方是你的专属 API Key，已自动填入。复制配置 → 粘贴到 AI 工具 → 你的 AI 就能获取你的偏好和记忆。全程 30 秒。'
                    : 'Your API key is filled in below. Copy the config → paste into your AI tool → your AI will know your preferences and memories. Takes 30 seconds.'}
                </p>
              </div>
            </div>
          </div>
        )}
        {/* Pro trial banner */}
        {planFromUrl === 'pro' && isNewUser && (
          <div className="mb-8 p-4 rounded-xl" style={{ background: 'linear-gradient(135deg, rgba(52,211,153,0.1), rgba(52,211,153,0.02))', boxShadow: '0 0 0 1px rgba(52,211,153,0.25)' }}>
            <div className="flex items-center gap-2">
              <Zap size={18} style={{ color: '#34d399' }} />
              <span className="text-sm" style={{ color: '#34d399', fontWeight: 510 }}>
                {lang === 'zh' ? '✅ Pro 90天试用已激活 — 全部功能已解锁' : '✅ Pro 90-Day Trial Activated — All Features Unlocked'}
              </span>
              <a
                href={`/share?key=${apiKey}`}
                className="ml-auto text-xs px-3 py-1 rounded-md transition-all"
                style={{ background: 'rgba(52,211,153,0.15)', color: '#34d399', fontWeight: 510, textDecoration: 'none' }}
              >
                🔥 {lang === 'zh' ? '炫耀一下' : 'Share'}
              </a>
            </div>
          </div>
        )}
        <h1 className="text-3xl sm:text-4xl mb-4" style={{ fontWeight: 590, letterSpacing: '-0.5px' }}>
          {lang === 'zh' ? '30 秒接入 Moltable' : 'Connect in 30 Seconds'}
        </h1>
        <p className="text-base mb-12 max-w-xl" style={{ color: '#888888', lineHeight: 1.7 }}>
          {lang === 'zh'
            ? '你的 AI 助手会通过 MCP 协议自动获取你的身份、偏好和记忆。不必每换个 AI 就重新介绍自己。'
            : 'Your AI assistants get your identity, preferences, and memories via MCP. Stop re-introducing yourself to every new AI.'
          }
        </p>

        {/* API Key Input */}
        <div className="mb-8 p-5 rounded-xl" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
          <label className="text-xs mb-2 block" style={{ color: '#888888', fontWeight: 500 }}>
            {lang === 'zh' ? '你的 Moltable API Key' : 'Your Moltable API Key'}
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={apiKey}
              onChange={e => handleApiKeyChange(e.target.value)}
              placeholder="molt_xxxxxxxxxxxx"
              className="flex-1 px-4 py-2.5 rounded-lg text-sm font-mono outline-none transition-all"
              style={{ background: '#0D0D14', color: '#4338CA', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)' }}
              onFocus={e => e.target.style.boxShadow = '0 0 0 1px #4338CA'}
              onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            />
            <a
              href="/register"
              className="px-5 py-2.5 rounded-lg text-sm whitespace-nowrap transition-all hover:opacity-90"
              style={{ background: '#4338CA', color: '#fff', fontWeight: 510, textDecoration: 'none' }}
            >
              {lang === 'zh' ? '免费注册' : 'Sign Up'}
            </a>
          </div>
          {/* Live validation status */}
          {keyStatus.state !== 'idle' && (
            <div className="mt-3 flex items-center gap-2 text-sm">
              {keyStatus.state === 'checking' && (
                <>
                  <Loader2 size={14} className="animate-spin" style={{ color: '#888888' }} />
                  <span style={{ color: '#888888' }}>{lang === 'zh' ? '验证中…' : 'Verifying…'}</span>
                </>
              )}
              {keyStatus.state === 'valid' && (
                <>
                  <span style={{ color: '#34d399' }}>✅</span>
                  <span style={{ color: '#34d399', fontWeight: 500 }}>
                    {keyStatus.user.name || keyStatus.user.email || (lang === 'zh' ? 'API Key 有效' : 'Valid API Key')}
                  </span>
                  {keyStatus.user.name && keyStatus.user.email && (
                    <span style={{ color: '#888888' }}> · {keyStatus.user.email}</span>
                  )}
                </>
              )}
              {keyStatus.state === 'invalid' && (
                <>
                  <span style={{ color: '#f87171' }}>❌</span>
                  <span style={{ color: '#f87171' }}>
                    {lang === 'zh' ? 'API Key 无效' : 'Invalid API Key'}
                    {keyStatus.message ? `（${keyStatus.message}）` : ''}
                  </span>
                </>
              )}
              {keyStatus.state === 'error' && (
                <>
                  <span style={{ color: '#fbbf24' }}>⚠️</span>
                  <span style={{ color: '#fbbf24' }}>{keyStatus.message}</span>
                  <button
                    onClick={retryValidate}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs transition-all hover:opacity-90"
                    style={{ background: 'rgba(255,255,255,0.08)', color: '#fbbf24', fontWeight: 500 }}
                  >
                    <RotateCcw size={12} />
                    {lang === 'zh' ? '重试' : 'Retry'}
                  </button>
                </>
              )}
            </div>
          )}
        </div>

        {/* Platform Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {(Object.keys(commands) as Platform[]).map(p => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className="px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all"
              style={{
                background: platform === p ? '#4338CA' : '#14141E',
                color: platform === p ? '#fff' : '#888888',
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
            <div key={i} className="rounded-xl p-5" style={{ background: '#14141E', boxShadow: '0 0 0 1px rgba(255,255,255,0.06)' }}>
              <h3 className="text-sm mb-3" style={{ fontWeight: 590, color: '#ffffff' }}>{step.title}</h3>
              {step.code && (
                <div className="relative group">
                  <pre className="p-4 rounded-lg text-sm font-mono overflow-x-auto" style={{ background: '#0D0D14', color: '#cccccc', lineHeight: 1.6 }}>
                    {step.code}
                  </pre>
                  <button
                    onClick={() => handleCopy(step.code!, `step-${i}`)}
                    className="absolute top-3 right-3 p-1.5 rounded-md transition-all"
                    style={{ background: 'rgba(255,255,255,0.06)', color: copied === `step-${i}` ? '#4338CA' : '#888888' }}
                  >
                    {copied === `step-${i}` ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </div>
              )}
              {step.desc && (
                <p className="text-sm mt-2" style={{ color: '#888888' }}>{step.desc}</p>
              )}
            </div>
          ))}
        </div>

        {/* One-liner for registered users */}
        <div className="mt-12 p-5 rounded-xl" style={{ background: 'linear-gradient(135deg, rgba(67,56,202,0.08), rgba(67,56,202,0.02))' }}>
          <h3 className="text-sm mb-3" style={{ fontWeight: 590 }}>
            ⚡ {lang === 'zh' ? '一行命令接入 Hermes（已注册用户）' : 'One-liner for Hermes (existing users)'}
          </h3>
          <div className="relative group">
            <pre className="p-4 rounded-lg text-sm font-mono overflow-x-auto" style={{ background: '#0D0D14', color: '#4338CA', lineHeight: 1.6 }}>
              {apiKey
                ? `curl -sL moltable.ai/connect.sh | bash -s -- ${apiKey}`
                : 'curl -sL moltable.ai/connect.sh | bash -s -- <你的API-KEY>'}
            </pre>
            <button
              onClick={() => handleCopy(`curl -sL moltable.ai/connect.sh | bash -s -- ${apiKey || '<你的API-KEY>'}`, 'oneline')}
              className="absolute top-3 right-3 p-1.5 rounded-md transition-all"
              style={{ background: 'rgba(255,255,255,0.06)', color: copied === 'oneline' ? '#4338CA' : '#888888' }}
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
            style={{ background: '#4338CA', color: '#fff', fontWeight: 510, textDecoration: 'none' }}
          >
            {lang === 'zh' ? '免费开始' : 'Get Started Free'} <ArrowRight size={18} />
          </a>
        </div>
      </div>
    </div>
  )
}
