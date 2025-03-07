from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND

# Define standard error response structure
class ErrorResponse:
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
    
    def dict(self):
        return {
            "status_code": self.status_code,
            "message": self.message,
            "details": self.details
        }

# Exception Handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error in request data",
            details={"errors": exc.errors()}
        ).dict()
    )

async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal data validation error",
            details={"errors": exc.errors()}
        ).dict()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Database error",
            details={"error": str(exc)}
        ).dict()
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Data validation error",
            details={"errors": exc.errors()}
        ).dict()
    )

# Improved handler to differentiate between invalid URLs/actions and not found resources
async def not_found_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_404_NOT_FOUND:
        # Check if this is a route not found error (no detail message)
        # or a method not allowed error (detail message usually specifies the method)
        if not exc.detail or "Method" in str(exc.detail) or isinstance(exc.detail, str) and "not found" in exc.detail.lower():
            # This is likely a route not found or method not allowed
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Invalid endpoint or request method",
                    details={
                        "error": "The requested URL or HTTP method is invalid",
                        "requested_url": str(request.url),
                        "method": request.method
                    }
                ).dict()
            )
        else:
            # This is a resource not found (raised from within a route handler)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Resource not found",
                    details={
                        "error": str(exc.detail)
                    }
                ).dict()
            )
    
    # For other HTTP errors, keep them as they are
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=str(exc.detail),
            details={}
        ).dict()
    )

# Generic exception handler for any other exceptions
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            details={"error": str(exc)}
        ).dict()
    )