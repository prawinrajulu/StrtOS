import asyncio
from typing import Dict, Any
from app.agents.ceo.interfaces import SpecialistAgentInterface, register_specialist_agent
from app.agents.marketing_strategy.service import MarketingStrategyService
from app.agents.marketing_strategy.schemas import MarketingStrategyInput
from app.agents.ceo.graph.state import CEOTaskItem
from app.core.logging import logger

class MarketingStrategyAgent(SpecialistAgentInterface):
    """
    Marketing Strategy Agent Wrapper implementing SpecialistAgentInterface.
    Executed strictly as a delegated specialist node under the CEO Agent Orchestrator.
    """
    def __init__(self):
        super().__init__(agent_name="Marketing Strategy Agent", domain="MARKETING_STRATEGY")
        self.service = MarketingStrategyService()

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Marketing Strategy Agent executing delegated task: {task.title}")

        payload = MarketingStrategyInput(
            business_analysis_result=context.get("business_analysis_result", {"status": "COMPLETED"}),
            seo_audit_result=context.get("seo_audit_result", {"status": "COMPLETED"}),
            competitor_research_result=context.get("competitor_research_result", {"status": "COMPLETED"}),
            business_goal=context.get("directive", "Acquire high-intent customers"),
            budget=context.get("budget", "$10,000 / mo"),
            target_audience=context.get("target_audience", "General Audience"),
            priority=task.priority
        )

        result = await self.service.create_strategy(payload)

        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": result.status,
            "findings": result.recommendations,
            "metrics": {
                "roi_projection": result.roi_projection,
                "timeline_days": result.implementation_timeline_days,
                "confidence": result.confidence_score
            },
            "confidence": result.confidence_score,
            "brand_positioning": result.brand_positioning,
            "full_result": result.model_dump()
        }

# Automatically register in CEO Specialist Interfaces registry
register_specialist_agent(MarketingStrategyAgent())
