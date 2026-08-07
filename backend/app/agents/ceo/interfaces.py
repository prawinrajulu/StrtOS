import asyncio
from typing import Dict, Any, List
from app.agents.ceo.graph.state import CEOTaskItem, TaskStatus

class SpecialistAgentInterface:
    """
    Interface Contract for Specialist AI Agents.
    CEO Agent delegates execution ONLY through this interface.
    No domain logic implemented.
    """
    def __init__(self, agent_name: str, domain: str):
        self.agent_name = agent_name
        self.domain = domain

    async def execute_task(self, task: CEOTaskItem, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1.5)  # Simulate execution latency
        return {
            "agent_name": self.agent_name,
            "domain": self.domain,
            "title": task.title,
            "status": "COMPLETED",
            "findings": [
                f"Completed {self.domain} analysis for {context.get('client_name', 'Client')}.",
                f"Generated strategic recommendations under {self.agent_name} scope."
            ],
            "metrics": {"health_score": 95, "confidence": 0.96},
            "confidence": 96.0
        }

SPECIALIST_INTERFACES: Dict[str, SpecialistAgentInterface] = {}

def register_specialist_agent(agent: SpecialistAgentInterface):
    SPECIALIST_INTERFACES[agent.agent_name] = agent

# Initial Default Interfaces Stubs
SPECIALIST_INTERFACES.update({
    "Competitor Research Agent": SpecialistAgentInterface("Competitor Research Agent", "COMPETITOR_RESEARCH"),
    "SEO Audit Agent": SpecialistAgentInterface("SEO Audit Agent", "SEO_AUDIT"),
    "Marketing Strategy Agent": SpecialistAgentInterface("Marketing Strategy Agent", "MARKETING_STRATEGY"),
    "Campaign Planner Agent": SpecialistAgentInterface("Campaign Planner Agent", "CAMPAIGN_PLANNING"),
    "Analytics Agent": SpecialistAgentInterface("Analytics Agent", "ANALYTICS"),
    "Client Onboarding Agent": SpecialistAgentInterface("Client Onboarding Agent", "ONBOARDING"),
    "Content Strategy Agent": SpecialistAgentInterface("Content Strategy Agent", "CONTENT_STRATEGY"),
    "Opportunity Intelligence Agent": SpecialistAgentInterface("Opportunity Intelligence Agent", "OPPORTUNITY_INTELLIGENCE"),
    "Report Generator Agent": SpecialistAgentInterface("Report Generator Agent", "REPORT_GENERATION")
})
