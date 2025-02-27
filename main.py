from fastapi import FastAPI
from routers import auth
from database import Base, engine
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the authentication router
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"Hello aboda"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)