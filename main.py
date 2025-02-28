from fastapi import FastAPI
from routers import auth, product
from database import Base, engine
import uvicorn
import models.user  # Import to ensure table is created
import models.product  # Import to ensure mapping is created
import models.cartsession    # Import to ensure table is created

Base.metadata.create_all(bind=engine)

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