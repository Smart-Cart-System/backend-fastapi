from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.cart_item import CartItemRequest, CartItemResponse, CartItemListResponse, RemoveResponse
from crud import item_read, cart_item
from typing import List, Dict
from routers.websocket import notify_clients

router = APIRouter(
    prefix="/cart-items",
    tags=["cart items"]
)

@router.post("/add", response_model=CartItemResponse)
async def add_item_to_cart(request: CartItemRequest, db: Session = Depends(get_db)):
    """Add item to cart or increment quantity"""
    # Update to pass weight parameter
    cart_item_obj, error = cart_item.add_cart_item(
        db, 
        request.sessionID, 
        request.barcode, 
        request.weight
    )
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Get product details for response
    product_info = db.query(cart_item.ProductionData).filter(
        cart_item.ProductionData.item_no_ == cart_item_obj.item_id
    ).first()
    
    # Build response with both cart item and product data
    response = CartItemResponse(
        session_id=cart_item_obj.session_id, 
        item_id=cart_item_obj.item_id,
        quantity=cart_item_obj.quantity,
        saved_weight=cart_item_obj.saved_weight,
        product={
            "item_no_": product_info.item_no_,
            "description": product_info.description,
            "description_ar": product_info.description_ar,
            "unit_price": product_info.unit_price,
            "product_size": product_info.product_size,
            "barcode": product_info.barcode
        } if product_info else None
    )
    await notify_clients(request.sessionID, "cart-updated", request.barcode)
    return response

@router.delete("/remove", response_model=RemoveResponse)
async def remove_item_from_cart(request: CartItemRequest, db: Session = Depends(get_db)):
    """Remove item from cart or decrement quantity"""
    result, error = cart_item.remove_cart_item(db, request.sessionID, request.barcode)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    if isinstance(result, dict) and "removed" in result:
        await notify_clients(request.sessionID, "cart-updated", request.barcode)
        return RemoveResponse(
            success=True,
            message="Item removed from cart",
            item=None
        )
    else:
        product_info = db.query(cart_item.ProductionData).filter(
            cart_item.ProductionData.item_no_ == result.item_id
        ).first()
        await notify_clients(request.sessionID, "cart-updated", request.barcode)
        return RemoveResponse(
            success=True,
            message="Item quantity reduced",
            item=CartItemResponse(
                session_id=result.session_id, 
                item_id=result.item_id,
                quantity=result.quantity,
                saved_weight=result.saved_weight,
                product={
                    "item_no_": product_info.item_no_,
                    "description": product_info.description,
                    "description_ar": product_info.description_ar,
                    "unit_price": product_info.unit_price,
                    "product_size": product_info.product_size,
                    "barcode": product_info.barcode
                } if product_info else None
            )
        )

@router.get("/session/{session_id}", response_model=CartItemListResponse)
def get_cart_items_by_session(session_id: int, db: Session = Depends(get_db)):
    """Get all items in a user's cart session"""
    items, total = cart_item.get_cart_items_by_session(db, session_id)
    
    if not items:
        raise HTTPException(status_code=404, detail="No items found in cart")
    
    item_responses = []
    for item in items:
        product_info = item.product  # Using the relationship
        
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
                "barcode": product_info.barcode
            } if product_info else None
        ))
    
    return CartItemListResponse(
        items=item_responses,
        total_price=total,
        item_count=len(items)
    )