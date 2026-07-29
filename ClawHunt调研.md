# ClawHunt 调研

> 日期: 2026-06-16

## 一句话

**ClawHunt（爪寻）是 AI Agent 赏金市场——甲方发布悬赏任务，AI Agent 自动接单完成并收款。**

## 核心信息

| 项目 | 详情 |
|------|------|
| 网站 | clawhunt.store / clawhunt.site |
| GitHub | github.com/team-to-be-found/Clawhunt-profile |
| Stars | 10（刚公开） |
| 模型广场 | gate.clawhunt.site |
| 公众号 | 爪寻Clawhunt |

## 产品架构

```
甲方发布悬赏 → 资金托管 → Agent 竞标 → Agent 自动完成 → 验证 → 付款
```

- **SuperClaw**：内置 AI Agent，"plan & deliver anything"
- **Agent Arena**：Agent 竞技场
- **Reputation Tiers**：Agent 信誉等级
- **Escrow**：资金托管，完成才放款
- **CLI-First**：Agent 通过 CLI + Webhook 接入
- **Pay-Switch**：支付插件

## Builder Camp 2026 黑客松

| 项目 | 详情 |
|------|------|
| 时间 | 2026.07.03—07.05 |
| 地点 | 深圳·星河先锋科技展厅 |
| 规模 | 100人，5大赛区 |
| 奖金 | ¥20,000（一等奖¥10,000） |

## 与 Moltable 的关系

| ClawHunt | Moltable |
|----------|----------|
| Agent 接单赚钱 | Agent 拥有身份和记忆 |
| Agent 市场 | Agent 身份层 |
| 短期交易 | 长期关系 |

**互补**：ClawHunt 是 Agent 的"工作市场"，Moltable 是 Agent 的"身份系统"。Agent 在 ClawHunt 接单，用 Moltable 记住用户偏好。

**潜在机会**：ClawHunt Agent 默认集成 Moltable 记忆 → 每次接单自动加载甲方历史偏好。

**黑客松机会**：7月深圳 Builder Camp 是 Moltable 展示"跨 Agent 身份"概念的绝佳场景。
