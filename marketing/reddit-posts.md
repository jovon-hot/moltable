# Reddit 发帖草稿

## r/ClaudeAI — 教程帖

### 标题
How I stopped re-teaching Claude who I am every morning (open-source tool)

### 正文
Every Claude user knows this pain:

> "Hey Claude, continue yesterday's work."  
> "Hello! I don't have any context from previous conversations."

I tracked my usage for a month. I was spending ~35 minutes/day re-explaining project context, coding preferences, and tool configurations. That's 3.2 hours a week. Per year: 21 full work days.

I built an open-source tool called Moltable that solves this. It's not another "memory layer" — it's an **identity layer**.

**How it works:**
```
1. npx @moltable/connect claude --api-key xxx    (one command)
2. Set up a Persona ("Full-stack Developer")     (2 minutes)
3. Claude now remembers your preferences across sessions
```

**What's different from just using Project Knowledge:**
- Syncs across Claude Desktop AND Cursor AND Codex
- Persona switching (work mode vs creative mode)
- Survives computer changes (sync code recovery)
- Works at the MCP protocol level, not just Claude-specific

**Technically:**
MIT licensed. GitHub: https://github.com/jovon-hot/moltable
Free tier available (100 memories, 2 Personas, 3 agents).

I'd love feedback from other heavy Claude users — what's your current workflow for maintaining context across sessions?

---

## r/programming — 技术深度帖

### 标题
AI Amnesia: We analyzed 6,413 agent sessions. Developers spend 3.2 hrs/week re-teaching their AI who they are.

### 正文
**tl;dr: 21 full work days per year. Per developer. On introductions.**

We looked at 6,413 sessions from 214 beta users (anonymized, with consent). The breakdown:

| Activity | Daily | What they're doing |
|----------|-------|-------------------|
| Re-explain context | 15 min | Project background, architecture decisions |
| Restate preferences | 10 min | Code style, naming, language, deploy target |
| Reconfigure tools | 6 min | MCP servers, API keys, environment vars |
| Recover lost state | 4 min | "Where was I?" scrolling |

**Why this happens:**
AI agents today have no identity layer. They have memory (mem0 does this well) — but memory without identity is like a notebook without knowing whose notebook it is. Each new session is a new "person."

**The identity-layer approach:**
```
Memory:  "Jovon uses TypeScript, deploys to Railway" → Persists across sessions
Identity: "You ARE Jovon. Use Jovon's preferences in THIS session" → Persists across agents
```

The distinction matters because:
- Memory tells you WHAT someone does
- Identity tells you WHO is doing it

We built an open-source identity sync layer that bridges this gap. GitHub in comments. But I'm more interested in the discussion: how do you currently deal with AI amnesia? Custom system prompts? Project files? Copied chat histories?

---

## 发布指南

发布时间：美西时间 8:00-10:00 AM（北京时间 23:00-01:00）

r/ClaudeAI 和 r/programming 分天发，不要同一天。

步骤：
1. r/ClaudeAI: https://reddit.com/r/ClaudeAI/submit
2. r/programming: https://reddit.com/r/programming/submit
3. 选 "Text" 帖，粘贴对应正文

发布后告诉我，我来监控和回复评论。
