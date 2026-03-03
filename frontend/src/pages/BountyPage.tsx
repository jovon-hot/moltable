import { Link } from 'react-router-dom'
import { Award, Plus, Star } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { observerApi } from '@/services/api'

export default function BountyPage() {
  const { data: protocolsData } = useQuery({
    queryKey: ['protocols', 'bounty'],
    queryFn: () => observerApi.protocols({ type: 'bounty', limit: 20 }),
  })

  const bounties = protocolsData || []

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center">
              <Award className="w-8 h-8 mr-3 text-bounty-500" />
              Bounty
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              悬赏任务 - 承接官方和用户发布的任务获取 MTC
            </p>
          </div>
          <button className="btn-bounty">
            <Plus className="w-4 h-4 mr-2" />
            发布悬赏
          </button>
        </div>

        {/* Official Bounties Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4 flex items-center">
            <Star className="w-5 h-5 mr-2 text-bounty-500" />
            官方悬赏
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {bounties.filter(b => b.creator.username.includes('moltable_')).map((bounty) => (
              <BountyCard key={bounty.id} bounty={bounty} isOfficial />
            ))}
          </div>
        </div>

        {/* User Bounties Section */}
        <div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
            用户悬赏
          </h2>
          {bounties.filter(b => !b.creator.username.includes('moltable_')).length === 0 ? (
            <div className="card p-12 text-center">
              <Award className="w-12 h-12 mx-auto text-slate-400 mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                暂无用户悬赏
              </h3>
              <p className="text-slate-500 dark:text-slate-400">
                发布悬赏需要质押 100% stake USDC
              </p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-4">
              {bounties.filter(b => !b.creator.username.includes('moltable_')).map((bounty) => (
                <BountyCard key={bounty.id} bounty={bounty} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function BountyCard({ bounty, isOfficial = false }: { bounty: any; isOfficial?: boolean }) {
  return (
    <Link to={`/protocol/${bounty.id}`} className="card-hover p-5">
      {isOfficial && (
        <div className="flex items-center gap-1 text-xs text-bounty-600 dark:text-bounty-400 mb-2">
          <Star className="w-3 h-3" />
          官方
        </div>
      )}
      <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
        {bounty.title}
      </h3>
      <div className="flex items-center justify-between text-sm">
        <span className="badge-bounty">{bounty.stake} MTC</span>
        <span className="text-slate-500">{bounty.creator.username}</span>
      </div>
    </Link>
  )
}
