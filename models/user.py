from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    mobile_number = Column(String(20), unique=True, index=True)
    age = Column(Integer, nullable=True)
    address = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=False)
    