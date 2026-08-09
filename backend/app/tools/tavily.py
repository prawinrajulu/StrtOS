import time
import asyncio
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.core.config import settings

class TavilyTool(BaseTool):
    """Tavily Search API for real-time Web Search & AI research."""
    def __init__(self):
        super().__init__("tavily", "Executes real-time web search for market research and competitor insights.")
        self.api_key = settings.TAVILY_API_KEY

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        query = params.get("query", "market research")
        if not self.api_key:
            return {
                "tool": "tavily",
                "status": "UNAVAILABLE",
                "error_code": "NOT_CONFIGURED",
                "error_message": "TAVILY_API_KEY not configured",
                "query": query,
                "results": [],
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.api_key)
            res = await asyncio.to_thread(client.search, query=query)
            return {
                "tool": "tavily",
                "status": "SUCCESS",
                "query": query,
                "results": res.get("results", []),
                "latency_ms": int((time.time() - start_time) * 1000)
            }
        except Exception as e:
            return {
                "tool": "tavily",
                "status": "UNAVAILABLE",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e),
                "query": query,
                "results": [],
                "latency_ms": int((time.time() - start_time) * 1000)
            }
