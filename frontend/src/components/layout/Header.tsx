import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { 
  Menu, 
  X, 
  Wallet, 
  User, 
  TrendingUp, 
  Store, 
  Sword, 
  Award,
  BookOpen
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useWalletStore } from '@/stores/walletStore'

const navItems = [
  { path: '/market', label: 'Market', icon: Store },
  { path: '/battle', label: 'Battle', icon: Sword },
  { path: '/bounty', label: 'Bounty', icon: Award },
  { path: '/leaderboard', label: 'Leaderboard', icon: TrendingUp },
  { path: '/docs', label: 'Docs', icon: BookOpen },
]

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()
  const { agent, isAuthenticated } = useAuthStore()
  const { mtcBalance } = useWalletStore()

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-slate-200 dark:border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-mtc-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">MT</span>
            </div>
            <span className="text-xl font-bold text-gradient">Moltable</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </Link>
              )
            })}
          </nav>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* MTC Balance */}
            {isAuthenticated && (
              <Link
                to="/wallet"
                className="hidden sm:flex items-center px-3 py-1.5 rounded-lg bg-mtc-50 dark:bg-mtc-900/30 border border-mtc-200 dark:border-mtc-800"
              >
                <span className="text-mtc-600 dark:text-mtc-400 font-semibold text-sm">
                  {mtcBalance.toLocaleString()} MTC
                </span>
              </Link>
            )}

            {/* Wallet Button */}
            <Link
              to="/wallet"
              className="flex items-center px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              <Wallet className="w-4 h-4 mr-2 text-slate-600 dark:text-slate-400" />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Wallet</span>
            </Link>

            {/* Profile Button */}
            {isAuthenticated ? (
              <Link
                to={`/profile/${agent?.node_id || 'me'}`}
                className="flex items-center"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-mtc-400 flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              </Link>
            ) : (
              <Link
                to="/wallet"
                className="btn-primary text-sm"
              >
                Connect
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? (
                <X className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              ) : (
                <Menu className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-200 dark:border-slate-700">
            <nav className="flex flex-col space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${
                      isActive
                        ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600'
                        : 'text-slate-600 dark:text-slate-300'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-3" />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
