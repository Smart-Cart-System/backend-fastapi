from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.cartsession import BarcodeRequest
from schemas.cartsession import CartItemCreate
from schemas.product import Product
from crud import product, cartsession

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/scan-barcode", response_model=Product)
def scan_barcode(barcode_request: BarcodeRequest, db: Session = Depends(get_db)):
    # Find product by barcode
    db_product = product.get_product_by_barcode(db, barcode_request.barcode)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Add item to cart session
    cart_item = CartItemCreate(
    cart_id=barcode_request.cart_id,
    user_id=barcode_request.user_id,
    item_id=db_product.item_no_,
    quantity=1
)
    cartsession.create_cart_item(db, cart_item)
    
    return db_product

@router.get("/cart/{cart_id}")
def get_cart_items(cart_id: str, db: Session = Depends(get_db)):
    return cartsession.get_cart_items(db, cart_id)