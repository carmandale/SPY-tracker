"""
Custom exception handlers and error responses for SPY TA Tracker API
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class SPYTrackerException(Exception):
    """Base exception for SPY Tracker application"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DataNotFoundException(SPYTrackerException):
    """Raised when requested data is not found"""
    def __init__(self, message: str = "Data not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class MarketDataException(SPYTrackerException):
    """Raised when market data cannot be fetched"""
    def __init__(self, message: str = "Market data unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class PredictionLockedException(SPYTrackerException):
    """Raised when trying to modify a locked prediction"""
    def __init__(self, message: str = "Prediction is locked and cannot be modified", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class InvalidDateRangeException(SPYTrackerException):
    """Raised when date range is invalid"""
    def __init__(self, message: str = "Invalid date range", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ValidationException(SPYTrackerException):
    """Raised when data validation fails"""
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


async def spy_tracker_exception_handler(request: Request, exc: SPYTrackerException):
    """Handle custom SPY Tracker exceptions"""
    logger.error(f"SPYTrackerException: {exc.message} - Details: {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with user-friendly messages"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed for the provided data",
                "type": "ValidationError",
                "details": {"validation_errors": errors}
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPExceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "HTTPException",
                "details": {}
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "type": "InternalServerError",
                "details": {"hint": "Check server logs for more information"}
            }
        }
    )


def create_error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "details": details or {}
            }
        }
    )