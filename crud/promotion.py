from sqlalchemy.orm import Session, joinedload
import datetime
from models.promotion import PromotionData
from models.product import ProductionData
from models.session_location import SessionLocation  # Add this import
from schemas.promotion import PromotionResponse  # Import the schema

def get_active_promotions(db: Session, skip: int = 0, limit: int = 100):
    """Get all active promotions where current date is between start and end date"""
    today = datetime.date.today()
    
    # Query promotions joining with products
    promotions = db.query(PromotionData, ProductionData)\
        .join(ProductionData, PromotionData.item_no_ == ProductionData.item_no_)\
        .options(joinedload(PromotionData.aisle))\
        .filter(
            PromotionData.promotion_starting_date <= today,
            PromotionData.promotion_ending_date >= today
        )\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    result = []
    for promo, product in promotions:
        # Calculate discounted price and discount percentage
        discounted_price = product.unit_price - promo.discount_amount
        discount_percentage = (promo.discount_amount / product.unit_price) * 100 if product.unit_price > 0 else 0
        
        # Create PromotionResponse with aisle information
        promotion_response = PromotionResponse(
            index=promo.index,
            item_no_=promo.item_no_,
            aisle_id=promo.aisle_id,
            aisle_name=promo.aisle.name if promo.aisle else None,
            promotion_description=promo.promotion_description,
            discount_amount=promo.discount_amount,
            promotion_starting_date=promo.promotion_starting_date,
            promotion_ending_date=promo.promotion_ending_date,
            product_description=product.description,
            product_description_ar=product.description_ar,
            unit_price=product.unit_price,
            discounted_price=discounted_price,
            discount_percentage=round(discount_percentage, 2),
            image_url=product.image_url
        )
        result.append(promotion_response)
    
    return result

def get_promotion_by_item(db: Session, item_no: int):
    """Get active promotion for specific item"""
    today = datetime.date.today()
    
    # Query promotion for specific item
    result = db.query(PromotionData, ProductionData)\
        .join(ProductionData, PromotionData.item_no_ == ProductionData.item_no_)\
        .options(joinedload(PromotionData.aisle))\
        .filter(
            PromotionData.item_no_ == item_no,
            PromotionData.promotion_starting_date <= today,
            PromotionData.promotion_ending_date >= today
        )\
        .first()
    
    if not result:
        return None
        
    promo, product = result
    
    # Calculate discounted price and discount percentage
    discounted_price = product.unit_price - promo.discount_amount
    discount_percentage = (promo.discount_amount / product.unit_price) * 100 if product.unit_price > 0 else 0
    
    # Return a PromotionResponse instance with aisle information
    return PromotionResponse(
        index=promo.index,
        item_no_=promo.item_no_,
        aisle_id=promo.aisle_id,
        aisle_name=promo.aisle.name if promo.aisle else None,
        promotion_description=promo.promotion_description,
        discount_amount=promo.discount_amount,
        promotion_starting_date=promo.promotion_starting_date,
        promotion_ending_date=promo.promotion_ending_date,
        product_description=product.description,
        product_description_ar=product.description_ar,
        unit_price=product.unit_price,
        discounted_price=discounted_price,
        discount_percentage=round(discount_percentage, 2),
        image_url=product.image_url
    )

def get_aisle_promotions(db: Session, aisle_id: int, skip: int = 0, limit: int = 100):
    """Get active promotions for a specific aisle"""
    today = datetime.date.today()
    
    # Query promotions for specific aisle
    promotions = db.query(PromotionData, ProductionData)\
        .join(ProductionData, PromotionData.item_no_ == ProductionData.item_no_)\
        .filter(
            PromotionData.aisle_id == aisle_id,
            PromotionData.promotion_starting_date <= today,
            PromotionData.promotion_ending_date >= today
        )\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    result = []
    for promo, product in promotions:
        # Calculate discounted price and discount percentage
        discounted_price = product.unit_price - promo.discount_amount
        discount_percentage = (promo.discount_amount / product.unit_price) * 100 if product.unit_price > 0 else 0
        
        # Create PromotionResponse
        promotion_response = PromotionResponse(
            index=promo.index,
            item_no_=promo.item_no_,
            aisle_id=promo.aisle_id,
            aisle_name=promo.aisle.name if promo.aisle else None,
            promotion_description=promo.promotion_description,
            discount_amount=promo.discount_amount,
            promotion_starting_date=promo.promotion_starting_date,
            promotion_ending_date=promo.promotion_ending_date,
            product_description=product.description,
            product_description_ar=product.description_ar,
            unit_price=product.unit_price,
            discounted_price=discounted_price,
            discount_percentage=round(discount_percentage, 2),
            image_url=product.image_url
        )
        result.append(promotion_response)
    
    return result

def get_session_location_promotions(db: Session, session_id: int, skip: int = 0, limit: int = 100):
    """Get promotions for a session based on their latest location"""
    # Get latest location for this session
    latest_location = db.query(SessionLocation).filter(
        SessionLocation.session_id == session_id
    ).order_by(SessionLocation.created_at.desc()).first()
    
    if not latest_location:
        return []
    
    # Get promotions for this aisle
    return get_aisle_promotions(db, latest_location.aisle_id, skip, limit)