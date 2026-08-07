import asyncio
from typing import Dict, Any
from app.agents.seo_audit.interfaces import SEOAuditAgent

class SEOAgentWrapper:
    """Wrapper exposing standard agent runner interface."""
    def __init__(self):
        self.agent = SEOAuditAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.agent.service.run_audit(context)
