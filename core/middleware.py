from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Define allowed hosts and origins
ALLOWED_HOST = "api.duckycart.me"

# Define CORS origins
CORS_ORIGINS = [
    "*",
]



def add_middlewares(app: FastAPI):
    """Add all necessary middlewares to the application"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app