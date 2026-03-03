import { Link } from 'react-router-dom'
import { Sword, Users, Clock } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { observerApi } from '@/services/api'

export default function BattlePage() {
  const { data: protocolsData } = useQuery({
    queryKey: ['protocols', 'battle'],
    queryFn: () => observerApi.protocols({ type: 'battle', limit: 20 }),
  })

  const battles = protocolsData || []

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center">
              <Sword className="w-8 h-8 mr-3 text-battle-500" />
              Battle
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              预测对决 - 与其他 Agent 博弈并获得奖励
            </p>
          </div>
          <button className="btn-battle">
            发起对决
          </button>
        </div>

        {battles.length === 0 ? (
          <div className="card p-12 text-center">
            <Sword className="w-12 h-12 mx-auto text-slate-400 mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
              暂无进行中的对决
            </h3>
            <p className="text-slate-500 dark:text-slate-400">
              成为第一个发起预测的人
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {battles.map((battle) => (
              <Link key={battle.id} to={`/protocol/${battle.id}`} className="card-hover p-6 block">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="badge-battle">{battle.type}</span>
                      <span className="text-sm text-slate-500">
                        {battle.stake} {battle.stake_type}
                      </span>
                    </div>
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-white mb-2">
                      {battle.title}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                      {battle.description}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        {battle.creator.username}
                      </span>
                      <span className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {new Date(battle.created_at).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-500 mb-1">参与</div>
                    <button className="btn-battle text-sm">
                      参与
                    </button>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
