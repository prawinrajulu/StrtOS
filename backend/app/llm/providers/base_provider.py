from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    json_mode: bool = True

class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_seconds: float = 0.0

class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass
