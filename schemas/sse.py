from pydantic import BaseModel
from typing import Dict, Any, Optional

class SSEMessage(BaseModel):
    """Base SSE message structure"""
    event: str
    data: Dict[str, Any]

class SSEAuthMessage(BaseModel):
    """Base authenticated SSE message"""
    session_id: int
    token: str  # Bearer token
    event_type: str
