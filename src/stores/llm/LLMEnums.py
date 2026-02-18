from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    COHERE = "cohere"
    
class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"

    DOCUMENT= "search_document"
    QUERY= "search_query"

class GeminiEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "model"   # Gemini uses "model" for assistant

    DOCUMENT = "retrieval_document"
    QUERY = "retrieval_query"


class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"