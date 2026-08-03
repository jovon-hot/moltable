# Moltable Benchmarks

Moltable 的三个专属评估基准（Sprint 3）。脚本化运行，结果写入 `results/benchmarks.json`，
`/research` 页面在构建时（`npm run build`）自动读取并展示。

## 三个维度

1. **Cross-Agent Recall（跨 Agent 记忆召回）**
   - Agent A 写入 20 条不同类别的记忆 → Agent B 用 `auto_provision` 加载 → 对每条记忆生成语义查询
   - 指标：`recall@1 ≥ 90%`、`MRR ≥ 0.85`
   - 输出 `id: "cross_agent_recall"`，`unit: "%"`

2. **Persona Fidelity（Persona 忠诚度）**
   - 创建 Persona（如「数据极客」：每次回答必须引用至少 3 个数字）→ 回答 10 个问题 → LLM-as-judge 评分
   - 指标：人工评分 `≥ 4.0/5.0`、LLM-judge 一致性 `> 85%`
   - 输出 `id: "persona_fidelity"`，`unit: "/5"`

3. **Provision Completeness（上下文加载完整性）**
   - 创建 1 用户 + 10 偏好 + 3 Persona + 2 项目 + 5 决策 → `auto_provision()` → 逐项核对
   - 指标：完整性 `= 返回项数 / 应有项数 ≥ 95%`
   - 输出 `id: "provision_completeness"`，`unit: "%"`

## 输出格式（results/benchmarks.json）

基准全部跑完后，脚本把结果写入此文件并置 `status: "completed"`。
`/research` 页面只在 `status === "completed"` 且有 metrics 时展示数据，否则显示「基准测试尚未运行」占位。

```json
{
  "status": "completed",
  "generated_at": "2026-08-19T10:00:00+08:00",
  "metrics": [
    {
      "id": "cross_agent_recall",
      "score": 92.5,
      "target": 90,
      "unit": "%",
      "trend": "up"
    },
    {
      "id": "persona_fidelity",
      "score": 4.2,
      "target": 4.0,
      "unit": "/5",
      "trend": "up"
    },
    {
      "id": "provision_completeness",
      "score": 96.0,
      "target": 95,
      "unit": "%",
      "trend": "up"
    }
  ],
  "comparison": [
    {
      "dimension": "cross_agent_recall",
      "moltable": { "value": "92.5%", "source": "measured" },
      "mem0":     { "value": "—", "source": "na" },
      "zep":      { "value": "—", "source": "na" }
    },
    {
      "dimension": "persona_fidelity",
      "moltable": { "value": "4.2/5", "source": "measured" },
      "mem0":     { "value": "—", "source": "na" },
      "zep":      { "value": "—", "source": "na" }
    },
    {
      "dimension": "provision_completeness",
      "moltable": { "value": "96.0%", "source": "measured" },
      "mem0":     { "value": "—", "source": "na" },
      "zep":      { "value": "—", "source": "na" }
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|:--|:--|:--|
| `status` | `"pending" \| "completed"` | 未跑完时保持 `pending`，页面显示占位 |
| `generated_at` | ISO 8601 或 `null` | 运行完成时间 |
| `metrics[]` | 数组 | 三基准得分。`trend`: `up` / `down` / `flat` |
| `comparison[]` | 数组 | 对比表行。`dimension` 复用 metric id；`moltable`/`mem0`/`zep` 单元格: `value`(展示字符串) + `source`: `measured`(实测) / `public`(公开) / `not_public`(未公开) / `na`(不适用) |

`comparison` 可省略或留空 —— 前端会自动用 metrics 生成对比行
（Moltable = 实测得分，mem0/Zep = 不适用）。

## 数据来源标注

- **moltable 实测**：本仓库 `benchmarks/` 脚本在干净测试账号上运行所得
- **mem0 公开**：mem0 公开发布的基准（LoCoMo / LongMemEval / BEAM），见 `docs/moltable-docs/ai-memory-benchmarks-2026.md`
- **Zep 未公开**：Zep 声称 SOTA 但未发布可复现的对比数值
