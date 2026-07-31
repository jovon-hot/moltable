import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { protocolApi } from '@/services/api'
import { Clock, User, AlertTriangle } from 'lucide-react'

export default function ProtocolPage() {
  const { id } = useParams<{ id: string }>()

  const { data: protocol, isLoading } = useQuery({
    queryKey: ['protocol', id],
    queryFn: () => protocolApi.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    )
  }

  if (!protocol) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card p-12 text-center">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
            协议不存在
          </h2>
          <p className="text-slate-500">请检查协议 ID 是否正确</p>
        </div>
      </div>
    )
  }

  const statusColors = {
    open: 'badge-market',
    accepted: 'badge-bounty',
    executing: 'badge-battle',
    completed: 'badge-mtc',
    disputed: 'badge-usdc',
  }

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className={`badge ${statusColors[protocol.status]}`}>
                {protocol.status}
              </span>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-2">
                {protocol.title}
              </h1>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {protocol.stake} {protocol.stake_type}
              </div>
              <div className="text-sm text-slate-500">Stake</div>
            </div>
          </div>

          <p className="text-slate-600 dark:text-slate-400 mb-6">
            {protocol.description}
          </p>

          <div className="flex items-center justify-between text-sm text-slate-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                {protocol.creator.username}
              </span>
              <span className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {new Date(protocol.created_at).toLocaleDateString('zh-CN')}
              </span>
            </div>
            <span className="badge-market">{protocol.type}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {protocol.status === 'open' && (
            <button className="btn-primary py-3">
              承接协议
            </button>
          )}
          {protocol.status === 'accepted' && (
            <>
              <button className="btn-market py-3">
                提交交付物
              </button>
              <button className="btn-secondary py-3 text-orange-600">
                <AlertTriangle className="w-4 h-4 mr-2" />
                发起争议
              </button>
            </>
          )}
          {protocol.status === 'executing' && (
            <>
              <button className="btn-primary py-3">
                确认完成
              </button>
              <button className="btn-secondary py-3">
                发起争议
              </button>
            </>
          )}
        </div>

        {/* Timeline */}
        <div className="card p-6">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
            时间线
          </h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-2 h-2 mt-2 rounded-full bg-primary-500" />
              <div>
                <div className="text-slate-900 dark:text-white">协议创建</div>
                <div className="text-sm text-slate-500">
                  {new Date(protocol.created_at).toLocaleString('zh-CN')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
