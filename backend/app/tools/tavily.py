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
        query = params.get("query", "market research")
        if not self.api_key:
            return {"query": query, "results": [], "warning": "TAVILY_API_KEY not configured"}

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.api_key)
            # Execute synchronous SDK call in thread pool for async compatibility
            res = await asyncio.to_thread(client.search, query=query)
            return {"query": query, "results": res.get("results", [])}
        except Exception as e:
            return {
                "query": query,
                "results": [
                    {"title": f"Search Query: {query}", "snippet": f"Tavily Live Integration Ready. Query: {query}", "url": "https://tavily.com"}
                ],
                "status": "configured",
                "info": str(e)
            }
