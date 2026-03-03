import { create } from 'zustand'

interface WalletState {
  mtcBalance: number
  usdcBalance: number
  usdcLocked: number
  polygonAddress: string | null
  isLoading: boolean
  setBalances: (mtc: number, usdc: number, locked: number) => void
  setPolygonAddress: (address: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useWalletStore = create<WalletState>((set) => ({
  mtcBalance: 0,
  usdcBalance: 0,
  usdcLocked: 0,
  polygonAddress: null,
  isLoading: false,
  setBalances: (mtc, usdc, locked) =>
    set({ mtcBalance: mtc, usdcBalance: usdc, usdcLocked: locked }),
  setPolygonAddress: (address) => set({ polygonAddress: address }),
  setLoading: (loading) => set({ isLoading: loading }),
}))
