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
                    "description": "来源标识（推荐填写: hermes/claude/chatgpt/manual/agent）。未传时服务端从 X-Agent-Platform 请求头推断，仍无则记为 unknown",
                    "recommended": True,
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
    },        {
        "name": "update_memory",
        "description": "更新已有记忆的内容、分类、标签或置信度。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "要更新的记忆 ID"},
                "content": {"type": "string", "description": "新的记忆内容"},
                "category": {"type": "string", "enum": ["preference","decision","fact","project","insight","task","relationship"], "description": "新的记忆类别"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "新的标签列表"},
                "confidence": {"type": "number", "description": "新的置信度 0.0-1.0"},
            },
            "required": ["memory_id"],
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
    {
        "name": "list_skills",
        "description": "列出用户的所有可用 Skills",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_skill",
        "description": "获取单个 Skill 的完整内容",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_id": {
                    "type": "string",
                    "description": "Skill ID",
                },
            },
            "required": ["skill_id"],
        },
    },
    {
        "name": "list_projects",
        "description": "列出用户的所有项目，含 knowledge_bases（知识库连接信息）和 tools（工具/MCP 服务器配置）。Agent 据此建立工作环境。",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_project",
        "description": "获取单个项目的完整环境配置，含 knowledge_bases 和 tools。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "项目 ID",
                },
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "create_project",
        "description": "创建新项目，含 knowledge_bases（如 PostgreSQL/Obsidian/Superset 连接）和 tools（如 MCP 服务器/Hermes Skill）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "项目名称",
                },
                "description": {
                    "type": "string",
                    "description": "项目描述",
                },
                "persona_id": {
                    "type": "string",
                    "description": "关联的 Persona ID",
                },
                "knowledge_bases": {
                    "type": "array",
                    "description": "知识库列表，每项含 type/label/host/port/database/path/url 等",
                },
                "tools": {
                    "type": "array",
                    "description": "工具列表，每项含 type/name/url 等",
                },
                "is_active": {
                    "type": "boolean",
                    "description": "是否为活跃项目",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "update_project",
        "description": "更新项目环境配置。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "项目 ID",
                },
                "name": {"type": "string", "description": "新名称"},
                "description": {"type": "string", "description": "新描述"},
                "persona_id": {"type": "string", "description": "关联 Persona ID"},
                "knowledge_bases": {"type": "array", "description": "新知识库配置"},
                "tools": {"type": "array", "description": "新工具配置"},
                "is_active": {"type": "boolean", "description": "是否活跃"},
            },
            "required": ["project_id"],
        },
    },
]


# ── 工具 → 权限范围映射 ─────────────────────────────────
TOOL_SCOPE_MAP = {
    "search_memory": ["memory:read"],
    "save_memory": ["memory:write"],
    "archive_memory": ["memory:write"],
    "update_memory": ["memory:write"],
    "auto_provision": ["provision:read"],
    "get_persona": ["persona:read"],
    "list_personas": ["persona:read"],
    "list_skills": ["skill:read"],
    "get_skill": ["skill:read"],
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
    """搜索记忆 — 向量搜索 + 关键词回退"""
    query = params.get("query", "")
    top_k = min(int(params.get("top_k", 5)), 50)
    category = params.get("category")

    if not query:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: query")

    vec = embed(query)
    results = get_store().search(user_id, vec, top_k=top_k * 3, category=category)

    # pgvector returns empty for near-zero trigram-hash vectors on Supabase.
    # Fallback: fetch all active memories and score by keyword match.
    if not results:
        all_mems = get_store().list(user_id, category=category, limit=200)
        if all_mems:
            scored = []
            for r in all_mems:
                kw = _keyword_score(query, r.get("content", ""))
                if kw > 0:
                    scored.append((kw, r))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [r for _, r in scored[:top_k]]
    else:
        # Re-rank by combined score (cosine + keyword)
        scored = []
        for r in results:
            sim = float(r.get("similarity", 0))
            kw = _keyword_score(query, r.get("content", ""))
            combined = sim * 0.4 + kw * 0.6
            scored.append((combined, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [r for _, r in scored[:top_k]]

    def _resolve_similarity(r: dict) -> float:
        """相似度优先级: pgvector 查询结果 → keyword_score → 默认 0.5 (范围 0.0–1.0)."""
        sim = r.get("similarity")
        if isinstance(sim, (int, float)) and not isinstance(sim, bool):
            return max(0.0, min(1.0, float(sim)))
        kw = _keyword_score(query, r.get("content", ""))
        if kw > 0:
            return kw
        return 0.5

    return {
        "query": query,
        "results": [
            {
                "id": r["id"],
                "content": r["content"],
                "category": r["category"],
                "source": r["source"],
                "similarity": round(_resolve_similarity(r), 3),
                "relevance": round(_keyword_score(query, r.get("content", "")), 3),
                "created_at": r.get("created_at", ""),
            }
            for r in results
        ],
    }


def _tool_save_memory(user_id: str, params: dict, agent_platform: str | None = None) -> dict:
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
    # source 解析: 显式传参 → X-Agent-Platform 请求头 → unknown
    source = (params.get("source") or "").strip() or (agent_platform or "").strip() or "unknown"
    confidence = float(params.get("confidence", 1.0))
    tags = params.get("tags", [])
    force = params.get("force", False)
    persona_id = params.get("persona_id")

    if not content:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: content")

    # Validate category enum
    VALID_CATEGORIES = {"preference", "decision", "fact", "project", "insight", "task", "relationship"}
    if category not in VALID_CATEGORIES:
        raise JSONRPCError(INVALID_PARAMS,
            f"Invalid category: '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}")

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
            persona_id=persona_id,
        )
        return {"saved": True, "id": doc["id"], "source": source}
    except JSONRPCError:
        raise
    except Exception as e:
        raise JSONRPCError(INTERNAL_ERROR, f"Save memory failed: {str(e)}")


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


def _tool_update_memory(user_id: str, params: dict) -> dict:
    """更新已有记忆"""
    memory_id = params.get("memory_id", "")
    if not memory_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: memory_id")
    updates = {}
    for field in ("content", "category", "tags", "confidence", "is_archived"):
        if field in params:
            updates[field] = params[field]
    if not updates:
        raise JSONRPCError(INVALID_PARAMS, "No fields to update")
    if not get_store().update(memory_id, user_id, **updates):
        raise JSONRPCError(TOOL_ERROR, f"Memory '{memory_id}' not found")
    return {"updated": True, "memory_id": memory_id, "fields": list(updates.keys())}


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


# ── Skills tools ────────────────────────────────────────

def _tool_list_skills(user_id: str, params: dict) -> dict:
    """列出用户的所有可用 Skills。

    1. 尝试通过 provision_service 获取 skills 数据
    2. 如果 provision_service 不返回 skills，从 projects 表的 tools 字段提取 type=skill 条目
    3. SQLite 回退：返回空列表
    """
    from services.provision_service import auto_provision

    # 尝试从 provision_service 获取
    if supabase is not None:
        try:
            ctx = auto_provision(supabase, user_id)
            if "skills" in ctx:
                return {"skills": ctx["skills"]}
        except Exception:
            pass

    # 回退：从 projects 表的 tools 字段提取 type=skill 的条目
    skills = []
    if supabase is not None:
        try:
            resp = supabase.table("projects") \
                .select("tools") \
                .eq("user_id", user_id) \
                .execute()
            for r in (resp.data or []):
                tools = r.get("tools") or []
                for t in tools:
                    if isinstance(t, dict) and t.get("type") == "skill":
                        skills.append(t)
        except Exception:
            # SQLite fallback: return empty skills list
            pass

    return {"skills": skills}


def _tool_get_skill(user_id: str, params: dict) -> dict:
    """获取单个 Skill 的完整内容。

    从 projects 表的 tools 字段中按 skill_id 检索。
    """
    skill_id = params.get("skill_id", "")
    if not skill_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: skill_id")

    if supabase is not None:
        try:
            resp = supabase.table("projects") \
                .select("tools") \
                .eq("user_id", user_id) \
                .execute()
            for r in (resp.data or []):
                tools = r.get("tools") or []
                for t in tools:
                    if isinstance(t, dict) and t.get("type") == "skill" \
                            and t.get("name") == skill_id:
                        return {"skill": t}
            raise JSONRPCError(TOOL_ERROR, f"Skill '{skill_id}' not found")
        except JSONRPCError:
            raise
        except Exception:
            pass

    raise JSONRPCError(TOOL_ERROR, f"Skill '{skill_id}' not found")


# ── Project environment tools ──────────────────────────

def _tool_list_projects(user_id: str, params: dict) -> dict:
    """列出用户的所有项目，含 knowledge_bases 和 tools 配置。"""
    resp = supabase.table("projects") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()
    projects = []
    for r in (resp.data or []):
        projects.append({
            "id": r.get("id", ""),
            "name": r.get("name", ""),
            "description": r.get("description", ""),
            "persona_id": r.get("persona_id"),
            "knowledge_bases": r.get("knowledge_bases") or [],
            "tools": r.get("tools") or [],
            "is_active": r.get("is_active", False),
            "created_at": str(r.get("created_at", "")),
        })
    return {"projects": projects}


def _tool_get_project(user_id: str, params: dict) -> dict:
    """获取单个项目的完整环境配置。"""
    project_id = params.get("project_id", "")
    if not project_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: project_id")
    resp = supabase.table("projects") \
        .select("*") \
        .eq("id", project_id) \
        .eq("user_id", user_id) \
        .single() \
        .execute()
    if not resp.data:
        raise JSONRPCError(TOOL_ERROR, f"Project not found: {project_id}")
    r = resp.data
    return {
        "id": r.get("id", ""),
        "name": r.get("name", ""),
        "description": r.get("description", ""),
        "persona_id": r.get("persona_id"),
        "knowledge_bases": r.get("knowledge_bases") or [],
        "tools": r.get("tools") or [],
        "is_active": r.get("is_active", False),
        "created_at": str(r.get("created_at", "")),
        "updated_at": str(r.get("updated_at", "")),
    }


def _tool_create_project(user_id: str, params: dict) -> dict:
    """创建新项目，含 knowledge_bases 和 tools 配置。"""
    name = params.get("name", "")
    if not name:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: name")
    import uuid as _uid
    pid = str(_uid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "id": pid,
        "user_id": user_id,
        "name": name,
        "description": params.get("description", ""),
        "knowledge_bases": params.get("knowledge_bases") or [],
        "tools": params.get("tools") or [],
        "is_active": params.get("is_active", True),
        "created_at": now,
        "updated_at": now,
    }
    if params.get("persona_id"):
        row["persona_id"] = params["persona_id"]
    supabase.table("projects").insert(row).execute()
    return {"id": pid, "name": name, "created": True}


def _tool_update_project(user_id: str, params: dict) -> dict:
    """更新项目环境配置。"""
    project_id = params.get("project_id", "")
    if not project_id:
        raise JSONRPCError(INVALID_PARAMS, "Missing required parameter: project_id")
    existing = supabase.table("projects") \
        .select("id") \
        .eq("id", project_id) \
        .eq("user_id", user_id) \
        .single() \
        .execute()
    if not existing.data:
        raise JSONRPCError(TOOL_ERROR, f"Project not found: {project_id}")
    payload = {"updated_at": datetime.now(timezone.utc).isoformat()}
    for f in ["name", "description", "persona_id", "knowledge_bases", "tools", "is_active"]:
        if f in params:
            payload[f] = params[f]
    supabase.table("projects").update(payload).eq("id", project_id).execute()
    return {"id": project_id, "updated": True}



# ── 工具路由表 ────────────────────────────────────────────
TOOL_DISPATCH = {
    "search_memory": _tool_search_memory,
    "save_memory": _tool_save_memory,
    "update_memory": _tool_update_memory,
    "get_persona": _tool_get_persona,
    "list_personas": _tool_list_personas,
    "auto_provision": _tool_auto_provision,
    "archive_memory": _tool_archive_memory,
    "ping": _tool_ping,
    "list_skills": _tool_list_skills,
    "get_skill": _tool_get_skill,
    "list_projects": _tool_list_projects,
    "get_project": _tool_get_project,
    "create_project": _tool_create_project,
    "update_project": _tool_update_project,
}


# ── Tools that need IP address ────────────────────────────
_IP_AWARE_TOOLS = {"auto_provision"}

# ── Tools that receive X-Agent-Platform header (Agent 来源追踪) ──
_PLATFORM_AWARE_TOOLS = {"save_memory"}


# ═══════════════════════════════════════════════════════════
# JSON-RPC 方法分发
# ═══════════════════════════════════════════════════════════

def _handle_jsonrpc(
    body: dict,
    user_id: str | None,
    ip_address: str = None,
    agent_platform: str | None = None,
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
            elif tool_name in _PLATFORM_AWARE_TOOLS:
                result = handler(user_id, tool_params, agent_platform=agent_platform)
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
    # Agent 来源追踪: X-Agent-Platform 请求头（hermes/claude/chatgpt 等）
    agent_platform = (request.headers.get("x-agent-platform") or "").strip() or None
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
            responses.append(_handle_jsonrpc(req, user_id, ip_address=ip_address, agent_platform=agent_platform))
        return JSONRPCResponse(responses)
    else:
        if not isinstance(body, dict):
            return JSONRPCResponse(
                jsonrpc_error(INVALID_REQUEST, "Request must be a JSON object", None),
                status_code=400,
            )
        result = _handle_jsonrpc(body, user_id, ip_address=ip_address, agent_platform=agent_platform)
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
