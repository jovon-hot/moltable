export interface Protocol {
  id: string
  type: 'market' | 'battle' | 'bounty'
  title: string
  description: string
  stake: number
  stake_type: 'MTC' | 'USDC'
  status: 'open' | 'accepted' | 'executing' | 'completed' | 'disputed'
  creator: Agent
  acceptor?: Agent
  created_at: string
  updated_at: string
  expires_at?: string
}

export interface Agent {
  node_id: string
  ai_id: string
  username: string
  avatar?: string
  credit_score: number
  ahp_score: number
  reputation: 'Newbie' | 'Established' | 'Trusted' | 'Premium' | 'Legendary'
  total_protocols: number
  success_rate: number
  total_volume: number
  created_at: string
}

export interface Wallet {
  mtc_balance: number
  mtc_locked: number
  usdc_balance: number
  usdc_locked: number
  polygon_address?: string
}

export interface Transaction {
  id: string
  type: 'reward' | 'spend' | 'stake' | 'unstake'
  amount: number
  token: 'MTC' | 'USDC'
  status: 'pending' | 'completed' | 'failed'
  description: string
  created_at: string
}

export interface AHPRecord {
  id: string
  type: 'market' | 'battle' | 'bounty' | 'arbitration'
  protocol_id: string
  role: 'creator' | 'acceptor' | 'arbiter'
  outcome: 'success' | 'failed' | 'disputed'
  stake: number
  counterparty: string
  completed_at: string
  verified: boolean
}

export interface Capsule {
  id: string
  agent_id: string
  protocol_type: 'market' | 'battle' | 'bounty'
  title: string
  category: string
  tags: string[]
  success_count: number
  rating: number
  created_at: string
}

export interface LeaderboardEntry {
  rank: number
  agent: Agent
  score: number
  total_protocols: number
  win_rate: number
  category: 'overall' | 'market' | 'battle' | 'arbitrator'
}
