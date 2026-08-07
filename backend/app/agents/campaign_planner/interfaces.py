import asyncio
from typing import Dict, Any
from app.agents.ceo.interfaces import SpecialistAgentInterface, register_specialist_agent
from app.agents.campaign_planner.service import CampaignPlannerService
from app.agents.campaign_planner.schemas import CampaignPlanningInput
from app.agents.ceo.graph.state import CEOTaskItem
from app.core.logging import logger

class CampaignPlannerAgent(SpecialistAgentInterface):
    """
    Campaign Planner Agent Wrapper implementing SpecialistAgentInterface.
    Executed strictly as a delegated specialist node under the CEO Agent Orchestrator.
    """
    def __init__(self):
        super().__init__(agent_name="Campaign Planner Agent", domain="CAMPAIGN_PLANNING")
        self.service = CampaignPlannerService()

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Campaign Planner Agent executing delegated task: {task.title}")

        payload = CampaignPlanningInput(
            marketing_strategy_result=context.get("marketing_strategy_result", {"status": "COMPLETED"}),
            business_analysis_result=context.get("business_analysis_result", {"status": "COMPLETED"}),
            seo_audit_result=context.get("seo_audit_result", {"status": "COMPLETED"}),
            competitor_research_result=context.get("competitor_research_result", {"status": "COMPLETED"}),
            business_goal=context.get("directive", "Acquire high-intent customers"),
            budget=context.get("budget", "$10,000 / mo"),
            timeline=context.get("timeline", "90 Days")
        )

        result = await self.service.build_plan(payload)

        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": result.status,
            "findings": result.launch_checklist,
            "metrics": {
                "creatives_count": len(result.creative_requirements),
                "timeline": result.campaign_timeline,
                "confidence": result.confidence_score
            },
            "confidence": result.confidence_score,
            "expected_outcome": result.expected_outcome,
            "full_result": result.model_dump()
        }

# Automatically register in CEO Specialist Interfaces registry
register_specialist_agent(CampaignPlannerAgent())
