import time
import httpx
from typing import Dict, Any
from app.tools.base_tool import BaseTool

class BrowserTool(BaseTool):
    """Headless browser / HTTP rendering verification tool."""
    def __init__(self):
        super().__init__("browser", "Headless browser / HTTP rendering verification tool.")

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        url = params.get("url", "https://example.com")

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url)
                return {
                    "tool": "browser",
                    "status": "SUCCESS" if resp.status_code < 400 else "UNAVAILABLE",
                    "url": str(resp.url),
                    "status_code": resp.status_code,
                    "content_length": len(resp.content),
                    "headers": dict(resp.headers),
                    "latency_ms": int((time.time() - start_time) * 1000)
                }
        except Exception as e:
            return {
                "tool": "browser",
                "status": "UNAVAILABLE",
                "error_code": "CONNECTION_FAILED",
                "error_message": str(e),
                "url": url,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
