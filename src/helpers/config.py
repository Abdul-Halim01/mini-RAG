from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    GEMINI_API_KEY: str

    # FILE CONFIGURAION
    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # mongodb configuration
    MONGODB_URL: str
    MONGODB_DATABASE: str
    # MONGODB_COLLECTION: str

    # LLM CONFIGURATION
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    GEMINI_API_KEY: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDIDING_MODEL_ID: str = None
    EMBEDIDING_MODEL_SIZE: int = None

    INPUT_DEFAULT_MAX_CHARACTER: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPREATURE: float = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()
    