from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from database import get_db

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("/", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint that verifies database connectivity.
    This endpoint helps keep database connections alive and provides system status.
    """
    try:
        # Simple query to verify connection is working
        result = db.execute(text("SELECT 1")).scalar()
        
        return {
            "status": "healthy",
            "services": {
                "database": {
                    "status": "up" if result == 1 else "degraded",
                    "message": "Database connection successful"
                }
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "services": {
                "database": {
                    "status": "down",
                    "error": str(e)
                }
            }
        }

@router.get("/readiness")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe to check if the application is ready to receive traffic.
    """
    return {"status": "ready"}

@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe to check if the application is running.
    """
    return {"status": "alive"}