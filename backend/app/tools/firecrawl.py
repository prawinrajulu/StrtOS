import time
import httpx
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.core.config import settings

class FirecrawlTool(BaseTool):
    """Firecrawl API for real web scraping and content extraction."""
    def __init__(self):
        super().__init__("firecrawl", "Scrapes web pages and extracts content into Markdown.")
        self.api_key = settings.FIRECRAWL_API_KEY

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        url = params.get("url", "https://example.com")
        
        if not self.api_key:
            return {
                "tool": "firecrawl",
                "status": "UNAVAILABLE",
                "error_code": "NOT_CONFIGURED",
                "error_message": "FIRECRAWL_API_KEY not configured",
                "url": url,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"url": url, "formats": ["markdown"]}
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    return {
                        "tool": "firecrawl",
                        "status": "SUCCESS",
                        "url": url,
                        "markdown_content": data.get("markdown", ""),
                        "title": data.get("metadata", {}).get("title", ""),
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
                else:
                    return {
                        "tool": "firecrawl",
                        "status": "UNAVAILABLE",
                        "error_code": f"HTTP_{resp.status_code}",
                        "error_message": resp.text,
                        "url": url,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
        except Exception as e:
            return {
                "tool": "firecrawl",
                "status": "UNAVAILABLE",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e),
                "url": url,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
