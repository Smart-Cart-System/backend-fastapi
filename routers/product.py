from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.product import ProductBase, SuggestedProductsResponse
from crud import product
from typing import List
from models.user import User
from core.security import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/suggestions/{user_id}", response_model=SuggestedProductsResponse)
def get_product_suggestions(
    user_id: int,
    count: int = Query(default=8, ge=3, le=10, description="Number of products to suggest (3-10)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get random product suggestions for a user.
    
    The authenticated user can only access their own suggestions.
    Admin users can access suggestions for any user.
    """
    # Verify that the user is requesting their own suggestions or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: You can only access your own product suggestions"
        )
    
    # Get random products
    suggested_products = product.get_random_product_suggestions(db, user_id=user_id, limit=count)
    
    # Return response
    return SuggestedProductsResponse(
        products=suggested_products,
        count=len(suggested_products)
    )