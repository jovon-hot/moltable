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
