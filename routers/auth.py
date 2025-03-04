from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud.user
import crud, models, schemas
from core.security import create_access_token, verify_password
from database import get_db
from schemas.user import User, UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/signup", response_model=User)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.user.create_user(db=db, user=user)

@router.post("/login")
def login(form_data: schemas.user.UserCreate, db: Session = Depends(get_db)):
    user = crud.user.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}