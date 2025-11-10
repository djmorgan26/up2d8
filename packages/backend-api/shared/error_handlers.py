"""
Custom error handlers for API validation and exceptions.

Provides standardized error responses with clear, actionable messages.
"""

import logging
from typing import Any, Dict, List

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def format_validation_error(error: dict) -> dict:
    """
    Format a single Pydantic validation error into a user-friendly message.

    Args:
        error: Pydantic validation error dict

    Returns:
        Formatted error dict with field, message, and type
    """
    loc = error.get("loc", [])
    msg = error.get("msg", "Validation error")
    error_type = error.get("type", "value_error")

    # Extract field name from location
    # loc is typically ("body", "field_name") or ("body", "field_name", "nested_field")
    field_name = ".".join(str(item) for item in loc if item != "body")

    # Clean up common Pydantic error messages for better readability
    if "String should have at least" in msg:
        msg = msg.replace("String should have at least", "Must be at least")
        msg = msg.replace("characters", "characters long")
    elif "String should have at most" in msg:
        msg = msg.replace("String should have at most", "Cannot exceed")
        msg = msg.replace("characters", "characters")
    elif "Field required" in msg:
        msg = "This field is required"
    elif "ensure this value" in msg.lower():
        msg = msg.replace("ensure this value", "Value")
    elif "Input should be a valid" in msg:
        msg = msg.replace("Input should be a valid", "Must be a valid")

    return {
        "field": field_name,
        "message": msg,
        "type": error_type.replace("_", " ").title()
    }


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Custom handler for request validation errors.

    Provides clear, structured error messages for invalid API requests.

    Args:
        request: FastAPI request object
        exc: Request validation exception

    Returns:
        JSONResponse with formatted validation errors
    """
    # Format all validation errors
    errors = [format_validation_error(error) for error in exc.errors()]

    # Log validation errors for monitoring (without request body to avoid serialization issues)
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    # Create response with detailed error information
    response_body = {
        "error": "Validation Error",
        "message": "The request contains invalid or missing fields",
        "details": errors,
        "path": request.url.path,
        "method": request.method
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_body
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Custom handler for Pydantic validation errors (from model validation).

    Args:
        request: FastAPI request object
        exc: Pydantic validation exception

    Returns:
        JSONResponse with formatted validation errors
    """
    # Format all validation errors
    errors = [format_validation_error(error) for error in exc.errors()]

    logger.warning(
        f"Pydantic validation error on {request.method} {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    response_body = {
        "error": "Validation Error",
        "message": "The data contains invalid fields",
        "details": errors,
        "path": request.url.path
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_body
    )


def create_error_response(
    status_code: int,
    error: str,
    message: str,
    details: Any = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code
        error: Error type/category
        message: User-friendly error message
        details: Optional additional details

    Returns:
        Standardized error response dict
    """
    response = {
        "error": error,
        "message": message,
        "status_code": status_code
    }

    if details is not None:
        response["details"] = details

    return response


# Common error response templates
def not_found_error(resource: str, identifier: str = None) -> Dict[str, Any]:
    """Create a 404 Not Found error response."""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"

    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        error="Not Found",
        message=message
    )


def bad_request_error(message: str, details: Any = None) -> Dict[str, Any]:
    """Create a 400 Bad Request error response."""
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error="Bad Request",
        message=message,
        details=details
    )


def unauthorized_error(message: str = "Authentication required") -> Dict[str, Any]:
    """Create a 401 Unauthorized error response."""
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error="Unauthorized",
        message=message
    )


def forbidden_error(message: str = "Access denied") -> Dict[str, Any]:
    """Create a 403 Forbidden error response."""
    return create_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        error="Forbidden",
        message=message
    )


def internal_server_error(message: str = "An internal error occurred") -> Dict[str, Any]:
    """Create a 500 Internal Server Error response."""
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="Internal Server Error",
        message=message
    )


def service_unavailable_error(message: str = "Service temporarily unavailable") -> Dict[str, Any]:
    """Create a 503 Service Unavailable error response."""
    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error="Service Unavailable",
        message=message
    )
