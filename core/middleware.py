from fastapi import Request, HTTPException, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Define allowed hosts and origins
ALLOWED_HOST = "api.duckycart.me"

# Define CORS origins
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080", 
    "https://64.226.127.205",
    "https://api.duckycart.me",
    "https://aastsmartcart.vercel.app",
]

class EnforceSubdomainMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure requests only come through the designated subdomain"""
    
    async def dispatch(self, request: Request, call_next):
        # Allow localhost for development
        if request.url.hostname not in [ALLOWED_HOST, "localhost", "127.0.0.1"]:
            raise HTTPException(status_code=403, detail=f"Forbidden: Use {ALLOWED_HOST}")
        return await call_next(request)

def add_middlewares(app: FastAPI):
    """Add all necessary middlewares to the application"""
    
    # Add subdomain enforcement middleware
    app.add_middleware(EnforceSubdomainMiddleware)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app