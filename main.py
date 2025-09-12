from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Local imports
from core.db_middleware import DBConnectionMiddleware
from database import Base, engine
from core.middleware import add_middlewares
from core.error_handling import (
    validation_exception_handler,
    response_validation_exception_handler,
    sqlalchemy_exception_handler,
    pydantic_validation_exception_handler,
    generic_exception_handler,
    not_found_exception_handler
)
from routers import (
    auth, 
    cart, 
    customer_session,
    item_read, 
    cart_item, 
    websocket,
    fraud_warnings,
    promotion,
    payment,
    user,
    checklist,
    sse,
    shared_checklist,
    ocr,
    aisle,
    session_location,
    aisle_layout,
    feedback,
    product,  # Add this import if not already there
    admin,
    recipe,
    health  # Add this import to existing routers import list
)
from middleware.logging_middleware import LoggingMiddleware

# Import models for table creation
import models.user
import models.cart
import models.customer_session
import models.product
import models.cart_item
import models.fruad_warnings
import models.item_read
import models.checklist

# Create database tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# Initialize FastAPI app
app = FastAPI(
    title="Smart Cart API",
    description="API for the smart shopping cart",
    version="1.0",
    servers=[{"url": "http://127.0.0.1:8000", "description": "Local development server"},
        {"url": "https://api.duckycart.me", "description": "Production server"}],
    openapi_tags=[
        {"name": "authentication", "description": "User authentication operations"},
        {"name": "customer_session", "description": "Customer session operations"},
        # ... other tags
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Add middlewares from the middleware module
app = add_middlewares(app)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(StarletteHTTPException, not_found_exception_handler)

# Add this after creating the FastAPI app and before other middleware
# In the add_middlewares function or directly in main.py if not using that function
app.add_middleware(DBConnectionMiddleware)

# Response Time Middleware
class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Convert to milliseconds and round to 2 decimal places
        process_time_ms = round(process_time * 1000, 2)
        
        # Add timing to response headers
        response.headers["X-Process-Time"] = f"{process_time_ms} ms"
        
        # If response is JSON, modify the response body and create new response
        if response.headers.get("content-type") == "application/json":
            try:
                # Get the original response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Parse JSON body
                import json
                data = json.loads(body)
                
                # Add timing info
                if isinstance(data, dict):
                    data["response_time_ms"] = process_time_ms
                
                # Create new JSON string and encode it
                new_body = json.dumps(data).encode()
                
                # Create new response WITHOUT copying the Content-Length header
                headers = dict(response.headers)
                if "content-length" in headers:
                    del headers["content-length"]  # Remove Content-Length header
                
                return Response(
                    content=new_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type="application/json"
                )
            except Exception as e:
                # If any error occurs during processing, return the original response
                print(f"Error in ResponseTimeMiddleware: {e}")
                return response
                
        return response

# Add this after defining ResponseTimeMiddleware
app.add_middleware(ResponseTimeMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(customer_session.router)
app.include_router(cart.router)
app.include_router(cart_item.router)
app.include_router(item_read.router)
app.include_router(websocket.router)
app.include_router(fraud_warnings.router)
app.include_router(promotion.router)
app.include_router(payment.router)
app.include_router(user.router)
app.include_router(checklist.router)
app.include_router(sse.router)
app.include_router(shared_checklist.router)
app.include_router(ocr.router)
app.include_router(aisle.router)
app.include_router(session_location.router)
app.include_router(aisle_layout.router)
app.include_router(feedback.router)
app.include_router(product.router)  # Include the product router here
app.include_router(admin.router)
app.include_router(recipe.router)
app.include_router(health.router)  # Add this with your other router includes

# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "Welcome to Smart Cart API"}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)