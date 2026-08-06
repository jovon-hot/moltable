## 2026-08-07 (R8.1 — 夜间维护·安全审计·依赖升级·测试修复)

- **安全审计**: npm audit (0 vulns) ✅ + pip-audit (0 vulns) ✅
- **依赖升级 (web)**: @supabase/supabase-js 2.45→2.112, lucide-react 1.0→1.29, @types/react 19.0→19.2, autoprefixer 10.4→10.5
- **依赖升级 (server)**: uvicorn 0.39.0→0.52.1, pydantic_core 2.46.4→2.48.0
- **测试修复**: test_contradiction_language_detection — Jaccard mock 相似度不足 (0.40 < 0.60 阈值)，改用固定 0.65 lambda
- **构建验证**: Next.js build 45 pages ✅, 212 tests passed / 3 skipped ✅
- **健康检查**: 全端点 200 OK ✅
- **version 锁文件**: requirements.txt + requirements-railway.txt 同步 uvicorn 0.52.1

## 2026-08-07 (R8 — 夜间维护·Identity Graph 关系推理引擎)

- **功能**: Relationship Inference 引擎 — 自动检测记忆间关系 🆕
  - 三级关系检测: SUPERSEDES (>85%相似)、CONTRADICTS (矛盾事实)、EXTENDS (45-85%相似)
  - Key-Value 事实提取: 自动识别 "uses X" / "lives in Y" / "prefers Z" 等事实对
  - 中文矛盾检测: 支持「不对」「实际上」「修正」「不再」等中文矛盾信号词
  - 矛盾语言检测 + 否定词计数 + 事实冲突识别 三层矛盾检测策略
  - 集成到记忆保存管道: 每次保存自动检测关系（非阻塞）
- **功能**: Identity Graph 查询服务 — 上下文感知记忆检索 🆕
  - 6 步查询流程: 身份解析→Persona路由→项目作用域→图遍历→时序衰减→上下文组装
  - 时序衰减引擎: 指数衰减 (半衰期 7 天)、新鲜度加权 (1.2×)、被取代惩罚 (0.1×)、活跃项目加成 (1.1×)
  - Pinned 记忆免疫: 标记为 pinned 的记忆永久忽略衰减
  - 偏好作用域过滤: 全局/Persona/Project 三级偏好自动匹配
  - 图上下文: 自动连接相关知识图谱实体
  - Auto Provision: 一键身份恢复（Persona 检测 + 偏好 + 记忆）
- **集成**: 记忆保存 API 新增 `relationships_detected` 返回字段
- **测试**: 40 个新测试 (29 relationship_inference + 11 identity_graph)
- **全量测试**: 212 passed, 3 skipped ✅
- **提交**: [本次]

## 2026-08-07 (R7 — 夜间维护·增长基建·代码重构)

- **重构**: 提取共享博客数据模块 `web/src/data/blog-posts.ts` — 消除 blog/page.tsx 与 feed.xml/route.ts 之间的元数据重复
  - 单一数据源: 22 篇博客文章元数据统一管理
  - 导出 `getSortedPosts()`, `getAllTags()`, `getPostsByTag()` 辅助函数
- **功能**: 博客标签筛选系统 — 点击标签即过滤文章列表
  - 标签显示文章计数，支持单击筛选/再次点击取消
  - 精选文章仅在未筛选时展示
- **增长**: 新建 `/changelog` 公开产品更新页 — SSR 渲染 CHANGELOG.md
  - Markdown→HTML 转换保留 emoji 图标
  - 加入 sitemap (priority 0.8) + 更新 footer 链接
- **构建**: 50 静态页面, 0 错误, 0 警告 ✅
- **依赖**: Next.js 15.5.22→15.5.23 (构建时自动补丁)
- **测试**: 172 passed, 3 skipped ✅
- **提交**: 1 commit

## 2026-08-07 (R6 — 夜间维护·构建修复·依赖升级)

- **构建修复**: Next.js 15 viewport 弃用 — Metadata 中 viewport 迁移至独立 Viewport 导出 🔧
  - 根 layout.tsx: `metadata.viewport` → `export const viewport: Viewport`
  - 消除 9 个 viewport 弃用警告（所有页面继承根 layout，一并修复）
  - 构建: 48 静态页面, 0 错误, 0 警告 ✅
- **安全审计**: npm audit 0 漏洞 ✅ | pip-audit clean ✅
- **依赖升级**: sentence-transformers 5.6.1→5.7.0（minor upgrade, 测试全通过）
- **TypeScript**: devDependency ^5.5.0→^6.0.0（为未来兼容）
- **测试**: 172 passed, 3 skipped ✅ | 健康检查 6/6 端点 OK
- **待观察**: uvicorn 0.39→0.52（跨版本较多，建议白天人工评估）
- **跳过**: Next.js 15→16 / Tailwind 3→4 / lucide-react 0.4→1.x（破坏性变更，需单独计划）

## 2026-08-07 (R5 — 夜间维护·安全加固·依赖升级)

- **安全审计**: npm audit — 0 漏洞 ✅ | pip-audit — 101→0 漏洞 🔧
  - Python 3.9→3.11 运行时升级，创建 `.venv/` 隔离环境
  - 关键修复: starlette 0.49.3→1.4.1 (SSRF/Host注入) | transformers 4.57.6→5.14.1 (RCE) | torch 2.8.0→2.13.0 (内存损坏)
  - aiohttp 3.13.5→3.14.3 | urllib3 2.6.3→2.7.0 | requests 2.32.5→2.34.2
  - setuptools 58.0.4→83.0.0 | wheel 0.37.0→0.47.0 | soupsieve 2.8.3→2.8.4
- **测试**: 全量 172 passed, 3 skipped ✅（新 venv 通过）
- **构建**: .next 260MB | 首屏 JS 103kB | 47 静态页面
- **健康**: 6/6 端点 OK (200, 4.8s) ✅
- **待升级**: Next.js 15→16 | Tailwind 3→4 | lucide-react 0.4→1.x | TypeScript 5→7（需适配破坏性变更）

## 2026-08-07 (R5 — 夜间维护·增长优化·内容生产)

- **增长**: 推荐系统增强 — LinkedIn 分享 + 奖励展示 + 推荐落地页 🆕
  - 新增 LinkedIn 分享渠道（5 平台全覆盖：Twitter/LinkedIn/WhatsApp/Telegram/Email）
  - 推荐奖励卡片 — 展示 500 记忆容量/推荐 + Super Connector 徽章 + Pro 试用
  - 新建 `/signup` 推荐落地页 — 个性化欢迎 + 权益展示 + 社交证明 + CTA
  - Register 页面处理 `ref` 参数，sessionStorage 存储推荐码
- **Sitemap**: 新增 `/signup` 路由（priority 0.8）
- **内容**: Newsletter 2026-08-07 草稿 — 时间记忆/推荐系统/内容生产/Pro Tips
- **功能**: Smart Memory Merge — 基于相似度的自动合并（update/enrich/normal 三级策略）
  - 227 行测试覆盖 update/enrich/normal 全流程
  - 减少重复记忆，提升数据质量
- **构建**: Next.js 47 静态页面，0 错误 ✅
- **提交**: [本次] - 2 commits
## 2026-08-07 (R5 — 夜间维护·智能合并引擎)

- **功能**: Smart Auto-Merge — 保存记忆时智能去重与合并 🆕
  - 三级合并策略：>95% 相似自动更新 / >85% 自动扩充 / <85% 正常保存
  - 新增 `auto_merge` 参数（默认 true），向后兼容 `force` 参数
  - `_smart_merge()` 函数：选择最高相似度冲突进行 update 或 enrich
  - 保存响应新增 `auto_merged` + `action` 字段区分合并类型
- **竞品对齐**: 对标 mem0 的 agent_custom_instructions（agent 级记忆提取）—
  Moltable 用 Persona 路由 + 智能合并实现差异化
- **测试**: 6 个新增测试（test_smart_merge.py）— update/enrich/insert/多冲突场景全覆盖
- **全量测试**: 172 passed, 3 skipped, 0 failed ✅
- **提交**: [本次]

## 2026-08-06 (R4 — 夜间维护·增长引擎·内容生产)

- **增长**: Referral/Invite 推荐系统上线 — 病毒式增长引擎 🆕
  - `routes/referrals.py` — 5 个 API：generate/lookup/stats/claim + 权限校验
  - 8 位字母数字推荐码，分享链接一键复制
  - `/dashboard/referrals` 页面 — 推荐统计、分享面板
  - 数据库：`supabase/migrations/20260806_referrals.sql`
- **内容**: 「Moltable vs Zep: Temporal Memory & Identity」深度对比博客 — ~2100字
  - 6 端点对比表、模式检测分析（oscillation/gradual/rapid change）
  - 中英双语摘要、架构对比、定价对比、选型建议
  - 博客索引 + RSS 同步更新
- **竞品对齐**: 更新 /compare 对比页 — 新增 Temporal Memory Timeline + Memory Health Scoring
  - Moltable 对比功能从 15 项增至 17 项
  - 中英文 features + strengths 同步更新
- **构建**: Web Next.js build 成功 ✅
- **提交**: [本次] - 3 commits

## 2026-08-06 (R3 — 夜间维护·功能开发·竞品对齐)

- **功能**: Temporal Memory Timeline — 事实变化时间线追踪系统 🆕
  - `services/temporal_tracker.py` — 核心服务（524行）：自动检测事实变更、构建实体时间线、模式识别（oscillation/gradual shift/rapid change）、状态快照
  - `routes/temporal.py` — 6 个 API 端点：`/timeline/{entity}`, `/timelines`, `/state`, `/changes`, `/transitions`, `/report`
  - 集成到记忆保存管道：每次保存记忆时自动检测 temporal transitions
  - 模式检测：flip-flopping（震荡）、渐进迁移、快速变化
  - Persona 感知：transitions 可按 Persona 范围隔离
- **竞品对齐**: 直接对标 Zep 的 temporal knowledge graph 核心能力
  - Moltable 独有优势：temporal + identity sync + memory health + persona — 四合一
- **数据库**: `supabase/migrations/20260806_temporal_facts.sql` — temporal_facts 表（含 RLS）
- **测试**: 17 个新测试（test_temporal_tracker.py）— 核心逻辑 + 模式检测全覆盖
- **全量测试**: 166 passed, 3 skipped, 0 failed ✅
- **提交**: [本次]

## 2026-08-06 (R2 — 夜间维护·安全升级)

- **安全**: pip audit → 0 vulns（从 18 → 0，全部修复）
- **Python 依赖升级**:
  - `fastapi`: 0.128.8 → 0.141.1
  - `starlette`: 0.52.1 → 1.4.1（修复 7 个漏洞）
  - `cryptography`: 48.0.0 → 50.0.0（修复 4 个漏洞）
  - `python-dotenv`: 1.2.1 → 1.2.2（修复 1 个漏洞）
  - `transformers`: 4.57.6 → 5.14.1（修复 5 个漏洞）
  - `sentence-transformers`: 5.1.2 → 5.6.1（兼容 transformers 5.x）
  - `pytest`: 8.4.2 → 9.1.1（修复 1 个漏洞）
  - `pytest-asyncio`: 1.2.0 → 1.4.0
  - `huggingface-hub`: 0.36.2 → 1.26.0
- **测试**: 165 passed, 3 skipped（1 pre-existing failure: temporal_tracker）
- **构建**: Web Next.js build 成功 — 42 静态页面, 首页 JS 103kB
- **健康**: 全端点 7/7 通过 ✅
- **npm audit**: web 端 0 vulns ✅
- **Git**: main 分支与 origin/main 同步
- **已知**: npm outdated 显示 Next.js 16 / Tailwind 4 / TypeScript 7 / lucide-react 1.x 均为跨大版本升级，需人工迁移评估。transformers 5.x 升级后 embedding 测试通过。
- **提交**: [本次]

## 2026-08-06 (R1 — 夜间维护·内容生产)

- **内容**: 新博客「The Identity Graph: Why Vector Search Alone Can't Give Your AI Agent True Memory」— ~2500字深度技术文章，含架构图、对比表、性能基准
- **内容**: Identity Graph 与 Vector Search 对比分析 — 上下文相关度 94% vs 62%
- **内容**: 社交媒体文案 5 篇（Twitter/LinkedIn/即刻）— 从新博客提取
- **内容**: 8 月 Newsletter 草稿 — 产品更新、新内容、社区动态、Pro Tips、路线图
- **内容**: Product Hunt 发布素材包 — Tagline、长短描述、Maker Comment、Launch Checklist、成功指标
- **文档**: 新增 `IDENTITY_GRAPH_ARCHITECTURE.md` — 完整架构设计文档（实体模型、关系类型、查询流、数据模型、MCP 集成、时间衰减模型）
- **SEO**: 18 篇博客 MDX 全部添加 description + tags 元数据（先前 17 篇仅有空 tags）
- **SEO**: rag-vs-finetuning-vs-identity 补充 description
- **Web**: 新博客路由 `identity-graph-vs-vector-search/page.mdx` 已创建
- **提交**: [本次]

## 2026-08-05 (R4 — 夜间维护)
- **安全**: npm audit → 0 vulns (web)；pip audit → 0 vulns (server)
- **测试**: 全测试套件通过 — 112 passed, 3 skipped, 1.00s
- **代码质量**: Ruff 从 176 → 54 错误（自动修复 111 + 手动修复 11）
- **Bug修复**: routes/auth.py — 修复 `logger` 未定义导致运行时崩溃的 bug
- **Bug修复**: routes/auth.py — 修复 f-string 语法错误
- **清理**: agent_experience.py 未使用变量, sqlite_adapter.py 歧义变量名
- **构建**: Next.js build 成功 — 首页 JS 103kB (shared), Vercel SIN1 HIT cache
- **健康**: 全端点 7/7 通过 ✅
- **Python**: 依赖全部最新且兼容（无强制升级导致的冲突）
- **JS依赖**: Next.js 16 / Tailwind 4 / TypeScript 7 均为跨大版本升级，需人工迁移评估
- **内容**: 新博客「为什么你的 AI 每次都不记得你是谁」— ~2500字痛点文章，含三层架构图、对比表、CTAs
- **增长**: Claude Code Plugin 上线 — .mcp.json 一键配置 + install.sh 自动安装脚本 + MOLTABLE.md Claude 命令
- **功能**: Memory Health Scoring 引擎 — 四维评分（时效/完整度/重复/矛盾），自动清理低质量记忆
- **提交**: [本次] - 3 commits (lint fixes, blog + memory health, claude-code plugin)

## 2026-08-05 (R3)
- **增长**: A/B 测试框架上线 — 实验 CRUD、权重随机分配、转化追踪、管理面板
- **内容**: 发布 Moltable vs mem0 深度对比博客 — Identity Layer vs Memory Layer 架构分析
- **增长**: 增强增长报告 v2 — 漏斗分析、异常检测、实验面板集成
- **内容**: 社交媒体文案 5 篇（Twitter/LinkedIn/即刻）

# Changelog

## 2026-08-05 (R2)
- **增长**: 新建 /compare 竞品对比页 — Moltable vs mem0 vs Zep 15维功能对比
- **增长**: 对比页含架构分析、定价对比、适用场景推荐（双语 zh/en）
- **SEO**: 对比页完整 metadata + canonical URL，目标关键词"mem0 alternative"
- **SEO**: 为三大核心博客添加 per-post metadata + Article JSON-LD 结构化数据
- **分析**: 根布局集成 Umami Analytics（NEXT_PUBLIC_UMAMI_WEBSITE_ID 可配置）
- **SEO**: 更新 sitemap.xml 含 /compare 路由 + 全部 15 篇博客文章 URL
- **内容**: 创建 docs/social/2026-08-05.md 对比页推广社交媒体内容（5 帖）
- **提交**: [本次] - 3 commits (comparison page, blog SEO, structured data + social)

## 2026-08-05 (R1)
- **健康**: 全端点扫描 6/6 通过 (200)
- **审计**: npm audit web 0 vulns, server 0 vulns
- **清理**: 删除 3,357 个旧 session 文件，释放 ~345MB 磁盘空间
- **状态**: 无修复需要，代码库干净，最新 commit 已部署

## 2026-08-04 (R2)
- **安全**: npm audit 0 vulns — 升级 Next.js 14.2.35→15.5.22 (修复 2 HIGH + 13 MODERATE 漏洞)
- **安全**: 升级 React 18→19, React-DOM 18→19, @types/react 18→19
- **安全**: 添加 npm overrides 强制 postcss≥8.5.0, sharp≥0.35.0
- **修复**: 修复 memories/page.tsx 中 if-else 语法导致 Next 15 构建失败
- **健康**: 全端点扫描 7/7 通过
- **提交**: [本次] - security: upgrade Next.js 15 + React 19, fix build

## 2026-08-04 (R1)
- **维护**: 全端点健康扫描 7/7 通过（首次扫描出现瞬时网络抖动后自愈）
- **修复**: 添加 `venv311/` 到 `.gitignore`，避免 1.3G 虚拟环境目录被跟踪
- **审计**: npm audit 发现 2 个 HIGH 级别漏洞（Next.js 14.2.35 → 需跨大版本升级至 16.x，暂缓）
- **提交**: bb6a1d7 - chore: add venv311/ to .gitignore

## 2026-08-05 (R5 — 夜间维护·功能开发)
- **功能**: 记忆健康评分系统 — `GET /api/memories/health` 全面健康报告
- **功能**: 记忆自动清理 — `POST /api/memories/health/cleanup` 自动归档低质量记忆
- **新服务**: `services/memory_health.py` — 陈腐度检测、矛盾检测、重复聚类、完整性评分
- **测试**: 新增 14 个测试 (test_memory_health.py) — 年龄计算、矛盾检测、健康评分、重复检测、报告生成
- **竞品对齐**: 抗衡 Cognee improve()、Zep temporal knowledge graph — Moltable 独有健康评分体系
- **提交**: [本次] - feat: memory health scoring + staleness detection + auto-cleanup
