from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from core.security import create_frontend_token, verify_password
from crud import user as user_crud
import crud, models, schemas
from schemas.user import User, UserCreate
from typing import Optional

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/signup", response_model=User)
def signup(
    user: UserCreate, 
    admin_secret: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    db_user = crud.user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user (admin_secret will be validated inside create_user)
    return crud.user.create_user(db=db, user=user, admin_secret=admin_secret)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_frontend_token(
        data={"sub": user.username}
    )
    
    return {
        "username": user.username,
        "email": user.email,
        "phone_number": user.mobile_number,
        "full_name": user.full_name,
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "expires_in": timedelta(hours=6).total_seconds(),
        "address": user.address,
        "is_admin": user.is_admin
    }
