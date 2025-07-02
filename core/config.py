from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_TOKEN_EXPIRE_HOURS: int = 6
    
    # QR Code Settings
    QR_EXPIRATION_MINUTES: int = 1
    
    # Pi Authentication
    PI_API_KEY: str = "PI_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION"
    
    XPAY_API_KEY: Optional[str] = None

    # Google Cloud settings
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Admin configuration
    ADMIN_SECRET_KEY: Optional[str] = None
    
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None  

    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    EMAIL_ADDRESS: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None



    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()