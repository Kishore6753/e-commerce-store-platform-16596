"""
FastAPI backend for an e-commerce platform.

This application exposes RESTful endpoints for:
- Authentication (integrates with Supabase via JWT verification hook)
- Product and catalog management
- Cart management
- Order processing
- Payment provider integration (pluggable)
- Admin features

OpenAPI docs are enriched with tags, route summaries, and response models.
All responses and errors follow the Ocean Professional Minimalist style:
- clean, minimal JSON with consistent keys
- colors noted for frontend usage: primary(#374151), secondary(#9CA3AF), success(#10B981), error(#EF4444)

Environment configuration:
- SUPABASE_JWT_SECRET: JWT secret to validate Supabase-issued tokens (request from user; do not hardcode)
- SITE_URL: for email redirect to be used by frontend during signup flows
- PAYMENT_PROVIDER: selected provider id (e.g., "mock")
- PAYMENT_PROVIDER_API_KEY: provider secret (if needed by a real provider)
"""
from typing import Optional, List, Dict, Any
import os
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.errors import api_error_response, APIError
from src.core.security import get_current_user_optional, get_current_user_required, UserContext
from src.core.responses import api_response
from src.core.settings import settings
from src.modules.products.routes import router as products_router
from src.modules.cart.routes import router as cart_router
from src.modules.orders.routes import router as orders_router
from src.modules.payments.routes import router as payments_router
from src.modules.admin.routes import router as admin_router

openapi_tags = [
    {
        "name": "health",
        "description": "Service health and status.",
    },
    {
        "name": "auth",
        "description": "Authentication and user context (via Supabase JWT).",
    },
    {
        "name": "products",
        "description": "Product and catalog endpoints.",
    },
    {
        "name": "cart",
        "description": "Shopping cart operations for the current user/session.",
    },
    {
        "name": "orders",
        "description": "Order creation and management.",
    },
    {
        "name": "payments",
        "description": "Payment provider integration.",
    },
    {
        "name": "admin",
        "description": "Administrative operations (requires admin role).",
    },
]

app = FastAPI(
    title="E-commerce Backend",
    description="REST API for a minimalist Ocean Professional themed store.",
    version="1.0.0",
    contact={"name": "Tech Support", "email": "support@example.com"},
    license_info={"name": "Proprietary"},
    openapi_tags=openapi_tags,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Adds user context (if any) to request.state for easier access in handlers.
    """

    async def dispatch(self, request: Request, call_next):
        user_ctx = await get_current_user_optional(request)
        request.state.user = user_ctx
        try:
            response = await call_next(request)
            return response
        except APIError as e:
            return JSONResponse(
                status_code=e.status_code,
                content=api_error_response(code=e.code, message=e.message, details=e.details),
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=api_error_response(code="http_error", message=e.detail, details=None),
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content=api_error_response(code="internal_error", message="Unexpected server error", details=str(e)),
            )


app.add_middleware(RequestContextMiddleware)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Returns service health status.")
def health_check():
    """Healthcheck endpoint to verify the service is alive."""
    return api_response(data={"status": "ok", "service": "ecommerce-backend"})


class WhoAmI(BaseModel):
    """Represents the current authenticated principal."""
    user_id: Optional[str] = Field(None, description="User id from Supabase token")
    email: Optional[str] = Field(None, description="User email from token")
    roles: List[str] = Field(default_factory=list, description="List of roles (e.g., ['user','admin'])")


# PUBLIC_INTERFACE
@app.get("/auth/whoami", tags=["auth"], summary="Who Am I", description="Returns current user context (if authenticated).", response_model=Dict[str, Any])
async def who_am_i(request: Request):
    """Return the authenticated user's identity if available."""
    user: Optional[UserContext] = request.state.user
    payload = None
    if user:
        payload = WhoAmI(user_id=user.user_id, email=user.email, roles=user.roles).dict()
    return api_response(data={"user": payload})


# Routers
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


def custom_openapi():
    """
    Generate OpenAPI schema with app-level branding and tags.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-theme"] = {
        "name": "Ocean Professional",
        "colors": {
            "primary": "#374151",
            "secondary": "#9CA3AF",
            "success": "#10B981",
            "error": "#EF4444",
            "background": "#FFFFFF",
            "surface": "#F9FAFB",
            "text": "#111827",
        },
        "applicationStyle": "Minimalist",
    }
    openapi_schema["tags"] = openapi_tags
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
