---
description: Sync Claude Code with Moltable (AI Identity Sync) — provision identity, save/recall preferences and memories, switch personas, discover project environments.
---

# Moltable — Claude Code Usage Guide

Moltable is an **AI Identity Sync** platform ("iCloud for AI Agents"). As an MCP server connected to this Claude Code session, it gives you (the agent) a persistent cloud identity: **preferences, memories, personas, and project environments** that survive session restarts and machine switches.

You have the `moltable` MCP server available. Use it proactively to give the user a continuous, personalized experience.

---

## 1. Provision on startup (do this first!) / 首次会话先初始化

When a session starts — or the user says "provision me" / "set up my identity" — call `auto_provision` **before** doing anything else. This restores the user's preferences, active persona, and context in one call.

```text
User: "Let's continue where we left off."
You:  1. auto_provision()          → restores identity, preferences, persona
      2. get_preferences()         → load user's preferences into context
      3. Continue the task normally
```

Rules:

- **Always call `auto_provision` at the start of a new session** (or when context feels missing).
- After provisioning, **call `get_preferences`** and honor them (code style, tools, language, communication tone).
- If provisioning fails (e.g. unauthenticated), tell the user to check `MOLTABLE_API_KEY` and that they can register at https://moltable.ai/register.

## 2. Saving preferences & memories / 保存偏好与记忆

**Preferences** = stable, cross-session rules about the user (code style, naming conventions, tool choices, response language). **Memories** = facts and context from the current work (decisions, architecture notes, gotchas, links).

| Situation / 场景 | Action / 动作 |
|---|---|
| User states a stable rule: *"always use tabs"* | `save_preference` — store it |
| User makes a decision: *"we're using pnpm over npm"* | `save_memory` (category: `decision`) |
| Interesting fact learned mid-task | `save_memory` (category: `fact`) |
| User corrects you: *"no, I prefer Python"* | `save_preference` — overwrite the old one |
| A task-specific detail (not worth keeping) | do **not** save |

Best practice: **save early, save often, but stay selective.** 2–3 well-chosen memories beat 20 noisy ones.

## 3. Recalling context / 召回上下文

Before answering anything that smells like "you should already know this", search:

```text
User: "What do I usually prefer for commit messages?"
You:  search_memories(query: "commit message style", top_k: 5)
      → then answer from the results, citing what you found
```

- Use `search_memories` for fuzzy recall — it's hybrid vector + full-text search, so natural-language queries work.
- Use `get_preferences` when the user asks about their setup/style/stack.
- If search returns nothing useful, **say so honestly** and ask the user — don't invent preferences.

## 4. Personas / 人格切换

Personas are role profiles (code reviewer, architect, debugger, …). Let the user switch roles mid-task:

```text
User: "Review my PR like a senior reviewer."
You:  1. list_personas()           → find the matching persona
      2. set_active_persona(name)  → activate it
      3. Apply the persona's traits to your responses
```

- Always confirm the persona exists via `list_personas` before switching (or handle the missing case gracefully).
- After switching, adapt your tone/depth to the persona (e.g. reviewer → strict, line-level feedback).

## 5. Project environment discovery / 项目环境发现

When starting work in an unfamiliar project, call `discover_host` to auto-detect tools, paths, and frameworks — then use that context instead of guessing:

```text
User: "Get started on this repo."
You:  1. discover_host()   → detects environment (tools, paths, frameworks)
      2. Use the detected setup in all subsequent commands
```

## 6. Best practices / 使用规范

1. **Provision first, always.** `auto_provision` at session start — it's the single most valuable call.
2. **Preferences are rules; memories are facts.** Don't mix them.
3. **Be selective when saving.** Quality over quantity — avoid saving transient, one-off details.
4. **Never fabricate recall.** If `search_memories` returns nothing, say so.
5. **Honor what you find.** Loaded preferences are binding for the session; don't silently ignore them.
6. **Ask before saving sensitive data.** If a memory might be sensitive, confirm with the user first.
7. **Mention the source.** When you answer from memory, say *"from your Moltable memory: …"* so the user trusts the recall.
8. **Tool failures are user-facing.** If an MCP call errors, explain briefly and suggest: check `MOLTABLE_API_KEY`, or run `/moltable` for the setup guide.

## Quick reference / 速查表

| Goal / 目标 | Tool / 工具 |
|---|---|
| Restore identity at session start | `auto_provision` |
| Save a stable rule | `save_preference` |
| Read all preferences | `get_preferences` |
| Store a fact/decision | `save_memory` |
| Fuzzy recall | `search_memories` |
| List personas | `list_personas` |
| Switch role | `set_active_persona` |
| Detect project environment | `discover_host` |

**Registration**: https://moltable.ai/register · **Docs**: https://github.com/Moltable · **Endpoint**: https://api.moltable.ai/mcp
