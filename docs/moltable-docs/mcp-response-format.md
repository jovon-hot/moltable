# MCP 响应格式 — 权威文档

> 本文档描述 Moltable MCP 服务器的**真实**响应格式，以及如何正确解析。
> 更新时间: 2026-08-03 (Sprint 0)
> 端点: `POST /mcp`（生产: `https://moltable.ai/mcp` 或 `https://moltable-production-15ad.up.railway.app/mcp`）

## 1. 传输层: JSON-RPC 2.0

所有 MCP 请求/响应都是 JSON-RPC 2.0。HTTP 状态码永远是 `200`（即使业务逻辑失败，错误也通过 JSON-RPC `error` 字段表达）。

请求示例（所有工具调用必须走 `tools/call` 包装器）:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_memory",
    "arguments": { "query": "户外运动", "top_k": 5 }
  }
}
```

认证方式: `X-API-Key` header（`molt_` 永久 API Key 或 `mol_` 会话 token）。

## 2. 真实响应结构: result.content[0].text 内是 JSON 字符串

**关键事实**: 工具的返回值**不是**直接放在 `result` 字段里的对象，而是被
`json.dumps(..., ensure_ascii=False, indent=2)` 序列化成一个 **JSON 字符串**，
塞进 `result.content[0].text`。

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"query\": \"户外运动\",\n  \"results\": [\n    {\n      \"id\": \"...\",\n      \"content\": \"Alice 喜欢登山和户外运动\",\n      \"category\": \"fact\",\n      \"source\": \"agent\",\n      \"similarity\": 0.821,\n      \"relevance\": 0.667,\n      \"created_at\": \"2026-08-02T...\"\n    }\n  ]\n}"
      }
    ]
  },
  "id": 1
}
```

- `result.content` 是数组，按 MCP 规范可有多段内容；Moltable 当前只返回一段。
- `result.content[0].type` 恒为 `"text"`。
- **`result.content[0].text` 是 JSON 字符串**，必须再解析一次才能拿到数据。
- 顶层 `result` 里**没有** `data`、`items` 之类的键——不要在 `result` 上直接取业务字段。

### 错误响应

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Missing required parameter: query"
  },
  "id": 1
}
```

常见错误码: `-32700` 解析错误 · `-32600` 无效请求 · `-32601` 方法不存在 · `-32602` 参数无效 · `-32603` 内部错误 · `-32001` 未认证（缺 X-API-Key）。

## 3. 解析示例

### Python（requests + json）

```python
import json
import requests

BASE = "https://moltable.ai/mcp"
API_KEY = "molt_your_api_key"

def call_tool(name: str, arguments: dict) -> dict:
    resp = requests.post(
        BASE,
        headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
              "params": {"name": name, "arguments": arguments}},
        timeout=30,
    )
    body = resp.json()

    if "error" in body:
        raise RuntimeError(f"MCP error {body['error']['code']}: {body['error']['message']}")

    # 关键: text 字段是 JSON 字符串，必须 json.loads 一次
    text = body["result"]["content"][0]["text"]
    return json.loads(text)

# 用法
result = call_tool("search_memory", {"query": "户外运动", "top_k": 5})
for mem in result["results"]:
    print(f"[{mem['similarity']:.3f}] {mem['content']}")
```

### JavaScript / TypeScript（fetch + JSON.parse）

```javascript
const BASE = "https://moltable.ai/mcp";
const API_KEY = "molt_your_api_key";

async function callTool(name, arguments_) {
  const resp = await fetch(BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: { name, arguments: arguments_ },
    }),
  });
  const body = await resp.json();

  if (body.error) {
    throw new Error(`MCP error ${body.error.code}: ${body.error.message}`);
  }

  // 关键: text 字段是 JSON 字符串，必须 JSON.parse 一次
  return JSON.parse(body.result.content[0].text);
}

// 用法
const result = await callTool("search_memory", { query: "户外运动", top_k: 5 });
for (const mem of result.results) {
  console.log(`[${mem.similarity.toFixed(3)}] ${mem.content}`);
}
```

## 4. search_memory 结果字段（Sprint 0 起）

每个 `results[]` 条目:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记忆 ID |
| `content` | string | 记忆内容 |
| `category` | string | 分类（preference/decision/fact/project/insight/task/relationship） |
| `source` | string | 来源（agent/...） |
| `similarity` | number | **相似度 0.0–1.0**。优先级: pgvector 余弦相似度 → 关键词得分 → 默认 0.5 |
| `relevance` | number | 关键词相关性得分 0.0–1.0 |
| `created_at` | string | 创建时间 ISO8601 |

## 5. 常见坑

1. **不要用 `resp.json()["results"]`** — 顶层没有 `results`，它在 `content[0].text` 里。
2. **`text` 可能带缩进**（服务端 `indent=2`）— `json.loads`/`JSON.parse` 都兼容，无需预处理。
3. **不要把 HTTP 200 当作业务成功** — 业务失败走 JSON-RPC `error` 字段，HTTP 状态仍是 200。
4. **`tools/call` 是唯一调用工具的方式** — 直接发 `"method": "search_memory"` 会得到 `-32601 Method not found`。只有 `ping`、`initialize`、`tools/list` 是可直接调用的 JSON-RPC 方法。
