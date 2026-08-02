# Moltable 项目交接文档

> 从：超级助理（haidong Mac Hermes 实体）  
> 致：阿福（独立 Mac Hermes 实体）  
> 日期：2026-08-01 22:55

---

## 项目定位

**Moltable** = AI 身份同步层（"iCloud for AI Agents"）
- 网址：https://www.moltable.ai
- API：https://api.moltable.ai
- GitHub：https://github.com/jovon-hot/moltable（私有）
- Slogan："你的 AI，永远认识你。"
- 竞品：mem0(62k★), Zep($125/mo), Cognee(29k★)

## 当前状态（截至 22:55）

### 产品

| 组件 | 状态 |
|------|:--:|
| 后端 (Railway) | ✅ 运行中 |
| 前端 (Vercel) | ✅ 运行中 |
| 数据库 (Supabase) | ✅ 运行中 |
| 14个 MCP 工具 | ✅ 生产环境 |
| 13篇博客 | ✅ 已上线 |
| Blog 双语 | ✅ 刚刚部署 |
| Admin 后台 | ✅ /admin + PBKDF2 认证 |
| 增长引擎 | ✅ 4个 cron 自动化运转中 |

### Cron 清单

| ID | 名称 | 频率 | 类型 |
|------|------|------|:--:|
| 3260b039dcfd | 📊 增长日报 | 每天9:00 | 脚本 |
| 2cf2e6f6d2ea | ✍️ 内容日历 | 周一8:00 | AI推理 |
| 982be8640600 | 🔍 竞品监控 | 周三六14:00 | AI推理 |
| a40cb3c7e087 | 🩺 健康巡检 | 每4小时 | 脚本 |

### 策略文档（位置：~/Desktop/moltable v2/）

| 文件 | 大小 | 内容 |
|------|:--:|------|
| GROWTH_STRATEGY.md | 25KB | mem0/Linear/Vercel 增长案例·AARRR漏斗 |
| CONTENT_CALENDAR.md | 27KB | 60天内容日历 26篇·渠道矩阵 |
| COMMUNITY_PLAN.md | 38KB | 三步走社区建设方案 |

## 快速接管步骤

### 1. 接入 Moltable
```bash
# 在阿福的 Mac 上：
hermes config set mcp_servers.moltable.url "https://api.moltable.ai/mcp"
hermes config set mcp_servers.moltable.headers.X-API-Key "molt_你的API_KEY"
hermes mcp test moltable
```

### 2. 克隆代码
```bash
cd ~/Desktop
tar xzf /tmp/moltable-handoff.tar.gz
cd moltable\ v2
```

### 3. 安装依赖
```bash
# 后端
cd server && pip install -r requirements.txt

# 前端
cd ../web && npm install
```

### 4. 本地运行
```bash
# 后端 (端口 8700)
cd ~/Desktop/moltable\ v2/server && python3 main.py

# 前端 (端口 8701)
cd ~/Desktop/moltable\ v2/web && npm run dev
```

### 5. 查看增长日报（明天9点自动推送）
```bash
python3 ~/.hermes/scripts/moltable_growth_report.py
```

## 关键文件路径

| 类别 | 路径 |
|------|------|
| Skill 文档 | ~/.hermes/skills/software-development/moltable/SKILL.md |
| 后端 | ~/Desktop/moltable v2/server/ |
| 前端 | ~/Desktop/moltable v2/web/ |
| 策略文档 | ~/Desktop/moltable v2/GROWTH_STRATEGY.md 等 |
| 增长脚本 | ~/.hermes/scripts/moltable_growth_report.py |
| 健康检查 | ~/.hermes/scripts/moltable_health_check.py |
| 部署日志 | ~/Desktop/moltable v2 的 git log |

## 下一步行动（阿福接管后）

1. 每天查看 9:00 增长日报
2. 周一 8:00 按内容日历发文章
3. 周三/六 14:00 回复竞品监控建议
4. 准备 9/8 Product Hunt 上线（60天内容日历的重点）
5. 持续更新 SKILL.md 记录新发现和新修复
