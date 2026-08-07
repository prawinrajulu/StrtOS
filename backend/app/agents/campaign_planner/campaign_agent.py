import asyncio
from typing import Dict, Any
from app.agents.campaign_planner.interfaces import CampaignPlannerAgent

class CampaignAgentWrapper:
    """Wrapper exposing standard agent runner interface."""
    def __init__(self):
        self.agent = CampaignPlannerAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.agent.service.build_plan(context)
