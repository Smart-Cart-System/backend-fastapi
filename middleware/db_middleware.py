from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import OperationalError
import logging

logger = logging.getLogger(__name__)

class DBConnectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle database connection failures.
    Particularly useful for the "MySQL server has gone away" error.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Try to process the request normally
            response = await call_next(request)
            return response
        except OperationalError as e:
            # Check if it's a "MySQL server has gone away" error
            if "MySQL server has gone away" in str(e):
                logger.warning("MySQL connection lost. Attempting to reconnect...")
                
                # Force reconnection of all connections in the pool
                from database import engine
                engine.dispose()
                
                logger.info("Connection pool reset. Retrying the request...")
                
                # Retry the request once
                try:
                    response = await call_next(request)
                    return response
                except Exception as retry_error:
                    logger.error(f"Failed to process request after reconnection: {retry_error}")
                    # Return a 500 error with a user-friendly message
                    return Response(
                        content='{"status_code": 500, "message": "Database connection error", "details": {"error": "Service temporarily unavailable"}}',
                        status_code=500,
                        media_type="application/json"
                    )
            # For other SQLAlchemy errors, let them be handled by the exception handlers
            raise