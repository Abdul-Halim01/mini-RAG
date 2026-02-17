from google import genai
from google.genai import types
import logging
from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum

class GeminiProvider(LLMInterface):

    def __init__(self,
                 api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_characters: int = 1000,
                 default_temperature: float = 1.0):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_characters = default_generation_max_characters
        self.default_temperature = default_temperature

        # Set up the client
        self.client = genai.Client(api_key=api_key)

        # Models
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.logger = logging.getLogger(__name__)

    # =====================
    # Model Setters
    # =====================

    def set_generation_model(self, model_id: str):
        """
        Example: "gemini-2.5-flash" or "gemini-3.0"
        """
        self.generation_model_id = model_id

    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size

    # =====================
    # Text Generation
    # =====================

    def generate_text(self,
                      prompt: str,
                      chat_history: list = None,
                      max_output_tokens: int = None,
                      temperature: float = None):

        if not self.api_key:
            raise Exception("Gemini API key is not configured")

        if not self.generation_model_id:
            raise Exception("Generation model is not set")

        # Prepare parameters
        max_output_tokens = max_output_tokens or self.default_generation_max_characters
        temperature = temperature or self.default_temperature

        # Prepare conversation input
        contents = prompt.strip()
        if chat_history:
            # If history is provided, simply append the combined conversation
            for msg in chat_history:
                contents += f"\n{msg['role']}: {msg['content']}"

        try:
            response = self.client.models.generate_content(
                model=self.generation_model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            )

            # Extract and return text
            return response.text if hasattr(response, "text") else None

        except Exception as e:
            self.logger.error(f"Error generating text with Gemini: {e}")
            return None

    # =====================
    # Embedding
    # =====================

    def embed_text(self,
                   document_type: str,
                   document_content: str = None):

        if not self.embedding_model_id:
            raise Exception("Embedding model is not set")

        # Determine the task type based on input
        task_type = types.EmbedContentConfig.TaskType.RETRIEVAL_DOCUMENT
        if document_type == DocumentTypeEnum.QUERY.value:
            task_type = types.EmbedContentConfig.TaskType.RETRIEVAL_QUERY

        try:
            result = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=document_content.strip(),
                config=types.EmbedContentConfig(
                    task_type=task_type
                )
            )

            # Return numeric embedding array
            return result.embeddings

        except Exception as e:
            self.logger.error(f"Error embedding text: {e}")
            return None

    # =====================
    # Utilities
    # =====================

    def construct_prompt(self, prompt: str, role: str):
        # Simple utility to standardize history
        return {
            "role": role,
            "content": prompt.strip()
        }

    def process_text(self, text: str):
        # Truncate and clean input text
        return text.strip()[: self.default_input_max_characters]
