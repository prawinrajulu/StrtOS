import time
import httpx
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.core.config import settings

class SerperTool(BaseTool):
    """Serper.dev API for Google SERP competitor search results."""
    def __init__(self):
        super().__init__("serper", "Queries Google SERP search results for domain indexing and rank tracking.")
        self.api_key = settings.SERPER_API_KEY

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        query = params.get("query", "competitors")

        if not self.api_key:
            return {
                "tool": "serper",
                "status": "UNAVAILABLE",
                "error_code": "NOT_CONFIGURED",
                "error_message": "SERPER_API_KEY not configured",
                "query": query,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                    json={"q": query}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "tool": "serper",
                        "status": "SUCCESS",
                        "query": query,
                        "organic_results": data.get("organic", []),
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
                else:
                    return {
                        "tool": "serper",
                        "status": "UNAVAILABLE",
                        "error_code": f"HTTP_{resp.status_code}",
                        "error_message": resp.text,
                        "query": query,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
        except Exception as e:
            return {
                "tool": "serper",
                "status": "UNAVAILABLE",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e),
                "query": query,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
