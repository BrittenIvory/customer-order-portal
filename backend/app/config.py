from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://portal:portal@db:5432/customer_portal"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    MYOB_BASE_URL: str = ""
    MYOB_API_KEY: str = ""
    MYOB_API_ID: str = ""
    MYOB_USERNAME: str = ""
    MYOB_PASSWORD: str = ""
    MYOB_COMPANY: str = ""
    MYOB_BRANCH: str = ""

    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
