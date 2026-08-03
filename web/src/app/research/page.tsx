import { loadBenchmarks } from '@/lib/benchmarks'
import BenchmarksClient from './benchmarks-client'

export default function ResearchPage() {
  // 构建时从 benchmarks/results/benchmarks.json 读取评测结果
  // 基准未运行 / 文件缺失时返回 null → 客户端渲染「基准测试尚未运行」占位
  const data = loadBenchmarks()

  return <BenchmarksClient data={data} />
}
