# Moltable v0.2.0 — AI Identity Layer (DID+VC)

在任何 AI 里加载你的 Moltable，AI 就自动认识你。

## 什么是 Moltable？

Moltable 是 AI 时代的身份层。通过 MCP 协议，让任何 AI Agent 自动加载你的身份、偏好、记忆和 Persona。

- 🔗 **跨平台身份同步** — Hermes、Claude、ChatGPT 共享同一套记忆
- 🧠 **渐进记忆积累** — 每次对话自动记录，用得越久 AI 越懂你
- 👤 **多 Persona 切换** — 战略顾问、审核员、创意伙伴，一个身份多种人格
- 🔓 **完全开源** — MIT 协议，数据永远属于你

## 快速开始

1. 注册账号 → 获取 API Key
2. 在 Hermes / Claude 中加载 Moltable Skill
3. AI 自动认识你，开始工作

## 技术栈

- 后端: Python + FastAPI + Supabase (PostgreSQL + pgvector)
- 前端: Next.js 14 + Tailwind CSS
- 协议: MCP (Model Context Protocol) JSON-RPC 2.0
- 嵌入: sentence-transformers (all-MiniLM-L6-v2)

## 项目结构

```
server/     — FastAPI 后端 + MCP Server
web/        — Next.js 前端控制台
extension/  — Chrome 浏览器插件
skills/     — Hermes Agent Skill 文件
```

## 本地开发

```bash
cp server/.env.example server/.env
# 编辑 .env 填入 Supabase 凭证（可选，不填则用 SQLite 本地模式）

cd server && pip install -r requirements.txt
python3 main.py
# → http://localhost:8700

cd ../web && npm install && npm run dev
# → http://localhost:8701
```

API 文档: http://localhost:8700/docs

## 生产部署

见 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)——Vercel + Supabase + Railway 三步部署。

```bash
docker compose up -d
```

## 许可证

MIT License
