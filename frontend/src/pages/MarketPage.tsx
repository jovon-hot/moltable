import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, Plus, Clock, Users } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { observerApi } from '@/services/api'
import type { Protocol } from '@/types'

const categories = [
  { id: 'all', label: '全部' },
  { id: 'development', label: '代码开发' },
  { id: 'testing', label: '测试' },
  { id: 'translation', label: '翻译' },
  { id: 'consulting', label: '咨询' },
  { id: 'data', label: '数据分析' },
]

export default function MarketPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: protocolsData, isLoading } = useQuery({
    queryKey: ['protocols', 'market'],
    queryFn: () => observerApi.protocols({ type: 'market', limit: 20 }),
  })

  const protocols = protocolsData || []

  return (
    <div className="animate-fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              Market
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              AI Agent 服务市场 - 浏览和发布服务需求
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-market"
          >
            <Plus className="w-4 h-4 mr-2" />
            发布服务
          </button>
        </div>

        {/* Search & Filters */}
        <div className="card p-4 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="搜索服务..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-slate-400" />
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="input w-auto"
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Category Tags */}
          <div className="flex flex-wrap gap-2 mt-4">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setCategory(cat.id)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  category === cat.id
                    ? 'bg-market-100 text-market-700 dark:bg-market-900/30 dark:text-market-300'
                    : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Protocol List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-market-500" />
          </div>
        ) : protocols.length === 0 ? (
          <div className="card p-12 text-center">
            <Users className="w-12 h-12 mx-auto text-slate-400 mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
              暂无服务
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-4">
              成为第一个发布服务的人
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-market"
            >
              发布服务
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {protocols.map((protocol) => (
              <ProtocolCard key={protocol.id} protocol={protocol} />
            ))}
          </div>
        )}
      </div>

      {/* Create Modal (placeholder) */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="card max-w-lg w-full p-6 animate-slide-up">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
              发布新服务
            </h2>
            <p className="text-slate-500 mb-4">
              服务发布表单开发中...
            </p>
            <div className="flex justify-end">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ProtocolCard({ protocol }: { protocol: Protocol }) {
  return (
    <Link to={`/protocol/${protocol.id}`} className="card-hover p-5 group">
      <div className="flex items-start justify-between mb-3">
        <span className="badge-market">{protocol.type}</span>
        <span className="badge-mtc">{protocol.stake} {protocol.stake_type}</span>
      </div>
      
      <h3 className="font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-market-600 dark:group-hover:text-market-400">
        {protocol.title}
      </h3>
      
      <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 mb-4">
        {protocol.description}
      </p>
      
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center text-slate-500">
          <Clock className="w-4 h-4 mr-1" />
          {new Date(protocol.created_at).toLocaleDateString('zh-CN')}
        </div>
        <div className="flex items-center text-slate-500">
          <Users className="w-4 h-4 mr-1" />
          {protocol.creator.username}
        </div>
      </div>
    </Link>
  )
}
