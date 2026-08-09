import time
import httpx
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from app.core.config import settings

class GeminiProvider(BaseLLMProvider):
    """Real Google Gemini LLM Provider."""
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        super().__init__(model_name)
        self.api_key = settings.GEMINI_API_KEY

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        if not self.api_key:
            return LLMResponse(
                provider="Gemini",
                model=self.model_name,
                status="UNAVAILABLE",
                error_code="NOT_CONFIGURED",
                error_message="GEMINI_API_KEY not configured in environment",
                retryable=False,
                latency_seconds=round(time.time() - start_time, 2)
            )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            prompt_text = request.prompt
            if request.system_prompt:
                prompt_text = f"System: {request.system_prompt}\nUser: {request.prompt}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt_text}]}],
                        "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_tokens}
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    usage = data.get("usageMetadata", {})
                    prompt_tokens = usage.get("promptTokenCount", 0)
                    completion_tokens = usage.get("candidatesTokenCount", 0)
                    total_tokens = usage.get("totalTokenCount", 0)
                    cost = (prompt_tokens * 0.00000125) + (completion_tokens * 0.00000375)

                    return LLMResponse(
                        content=content,
                        provider="Gemini",
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
                        provider="Gemini",
                        model=self.model_name,
                        status="UNAVAILABLE",
                        error_code=f"HTTP_{resp.status_code}",
                        error_message=resp.text,
                        retryable=True,
                        latency_seconds=round(time.time() - start_time, 2)
                    )
        except Exception as e:
            return LLMResponse(
                provider="Gemini",
                model=self.model_name,
                status="UNAVAILABLE",
                error_code="EXECUTION_ERROR",
                error_message=str(e),
                retryable=True,
                latency_seconds=round(time.time() - start_time, 2)
            )
