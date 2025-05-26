from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.security import get_current_user, verify_pi_api_key
from database import get_db
from models.user import User
from schemas.item_read import ItemReadRequest, ItemReadResponse
from crud import item_read
from services.websocket_service import notify_clients
router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("/read", response_model=ItemReadResponse)
async def read_item(request: ItemReadRequest, db: Session = Depends(get_db),pi_authenticated: bool = Depends(verify_pi_api_key)):
    """Record an item being read by the scanner"""
    product, error = item_read.read_item(db, request.sessionID, request.barcode)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    await notify_clients(request.sessionID, "item-read", request.barcode)
    return product

@router.get("/read/{barcode}", response_model=ItemReadResponse)
async def get_item(barcode: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """Get product details by barcode"""
    product = item_read.get_product_by_barcode(db, barcode)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product