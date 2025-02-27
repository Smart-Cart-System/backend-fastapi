from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "mysql+pymysql://root:WQbqmFXVxqKbSyygcmLdVLNpgumpVNWx@metro.proxy.rlwy.net:29557/railway"
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()