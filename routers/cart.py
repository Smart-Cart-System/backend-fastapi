from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.cart import Cart, CartCreate
from schemas.customer_session import SessionCreate, Session, QRScanRequest
from crud import cart, customer_session

router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)

@router.post("/", response_model=Cart)
def create_cart(cart_data: CartCreate, db: Session = Depends(get_db)):
    """Create a new shopping cart"""
    return cart.create_cart(db=db, cart=cart_data)

@router.get("/", response_model=List[Cart])
def read_carts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all shopping carts"""
    carts = cart.get_carts(db, skip=skip, limit=limit)
    return carts

@router.get("/{cart_id}", response_model=Cart)
def read_cart(cart_id: int, db: Session = Depends(get_db)):
    """Get a specific cart by ID"""
    db_cart = cart.get_cart_by_id(db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return db_cart
