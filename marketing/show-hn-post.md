# Show HN 发帖草稿

## 标题
Show HN: Moltable — AI Identity Sync (one identity, every agent)

## 正文
I got tired of restarting every Claude conversation from zero.

Every morning:
- "Hey Claude, continue yesterday's work"
- "I don't have any context from previous conversations."
- Spend 20 minutes re-teaching it who I am.

Then I switched to Cursor. Same problem. Then Codex. Same.

So I built Moltable — an identity sync layer for AI agents.

**What it does:**
- One command connects Claude, Cursor, Codex, Hermes (npx @moltable/connect claude --api-key xxx)
- Your preferences, Personas, skills, and memories sync across ALL agents
- Switch computers? 3 minutes to restore everything. One sync code.

**Architecture:**
```
Identity Layer → Cross-platform unique ID (DID-based)
Persona Layer → Role management (Developer / Architect / Writer)
Sync Layer → Sync code mechanism + MCP protocol
Memory Layer → 10K cards, semantic search
```

**Tech stack:**
FastAPI (Python) + Next.js (React) + Supabase + MCP protocol
MIT licensed. Self-hostable.

**Why not mem0?**
mem0 is brilliant at memory extraction. But what I needed was identity — a layer that tells every agent "this is the same person, use the same preferences." They're complementary, not competitive.

**Current state:**
- 14 MCP tools
- Free tier (100 memories, 2 Personas, 3 agents)
- Pro ¥19/mo (~$2.60 USD)
- 18 blog posts (bilingual CN/EN)

**I'm looking for feedback on:**
1. The onboarding flow — too many steps?
2. Would you trust a sync code for identity recovery?
3. What agent platforms should I support next?

Try it: https://moltable.ai/register
GitHub: https://github.com/jovon-hot/moltable

---

## 发布指南

⚠️ 重要：必须由你手动发，HN 禁止代理/自动化发帖。

发布时机：美西时间 8:00-10:00 AM（北京时间 23:00-01:00）
最佳日期：周二到周四

步骤：
1. 打开 https://news.ycombinator.com/submit
2. Title: Show HN: Moltable — AI Identity Sync (one identity, every agent)
3. URL: 留空（Show HN 不需要 URL，正文就是产品）
4. Text: 粘贴上面正文
5. Submit

发布后即刻通知我，我帮你监控回复并在 5 分钟内回复第一条评论。
