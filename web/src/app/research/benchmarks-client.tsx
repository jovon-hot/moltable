'use client'

import { TrendingUp, TrendingDown, Minus, FlaskConical } from 'lucide-react'
import { useLang } from '@/contexts/LanguageContext'
import type { BenchmarkData, BenchmarkCell, BenchmarkMetric, MetricTrend, SourceTag } from '@/lib/benchmarks'

const METRIC_IDS = ['cross_agent_recall', 'persona_fidelity', 'provision_completeness'] as const
type MetricId = (typeof METRIC_IDS)[number]

function formatScore(n: number): string {
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}

function SourceBadge({ source }: { source: SourceTag }) {
  const { t } = useLang()
  const map: Record<SourceTag, { label: string; cls: string }> = {
    measured: {
      label: t.benchmarks.sourceMeasured,
      cls: 'bg-ln-accent-muted text-ln-accent border-ln-border-accent',
    },
    public: {
      label: t.benchmarks.sourcePublic,
      cls: 'bg-[rgba(39,166,68,0.12)] text-ln-success border-[rgba(39,166,68,0.35)]',
    },
    not_public: {
      label: t.benchmarks.sourceNotPublic,
      cls: 'bg-[rgba(234,179,8,0.12)] text-ln-warning border-[rgba(234,179,8,0.35)]',
    },
    na: {
      label: t.benchmarks.sourceNa,
      cls: 'bg-ln-btn-bg text-ln-quaternary border-ln-border',
    },
  }
  const badge = map[source] ?? map.na
  return (
    <span
      className={`mt-1.5 inline-block rounded-btn border px-1.5 py-0.5 text-[10px] leading-none font-ui ${badge.cls}`}
    >
      {badge.label}
    </span>
  )
}

function TrendChip({ trend }: { trend: MetricTrend }) {
  const { t } = useLang()
  const map: Record<MetricTrend, { icon: typeof TrendingUp; label: string; cls: string }> = {
    up: { icon: TrendingUp, label: t.benchmarks.trendUp, cls: 'text-ln-success' },
    down: { icon: TrendingDown, label: t.benchmarks.trendDown, cls: 'text-ln-error' },
    flat: { icon: Minus, label: t.benchmarks.trendFlat, cls: 'text-ln-quaternary' },
  }
  const item = map[trend] ?? map.flat
  const Icon = item.icon
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-ui ${item.cls}`}>
      <Icon size={14} />
      {item.label}
    </span>
  )
}

function Cell({ cell }: { cell?: BenchmarkCell }) {
  if (!cell || !cell.value) return <span className="text-ln-quaternary">—</span>
  return (
    <div>
      <div className="font-ui text-ln-text">{cell.value}</div>
      <SourceBadge source={cell.source} />
    </div>
  )
}

export default function BenchmarksClient({ data }: { data: BenchmarkData | null }) {
  const { t, lang } = useLang()
  const metrics = data?.metrics ?? []
  const generatedAt = data?.generated_at ?? null

  const metricById = (id: MetricId): BenchmarkMetric | undefined => metrics.find((m) => m.id === id)

  // JSON 中的 metric id 是 snake_case（数据稳定），i18n key 是 camelCase（展示文案）
  const metaById: Record<string, { name: string; nameZh: string; desc: string }> = {
    cross_agent_recall: t.benchmarks.metric.crossAgentRecall,
    persona_fidelity: t.benchmarks.metric.personaFidelity,
    provision_completeness: t.benchmarks.metric.provisionCompleteness,
  }
  const metricMeta = (id: MetricId) => metaById[id]

  // 对比表：JSON 未提供时，用 metrics 自动生成（Moltable 实测，mem0/Zep 不适用）
  const comparisonRows =
    data && Array.isArray(data.comparison) && data.comparison.length > 0
      ? data.comparison
      : metrics.map((m) => ({
          dimension: m.id,
          moltable: { value: `${formatScore(m.score)}${m.unit ?? ''}`, source: 'measured' as SourceTag },
          mem0: { value: '—', source: 'na' as SourceTag },
          zep: { value: '—', source: 'na' as SourceTag },
        }))

  const dimName = (id: string) => {
    const meta = metaById[id]
    if (!meta) return id
    return lang === 'zh' ? meta.nameZh : meta.name
  }

  const lastRun = generatedAt
    ? new Date(generatedAt).toLocaleString(lang === 'zh' ? 'zh-CN' : 'en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null

  return (
    <div className="mx-auto max-w-7xl px-6 py-16">
      {/* ── 标题 ─────────────────────────────── */}
      <div className="max-w-3xl">
        <h1 className="text-3xl font-heading text-ln-text">
          {t.benchmarks.title}
          <span className="ml-3 text-xl font-body text-ln-quaternary">/ {t.benchmarks.titleEn}</span>
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-ln-tertiary">{t.benchmarks.subtitle}</p>
        {lastRun && (
          <p className="mt-4 text-xs text-ln-quaternary">
            {t.benchmarks.lastRun}: <span className="font-mono text-ln-secondary">{lastRun}</span>
          </p>
        )}
      </div>

      {/* ── 三基准卡片 ─────────────────────────── */}
      <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
        {METRIC_IDS.map((id) => {
          const m = metricById(id)
          const meta = metricMeta(id)
          const ran = !!m
          return (
            <div
              key={id}
              className="rounded-panel border border-ln-border bg-ln-surface p-6 transition-shadow duration-200 hover:shadow-card-hover"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-ui text-sm text-ln-secondary">
                    {lang === 'zh' ? meta.nameZh : meta.name}
                  </h3>
                  <p className="mt-0.5 text-xs text-ln-quaternary">{lang === 'zh' ? meta.name : meta.nameZh}</p>
                </div>
                {ran && m.trend && <TrendChip trend={m.trend} />}
              </div>

              {/* 当前得分（大数字） */}
              <div className="mt-6 flex items-baseline gap-1">
                {ran && m!.score != null ? (
                  <>
                    <span className="text-5xl font-heading tracking-tight text-ln-text">
                      {formatScore(m!.score)}
                    </span>
                    {m!.unit && <span className="text-xl font-ui text-ln-quaternary">{m!.unit}</span>}
                  </>
                ) : (
                  <span className="text-5xl font-heading text-ln-quaternary">—</span>
                )}
              </div>

              {/* 目标值 */}
              <div className="mt-3 flex items-center gap-2 text-xs">
                <span className="text-ln-quaternary">{t.benchmarks.target}</span>
                <span className="font-ui text-ln-secondary">
                  {ran ? `${formatScore(m!.target)}${m!.unit ?? ''}` : '—'}
                </span>
              </div>

              <p className="mt-4 border-t border-ln-border-subtle pt-4 text-xs leading-relaxed text-ln-tertiary">
                {meta.desc}
              </p>
            </div>
          )
        })}
      </div>

      {/* ── 未运行占位 ─────────────────────────── */}
      {!data && (
        <div className="mt-10 rounded-panel border border-dashed border-ln-border bg-ln-surface/60 p-12 text-center">
          <FlaskConical size={36} className="mx-auto text-ln-quaternary" strokeWidth={1.5} />
          <h2 className="mt-4 text-lg font-heading text-ln-text">{t.benchmarks.notRunTitle}</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-ln-tertiary">
            {t.benchmarks.notRunDesc}
          </p>
          <p className="mt-4 font-mono text-xs text-ln-quaternary">{t.benchmarks.notRunHint}</p>
        </div>
      )}

      {/* ── 对比表 ─────────────────────────────── */}
      {data && comparisonRows.length > 0 && (
        <div className="mt-16">
          <h2 className="text-xl font-heading text-ln-text">{t.benchmarks.comparisonTitle}</h2>
          <p className="mt-1 max-w-2xl text-sm leading-relaxed text-ln-tertiary">{t.benchmarks.comparisonSub}</p>

          <div className="mt-6 overflow-x-auto rounded-panel border border-ln-border bg-ln-surface">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-ln-border-subtle text-left">
                  <th className="px-6 py-4 font-ui text-xs text-ln-quaternary">{t.benchmarks.colDimension}</th>
                  <th className="px-6 py-4 font-ui text-xs text-ln-quaternary">{t.benchmarks.colMoltable}</th>
                  <th className="px-6 py-4 font-ui text-xs text-ln-quaternary">{t.benchmarks.colMem0}</th>
                  <th className="px-6 py-4 font-ui text-xs text-ln-quaternary">{t.benchmarks.colZep}</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map((row) => (
                  <tr
                    key={row.dimension}
                    className="border-b border-ln-border-subtle last:border-b-0"
                  >
                    <td className="px-6 py-5 align-top">
                      <div className="font-ui text-ln-secondary">{dimName(row.dimension)}</div>
                    </td>
                    <td className="px-6 py-5 align-top">
                      <Cell cell={row.moltable} />
                    </td>
                    <td className="px-6 py-5 align-top">
                      <Cell cell={row.mem0} />
                    </td>
                    <td className="px-6 py-5 align-top">
                      <Cell cell={row.zep} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-4 max-w-3xl text-xs leading-relaxed text-ln-quaternary">{t.benchmarks.dataNote}</p>
        </div>
      )}
    </div>
  )
}
