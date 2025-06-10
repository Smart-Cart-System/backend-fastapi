from fastapi import Depends
from sqlalchemy.orm import Session
from models.logging import SecurityLog, SessionActivityLog, PerformanceLog, ErrorLog
from models.logging import LogLevel, SecurityEventType, SessionEventType
from database import get_db
import json
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

class LoggingService:
    def __init__(self, db: Session):
        self.db = db


    def log_security_event(
        self,
        event_type: SecurityEventType,
        ip_address: str,
        success: bool,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        log_entry = SecurityLog(
            event_type=event_type,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            additional_data=additional_data
        )
        self.db.add(log_entry)
        self.db.commit()

    def log_session_activity(
        self,
        event_type: SessionEventType,
        session_id: int,
        user_id: int,
        cart_id: Optional[int] = None,
        item_id: Optional[int] = None,
        barcode: Optional[int] = None,
        quantity: Optional[int] = None,
        weight: Optional[float] = None,
        total_price: Optional[float] = None,
        duration_seconds: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        log_entry = SessionActivityLog(
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            cart_id=cart_id,
            item_id=item_id,
            barcode=barcode,
            quantity=quantity,
            weight=weight,
            total_price=total_price,
            duration_seconds=duration_seconds,
            additional_data=additional_data
        )
        self.db.add(log_entry)
        self.db.commit()

    def log_performance(
        self,
        endpoint: str,
        method: str,
        response_time_ms: int,
        status_code: int,
        user_id: Optional[int] = None,
        request_size_bytes: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
        db_query_count: Optional[int] = None,
        db_query_time_ms: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        log_entry = PerformanceLog(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=status_code,
            user_id=user_id,
            request_size_bytes=request_size_bytes,
            response_size_bytes=response_size_bytes,
            db_query_count=db_query_count,
            db_query_time_ms=db_query_time_ms,
            additional_data=additional_data
        )
        self.db.add(log_entry)
        self.db.commit()

    def log_error(
        self,
        error_type: str,
        error_message: str,
        severity: str = "MEDIUM",
        endpoint: Optional[str] = None,
        user_id: Optional[int] = None,
        session_id: Optional[int] = None,
        request_data: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        if stack_trace is None:
            stack_trace = traceback.format_exc()
            
        log_entry = ErrorLog(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            endpoint=endpoint,
            user_id=user_id,
            session_id=session_id,
            request_data=request_data,
            severity=severity,
            additional_data=additional_data
        )
        self.db.add(log_entry)
        self.db.commit()

def get_logging_service(db: Session = Depends(get_db)) -> LoggingService:
    return LoggingService(db)