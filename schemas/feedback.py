from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SatisfactionLevel(str, Enum):
    SAD = "sad"
    NEUTRAL = "neutral"
    HAPPY = "happy"

class FeedbackItemBase(BaseModel):
    text: str
    category: str

class FeedbackItem(FeedbackItemBase):
    id: int
    
    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    session_id: int
    satisfaction: SatisfactionLevel
    additional_comments: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    selected_item_ids: List[int]

class FeedbackResponse(FeedbackBase):
    id: int
    created_at: datetime
    selected_items: List[FeedbackItem]
    
    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    total: int
    sad: int
    neutral: int
    happy: int
    top_sad_items: List[FeedbackItemBase]
    top_neutral_items: List[FeedbackItemBase]
    top_happy_items: List[FeedbackItemBase]