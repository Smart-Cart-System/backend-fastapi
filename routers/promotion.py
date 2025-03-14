from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.security import get_current_user
from database import get_db
from models.user import User
from schemas.promotion import PromotionResponse
from crud import promotion

router = APIRouter(
    prefix="/promotions",  # Add the forward slash here
    tags=["promotions"]
)

@router.get("/", response_model=List[PromotionResponse])
def get_active_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get all currently active promotions"""
    promotions = promotion.get_active_promotions(db, skip=skip, limit=limit)
    return promotions

@router.get("/item/{item_no}", response_model=PromotionResponse)
def get_promotion_for_item(item_no: int, db: Session = Depends(get_db)):
    """Get active promotion for a specific item if exists"""
    promo = promotion.get_promotion_by_item(db, item_no=item_no)
    if promo is None:
        raise HTTPException(status_code=404, detail=f"No active promotion found for item {item_no}")
    return promo