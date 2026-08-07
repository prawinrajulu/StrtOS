import asyncio
from typing import Dict, Any
from app.agents.ceo.interfaces import SpecialistAgentInterface, register_specialist_agent
from app.agents.competitor_research.service import CompetitorResearchService
from app.agents.competitor_research.schemas import CompetitorResearchInput
from app.agents.ceo.graph.state import CEOTaskItem
from app.core.logging import logger

class CompetitorResearchAgent(SpecialistAgentInterface):
    """
    Competitor Research Agent Wrapper implementing SpecialistAgentInterface.
    Executed strictly as a delegated specialist node under the CEO Agent Orchestrator.
    """
    def __init__(self):
        super().__init__(agent_name="Competitor Research Agent", domain="COMPETITOR_RESEARCH")
        self.service = CompetitorResearchService()

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Competitor Research Agent executing delegated task: {task.title}")

        payload = CompetitorResearchInput(
            business_name=context.get("client_name", "Arcadia Ventures"),
            industry=context.get("industry", "D2C SKINCARE / FinTech"),
            location=context.get("location", "Global / Remote"),
            website=context.get("website_url"),
            business_analysis_result=context.get("business_analysis_result", {}),
            seo_audit_result=context.get("seo_audit_result", {})
        )

        result = await self.service.run_research(payload)

        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": result.status,
            "findings": result.recommendations,
            "metrics": {
                "direct_competitors_count": len(result.direct_competitors),
                "indirect_competitors_count": len(result.indirect_competitors),
                "confidence": result.confidence_score
            },
            "confidence": result.confidence_score,
            "market_position": result.market_position_summary,
            "full_result": result.model_dump()
        }

# Automatically register in CEO Specialist Interfaces registry
register_specialist_agent(CompetitorResearchAgent())
