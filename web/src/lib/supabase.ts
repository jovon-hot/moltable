'use client'

import { createBrowserClient } from '@supabase/ssr'

// 检测是否有 Supabase 配置
const hasSupabase = () => {
  return !!(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
}

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

/** 是否使用本地 SQLite 模式（无 Supabase） */
export function isLocalMode(): boolean {
  return !hasSupabase()
}

/** 本地存储 API Key */
export function setLocalKey(key: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('moltable_key', key)
  }
}

/** 读取本地 API Key */
export function getLocalKey(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('moltable_key')
  }
  return null
}

/** 删除本地 API Key（登出） */
export function clearLocalKey() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('moltable_key')
  }
}

/** 检测是否已登录（本地模式） */
export function isLocalLoggedIn(): boolean {
  return !!getLocalKey()
}

/** 本地注册 */
export async function localRegister(email: string, password: string, name?: string) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name: name || '' }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    // FastAPI returns detail as array of objects or string — extract first human-readable message
    let msg = '注册失败'
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      msg = translatePydanticError(data.detail[0].msg) || '注册失败'
    } else if (typeof data.detail === 'string') {
      msg = data.detail
    }
    throw new Error(msg)
  }
  const data = await res.json()
  if (data.key) setLocalKey(data.key)
  return data
}

/** 把 FastAPI/Pydantic 校验错误转成中文可读信息 */
function translatePydanticError(msg: string): string {
  const m = (msg || '').toLowerCase()
  if (m.includes('at least') && m.includes('character')) return '密码至少需要 8 个字符'
  if (m.includes('email address') || m.includes('valid email')) return '请输入有效的邮箱地址'
  if (m.includes('already registered') || m.includes('already exists') || m.includes('already')) return '该邮箱已注册'
  if (m.includes('disposable') || m.includes('请使用真实邮箱')) return '请使用真实邮箱注册'
  if (m.includes('field required') || m.includes('missing')) return '请填写必填项'
  if (m.includes('too long') || m.includes('too short')) return '输入长度不符合要求'
  // 已经是中文或无法识别时原样返回
  return msg
}

/** 本地登录 */
export async function localLogin(email: string, password: string) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as any).detail || '登录失败')
  }
  const data = await res.json()
  // 存储 session token（MCP 端点通过 X-API-Key header 接受 mol_ 前缀的 session token）
  if (data.session_token) setLocalKey(data.session_token)
  return data
}
