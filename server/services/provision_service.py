"""Shared auto_provision service — used by both REST and MCP endpoints."""

from app_state import _is_sqlite, get_persona_version


def auto_provision(supabase, user_id: str, ip_address: str = None) -> dict:
    """Fetch full user context for agent provisioning.

    Returns user profile, preferences, rules, personas, active projects,
    recent decisions, and core knowledge.
    """
    # Check if this is a session user (anonymous, not yet registered)
    is_session = False
    try:
        user_check = supabase.table("users").select("id").eq("id", user_id).execute()
        if not user_check.data:
            is_session = True
    except Exception:
        pass

    # 2. User profile
    if is_session:
        user_data = {"name": None, "timezone": "Asia/Shanghai", "language": "zh"}
    else:
        try:
            user_data_resp = supabase.table("users").select("*").eq("id", user_id).single().execute()
            user_data = user_data_resp.data or {}
        except Exception:
            user_data = {"name": None, "timezone": "Asia/Shanghai", "language": "zh"}

    # 2. Preferences & rules (category=preference)
    prefs_resp = None
    try:
        prefs_resp = (
            supabase.table("memories")
            .select("content, tags")
            .eq("user_id", user_id)
            .eq("category", "preference")
            .execute()
        )
    except Exception:
        prefs_resp = None
    preferences = []
    rules = []
    for p in (prefs_resp.data if prefs_resp is not None else None) or []:
        if "rule" in (p.get("tags") or []):
            rules.append(p["content"])
        else:
            preferences.append(p["content"])

    # 3. Active projects (full environment including knowledge_bases + tools)
    projects_data = []
    try:
        projects = (
            supabase.table("projects")
            .select("id, name, description, persona_id, knowledge_bases, tools")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        projects_data = projects.data or []
    except Exception:
        projects_data = []

    projects_env = []
    for p in projects_data:
        projects_env.append({
            "id": p.get("id", ""),
            "name": p.get("name", ""),
            "description": p.get("description", ""),
            "persona_id": p.get("persona_id"),
            "knowledge_bases": p.get("knowledge_bases") or [],
            "tools": p.get("tools") or [],
        })

    # 4. Recent decisions
    decisions_data = []
    try:
        decisions = (
            supabase.table("decisions")
            .select("content")
            .eq("user_id", user_id)
            .order("decided_at", desc=True)
            .limit(10)
            .execute()
        )
        decisions_data = decisions.data or []
    except Exception:
        decisions_data = []

    # 5. Available personas
    personas_data = []
    try:
        personas = (
            supabase.table("personas")
            .select("id, name, description, type")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        personas_data = personas.data or []
    except Exception:
        personas_data = []
    if not personas_data and _is_sqlite:
        # SQLite mode: personas live in the in-memory persona store, not the
        # SQLite personas table (routes/personas.py `_is_offline()` gate).
        from services.persona_store import get_persona_store
        personas_data = [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description"),
                "type": p.get("type", "constructed"),
            }
            for p in get_persona_store().list(user_id)
        ]

    # 6. Core knowledge (facts + projects)
    facts_data = []
    try:
        facts = (
            supabase.table("memories")
            .select("content, category")
            .eq("user_id", user_id)
            .in_("category", ["fact", "project"])
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        facts_data = facts.data or []
    except Exception:
        facts_data = []

    # 7. Audit log (skip for sessions — no real user_id)
    if not is_session:
        try:
            supabase.table("audit_logs").insert({
                "user_id": user_id,
                "action": "auto_provision",
                "ip_address": ip_address,
                "details": {
                    "preferences": len(preferences),
                    "rules": len(rules),
                    "projects": len(projects_data),
                    "personas": len(personas_data),
                },
            }).execute()
        except Exception:
            pass  # Audit failure must not block

    # Count total memories for this user
    try:
        mem_count = supabase.table("memories").select("id", count="exact").eq("user_id", user_id).execute()
        memory_count = mem_count.count if hasattr(mem_count, 'count') else len(mem_count.data or [])
    except Exception:
        memory_count = 0

    return {
        "profile": {
            "name": user_data.get("name"),
            "timezone": user_data.get("timezone", "Asia/Shanghai"),
            "language": user_data.get("language", "zh"),
        },
        "is_anonymous": is_session,
        "memory_count": memory_count,
        "personas_version": get_persona_version(),  # Agent 对比用
        "rules": rules,
        "preferences": preferences,
        "active_projects": projects_env,
        "recent_decisions": [d["content"] for d in decisions_data],
        "available_personas": [
            {"id": p["id"], "name": p["name"], "description": p.get("description"), "type": p["type"]}
            for p in personas_data
        ],
        "core_knowledge": [
            {"content": f["content"], "type": f["category"]}
            for f in facts_data
        ],
    }
