from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routers import auth, cart, customer_session,item_read, cart_item, websocket,fraud_warnings,promotion
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from core.error_handling import (
    validation_exception_handler,
    response_validation_exception_handler,
    sqlalchemy_exception_handler,
    pydantic_validation_exception_handler,
    generic_exception_handler,
    not_found_exception_handler
)

import uvicorn
import models.user
import models.cart
import models.customer_session
import models.product
import models.cart_item


print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

app = FastAPI(
    title="Smart Cart API",
    description="API for the smart shopping cart",
    version="1.0",
    servers=[{"url": "https://api.duckycart.me", "description": "Production server"}],
)
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class EnforceSubdomainMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        allowed_host = "api.duckycart.me"
        if request.url.hostname != allowed_host:
            raise HTTPException(status_code=403, detail="Forbidden: Use api.duckycart.me")
        return await call_next(request)

app.add_middleware(EnforceSubdomainMiddleware)


origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://64.226.127.205",
    "https://api.duckycart.me",
    "https://aastsmartcart.vercel.app",

]

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(StarletteHTTPException, not_found_exception_handler)

app.include_router(auth.router)

app.include_router(customer_session.router)
app.include_router(cart.router)
app.include_router(cart_item.router)
app.include_router(item_read.router)
app.include_router(websocket.router)
app.include_router(fraud_warnings.router)
app.include_router(promotion.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "Welcome to Smart Cart API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)