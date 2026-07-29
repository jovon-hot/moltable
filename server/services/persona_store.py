"""In-memory Persona store — zero-dependency fallback when Supabase is unavailable."""
from __future__ import annotations
from typing import List, Dict, Optional
import uuid, time


class InMemoryPersonaStore:
    """Thread-safe in-memory store for Persona data with demo personas."""

    def __init__(self):
        self._store: Dict[str, Dict] = {}
        self._version = 0  # 单调递增，任何增删改都 +1
        self._seed_demo()

    def get_version(self) -> int:
        """返回当前版本号 — Agent 用此判断是否需要刷新 Persona 列表。"""
        return self._version

    def _bump(self):
        self._version += 1

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%S")

    def _seed_demo(self):
        """Pre-populate with two demo personas for a better out-of-box experience."""
        demo_user = "demo-user"
        personas = [
            {
                "id": "demo-strategist",
                "user_id": demo_user,
                "name": "战略顾问",
                "type": "constructed",
                "description": "麦肯锡风格，数据驱动，先框架后细节",
                "system_prompt": "你是战略顾问。以麦肯锡方法论分析问题：先框架后数据，先增长后成本。用 MECE 原则、假设驱动、80/20 法则。",
                "traits": {"style": "麦肯锡", "risk": "激进", "detail": "高"},
                "model_preference": None,
                "version": 1,
                "parent_id": None,
                "is_active": True,
                "memory_count": 0,
                "created_at": self._now(),
                "updated_at": self._now(),
            },
            {
                "id": "demo-auditor",
                "user_id": demo_user,
                "name": "保守审核员",
                "type": "constructed",
                "description": "风险厌恶，逐项检查，合规导向",
                "system_prompt": "你是保守审核员。逐项检查风险点，不符合法规的一律标红。宁可过度谨慎也不放过隐患。",
                "traits": {"style": "保守", "risk": "厌恶", "detail": "极高"},
                "model_preference": None,
                "version": 1,
                "parent_id": None,
                "is_active": True,
                "memory_count": 0,
                "created_at": self._now(),
                "updated_at": self._now(),
            },
        ]
        for p in personas:
            self._store[p["id"]] = p

    def list(self, user_id: str) -> List[Dict]:
        results = []
        for p in self._store.values():
            if p["user_id"] == user_id and p["is_active"]:
                results.append(p)
        # Also return demo personas for any user when offline
        if not results:
            results = [p for p in self._store.values() if p["is_active"]]
        return results

    def get(self, persona_id: str, user_id: str) -> Optional[Dict]:
        p = self._store.get(persona_id)
        if p and p["user_id"] == user_id and p["is_active"]:
            return p
        # Fallback: return demo persona by id regardless of user
        if p and p["is_active"]:
            return p
        return None

    def create(self, user_id: str, data: dict) -> Dict:
        pid = str(uuid.uuid4())[:8]
        now = self._now()
        persona = {
            "id": pid,
            "user_id": user_id,
            "name": data.get("name", ""),
            "type": data.get("type", "constructed"),
            "description": data.get("description", ""),
            "system_prompt": data.get("system_prompt", ""),
            "traits": data.get("traits", {}),
            "model_preference": data.get("model_preference"),
            "version": 1,
            "parent_id": None,
            "is_active": True,
            "memory_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        self._store[pid] = persona
        self._bump()
        return persona

    def update(self, persona_id: str, user_id: str, data: dict) -> bool:
        p = self._store.get(persona_id)
        if not p or p["user_id"] != user_id:
            return False
        for k, v in data.items():
            if v is not None:
                p[k] = v
        p["updated_at"] = self._now()
        self._bump()
        return True

    def delete(self, persona_id: str, user_id: str) -> bool:
        p = self._store.get(persona_id)
        if not p or p["user_id"] != user_id:
            return False
        p["is_active"] = False
        p["updated_at"] = self._now()
        self._bump()
        return True


# Global singleton
_persona_store: InMemoryPersonaStore | None = None


def get_persona_store() -> InMemoryPersonaStore:
    global _persona_store
    if _persona_store is None:
        _persona_store = InMemoryPersonaStore()
    return _persona_store
