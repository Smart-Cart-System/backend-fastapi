from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from core.config import settings

# For debugging - print the connection string
print(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Enable connection testing
    pool_recycle=3600,   # Recycle connections after 1 hour
    poolclass=QueuePool,
    pool_size=10,        # Adjust based on your needs
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()