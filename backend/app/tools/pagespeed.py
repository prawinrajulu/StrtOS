import time
import httpx
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.core.config import settings

class PageSpeedTool(BaseTool):
    """Google PageSpeed Insights API tool."""
    def __init__(self):
        super().__init__("pagespeed", "Evaluates PageSpeed Insights metrics and Core Web Vitals.")
        self.api_key = settings.GOOGLE_PAGESPEED_API_KEY

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        url = params.get("url", "https://example.com")

        if not self.api_key:
            return {
                "tool": "pagespeed",
                "status": "UNAVAILABLE",
                "error_code": "NOT_CONFIGURED",
                "error_message": "GOOGLE_PAGESPEED_API_KEY not configured",
                "url": url,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        try:
            req_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={self.api_key}"
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.get(req_url)
                if resp.status_code == 200:
                    data = resp.json()
                    lighthouse = data.get("lighthouseResult", {})
                    cats = lighthouse.get("categories", {})
                    perf_score = int((cats.get("performance", {}).get("score", 0)) * 100)
                    acc_score = int((cats.get("accessibility", {}).get("score", 0)) * 100)

                    audits = lighthouse.get("audits", {})
                    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
                    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")

                    return {
                        "tool": "pagespeed",
                        "status": "SUCCESS",
                        "url": url,
                        "performance_score": perf_score,
                        "accessibility_score": acc_score,
                        "lcp": lcp,
                        "cls": cls,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
                else:
                    return {
                        "tool": "pagespeed",
                        "status": "UNAVAILABLE",
                        "error_code": f"HTTP_{resp.status_code}",
                        "error_message": resp.text,
                        "url": url,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
        except Exception as e:
            return {
                "tool": "pagespeed",
                "status": "UNAVAILABLE",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e),
                "url": url,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
