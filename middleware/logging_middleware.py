from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from services.logging_service import LoggingService, LogLevel
from database import get_db

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = int((time.time() - start_time) * 1000)
            
            # Log performance metrics
            db = next(get_db())
            logging_service = LoggingService(db)
            
            user_id = getattr(request.state, 'user_id', None)
            
            logging_service.log_performance(
                endpoint=str(request.url.path),
                method=request.method,
                response_time_ms=process_time,
                status_code=response.status_code,
                user_id=user_id,
                additional_data={
                    "request_id": request_id,
                    "query_params": dict(request.query_params),
                    "ip_address": client_ip,
                    "user_agent": user_agent
                }
            )
            
            return response
            
        except Exception as e:
            # Log errors
            db = next(get_db())
            logging_service = LoggingService(db)
            
            logging_service.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                severity="HIGH",
                endpoint=str(request.url.path),
                user_id=getattr(request.state, 'user_id', None),
                additional_data={
                    "request_id": request_id,
                    "method": request.method,
                    "ip_address": client_ip,
                    "user_agent": user_agent
                }
            )
            raise