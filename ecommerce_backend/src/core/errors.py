from typing import Any, Optional
from fastapi import status


class APIError(Exception):
    """
    Custom API error to be caught by middleware and rendered consistently.
    """

    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def bad_request(message: str, details: Optional[Any] = None) -> APIError:
    return APIError("bad_request", message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


def unauthorized(message: str = "Unauthorized", details: Optional[Any] = None) -> APIError:
    return APIError("unauthorized", message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


def forbidden(message: str = "Forbidden", details: Optional[Any] = None) -> APIError:
    return APIError("forbidden", message, status_code=status.HTTP_403_FORBIDDEN, details=details)


def not_found(message: str = "Not found", details: Optional[Any] = None) -> APIError:
    return APIError("not_found", message, status_code=status.HTTP_404_NOT_FOUND, details=details)
