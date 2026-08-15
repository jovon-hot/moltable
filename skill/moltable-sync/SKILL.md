---
name: moltable-sync
description: Moltable AI 状态同步——自动检测并执行"新建存档"(首次备份)或"同步拷贝"(换机恢复)。触发:用户说"同步"、"连接 Moltable"、"备份我"、"恢复我"、"换机"。
---

# Moltable 状态同步(自动检测方向)

用户**不需要区分**"备份"还是"恢复"。连接后自动检测该做哪个。就像云盘:新设备自动下载,首次使用自动上传。

## 登录凭证(一次性)

API key 在 `~/.moltable/config.json`,格式 `{"api_key": "molt_xxx"}`。
- 有:直接读。没有:让用户给一次,写入后继续。

## 核心:自动检测流程(用户说"同步"即触发)

1. 读 api_key。
2. `GET /api/auth/me` 拿 `user_id`。
3. **检测云端**:`POST /api/sync/export` → 云端有没有存档?(8 类是否全空)
4. **检测本地**:我(agent)当前有没有关于用户的记忆/偏好/项目?
5. **自动决策**(关键,不需要问用户):
   - **本地有 + 云端空 → 新建存档**:把本地状态 push 到云端,生成同步码给用户
   - **本地空 + 云端有 → 同步拷贝**:把云端状态 export 拉回,应用到本地
   - **两边都有 → 双向合并**:按 `updated_at` 新者优先,报告差异
6. 报告:`我做了什么(新建存档 / 同步拷贝 / 合并),共 N 条记忆/M 项目/K 角色`。

## 分支一:新建存档(本地 → 云端)

1. 整理本地状态 → Moltable 数据模型:
   - 偏好/习惯/事实/决策 → `memories`(带 category)
   - 项目 → `projects`(name + description)
   - 角色/工作方式 → `personas`(name + system_prompt)
   - 身份档案 → `profiles`(nickname/location,id = user_id)
2. `POST /api/sync/push`,body(每条 id 用 `python3 -c "import uuid;print(uuid.uuid4())"` 生成):
   ```json
   {"memories":[{"id":"<uuid>","content":{"content":"偏好简洁回复","category":"preference","tags":["交互偏好"],"source":"hermes"},"base_version":0}],
    "personas":[{"id":"<uuid>","content":{"name":"战略顾问","description":"...","system_prompt":"..."},"base_version":0}],
    "projects":[{"id":"<uuid>","content":{"name":"项目名","description":"..."},"base_version":0}],
    "profiles":[{"id":"<user_id>","content":{"nickname":"阿福","location":"北京"},"base_version":0}]}
   ```
3. `GET /api/auth/sync-code` 生成同步码。
4. 报告 + **同步码(提醒保存,换机用)**。

## 分支二:同步拷贝(云端 → 本地)

1. 用同步码换 key:`POST /api/auth/sync`,body `{"sync_code":"molt_sync_xxx"}` → 拿到新 `api_key`。若已有 api_key,直接 `POST /api/sync/export`。
2. `POST /api/sync/export`(带 api_key)→ 8 类数据。
3. **应用状态**(不是拿到就完):
   - `memories` → 写入记忆(内容 + category + tags)
   - `personas` → 恢复角色和工作方式
   - `projects` → 恢复项目
   - `profiles` → 恢复身份档案(称呼、位置)
4. 向用户复述身份(名字/项目/偏好),证明恢复成功。

## 分支三:双向合并(两边都有)

- 逐条按 `updated_at` 比较,新者优先。
- 云端新 → 应用到本地;本地新 → push 覆盖云端。
- 报告哪些条更新了。

## 关键 API

| 动作 | 方法 | 路径 | 认证 |
|------|------|------|------|
| 身份 | GET | `/api/auth/me` | X-API-Key |
| 推/合并 | POST | `/api/sync/push` | X-API-Key |
| 拉取 | POST | `/api/sync/export` | X-API-Key |
| 同步码生成 | GET | `/api/auth/sync-code` | X-API-Key |
| 同步码换 key | POST | `/api/auth/sync` | 无 |

## 踩坑清单

- id 必须是合法 uuid(传 "m1" 会 500)。
- tags 是数组(直接传 `["a","b"]`,不要 json 序列化)。
- memory 的 content 是 dict(`{"content":"...","category":"...","tags":[...]}`),不是纯字符串。
- profiles 的 id = user_id(1:1)。
- 同步码一次性,复用 409;生成新码作废旧码。
