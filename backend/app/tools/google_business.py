import time
import httpx
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.core.config import settings

class GoogleBusinessTool(BaseTool):
    """Google Maps / Places Business API tool."""
    def __init__(self):
        super().__init__("google_business", "Fetches Google Maps location listings and customer review metrics.")
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        name = params.get("name", "Business")

        if not self.api_key:
            return {
                "tool": "google_business",
                "status": "UNAVAILABLE",
                "error_code": "NOT_CONFIGURED",
                "error_message": "GOOGLE_MAPS_API_KEY not configured",
                "name": name,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        try:
            req_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={name}&inputtype=textquery&fields=name,rating,user_ratings_total,formatted_address&key={self.api_key}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(req_url)
                if resp.status_code == 200:
                    candidates = resp.json().get("candidates", [])
                    if candidates:
                        c = candidates[0]
                        return {
                            "tool": "google_business",
                            "status": "SUCCESS",
                            "name": c.get("name", name),
                            "address": c.get("formatted_address", ""),
                            "rating": c.get("rating", 0.0),
                            "review_count": c.get("user_ratings_total", 0),
                            "latency_ms": int((time.time() - start_time) * 1000)
                        }
                    else:
                        return {
                            "tool": "google_business",
                            "status": "UNAVAILABLE",
                            "error_code": "NOT_FOUND",
                            "error_message": f"No Google Maps business listing found for '{name}'",
                            "name": name,
                            "latency_ms": int((time.time() - start_time) * 1000)
                        }
                else:
                    return {
                        "tool": "google_business",
                        "status": "UNAVAILABLE",
                        "error_code": f"HTTP_{resp.status_code}",
                        "error_message": resp.text,
                        "name": name,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
        except Exception as e:
            return {
                "tool": "google_business",
                "status": "UNAVAILABLE",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e),
                "name": name,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
