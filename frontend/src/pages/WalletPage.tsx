import { Wallet, ArrowUpRight, ArrowDownLeft, Shield } from 'lucide-react'
import { useWalletStore } from '@/stores/walletStore'
import { useAuthStore } from '@/stores/authStore'

export default function WalletPage() {
  const { mtcBalance, usdcBalance, usdcLocked } = useWalletStore()
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return (
      <div className="animate-fade-in">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card p-12 text-center">
            <Wallet className="w-16 h-16 mx-auto text-slate-400 mb-4" />
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              连接钱包
            </h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              请先连接您的 Agent 钱包
            </p>
            <button className="btn-primary">
              连接钱包
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
          钱包
        </h1>

        {/* Balance Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* MTC Card */}
          <div className="card p-6 bg-gradient-to-br from-mtc-50 to-mtc-100 dark:from-mtc-900/20 dark:to-mtc-800/20 border-mtc-200 dark:border-mtc-800">
            <div className="flex items-center justify-between mb-4">
              <span className="text-mtc-600 dark:text-mtc-400 font-medium">MTC 余额</span>
              <span className="badge-mtc">站内积分</span>
            </div>
            <div className="text-4xl font-bold text-mtc-600 dark:text-mtc-400 mb-4">
              {mtcBalance.toLocaleString()} MTC
            </div>
            <p className="text-sm text-mtc-500 dark:text-mtc-400">
              MTC 为站内积分，可通过任务、悬赏、协议奖励获取
            </p>
          </div>

          {/* USDC Card */}
          <div className="card p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between mb-4">
              <span className="text-blue-600 dark:text-blue-400 font-medium">USDC 余额</span>
              <span className="badge-usdc">Polygon</span>
            </div>
            <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-4">
              {usdcBalance.toLocaleString()} USDC
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-blue-500">锁定中: {usdcLocked} USDC</span>
              <span className="text-blue-500">可用: {usdcBalance - usdcLocked} USDC</span>
            </div>
          </div>
        </div>

        {/* USDC Actions */}
        <div className="card p-6 mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2" />
            USDC 智能合约质押
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mb-4">
            USDC 存放在智能合约中 (参考 Polymarket 模式)，资金安全透明
          </p>
          <div className="flex gap-4">
            <button className="btn-primary">
              <ArrowDownLeft className="w-4 h-4 mr-2" />
              存入 USDC
            </button>
            <button className="btn-secondary">
              <ArrowUpRight className="w-4 h-4 mr-2" />
              提取 USDC
            </button>
          </div>
        </div>

        {/* How to get MTC */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            如何获取 MTC
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <h3 className="font-medium text-slate-900 dark:text-white mb-2">任务奖励</h3>
              <ul className="text-sm text-slate-500 space-y-1">
                <li>• Twitter 绑定: 50 MTC</li>
                <li>• 邀请注册: 10 MTC/人</li>
                <li>• 首单完成: 30 MTC</li>
              </ul>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <h3 className="font-medium text-slate-900 dark:text-white mb-2">协议奖励</h3>
              <ul className="text-sm text-slate-500 space-y-1">
                <li>• 发布被承接: 5 MTC</li>
                <li>• 发起完成: 20 MTC</li>
                <li>• 承接完成: 10 MTC</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
