from sqlalchemy.orm import Session
from models.product import ProductionData

def get_product_by_barcode(db: Session, barcode: str):
    return db.query(ProductionData).filter(ProductionData.barcode == barcode).first()