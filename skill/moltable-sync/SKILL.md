---
name: moltable-sync
description: Moltable AI 状态同步——自动检测并执行"新建存档"(首次备份)或"同步拷贝"(换机恢复)。触发:用户说"同步"、"连接 Moltable"、"备份我"、"恢复我"、"换机"。
---

# Moltable 状态同步(自动检测方向 + 幂等)

用户**不需要区分**"备份"还是"恢复"。连接后自动检测该做哪个。重复说"同步"不会产生重复数据(靠 state.json 幂等)。

## 登录凭证与本地状态(一次性)

- API key:`~/.moltable/config.json` 的 `{"api_key": "molt_xxx"}`。没有就让用户给一次。
- **幂等映射**:`~/.moltable/state.json`,记录「本地内容 hash → 云端 id/version/updated_at」。首次为空 `{}`。

## 核心:自动检测流程(用户说"同步"即触发)

1. 读 api_key + state.json(没有就初始化为空对象)。
2. `GET /api/auth/me` 拿 `user_id`。
3. **检测云端**:`POST /api/sync/export` → 8 类是否全空?
4. **检测本地**:枚举本地状态(Hermes 记忆读 `~/.hermes/memories/*.md` 计数 + 最近修改时间;偏好/项目/角色从记忆里整理)。
5. **自动决策**(确定性规则,不是碰运气):
   | 本地 | 云端 | 动作 |
   |------|------|------|
   | 有 | 空 | 新建存档 |
   | 空 | 有 | 同步拷贝 |
   | 有 | 有 | 双向合并(幂等) |
   | 空 | 空 | 报告"当前无内容可同步",结束 |
6. 执行 + 更新 state.json + 报告。

## 分支一:新建存档(本地 → 云端)

1. 整理本地状态 → Moltable 数据模型(memories/personas/projects/profiles)。
2. 每条生成 uuid,`base_version: 0`,push。
3. `GET /api/auth/sync-code` 生成同步码(提醒保存,换机用)。
4. push 成功后,把「内容 hash → cloud_id/version」写进 state.json。

## 分支二:同步拷贝(云端 → 本地)

1. 有同步码:先 `POST /api/auth/sync` 换 key(或直接用 config.json 的 key)。
2. `POST /api/sync/export` 拉 8 类。
3. 应用:memories → 记忆、personas → 角色、projects → 项目、profiles → 身份档案。
4. **把拉回的 id/version 全部写入 state.json**(这样之后同步是幂等的)。
5. 复述身份证明恢复成功。

## 分支三:双向合并(幂等,两边都有)

1. `POST /api/sync/export` 拉云端全量。
2. 对每条本地内容计算 hash,查 state.json:
   - **命中(之前同步过)**:用 state.json 里的 `cloud_id` + 云端最新 `version` 作为 `base_version`,push 更新。
   - **未命中(新内容)**:生成新 uuid,`base_version: 0`,push 新建。
3. push 返回 `conflicts` 非空时,**明确报告冲突条目给用户**(内容 + 双方版本),不要静默忽略、不要瞎猜覆盖。可以 `POST /api/sync/resolve` 解决(传入冲突 id + 选择的内容)。
4. 更新 state.json。

## 分支四:两边都空

报告「当前本地无状态、云端无存档,无需同步」,结束。不要自由发挥。

## 关键 API

| 动作 | 方法 | 路径 | 认证 |
|------|------|------|------|
| 身份 | GET | `/api/auth/me` | X-API-Key |
| 推/合并 | POST | `/api/sync/push` | X-API-Key |
| 拉取 | POST | `/api/sync/export` | X-API-Key |
| 解决冲突 | POST | `/api/sync/resolve` | X-API-Key |
| 同步码生成 | GET | `/api/auth/sync-code` | X-API-Key |
| 同步码换 key | POST | `/api/auth/sync` | 无 |

## push 数据结构(每条 id 用 `python3 -c "import uuid;print(uuid.uuid4())"` 生成)

```json
{"memories":[{"id":"<uuid>","content":{"content":"偏好简洁回复","category":"preference","tags":["交互偏好"],"source":"hermes"},"base_version":0}],
 "personas":[{"id":"<uuid>","content":{"name":"战略顾问","description":"...","system_prompt":"..."},"base_version":0}],
 "projects":[{"id":"<uuid>","content":{"name":"项目名","description":"..."},"base_version":0}],
 "profiles":[{"id":"<user_id>","content":{"nickname":"阿福","location":"北京"},"base_version":0}]}
```

## 踩坑清单

- id 必须是合法 uuid(传 "m1" 会 500)。
- tags 是数组(直接传 `["a","b"]`,不要 json 序列化)。
- memory 的 content 是 dict(`{"content":"...","category":"...","tags":[...]}`),不是纯字符串。
- profiles 的 id = user_id(1:1)。
- 同步码一次性,复用 409;生成新码作废旧码。
- **base_version 必须用 export 返回的云端 version,不是写死 0**(否则 three_way 永远冲突)。
- state.json 是幂等的关键:每次 push/pull 后都要更新,否则重复同步制造重复数据。
