# Moltable — AI Identity Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**你的 AI，永远认识你。** · **One identity. Every agent.**

Moltable 是 AI Agent 的身份同步层。一个身份接入，所有 Agent 自动同步偏好、技能和记忆。换电脑 3 分钟恢复完整 AI 环境。

---

## 核心能力

- 🔄 **3 分钟环境恢复** — 换电脑后身份/偏好/Persona/Skills/MCP 配置一键恢复
- 🧠 **跨 Agent 记忆** — 10,000 条记忆跨平台同步（Pro），向量 + 全文混合搜索
- 🗺️ **项目环境地图** — knowledge_bases + tools 配置化存储
- 🎭 **多 Persona 切换** — 不同角色不同视角

---

## 快速开始

```bash
# 注册获取 API Key（30 秒）
# https://moltable.ai/register
```

### 🚀 一行接入（推荐）

```bash
# Claude Desktop
npx @moltable/connect claude --api-key <你的API-Key>

# Cursor
npx @moltable/connect cursor --api-key <你的API-Key>

# Hermes
npx @moltable/connect hermes --api-key <你的API-Key>
```

`@moltable/connect` 自动完成：读取/创建平台 MCP 配置 → 备份原配置 → 写入 Moltable
server（`https://api.moltable.ai/mcp` + `X-API-Key` header）→ 在线验证 API Key →
打印接入指引。无需手动编辑任何 JSON。

### 其他方式

```bash
# 一键脚本（已注册用户）
curl -sL https://moltable.ai/connect.sh | bash -s -- <你的API-Key>

# 或手动配置 MCP
```

```json
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "https://api.moltable.ai/mcp",
      "headers": { "X-API-Key": "你的API-Key" }
    }
  }
}
```

---

## 定价

| | Free | Pro |
|--|------|-----|
| 价格 | ¥0 | ¥19/月 |
| 记忆 | 100 条 | 10,000 条 |
| Persona | 2 个 | 无限 |
| 主机发现 | 1 个 | 无限 |

---

## 支持的 Agent

Hermes · Claude Code · Cursor · 任意 MCP 兼容客户端

---

## 自托管

```bash
git clone https://github.com/jovon-hot/moltable.git
cd moltable/server
pip install -r requirements.txt
python main.py
```

MIT License
