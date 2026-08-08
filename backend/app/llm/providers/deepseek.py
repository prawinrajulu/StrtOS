import time
import os
import asyncio
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek Provider."""
    def __init__(self, model_name: str = "deepseek-coder"):
        super().__init__(model_name)
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.3)
        
        return LLMResponse(
            content="{}",
            provider="DeepSeek",
            model=self.model_name,
            prompt_tokens=390,
            completion_tokens=310,
            total_tokens=700,
            estimated_cost_usd=0.0007,
            latency_seconds=round(time.time() - start_time, 2)
        )
