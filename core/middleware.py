from fastapi import FastAPI
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



def add_middlewares(app: FastAPI):
    """Add all necessary middlewares to the application"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app