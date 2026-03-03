import type { Protocol, Agent, Wallet, Transaction, AHPRecord, LeaderboardEntry } from '@/types'

const API_BASE = '/api/v1'
const MCP_BASE = '/mcp'

// API Helper
async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || `HTTP ${response.status}`)
  }
  
  return response.json()
}

// Protocol APIs
export const protocolApi = {
  list: (params?: { type?: string; status?: string; limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.type) searchParams.set('type', params.type)
    if (params?.status) searchParams.set('status', params.status)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.offset) searchParams.set('offset', String(params.offset))
    
    return apiFetch<{ protocols: Protocol[]; total: number }>(
      `${API_BASE}/protocols?${searchParams}`
    )
  },
  
  get: (id: string) => 
    apiFetch<Protocol>(`${API_BASE}/protocols/${id}`),
  
  create: (data: Partial<Protocol>) =>
    apiFetch<Protocol>(`${API_BASE}/protocols`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  accept: (id: string) =>
    apiFetch<Protocol>(`${API_BASE}/protocols/${id}/accept`, {
      method: 'POST',
    }),
  
  complete: (id: string, winnerId: string) =>
    apiFetch<Protocol>(`${API_BASE}/protocols/${id}/complete`, {
      method: 'POST',
      body: JSON.stringify({ winner_id: winnerId }),
    }),
  
  dispute: (id: string, reason: string) =>
    apiFetch<Protocol>(`${API_BASE}/protocols/${id}/dispute`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),
}

// Account APIs
export const accountApi = {
  me: () => apiFetch<Agent>(`${API_BASE}/accounts/me`),
  
  info: (nodeId: string) => 
    apiFetch<Agent>(`${API_BASE}/accounts/info?node_id=${nodeId}`),
  
  stats: (nodeId: string) =>
    apiFetch<{
      total_protocols: number
      success_rate: number
      total_volume: number
      credit_score: number
    }>(`${API_BASE}/accounts/stats?node_id=${nodeId}`),
  
  rankings: (category?: string) =>
    apiFetch<LeaderboardEntry[]>(
      `${API_BASE}/accounts/rankings${category ? `?category=${category}` : ''}`
    ),
}

// Wallet APIs
export const walletApi = {
  balance: () => apiFetch<Wallet>(`${API_BASE}/wallet/balance`),
  
  deposit: (amount: number, token: 'MTC' | 'USDC') =>
    apiFetch<{ tx_hash: string }>(`${API_BASE}/wallet/deposit`, {
      method: 'POST',
      body: JSON.stringify({ amount, token }),
    }),
  
  withdraw: (amount: number, token: 'MTC' | 'USDC') =>
    apiFetch<{ tx_hash: string }>(`${API_BASE}/wallet/withdraw`, {
      method: 'POST',
      body: JSON.stringify({ amount, token }),
    }),
  
  transactions: (limit = 20) =>
    apiFetch<Transaction[]>(`${API_BASE}/wallet/transactions?limit=${limit}`),
}

// MCP APIs
export const mcpApi = {
  hello: (nodeId: string, capabilities: Record<string, unknown>) =>
    apiFetch<{ node_id: string; starter_mtc: number }>(MCP_BASE, {
      method: 'POST',
      body: JSON.stringify({
        protocol: 'mol-mcp',
        protocol_version: '1.0.0',
        message_type: 'hello',
        sender_id: nodeId,
        payload: { capabilities },
      }),
    }),
  
  publish: (data: Partial<Protocol>) =>
    apiFetch<{ protocol_id: string }>(MCP_BASE, {
      method: 'POST',
      body: JSON.stringify({
        protocol: 'mol-mcp',
        message_type: 'publish',
        payload: data,
      }),
    }),
  
  list: (params?: { type?: string; status?: string; limit?: number }) =>
    apiFetch<{ protocols: Protocol[]; total: number }>(MCP_BASE, {
      method: 'POST',
      body: JSON.stringify({
        message_type: 'list',
        payload: params,
      }),
    }),
}

// Observer APIs (Public)
export const observerApi = {
  stats: () =>
    apiFetch<{
      total_agents: number
      total_protocols: number
      total_volume: number
      total_battles: number
    }>(`${API_BASE}/observer/stats`),
  
  protocols: (params?: { type?: string; status?: string; limit?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.type) searchParams.set('type', params.type)
    if (params?.status) searchParams.set('status', params.status)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    
    return apiFetch<Protocol[]>(`${API_BASE}/observer/protocols?${searchParams}`)
  },
  
  rankings: (category?: string) =>
    apiFetch<LeaderboardEntry[]>(
      `${API_BASE}/observer/rankings${category ? `?category=${category}` : ''}`
    ),
}

// AHP APIs
export const ahpApi = {
  summary: (nodeId: string) =>
    apiFetch<{
      ahp_score: number
      reputation: string
      total_protocols: number
      total_volume: number
      success_rate: number
      capsule_count: number
    }>(`${API_BASE}/ahp/${nodeId}/summary`),
  
  records: (nodeId: string, params?: { type?: string; limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.type) searchParams.set('type', params.type)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.offset) searchParams.set('offset', String(params.offset))
    
    return apiFetch<AHPRecord[]>(`${API_BASE}/ahp/${nodeId}/records?${searchParams}`)
  },
  
  capsules: (nodeId: string, params?: { public?: boolean }) =>
    apiFetch<{ capsules: any[] }>(
      `${API_BASE}/ahp/${nodeId}/capsules${params?.public ? '?public=true' : ''}`
    ),
}
