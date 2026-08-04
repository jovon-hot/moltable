"""A/B Testing & Experiments Framework.

Tables (created by init_schema if using SQLite, or via Supabase SQL editor):
  - experiments: (id, name, description, variants JSON, goal, status, created_at, updated_at)
  - experiment_assignments: (experiment_id, user_id, variant, assigned_at)
  - experiment_conversions: (experiment_id, user_id, variant, goal, converted_at)

Admin endpoints under /api/admin/experiments/...
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app_state import supabase, _is_sqlite, limiter
from services.admin_auth import require_staff

logger = logging.getLogger("moltable.experiments")

router = APIRouter(prefix="/api/admin/experiments", tags=["experiments"])


# ── Pydantic models ──────────────────────────────────────

class VariantConfig(BaseModel):
    key: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    weight: float = Field(default=1.0, ge=0.0)
    description: str = Field(default="", max_length=512)

class CreateExperimentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=1024)
    variants: list[VariantConfig] = Field(..., min_length=2, max_length=8)
    goal: str = Field(default="conversion", max_length=64)
    traffic_pct: float = Field(default=100.0, ge=0.0, le=100.0)

class UpdateExperimentRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=1024)
    status: Optional[str] = Field(None, pattern="^(draft|running|paused|completed)$")
    traffic_pct: Optional[float] = Field(None, ge=0.0, le=100.0)


# ── Helpers ──────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _table(name: str):
    """Return a Supabase/SQLite table-like object."""
    if _is_sqlite:
        # SQLite mode — use the adapter's raw methods
        return supabase  # The SQLiteClient has a .table() that returns a proxy
    return supabase.table(name)


# ── Endpoints ────────────────────────────────────────────

@router.post("")
@limiter.limit("30/minute")
def create_experiment(request: Request, body: CreateExperimentRequest,
                       _staff=Depends(require_staff)):
    """Create a new A/B experiment."""
    exp_id = str(uuid.uuid4())[:12]
    now = _now_iso()

    data = {
        "id": exp_id,
        "name": body.name,
        "description": body.description,
        "variants": json.dumps([v.model_dump() for v in body.variants]),
        "goal": body.goal,
        "status": "draft",
        "traffic_pct": body.traffic_pct,
        "created_at": now,
        "updated_at": now,
    }

    try:
        supabase.table("experiments").insert(data).execute()
        logger.info("Experiment created: %s (%s)", exp_id, body.name)
        return {"id": exp_id, **data, "variants": [v.model_dump() for v in body.variants]}
    except Exception as e:
        logger.error("Failed to create experiment: %s", e)
        raise HTTPException(500, f"Failed to create experiment: {e}")


@router.get("")
@limiter.limit("60/minute")
def list_experiments(request: Request, status: Optional[str] = None,
                      _staff=Depends(require_staff)):
    """List all experiments, optionally filtered by status."""
    try:
        q = supabase.table("experiments").select("*").order("created_at", desc=True)
        if status:
            q = q.eq("status", status)
        result = q.execute()

        experiments = []
        for row in (result.data if hasattr(result, "data") else []):
            try:
                row["variants"] = json.loads(row.get("variants", "[]"))
            except (json.JSONDecodeError, TypeError):
                row["variants"] = []
            experiments.append(row)

        return {"experiments": experiments, "total": len(experiments)}
    except Exception as e:
        logger.error("Failed to list experiments: %s", e)
        return {"experiments": [], "total": 0, "error": str(e)}


@router.get("/{experiment_id}")
@limiter.limit("60/minute")
def get_experiment(experiment_id: str, request: Request,
                    _staff=Depends(require_staff)):
    """Get a single experiment by ID."""
    try:
        result = supabase.table("experiments").select("*").eq("id", experiment_id).execute()
        rows = result.data if hasattr(result, "data") else []
        if not rows:
            raise HTTPException(404, "Experiment not found")

        row = dict(rows[0])
        try:
            row["variants"] = json.loads(row.get("variants", "[]"))
        except (json.JSONDecodeError, TypeError):
            row["variants"] = []

        # Get assignment counts per variant
        try:
            assign_result = supabase.table("experiment_assignments").select("variant", count="exact").eq("experiment_id", experiment_id).execute()
        except Exception:
            assign_result = None

        variant_counts = {}
        if assign_result and hasattr(assign_result, "data"):
            for a in assign_result.data:
                v = a.get("variant", "unknown")
                variant_counts[v] = variant_counts.get(v, 0) + 1
        row["assignment_counts"] = variant_counts

        # Get conversion counts per variant
        try:
            conv_result = supabase.table("experiment_conversions").select("variant", count="exact").eq("experiment_id", experiment_id).execute()
        except Exception:
            conv_result = None

        conversion_counts = {}
        if conv_result and hasattr(conv_result, "data"):
            for c in conv_result.data:
                v = c.get("variant", "unknown")
                conversion_counts[v] = conversion_counts.get(v, 0) + 1
        row["conversion_counts"] = conversion_counts

        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get experiment %s: %s", experiment_id, e)
        raise HTTPException(500, str(e))


@router.patch("/{experiment_id}")
@limiter.limit("30/minute")
def update_experiment(experiment_id: str, request: Request,
                       body: UpdateExperimentRequest,
                       _staff=Depends(require_staff)):
    """Update experiment status/name/description."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")

    updates["updated_at"] = _now_iso()

    try:
        supabase.table("experiments").update(updates).eq("id", experiment_id).execute()
        logger.info("Experiment %s updated: %s", experiment_id, updates)
        return {"ok": True, "updated": updates}
    except Exception as e:
        logger.error("Failed to update experiment %s: %s", experiment_id, e)
        raise HTTPException(500, str(e))


@router.delete("/{experiment_id}")
@limiter.limit("10/minute")
def delete_experiment(experiment_id: str, request: Request,
                       _staff=Depends(require_staff)):
    """Delete an experiment and its assignments/conversions."""
    try:
        supabase.table("experiment_conversions").delete().eq("experiment_id", experiment_id).execute()
        supabase.table("experiment_assignments").delete().eq("experiment_id", experiment_id).execute()
        supabase.table("experiments").delete().eq("id", experiment_id).execute()
        logger.info("Experiment %s deleted", experiment_id)
        return {"ok": True}
    except Exception as e:
        logger.error("Failed to delete experiment %s: %s", experiment_id, e)
        raise HTTPException(500, str(e))


@router.get("/{experiment_id}/results")
@limiter.limit("30/minute")
def get_experiment_results(experiment_id: str, request: Request,
                            _staff=Depends(require_staff)):
    """Get statistical results for an experiment with conversion rates."""
    try:
        # Get experiment metadata
        exp_result = supabase.table("experiments").select("*").eq("id", experiment_id).execute()
        rows = exp_result.data if hasattr(exp_result, "data") else []
        if not rows:
            raise HTTPException(404, "Experiment not found")

        exp = dict(rows[0])
        try:
            variants = json.loads(exp.get("variants", "[]"))
        except (json.JSONDecodeError, TypeError):
            variants = []

        # Get assignment counts
        try:
            assign_result = supabase.table("experiment_assignments").select("variant", count="exact").eq("experiment_id", experiment_id).execute()
        except Exception:
            assign_result = None

        # Get conversion counts
        try:
            conv_result = supabase.table("experiment_conversions").select("variant", count="exact").eq("experiment_id", experiment_id).execute()
        except Exception:
            conv_result = None

        # Build per-variant stats
        assignment_counts = {}
        conversion_counts = {}

        if assign_result and hasattr(assign_result, "data"):
            for a in assign_result.data:
                v = a.get("variant", "unknown")
                assignment_counts[v] = assignment_counts.get(v, 0) + 1

        if conv_result and hasattr(conv_result, "data"):
            for c in conv_result.data:
                v = c.get("variant", "unknown")
                conversion_counts[v] = conversion_counts.get(v, 0) + 1

        variant_stats = []
        total_assigned = sum(assignment_counts.values())

        for v in variants:
            key = v.get("key", v.get("name", "unknown"))
            assigned = assignment_counts.get(key, 0)
            converted = conversion_counts.get(key, 0)
            rate = round(converted / assigned * 100, 2) if assigned > 0 else 0

            variant_stats.append({
                "variant": key,
                "name": v.get("name", key),
                "assigned": assigned,
                "converted": converted,
                "conversion_rate": rate,
                "share_pct": round(assigned / total_assigned * 100, 2) if total_assigned > 0 else 0,
            })

        # Find winner (highest conversion rate)
        if variant_stats:
            winner = max(variant_stats, key=lambda x: x["conversion_rate"])
        else:
            winner = None

        return {
            "experiment": exp["name"],
            "status": exp.get("status", "unknown"),
            "goal": exp.get("goal", "conversion"),
            "variants": variant_stats,
            "winner": winner,
            "total_assigned": total_assigned,
            "total_converted": sum(conversion_counts.values()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get results for experiment %s: %s", experiment_id, e)
        raise HTTPException(500, str(e))


# ── Public assignment endpoint (used by frontend) ────────

@router.post("/{experiment_id}/assign")
@limiter.limit("120/minute")
def assign_variant(experiment_id: str, request: Request):
    """Assign a user to an experiment variant. Used by landing page / CTA."""
    # Get experiment
    try:
        exp_result = supabase.table("experiments").select("*").eq("id", experiment_id).execute()
        rows = exp_result.data if hasattr(exp_result, "data") else []
    except Exception:
        return {"variant": "control", "reason": "experiment_fetch_failed"}

    if not rows:
        return {"variant": "control", "reason": "not_found"}

    exp = dict(rows[0])
    if exp.get("status") != "running":
        return {"variant": "control", "reason": f"status={exp.get('status')}"}

    try:
        variants = json.loads(exp.get("variants", "[]"))
    except (json.JSONDecodeError, TypeError):
        return {"variant": "control", "reason": "invalid_variants"}

    if len(variants) < 2:
        return {"variant": "control", "reason": "too_few_variants"}

    # Check if user already assigned
    user_id = request.headers.get("X-User-Id") or request.client.host
    try:
        existing = supabase.table("experiment_assignments").select("variant").eq("experiment_id", experiment_id).eq("user_id", user_id).execute()
        if existing.data and len(existing.data) > 0:
            return {"variant": existing.data[0]["variant"], "reason": "already_assigned"}
    except Exception:
        pass

    # Weighted random assignment
    import random
    total_weight = sum(v.get("weight", 1.0) for v in variants)
    r = random.random() * total_weight
    cumulative = 0
    chosen = variants[0]["key"]
    for v in variants:
        cumulative += v.get("weight", 1.0)
        if r <= cumulative:
            chosen = v["key"]
            break

    # Record assignment
    now = _now_iso()
    try:
        supabase.table("experiment_assignments").insert({
            "experiment_id": experiment_id,
            "user_id": user_id,
            "variant": chosen,
            "assigned_at": now,
        }).execute()
    except Exception as e:
        logger.warning("Failed to record assignment: %s", e)

    return {"variant": chosen, "experiment": exp["name"]}


@router.post("/{experiment_id}/convert")
@limiter.limit("120/minute")
def record_conversion(experiment_id: str, request: Request):
    """Record a conversion event for a user in an experiment."""
    user_id = request.headers.get("X-User-Id") or request.client.host

    # Look up assignment
    try:
        existing = supabase.table("experiment_assignments").select("variant").eq("experiment_id", experiment_id).eq("user_id", user_id).execute()
        if not existing.data or len(existing.data) == 0:
            return {"ok": False, "reason": "not_assigned"}
        variant = existing.data[0]["variant"]
    except Exception as e:
        return {"ok": False, "reason": str(e)}

    # Get experiment goal
    try:
        exp_result = supabase.table("experiments").select("goal").eq("id", experiment_id).execute()
        goal = exp_result.data[0]["goal"] if exp_result.data else "conversion"
    except Exception:
        goal = "conversion"

    # Record conversion
    now = _now_iso()
    try:
        supabase.table("experiment_conversions").insert({
            "experiment_id": experiment_id,
            "user_id": user_id,
            "variant": variant,
            "goal": goal,
            "converted_at": now,
        }).execute()
        return {"ok": True, "variant": variant, "goal": goal}
    except Exception as e:
        logger.warning("Failed to record conversion: %s", e)
        return {"ok": False, "reason": str(e)}
