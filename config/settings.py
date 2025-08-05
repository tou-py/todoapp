from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    PORT: int = 8000
    ECHO_SQL: bool = False
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # 30 minutos en default
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 días en default

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()