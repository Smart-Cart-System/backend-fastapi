from sqlalchemy.orm import Session
from models.product import ProductionData
from sqlalchemy.sql.expression import func
from typing import List

def get_product_by_barcode(db: Session, barcode: int):
    # Convert string barcode to integer for comparison with BigInteger field
    try:
        barcode_int = int(barcode)
        return db.query(ProductionData).filter(ProductionData.barcode == barcode_int).first()
    except ValueError:
        return None

def get_random_product_suggestions(db: Session, user_id: int = None, limit: int = 10) -> List[ProductionData]:
    # Query random products with valid prices
    suggestions = db.query(ProductionData)\
        .filter(ProductionData.unit_price > 0)\
        .order_by(func.random())\
        .limit(limit)\
        .all()
    
    return suggestions