import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/Toaster'
import Layout from '@/components/layout/Layout'
import HomePage from '@/pages/HomePage'
import MarketPage from '@/pages/MarketPage'
import BattlePage from '@/pages/BattlePage'
import BountyPage from '@/pages/BountyPage'
import LeaderboardPage from '@/pages/LeaderboardPage'
import ProfilePage from '@/pages/ProfilePage'
import WalletPage from '@/pages/WalletPage'
import ProtocolPage from '@/pages/ProtocolPage'
import DocsPage from '@/pages/DocsPage'
import AdminPage from '@/pages/AdminPage'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="market" element={<MarketPage />} />
          <Route path="battle" element={<BattlePage />} />
          <Route path="bounty" element={<BountyPage />} />
          <Route path="leaderboard" element={<LeaderboardPage />} />
          <Route path="profile/:id" element={<ProfilePage />} />
          <Route path="wallet" element={<WalletPage />} />
          <Route path="protocol/:id" element={<ProtocolPage />} />
          <Route path="docs" element={<DocsPage />} />
          <Route path="admin" element={<AdminPage />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  )
}

export default App
