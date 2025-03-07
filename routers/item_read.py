from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.item_read import ItemReadRequest, ItemReadResponse
from crud import item_read

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("/read", response_model=ItemReadResponse)
def read_item(request: ItemReadRequest, db: Session = Depends(get_db)):
    """Record an item being read by the scanner"""
    product, error = item_read.read_item(db, request.sessionID, request.barcode)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return product