import asyncio
from typing import Dict, Any
from app.agents.competitor_research.interfaces import CompetitorResearchAgent

class CompetitorAgentWrapper:
    """Wrapper exposing standard agent runner interface."""
    def __init__(self):
        self.agent = CompetitorResearchAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.agent.service.run_research(context)
