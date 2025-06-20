from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from core.config import settings
from services.logging_service import LoggingService, SecurityEventType, get_logging_service

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Frontend Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Pi Authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_frontend_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.FRONTEND_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def check_admin_permissions(user: User):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
# Frontend user authentication
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logging_service = get_logging_service(db)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Log invalid token payload
            logging_service.log_security_event(
                event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
                ip_address="unknown",
                success=False,
                failure_reason="Invalid token payload - no username",
                additional_data={"token_validation": "failed", "reason": "missing_username"}
            )
            raise credentials_exception
    except JWTError as e:
        # Log JWT decode error
        logging_service.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
            ip_address="unknown",
            success=False,
            failure_reason=f"JWT decode error: {str(e)}",
            additional_data={"token_validation": "failed", "error": str(e)}
        )
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        # Log user not found during token validation
        logging_service.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
            username=username,
            ip_address="unknown",
            success=False,
            failure_reason="User not found during token validation",
            additional_data={"token_validation": "failed", "username": username}
        )
        raise credentials_exception
    
    # Log successful token validation
    logging_service.log_security_event(
        event_type=SecurityEventType.TOKEN_REFRESH,
        user_id=user.id,
        username=username,
        ip_address="unknown",
        success=True,
        additional_data={"token_validation": "success"}
    )
    
    return user

# Raspberry Pi authentication
def verify_pi_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    logging_service = get_logging_service(db)
    
    if api_key is None:
        # Log missing API key
        logging_service.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
            ip_address="unknown",
            success=False,
            failure_reason="API Key header missing",
            additional_data={"source": "raspberry_pi", "error": "missing_api_key"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header missing",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    if api_key != settings.PI_API_KEY:
        # Log invalid API key
        logging_service.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
            ip_address="unknown",
            success=False,
            failure_reason="Invalid API Key",
            additional_data={
                "source": "raspberry_pi", 
                "provided_key": api_key[:10] + "..." if len(api_key) > 10 else api_key,
                "expected_key_prefix": settings.PI_API_KEY[:10] + "..."
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    # Log successful PI authentication
    logging_service.log_security_event(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        username="raspberry_pi",
        ip_address="unknown",
        success=True,
        additional_data={"source": "raspberry_pi", "api_key_validation": "success"}
    )
    
    return True

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to verify the current user has admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires admin privileges"
        )
    return current_user