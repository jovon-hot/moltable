<p align="center">
  <img src="web/public/logo-brand.svg" width="120" alt="Moltable" />
</p>

<h1 align="center">Moltable — Agent Soul Backup</h1>
<p align="center"><strong>换 Agent，不换灵魂。</strong> · <strong>Switch agents, keep your soul.</strong></p>

<p align="center">
  <a href="https://github.com/jovon-hot/moltable/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" /></a>
  <a href="https://www.moltable.ai"><img src="https://img.shields.io/badge/Website-moltable.ai-4338CA" /></a>
  <a href="https://www.moltable.ai/blog"><img src="https://img.shields.io/badge/Blog-37_posts-FB6B4B" /></a>
</p>

---

Moltable is the **versioned backup repository for your AI agent's soul**. One command packs your tuned AI — SOUL, skills, MCP configs, memories — into a versioned, deduplicated backup. Switch frameworks or machines without losing the agent you tuned.

Moltable 是你调教 AI 的**灵魂资产版本仓库**。一条命令把你调教的成果——SOUL、Skills、MCP 配置、记忆——打包成版本化、去重的备份。换框架、换电脑，你调教的 AI 都不会丢。

---

## 一条命令备份

```bash
curl -sL https://moltable.ai/install.sh | bash

moltable backup init        # 生成配置
moltable backup push        # 打包上传（快照 + 版本号 + 增量去重）
moltable backup pull        # 下载还原
moltable backup sources     # 查看备份源
moltable backup add-ref ailib ~/Desktop/ailib   # 引用外部知识库一并备份
```

备份的是你的「灵魂资产」，自动排除流水账（`state.db` / WAL / FTS 索引）和密钥（`.env` / `*.key`）：

```
SOUL.md · AGENTS.md · USER.md · config.yaml（MCP 配置，密钥脱敏）· memories/ · skills/
```

## 核心能力

| | 说明 |
|---|---|
| **灵魂备份** | 文件级打包 = bundle + manifest + CAS（内容寻址去重）+ 对象存储 |
| **版本管理** | 每个备份源独立版本库，快照 + 版本号，随时回滚到任意历史版本 |
| **增量去重** | 内容寻址（sha256），未变化的文件只传一次 |
| **引用同步** | 你引用的知识库、内容来源一并备份（`add-ref`） |
| **你拥有数据** | 随时导出或删除，我们永远不用你的数据训练模型 |

## 定价

| | Free | Pro | Ultra |
|---|---|---|---|
| 备份源 | 3 | 10 | 100 |
| 存储 | 100MB | 1GB | 10GB |
| 价格 | $0 | **$3/月** | **$5/月** |
| | [免费开始](https://moltable.ai/register) | [升级 Pro](https://moltable.ai/register) | [升级 Ultra](https://moltable.ai/register) |

无需信用卡 · 随时取消。

## 支持框架

**Hermes · OpenClaw · Claude · Codex** —— 每个框架实例是一个独立备份源。跨框架迁移（用你自己的 LLM 翻译灵魂资产）即将推出。

## Self-Host

```bash
git clone https://github.com/jovon-hot/moltable.git
cd moltable/server
pip install -r requirements.txt
python main.py
```

Licensed under **MIT**. Your soul belongs to you — always.

---

<p align="center">
  <a href="https://www.moltable.ai">🌐 Website</a> ·
  <a href="https://www.moltable.ai/docs">📚 Docs</a> ·
  <a href="https://www.moltable.ai/blog">📝 Blog</a> ·
  <a href="https://www.moltable.ai/faq">❓ FAQ</a>
</p>

<p align="center"><sub>MIT License · Built with ❤️ in Beijing</sub></p>
