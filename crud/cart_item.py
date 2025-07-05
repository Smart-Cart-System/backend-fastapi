from sqlalchemy.orm import Session
from models.cart_item import CartItem
from models.customer_session import CustomerSession
from models.product import ProductionData
from typing import List, Tuple, Dict, Union, Any
from services.logging_service import LoggingService, SessionEventType, get_logging_service

def validate_session(db: Session, session_id: int):
    """Check if session exists and is active"""
    return db.query(CustomerSession).filter(
        CustomerSession.session_id == session_id,
        CustomerSession.is_active == True
    ).first()

def add_cart_item(db: Session, session_id: int, barcode: int, weight: float = None):
    """Add item to cart or increment quantity"""
    logging_service = get_logging_service(db)
    
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_ADD,
            session_id=session_id,
            user_id=0,  # Unknown user
            barcode=barcode,
            additional_data={"error": "Invalid or inactive session"}
        )
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_ADD,
            session_id=session_id,
            user_id=session.user_id,
            barcode=barcode,
            additional_data={"error": "Product not found"}
        )
        return None, "Product not found"
    
    # Check if item already exists in cart
    cart_item = db.query(CartItem).filter(
        CartItem.session_id == session_id, 
        CartItem.item_id == product.item_no_
    ).first()
    
    if cart_item:
        # Increment quantity
        old_quantity = cart_item.quantity
        cart_item.quantity += 1
        
        # Update weight if provided
        if weight is not None:
            cart_item.saved_weight = weight
            
        db.commit()
        db.refresh(cart_item)
        
        # Log item addition
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_ADD,
            session_id=session_id,
            user_id=session.user_id,
            cart_id=session.cart_id,
            item_id=product.item_no_,
            barcode=barcode,
            quantity=cart_item.quantity,
            weight=weight,
            additional_data={
                "action": "quantity_increment",
                "old_quantity": old_quantity,
                "new_quantity": cart_item.quantity,
                "product_name": product.description
            }
        )
    else:
        # Add new item
        cart_item = CartItem(
            session_id=session_id,
            item_id=product.item_no_,
            quantity=1,
            saved_weight=weight
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        
        # Log new item addition
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_ADD,
            session_id=session_id,
            user_id=session.user_id,
            cart_id=session.cart_id,
            item_id=product.item_no_,
            barcode=barcode,
            quantity=1,
            weight=weight,
            additional_data={
                "action": "new_item_added",
                "product_name": product.description,
                "unit_price": float(product.unit_price)
            }
        )
    
    return cart_item, None

def remove_cart_item(db: Session, session_id: int, barcode: int):
    """Remove item from cart or decrement quantity"""
    logging_service = get_logging_service(db)
    
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_REMOVE,
            session_id=session_id,
            user_id=0,
            barcode=barcode,
            additional_data={"error": "Invalid or inactive session"}
        )
        return None, "Invalid or inactive session"
    
    # Find product
    product = db.query(ProductionData).filter(ProductionData.barcode == barcode).first()
    if not product:
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_REMOVE,
            session_id=session_id,
            user_id=session.user_id,
            barcode=barcode,
            additional_data={"error": "Product not found"}
        )
        return None, "Product not found"
    
    # Find cart item
    cart_item = db.query(CartItem).filter(
        CartItem.session_id == session_id, 
        CartItem.item_id == product.item_no_
    ).first()
    
    if not cart_item:
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_REMOVE,
            session_id=session_id,
            user_id=session.user_id,
            barcode=barcode,
            additional_data={"error": "Item not in cart"}
        )
        return None, "Item not in cart"
    
    old_quantity = cart_item.quantity
    
    if cart_item.quantity > 1:
        # Decrement quantity
        cart_item.quantity -= 1
        db.commit()
        db.refresh(cart_item)
        
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_REMOVE,
            session_id=session_id,
            user_id=session.user_id,
            cart_id=session.cart_id,
            item_id=product.item_no_,
            barcode=barcode,
            quantity=cart_item.quantity,
            additional_data={
                "action": "quantity_decrement",
                "old_quantity": old_quantity,
                "new_quantity": cart_item.quantity,
                "product_name": product.description
            }
        )
        return cart_item, None
    else:
        # Remove item completely
        db.delete(cart_item)
        db.commit()
        
        logging_service.log_session_activity(
            event_type=SessionEventType.ITEM_REMOVE,
            session_id=session_id,
            user_id=session.user_id,
            cart_id=session.cart_id,
            item_id=product.item_no_,
            barcode=barcode,
            quantity=0,
            additional_data={
                "action": "item_removed_completely",
                "old_quantity": old_quantity,
                "product_name": product.description
            }
        )
        return None, None

def get_cart_items_by_session(db: Session, session_id: int) -> Tuple[List[CartItem], float]:
    """Get all items in a session with total price calculation"""
    # Validate session
    session = validate_session(db, session_id)
    if not session:
        return [], 0
    
    # Get all items with eager loading of products
    items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()
    
    # Calculate total
    total_price = 0
    for item in items:
        if hasattr(item, 'product') and item.product:
            total_price += item.product.unit_price * item.quantity
    
    return items, total_price

def get_sessions_summary(db: Session, session_id: int) -> Tuple[List[CartItem], float]:
    """Get all items in a session with total price calculation"""
    session = db.query(CustomerSession).filter(
        CustomerSession.session_id == session_id).first()
    if not session:
        return [], 0
    # Get all items with eager loading of products
    items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()
    # Calculate total
    total_price = 0
    for item in items:
        if hasattr(item, 'product') and item.product:
            total_price += item.product.unit_price * item.quantity
    
    return items, total_price

def get_cart_items_for_recipe(db: Session, session_id: int) -> Tuple[List[CartItem], float]:
    """
    Get all items in a session for recipe generation regardless of session status.
    This allows recipe generation for completed (inactive) sessions.
    """
    # Check if session exists (without checking is_active)
    session = db.query(CustomerSession).filter(
        CustomerSession.session_id == session_id
    ).first()
    
    if not session:
        return [], 0
    
    # Get all items with eager loading of products
    items = db.query(CartItem).filter(
        CartItem.session_id == session_id
    ).all()
    
    # Calculate total
    total_price = 0
    for item in items:
        if hasattr(item, 'product') and item.product:
            total_price += item.product.unit_price * item.quantity
    
    return items, total_price