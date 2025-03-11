from sqlalchemy.orm import Session
from models.fruad_warnings import FraudWarning, WarningType
from schemas.fraud_warnings import FraudWarningCreate

def create_warning(db: Session, warning: FraudWarningCreate):
    # Convert string enum value to Python enum object
    if warning.type_of_warning == "weight increased":
        enum_value = WarningType.WEIGHT_INCREASED
    else:
        enum_value = WarningType.WEIGHT_DECREASED
        
    db_warning = FraudWarning(
        session_id=warning.session_id,
        type_of_warning=enum_value  # Use the enum object
    )
    db.add(db_warning)
    db.commit()
    db.refresh(db_warning)
    return db_warning

def get_warnings_by_session(db: Session, session_id: int):
    return db.query(FraudWarning).filter(FraudWarning.session_id == session_id).all()