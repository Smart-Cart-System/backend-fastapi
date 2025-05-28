from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.feedback import Feedback as FeedbackModel
from schemas.feedback import FeedbackItem, FeedbackCreate, FeedbackResponse, FeedbackStats
from crud import feedback as feedback_crud
from models.customer_session import CustomerSession
from core.security import get_current_user
from models.user import User

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"]
)

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a shopping session
    """
    # Check if feedback already exists for this session
    existing = feedback_crud.get_feedback_by_session(db, feedback_data.session_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Feedback already exists for this session"
        )
    
    # Check if the session exists and belongs to the current user
    session = db.query(CustomerSession).filter(
        CustomerSession.session_id == feedback_data.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit feedback for this session"
        )
    
    return feedback_crud.create_feedback(db, feedback_data)

@router.get("/session/{session_id}", response_model=FeedbackResponse)
def get_feedback_by_session(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback for a specific shopping session
    """
    feedback = feedback_crud.get_feedback_by_session(db, session_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this session"
        )
    return feedback

@router.get("/", response_model=List[FeedbackResponse])
def get_all_feedback(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all feedback (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all feedback"
        )
    return feedback_crud.get_all_feedback(db, skip, limit)

@router.get("/items", response_model=List[FeedbackItem])
def get_feedback_items(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get available feedback items for a specific category or all categories
    """
    items = db.query(feedback_crud.FeedbackItem)
    
    if category:
        items = items.filter(feedback_crud.FeedbackItem.category == category)
        
    return items.all()

@router.get("/stats", response_model=FeedbackStats)
def get_feedback_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback statistics (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view feedback statistics"
        )
    return feedback_crud.get_feedback_stats(db)