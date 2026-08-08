import time
import os
import asyncio
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4o Provider."""
    def __init__(self, model_name: str = "gpt-4o"):
        super().__init__(model_name)
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        await asyncio.sleep(0.35)
        
        return LLMResponse(
            content="{}",
            provider="OpenAI",
            model=self.model_name,
            prompt_tokens=480,
            completion_tokens=390,
            total_tokens=870,
            estimated_cost_usd=0.0028,
            latency_seconds=round(time.time() - start_time, 2)
        )
