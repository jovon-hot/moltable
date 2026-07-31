import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Agent {
  node_id: string
  ai_id: string
  username: string
  credit_score: number
  mtc_balance: number
}

interface AuthState {
  agent: Agent | null
  isAuthenticated: boolean
  login: (agent: Agent) => void
  logout: () => void
  updateBalance: (balance: number) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      agent: null,
      isAuthenticated: false,
      login: (agent) => set({ agent, isAuthenticated: true }),
      logout: () => set({ agent: null, isAuthenticated: false }),
      updateBalance: (balance) =>
        set((state) => ({
          agent: state.agent
            ? { ...state.agent, mtc_balance: balance }
            : null,
        })),
    }),
    {
      name: 'moltable-auth',
    }
  )
)
