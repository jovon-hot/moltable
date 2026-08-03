# Moltable 评测基准报告

> 最后更新: 2026-08-03
> 测试环境: 生产 (moltable.ai + api.moltable.ai)
> 基准版本: v1.0

---

## 1. Cross-Agent Recall (跨Agent记忆召回)

**测试目标**: Agent A 写入记忆 → Agent B 通过 auto_provision 加载 → 语义搜索召回率

**方法**:
- Agent A 注册 → 写入 21 条记忆（7 类别 × 3 条）
- Agent B 用同步码恢复身份 + auto_provision
- 对每条记忆生成语义查询，调用 search_memory
- 计算 recall@k 和 MRR

**结果**:

| 指标 | 得分 | 目标 | 状态 |
|:--|:--|:--|:--:|
| recall@1 | **1.000** | ≥ 0.70 | ✅ |
| recall@3 | **1.000** | ≥ 0.85 | ✅ |
| recall@5 | **1.000** | ≥ 0.90 | ✅ |
| MRR | **1.000** | ≥ 0.80 | ✅ |

**分类别明细**:

| 类别 | recall@1 | 样本数 |
|:--|:--|:--|
| preference | 1.000 | 3 |
| decision | 1.000 | 3 |
| fact | 1.000 | 3 |
| project | 1.000 | 3 |
| insight | 1.000 | 3 |
| task | 1.000 | 3 |
| relationship | 1.000 | 3 |

---

## 2. Persona Fidelity (Persona 忠诚度)

**测试目标**: Persona 切换后回答是否遵循 system_prompt 设定

**方法**:
- 创建 Persona "数据极客"（要求每次回答引用 ≥3 个数字）
- 10 个标准问题
- 双重评分: 客观正则计数字数 + LLM-as-judge (DeepSeek)

**状态**: ⚠️ 脚本已完成，待运行（需配置 DEEPSEEK_API_KEY）

---

## 3. Provision Completeness (上下文加载完整性)

**测试目标**: auto_provision 是否能完整加载所有用户数据

**方法**:
- 写入 20 条记忆（10 preference + 5 decision + 5 fact）
- 创建 3 个 Persona
- 创建 2 个 Project
- auto_provision() → 检查各维度完整性

**结果**:

| 维度 | 期望 | 实际 | 完整率 |
|:--|:--|:--|:--:|
| 记忆 | ≥20 | 20 | 100% |
| Persona | 3 | 3 | 100% |
| 项目 | 2 | 2 | 100% |
| **综合** | **≥90%** | **100%** | ✅ |

---

## 竞品对比

| 基准 | Moltable | mem0 | Zep | Letta |
|:--|:--|:--|:--|:--|
| Cross-Agent Recall | **1.000** | N/A | N/A | N/A |
| Provision Complete | **100%** | ~95%¹ | N/A | N/A |
| Persona Fidelity | 待测 | N/A | N/A | N/A |
| LoCoMo | 未参与 | 92.5² | 未公开 | 见排行榜³ |
| LongMemEval | 未参与 | 94.4² | 未公开 | 见排行榜³ |

¹ mem0 数据来自其文档中的 auto-enroll 功能描述，非独立评测
² mem0 在其 GitHub README 公开的数据 (2026.06)
³ Letta 的 Letta Bench 排行榜: letta.ai/benchmark

**说明**: Cross-Agent Recall 和 Persona Fidelity 是 Moltable 独有的维度——mem0/Zep/Letta 均不支持跨 Agent 身份同步，无法参与评测。

---

## 运行方式

```bash
cd benchmarks/

# 基准 1: Cross-Agent Recall
python3 cross_agent_recall.py

# 基准 2: Persona Fidelity (需 DEEPSEEK_API_KEY)
DEEPSEEK_API_KEY=sk-xxx python3 persona_fidelity.py

# 基准 3: Provision Completeness
python3 provision_completeness.py
```

结果输出到 `benchmarks/results/`。
