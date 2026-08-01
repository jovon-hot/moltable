'use client'

import { useState, useEffect } from 'react'
import {
  Users, Database, Activity, AlertTriangle,
  Zap, Server, Shield,
} from 'lucide-react'

interface AdminStats {
  users: {
    total: number
    new_today: number
    new_week: number
    active_today: number
    trial_activated: number
    trial_active: number
  }
  data: {
    total_memories: number
    total_projects: number
    total_personas: number
  }
  api: {
    calls_today: number
    error_count: number
  }
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

export default function AdminDashboard() {
  const [token, setToken] = useState('')
  const [secret, setSecret] = useState('')
  const [loggedIn, setLoggedIn] = useState(false)
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const login = async () => {
    setLoading(true)
    setError('')
    try {
      const r = await fetch(`${API_BASE}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ secret }),
      })
      if (!r.ok) throw new Error('Invalid admin secret')
      const d = await r.json()
      setToken(d.token)
      setLoggedIn(true)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    if (!token) return
    try {
      const r = await fetch(`${API_BASE}/api/admin/stats`, {
        headers: { 'X-Admin-Token': token },
      })
      const d = await r.json()
      setStats(d)
    } catch {}
  }

  const fetchUsers = async () => {
    if (!token) return
    try {
      const r = await fetch(`${API_BASE}/api/admin/users?limit=50`, {
        headers: { 'X-Admin-Token': token },
      })
      const d = await r.json()
      setUsers(d.users || [])
    } catch {}
  }

  useEffect(() => {
    if (loggedIn) {
      fetchStats()
      fetchUsers()
      const i = setInterval(fetchStats, 30000)
      return () => clearInterval(i)
    }
  }, [loggedIn, token])

  if (!loggedIn) {
    return (
      <div className="min-h-screen px-6 py-24 max-w-md mx-auto" style={{ background: '#08090a', color: '#f7f8f8' }}>
        <h1 className="text-2xl mb-6" style={{ fontWeight: 590 }}>Admin</h1>
        <p className="text-sm mb-4" style={{ color: '#8a8f98' }}>
          Enter the ADMIN_SECRET to access the dashboard.
        </p>
        <input
          type="password"
          value={secret}
          onChange={(e) => setSecret(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && login()}
          placeholder="Admin secret"
          className="w-full px-4 py-2.5 rounded-lg text-sm mb-3"
          style={{ background: '#0f1011', border: '1px solid rgba(255,255,255,0.08)', color: '#f7f8f8' }}
        />
        <button
          onClick={login}
          disabled={loading || !secret}
          className="w-full px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          style={{ background: '#7170ff', color: '#fff', opacity: loading ? 0.6 : 1 }}
        >
          {loading ? '...' : 'Login'}
        </button>
        {error && <p className="text-xs mt-3" style={{ color: '#f87171' }}>{error}</p>}
      </div>
    )
  }

  const cards = [
    { icon: Users, label: 'Total Users', value: stats?.users.total ?? '-', sub: `+${stats?.users.new_today ?? 0} today` },
    { icon: Activity, label: 'Active Today', value: stats?.users.active_today ?? '-', sub: `${stats?.api.calls_today ?? 0} API calls` },
    { icon: Zap, label: 'Pro Users', value: stats?.users.trial_active ?? '-', sub: `${stats?.users.trial_activated ?? 0} activated` },
    { icon: Database, label: 'Memories', value: stats?.data.total_memories ?? '-', sub: `${stats?.data.total_projects ?? 0} projects · ${stats?.data.total_personas ?? 0} personas` },
    { icon: AlertTriangle, label: 'Errors (1h)', value: stats?.api.error_count ?? 0, sub: 'Rolling 60-min window' },
  ]

  return (
    <div className="min-h-screen px-6 py-20 max-w-6xl mx-auto" style={{ background: '#08090a', color: '#f7f8f8' }}>
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590 }}>Admin Dashboard</h1>
          <p className="text-sm" style={{ color: '#8a8f98' }}>Moltable platform overview</p>
        </div>
        <button
          onClick={() => { fetchStats(); fetchUsers() }}
          className="px-4 py-2 rounded-lg text-sm"
          style={{ background: 'rgba(255,255,255,0.06)', color: '#8a8f98' }}
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
        {cards.map((c, i) => (
          <div key={i} className="p-5 rounded-lg" style={{ background: '#0f1011' }}>
            <c.icon size={18} style={{ color: '#7170ff', marginBottom: 8 }} />
            <p className="text-3xl mb-1" style={{ fontWeight: 590 }}>{c.value}</p>
            <p className="text-xs" style={{ color: '#8a8f98' }}>{c.label}</p>
            <p className="text-xs mt-1" style={{ color: '#5a5f68' }}>{c.sub}</p>
          </div>
        ))}
      </div>

      <h2 className="text-lg mb-4" style={{ fontWeight: 590 }}>Recent Users</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm" style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              {['Email', 'Plan', 'Active', 'Created'].map((h) => (
                <th key={h} className="text-left py-2 px-3 text-xs" style={{ color: '#5a5f68', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td className="py-2 px-3" style={{ color: '#f7f8f8' }}>{u.email}</td>
                <td className="py-2 px-3">
                  <span
                    className="px-2 py-0.5 rounded-full text-xs"
                    style={{
                      background: u.plan === 'pro' ? 'rgba(113,112,255,0.15)' : 'rgba(255,255,255,0.06)',
                      color: u.plan === 'pro' ? '#9d9cff' : '#8a8f98',
                    }}
                  >
                    {u.plan}
                  </span>
                </td>
                <td className="py-2 px-3 text-xs" style={{ color: '#8a8f98' }}>
                  {u.last_active_at ? new Date(u.last_active_at).toLocaleDateString() : '-'}
                </td>
                <td className="py-2 px-3 text-xs" style={{ color: '#5a5f68' }}>
                  {u.created_at ? new Date(u.created_at).toLocaleDateString() : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
