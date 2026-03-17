from langchain_community.chat_models import ChatTongyi, ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from src.config.llm_config import LLMConfig, LLMVendor

class ModelFactory:
    @staticmethod
    def create(config: LLMConfig) -> BaseChatModel:
        """
        Create a Chat Model instance based on configuration
        """
        if config.vendor == LLMVendor.ALIYUN:
            if not config.api_key:
                print("Warning: Aliyun API Key is missing.")
            return ChatTongyi(
                model=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature
            )
        elif config.vendor == LLMVendor.OPENAI:
            if not config.api_key:
                print("Warning: OpenAI API Key is missing.")
            return ChatOpenAI(
                model=config.model_name,
                api_key=config.api_key,
                base_url=config.base_url if config.base_url else None,
                temperature=config.temperature
            )
        else:
            raise ValueError(f"Unsupported LLM Vendor: {config.vendor}")
