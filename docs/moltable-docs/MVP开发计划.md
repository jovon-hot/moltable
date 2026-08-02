# Moltable · MVP 开发计划

> 版本: V1.0 | 日期: 2026-06-16

---

## 总览

```
Week 1: 后端骨架 + 数据库 + MCP Server 最小可用
Week 2: 记忆核心 + auto_provision + Hermes Skill 接入
Week 3: Web 控制台 + 浏览器插件
Week 4: 测试 + 部署 + 上线
```

---

## Week 1：后端骨架（Day 1-7）

### Day 1-2：项目初始化

```bash
# 项目结构
moltable/
├── server/
│   ├── main.py              # FastAPI 入口
│   ├── config.py             # 配置
│   ├── models/               # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── memory.py
│   │   └── persona.py
│   ├── routes/               # REST API
│   │   ├── auth.py
│   │   └── memories.py
│   ├── mcp_server.py         # MCP Server
│   └── services/
│       ├── memory_service.py # 记忆 CRUD + 检索
│       ├── embedding_service.py
│       └── provision_service.py
├── web/                      # Next.js 前端 (Week 3 开始)
├── extension/                # Chrome 插件 (Week 3 开始)
├── skills/                   # Agent Skill 文件
│   └── moltable/
│       └── SKILL.md
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Day 2-3：数据库

- [x] PostgreSQL + pgvector Docker 配置
- [x] 运行所有 DDL（见《技术架构设计》Schema）
- [x] 创建 seed 数据用于开发测试

### Day 3-4：用户系统

- [x] 注册/登录 API（邮箱 + bcrypt）
- [x] Google OAuth 集成
- [x] JWT token 签发
- [x] API Key 生成/吊销/列表 API

### Day 4-5：记忆 CRUD

- [x] save_memory / search_memory / update_memory / delete_memory API
- [x] OpenAI embedding 集成（text-embedding-3-small）
- [x] pgvector 向量检索 + HNSW 索引

### Day 5-7：MCP Server v0.1

- [x] auto_provision() 实现
- [x] search_memory() 实现
- [x] save_memory() 实现
- [x] stdio transport 支持（本地 Agent）
- [x] 与 Hermes 手动测试

---

## Week 2：记忆核心 + 接入验证（Day 8-14）

### Day 8-9：auto_provision 完善

- [x] 返回完整 profile（user表+preference类memory）
- [x] 返回 rules（从 memory 中提取 category=preference 且 tags 含 'rule' 的条目）
- [x] 返回 active_projects + recent_decisions
- [x] 返回 available_personas 列表
- [x] 性能优化：单次查询完成（使用 JOIN + JSON 聚合）

### Day 9-10：冲突检测

- [x] save_memory 前做相似度检测
- [x] 相似度 > 0.9 → 返回 {"conflict": true, "existing": [...]}
- [x] Agent 可选择覆盖/合并/跳过

### Day 10-11：Hermes Skill 接入

- [x] 写 Moltable Skill（SKILL.md）
- [x] 包含完整的 auto_provision → search → save 工作流
- [x] 在 Hermes 上端到端测试：
  - [x] 加载 Skill
  - [x] 输入 API Key
  - [x] 新会话自动识别用户
  - [x] 工作过程自动记录记忆
  - [x] 第二天新会话验证记忆持久化

### Day 11-12：HTTP Transport + 认证

- [x] MCP Server HTTP/SSE transport
- [x] API Key 认证中间件
- [x] 请求日志记录到 audit_logs

### Day 12-14：测试 + 文档

- [x] 单元测试：memory_service, provision_service
- [x] 集成测试：MCP 端到端流程
- [x] API 文档（OpenAPI/Swagger）
- [x] 快速开始指南

---

## Week 3：前端 + 插件（Day 15-21）

### Day 15-17：Web 控制台

```
页面：
├── /login          登录
├── /register       注册
├── /dashboard      总览（记忆数、Persona数、最近活动）
├── /memories       记忆管理
│   └── 列表 + 搜索 + 筛选 + 编辑 + 删除
├── /personas        Persona管理（Phase 2）
├── /settings       设置
│   ├── API Keys 管理
│   └── 账户设置
└── /docs           快速开始指南
```

### Day 17-19：Chrome 插件

- [x] 检测 AI 页面（chatgpt.com, claude.ai, gemini.google.com, chat.deepseek.com）
- [x] 注入 Moltable 工具栏（浮动按钮）
- [x] 用户点击 → 调 search_memory() → 注入到输入框
- [x] 记忆保存提示（检测到新信息 → 弹窗确认是否保存）

### Day 19-21：文档站 + 落地页

- [x] moltable.ai 落地页
- [x] 接入文档（Hermes / Claude / Cursor / 通用 MCP）
- [x] 定价页（Free / Pro $12 / Team $29）
- [x] 3分钟 Demo 视频录制

---

## Week 4：上线（Day 22-28）

### Day 22-24：生产环境部署

- [x] Railway/Render 部署
- [x] 域名 moltable.ai DNS 配置
- [x] TLS 证书
- [x] PostgreSQL 生产实例（备份策略）
- [x] 环境变量管理

### Day 24-25：监控 + 告警

- [x] API 响应时间监控
- [x] 错误率告警
- [x] 用量统计（每条 API 调用记录）

### Day 25-26：灰度测试

- [x] 5 个内测用户（赵 + 4个朋友）
- [x] Hermes + Claude Desktop 双平台验证
- [x] 收集反馈 → 修 bug

### Day 27-28：正式上线

- [x] Product Hunt 发布
- [x] Twitter/即刻 宣布
- [x] Hermes 社区发帖
- [x] Hacker News Show HN

---

## 后续路线图

```
MVP (Week 4)
  ↓
Phase 2: Persona 系统 (Week 5-10)
  ├─ Persona CRUD + 切换
  ├─ consult_persona()
  ├─ 多 Persona 对比
  └─ 记忆冲突检测增强
  ↓
Phase 3: 进化与生态 (Week 11-18)
  ├─ Entity Evolution (Git式版本管理)
  ├─ Knowledge Graph
  ├─ Persona Marketplace
  └─ Team Memory
```

---

## 团队配置（MVP 阶段）

| 角色 | 人数 | 职责 |
|------|------|------|
| 全栈工程师 | 1 | FastAPI + MCP Server + 前端 |
| 前端工程师 | 0.5 | Chrome 插件 + 落地页 |
| 设计师 | 0.3 | Logo + 控制台 UI + 插件 UI |

> MVP 阶段可以 1 人完成（全栈 + AI 辅助），后续按需扩展。

---

## 成本估算（MVP 月度运营）

| 项目 | 月成本 |
|------|--------|
| Railway/Render (API + Web) | $25 |
| PostgreSQL (托管) | $15 |
| OpenAI Embedding API | ~$10 (10万次检索) |
| 域名 | $1 |
| **合计** | **~$51/月** |
