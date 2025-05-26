from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Local imports
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
    sse
)

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

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(StarletteHTTPException, not_found_exception_handler)

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

# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "Welcome to Smart Cart API"}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)