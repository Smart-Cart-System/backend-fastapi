from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Enum, BigInteger, DECIMAL
from sqlalchemy.sql import func
from database import Base
import enum

class LogLevel(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SecurityEventType(enum.Enum):
    USER_CREATE = "USER_CREATE"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ADMIN_LOGIN = "ADMIN_LOGIN"
    ADMIN_CREATE_USER = "ADMIN_CREATE_USER"
    ADMIN_LOGIN_FAILED = "ADMIN_LOGIN_FAILED"
    QR_SCAN_OK = "QR_SCAN_OK"


class SessionEventType(enum.Enum):
    SESSION_START = "SESSION_START"
    SESSION_END = "SESSION_END"
    ITEM_READ = "ITEM_READ"
    ITEM_ADD = "ITEM_ADD"
    ITEM_REMOVE = "ITEM_REMOVE"
    QR_SCAN = "QR_SCAN"

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    event_type = Column(Enum(SecurityEventType), nullable=False)
    user_id = Column(Integer, nullable=True)
    username = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    additional_data = Column(JSON, nullable=True)

class SessionActivityLog(Base):
    __tablename__ = "session_activity_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    event_type = Column(Enum(SessionEventType), nullable=False)
    session_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    cart_id = Column(Integer, nullable=True)
    item_id = Column(Integer, nullable=True)
    barcode = Column(BigInteger, nullable=True)
    quantity = Column(Integer, nullable=True)
    weight = Column(DECIMAL(10, 3), nullable=True)
    total_price = Column(DECIMAL(10, 2), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    additional_data = Column(JSON, nullable=True)

class PerformanceLog(Base):
    __tablename__ = "performance_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    db_query_count = Column(Integer, nullable=True)
    db_query_time_ms = Column(Integer, nullable=True)
    additional_data = Column(JSON, nullable=True)

class ErrorLog(Base):
    __tablename__ = "error_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    error_type = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(Integer, nullable=True)
    request_data = Column(JSON, nullable=True)
    severity = Column(Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), nullable=False)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    additional_data = Column(JSON, nullable=True)