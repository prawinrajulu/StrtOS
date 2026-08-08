import json
from typing import Dict, Any, Optional
from app.tools.base_tool import BaseTool
from app.tools.firecrawl import FirecrawlTool
from app.tools.tavily import TavilyTool
from app.tools.serper import SerperTool
from app.tools.pagespeed import PageSpeedTool
from app.tools.google_business import GoogleBusinessTool
from app.tools.browser import BrowserTool
from app.core.logging import logger

class ToolRegistry:
    """
    Centralized Tool Registry with Built-in Result Caching.
    Prevents duplicate API calls across agent executions.
    """
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            "firecrawl": FirecrawlTool(),
            "tavily": TavilyTool(),
            "serper": SerperTool(),
            "pagespeed": PageSpeedTool(),
            "google_business": GoogleBusinessTool(),
            "browser": BrowserTool()
        }
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized ToolRegistry with 6 registered tools & result caching.")

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = f"{tool_name}:{json.dumps(params, sort_keys=True)}"
        if cache_key in self.cache:
            logger.info(f"Cache HIT for tool '{tool_name}' with key: {cache_key}")
            return self.cache[cache_key]

        tool = self.tools.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' is not registered in ToolRegistry.")

        logger.info(f"Executing tool '{tool_name}'...")
        result = await tool.execute(params)
        self.cache[cache_key] = result
        return result

tool_registry = ToolRegistry()
