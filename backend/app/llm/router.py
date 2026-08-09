from typing import Dict, Any, Optional
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from app.llm.providers.gemini import GeminiProvider
from app.llm.providers.claude import ClaudeProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.qwen import QwenProvider
from app.llm.providers.openrouter import OpenRouterProvider
from app.core.logging import logger

class LLMRouter:
    """
    Dynamic AI Model Router.
    Routes specialist agent tasks to specific optimized LLMs with automatic fallback mechanisms.
    """
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "gemini": GeminiProvider(),
            "claude": ClaudeProvider(),
            "openai": OpenAIProvider(),
            "deepseek": DeepSeekProvider(),
            "qwen": QwenProvider(),
            "openrouter": OpenRouterProvider()
        }

        # Agent-to-Model Routing Rules Matrix
        self.routing_matrix: Dict[str, str] = {
            "Business Analysis Agent": "gemini",
            "SEO Audit Agent": "deepseek",
            "Competitor Research Agent": "gemini",
            "Marketing Strategy Agent": "claude",
            "Campaign Planner Agent": "openai"
        }
        logger.info("Initialized LLMRouter with 6 providers.")

    async def route_and_generate(self, agent_name: str, request: LLMRequest) -> LLMResponse:
        primary_key = self.routing_matrix.get(agent_name, "gemini")
        fallback_keys = ["gemini", "openai", "claude", "deepseek", "qwen", "openrouter"]
        ordered_keys = [primary_key] + [k for k in fallback_keys if k != primary_key]

        for provider_key in ordered_keys:
            provider = self.providers.get(provider_key)
            if not provider:
                continue

            logger.info(f"Attempting LLM generation for {agent_name} using provider: {provider_key.upper()}")
            resp = await provider.generate(request)
            if resp.status == "SUCCESS":
                return resp
            else:
                logger.warning(f"Provider {provider_key.upper()} failed for {agent_name}: {resp.error_message}. Trying fallback...")

        logger.error(f"All LLM providers failed for {agent_name}.")
        return LLMResponse(
            provider="LLMRouter",
            model="none",
            status="UNAVAILABLE",
            error_code="ALL_PROVIDERS_UNAVAILABLE",
            error_message=f"No configured LLM provider available for {agent_name}.",
            retryable=True
        )

llm_router = LLMRouter()
