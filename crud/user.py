from sqlalchemy.orm import Session
from models.user import User  # Import the class, not the module
from schemas.user import UserCreate
from core.security import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()  # Use the User class

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()  # Use the User class
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        mobile=user.mobile,  # Add this line
        age=user.age        # Add this line
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user