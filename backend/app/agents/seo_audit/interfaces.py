import asyncio
from typing import Dict, Any
from app.agents.ceo.interfaces import SpecialistAgentInterface, register_specialist_agent
from app.agents.seo_audit.service import SEOAuditService
from app.agents.seo_audit.schemas import SEOAuditInput
from app.agents.ceo.graph.state import CEOTaskItem
from app.core.logging import logger

class SEOAuditAgent(SpecialistAgentInterface):
    """
    SEO Audit Agent Wrapper implementing SpecialistAgentInterface.
    Executed strictly as a specialist node delegated by the CEO Agent Orchestrator.
    """
    def __init__(self):
        super().__init__(agent_name="SEO Audit Agent", domain="SEO_AUDIT")
        self.service = SEOAuditService()

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"SEO Audit Agent executing delegated task: {task.title}")
        
        website_url = context.get("website_url") or "https://orbitalabs.io"

        payload = SEOAuditInput(
            website_url=website_url,
            business_context=context.get("client_name", "Arcadia Ventures"),
            industry=context.get("industry", "FinTech / D2C"),
            target_audience=context.get("target_audience", "General Consumers"),
            business_analysis_result=context.get("business_analysis_result", {})
        )

        result = await self.service.run_audit(payload)

        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": result.status,
            "findings": result.recommendations,
            "metrics": {
                "overall_seo_score": result.overall_seo_score,
                "technical_seo_score": result.technical_seo_score,
                "performance_score": result.performance_score,
                "lcp": result.core_web_vitals.lcp,
                "confidence": result.confidence_score
            },
            "confidence": result.confidence_score,
            "full_result": result.model_dump()
        }

# Automatically register in CEO Specialist Interfaces registry
register_specialist_agent(SEOAuditAgent())
