from fastapi import FastAPI
from routers import auth, product
from database import Base, engine
import uvicorn
# Import ALL models before creating tables
import models.user
import models.cartsession
import models.product

# Print a debug message
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

app = FastAPI()

# Include the authentication router
app.include_router(auth.router)
# Include the product router
app.include_router(product.router)

@app.get("/")
def read_root():
    return {"Hello": "Welcome to Smart Cart API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)