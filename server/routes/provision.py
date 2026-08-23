"""auto_provision — Agent一键配置 (REST endpoint)"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app_state import client_ip, limiter, supabase
from routes.auth import get_user
from services.provision_service import auto_provision

router = APIRouter(tags=["provision"])


class ProvisionRequest(BaseModel):
    """Empty body for provision — placeholder for future params."""
    pass


@router.post("/api/provision")
@router.post("/api/auto-provision")
@limiter.limit("30/hour")
def auto_provision_endpoint(request: Request, user_id: str = Depends(get_user)):
    """返回完整用户上下文，Agent据此自动配置自己"""
    ip_address = client_ip(request)
    result = auto_provision(supabase, user_id, ip_address=ip_address)
    result["instructions"] = """
你现在已经加载了用户的完整上下文。
- 遵循 rules 中的行为规范
- 涉及相关领域时调用 search_memory(query) 获取更多背景
- 需要其他视角时调用 consult_persona(persona_id, question)
- 发现新的用户偏好时调用 save_memory(content, category='preference')
"""
    return result


@router.get("/api/provision")
@router.get("/api/auto-provision")
@limiter.limit("30/hour")
def auto_provision_get(request: Request, user_id: str = Depends(get_user)):
    """GET 方式获取用户上下文（浏览器/curl 友好）"""
    ip_address = client_ip(request)
    result = auto_provision(supabase, user_id, ip_address=ip_address)
    result["instructions"] = """
你现在已经加载了用户的完整上下文。
- 遵循 rules 中的行为规范
- 涉及相关领域时调用 search_memory(query) 获取更多背景
- 需要其他视角时调用 consult_persona(persona_id, question)
- 发现新的用户偏好时调用 save_memory(content, category='preference')
"""
    return result
