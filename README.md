<p align="center">
  <img src="web/public/logo-brand.svg" width="120" alt="Moltable" />
</p>

<h1 align="center">Moltable — AI Identity Sync</h1>
<p align="center"><strong>One identity. Every agent.</strong> · <strong>你的 AI，永远认识你。</strong></p>

<p align="center">
  <a href="https://github.com/Moltable/moltable/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" /></a>
  <a href="https://www.moltable.ai"><img src="https://img.shields.io/badge/Website-moltable.ai-4338CA" /></a>
  <a href="https://www.moltable.ai/blog"><img src="https://img.shields.io/badge/Blog-18_posts-FB6B4B" /></a>
</p>

---

Moltable is the **identity sync layer for AI agents**. Connect once — every agent (Claude, Cursor, Codex, Hermes) auto-syncs your preferences, Personas, skills, and memories. Switch computers? Full AI environment recovery in 3 minutes.

Moltable 是 AI Agent 的**身份同步层**。一个身份接入，所有 Agent 自动同步偏好、Persona、技能和记忆。换电脑 3 分钟恢复完整 AI 环境。

---

## Why does my AI forget me every morning?

> "Hey Claude, continue yesterday's work."  
> "Hello! I don't have any context from previous conversations."

Every AI agent session starts from zero. You spend 3.2 hours/week re-teaching your AI who you are. Moltable fixes this with a **three-layer identity architecture**:

```
Identity Layer    → Cross-platform unique ID
Persona Layer     → Role management (Developer / Architect / Writer)
Sync Layer        → One sync code restores everything
```

Not a memory tool. **An identity layer.** Read more: [moltable vs mem0](https://www.moltable.ai/blog/moltable-vs-mem0-identity-vs-memory)

---

## 🚀 One-line Connect

```bash
# Claude Desktop
npx @moltable/connect claude --api-key <your-api-key>

# Cursor
npx @moltable/connect cursor --api-key <your-api-key>

# Hermes
npx @moltable/connect hermes --api-key <your-api-key>
```

No manual JSON editing. Auto-detects your config, backs it up, injects Moltable MCP server, validates your key. [Get a free API key →](https://moltable.ai/register)

### Manual MCP config

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

## Capabilities

| | Free | Pro (¥19/mo) |
|---|---|---|
| Memory | 100 cards | 10,000 cards |
| Personas | 2 | Unlimited |
| Agent platforms | 3 | Unlimited |
| Semantic search | ✅ | ✅ |
| Sync code recovery | ✅ | ✅ |
| Discovery | 1 host | Unlimited |

---

## Supported Agents

<p>
  <img src="https://img.shields.io/badge/Hermes-Agent-4338CA" />
  <img src="https://img.shields.io/badge/Claude_Desktop-MCP-4338CA" />
  <img src="https://img.shields.io/badge/Cursor-MCP-4338CA" />
  <img src="https://img.shields.io/badge/Codex-MCP-4338CA" />
  <img src="https://img.shields.io/badge/OpenCode-MCP-4338CA" />
</p>

Any MCP-compatible client works out of the box.

---

## Self-Host

```bash
git clone https://github.com/Moltable/moltable.git
cd moltable/server
pip install -r requirements.txt
python main.py
```

Licensed under **MIT**. Identity data belongs to you — always.

---

<p align="center">
  <a href="https://www.moltable.ai">🌐 Website</a> ·
  <a href="https://www.moltable.ai/docs">📚 Docs</a> ·
  <a href="https://www.moltable.ai/blog">📝 Blog</a> ·
  <a href="https://www.moltable.ai/faq">❓ FAQ</a>
</p>

<p align="center"><sub>MIT License · Built with ❤️ in Beijing</sub></p>
