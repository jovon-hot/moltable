# Moltable × Claude Code

**AI Identity Sync — "iCloud for AI Agents"** · 为 AI Agent 打造的身份云同步

> Your AI's preferences, memories, and personas — synced across every Claude Code session, on every machine. / 让 Claude Code 的偏好、记忆与人格，跨会话、跨设备自动同步。

![MCP](https://img.shields.io/badge/MCP-Server-blue) ![Claude Code](https://img.shields.io/badge/Claude%20Code-Ready-000000) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents / 目录

- [What is Moltable? / 什么是 Moltable](#what-is-moltable)
- [Why Claude Code users need it / 为什么 Claude Code 用户需要它](#why-claude-code-users-need-it)
- [Features / 功能](#features)
- [Install (30 seconds) / 安装（30 秒）](#install)
- [Configuration / 配置](#configuration)
- [Usage examples / 使用示例](#usage-examples)
- [MCP tools / 工具一览](#mcp-tools)
- [Pricing / 价格](#pricing)
- [Troubleshooting / 故障排查](#troubleshooting)
- [Links / 链接](#links)

---

## What is Moltable? / 什么是 Moltable

**English.** Moltable is an **AI Identity Sync** platform — the "iCloud for AI Agents". It gives every AI agent a persistent identity: a cloud-synced store of **preferences, memories, personas, skills, and project environments** that follows the agent wherever it runs.

For Claude Code, Moltable acts as a Memory & Identity Server (MCP). Claude Code connects to `https://api.moltable.ai/mcp` over HTTP, and gets instant access to:

- **Preferences** — how you like code formatted, which tools you prefer, your communication style
- **Memories** — facts, decisions, and context worth remembering across sessions
- **Personas** — ready-made role profiles (code reviewer, architect, debugger, writer…)
- **Project environments** — auto-discovered tools, paths, and frameworks

Switch laptops, start a fresh session, spin up a second instance — your Claude Code still knows you.

**中文.** Moltable 是一个 **AI 身份同步**平台 —— 相当于“AI Agent 的 iCloud”。它为每个 AI Agent 提供持久化的云端身份：偏好、记忆、人格、技能与项目环境，跟随 Agent 在任何设备、任何会话间同步。

对 Claude Code 而言，Moltable 是一个 MCP 身份与记忆服务器。Claude Code 通过 HTTP 连接 `https://api.moltable.ai/mcp`，即刻获得：

- **偏好** —— 你的代码风格、工具偏好、沟通方式
- **记忆** —— 跨会话值得记住的事实、决策与上下文
- **人格（Persona）** —— 开箱即用的角色模板（代码评审、架构师、调试、写作……）
- **项目环境** —— 自动发现的项目工具、路径与框架

换电脑、开新会话、起第二个实例 —— Claude Code 依然认识你。

---

## Why Claude Code users need it / 为什么 Claude Code 用户需要它

**English.** Every fresh Claude Code session starts from zero. You re-explain your preferences, re-upload project context, and lose the accumulated knowledge from previous conversations. Moltable fixes this:

| Problem / 痛点 | Without Moltable | With Moltable |
|---|---|---|
| New session, new machine | Re-explain everything | `auto_provision` restores your identity in one call |
| Lost context | "I told you this last week…" | `search_memories` recalls it instantly |
| Different roles | Manual prompt engineering per task | One command persona switching |
| Onboarding a project | Re-discover tools & paths by hand | `discover_host` does it automatically |

**中文.** 每次新开 Claude Code 会话都从零开始：重新交代偏好、重新上传项目上下文、丢失此前对话积累的知识。Moltable 一次性解决：

| 场景 | 没有 Moltable | 有 Moltable |
|---|---|---|
| 新会话 / 新机器 | 全部重新解释 | 一次 `auto_provision` 恢复身份 |
| 上下文丢失 | “上周不是告诉过你吗……” | `search_memories` 即刻召回 |
| 角色切换 | 每次手动写提示词 | 一条命令切换 Persona |
| 项目上手 | 手动摸索工具与路径 | `discover_host` 自动发现 |

---

## Features / 功能

- **⚡ 30-second setup** — one command, zero config files to hand-edit
- **🧠 Persistent memory** — hybrid vector + full-text search across all your memories
- **🪪 Persona switching** — flip between code-review, architecture, debugging, and more
- **📦 Project environment discovery** — tools, paths, frameworks, knowledge bases
- **🔄 Cross-device sync** — your identity lives in the cloud, not in one laptop
- **🔌 Native MCP** — Claude Code auto-discovers `.mcp.json`; no plugin manager needed
- **🔒 Key-based auth** — simple `X-API-Key` header with `molt_`-prefixed keys

**中文.**
- **⚡ 30 秒安装** —— 一条命令，无需手改任何配置文件
- **🧠 持久记忆** —— 对全部记忆做向量 + 全文混合检索
- **🪪 人格切换** —— 在代码评审、架构、调试等角色间一键切换
- **📦 项目环境发现** —— 工具、路径、框架、知识库自动识别
- **🔄 跨设备同步** —— 身份存在云端，而不是某一台笔记本
- **🔌 原生 MCP** —— Claude Code 自动发现 `.mcp.json`，无需插件管理器
- **🔒 Key 认证** —— 简单 `X-API-Key` 头，`molt_` 前缀密钥

---

## Install / 安装

### Method 1 — One-command install (recommended) / 方式一：一键安装（推荐）

```bash
# Clone or copy this folder into your project, then run:
cd claude-code
./install.sh

# Or install into a specific project non-interactively:
./install.sh --project-dir ~/my-project --key molt_xxxxxxxx --yes
```

What the installer does / 安装器会做：

1. Detects your Claude Code project directory (`.claude/` or git root) / 自动检测项目目录
2. Creates **`.mcp.json`** (or merges the `moltable` server into an existing one, with a timestamped backup) / 创建或合并 `.mcp.json`（自动备份旧文件）
3. Prompts for your API key (get one at [moltable.ai/register](https://moltable.ai/register)) / 提示输入 API Key
4. Validates connectivity to `https://api.moltable.ai/mcp` / 校验 API 连通性
5. Persists `MOLTABLE_API_KEY` to your shell profile / 将密钥写入 shell 配置
6. Prints usage examples / 打印使用示例

Then **restart Claude Code** — it auto-discovers `.mcp.json` on startup.

### Method 2 — Manual / 方式二：手动

```bash
# 1. Copy the MCP config into your project root
cp claude-code/.mcp.json .mcp.json

# 2. Export your API key
export MOLTABLE_API_KEY="molt_xxxxxxxx"

# 3. Restart Claude Code, then ask:
#    "Use Moltable to auto-provision my identity"
```

### Get an API key / 获取 API Key

1. Register at **[https://moltable.ai/register](https://moltable.ai/register)** — free
2. Create an API key (starts with `molt_`)
3. Export it: `export MOLTABLE_API_KEY="molt_..."`

---

## Configuration / 配置

### Environment variable / 环境变量

| Variable / 变量 | Required / 必填 | Description / 说明 |
|---|---|---|
| `MOLTABLE_API_KEY` | ✅ | Your Moltable API key (`molt_...`) — referenced by `.mcp.json` via `${MOLTABLE_API_KEY}` |

### `.mcp.json` — auto-discovered by Claude Code

Claude Code loads `.mcp.json` from your **project root** or **user home** on startup. The config:

```json
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "https://api.moltable.ai/mcp",
      "headers": {
        "X-API-Key": "${MOLTABLE_API_KEY}"
      }
    }
  }
}
```

> `${MOLTABLE_API_KEY}` is expanded from your environment by Claude Code — the key never needs to be written into the JSON file itself. / `${MOLTABLE_API_KEY}` 由 Claude Code 从环境中展开，密钥无需写入 JSON 文件。

### Optional: `.claude/settings.json` / 可选：写入 settings

You can also pin the key via Claude Code settings (e.g. `~/.claude/settings.json`):

```json
{
  "env": {
    "MOLTABLE_API_KEY": "molt_xxxxxxxx"
  }
}
```

### Optional: install the `/moltable` command / 可选：安装 `/moltable` 命令

```bash
mkdir -p ~/.claude/commands
cp claude-code/MOLTABLE.md ~/.claude/commands/moltable.md
```

Now `/moltable` loads the full usage guide into any session — Claude knows exactly how to use Moltable.

---

## Usage examples / 使用示例

### First run: provision your identity / 首次运行：初始化身份

```
/ moltable            → loads the Moltable usage guide
"Provision my Moltable identity"   → Claude calls auto_provision
```

### Save & recall / 保存与召回

```
"Remember my preference: always use tabs, 2-space indentation"
"Save this as a memory: the deploy pipeline requires BUILD_ID"
"What do I prefer for code style?"           → get_preferences
"Do we have any memories about the auth flow?" → search_memories
```

### Personas / 人格切换

```
"Switch to my code-review persona"    → set_active_persona
"What personas do I have?"            → list_personas
```

### Project environment / 项目环境

```
"Discover this project's environment" → discover_host
```

---

## MCP tools / 工具一览

Moltable exposes **14 MCP tools**. Key ones / 核心工具：

| Tool / 工具 | Purpose / 用途 |
|---|---|
| `auto_provision` | One-click identity provisioning — restores preferences, personas & context / 一键身份初始化 |
| `save_preference` | Save a user preference / 保存用户偏好 |
| `get_preferences` | Retrieve all preferences / 获取全部偏好 |
| `save_memory` | Store a memory / 存储一条记忆 |
| `search_memories` | Hybrid vector + full-text search / 向量 + 全文混合检索 |
| `list_personas` | List available personas / 列出可用人格 |
| `set_active_persona` | Switch persona / 切换人格 |
| `discover_host` | Auto-discover project environment (tools, paths, frameworks) / 自动发现项目环境 |
| … | 6 more: project management, skills, archiving & updates / 其余：项目管理、技能、归档与更新 |

---

## Pricing / 价格

| Tier / 套餐 | Price / 价格 | Includes / 包含 |
|---|---|---|
| **Free / 免费** | $0 | 100 memories, 2 personas / 100 条记忆、2 个人格 |
| **Pro / 专业版** | ¥19 / month | 10K memories, unlimited personas / 1 万条记忆、无限人格 |

---

## Troubleshooting / 故障排查

| Issue / 问题 | Fix / 解决 |
|---|---|
| MCP server not loaded | Restart Claude Code after writing `.mcp.json`; check `Claude Code → MCP servers` shows `moltable` |
| `401 Unauthorized` | Key invalid or missing — verify `MOLTABLE_API_KEY` is exported and starts with `molt_` |
| Tools not showing up | Ensure `.mcp.json` is in the project root (or `~`), not a subfolder |
| Key leaks into git | Never commit `.mcp.json` with a literal key — always use `${MOLTABLE_API_KEY}`; add `.env` to `.gitignore` |

---

## Links / 链接

- **Register / 注册**: <https://moltable.ai/register>
- **GitHub / 源码**: <https://github.com/Moltable>
- **MCP Endpoint**: `https://api.moltable.ai/mcp`
- **Docs**: see `MOLTABLE.md` in this folder for the agent-facing usage guide

---

<p align="center">Made with ❤️ by the Moltable team · AI Identity Sync for everyone</p>
