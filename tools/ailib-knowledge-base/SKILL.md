---
name: ailib-knowledge-base
description: 一键部署ailib知识库——目录+x-core+认知流水线+Agent规则。触发：建知识库、搭ailib。
category: knowledge
---

# ailib 知识库一键部署

## 触发条件

用户说"建知识库"、"搭ailib"、"部署知识库"、"我要一个会考试的知识库"、或讨论知识管理系统建设时。

## 部署流程

### 步骤 1：确定路径

问用户知识库放哪里。默认 `~/Desktop/ailib/`。

### 步骤 2：创建目录

```bash
TARGET="$HOME/Desktop/ailib"
mkdir -p "$TARGET"/{00-raw,01-pending}
mkdir -p "$TARGET"/02-entities/{people,companies,products}
mkdir -p "$TARGET"/03-intel/{market,tech,competitors}
mkdir -p "$TARGET"/04-reports/{analysis,research,review}
mkdir -p "$TARGET"/05-workspace
mkdir -p "$TARGET"/{10-journal,20-templates,30-scripts}
mkdir -p "$TARGET"/99-cognition/{concepts,frameworks,methodologies,domains}
mkdir -p "$TARGET"/x-core/{principles,decisions,patterns,identity,operating}
```

### 步骤 3：写入 AGENTS.md

写入以下内容到 `$TARGET/AGENTS.md`：

```
# AGENTS — ailib 知识库操作规范

## 目录结构
00-raw/ 原始资料 · 01-pending/ 待处理 · 02-entities/ 实体
03-intel/ 情报 · 04-reports/ 报告 · 05-workspace/ 工作区
99-cognition/ 认知层 · x-core/ 操作系统

## Ingest 流程
新资料 → 00-raw → 01-pending → 分析提取 →
  ├─ 实体 → 02-entities · 情报 → 03-intel
  ├─ 报告 → 04-reports · 认知 → 99-cognition

## x-core 规则 (v2)
- 禁止 Agent 写入 x-core
- 仅用户说"吸收到 x-core"时可执行单文件迁移
- Agent 可标记 #候选，不可自动迁移

### 范围限定
x-core 只接受四类：Principles · Frameworks · Decision Patterns · Identity Anchors

### 吸收标准（三条铁律）
1. 已用它做过决策
2. 不看笔记能复述核心  
3. 在至少两个场景验证有效

### 证据驱动
不再使用 AI 评分。Agent 收集可追踪的行为证据（跨域复用·无提示复述·否定使用·时效·教学）。满足 4/5 条 → 提请确认 → 用户说"吸收" → 迁移。

### 认知流水线 (v2)
1. 对话/入库 → 提取认知 → 99-cognition
2. 证据驱动 → 标记 #候选 + 证据日志
3. 碎片化验证（7-10天·四轮）→ 迁移 x-core
4. 闭环激活：_ACTIVE.md 调度 → 对话中主动点亮节点

### 步骤 4：写入 x-core

创建 `$TARGET/x-core/_GATE.md`：
```
# x-core · 写入禁令 v2

## 范围限定
x-core 只接受四类：Principles · Frameworks · Decision Patterns · Identity Anchors

## 三条铁律
1. 用过 — 已用它做过决策
2. 记得 — 不看笔记能复述核心
3. 复用 — 在至少两个场景验证有效

## 证据驱动
Agent 收集可追踪的行为证据（跨域复用·无提示复述·否定使用·时效·教学）
满足 4/5 → 提请用户确认 → 用户说"吸收" → 迁移

## 遗忘机制
年审制 + 15节点上限

## Agent 禁令
禁止写入 x-core。唯一例外：用户说"吸收到 x-core"。
允许：读取上下文、标记 #候选、收集证据。
```

创建 `$TARGET/x-core/_PIPELINE.md`：
```
# 认知流水线 v2

阶段一：提取 — 对话中识别思维模式 → 写入 99-cognition
阶段二：标记候选（证据驱动）— 观察跨域复用/无提示复述/否定使用/时效/教学 → #候选 + 证据日志
阶段三：验证吸收（碎片化）— 4 Rounds 分散在 7-10 天完成，证据达标(4/5条) → 用户确认 → x-core
阶段四：闭环激活 — _ACTIVE.md 调度，对话中主动点亮节点

Agent 角色：证据采集员 · 激活调度器 · 年审执行者
禁止：替用户判定"是否内化" · 自动迁移到 x-core
```

### 步骤 5：写入 README.md

写入用户友好的知识库说明，包含目录结构和操作流程。

### 步骤 6：写入模板

在 `20-templates/` 下创建四个模板文件：
- `entity.md` — 实体节点模板
- `cognition.md` — 认知节点模板
- `report.md` — 报告节点模板
- `principle.md` — x-core 原则节点模板

模板格式：`# 标题\n\n## 定义\n\n## 来源\n\n## 证据\n\n## 关联\n`

### 步骤 7：确认

运行 `find "$TARGET" -name "*.md" | wc -l` 确认文件数，向用户报告。

## 部署后 Agent 行为

1. **提取认知**：对话中识别思维模式 → `99-cognition/`
2. **标记候选**：观察内化证据 → `#候选` + 证据日志
3. **主动考试**：满 3 条证据 → 提议学习会话(4 Rounds)
4. **禁止写入 x-core**：除非用户确认"吸收"

## 用户命令

| 命令 | 行为 |
|------|------|
| "检查候选" | 列出候选节点及证据 |
| "学习 XX" | 启动学习会话 |
| "验证 XX" | 直接考试 |
| "吸收 XX" | 直接迁移到 x-core |
