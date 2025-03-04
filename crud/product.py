from sqlalchemy.orm import Session
from models.product import ProductionData

def get_product_by_barcode(db: Session, barcode: int):
    # Convert string barcode to integer for comparison with BigInteger field
    try:
        barcode_int = int(barcode)
        return db.query(ProductionData).filter(ProductionData.barcode == barcode_int).first()
    except ValueError:
        return None