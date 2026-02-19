from google import genai
from google.genai import types
import logging
from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums, DocumentTypeEnum

class GeminiProvider(LLMInterface):
    def __init__(self,api_key:str,
                default_input_max_characters:int=1000,
                default_generation_max_characters:int=1000,
                default_temperature:float=0.1,
                ):

        # attributes of the provider        
        self.api_key = api_key

        # Gemini client
        self.client = genai.Client(api_key=api_key)

        # default values for generation
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_characters = default_generation_max_characters
        self.default_temperature = default_temperature

        # Name of model 
        self.generation_model_id = None
        
        # embedding model
        self.embedding_model_id = None
        self.embedding_size=None

        self.enums = GeminiEnums
        # logger
        self.logger = logging.getLogger(__name__)
    
    
    def set_generation_model(self,model_id:str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self,embedding_model_id:str,embedding_size:int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size
    

    def generate_text(self,prompt:str,chat_history:list=[],max_output_tokens:int=None,temperature:float=None):
        print("IN generate text GEMINI")
        if not self.client:
            self.logger.error("Gemini client is not initialized")
            raise Exception("Gemini client is not initialized")
        
        if not self.generation_model_id:
            self.logger.error("Generation model is not set")
            raise Exception("Generation model is not set")

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_characters
        temperature = temperature if temperature else self.default_temperature
        
        # Prepare system instruction
        system_instruction_text = None
        if chat_history and len(chat_history) > 0:
            system_msg = chat_history[0]
            # Handle different formats of system message
            if isinstance(system_msg, dict):
                if "content" in system_msg:
                    system_instruction_text = system_msg["content"]
                elif "parts" in system_msg and len(system_msg["parts"]) > 0:
                    system_instruction_text = system_msg["parts"][0].get("text")
            
            # Remove system prompt from history for 'contents' if it's there
            contents = chat_history[1:]
        else:
            contents = []

        # Ensure all items in contents have 'parts' instead of 'content'
        formatted_contents = []
        for msg in contents:
            if isinstance(msg, dict) and "content" in msg:
                formatted_contents.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })
            else:
                formatted_contents.append(msg)

        # Add current user prompt
        formatted_contents.append({
            "role": self.enums.USER.value,
            "parts": [{"text": self.process_text(prompt)}]
        })

        response = self.client.models.generate_content(
                model=self.generation_model_id,
                contents=formatted_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction_text,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            )

        if not response or not response.candidates or len(response.candidates)==0 or not response.candidates[0].content or not response.candidates[0].content.parts or len(response.candidates[0].content.parts)==0:
            self.logger.error("No response from Gemini")
            return None
        
        return response.candidates[0].content.parts[0].text

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

    def construct_prompt(self,prompt:str,role:str):
        # Gemini expects 'parts' instead of 'content'
        return {
            "role":role,
            "parts":[{"text": self.process_text(prompt)}]
        }
   
    def process_text(self,text:str):
        return text.strip()[:self.default_input_max_characters]


