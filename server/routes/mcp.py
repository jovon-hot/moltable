from __future__ import annotations
"""Moltable MCP HTTP Transport — JSON-RPC 2.0 协议端点

MCP (Model Context Protocol) 2024-11-05 规范实现:
- POST /mcp — 主 JSON-RPC 2.0 入口
- 支持: tools/list, tools/call, initialize, ping
- 认证: X-API-Key header (复用 auth.get_user)
"""

import json
from datetime import datetime, timezone
import traceback
from typing import Any

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app_state import limiter, supabase, get_store
from routes.auth import get_user, authenticate_agent
from services.embedding import embed
from services.verifier_service import get_verifier

router = APIRouter(tags=["mcp"])


# ═══════════════════════════════════════════════════════════
# JSON-RPC 2.0 数据模型
# ═══════════════════════════════════════════════════════════

class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 请求"""
    jsonrpc: str = Field(default="2.0", pattern=r"^2\.0$")
    method: str = Field(..., min_length=1, max_length=200)
    params: dict[str, Any] | list[Any] | None = None
    id: str | int | float | None = None


class JSONRPCError(Exception):
    """JSON-RPC 标准错误"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data


# ── JSON-RPC 2.0 标准错误码 ─────────────────────────────
PARSE_ERROR = -32700       # 解析错误
INVALID_REQUEST = -32600   # 无效请求
METHOD_NOT_FOUND = -32601  # 方法不存在
INVALID_PARAMS = -32602    # 无效参数
INTERNAL_ERROR = -32603    # 内部错误
# 自定义错误码
AUTH_ERROR = -32001        # 认证失败
TOOL_ERROR = -32000        # 工具调用错误
SERVER_NOT_INITIALIZED = -32002  # 尚未初始化


def jsonrpc_error(code: int, message: str, id_val: Any = None, data: Any = None) -> dict:
    """构建 JSON-RPC 2.0 错误响应"""
    resp = {
        "jsonrpc": "2.0",
        "error": {"code": code, "message": message},
    }
    if id_val is not None:
        resp["id"] = id_val
    else:
        resp["id"] = None
    if data is not None:
        resp["error"]["data"] = data
    return resp


def jsonrpc_success(result: Any, id_val: Any) -> dict:
    """构建 JSON-RPC 2.0 成功响应"""
    return {"jsonrpc": "2.0", "result": result, "id": id_val}


# ═══════════════════════════════════════════════════════════
# MCP 工具定义
# ═══════════════════════════════════════════════════════════

MCP_TOOLS = [
    {
        "name": "search_memory",
        "description": "语义搜索用户记忆。传入自然语言查询，返回最相关的记忆条目。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索内容（自然语言查询）",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回结果数量（1-50）",
                    "default": 5,
                },
                "category": {
                    "type": "string",
                    "description": "可选过滤类别: preference, decision, fact, project, insight, task, relationship",
                    "enum": ["preference", "decision", "fact", "project", "insight", "task", "relationship"],
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_memory",
        "description": "保存一条新记忆。如检测到语义冲突（相似度>0.9），返回已有条目供确认。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "记忆内容",
                },
                "category": {
                    "type": "string",
                    "description": "记忆类别: preference, decision, fact, project, insight, task, relationship",
                    "enum": ["preference", "decision", "fact", "project", "insight", "task", "relationship"],
                    "default": "fact",
                },
                "source": {
                    "type": "string",
                    "description": "来源（如 hermes, claude, chatgpt, manual, agent）",
                    "default": "agent",
                },
                "confidence": {
                    "type": "number",
                    "description": "置信度 0.0 - 1.0",
                    "default": 1.0,
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "标签列表",
                },
            },
            "required": ["content"],
        },
    },
    {
        "name": "get_persona",
        "description": "获取指定 Persona（人格）的完整配置，包括 system_prompt、traits 等。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona_id": {
                    "type": "string",
                    "description": "Persona ID",
                },
            },
            "required": ["persona_id"],
        },
    },
    {
        "name": "list_personas",
        "description": "列出用户的所有可用 Persona（人格配置），返回名称、类型、描述等摘要信息。",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "auto_provision",
        "description": "一键获取用户完整上下文。返回用户画像、行为规则、可用Persona、活跃项目、核心知识。AI Agent 连接后应优先调用此工具。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona_id": {
                    "type": "string",
                    "description": "可选的 Persona ID，用于指定配置视角",
                },
            },
        },
    },
    {
        "name": "consult_persona",
        "description": "用指定Persona的系统提示和traits，在用户记忆上下文中回答问题",
        "inputSchema": {
            "type": "object",
            "properties": {
                "persona_id": {
                    "type": "string",
                    "description": "Persona ID",
                },
                "question": {
                    "type": "string",
                    "description": "要咨询的问题",
                },
            },
            "required": ["persona_id", "question"],
        },
    },
    {
        "name": "match_persona",
        "description": "根据问题自动推荐最匹配的 Persona。基于问题与 Persona 描述的语义匹配度排序。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "要匹配的问题或任务描述",
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "compare_personas",
        "description": "让多个 Persona 回答同一个问题，返回各 Persona 的视角对比。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "要对比的问题",
                },
                "persona_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要对比的 Persona 名称列表（至少2个）；传 \"*\" 或省略则对比所有活跃 Persona",
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "archive_memory",
        "description": "归档记忆（软删除）。归档后的记忆不会出现在搜索和列表中，但数据保留。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "要归档的记忆 ID",
                },
            },
            "required": ["memory_id"],
        },
    },
    {
        "name": "save_memories",
        "description": "批量保存多条记忆。每项需提供 content、category，可选 source、confidence、tags。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "category": {"type": "string", "enum": ["preference", "decision", "fact", "project", "insight", "task", "relationship"]},
                            "source": {"type": "string"},
                            "confidence": {"type": "number"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["content", "category"],
                    },
                }
            },
            "required": ["memories"],
        },
    },
    {
        "name": "search_by_tag",
        "description": "按标签搜索记忆。返回匹配标签的所有记忆条目。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "items": {"type": "string"}, "description": "要搜索的标签列表（OR 逻辑）"},
                "category": {"type": "string", "description": "可选过滤类别"},
                "limit": {"type": "integer", "description": "返回结果数量", "default": 20},
            },
            "required": ["tags"],
        },
    },
    {
        "name": "ping",
        "description": "心跳检测 — 检查服务是否正常。",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ── 工具 → 权限范围映射 ─────────────────────────────────
TOOL_SCOPE_MAP = {
    "search_memory": ["memory:read"],
    "save_memory": ["memory:write"],
    "save_memories": ["memory:write"],
    "archive_memory": ["memory:write"],
    "auto_provision": ["provision:read"],
    "get_persona": ["persona:read"],
    "list_personas": ["persona:read"],
    "match_persona": ["persona:read"],
    "consult_persona": ["persona:read", "persona:use"],
    "compare_personas": ["persona:read", "persona:use"],
    "search_by_tag": ["memory:read"],
}


# ═══════════════════════════════════════════════════════════
# 工具实现（直接复用现有业务逻辑）
# ═══════════════════════════════════════════════════════════

def _keyword_score(query: str, content: str) -> float:
    """Simple keyword overlap score — 0.0 to 1.0.
    
    Works as a lightweight fallback when semantic embeddings
    (sentence-transformers) are unavailable.
    """
    import re
    q_lower = query.lower()
    c_lower = content.lower()

    # Extract meaningful tokens from query (single char, CJK single chars)
    # Split on word boundaries for mixed CJK/English text
    q_tokens = set()
    # English words
    for w in re.findall(r'[a-zA-Z0-9]{2,}', q_lower):
        q_tokens.add(w)
    # CJK bigrams (sliding window of 2 chars)
    cjk = re.sub(r'[^\u4e00-\u9fff]', '', q_lower)
    for i in range(len(cjk)):
        q_tokens.add(cjk[i])  # single CJK char
        if i < len(cjk) - 1:
            q_tokens.add(cjk[i:i+2])  # bigram

    if not q_tokens:
        return 0.0

    # Count matches
    hits = sum(1 for t in q_tokens if t in c_lower)
    # Also check if the full query appears as a substring
    if len(query) >= 2 and query.lower() in content.lower():
        hits += len(q_tokens) * 0.5

    return min(1.0, hits / len(q_tokens))


def _tool_search_memory(user_id: str, params: dict) -> dict:
    """搜索记忆"""
    query = params.get("query", "")
    top_k = min(int(params.get("top_k", 5)), 50)
    category = params.get("category")

    if not query:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: query")

    vec = embed(query)
    results = get_store().search(user_id, vec, top_k=top_k * 3, category=category)

    # SQLite mode: re-rank by keyword match + cosine
    # (trigram hash embeddings are sparse; plain cosine gives near-zero)
    if results:
        scored = []
        for r in results:
            sim = float(r.get("similarity", 0))
            kw = _keyword_score(query, r.get("content", ""))
            combined = sim * 0.4 + kw * 0.6
            scored.append((combined, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [r for _, r in scored[:top_k]]

    return {
        "query": query,
        "results": [
            {
                "id": r["id"],
                "content": r["content"],
                "category": r["category"],
                "source": r["source"],
                "relevance": round(_keyword_score(query, r.get("content", "")), 3),
                "created_at": r.get("created_at", ""),
            }
            for r in results
        ],
    }


def _tool_save_memory(user_id: str, params: dict) -> dict:
    """保存记忆"""
    # ── Enforce 100 memory limit per user ─────────────────
    existing = get_store().list(user_id, limit=0)
    if len(existing) >= 200:
        return {
            "saved": False,
            "error": "Memory limit reached (200). Register to unlock unlimited storage.",
        }
    if len(existing) >= 160:
        # Warn at 80% — but don't block
        pass  # Warning will come from Skill (memory_count in auto_provision)

    content = params.get("content", "")
    category = params.get("category", "fact")
    source = params.get("source", "agent")
    confidence = float(params.get("confidence", 1.0))
    tags = params.get("tags", [])
    force = params.get("force", False)

    if not content:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: content")

    vec = embed(content)

    try:
        if not force:
            conflicts = get_store().find_conflicts(user_id, vec)
            strong = [c for c in conflicts if c["similarity"] > 0.9]
            if strong:
                return {
                    "saved": False,
                    "conflict": True,
                    "existing": [
                        {
                            "id": c["id"],
                            "content": c["content"][:100],
                            "similarity": c["similarity"],
                        }
                        for c in strong
                    ],
                    "message": "发现相似记忆，使用 force=true 强制保存覆盖。",
                }

        doc = get_store().insert(
            user_id, content, vec,
            category=category, source=source,
            confidence=confidence, tags=tags,
        )
        return {"saved": True, "id": doc["id"]}
    except JSONRPCError:
        raise
    except Exception as e:
        raise JSONRPCError(INTERNAL_ERROR, f"Save memory failed: {str(e)}")


def _tool_save_memories(user_id: str, params: dict) -> dict:
    """批量保存多条记忆"""
    memories = params.get("memories", [])
    if not memories or not isinstance(memories, list):
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: memories (non-empty array)")

    # ── Enforce 200 memory limit per user ─────────────────
    existing = get_store().list(user_id, limit=0)
    if len(existing) >= 200:
        return {
            "total": len(memories),
            "saved": 0,
            "failed": 0,
            "error": "Memory limit reached (200). Register to unlock unlimited storage.",
        }

    results = []
    for i, mem in enumerate(memories):
        content = mem.get("content", "")
        category = mem.get("category", "fact")
        source = mem.get("source", "agent")
        confidence = float(mem.get("confidence", 1.0))
        tags = mem.get("tags", [])

        if not content:
            results.append({
                "index": i,
                "saved": False,
                "error": "Missing required field: content",
            })
            continue
        if category not in ("preference", "decision", "fact", "project", "insight", "task", "relationship"):
            results.append({
                "index": i,
                "saved": False,
                "error": f"Invalid category: {category}",
            })
            continue

        try:
            vec = embed(content)

            # Conflict detection (same as single save)
            conflicts = get_store().find_conflicts(user_id, vec)
            strong = [c for c in conflicts if c["similarity"] > 0.9]
            if strong:
                results.append({
                    "index": i,
                    "saved": False,
                    "conflict": True,
                    "existing": [
                        {
                            "id": c["id"],
                            "content": c["content"][:100],
                            "similarity": c["similarity"],
                        }
                        for c in strong
                    ],
                    "message": "发现相似记忆，跳过保存。可单独使用 save_memory force=true 强制覆盖。",
                })
                continue

            doc = get_store().insert(
                user_id, content, vec,
                category=category, source=source,
                confidence=confidence, tags=tags,
            )
            results.append({
                "index": i,
                "saved": True,
                "id": doc["id"],
            })
        except Exception as e:
            results.append({
                "index": i,
                "saved": False,
                "error": str(e),
            })

    saved_count = sum(1 for r in results if r.get("saved"))
    return {
        "total": len(memories),
        "saved": saved_count,
        "failed": len(memories) - saved_count,
        "results": results,
    }


def _tool_search_by_tag(user_id: str, params: dict) -> dict:
    """按标签搜索记忆"""
    tags = params.get("tags", [])
    category = params.get("category")
    limit = min(int(params.get("limit", 20)), 100)

    if not tags or not isinstance(tags, list):
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: tags (non-empty array)")

    # Try Supabase first, fallback to in-memory VectorStore
    store = get_store()
    results = []

    # Check if we have Supabase available via the store
    from app_state import supabase
    if supabase is not None and not store._offline:
        try:
            # Use jsonb ?| operator (tags contains any of the given tags)
            query = supabase.table("memories") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("is_archived", False) \
                .contains("tags", tags) \
                .order("created_at", desc=True) \
                .limit(limit)

            if category:
                query = query.eq("category", category)

            resp = query.execute()
            for r in (resp.data or []):
                results.append({
                    "id": str(r.get("id", "")),
                    "content": r.get("content", ""),
                    "category": r.get("category", ""),
                    "source": r.get("source", ""),
                    "tags": r.get("tags") or [],
                    "confidence": float(r.get("confidence", 1.0)),
                    "created_at": r.get("created_at", ""),
                })
            return {"tags": tags, "results": results, "total": len(results)}
        except Exception:
            pass  # Fall through to in-memory fallback

    # In-memory fallback: filter by tags
    if hasattr(store, '_fallback') and store._fallback:
        tag_set = set(tags)
        for doc in store._fallback._store.values():
            if doc["user_id"] != user_id or doc["is_archived"]:
                continue
            if category and doc["category"] != category:
                continue
            doc_tags = set(doc.get("tags") or [])
            if tag_set & doc_tags:  # Intersection — OR logic
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "category": doc["category"],
                    "source": doc["source"],
                    "tags": doc.get("tags") or [],
                    "confidence": doc.get("confidence", 1.0),
                    "created_at": doc.get("created_at", ""),
                })
        results = results[:limit]
        return {"tags": tags, "results": results, "total": len(results)}

    return {"tags": tags, "results": [], "total": 0}


def _tool_get_persona(user_id: str, params: dict) -> dict:
    """获取 Persona 详情"""
    persona_id = params.get("persona_id", "")
    if not persona_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: persona_id")

    # Try supabase first, fallback to in-memory persona store
    if supabase is not None:
        try:
            result = (
                supabase.table("personas")
                .select("*")
                .eq("id", persona_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            if result.data:
                return {
                    "id": result.data.get("id"),
                    "name": result.data.get("name"),
                    "type": result.data.get("type"),
                    "description": result.data.get("description"),
                    "system_prompt": result.data.get("system_prompt"),
                    "traits": result.data.get("traits", {}),
                    "model_preference": result.data.get("model_preference"),
                    "is_active": result.data.get("is_active", True),
                    "created_at": result.data.get("created_at"),
                }
        except Exception:
            pass  # fall through to in-memory

    # In-memory fallback
    from services.persona_store import get_persona_store
    p = get_persona_store().get(persona_id, user_id)
    if not p:
        raise JSONRPCError(TOOL_ERROR, f"Persona '{persona_id}' not found")
    return {
        "id": p.get("id"), "name": p.get("name"),
        "type": p.get("type"), "description": p.get("description"),
        "system_prompt": p.get("system_prompt"), "traits": p.get("traits", {}),
        "model_preference": p.get("model_preference"),
        "is_active": p.get("is_active", True), "created_at": p.get("created_at"),
    }


def _tool_list_personas(user_id: str, params: dict) -> dict:
    """列出所有 Persona"""
    # Try supabase first, fallback to in-memory persona store
    if supabase is not None:
        try:
            result = (
                supabase.table("personas")
                .select("id, name, type, description, traits, created_at")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            return {"personas": result.data}
        except Exception:
            pass

    from services.persona_store import get_persona_store
    personas = get_persona_store().list(user_id)
    return {"personas": personas}


def _tool_auto_provision(user_id: str, params: dict, ip_address: str = None) -> dict:
    """一键获取用户完整上下文"""
    from services.provision_service import auto_provision

    if supabase is not None:
        try:
            return auto_provision(supabase, user_id, ip_address=ip_address)
        except Exception:
            pass

    # In-memory fallback: build from persona store + vector store
    from services.persona_store import get_persona_store
    from app_state import get_persona_version
    store = get_store()
    pstore = get_persona_store()
    personas = pstore.list(user_id)
    mem_stats = store.stats(user_id)
    recent = store.list(user_id, limit=10)
    prefs = [m for m in recent if m.get("category") == "preference"]

    return {
        "profile": {"name": None, "timezone": "Asia/Shanghai", "language": "zh"},
        "is_anonymous": True,
        "memory_count": mem_stats.get("total", 0),
        "personas_version": get_persona_version(),  # 全局版本号 — Agent 对比用
        "rules": [],
        "preferences": [p["content"] for p in prefs],
        "active_projects": [],
        "recent_decisions": [],
        "available_personas": [
            {"id": p["id"], "name": p["name"], "description": p.get("description"), "type": p["type"]}
            for p in personas
        ],
        "core_knowledge": [],
    }


def _tool_consult_persona(user_id: str, params: dict, ip_address: str = None) -> dict:
    """用指定 Persona 的身份回答问题"""
    persona_id = params.get("persona_id", "")
    question = params.get("question", "")

    if not persona_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: persona_id")
    if not question:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: question")

    if supabase is None:
        raise JSONRPCError(INTERNAL_ERROR, "Database not available")

    # 1. Load Persona
    result = (
        supabase.table("personas")
        .select("*")
        .eq("id", persona_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise JSONRPCError(TOOL_ERROR, f"Persona '{persona_id}' not found")

    persona = result.data
    persona_name = persona.get("name", persona_id)
    system_prompt = persona.get("system_prompt", "")
    traits = persona.get("traits", {})

    # 2. Search relevant memories as context
    memories = []
    memory_context = ""
    try:
        from services.embedding import embed
        vec = embed(question)
        memories = get_store().search(user_id, vec, top_k=10, category=None)
        memory_context = "\n".join(
            f"[{m['category']}] {m['content']}"
            for m in memories
        ) if memories else ""
    except Exception:
        pass

    # 3. Build system prompt with context
    if traits:
        traits_str = "; ".join(f"{k}: {v}" for k, v in traits.items())
        full_system = f"{system_prompt}\n\n角色特质: {traits_str}"
    else:
        full_system = system_prompt

    if memory_context:
        full_system += f"\n\n用户上下文:\n{memory_context}"

    # 4. Check LLM availability — lazy import from main to avoid circular import
    try:
        from main import deepseek_client as _ds_client
    except ImportError:
        _ds_client = None

    if _ds_client is None:
        # Fallback: return persona context + memories without LLM
        answer = (
            f"[本地回退模式 — LLM 未配置]\n\n"
            f"Persona: {persona_name}\n"
            f"描述: {persona.get('description', '')}\n\n"
            f"相关记忆:\n"
        )
        if memory_context:
            answer += memory_context
        else:
            answer += "（无相关记忆）"
        answer += f"\n\n原始问题: {question}"
        return {
            "answer": answer,
            "persona_name": persona_name,
        }

    # 5. Call DeepSeek LLM with local fallback (timeout: 30s, retries: 2)
    from openai import OpenAI, APITimeoutError, APIConnectionError
    import time as _time

    max_retries = 2
    answer = ""  # initialized before loop for type safety
    for attempt in range(max_retries + 1):
        try:
            response = _ds_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": question},
                ],
                max_tokens=1000,
                temperature=0.7,
                timeout=30.0,
            )
            answer = response.choices[0].message.content.strip()
            break
        except (APITimeoutError, APIConnectionError) as e:
            if attempt < max_retries:
                _time.sleep(1.0 * (attempt + 1))  # exponential backoff: 1s, 2s
                continue
            # All retries exhausted — fallback
            answer = (
                f"[本地回退模式 — LLM 不可用 ({type(e).__name__})]\\n\\n"
                f"Persona: {persona_name}\\n"
                f"描述: {persona.get('description', '')}\\n\\n"
                f"相关记忆:\\n"
            )
            if memory_context:
                answer += memory_context
            else:
                answer += "（无相关记忆）"
            answer += f"\\n\\n原始问题: {question}"
        except Exception as e:
            # Other exceptions — immediate fallback
            answer = (
                f"[本地回退模式 — LLM 不可用]\\n\\n"
                f"Persona: {persona_name}\\n"
                f"描述: {persona.get('description', '')}\\n\\n"
                f"相关记忆:\\n"
            )
            if memory_context:
                answer += memory_context
            else:
                answer += "（无相关记忆）"
            answer += f"\\n\\n原始问题: {question}"
            break

    # 6. Audit log
    try:
        supabase.table("audit_logs").insert({
            "user_id": user_id,
            "action": "consult_persona",
            "ip_address": ip_address,
            "details": {
                "persona_id": persona_id,
                "persona_name": persona_name,
                "question_length": len(question),
                "memories_used": len(memories) if memory_context else 0,
            },
        }).execute()
    except Exception:
        pass  # 审计失败不应阻塞

    return {
        "answer": answer,
        "persona_name": persona_name,
    }


def _tool_match_persona(user_id: str, params: dict) -> dict:
    """根据问题自动推荐最匹配的 Persona（基于简单词重叠评分）"""
    question = params.get("question", "")
    if not question:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: question")

    # Try supabase first, fallback to in-memory persona store
    personas_data = []
    if supabase is not None:
        try:
            result = (
                supabase.table("personas")
                .select("id, name, description")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )
            personas_data = result.data or []
        except Exception:
            pass

    if not personas_data:
        from services.persona_store import get_persona_store
        personas_data = get_persona_store().list(user_id)

    if not personas_data:
        return {"matches": []}

    # Compute simple keyword overlap score (jaccard-like word overlap)
    def _tokenize(text: str) -> set[str]:
        import re
        words = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text.lower())
        return set(words)

    question_tokens = _tokenize(question)

    scored = []
    for p in personas_data:
        text = f"{p.get('name', '')} {p.get('description', '')}"
        persona_tokens = _tokenize(text)
        if not persona_tokens:
            continue
        intersection = len(question_tokens & persona_tokens)
        union = len(question_tokens | persona_tokens)
        score = intersection / union if union > 0 else 0.0
        scored.append({
            "id": p["id"],
            "name": p["name"],
            "description": p.get("description", ""),
            "score": round(score, 4),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": scored[:3], "question": question}


def _tool_compare_personas(user_id: str, params: dict, ip_address: str = None) -> dict:
    """让多个 Persona 回答同一个问题，返回各 Persona 的视角对比"""
    question = params.get("question", "")
    persona_names = params.get("persona_names", ["*"])

    if not question:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: question")

    # 1. Determine which personas to compare (supabase → in-memory fallback)
    personas = []
    if supabase is not None:
        try:
            if persona_names == ["*"] or not persona_names:
                result = (
                    supabase.table("personas")
                    .select("id, name")
                    .eq("user_id", user_id)
                    .eq("is_active", True)
                    .execute()
                )
            else:
                result = (
                    supabase.table("personas")
                    .select("id, name")
                    .eq("user_id", user_id)
                    .in_("name", persona_names)
                    .execute()
                )
            personas = result.data or []
        except Exception:
            pass

    if not personas:
        from services.persona_store import get_persona_store
        all_p = get_persona_store().list(user_id)
        if persona_names == ["*"] or not persona_names:
            personas = [{"id": p["id"], "name": p["name"]} for p in all_p]
        else:
            name_set = set(persona_names)
            personas = [{"id": p["id"], "name": p["name"]} for p in all_p if p["name"] in name_set]

    if not personas:
        raise JSONRPCError(TOOL_ERROR, "No matching personas found")
    if len(personas) < 2 and persona_names != ["*"]:
        raise JSONRPCError(INVALID_PARAMS, "Need at least 2 personas to compare")

    # 2. Load full persona data (supabase → in-memory fallback)
    def _load_persona(pid: str) -> dict | None:
        if supabase is not None:
            try:
                r = supabase.table("personas").select("*").eq("id", pid).eq("user_id", user_id).single().execute()
                if r.data:
                    return r.data
            except Exception:
                pass
        from services.persona_store import get_persona_store
        return get_persona_store().get(pid, user_id)

    # 3. For each persona, build prompt and call LLM (with timeout/retry)
    from openai import APITimeoutError, APIConnectionError
    import time as _time

    comparisons = {}
    for p in personas:
        persona_data = _load_persona(p["id"])
        if not persona_data:
            comparisons[p["name"]] = {"error": "Persona data not found"}
            continue

        system_prompt = persona_data.get("system_prompt", "")
        traits = persona_data.get("traits", {})

        traits_str = "; ".join(f"{k}: {v}" for k, v in traits.items()) if traits else ""
        persona_prompt = system_prompt
        if traits_str:
            persona_prompt += f"\n\n角色特质: {traits_str}"

        # Search relevant memories
        try:
            from services.embedding import embed
            vec = embed(question)
            memories = get_store().search(user_id, vec, top_k=5, category=None)
            memory_context = "\n".join(
                f"[{m['category']}] {m['content']}" for m in memories
            ) if memories else ""
            if memory_context:
                persona_prompt += f"\n\n用户上下文:\n{memory_context}"
        except Exception:
            pass

        # Call LLM with timeout/retry
        try:
            from main import deepseek_client as _ds_client
            if _ds_client is None:
                comparisons[p["name"]] = f"[LLM 未配置] {p['name']}: 需要配置 DEEPSEEK_API_KEY"
                continue

            max_retries = 2
            answer = None
            for attempt in range(max_retries + 1):
                try:
                    response = _ds_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": persona_prompt},
                            {"role": "user", "content": question},
                        ],
                        max_tokens=1000,
                        temperature=0.7,
                        timeout=30.0,
                    )
                    answer = response.choices[0].message.content.strip()
                    break
                except (APITimeoutError, APIConnectionError):
                    if attempt < max_retries:
                        _time.sleep(1.0 * (attempt + 1))
                        continue
                    answer = f"[LLM 超时] {p['name']}: 请求超时，请稍后重试"
                except Exception as e:
                    answer = f"[LLM 错误] {p['name']}: {str(e)[:100]}"
                    break

            comparisons[p["name"]] = answer or f"[无响应] {p['name']}"
        except Exception as e:
            comparisons[p["name"]] = f"[错误] {p['name']}: {str(e)[:100]}"

    # 4. Audit log (supabase only)
    if supabase is not None:
        try:
            supabase.table("audit_logs").insert({
                "user_id": user_id,
                "action": "compare_personas",
                "ip_address": ip_address,
                "details": {
                    "persona_count": len(personas),
                    "persona_names": [p["name"] for p in personas],
                    "question_length": len(question),
                },
            }).execute()
        except Exception:
            pass

    return {"question": question, "comparisons": comparisons}


def _tool_archive_memory(user_id: str, params: dict) -> dict:
    """归档记忆（软删除）"""
    memory_id = params.get("memory_id", "")
    if not memory_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: memory_id")

    if not get_store().update(memory_id, user_id, is_archived=True):
        raise JSONRPCError(TOOL_ERROR, f"Memory '{memory_id}' not found")
    return {"status": "archived", "memory_id": memory_id}


def _tool_ping(user_id: str, params: dict) -> dict:
    """心跳检测"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── 工具路由表 ────────────────────────────────────────────
TOOL_DISPATCH = {
    "search_memory": _tool_search_memory,
    "save_memory": _tool_save_memory,
    "save_memories": _tool_save_memories,
    "search_by_tag": _tool_search_by_tag,
    "get_persona": _tool_get_persona,
    "list_personas": _tool_list_personas,
    "auto_provision": _tool_auto_provision,
    "consult_persona": _tool_consult_persona,
    "match_persona": _tool_match_persona,
    "compare_personas": _tool_compare_personas,
    "archive_memory": _tool_archive_memory,
    "ping": _tool_ping,
}


# ── Tools that need IP address ────────────────────────────
_IP_AWARE_TOOLS = {"auto_provision", "consult_persona", "compare_personas"}


# ═══════════════════════════════════════════════════════════
# JSON-RPC 方法分发
# ═══════════════════════════════════════════════════════════

def _handle_jsonrpc(
    body: dict,
    user_id: str | None,
    ip_address: str = None,
) -> dict:
    """处理单条 JSON-RPC 2.0 请求"""
    # ── validate jsonrpc field ─────────────────────────
    if body.get("jsonrpc") != "2.0":
        return jsonrpc_error(
            INVALID_REQUEST,
            "Invalid JSON-RPC version — must be '2.0'",
            body.get("id"),
        )

    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params")

    if not isinstance(params, dict):
        params = {} if params is None else params
    if not isinstance(params, dict):
        return jsonrpc_error(
            INVALID_PARAMS,
            "params must be a JSON object (dict)",
            req_id,
        )

    # ── 不需要认证的特殊方法 ────────────────────────────
    if method == "ping":
        return jsonrpc_success(_tool_ping(None, params), req_id)

    # ── 需要认证的方法（tools/list 和 initialize 不再免认证）──
    if method == "tools/list":
        if user_id is None:
            return jsonrpc_error(AUTH_ERROR, "Authentication required — provide X-API-Key header", req_id)
        return jsonrpc_success({"tools": MCP_TOOLS}, req_id)

    if method == "initialize":
        if user_id is None:
            return jsonrpc_error(AUTH_ERROR, "Authentication required — provide X-API-Key header", req_id)
        return jsonrpc_success({
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False,
                },
                "sampling": {},
                "experimental": {},
            },
            "serverInfo": {
                "name": "moltable",
                "version": "0.1.0",
                "auth": {
                    "type": "did_vc",
                    "challenge": "placeholder",
                    "supportedCredentials": ["AgentIdentityCredential", "PersonaDelegationCredential"]
                },
            },
        }, req_id)

    # ── 需要认证的方法 ─────────────────────────────────
    if method == "tools/call":
        if user_id is None:
            return jsonrpc_error(AUTH_ERROR, "Authentication required", req_id)

        tool_name = (params or {}).get("name", "")
        tool_params = (params or {}).get("arguments", {})

        if not isinstance(tool_params, dict):
            tool_params = {}

        handler = TOOL_DISPATCH.get(tool_name)
        if handler is None:
            return jsonrpc_error(
                METHOD_NOT_FOUND,
                f"Unknown tool: '{tool_name}'",
                req_id,
            )

        # ── 权限检查（DID+VC Agent 认证上下文）──
        if hasattr(user_id, 'scopes'):
            required = TOOL_SCOPE_MAP.get(tool_name, [])
            if required:
                user_scopes = set(user_id.scopes or [])
                if not user_scopes.intersection(required) and "*" not in user_scopes:
                    return jsonrpc_error(
                        AUTH_ERROR,
                        f"权限不足: 工具 '{tool_name}' 需要 {required}，当前有 {list(user_scopes)}",
                        req_id,
                    )

        try:
            if tool_name in _IP_AWARE_TOOLS:
                result = handler(user_id, tool_params, ip_address=ip_address)
            else:
                result = handler(user_id, tool_params)
            # MCP tools/call 响应格式：将结果包裹在 content 中
            return jsonrpc_success({
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2),
                    }
                ],
            }, req_id)
        except JSONRPCError as e:
            return jsonrpc_error(e.code, e.message, req_id, e.data)
        except Exception as e:
            traceback.print_exc()
            return jsonrpc_error(
                INTERNAL_ERROR,
                "Tool execution failed",
                req_id,
            )

    # ── 未知方法 ───────────────────────────────────────
    return jsonrpc_error(
        METHOD_NOT_FOUND,
        f"Method not found: '{method}'",
        req_id,
    )


# ═══════════════════════════════════════════════════════════
# HTTP 端点
# ═══════════════════════════════════════════════════════════

@router.post("/mcp")
@limiter.limit("300/minute")
async def mcp_endpoint(
    request: Request,
    x_api_key: str = Header(None),
):
    """MCP JSON-RPC 2.0 主入口

    接收单个或批量 JSON-RPC 请求。
    支持: initialize, ping, tools/list, tools/call

    认证方式: X-API-Key header（可选的，ping 和 initialize 不需要）
    """
    # ── 解析请求体 ──────────────────────────────────
    try:
        body = await request.json()
    except Exception:
        return JSONRPCResponse(
            jsonrpc_error(PARSE_ERROR, "Parse error — invalid JSON", None),
            status_code=400,
        )

    # ── 可选认证 ────────────────────────────────────
    user_id = None
    ip_address = request.client.host if request and request.client else None
    if x_api_key:
        try:
            user_id = await _resolve_api_key(x_api_key)
        except Exception as e:
            return JSONRPCResponse(
                jsonrpc_error(AUTH_ERROR, f"Authentication failed: {str(e)}", None)
            )

    # ── 批量 vs 单条 ────────────────────────────────
    is_batch = isinstance(body, list)

    if is_batch:
        responses = []
        for req in body:
            if not isinstance(req, dict):
                responses.append(
                    jsonrpc_error(INVALID_REQUEST, "Invalid Request", None)
                )
                continue
            responses.append(_handle_jsonrpc(req, user_id, ip_address=ip_address))
        return JSONRPCResponse(responses)
    else:
        if not isinstance(body, dict):
            return JSONRPCResponse(
                jsonrpc_error(INVALID_REQUEST, "Request must be a JSON object", None),
                status_code=400,
            )
        result = _handle_jsonrpc(body, user_id, ip_address=ip_address)
        status = 200
        if "error" in result:
            code = result["error"].get("code", 0)
            if code == PARSE_ERROR:
                status = 400
            elif code == METHOD_NOT_FOUND:
                status = 404
            elif code == AUTH_ERROR:
                status = 401
            elif code >= -32000 and code <= -32099:
                status = 500
        return JSONRPCResponse(result, status_code=status)


@router.get("/.well-known/mcp")
async def mcp_discovery(request: Request):
    """MCP 发现端点 — 返回服务器元信息"""
    return {
        "schemaVersion": "2024-11-05",
        "server": {
            "name": "moltable",
            "version": "0.1.0",
            "description": "Moltable — AI Identity Layer: Cross-AI identity system with memory, persona, and provisioning",
        },
        "capabilities": {
            "tools": {
                "total": len(MCP_TOOLS),
                "tools": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                    }
                    for t in MCP_TOOLS
                ],
            },
        },
        "endpoints": {
            "jsonrpc": "/mcp",
            "transport": "http",
        },
        "authentication": {
            "type": "api-key",
            "header": "X-API-Key",
        },
    }


# ═══════════════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════════════

async def _resolve_api_key(x_api_key: str) -> str:
    """通过 X-API-Key 解析用户 ID，支持 API key（molt_xxx）和匿名会话 token（mol_xxx）。

    注意: 必须先检查 molt_（API key），再检查 mol_（session token），
    否则 mol_ 会贪婪匹配 molt_ 开头的 API key。
    """
    # 1. API key detection: if key starts with molt_, treat as API key
    if x_api_key.startswith("molt_"):
        from routes.auth import hash_api_key
        key_hash = hash_api_key(x_api_key)
        if supabase is None:
            raise JSONRPCError(INTERNAL_ERROR, "Database not available")
        resp = supabase.table("api_keys").select("user_id, is_active").eq("key_hash", key_hash).execute()
        if not resp.data:
            raise JSONRPCError(AUTH_ERROR, "Invalid API key")
        if not resp.data[0].get("is_active", False):
            raise JSONRPCError(AUTH_ERROR, "API key revoked")
        return resp.data[0]["user_id"]

    # 2. Session token detection: if key starts with mol_ (not molt_), treat as session token
    if x_api_key.startswith("mol_"):
        # Validate session token via Supabase
        if supabase is None:
            raise JSONRPCError(INTERNAL_ERROR, "Database not available")
        try:
            from datetime import datetime, timezone
            resp = supabase.table("sessions").select("session_uuid, token, expires_at, migrated_at").eq("token", x_api_key).execute()
            if not resp.data:
                raise JSONRPCError(AUTH_ERROR, "Invalid session token")
            session = resp.data[0]
            if session.get("migrated_at"):
                raise JSONRPCError(AUTH_ERROR, "Session already migrated — use API key instead")
            expires_at = session.get("expires_at")
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expires_at < datetime.now(timezone.utc):
                    raise JSONRPCError(AUTH_ERROR, "Session expired — create a new one")
            # Return session_uuid as the user_id (valid UUID for Supabase columns)
            return str(session.get("session_uuid", x_api_key))
        except JSONRPCError:
            raise
        except Exception:
            raise JSONRPCError(AUTH_ERROR, "Invalid session token")

    from routes.auth import hash_api_key
    key_hash = hash_api_key(x_api_key)
    if supabase is None:
        raise JSONRPCError(INTERNAL_ERROR, "Database not available")
    resp = supabase.table("api_keys").select("user_id, is_active").eq("key_hash", key_hash).execute()
    if not resp.data:
        raise JSONRPCError(AUTH_ERROR, "Invalid API key")
    if not resp.data[0].get("is_active", False):
        raise JSONRPCError(AUTH_ERROR, "API key revoked")
    return resp.data[0]["user_id"]


class JSONRPCResponse(JSONResponse):
    """JSON-RPC 2.0 响应"""
    def __init__(self, content: Any, status_code: int = 200, **kwargs):
        super().__init__(content=content, status_code=status_code, **kwargs)
