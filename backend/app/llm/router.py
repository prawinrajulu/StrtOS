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
        primary_provider_key = self.routing_matrix.get(agent_name, "gemini")
        provider = self.providers.get(primary_provider_key, self.providers["gemini"])

        try:
            logger.info(f"Routing {agent_name} request to primary provider: {primary_provider_key.upper()}")
            return await provider.generate(request)
        except Exception as e:
            logger.error(f"Primary provider {primary_provider_key} failed: {str(e)}. Falling back to Gemini...")
            fallback_provider = self.providers["gemini"]
            return await fallback_provider.generate(request)

llm_router = LLMRouter()
