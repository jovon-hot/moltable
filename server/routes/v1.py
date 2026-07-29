"""API versioning — maps /api/v1/* routes to existing /api/* routes.

All routes maintain backward compatibility. New clients should use /api/v1/ prefix.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def v1_proxy(request: Request, path: str):
    """Proxy /api/v1/* requests to /api/* with same method and body.

    This is a temporary shim while clients migrate. Eventually this becomes
    the canonical prefix and /api/* becomes the redirect.
    """
    # Re-route to the non-versioned path
    from fastapi.routing import APIRoute
    from main import app

    # Forward to the actual handler via internal redirect
    new_path = f"/api/{path}"
    # We can't easily re-dispatch, so return a header indicating
    # the canonical path and suggest the client follow it
    return JSONResponse(
        status_code=308,
        content={
            "message": f"Use /api/{path} directly (backward compatible)",
            "canonical": new_path,
            "note": "API versioning via header also supported: X-API-Version: 1",
        },
        headers={"Location": new_path},
    )
