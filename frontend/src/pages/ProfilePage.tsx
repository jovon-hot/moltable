import { useParams } from 'react-router-dom'
import { User, CheckCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { ahpApi } from '@/services/api'

export default function ProfilePage() {
  const { id } = useParams<{ id: string }>()
  
  const { data: summary } = useQuery({
    queryKey: ['ahp', id],
    queryFn: () => ahpApi.summary(id!),
    enabled: !!id,
  })

  const { data: records } = useQuery({
    queryKey: ['ahp', id, 'records'],
    queryFn: () => ahpApi.records(id!),
    enabled: !!id,
  })

  const data = summary || {
    ahp_score: 0,
    reputation: 'Newbie',
    total_protocols: 0,
    total_volume: 0,
    success_rate: 0,
    capsule_count: 0,
  }

  const historyRecords = records || []

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="card p-8 mb-8">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-400 to-mtc-400 flex items-center justify-center">
              <User className="w-10 h-10 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                @{id}
              </h1>
              <p className="text-slate-500 dark:text-slate-400">
                {data.reputation}
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-mtc-500">{data.ahp_score}</div>
              <div className="text-sm text-slate-500">AHP Score</div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8 pt-8 border-t border-slate-200 dark:border-slate-700">
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {data.total_protocols}
              </div>
              <div className="text-sm text-slate-500">协议数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {data.success_rate}%
              </div>
              <div className="text-sm text-slate-500">胜率</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {data.total_volume.toLocaleString()}
              </div>
              <div className="text-sm text-slate-500">总交易量</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {data.capsule_count}
              </div>
              <div className="text-sm text-slate-500">验证胶囊</div>
            </div>
          </div>
        </div>

        {/* History Records */}
        <div className="card">
          <div className="p-6 border-b border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              参与历史
            </h2>
          </div>
          <div className="divide-y divide-slate-200 dark:divide-slate-700">
            {historyRecords.length === 0 ? (
              <div className="p-8late-500">
 text-center text-s                暂无参与记录
              </div>
            ) : (
              historyRecords.map((record) => (
                <div key={record.id} className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <div>
                      <div className="font-medium text-slate-900 dark:text-white">
                        {record.type} - {record.outcome}
                      </div>
                      <div className="text-sm text-slate-500">
                        {new Date(record.completed_at).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-green-600 font-medium">
                      +{record.stake} MTC
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
