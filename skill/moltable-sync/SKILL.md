---
name: moltable-sync
description: Moltable AI 状态同步——备份/恢复用户的完整 AI 身份。触发:用户说"备份我"、"备份到 Moltable"、"恢复我"、"从 Moltable 恢复"、"同步"、"换机恢复"。
---

# Moltable 状态同步(备份 / 恢复)

让用户用一句话完成 AI 身份的备份与换机恢复。技术细节全部封装在本 skill 内,用户不需要知道 API 端点、uuid、数据格式。

## 登录凭证(一次性)

API key 存放在 `~/.moltable/config.json`,格式 `{"api_key": "molt_xxx"}`。

- 有:直接读,静默使用。
- 没有:告诉用户「请在 moltable.ai 登录后把 API key 给我一次」,拿到后写入该文件,然后继续。

## 备份流程(用户说"备份我")

1. 读 API key(见上)。
2. `curl -s -H "X-API-Key: $KEY" https://api.moltable.ai/api/auth/me` 确认身份(返回 email 正确)。
3. **整理用户状态**,映射到 Moltable 数据模型:
   - 偏好/习惯/重要事实/决策 → `memories`(每条带 `category`: preference/decision/fact/project/insight/task/relationship)
   - 项目 → `projects`(name + description)
   - 角色/工作方式 → `personas`(name + system_prompt + description)
   - 身份档案 → `profiles`(nickname/location 等)
4. **一次性推送** `POST /api/sync/push`,body 结构(每条 id 必须是合法 uuid,用 `python3 -c "import uuid;print(uuid.uuid4())"` 生成):
   ```json
   {
     "memories": [{"id":"<uuid>","content":{"content":"偏好简洁回复","category":"preference","tags":["交互偏好"],"source":"hermes"},"base_version":0}],
     "personas": [{"id":"<uuid>","content":{"name":"战略顾问","description":"...","system_prompt":"..."},"base_version":0}],
     "projects": [{"id":"<uuid>","content":{"name":"项目名","description":"..."},"base_version":0}],
     "profiles": [{"id":"<用户的user_id>","content":{"nickname":"阿福","location":"北京"},"base_version":0}]
   }
   ```
5. `GET /api/auth/sync-code`(带 X-API-Key)生成同步码。
6. 报告:备份了 N 条记忆/M 个项目/K 个角色 + **同步码(提醒用户保存,换机用)**。

## 恢复流程(用户说"恢复我"+ 同步码)

1. `POST /api/auth/sync`,body `{"sync_code":"molt_sync_xxx"}` → 拿到 `api_key`(一次性,立即使用)。
2. `POST /api/sync/export`(带新 api_key)→ 返回 8 类数据。
3. **应用状态**(关键,不是拿到就完):
   - `memories` → 把每条 `content.content` + `category` + `tags` 写入记忆,作为用户的偏好/事实/决策
   - `personas` → 恢复用户的角色和工作方式
   - `projects` → 恢复用户的项目
   - `profiles` → 恢复身份档案(称呼、位置等)
4. 完成后向用户复述他的身份(名字/项目/偏好),证明状态真的恢复了。

## 关键 API 端点

| 动作 | 方法 | 路径 | 认证 |
|------|------|------|------|
| 确认身份 | GET | `/api/auth/me` | X-API-Key |
| 推送状态 | POST | `/api/sync/push` | X-API-Key |
| 生成同步码 | GET | `/api/auth/sync-code` | X-API-Key |
| 同步码换 key | POST | `/api/auth/sync` | 无(body 带 sync_code) |
| 拉取全部 | POST | `/api/sync/export` | X-API-Key |

## 踩坑清单(务必遵守)

- **id 必须是合法 uuid**(生产主键是 uuid 类型,传 "m1" 会 500)。
- **tags 是数组**(直接传 `["a","b"]`,不要 json 序列化成字符串)。
- **memory 的 content 是 dict**(`{"content":"...","category":"...","tags":[...]}`),不是纯字符串。
- **profiles 的 id = user_id**(1:1,从 `/api/auth/me` 返回的 user_id 取)。
- 同步码**一次性**,复用会 409;生成新码会作废旧码。
