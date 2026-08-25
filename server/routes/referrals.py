"""Referral / Invite system.

Endpoints:
  POST /api/referrals/generate        — create a unique 8-char invite code (auth required)
  GET  /api/referrals/{code}          — public code lookup (used on the signup page)
  GET  /api/referrals/stats/{user_id} — referral stats for a user (auth required, owner only)
  POST /api/referrals/claim           — claim a referral code at signup (public)

Table `referrals` (Supabase migration / SQLite schema):
  id, referrer_id, code (unique, 8-char alphanumeric), referred_email,
  status (pending|claimed), created_at, claimed_at

Auth: generate + stats require an authenticated user (Supabase JWT, API key,
or session token via `routes.auth.get_user`). Lookup and claim are intentionally
public because they run on the signup page *before* an account exists.
"""
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app_state import limiter, supabase
from routes.auth import get_user
from services.bonus_service import (
    SHARE_BONUS_CAP, SHARE_BONUS_GB, count_share_bonuses, get_bonus_gb, grant_bonus,
)

logger = logging.getLogger("moltable.referrals")

router = APIRouter(prefix="/api/referrals", tags=["referrals"])

CODE_LENGTH = 8

APP_URL = os.getenv("APP_URL", "https://moltable.ai")


# ── Pydantic models ──────────────────────────────────────

class GenerateReferralRequest(BaseModel):
    """Optional email the invite will be sent to (stored on the code)."""
    email: Optional[str] = Field(None, max_length=320)


class ClaimReferralRequest(BaseModel):
    code: str = Field(..., min_length=CODE_LENGTH, max_length=CODE_LENGTH)
    email: str = Field(..., min_length=3, max_length=320)


class ClaimShareBonusRequest(BaseModel):
    post_url: str = Field(..., min_length=10, max_length=2048)


# ── Helpers ──────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_code() -> str:
    """8-char alphanumeric code derived from a UUID (uuid4 hex, uppercased).

    UUID-based so codes are globally unique-ish by construction; the DB unique
    constraint + retry loop in generate_referral guards against collisions.
    """
    return uuid.uuid4().hex[:CODE_LENGTH].upper()


def _share_url(code: str) -> str:
    return f"{APP_URL}/signup?ref={code}"


def _normalize_code(code: str) -> str:
    return code.strip().upper()


# ── Endpoints ────────────────────────────────────────────

@router.post("/generate")
@limiter.limit("20/minute")
def generate_referral(request: Request, body: GenerateReferralRequest,
                      user_id: str = Depends(get_user)):
    """Create a unique invite code for the authenticated user.

    Reuses the user's existing pending code if they already have one, so
    refreshing the referrals page doesn't burn codes.
    """
    # 1. Reuse existing pending code (idempotent)
    try:
        existing = supabase.table("referrals").select(
            "code,status,created_at"
        ).eq("referrer_id", user_id).eq("status", "pending").execute()
        rows = existing.data if hasattr(existing, "data") else []
        if rows:
            row = rows[0]
            return {
                "code": row["code"],
                "status": row.get("status", "pending"),
                "created_at": row.get("created_at"),
                "share_url": _share_url(row["code"]),
                "reused": True,
            }
    except Exception as e:
        logger.warning("Existing referral lookup failed: %s", e)

    # 2. Generate a fresh unique code (retry on the rare collision)
    code = None
    for _ in range(5):
        candidate = _generate_code()
        try:
            dup = supabase.table("referrals").select("id").eq("code", candidate).execute()
            if dup.data:
                continue
            code = candidate
            break
        except Exception:
            code = candidate
            break
    if code is None:
        raise HTTPException(500, "Could not allocate a unique referral code")

    now = _now_iso()
    data = {
        "referrer_id": user_id,
        "code": code,
        "referred_email": body.email,
        "status": "pending",
        "created_at": now,
    }
    try:
        supabase.table("referrals").insert(data).execute()
        logger.info("Referral code %s created for user %s", code, user_id)
    except Exception as e:
        logger.error("Failed to create referral code: %s", e)
        raise HTTPException(500, "Failed to create referral code")

    return {
        "code": code,
        "status": "pending",
        "created_at": now,
        "share_url": _share_url(code),
        "reused": False,
    }


@router.get("/stats/{user_id}")
@limiter.limit("60/minute")
def referral_stats(user_id: str, request: Request,
                   auth_user_id: str = Depends(get_user)):
    """Referral stats for a user — only the owner may view their own stats."""
    if user_id != auth_user_id:
        raise HTTPException(403, "You can only view your own referral stats")

    try:
        result = supabase.table("referrals").select("*").eq(
            "referrer_id", user_id
        ).order("created_at", desc=True).execute()
        rows = result.data if hasattr(result, "data") else []
    except Exception as e:
        logger.error("Failed to fetch referral stats for %s: %s", user_id, e)
        raise HTTPException(500, "Failed to fetch referral stats")

    codes = [{
        "code": r.get("code"),
        "status": r.get("status", "pending"),
        "referred_email": r.get("referred_email"),
        "created_at": r.get("created_at"),
        "claimed_at": r.get("claimed_at"),
    } for r in rows]

    return {
        "referrer_id": user_id,
        "invites_sent": len(rows),
        "claimed": sum(1 for r in rows if r.get("status") == "claimed"),
        "pending": sum(1 for r in rows if r.get("status") == "pending"),
        "codes": codes,
    }


@router.get("/{code}")
@limiter.limit("60/minute")
def lookup_referral(code: str, request: Request):
    """Public lookup — validate an invite code on the signup page."""
    normalized = _normalize_code(code)
    try:
        result = supabase.table("referrals").select("*").eq("code", normalized).execute()
        rows = result.data if hasattr(result, "data") else []
    except Exception as e:
        logger.error("Referral lookup failed for %s: %s", normalized, e)
        raise HTTPException(500, "Failed to look up referral code")

    if not rows:
        raise HTTPException(404, "Invalid referral code")

    row = dict(rows[0])

    # Attach referrer display info (public, minimal)
    referrer = {}
    try:
        u = supabase.table("users").select("name,email").eq(
            "id", row.get("referrer_id")
        ).execute()
        if u.data:
            referrer = {
                "name": u.data[0].get("name"),
                "email": u.data[0].get("email"),
            }
    except Exception:
        pass

    return {
        "code": row["code"],
        "status": row.get("status", "pending"),
        "referrer_id": row.get("referrer_id"),
        "referrer": referrer,
        "created_at": row.get("created_at"),
    }


@router.post("/claim")
@limiter.limit("20/minute")
def claim_referral(request: Request, body: ClaimReferralRequest):
    """Claim a referral code at signup — records the new user's email and
    flips the code from pending → claimed.
    """
    code = _normalize_code(body.code)
    email = body.email.strip().lower()

    try:
        result = supabase.table("referrals").select("*").eq("code", code).execute()
        rows = result.data if hasattr(result, "data") else []
    except Exception as e:
        logger.error("Referral claim lookup failed for %s: %s", code, e)
        raise HTTPException(500, "Failed to claim referral code")

    if not rows:
        raise HTTPException(404, "Invalid referral code")

    row = dict(rows[0])
    if row.get("status") == "claimed":
        raise HTTPException(409, "Referral code already claimed")

    # Prevent self-referral (claimer's email matches the referrer's email)
    try:
        u = supabase.table("users").select("email").eq(
            "id", row.get("referrer_id")
        ).execute()
        if u.data and u.data[0].get("email"):
            if u.data[0]["email"].strip().lower() == email:
                raise HTTPException(400, "You cannot use your own referral code")
    except HTTPException:
        raise
    except Exception:
        pass

    now = _now_iso()
    try:
        supabase.table("referrals").update({
            "status": "claimed",
            "referred_email": email,
            "claimed_at": now,
        }).eq("id", row["id"]).execute()
        logger.info("Referral code %s claimed by %s (referrer %s)", code, email, row.get("referrer_id"))
    except Exception as e:
        logger.error("Failed to claim referral %s: %s", code, e)
        raise HTTPException(500, "Failed to claim referral code")

    return {
        "ok": True,
        "code": code,
        "status": "claimed",
        "referrer_id": row.get("referrer_id"),
        "claimed_at": now,
    }


@router.post("/share-bonus")
@limiter.limit("10/hour")
def claim_share_bonus(request: Request, body: ClaimShareBonusRequest,
                      user_id: str = Depends(get_user)):
    """分享 LinkedIn 帖子 → +1GB 永久存储额度（上限 3 次）。

    验证：帖子链接必须是 http(s) 且指向 linkedin.com；同一链接不可重复领取。
    """
    post_url = body.post_url.strip()
    if not post_url.startswith(("https://", "http://")):
        raise HTTPException(400, "无效的帖子链接")
    if "linkedin.com" not in post_url.lower():
        raise HTTPException(400, "请提供 LinkedIn 帖子链接")

    count = count_share_bonuses(user_id)
    if count >= SHARE_BONUS_CAP:
        raise HTTPException(409, f"分享奖励已达上限（{SHARE_BONUS_CAP}GB）")

    if not grant_bonus(user_id, "share", SHARE_BONUS_GB, source=post_url):
        raise HTTPException(409, "该帖子已领取过奖励")

    total = get_bonus_gb(user_id)
    return {
        "ok": True,
        "event_type": "share",
        "amount_gb": SHARE_BONUS_GB,
        "bonus_storage_gb": total,
        "remaining": SHARE_BONUS_CAP - count - 1,
    }
