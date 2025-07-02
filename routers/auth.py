from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from core.security import create_frontend_token, verify_password, check_admin_permissions, get_current_user
from models.user import User
from crud import user as user_crud
from schemas.user import UserOut, UserCreate, UserBase, PasswordUpdateForm, UserUpdate
from services.logging_service import LoggingService, SecurityEventType, get_logging_service
from core.config import settings
from typing import Optional

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/signup", response_model=UserOut)
def signup(
    user: UserCreate, 
    admin_secret: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    logging_service: LoggingService = Depends(get_logging_service)
):
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        # Log failed signup - username already exists
        logging_service.log_security_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            username=user.username,
            ip_address="unknown",
            success=False,
            failure_reason="Username already registered"
        )
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return user_crud.create_user(db=db, user=user, admin_secret=admin_secret)


@router.post("/login")
def login(request: Request, 
          form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),
          logging_service: LoggingService = Depends(get_logging_service)):
    
    # Get client info
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    
    # Authenticate user
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login
        user_id = user.id if user else None
        logging_service.log_security_event(
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id=user_id,
            username=form_data.username,
            ip_address=client_ip,
            user_agent=user_agent,
            success=False,
            failure_reason="Incorrect username or password"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_frontend_token(
        data={"sub": user.username}
    )
    
    # Log successful login
    logging_service.log_security_event(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        user_id=user.id,
        username=form_data.username,
        ip_address=client_ip,
        user_agent=user_agent,
        success=True,
        additional_data={
            "login_method": "password",
            "token_created": True,
            "user_email": user.email
        }
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
        "is_admin": user.is_admin,
        "sql_string": settings.SQLALCHEMY_DATABASE_URL if user.is_admin else None
    }

@router.put("/update-data", response_model=UserOut)
def update_user_data(
    user: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_user = user_crud.get_user_by_username(db, username=current_user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = user_crud.update_user(db=db, user_id=db_user.id, user_data=user)
    
    
    return updated_user

@router.put("/update-password")
def update_password(
    request: Request,
    form_data: PasswordUpdateForm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    user_crud.update_user_password(db=db, user_id=user.id, new_password=form_data.new_password)
    
    return {"detail": "Password updated successfully"}

