from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    GEMINI_API_KEY: str

    # FILE CONFIGURAION
    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()
    