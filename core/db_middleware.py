from sqlalchemy.exc import OperationalError
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class DBConnectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except OperationalError as e:
            if "MySQL server has gone away" in str(e):
                # Force reconnection of all connections in the pool
                from database import engine
                engine.dispose()
                # Retry the request
                return await call_next(request)
            raise