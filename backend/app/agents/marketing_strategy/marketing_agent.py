import asyncio
from typing import Dict, Any
from app.agents.marketing_strategy.interfaces import MarketingStrategyAgent

class MarketingAgentWrapper:
    """Wrapper exposing standard agent runner interface."""
    def __init__(self):
        self.agent = MarketingStrategyAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.agent.service.create_strategy(context)
