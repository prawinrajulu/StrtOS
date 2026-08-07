import asyncio
from typing import Dict, Any
from app.agents.ceo.interfaces import SpecialistAgentInterface, register_specialist_agent
from app.agents.business_analysis.service import BusinessAnalysisService
from app.agents.business_analysis.schemas import BusinessAnalysisInput
from app.agents.ceo.graph.state import CEOTaskItem
from app.core.logging import logger

class BusinessAnalysisAgent(SpecialistAgentInterface):
    """
    Business Analysis Agent Wrapper implementing the SpecialistAgentInterface contract.
    Executed strictly as a specialist node delegated by the CEO Agent Orchestrator.
    """
    def __init__(self):
        super().__init__(agent_name="Business Analysis Agent", domain="BUSINESS_ANALYSIS")
        self.service = BusinessAnalysisService()

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Business Analysis Agent executing delegated task: {task.title}")
        
        payload = BusinessAnalysisInput(
            business_name=context.get("client_name", "Arcadia Ventures"),
            industry=context.get("industry", "D2C SKINCARE"),
            description=task.title,
            target_audience=context.get("target_audience", "General Consumers"),
            business_goal=context.get("directive", "Expand Market Share")
        )

        result = await self.service.run_analysis(payload)
        
        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": result.status,
            "findings": result.recommendations,
            "metrics": {
                "digital_maturity": result.digital_maturity_score,
                "business_maturity": result.business_maturity_score,
                "confidence": result.confidence_score
            },
            "confidence": result.confidence_score,
            "swot": result.swot.model_dump(),
            "customer_personas": [p.model_dump() for p in result.customer_personas],
            "full_result": result.model_dump()
        }

# Automatically register in CEO Specialist Interfaces registry
register_specialist_agent(BusinessAnalysisAgent())
