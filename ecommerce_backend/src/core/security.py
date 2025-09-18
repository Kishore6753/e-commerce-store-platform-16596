import base64
import json
from typing import List, Optional
from fastapi import Request
from src.core.errors import unauthorized, forbidden
from src.core.settings import settings


class UserContext:
    """
    Minimal representation of authenticated user context.
    """
    def __init__(self, user_id: str, email: Optional[str], roles: Optional[List[str]] = None):
        self.user_id = user_id
        self.email = email
        self.roles = roles or []


def _parse_jwt_without_verification(token: str) -> Optional[dict]:
    """
    Parse JWT payload without verifying signature to extract claims.
    WARNING: This is for demo/dev purposes. In production, verify signature using SUPABASE_JWT_SECRET.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # Add padding for base64
        padding = '=' * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(decoded)
    except Exception:
        return None


async def get_current_user_optional(request: Request) -> Optional[UserContext]:
    """
    Extract user from Authorization: Bearer <token> header if present.
    Signature verification is not implemented here; for production integrate Supabase Admin SDK or JWKS.
    """
    auth = request.headers.get("Authorization") or request.cookies.get("sb:token")
    if not auth:
        return None
    token = auth.replace("Bearer ", "")
    claims = _parse_jwt_without_verification(token)
    if not claims:
        return None
    user_id = claims.get("sub") or claims.get("user_id")
    email = claims.get("email")
    roles = claims.get("roles") or claims.get("app_metadata", {}).get("roles") or []
    if not isinstance(roles, list):
        roles = [str(roles)]
    if not user_id:
        return None
    return UserContext(user_id=user_id, email=email, roles=roles)


# PUBLIC_INTERFACE
async def get_current_user_required(request: Request) -> UserContext:
    """FastAPI dependency to require authentication (Supabase JWT)."""
    user = await get_current_user_optional(request)
    if not user:
        raise unauthorized()
    return user


# PUBLIC_INTERFACE
def require_admin(user: UserContext):
    """Helper to ensure the user has admin role."""
    if "admin" not in (user.roles or []):
        raise forbidden("Admin privileges required")
