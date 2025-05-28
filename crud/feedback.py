from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any, Tuple
from models.feedback import Feedback, FeedbackItem, SatisfactionLevel
from schemas.feedback import FeedbackCreate

def create_feedback(db: Session, feedback_data: FeedbackCreate):
    # Create new feedback object
    db_feedback = Feedback(
        session_id=feedback_data.session_id,
        satisfaction=feedback_data.satisfaction,
        additional_comments=feedback_data.additional_comments
    )
    
    # Add feedback items
    if feedback_data.selected_item_ids:
        items = db.query(FeedbackItem).filter(
            FeedbackItem.id.in_(feedback_data.selected_item_ids)
        ).all()
        db_feedback.selected_items = items
    
    # Save to database
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback(db: Session, feedback_id: int):
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def get_feedback_by_session(db: Session, session_id: int):
    return db.query(Feedback).filter(Feedback.session_id == session_id).first()

def get_all_feedback(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Feedback).offset(skip).limit(limit).all()

def get_feedback_stats(db: Session):
    total = db.query(func.count(Feedback.id)).scalar()
    
    # Count by satisfaction level
    satisfaction_counts = db.query(
        Feedback.satisfaction, 
        func.count(Feedback.id)
    ).group_by(Feedback.satisfaction).all()
    
    # Create dictionary with counts
    counts = {level.value: 0 for level in SatisfactionLevel}
    for level, count in satisfaction_counts:
        counts[level.value] = count
    
    # Get top feedback items by category
    def get_top_items_by_category(category, limit=5):
        return (
            db.query(FeedbackItem, func.count(FeedbackItem.id).label('count'))
            .join(FeedbackItem.feedbacks)
            .filter(FeedbackItem.category == category)
            .group_by(FeedbackItem.id)
            .order_by(func.count(FeedbackItem.id).desc())
            .limit(limit)
            .all()
        )
    
    top_sad = get_top_items_by_category('sad')
    top_neutral = get_top_items_by_category('neutral')
    top_happy = get_top_items_by_category('happy')
    
    return {
        "total": total,
        "sad": counts.get("sad", 0),
        "neutral": counts.get("neutral", 0),
        "happy": counts.get("happy", 0),
        "top_sad_items": [item[0] for item in top_sad],
        "top_neutral_items": [item[0] for item in top_neutral],
        "top_happy_items": [item[0] for item in top_happy],
    }