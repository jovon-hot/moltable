# 环境版本管理方案调研报告 — 跨 Agent 跨设备的环境一致性

> 为 Moltable 的跨 Agent 环境同步功能提供技术方案。目标场景：用户在 Hermes (Mac, Python 3.11) 创建项目环境，切换到 Claude Desktop (Linux, Python 3.10) 时如何保证环境一致。
> 调研日期：2026-08-03 · 调研人：Hermes 子代理

---

## 0. 结论速览（TL;DR）

1. **mem0 / Letta / LangMem 都没有环境版本管理** —— 它们管理"记忆"（facts/preferences/会话状态），不管理"环境"（Python 版本、依赖、工具链、MCP server 版本）。这是 Moltable 的空白地带，也正是差异化的机会。
2. **Moltable `projects` 表的 `knowledge_bases` / `tools` JSONB 是"环境描述"（declarative intent），不是"环境快照"（executable state）**。业界成熟的思路是分层：描述（manifest）→ 锁定（lock file）→ 映像（image/derivation）。Moltable 应补齐后两层。
3. **业界主流的四类方案**：Docker 镜像（最重、最全）、Nix/Devbox（最可复现、最陡峭）、`pip freeze`/requirements.txt（最轻、跨平台最差）、Poetry/Pipenv/**uv lock**（锁文件、跨平台最优解）。2025-2026 的收敛趋势是 **uv**（`uv.lock` 是通用锁文件，一个文件覆盖 Mac ARM + Linux x86）。
4. **跨平台（Mac ARM → Linux x86）的本质问题**：二进制 wheel 的平台标签（`macosx_11_0_arm64` vs `manylinux_2_17_x86_64`）不同 → **锁文件必须按平台标记区分**，`pip freeze` 做不到（它是当前环境的快照，不是多平台锁定），uv/Poetry 的 lock 可以。
5. **DevContainer 模式对 Moltable 部分适用**：它是"容器即开发环境"的标准（`devcontainer.json` + features + lifecycle scripts），VS Code/Codespaces/Gitpod 通用。但对 Claude Desktop 这类桌面 Agent 不直接适用（Agent 跑在宿主机上），更适合作为"完整快照"层（Phase 3）的可选能力。
6. **MCP 工具版本管理已有官方答案**：MCP Registry（server.json + semver + packages[] 版本），客户端配置里 pin 版本（npx pkg@x.y.z / uvx pkg==x.y.z / pip install pkg==x.y.z）。Moltable 的 `tools` JSONB 应升级为带版本的结构化条目。
7. **建议方案（分阶段）**：
   - **MVP（现在）**：`projects` 增加 `env_manifest` JSONB + `version` 字段，快照式更新（append-only），tools 条目带 `type/identifier/version`；提供 `snapshot_project` / `restore_project` MCP 工具。
   - **Phase 2（锁定）**：以 **uv** 为规范工具（`requires-python` + `uv.lock` 内容入库），restore 时落盘 + `uv sync`，天然跨 Mac ARM / Linux x86。
   - **Phase 3（映像）**：可选 devcontainer.json / Dockerfile / devbox.json+lock 作为"完整快照"层，按需生成，不强制。

---

## 1. 竞品/同类项目调研：mem0、Letta、LangMem 有没有环境版本管理？

**结论：没有。它们全部聚焦于"记忆"而非"环境"。**

### 1.1 mem0（58K+ ⭐，通用记忆层）
- 定位：LLM 应用的记忆层。核心是 `add/search/update` 记忆条目，LLM 从对话中抽取 facts/preferences/events，存入向量库（Qdrant/pgvector 等）。
- 抽象层级：`user_id / agent_id / run_id / session_id` —— 全是"谁在记"，没有"在什么环境里记"。
- 与环境的交集：仅限 `metadata` 字段（用户自己塞 `env` 之类），无版本、无快照、无锁文件。
- 结论：**mem0 不解决环境一致性**。它的官方文档从没提过 Python 版本/依赖/MCP server 版本管理。

### 1.2 Letta（原 MemGPT）
- 定位：Agent 操作系统 / 显式记忆管理平台（server + memory blocks + archival memory）。
- 有版本概念，但那是 **agent state / 会话 checkpoint**（agent 保存、恢复、fork），不是运行时环境（解释器、依赖、工具链）。
- Letta server 本身用 Docker 部署，但那是"Letta 怎么跑"，不是"用户的 agent 环境怎么同步"。
- 结论：**Letta 有 state versioning，无 environment versioning**。它管"记忆内容的状态"，Moltable 管"干活环境的版本"。

### 1.3 LangMem（LangChain 系）
- 定位：LangGraph 的记忆组件，语义/情景/程序性记忆三件套。
- 与版本最接近的是 **procedural memory**（技能/工作流的记忆），但它存的是"如何做"的文本/代码片段，不是可执行的依赖锁定。
- 结论：**无环境版本管理**。

### 1.4 对 Moltable 的启示
- "记忆"赛道已经拥挤（mem0/Letta/Zep/LangMem/Cognee），且**没人做环境同步** —— Moltable V3 定位（环境同步层）成立，且调研印证了这一点。
- Moltable 不应学它们存"对话事实"，而应存"环境的可执行描述"：**manifest（声明）+ lock（锁定）+ 可选 image（映像）**。这正是传统 DevOps 三十年沉淀的答案。

---

## 2. 业界方案全景：四类环境复现技术对比

| 方案 | 复现粒度 | 跨平台 (Mac ARM→Linux x86) | 用户心智成本 | 适用场景 | 代表 |
|---|---|---|---|---|---|
| **requirements.txt / pip freeze** | Python 依赖（顶层 or 全锁定） | ❌ 差：pip freeze 是当前环境快照，绑定当前平台 wheel | 低 | 简单脚本、快速共享 | pip |
| **Poetry / Pipenv lock** | Python 依赖 + 锁定 | ⚠️ 中：poetry.lock 按环境生成，多平台需分环境 lock；PEP 751 正在统一 | 中 | Python 项目 | poetry |
| **uv（uv.lock）** | Python 版本 + 依赖 + 通用锁 | ✅ 好：uv.lock 是**多平台通用锁文件**（environment markers），一份锁 Mac ARM/Linux x86 通吃 | 低-中（uv 极快） | **2025-2026 收敛主流** | Astral uv |
| **Conda environment.yml** | Python + 原生库（C/CUDA） | ✅ 好（conda-forge 多平台） | 中 | 数据科学 | conda |
| **Docker 镜像** | 整个操作系统 + 全部依赖 | ✅ 好（多架构 build，但镜像大、启动重） | 中（写 Dockerfile） | 服务部署、复杂环境 | Docker |
| **DevContainer** | 容器 + dev 工具链 + features | ✅ 好（container image 多架构） | 中 | **开发环境**（VS Code/Codespaces/Gitpod） | containers.dev |
| **Nix / Devbox** | 逐字节可复现（hash 锁定一切） | ✅ 好（Nixpkgs 全平台） | **高**（Nix 语言学习曲线） | 极致复现、CI | Nix, Jetify Devbox |
| **uv + .python-version** | Python 解释器版本 | ✅ uv 自动下载对应平台解释器 | 低 | 与 uv.lock 配合 | uv |

### 2.1 关键判断：为什么选 **uv** 作为核心推荐

1. **`uv.lock` 是通用（universal）锁文件**：同一份 lock 内用 PEP 508 environment markers 区分平台（`sys_platform == 'darwin' and platform_machine == 'arm64'` vs `sys_platform == 'linux' and platform_machine == 'x86_64'`），**一份文件锁定 Mac ARM 和 Linux x86 两套 wheel**。这是 `pip freeze` 永远做不到的 —— `pip freeze` 只输出"当前这台机器装了什么"，换平台即失效。
2. **`requires-python` 锁解释器**：`pyproject.toml` 里声明 `requires-python = ">=3.10"` + `.python-version` 文件 pin 具体版本；`uv sync` 在目标机器上**自动下载对应平台的 Python 解释器**。Hermes (Python 3.11) → Claude Desktop (Python 3.10) 场景：lock 里声明 3.10–3.11 兼容范围，两边的解释器都由 uv 拉取，行为一致。
3. **极快（Rust 实现）**，`uv sync` 冷缓存几秒级，用户"3 分钟恢复环境"的承诺可兑现。
4. **生态收敛**：PEP 751（通用 lock 文件格式）2025 年进入 provisional，pip/uv 都朝这个方向走；uv 已成为 2025-2026 Python 包管理的默认答案（fastapi/torch 等官方文档均转向 uv）。
5. **可以导出**：`uv export` 可生成 requirements.txt（给不使用 uv 的机器兜底）。

> ⚠️ `pip freeze` 的正确定位：它是**快照**不是**锁定**。快照=这台机器当前状态（含平台特定版本），锁定=声明可跨平台复现的版本集。Moltable 要的是后者。

### 2.2 Nix / Devbox 的角色
- **Nix**：逐字节复现（cryptographic hash 锁定所有输入），最强但学习曲线最陡，普通用户（Moltable 的目标用户是"换台电脑 3 分钟恢复"的个人）不会写 Nix。
- **Devbox**（Jetify）：Nix 的友好封装，`devbox.json`（声明包）+ `devbox.lock`（锁定）→ `devbox shell`。比裸 Nix 平易得多，但仍要求用户安装 Devbox。
- **Moltable 的定位**：Nix/Devbox 适合作为 Phase 3 的可选"极致复现"层，**不是 MVP**。MVP 用户要的是"快、准、零学习成本"。

### 2.3 Docker / DevContainer 的角色
- **Docker**：环境一致性的"重武器"。但用户场景是**本地桌面 Agent（Hermes on Mac、Claude Desktop on Linux）**，Agent 跑在宿主机上直接调工具，把整个环境装进容器意味着 Agent 也要容器化 —— 对 Hermes/Claude Desktop 都不现实（Claude Desktop 不跑在容器里）。
- **DevContainer**（containers.dev 标准）：`devcontainer.json` = image/dockerfile + features（预置工具） + lifecycle scripts（postCreateCommand 等）。VS Code/Codespaces/Gitpod 通用。
  - **适用性判断**：**部分适用**。对"开发类项目"（用户在项目里写代码），Moltable 可以**为项目生成一个 `devcontainer.json` 并存为环境快照的"容器视图"**，用户在有 VS Code/Codespaces 的设备上直接打开。但对"Agent 工具类项目"（MCP servers、脚本、数据管道），容器不是 Agent 的执行环境，价值有限。
  - **结论**：DevContainer 作为 Phase 3 的**可选生成物**（"export as devcontainer"），不做为同步主路径。

### 2.4 Conda 的角色
- 强在原生库（CUDA、BLAS 等）。Moltable 的用户（Agent 环境）绝大多数是纯 Python + MCP server + 少量 CLI 工具，Conda 的收益不大、安装重。**不作为推荐，但 manifest 里保留 `conda` 作为 tool 类型之一**（表示"这个项目用 environment.yml"）。

---

## 3. 跨平台兼容性（Mac ARM → Linux x86）的工程细节

### 3.1 Python wheel 平台标签
- wheel 文件名编码 `{python}-{abi}-{platform}`，例如：
  - `torch-2.5.1-cp311-cp311-macosx_11_0_arm64.whl`（Mac ARM）
  - `torch-2.5.1-cp311-cp311-manylinux_2_17_x86_64.whl`（Linux x86）
- **含义**：同一版本号，不同平台的 wheel 是**不同文件**（不同 hash）。所以：
  - `pip freeze` 在 Mac 上锁出的是 macosx 版本的 hash，拿到 Linux 上 `pip install -r` 会失败或装错。
  - **只有"按平台标记的通用锁文件"（uv.lock / PEP 751）能跨平台**：锁文件里同一个包可以有多条记录，各带 `markers`，安装器按当前平台选。
- **对 Moltable 的硬性要求**：**环境锁必须存通用锁（uv.lock 或 PEP 751 格式），绝不存 `pip freeze` 的输出**。

### 3.2 Python 解释器版本
- `requires-python` 声明兼容范围；`.python-version` 或 `uv python pin 3.11` 锁定具体版本。
- uv 在目标机器自动下载匹配平台 + 架构的解释器（`python-build-standalone` 覆盖 macos-arm64 / linux-x86_64 等）。→ Moltable 存"python 版本约束"，restore 侧交给 uv 落地。

### 3.3 非 Python 依赖（Node、Go、系统库）
- 跨平台二进制工具（如 `node@20`、`ripgrep`、`protoc`）无法用 Python lock 表达 → 需要 Devbox/Nix/容器层。
- **MVP 处理**：manifest 中 `tools` 条目声明 `type: "system"` + `package: "node@20"` + `source: "devbox|brew|apt"`，restore 时生成对应平台的安装提示或脚本；Phase 3 用 devbox.json/容器接管。

### 3.4 实操建议（写在 manifest 规范里）
```
env_manifest:
  schema_version: "1"
  python:
    requires: ">=3.10,<3.12"     # uv 用 requires-python
    pinned: "3.11.15"             # 可选：精确解释器版本
  lock:                            # 二选一：
    type: "uv"                     # 推荐
    content: "<uv.lock 全文>"      # 或存为附件/blob
    # 或 type: "pep751"
  tools: [...]                     # MCP server + CLI 工具，见 §5
  knowledge_bases: [...]           # 保持现有结构
```

---

## 4. Python 依赖锁定方案对比（pip freeze vs Poetry vs uv）

| 维度 | pip freeze + requirements.txt | pip-tools (requirements.in) | Poetry (poetry.lock) | **uv (uv.lock)** |
|---|---|---|---|---|
| 锁文件 | 无原生概念，freeze 输出即锁 | requirements.txt（编译生成） | poetry.lock | uv.lock |
| 跨平台 | ❌ 单平台快照 | ⚠️ 单平台 | ⚠️ 按环境 | ✅ 通用锁（markers） |
| 顶层依赖 vs 全锁定 | 只有全锁定 | 声明 + 锁定分离 ✅ | 声明 + 锁定分离 ✅ | 声明 + 锁定分离 ✅ |
| 解释器管理 | ❌ | ❌ | ⚠️ 有限 | ✅ 自动下载 |
| 速度 | 慢 | 慢 | 中 | **极快** |
| 多环境 (dev/prod) | ❌ | ⚠️ | ✅ | ✅ |
| 2026 状态 | 存量主力 | 存量 | 存量 | **增量主流** |

**结论**：MVP 兼容三种输入（用户可能已有任何一种），**但 Moltable 官方推荐的锁定格式是 `uv.lock`**。restore 侧：有 uv → `uv sync`；无 uv → 从 uv.lock 导出 requirements.txt（`uv export`）。

---

## 5. MCP 工具版本管理

### 5.1 官方机制（已成熟）
- **MCP Registry**（registry.modelcontextprotocol.io，Anthropic 主导、社区驱动，preview 中）：
  - 每个 server 发布时必须有 `server.json`：`name`、`version`（**强制 semver 风格，发布后不可变**）、`packages[]`（registryType: npm/pypi/nuget/… + identifier + **version** + transport）。
  - **版本号必须是唯一的**，registry 拒绝版本区间（`^1.2.3` 等）。
- **客户端 pin 版本的方式**（Moltable 的 tools 条目要能表达这些）：
  - npm 系（Claude Code / npx）：`npx -y @modelcontextprotocol/server-xxx@1.2.3`
  - Python 系（Hermes / uvx）：`uvx --from mcp-server-xxx==1.2.3 mcp-server-xxx`
  - pip：`pip install mcp-server-xxx==1.2.3`
  - 远程（streamable-http）：URL + `X-MCP-Protocol-Version` 头；server.json 建议 version 与 API 版本对齐

### 5.2 Moltable `tools` JSONB 升级建议
现在 `tools` 是自由 JSON 数组（项目里实际只存了描述）。升级为**结构化条目**：

```json
{
  "name": "github",
  "type": "mcp",                    // mcp | cli | http | skill | python
  "package": {
    "registry": "npm",              // npm | pypi | uvx | github | system
    "identifier": "@modelcontextprotocol/server-github",
    "version": "1.2.3",             // 精确 pin
    "pin_strategy": "exact"         // exact | range | latest
  },
  "transport": { "type": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github@1.2.3"] },
  "config": { ... },                // 非敏感配置
  "secrets_ref": "kv:github-token"  // 敏感配置 → 加密引用，不存明文（对齐 Moltable 现有 secrets 处理）
}
```

- **snapshot 语义**：restore 时按 `registry+identifier+version` 幂等安装；`version` 为空 = "取该设备上最新"（显式允许漂移）。
- **依赖关系**：MCP server 本身可能依赖 Python 包 → 该 server 的 Python 依赖应并入项目 lock（uv 项目里 `uv add mcp-server-github` 即可统一管理）。

---

## 6. 给 Moltable 的分阶段落地方案

### Phase 0 / MVP（现在就能做，纯 schema + 工具扩展）

**目标**：把"描述"升级为"可比较、可回滚的版本化快照"，零新依赖。

1. **`projects` 表扩展**（向后兼容，旧行 `env_manifest` 为 NULL）：
   ```sql
   alter table projects add column if not exists env_manifest jsonb default null;
   alter table projects add column if not exists version int not null default 1;
   alter table projects add column if not exists manifest_sha text default null;  -- 内容哈希，用于变更检测
   ```
2. **新增 `project_snapshots` 表**（append-only，回滚支持）：
   ```sql
   create table project_snapshots (
     id uuid primary key default gen_random_uuid(),
     project_id uuid references projects(id) on delete cascade,
     version int not null,
     knowledge_bases jsonb not null,
     tools jsonb not null,
     env_manifest jsonb,
     created_at timestamptz default now(),
     created_by text default 'agent',
     note text
   );
   ```
3. **`update_project` 语义变更**：写入时计算 `manifest_sha`，与旧值不同 → `version+1` + 自动落一条 snapshot（保留最近 N=50 条）。
4. **新 MCP 工具**（或扩展现有工具，注意 14 工具上限的权衡）：
   - `snapshot_project(project_id, note?)` — 手动打点
   - `get_project_versions(project_id)` — 列出历史版本 + diff 摘要
   - `restore_project(project_id, version?)` — 把指定版本写回（并生成新的 snapshot 便于撤销）
   - `diff_project(project_id, target_env?)` — 对比"项目声明环境"与"当前设备实际环境"（见 6.4 指纹）
5. **tools 条目结构化**（§5.2 的 JSON 形状），旧条目自动迁移：无结构 → `{name, type:"unknown"}`。

### Phase 2 / 锁定（1-2 个迭代后）

**目标**：真正可执行的跨平台复现，拥抱 uv。

1. **新增 `env_locks` 表**：
   ```sql
   create table env_locks (
     id uuid primary key default gen_random_uuid(),
     project_id uuid references projects(id) on delete cascade,
     lock_type text not null default 'uv',   -- uv | pep751 | poetry | conda
     content text not null,                   -- uv.lock 全文 / PEP751 JSON
     requires_python text,
     tools jsonb default '[]',                -- MCP server pins 并入
     created_at timestamptz default now()
   );
   ```
2. **snapshot 工具升级**：`snapshot_project` 时如设备上有 uv，自动 `uv lock` 生成 `uv.lock` 一并入库（`lock_type='uv'`）；`restore_project` 时落盘 `pyproject.toml`（requires-python）+ `uv.lock` + `.python-version`，执行 `uv sync`。
3. **restore 流程（Hermes → Claude Desktop 场景）**：
   ```
   1. 新设备 auto_provision → 拉到 project + env_manifest + env_locks
   2. 检测设备：无 uv → 提示安装（或 curl 安装脚本）；有 uv → 继续
   3. 生成临时项目目录：pyproject.toml + uv.lock + .python-version
   4. uv sync → 解释器 + 依赖按平台自动落地（Mac ARM / Linux x86 各取所需 wheel）
   5. tools 条目：uvx/npx/pip 按 registry 幂等安装
   6. 校验：diff_project 输出一致性报告（"✅ 3 处一致，⚠️ 2 处漂移"）
   ```
4. **兼容输入**：用户已有 poetry.lock / requirements.txt → snapshot 时按类型入库，restore 时提示对应命令（`poetry install` / `pip install -r`）。

### Phase 3 / 映像（可选，按用户需求）

**目标**：原生二进制工具链、极致复现、容器化工作流。

1. **DevContainer 生成物**：`restore_project --format devcontainer` → 生成 `.devcontainer/devcontainer.json`（base image + features + postCreateCommand=uv sync），供 VS Code/Codespaces/Gitpod 使用。**不改变 Agent 侧执行路径**。
2. **Devbox 可选层**：manifest 里声明了 `type:"system"` 工具 → 生成 `devbox.json` + `devbox.lock`，`devbox shell` 提供与平台无关的 CLI 工具。
3. **Docker 可选层**：对"部署型项目"，`export Dockerfile`（多阶段：uv sync → 运行镜像）。用于把项目环境固化为可部署产物。
4. **Nix（仅重度用户）**：保留接口，不默认启用。

### 6.4 横切能力：环境指纹与漂移检测（值得单独做）
- 设备侧轻量探针（Hermes skill / Claude Desktop 插件 / 独立 CLI `moltable env probe`）上报：
  ```json
  {
    "os": "darwin|linux", "arch": "arm64|x86_64",
    "python": "3.11.15", "uv": "0.11.19",
    "node": "20.x", "mcp_servers": [{"name":"github","version":"1.2.3"}],
    "installed_packages_sha": "..."   // 可选：对当前 venv 做内容指纹
  }
  ```
- `diff_project(project_id)` = 项目声明 vs 设备指纹 → 输出差异清单，Agent 据此决定是否 restore。**这是"环境一致性"的用户可见价值点**，也是营销上"换电脑 3 分钟恢复"的技术支撑。

---

## 7. 风险与注意事项

1. **lock 文件体积**：uv.lock 数千行（JSON 文本），Supabase `text` 列可存（<1MB），但 API 响应会变大 → MCP 工具里按需取（`get_env_lock(project_id, version?)`），不要在 `list_projects` 里内联全文。
2. **敏感信息**：MCP server 的 `config` 可能含 API token（如 GitHub token）→ 一律走现有加密 secrets 机制（`secrets_ref`），**lock 文件与 manifest 中禁止明文密钥**（uv.lock 本身是安全的，但 server 配置不是）。
3. **向后兼容**：现有 `knowledge_bases`/`tools` JSONB 保留为"描述层"（供 LLM 读取、展示），新增 `env_manifest`/`env_locks` 为"执行层"。两者并存，`update_project` 同时写两层。
4. **不要存 `pip freeze` 输出作为跨平台锁**（§3.1 已论证），会误导用户以为锁住了。
5. **uv 未安装时的降级**：restore 必须提供"无 uv 路径"（生成 requirements.txt + 提示手动 pip install），否则 Linux 新设备首次体验会卡在工具安装。
6. **MCP Registry 是 preview**：versioning 规范已定（§5.1），但 registry 本身可能 reset；Moltable 的 tools 条目以"客户端 pin"为主，registry 元数据为辅，不依赖 registry 可用性。

---

## 8. 参考来源

- MCP Registry Versioning 规范: https://modelcontextprotocol.io/registry/versioning
- MCP Registry 官方文档: https://registry.modelcontextprotocol.io/docs
- uv 项目配置（requires-python / .python-version）: https://docs.astral.sh/uv/concepts/projects/config/
- PEP 751（Python 通用 lock 文件）: https://peps.python.org/pep-0751/
- PEP 817 Wheel Variants: https://peps.python.org/pep-0817/
- Python platform compatibility tags: https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
- Devbox 官方文档: https://www.jetify.com/devbox/docs/
- Dev Container 规范: https://containers.dev/
- Devbox vs Dev Containers vs Nix (2026): https://www.devtoolreviews.com/reviews/devbox-vs-dev-containers-vs-nix-2026
- Nix vs Docker 对比: https://flox.dev/blog/nix-and-containers-why-not-both/
- Agent Memory 系统对比 (Letta/LangMem/Mem0/Zep): https://jobsbyculture.com/blog/ai-agent-memory-systems-guide-2026
- mem0 仓库: https://github.com/mem0ai/mem0
- OpenHands（云端 coding agent 的沙箱环境实践）: https://www.openhands.dev/
- Moltable 内部文档: `~/Desktop/moltable v2/MOLTABLE_FINAL.md`、`server/schema.sql`、`server/routes/projects.py`
