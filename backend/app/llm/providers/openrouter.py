import time
import os
import asyncio
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider."""
    def __init__(self, model_name: str = "openrouter/auto"):
        super().__init__(model_name)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.3)
        return LLMResponse(
            content="{}",
            provider="OpenRouter",
            model=self.model_name,
            prompt_tokens=450,
            completion_tokens=360,
            total_tokens=810,
            estimated_cost_usd=0.0015,
            latency_seconds=round(time.time() - start_time, 2)
        )
