import fs from 'fs'
import path from 'path'

/**
 * Moltable 评测基准数据加载器。
 *
 * 构建时（npm run build / npm run dev）从仓库根目录的 benchmarks/results/benchmarks.json
 * 读取评测结果。基准未运行（文件缺失 / status 非 completed / 无 metrics）时返回 null，
 * /research 页面显示「基准测试尚未运行」占位。
 *
 * 数据格式见 benchmarks/README.md。
 */

export type BenchmarkStatus = 'pending' | 'completed'
export type MetricTrend = 'up' | 'down' | 'flat'
export type SourceTag = 'measured' | 'public' | 'not_public' | 'na'

export interface BenchmarkMetric {
  id: string
  score: number | null
  target: number
  unit?: string
  trend?: MetricTrend
}

export interface BenchmarkCell {
  value: string
  source: SourceTag
}

export interface BenchmarkComparisonRow {
  dimension: string
  moltable?: BenchmarkCell
  mem0?: BenchmarkCell
  zep?: BenchmarkCell
}

export interface BenchmarkData {
  status: BenchmarkStatus
  generated_at: string | null
  metrics: BenchmarkMetric[]
  comparison: BenchmarkComparisonRow[]
}

export function loadBenchmarks(): BenchmarkData | null {
  try {
    // npm run build / dev 的工作目录是 web/，benchmarks/ 在仓库根目录
    const file = path.join(process.cwd(), '..', 'benchmarks', 'results', 'benchmarks.json')
    const raw = fs.readFileSync(file, 'utf-8')
    const data = JSON.parse(raw) as BenchmarkData
    if (!data || data.status !== 'completed' || !Array.isArray(data.metrics) || data.metrics.length === 0) {
      return null
    }
    return data
  } catch {
    return null
  }
}
