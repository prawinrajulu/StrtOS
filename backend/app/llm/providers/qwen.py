import time
import os
import asyncio
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse

class QwenProvider(BaseLLMProvider):
    """Qwen Provider."""
    def __init__(self, model_name: str = "qwen-max"):
        super().__init__(model_name)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.3)
        return LLMResponse(
            content="{}",
            provider="Qwen",
            model=self.model_name,
            prompt_tokens=400,
            completion_tokens=320,
            total_tokens=720,
            estimated_cost_usd=0.0008,
            latency_seconds=round(time.time() - start_time, 2)
        )
