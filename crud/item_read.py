from sqlalchemy.orm import Session
from models.item_read import ItemRead
from models.cart_item import CartItem
from models.customer_session import CustomerSession
from models.product import ProductionData

def validate_session(db: Session, session_id: int):
    """Check if session exists and is active"""
    return db.query(CustomerSession).filter(
        CustomerSession.session_id == session_id,
        CustomerSession.is_active == True
    ).first()

def read_item(db: Session, session_id: int, barcode: int):
    """Record an item read event"""
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        return None, "Product not found"
    
    # Record read event
    item_read = ItemRead(
        session_id=session_id,
        item_no_=product.item_no_
    )
    db.add(item_read)
    db.commit()
    db.refresh(item_read)
    
    return product, None  # Return product and no error
    
def get_product_by_barcode(db: Session, barcode: int):
    """Get product details by barcode"""
    return db.query(ProductionData).filter(ProductionData.barcode == barcode).first()