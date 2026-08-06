# Moltable — AI Identity Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**你的 AI，永远认识你。** · **One identity. Every agent.**

Moltable 是 AI Agent 的身份同步层。一个身份接入，所有 Agent 自动同步偏好、技能和记忆。换电脑 3 分钟恢复完整 AI 环境。

Moltable is the identity sync layer for AI agents. Connect once — every agent auto-syncs your preferences, skills, and memories. Full AI environment recovery in 3 minutes on any machine.

---

## 核心能力 · Core Capabilities

- 🔄 **3 分钟环境恢复** — 换电脑后身份/偏好/Persona/Skills/MCP 配置一键恢复
  - **3-Minute Environment Recovery** — Identity, preferences, personas, skills, and MCP configs restore with one click
- 🧠 **跨 Agent 记忆** — 10,000 条记忆跨平台同步（Pro），向量 + 全文混合搜索
  - **Cross-Agent Memory** — 10,000 memories synced across platforms (Pro), hybrid vector + full-text search
- 🗺️ **项目环境地图** — knowledge_bases + tools 配置化存储
  - **Project Environment Map** — Configurable storage for knowledge bases and tool configurations
- 🎭 **多 Persona 切换** — 不同角色不同视角
  - **Multi-Persona Switching** — Different roles, different perspectives

---

## 快速开始 · Quick Start

```bash
# 注册获取 API Key（30 秒）· Register for API Key (30 seconds)
# https://moltable.ai/register
```

### 🚀 一行接入 · One-Line Connect

```bash
# Claude Desktop
npx @moltable/connect claude --api-key <your-api-key>

# Cursor
npx @moltable/connect cursor --api-key <your-api-key>

# Hermes
npx @moltable/connect hermes --api-key <your-api-key>
```

`@moltable/connect` 自动完成：读取/创建平台 MCP 配置 → 备份原配置 → 写入 Moltable
server（`https://api.moltable.ai/mcp` + `X-API-Key` header）→ 在线验证 API Key →
打印接入指引。无需手动编辑任何 JSON。

`@moltable/connect` auto-completes: read/create platform MCP config → backup original → write Moltable server → validate API key online → print setup guide. No manual JSON editing needed.

### 其他方式 · Alternative Methods

```bash
# 一键脚本 · One-liner script (registered users)
curl -sL https://moltable.ai/connect.sh | bash -s -- <your-api-key>

# 或手动配置 MCP · Or manual MCP config
```

```json
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "https://api.moltable.ai/mcp",
      "headers": { "X-API-Key": "your-api-key" }
    }
  }
}
```

---

## 定价 · Pricing

| | Free | Pro |
|--|------|-----|
| 价格 Price | ¥0 | ¥19/月 |
| 记忆 Memory | 100 条 | 10,000 条 |
| Persona | 2 个 | 无限 Unlimited |
| 主机发现 Discovery | 1 个 | 无限 Unlimited |

---

## 支持的 Agent · Supported Agents

Hermes · Claude Code · Cursor · Any MCP-compatible client

---

## 自托管 · Self-Host

```bash
git clone https://github.com/Moltable.git
cd moltable/server
pip install -r requirements.txt
python main.py
```

---

## 📚 博客 · Blog

Read deep dives on AI identity, MCP protocol, and agent memory architecture:
→ [moltable.ai/blog](https://www.moltable.ai/blog)

---

MIT License
