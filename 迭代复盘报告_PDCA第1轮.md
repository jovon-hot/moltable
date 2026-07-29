# Moltable · PDCA 循环复盘报告 — 第 1 轮

> 日期：2026-06-18 | 版本：V1.0 | 复盘轮次：第 1 轮

---

## 一、本轮 PDCA 投入产出总览

### 1.1 周期与范围

| 维度 | 内容 |
|------|------|
| **周期** | 2026-06-16 ~ 2026-06-18（约 2.5 天） |
| **阶段** | Plan → Do (Phase 0: 安全修复 + Phase 1: 数据持久化 + Phase 2: MCP 端点) → Check |
| **涉及文件** | 13 个源文件（审查）、20+ 源文件（修改） |
| **核心模块** | 认证、记忆 CRUD、MCP JSON-RPC、Persona 管理、Provision |

### 1.2 Phase 0：安全修复（6 项）

| ID | 修复项 | 状态 | 说明 |
|----|--------|------|------|
| F01 | CORS 白名单 | ✅ Done | `ALLOWED_ORIGINS` 环境变量管理，拒绝通配符 |
| F02 | API Key SHA-256 哈希存储 | ✅ Done | 原始 Key 仅创建时返回一次 |
| F03 | Pydantic 输入校验 | ✅ Done | 所有 route 模块增加 min_length/max_length/pattern 校验 |
| F04 | 速率限制 | ✅ Done | slowapi 集成，按端点分级限流（memory: 60/min, MCP: 300/min） |
| F05 | HTTP 安全头 | ✅ Done | `X-Content-Type-Options`, `X-Frame-Options`, `HSTS` |
| F06 | Profiles 无依赖崩溃 | ✅ Done | `/api/auth/me` 无 crash，catch Exception |

### 1.3 Phase 1：数据持久化

| ID | 功能 | 状态 | 说明 |
|----|------|------|------|
| P01 | Supabase pgvector Repository 层 | ✅ Done | `SupabaseMemoryRepository` 实现完整 CRUD + 语义搜索 |
| P02 | Repository 抽象基类 | ✅ Done | `Repository` ABC 定义 8 个接口方法 |
| P03 | 内存 VectorStore 回退 | ✅ Done | Supabase 离线时自动降级到内存存储 |
| P04 | pgvector RPC (`match_memories`) | ✅ Done | `migration.sql` 定义，支持 category+threshold 过滤 |
| P05 | HNSW 向量索引 | ✅ Done | `schema.sql` 包含 HNSW 索引创建 |
| P06 | RLS 行级安全策略 | ✅ Done | 5 张表全部启用 RLS |

### 1.4 Phase 2：MCP JSON-RPC 2.0

| ID | 功能 | 状态 | 说明 |
|----|------|------|------|
| M01 | JSON-RPC 2.0 端点 `/mcp` | ✅ Done | 支持单条 + 批量请求 |
| M02 | `initialize` 协议协商 | ✅ Done | 返回 capabilities、protocolVersion |
| M03 | `ping` 心跳 | ✅ Done | 无需认证 |
| M04 | `tools/list` 工具列表 | ✅ Done | 6 个工具完整定义 |
| M05 | `tools/call` 工具调用 | ✅ Done | `search_memory`, `save_memory`, `get_persona`, `list_personas`, `auto_provision`, `ping` |
| M06 | `.well-known/mcp` 发现端点 | ✅ Done | MCP 规范兼容的发现接口 |
| M07 | X-API-Key 认证解析 | ✅ Done | `_resolve_api_key` 支持 Key 哈希匹配 |
| M08 | 标准错误码 | ✅ Done | -32700 ~ -32002 完整映射 |
| M09 | 59 个测试用例全部通过 | ✅ Done | 5 个测试文件覆盖 |
| M10 | MCP/Provision 零测试 | ⚠️ **缺失** | 无 `test_mcp.py`, 无 `test_provision.py` |

---

## 二、代码质量统计

### 2.1 源文件全景（23 个 Python 文件）

| 模块 | 文件数 | 说明 |
|------|--------|------|
| `routes/` | 6 | auth, memories, personas, provision, mcp, `__init__` |
| `services/` | 4 | vector_store, embedding, repository, `__init__` |
| `repositories/` | 1 | memory_repo |
| `tests/` | 7 | 5 个测试 + conftest + `__init__` |
| 入口文件 | 3 | main.py, app_state.py, mcp_server.py |

### 2.2 测试覆盖率

| 测试文件 | 模块 | 测试数 | Mock 依赖 | 状态 |
|---------|------|--------|-----------|------|
| `test_vector_store.py` | VectorStore | 14 | 无 | ✅ |
| `test_memory_repo.py` | SupabaseMemoryRepository | 8 | mock_supabase | ✅ |
| `test_memories_api.py` | Memories API | 12 | mock_supabase + mock_embed | ✅ |
| `test_personas_api.py` | Personas API | 5 | mock_supabase | ✅ |
| `test_auth_api.py` | Auth API | 7 | mock_supabase | ✅ |
| `test_embedding.py` | Embedding Service | 5 | mock OpenAI | ✅ |
| **合计** | **6 个测试文件** | **51** | — | ✅ |

> ⚠️ **MCP 端点 (`routes/mcp.py`) 零测试覆盖**
> ⚠️ **Provision 端点 (`routes/provision.py`) 零测试覆盖**

### 2.3 已知严重问题（6 项）

| # | 严重性 | 问题 | 位置 | 影响 |
|---|--------|------|------|------|
| S01 | 🔴 致命 | `schema.sql` 中 `match_memories` RPC 缺少 `match_category` 和 `match_threshold` 参数 | `schema.sql:120-152` | SQL 与 `memory_repo.py` 调用签名不一致 |
| S02 | 🔴 致命 | `migration.sql` 中 embedding 维度是 `vector(1024)`，但 `embedding.py` 返回 `4096` 维 | `migration.sql:9`, `embedding.py:39` | pgvector 维度不匹配导致 RPC 崩溃 |
| S03 | 🔴 致命 | `schema.sql` 定义的 embedding 维度是 `vector(1536)`，与 `embedding.py` 的 `4096` 不一致 | `schema.sql:71`, `embedding.py:39` | 同维度不匹配问题 |
| S04 | 🔴 致命 | DeepSeek 的 `deepseek-chat` 模型是否真正支持 Embedding 未经验证 | `embedding.py:22` | 可能根本跑不通 |
| S05 | 🔴 致命 | `provision.py` 中的 `auto_provision` 如果 `user.data` 为 `None` 会引发 `AttributeError` | `provision.py:21,86-104` | 生产环境可能 500 |
| S06 | 🔴 致命 | `supabase.auth.get_user()` 需要 Supabase Auth 配置，本地/Supabase URL 缺失时直接崩溃 | `auth.py:29` | 双因素认证缺失 |

### 2.4 已知改进项（11 项）

| # | 改进 | 位置 | 说明 |
|---|------|------|------|
| I01 | `mcp_server.py` 与 `mcp.py` 代码重复 | 两套 MCP 实现 | `mcp_server.py` 是 old stdio 模式，未集成新 JSON-RPC |
| I02 | 双 MCP 入口（`main.py` 和 `mcp_server.py`） | 两套入口 | 运维混乱，用户不知启动哪个 |
| I03 | 无 `consult_persona` MCP 工具 | `mcp.py` | PRD 定义的 P0 功能未实现 |
| I04 | Persona API 缺 `GET /{id}`, `PUT /{id}`, `DELETE /{id}` | `personas.py` | 只有 list + create |
| I05 | Web 前端零开发 | `web/` 目录 | PRD 定义的 F07（记忆管理后台）未启动 |
| I06 | Chrome 插件零开发 | `extension/` 目录 | PRD 定义的 F15 未启动 |
| I07 | Hermes Skill SKILL.md 文件存在但内容待验证 | `skills/moltable/SKILL.md` | 未端到端验证 |
| I08 | `mcp_server.py` 使用 httpx 但不在 requirements.txt | `requirements.txt` | 部署时会失败 |
| I09 | `embedding.py` 的 `embed_dim()` 返回 `4096` 但实际 DeepSeek 模型维度未知 | `embedding.py:39` | 硬编码可能错误 |
| I10 | 无 API 版本化策略 | Routes | `/api/` 路径有但无版本号 |
| I11 | 无 CI/CD 配置 | 项目根 | 无 GitHub Actions/Dockerfile |

---

## 三、核心成就总结

### 3.1 做对的事

1. **安全底盘扎实**：CORS + 输入校验 + 速率限制 + 安全头 + API Key 哈希，5 层安全防护到位
2. **数据层弹性好**：SupabaseRepository + VectorStore 降级机制，无依赖时也可运行测试
3. **MCP 协议实现完整**：JSON-RPC 2.0 规范实现，6 个工具，标准错误码，批量请求支持
4. **测试基础好**：51 个测试，全部 mock 化，零外部依赖可运行
5. **架构分离清晰**：Routes → Services → Repositories 三层划分明确
6. **Repository 设计模式**：ABC 抽象基类 + 多实现（Supabase / In-memory）可切换

### 3.2 需要警惕的问题

1. **SQL Schema 与代码严重脱节**：`schema.sql`、`migration.sql`、`embedding.py` 三个文件对 embedding 维度的定义互不一致（1536 / 1024 / 4096）
2. **MCP 端点零测试覆盖**：最核心的 `routes/mcp.py`（647 行）没有任何单元/集成测试
3. **Provision 端点零测试覆盖**：`routes/provision.py`（111 行）也没有测试
4. **DeepSeek Embedding 可行性未验证**：依赖未知模型能力
5. **双 MCP 入口**：`mcp_server.py`（旧 stdio）和 `mcp.py`（新 HTTP）并行，运维混乱

---

## 四、下一轮 PDCA 优先级建议

### P0 — 本轮不可跳过（安全+核心功能保障）

| ID | 任务 | 原因 | 预估工时 |
|----|------|------|----------|
| P0-01 | 🔴 统一所有 embedding 维度定义 | 修复致命 Schema-Code 不一致 | 0.5h |
| P0-02 | 🔴 验证 DeepSeek Embedding 可行性或切换到 OpenAI text-embedding-3-small | 核心功能依赖，不可用即不可用 | 1h |
| P0-03 | 🔴 编写 MCP 端到端测试（`test_mcp.py`） | 最核心代码零覆盖 | 3h |
| P0-04 | 🔴 编写 Provision 端到端测试（`test_provision.py`） | 核心业务逻辑零覆盖 | 1.5h |
| P0-05 | 🔴 修复 `provision.py` 中 `user.data` 可能为 None 的崩溃 | 生产 500 隐患 | 0.5h |
| P0-06 | 🔴 统一 MCP 入口（废弃 `mcp_server.py` 或明确双入口职责） | 运维确定性 | 0.5h |

### P1 — 完善 MVP 功能

| ID | 任务 | 原因 | 预估工时 |
|----|------|------|----------|
| P1-01 | 🟡 实现 MCP `consult_persona` 工具 | PRD Phase 2 P0 功能 | 3h |
| P1-02 | 🟡 Persona API 补全 CRUD（GET/PUT/DELETE by id） | RESTful 完整性 | 2h |
| P1-03 | 🟡 `mcp_server.py` 的 httpx 加入 requirements.txt | 部署必现 | 0.5h |
| P1-04 | 🟡 添加 `setup.cfg` / `pyproject.toml` 基础项目配置 | 包管理规范 | 1h |
| P1-05 | 🟡 运行一次完整的 `pytest` 并修复所有失败 | 质量门禁 | 1h |
| P1-06 | 🟡 添加 `Dockerfile` 和 `docker-compose.yml` | 部署基础 | 2h |

### P2 — 功能增强与质量提升

| ID | 任务 | 原因 | 预估工时 |
|----|------|------|----------|
| P2-01 | 🟢 记忆管理后台（Web 前端） | PRD F07，用户可见 | 8h+ |
| P2-02 | 🟢 Chrome 浏览器插件 | PRD F15，入口扩展 | 8h+ |
| P2-03 | 🟢 CI/CD（GitHub Actions） | 自动化质量保障 | 3h |
| P2-04 | 🟢 API 版本化（`/api/v1/...`） | 向后兼容 | 1h |
| P2-05 | 🟢 生产部署就绪（Railway/Render 配置） | 上线准备 | 3h |
| P2-06 | 🟢 Hermes Skill 端到端验证 | 首个实际接入验证 | 2h |

### 优先级矩阵

```
高影响 + 高风险 → P0 （立即做）
  ├─ 维度不一致修复
  ├─ MCP/Provision 测试补齐
  ├─ Embedding 可行性验证
  └─ 入口统一

高影响 + 低风险 → P1 （本轮做）
  ├─ consult_persona 工具
  ├─ Persona CRUD 补齐
  ├─ pytest 修复
  └─ 部署配置

低影响 + 高风险 → P2 （关注）
  ├─ CI/CD 管线
  └─ 文档完善

低影响 + 低风险 → 后续轮次
  ├─ 前端开发
  ├─ Chrome 插件
  └─ 更多集成测试
```

---

## 五、风险评估

### 5.1 高概率高危风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| DeepSeek 不支持 Embedding | 高⚠️ | 核心功能瘫痪 | 立即验证；准备 OpenAI key 作为备用 |
| pgvector 维度不匹配导致 SQL 运行失败 | 高⚠️ | 数据库不可用 | 统一所有维度定义并运行 SQL |
| 双 MCP 入口对 Hermes Skill 造成混淆 | 中⚠️ | 接入失败 | 统一入口或明确职责 |
| auto_provision 在生产环境 500 | 中⚠️ | 用户无法登录 | 添加 `user.data` None 检查 |

### 5.2 中概率中风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| MCP 协议实现有规范偏差 | 中 | Agent 连接失败 | 补全 MCP 测试 |
| Supabase 认证（get_user）缺少双因素 | 中 | 安全漏洞 | 添加 API Key 备份认证 |
| 测试 mock 与实际行为脱节 | 中 | 误报绿色 | 添加 1-2 个真实 Supabase 集成测试 |

---

## 六、更新项目文档

### 6.1 修复 PRD 状态标记

已更新以下文档：
- ✅ 新增本复盘报告：`迭代复盘报告_PDCA第1轮.md`
- 待更新：
  - `PRD_产品需求文档.md` — 将状态从"草案"更新为"开发中"
  - `MVP开发计划.md` — 标记已完成功能
  - `技术架构设计.md` — 确认 embedding 维度一致性

### 6.2 项目状态看板

```
Phase 0 (安全):    6/6 ✅ (100%)
Phase 1 (持久化):  6/6 ✅ (100%)
Phase 2 (MCP):     8/10 ⚠️ (80%)  [缺 test_mcp, test_provision]
Phase 2 (Persona): 2/5 ⚠️ (40%)   [仅 list/create]
Web 前端:          0/1 ❌ (0%)
Chrome 插件:       0/1 ❌ (0%)
安全扫描:          5/5 ✅ (100%)
测试覆盖(MCP+Provision): 0/2 ❌ (0%)
```

---

## 七、下一轮行动清单

### 立即行动（今天）

| 顺序 | 任务 | 负责人 |
|------|------|--------|
| 1 | 验证 DeepSeek Embedding（写一个小脚本调 `embed("hello")`） | 开发者 |
| 2 | 统一 `embedding.py:39` 的维度为真实值（1536 或 4096 或 1024） | 开发者 |
| 3 | 统一 `schema.sql:71` + `migration.sql:9` 的 embedding 类型 | 开发者 |
| 4 | 编写 `test_mcp.py`（JSON-RPC 端到端测试） | 开发者 |
| 5 | 编写 `test_provision.py`（auto_provision 逻辑测试） | 开发者 |

### 本周完成

| 顺序 | 任务 | 预估工时 |
|------|------|----------|
| 6 | 修复 `provision.py` user.data None 崩溃 | 0.5h |
| 7 | 统一 MCP 入口 | 0.5h |
| 8 | 运行完整 pytest 并修复 | 1h |
| 9 | 实现 `consult_persona` 工具 | 3h |
| 10 | 补全 Persona CRUD | 2h |
| 11 | 添加 Dockerfile | 2h |

---

> **核心结论**：第 1 轮 PDCA 完成了 MVP 功能开发和安全加固的"硬骨架"，但在 Schema-Code 一致性和核心路径的测试覆盖上存在致命盲区。下一轮必须以 **验证 Embedding → 修复维度 → 补齐测试** 为绝对优先，在此基础上再推进功能增强。
