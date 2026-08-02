# Moltable 产品方案 v3

> 核心理念：**iCloud for AI Identity** — 你的 AI 身份和记忆的中枢同步层。  
> 一句话：你在 Hermes 里说过的事，Claude 也知道。换台电脑，3 分钟恢复完整 AI 环境。

---

## 一、定位

| 之前（模糊） | 之后（清晰） |
|-------------|-------------|
| 记忆引擎 + 环境配置 | **身份 + 偏好 + 地图 + 同步中枢** |
| 和 mem0 抢"记忆存在哪" | **告诉 Agent 知识库在哪，记忆统一存 Moltable** |
| 16 个 MCP 工具，一半是冗余的 | **12 个 MCP 工具（8 Free + 4 Pro），每个都有明确职责** |

---

## 二、双层架构

```
┌─────────────────────────────────────────────────────────┐
│  Free · 永远免费                                          │
│  ────────────────────────────────────────                 │
│  身份          name, email, language, timezone            │
│  偏好规则      ≤50 条纯文本，auto_provision 加载            │
│  Persona 定义  ≤2 个（name, system_prompt, traits）       │
│  项目地图      knowledge_bases + tools  JSONB              │
│  跨平台同步    任何 Agent 接入即同步                        │
│                                                          │
│  8 MCP 工具 → auto_provision, list/get/create/update       │
│                project, list/get persona, ping             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Pro · ¥19/月                                            │
│  ────────────────────────────────────────                 │
│  所有 Free 功能                                           │
│  + 记忆库       10,000 条，pgvector 向量 + 全文混合搜索      │
│  + 记忆去重     语义相似 >0.9 自动合并                      │
│  + 决策记录     时间线，可追溯                              │
│  + Persona ∞    无限 Persona，多 Persona 记忆隔离           │
│  + 跨平台记忆   Claude ↔ Hermes ↔ Cursor 自动同步          │
│  + 知识文档     在线存储关键文档（钉选同步）                  │
│                                                          │
│  +4 MCP 工具  → search_memory, save_memory,               │
│                 archive_memory, search_by_tag              │
└─────────────────────────────────────────────────────────┘
```

---

## 三、记忆库 vs 知识库 · 明确边界

| | 记忆库 (Moltable) | 知识库 (外部) |
|--|-----------------|-------------|
| **存什么** | "偏好中文回复"、"决策:暂不涨价" | FOST 报表、行业 PDF、代码仓库 |
| **谁写** | Agent 自动（工作中学到的） | 用户手动 |
| **大小** | 轻量文本（每条 <1000 字） | 可 GB 级 |
| **搜索** | search_memory → pgvector 混合搜索 | Agent 按 knowledge_bases 连接 → 自己搜 |
| **存储** | Moltable pgvector | Obsidian / PG / Superset / 你的硬盘 |
| **跨平台** | ✅ 任何 Agent 都能搜 | ❌ 取决于源的可达性 |
| **Free** | 0 条 | knowledge_bases 指向即可 |
| **Pro** | 10,000 条 | knowledge_bases 指向即可 |

---

## 四、MCP 工具清单

### Free 层（8 个）

| 工具 | 职责 |
|------|------|
| `auto_provision` | 一键拉取身份 + 偏好规则 + Persona + 项目地图 |
| `list_projects` | 列出项目 + knowledge_bases + tools 配置 |
| `get_project` | 获取单个项目的完整环境配置 |
| `create_project` | 创建项目环境（PG 连接、MCP 服务器等） |
| `update_project` | 更新项目环境 |
| `list_personas` | 列出所有 Persona 定义 |
| `get_persona` | 获取 Persona 完整 system_prompt |
| `ping` | 心跳 |

### Pro 层（+4 个）

| 工具 | 职责 |
|------|------|
| `search_memory` | 混合搜索（向量 + 全文，三级回退） |
| `save_memory` | 保存记忆（语义去重） |
| `archive_memory` | 软删除记忆 |
| `search_by_tag` | 按标签搜索记忆 |

### 砍掉的工具

| 工具 | 原因 |
|------|------|
| ~~`consult_persona`~~ | 需要 LLM。Agent 端的模型更强 |
| ~~`match_persona`~~ | 同上 |
| ~~`compare_personas`~~ | 同上 |
| ~~`save_memories`~~ | 批量保存可合并到 save_memory |

---

## 五、auto_provision 返回体

```json
{
  "profile": {
    "name": "王海东",
    "email": "haidong@fost.cn",
    "language": "zh",
    "timezone": "Asia/Shanghai",
    "plan": "pro"
  },
  "rules": [
    "中文回复",
    "直接给结论，不啰嗦",
    "数据驱动决策，需要数字支撑"
  ],
  "preferences": [
    "关注资金链、成本、利润率",
    "优先方案正确性而非速度"
  ],
  "active_projects": [
    {
      "id": "...",
      "name": "FOST 经营分析",
      "description": "16站车辆检测企业数据分析",
      "persona_id": "...",
      "knowledge_bases": [
        {"type": "postgres", "host": "192.168.14.93", "port": 5432, "database": "fost", "label": "业务数据库"},
        {"type": "obsidian", "vault": "hdlib", "path": "~/Desktop/hdlib", "label": "FOST 知识库"},
        {"type": "superset", "url": "http://192.168.14.93:8088", "label": "数据可视化"},
        {"type": "mem0", "label": "旧记忆（只读）"}
      ],
      "tools": [
        {"type": "mcp", "name": "superset", "url": "http://192.168.14.93:8088/"},
        {"type": "wecom", "name": "阿福Bot"}
      ]
    }
  ],
  "available_personas": [
    {"id": "...", "name": "CFO", "type": "constructed", "description": "财务总监视角", "memory_count": 15},
    {"id": "...", "name": "CEO", "type": "constructed", "description": "总经理战略视角", "memory_count": 8}
  ],
  "core_knowledge": [
    {"content": "FOST 淄博 16 个检测站，268 员工", "category": "fact"},
    {"content": "2026 年 7 月全市份额 19.4%", "category": "fact"}
  ],
  "personas_version": 12,
  "instructions": "你现在已经加载了用户的完整上下文..."
}
```

---

## 六、技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 向量存储 | Supabase pgvector | 已有，零迁移，免费层够用 |
| 全文搜索 | PostgreSQL GIN tsvector | 已有索引，RRF 混合搜索 |
| 混合搜索 | pgvector RRF（向量 + 全文融合） | 不引入新引擎 |
| 记忆去重 | 余弦相似度 >0.9 → 自动合并 | 已有代码 |
| 嵌入模型 | 默认 trigram hash（轻量），可选 sentence-transformers | 无需 GPU |

### Graph 方案评估（基于 2025-2026 行业调研）

| 方案 | ⭐ | 适合 Moltable? | 原因 |
|------|:--:|:--:|------|
| **Cognee** | 29.6k | ⚠️ 远期可参考 | Apache 2.0，Kuzu 嵌入式图DB，v1.4.1 活跃。但引入新引擎，当前过重 |
| **mem0 Graph Memory** | 62k | ❌ | 实体链接锁在 $249/月 Pro 档——图记忆 = 高价功能，行业共识已形成 |
| **Microsoft GraphRAG** | 35k | ❌ | 需 Neo4j + LLM 大量抽取，成本高，偏企业文档 RAG 非 Agent 记忆 |
| **Zep Temporal Graph** | 4.8k | ❌ | 闭源 SaaS，$125/月起，企业级但重 |
| **Neo4j GenAI** | — | ❌ | Java 运行时，运维复杂 |
| **pg CTE 递归查询** | — | ✅ **P3** | 纯 SQL，零新依赖。Pro >100 用户时加"Graph Memory"卖点 |

**结论：当前不需要 graph。** pgvector 混合搜索（RRF 向量+全文融合）对"查我上次说的偏好"足够。Graph 是 Pro 档中期功能，用纯 SQL CTE 实现，对标 mem0 的 $249/月。**先做混合搜索，再做图记忆。**

### 渐进路线（对齐行业节奏）

```
Phase 1（现在）:  RRF 混合搜索 RPC — 向量 + 全文融合排序
Phase 2（1-2月）: 关系 + 实体标签 — memories.related_to, entities 表
                  Agent 自行声明关系（保持轻量，不做 LLM 自动抽取）
Phase 3（3-6月）: Graph Memory（Pro 档）— CTE 递归图查询
                  对标 mem0 $249/月，Moltable ¥39/月
```

### 竞品定价对比

| 方案 | Free | Pro | Enterprise |
|------|------|-----|------------|
| **mem0 Platform** | 1万 add/1千 search | $19 (5万/5千) → $249 (50万) | 定制 |
| **Zep** | 1万 credits 试用 | $125 (5万) → $375 (20万) | 定制 |
| **Letta** | 3 Agent | $20/月 | 定制 |
| **Moltable（计划）** | 身份+偏好+项目 | ¥19/月 (1万记忆) | ¥39/月 (5万+团队) |

**Moltable 差异化：** 唯一把 DID+VC 和 Agent 记忆结合的产品。比 mem0 便宜 10 倍，比 Zep 轻 100 倍。

---

## 七、用户场景全覆盖

| # | 场景 | Free | Pro |
|---|------|:--:|:--:|
| 1 | 换 AI 时自我介绍 | ✅ auto_provision | ✅ 加记忆增强 |
| 2 | Agent 忘了偏好 | ✅ rules 列表 | ✅ search_memory |
| 3 | Agent 不知道项目背景 | ✅ project 描述 | ✅ 项目关联记忆 |
| 4 | 查之前的决策 | ❌ Agent 自己搜知识库 | ✅ search_memory("决策") |
| 5 | 工作/个人切换 | ✅ get_persona | ✅ 多 Persona 记忆隔离 |
| 6 | 新电脑装 Hermes | ✅ auto_provision + 项目地图 | ✅ 加 10K 记忆同步 |
| 7 | 从 Claude 换到 Hermes | ✅ 同一身份 | ✅ 记忆 100% 同步 |
| 8 | 新项目 | ✅ create_project | ✅ 记忆关联 |
| 9 | 团队共享 | — | ✅ Team 计划 |
| 10 | 周报生成 | ✅ 项目地图 → 连 PG | ✅ search_memory 上周结论 |
| 11 | 多视角决策 | ✅ Persona 定义 | ✅ 按 Persona 查记忆 |
| 12 | 跨项目记忆隔离 | ✅ Persona 隔离 | ✅ + 项目隔离 |
| 13 | 记录决策 | ❌ | ✅ save_memory |
| 14 | AI 越来越懂你 | ✅ 偏好规则可更新 | ✅ 10K 条记忆积累 |
| 15 | 知识不丢失 | ✅ 身份不丢 | ✅ 记忆不丢 |
| 16 | 数据主权 | ✅ 导出 | ✅ 导出 |
| 17 | 跨平台一致性 | ✅ 身份一致 | ✅ 记忆一致 |

---

## 八、与现有系统的关系

| 用户已有 | 关系 |
|---------|------|
| **mem0** | 旧记忆原地保留。Agent 新记忆 → 写入 Moltable。mem0 作为 knowledge_bases 的一个只读源 |
| **Obsidian** | 知识库，不是记忆库。Moltable 存你的笔记位置，Agent 自己去搜 |
| **Notion** | 同 Obsidian |
| **PG 数据库** | 业务数据。knowledge_bases 指向，Agent 自己连 |
| **Superset / Grafana** | tools 配置指向 |

**Moltable 不做的事：**
- 不代搜外部知识库
- 不自动导入 mem0/Obsidian 全文
- 不建知识图谱
- 不跑 LLM 推理

---

## 九、Meta-Memory 层：与用户现有系统的融合

> Moltable 不替代 mem0/Obsidian/Notion。Moltable 是"目录"，知道每段知识在哪个系统里。
> 
> 类比：**mem0/Obsidian = 硬盘上的文件，Moltable = Spotlight 索引。**

### 设计原则

```
Knowledge Layer:
  Moltable 只存「索引指针」—— 标题 + 摘要(前200字) + 路径 + 内容哈希
  不存全文（除非用户付费选择"缓存到 Moltable"）

Agent 搜索时:
  search_memory("FOST Q2 财报")
  → Moltable 搜索: 自有记忆 + knowledge_pointers
  → 返回:
    - [Moltable] "FOST Q2 营收 5000 万" (置信度: 0.95)
    - [Obsidian] /vault/reports/Q2.md (摘要: "Q2 财报分析...")
    - [mem0] memory_id: abc123 (摘要: "FOST Q2...")
  → Agent 按需去对应源获取全文
```

### 数据模型（P2 新增）

```sql
-- 知识源配置
CREATE TABLE knowledge_sources (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    source_type TEXT NOT NULL,       -- 'mem0', 'obsidian', 'notion'
    source_config JSONB,              -- 连接配置
    sync_status TEXT DEFAULT 'idle',  -- 'idle','syncing','error'
    last_synced_at TIMESTAMPTZ,
    item_count INT DEFAULT 0
);

-- 轻量指针索引（不存全文）
CREATE TABLE knowledge_pointers (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    source_id UUID REFERENCES knowledge_sources(id),
    external_id TEXT,                 -- 源系统 ID
    external_path TEXT,               -- 源系统路径/URL
    title TEXT,
    snippet TEXT,                     -- 前 200 字符
    content_hash TEXT,                -- 跨源去重
    metadata JSONB,
    last_modified_at TIMESTAMPTZ
);
```

### 跨源去重

| 策略 | 实现 |
|------|------|
| **内容哈希** | MD5(title + first_200_chars) |
| **语义去重** | 向量相似度（已有 trigram hash） |
| **冲突处理** | 同一内容在 mem0 和 Obsidian 都有 → 两条都返回，标注 `duplicate_of`，Agent 选择 |

### 融合路线（P2→P3）

```
Phase 1 (当前): Agent 端多 MCP 连接
  mcp.json: {moltable, mem0, obsidian, notion}
  → Agent LLM 决定调哪个

Phase 2 (1月内): Moltable 内置 connector
  + mem0 connector（最高优先，用户已有）
  + 文件上传（MD/JSON/CSV）
  + POST /api/knowledge/connect → 同步元数据指针
  + search_memory 加 source:"federated" 选项

Phase 3 (远期): Moltable Gateway
  用户只配 Moltable → mem0/Notion/Obsidian 透明代理
  + "付费缓存" (Pro: 1000条热门知识全文)
```

### 导入导出（mem0 → Moltable）

```python
# mem0 → Moltable 迁移脚本（Pro 功能）
from mem0 import Memory
m = Memory()
for mem in m.get_all():
    requests.post("moltable.ai/api/memories", json={
        "content": mem["memory"],
        "category": "imported",
        "source": "mem0",
        "metadata": {"mem0_id": mem["id"]},
        "confidence": 0.8  # 导入记忆降置信度
    })
```

**要点：** 嵌入向量不可跨系统移植（各系统 embedding model 不同）。导入时 Moltable 重新计算向量。

---

## 十、与现有系统的关系（更新）

| 用户已有 | 关系 |
|---------|------|
| **mem0** | 旧记忆原地保留。新记忆 → Moltable。可一键迁移。mem0 作为 knowledge_sources 的一个联邦源 |
| **Obsidian** | 知识库，不是记忆库。Moltable 存路径+摘要指针，Agent 按需去搜 |
| **Notion** | 同 Obsidian |
| **PG 数据库** | 业务数据。knowledge_bases 指向，Agent 自己连 |
| **本地文件** | 文件上传 → 提取文本 → 指针索引 |

---

## 十一、实施计划

| 阶段 | 内容 | 预估 |
|:--:|------|:--:|
| **P0** | Free 层精简：砍掉记忆 CRUD MCP 工具，保留 8 个核心工具。quota 门控 | 2h |
| **P1** | Pro 记忆库：RRF 混合搜索 RPC + 语义去重 + Pro 配额 | 4h |
| **P2** | Meta-Memory：knowledge_sources + pointers 表，mem0 connector，文件上传 | 6h |
| **P3** | 计费集成：Stripe + plan 升级 + 免费额度 | 2h |
| **P4** | Dashboard：记忆管理 + 知识源管理 + Persona 记忆隔离 UI | 4h |
| **P5** | Graph Memory（Pro 档）：CTE 递归查询，Agent 声明关系 | 4h |

---

## 十二、一句话

```
Moltable = iCloud for AI Identity

Free:  你的 AI 认识你是谁、偏好什么、项目在哪
Pro:   10,000 条跨平台记忆，任何 Agent 都能存取
       搜"我上次对摩托车成本的结论是什么？"→ 秒回
```
