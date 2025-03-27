from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.customer_session import RecentSessionsResponse
from schemas.cart_item import CartItemResponse, CartItemListResponse
from crud.user import get_recent_sessions, get_user_sessions_with_cart_details
from crud.cart_item import get_cart_items_by_session
from core.security import get_current_user, verify_pi_api_key
from models.user import User
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/sessions/{user_id}", response_model=RecentSessionsResponse)
def get_all_sessions(user_id: int, db: Session = Depends(get_db)):
    """Get all sessions for a specific user"""
    sessions = get_user_sessions_with_cart_details(db, user_id)
    if not sessions:
        raise HTTPException(status_code=404, detail="No recent sessions found")
    return RecentSessionsResponse(sessions=sessions)