from typing import Any, Dict, Optional


def api_meta() -> Dict[str, Any]:
    """
    Shared metadata to allow the frontend to style consistently.
    """
    return {
        "theme": {
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
            "style": "Minimalist",
        }
    }


# PUBLIC_INTERFACE
def api_response(data: Any, message: str = "success", code: str = "ok") -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "status": "success",
        "code": code,
        "message": message,
        "data": data,
        "meta": api_meta(),
    }


def api_error_response(code: str, message: str, details: Optional[Any]) -> Dict[str, Any]:
    """
    Create a standardized error response payload.
    """
    return {
        "status": "error",
        "code": code,
        "message": message,
        "details": details,
        "meta": api_meta(),
    }
