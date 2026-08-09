import time
import httpx
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from app.core.config import settings

class OpenAIProvider(BaseLLMProvider):
    """Real OpenAI LLM Provider."""
    def __init__(self, model_name: str = "gpt-4o"):
        super().__init__(model_name)
        self.api_key = settings.OPENAI_API_KEY

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        if not self.api_key:
            return LLMResponse(
                provider="OpenAI",
                model=self.model_name,
                status="UNAVAILABLE",
                error_code="NOT_CONFIGURED",
                error_message="OPENAI_API_KEY not configured in environment",
                retryable=False,
                latency_seconds=round(time.time() - start_time, 2)
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.model_name,
                        "messages": [
                            *([{"role": "system", "content": request.system_prompt}] if request.system_prompt else []),
                            {"role": "user", "content": request.prompt}
                        ],
                        "temperature": request.temperature,
                        "max_tokens": request.max_tokens,
                        **({"response_format": {"type": "json_object"}} if request.json_mode else {})
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
                    total_tokens = usage.get("total_tokens", 0)
                    cost = (prompt_tokens * 0.000005) + (completion_tokens * 0.000015)

                    return LLMResponse(
                        content=content,
                        provider="OpenAI",
                        model=self.model_name,
                        status="SUCCESS",
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost_usd=round(cost, 6),
                        latency_seconds=round(time.time() - start_time, 2)
                    )
                else:
                    return LLMResponse(
                        provider="OpenAI",
                        model=self.model_name,
                        status="UNAVAILABLE",
                        error_code=f"HTTP_{resp.status_code}",
                        error_message=resp.text,
                        retryable=True,
                        latency_seconds=round(time.time() - start_time, 2)
                    )
        except Exception as e:
            return LLMResponse(
                provider="OpenAI",
                model=self.model_name,
                status="UNAVAILABLE",
                error_code="EXECUTION_ERROR",
                error_message=str(e),
                retryable=True,
                latency_seconds=round(time.time() - start_time, 2)
            )
