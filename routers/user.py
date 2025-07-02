from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.customer_session import RecentSessionsResponse
from schemas.cart_item import CartItemResponse, CartItemListResponse
from crud.user import get_user_sessions_with_cart_details
from crud.cart_item import get_cart_items_by_session
from core.security import get_current_user, verify_pi_api_key
from models.user import User
from fastapi.responses import StreamingResponse
from services.email_service import send_cart_receipt_email
from crud.customer_session import get_session
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

@router.post("/send-receipt")
async def send_cart_receipt(
    session_id: int,
    recipient_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send cart receipt via email"""
    session = get_session(db, session_id)
    print(f"Session: {session.session_id}, Current User: {current_user.id}")
    # Get cart items
    items, total = get_cart_items_by_session(db, session.session_id)
    
    if not items:
        raise HTTPException(status_code=404, detail="No items found in cart")
    
    # Build response object
    item_responses = []
    for item in items:
        product_info = item.product
        item_responses.append(CartItemResponse(
            session_id=item.session_id,
            item_id=item.item_id,
            quantity=item.quantity,
            saved_weight=item.saved_weight,
            product={
                "item_no_": product_info.item_no_,
                "description": product_info.description,
                "description_ar": product_info.description_ar,
                "unit_price": product_info.unit_price,
                "product_size": product_info.product_size,
                "barcode": product_info.barcode,
                "image_url": product_info.image_url
            } if product_info else None
        ))
    
    cart_data = CartItemListResponse(
        items=item_responses,
        total_price=total,
        item_count=len(items)
    )
    
    # Send email
    success = send_cart_receipt_email(
        recipient_email=recipient_email,
        cart_data=cart_data,
        user_name=current_user.full_name
    )
    
    if success:
        return {"message": "Receipt sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send receipt")