from .LLMEnums import LLMEnums
from .LLMInterface import LLMInterface
from .providers.OpenAIProvider import OpenAIProvider
from .providers.GeminiProvider import GeminiProvider
from .providers.CoHereProvider import CoHereProvider


class LLMProviderFactory:

    def __init__(self,config:dict):
        self.config=config
    
    def create(self,provider:str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTER,
                default_generation_max_characters=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPREATURE
            )

        if provider == LLMEnums.GEMINI.value:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTER,
                default_generation_max_characters=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPREATURE
            )


        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTER,
                default_generation_max_characters=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPREATURE
            )




    @staticmethod
    def get_provider(provider_name:str):
        if provider_name==LLMEnums.OPENAI.value:
            return OpenAIProvider()
        if provider_name == LLMEnums.GEMINI.value:
            return GeminiProvider()
        if provider_name == LLMEnums.COHERE.value:
            return CoHereProvider()
        