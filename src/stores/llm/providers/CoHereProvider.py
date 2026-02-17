from ..LLMInterface import LLMInterface
import logging
from ..LLMEnums import CohereEnums,DocumentTypeEnum

import cohere

class CoHereProvider(LLMInterface):
    def __init__(self,api_key:str,
                default_input_max_characters:int=1000,
                default_generation_max_characters:int=1000,
                default_temperature:float=0.1,
                ):

        # attributes of the provider        
        self.api_key = api_key

        # cohere client
        self.client = cohere.ClientV2(api_key=api_key)

        # default values for generation
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_characters = default_generation_max_characters
        self.default_temperature = default_temperature

        # Name of model 
        self.generation_model_id = None
        
        # embedding model
        self.embedding_model_id = None
        self.embedding_size=None

        # logger
        self.logger = logging.getLogger(__name__)
    

    def set_generation_model(self,model_id:str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self,embedding_model_id:str,embedding_size:int):
        self.embedding_model_id = embedding_model_id
        self.embedding_size = embedding_size
    
    def generate_text(self,prompt:str,chat_history:list=[],max_output_tokens:int=None,temperature:float=None):
        if not self.client:
            self.logger.error("Cohere client is not initialized")
            raise Exception("Cohere client is not initialized")
        
        if not self.generation_model_id:
            self.logger.error("Generation model is not set")
            raise Exception("Generation model is not set")
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_characters
        temperature = temperature if temperature else self.default_temperature
        
        chat_history.append(
            self.construct_prompt(prompt=prompt,role=CohereEnums.USER.value)
        )

        # call the cohere api
    
        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message = self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        if not response or not response.text:
            self.logger.error("No response from Cohere")
            return None

        return response.text
    
    def embed_text(self,document_type:str,document_content:str=None):
        if not self.client:
            self.logger.error("Cohere client is not initialized")
            raise Exception("Cohere client is not initialized")
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set")
            raise Exception("Embedding model is not set")

        
        input_type = CohereEnums.DOCUMENT.value 
        if document_type==DocumentTypeEnum.QUERY.value:
            input_type = CohereEnums.QUERY.value



        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(document_content)],
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or response.embeddings.float:
            self.logger.error("No response from Cohere")
            return None
        return response.embeddings.float[0]
        

    def construct_prompt(self,prompt:str,role:str):
        return {
            "role":role,
            "content":self.process_text(prompt)
        }
   
    def process_text(self,text:str):
        return text.strip()[:self.default_input_max_characters]

