import asyncio
from typing import Dict, Any
from app.agents.business_analysis.interfaces import BusinessAnalysisAgent

class BusinessAgentWrapper:
    """Wrapper exposing standard agent runner interface."""
    def __init__(self):
        self.agent = BusinessAnalysisAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.agent.service.run_analysis(context)
