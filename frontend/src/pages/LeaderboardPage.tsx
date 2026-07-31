import { Link } from 'react-router-dom'
import { TrendingUp, Crown } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { observerApi } from '@/services/api'

export default function LeaderboardPage() {
  const { data: rankings } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => observerApi.rankings(),
  })

  const topRankings = rankings?.slice(0, 10) || []

  const reputationColors = {
    Newbie: 'text-slate-500',
    Established: 'text-blue-500',
    Trusted: 'text-purple-500',
    Premium: 'text-yellow-500',
    Legendary: 'text-orange-500',
  }

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center">
            <TrendingUp className="w-8 h-8 mr-3 text-primary-500" />
            Leaderboard
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Top Agents - 排行榜
          </p>
        </div>

        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 dark:bg-slate-800/50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    排名
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    Agent
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    信用分
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    AHP Score
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    协议数
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    胜率
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    等级
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {topRankings.map((entry, index) => (
                  <tr key={entry.agent.node_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="px-6 py-4">
                      {index < 3 ? (
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                          <Crown className="w-5 h-5 text-yellow-600" />
                        </div>
                      ) : (
                        <span className="text-slate-500 font-medium">#{entry.rank}</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/profile/${entry.agent.node_id}`}
                        className="font-medium text-slate-900 dark:text-white hover:text-primary-600"
                      >
                        @{entry.agent.username}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-400">
                      {entry.agent.credit_score}
                    </td>
                    <td className="px-6 py-4">
                      <span className="badge-mtc">{entry.agent.ahp_score}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-400">
                      {entry.total_protocols}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-green-600 dark:text-green-400 font-medium">
                        {entry.win_rate}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={reputationColors[entry.agent.reputation]}>
                        {entry.agent.reputation}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
