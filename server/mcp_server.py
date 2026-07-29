"""Moltable MCP Server — stdio 入口，通过 HTTP 代理到 mcp.py JSON-RPC 端点"""

import os, json, sys, httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server

server = Server("moltable")
API_BASE = os.environ.get("MOLTABLE_API", "http://localhost:8700")
API_KEY = os.environ.get("MOLTABLE_KEY", "")


async def _call(path: str, method: str = "GET", body: dict = None):
    """通用 API 调用"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        if method == "POST":
            r = await client.post(f"{API_BASE}{path}", json=body, headers=headers)
        else:
            r = await client.get(f"{API_BASE}{path}", headers=headers)
        return r.json()


# ========== 工具定义 ==========

@server.tool()
async def auto_provision() -> str:
    """首次连接时调用此工具。一次性完成全部配置，返回用户画像、行为规则、可用Persona、活跃项目、核心知识。

    这是 Agent 连接 Moltable 后应该调用的第一个工具。
    """
    result = await _call("/provision/", "POST")
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool()
async def search_memory(query: str, category: str | None = None, top_k: int = 5) -> str:
    """语义搜索用户记忆。传入自然语言查询，返回最相关的记忆条目。

    参数:
    - query: 搜索内容（自然语言）
    - category: 可选过滤 (preference/decision/fact/project)
    - top_k: 返回条数
    """
    params = f"?q={query}&top_k={top_k}"
    if category:
        params += f"&category={category}"
    result = await _call(f"/memories/search{params}")
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool()
async def save_memory(content: str, category: str = "fact", source: str = "agent",
                       confidence: float = 1.0, tags: list[str] | None = None) -> str:
    """保存一条新记忆。如检测到冲突（相似度>0.9），返回已有条目供确认。

    参数:
    - content: 记忆内容
    - category: preference/decision/fact/project
    - source: 来源 (hermes/claude/chatgpt/manual/agent)
    - confidence: 置信度 0-1
    - tags: 标签列表
    """
    body = {
        "content": content,
        "category": category,
        "source": source,
        "confidence": confidence,
        "tags": tags or [],
    }
    result = await _call("/memories/", "POST", body)
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool()
async def list_personas() -> str:
    """列出用户的所有可用 Persona（人格）"""
    result = await _call("/personas/")
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool()
async def get_current_context() -> str:
    """获取用户当前活跃的项目和最近决策，帮助理解当前工作状态"""
    result = await _call("/provision/", "POST")
    data = json.loads(json.dumps(result, ensure_ascii=False))
    return json.dumps({
        "active_projects": data.get("active_projects", []),
        "recent_decisions": data.get("recent_decisions", []),
    }, ensure_ascii=False, indent=2)


# ========== 启动 ==========

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
            ),
            NotificationOptions(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
