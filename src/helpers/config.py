from pydantic_settings import BaseSettings
from typing import List
class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    GEMINI_API_KEY: str

    # FILE CONFIGURAION
    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # postgress Configuration
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    # LLM CONFIGURATION
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    GEMINI_API_KEY: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID_LITERAL: List[str] = None
    GENERATION_MODEL_ID: str = None
    EMBEDIDING_MODEL_ID: str = None
    EMBEDIDING_MODEL_SIZE: int = None

    INPUT_DEFAULT_MAX_CHARACTER: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPREATURE: float = None

    # ========== VectorDB config ============
    VECTOR_DB_BACKEND_LITERAL: List[str] = None
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD : str = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD : int = 100

    # ========== Template config ============
    PRIMARY_LANG : str = None
    DEFAULT_LANG : str = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def get_settings() -> Settings:
    return Settings()
    