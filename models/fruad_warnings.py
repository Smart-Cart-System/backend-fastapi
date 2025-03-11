from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class WarningType(enum.Enum):
    WEIGHT_INCREASED = "weight increased"
    WEIGHT_DECREASED = "weight decreased"

class FraudWarning(Base):
    __tablename__ = "fraud_warnings"
    
    id = Column(Integer, primary_key=True, index=True)
    type_of_warning = Column(Enum(WarningType), nullable=False)
    session_id = Column(Integer, ForeignKey("customer_session.session_id"))