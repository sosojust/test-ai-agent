import os
from enum import Enum
from pydantic import BaseModel, Field

class LLMVendor(str, Enum):
    ALIYUN = "aliyun"
    OPENAI = "openai"
    # Add more vendors as needed

class LLMConfig(BaseModel):
    vendor: LLMVendor = Field(default=LLMVendor.ALIYUN, description="LLM vendor")
    model_name: str = Field(default="qwen-max", description="Model name")
    api_key: str = Field(default="", description="API Key")
    base_url: str = Field(default="", description="Base URL for API")
    temperature: float = Field(default=0.7, description="Temperature")

    @staticmethod
    def from_env(prefix: str = "DEFAULT_LLM") -> "LLMConfig":
        """
        Load config from environment variables with a specific prefix.
        Example: DEFAULT_LLM_VENDOR, SUPERVISOR_LLM_MODEL
        """
        vendor_str = os.getenv(f"{prefix}_VENDOR", "aliyun").lower()
        try:
            vendor = LLMVendor(vendor_str)
        except ValueError:
            vendor = LLMVendor.ALIYUN
            
        return LLMConfig(
            vendor=vendor,
            model_name=os.getenv(f"{prefix}_MODEL", "qwen-max"),
            api_key=os.getenv(f"{prefix}_API_KEY", os.getenv("DASHSCOPE_API_KEY", "")),
            base_url=os.getenv(f"{prefix}_BASE_URL", ""),
            temperature=float(os.getenv(f"{prefix}_TEMPERATURE", "0.7"))
        )

# Define configurations for different agents
class AgentLLMConfigs:
    @property
    def supervisor(self) -> LLMConfig:
        return LLMConfig.from_env("SUPERVISOR_LLM")

    @property
    def insurance_consultant(self) -> LLMConfig:
        return LLMConfig.from_env("INSURANCE_LLM")

    @property
    def doc_processor(self) -> LLMConfig:
        return LLMConfig.from_env("DOC_LLM")

agent_llm_configs = AgentLLMConfigs()
