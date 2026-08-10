from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.learning.models import (
    AgentPerformanceModel, ToolReliabilityModel, LLMProviderPerformanceModel,
    AgentPolicyModel, AgentAdaptationModel, PolicyStatus, ReliabilityClass
)

FIVE_SPECIALIST_AGENTS = [
    "Business Analysis Agent",
    "SEO Audit Agent",
    "Competitor Research Agent",
    "Marketing Strategy Agent",
    "Campaign Planner Agent"
]

class LearningRepository:
    """Async Repository managing database persistence for Learning & Self-Optimization with multi-tenant isolation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_agent_performance(self, agent_name: str, org_id: str) -> AgentPerformanceModel:
        stmt = select(AgentPerformanceModel).where(
            AgentPerformanceModel.agent_name == agent_name,
            AgentPerformanceModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        perf = res.scalars().first()

        if not perf:
            perf = AgentPerformanceModel(
                organization_id=org_id,
                agent_name=agent_name,
                agent_version="1.0.0",
                reliability_class=ReliabilityClass.INSUFFICIENT_DATA
            )
            self.session.add(perf)
            await self.session.flush()

        return perf

    async def list_agent_performances(self, org_id: str) -> List[AgentPerformanceModel]:
        # Ensure all 5 core specialist agents exist for org
        for ag_name in FIVE_SPECIALIST_AGENTS:
            await self.get_or_create_agent_performance(ag_name, org_id)

        stmt = select(AgentPerformanceModel).where(AgentPerformanceModel.organization_id == org_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_or_create_tool_reliability(self, tool_name: str, org_id: str) -> ToolReliabilityModel:
        stmt = select(ToolReliabilityModel).where(
            ToolReliabilityModel.tool_name == tool_name,
            ToolReliabilityModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        tr = res.scalars().first()

        if not tr:
            tr = ToolReliabilityModel(organization_id=org_id, tool_name=tool_name)
            self.session.add(tr)
            await self.session.flush()

        return tr

    async def list_tool_reliabilities(self, org_id: str) -> List[ToolReliabilityModel]:
        tools = ["firecrawl", "tavily", "serper", "pagespeed", "google_business", "browser"]
        for t in tools:
            await self.get_or_create_tool_reliability(t, org_id)

        stmt = select(ToolReliabilityModel).where(ToolReliabilityModel.organization_id == org_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_or_create_provider_performance(self, provider: str, model: str, org_id: str) -> LLMProviderPerformanceModel:
        stmt = select(LLMProviderPerformanceModel).where(
            LLMProviderPerformanceModel.provider == provider,
            LLMProviderPerformanceModel.model == model,
            LLMProviderPerformanceModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        p = res.scalars().first()

        if not p:
            p = LLMProviderPerformanceModel(organization_id=org_id, provider=provider, model=model)
            self.session.add(p)
            await self.session.flush()

        return p

    async def list_provider_performances(self, org_id: str) -> List[LLMProviderPerformanceModel]:
        providers = [
            ("gemini", "gemini-1.5-pro"),
            ("openai", "gpt-4o"),
            ("claude", "claude-3-5-sonnet"),
            ("deepseek", "deepseek-chat")
        ]
        for prov, mod in providers:
            await self.get_or_create_provider_performance(prov, mod, org_id)

        stmt = select(LLMProviderPerformanceModel).where(LLMProviderPerformanceModel.organization_id == org_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_agent_policy(self, policy: AgentPolicyModel) -> AgentPolicyModel:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def get_active_policy(self, agent_name: str, org_id: str) -> Optional[AgentPolicyModel]:
        stmt = select(AgentPolicyModel).where(
            AgentPolicyModel.agent_name == agent_name,
            AgentPolicyModel.organization_id == org_id,
            AgentPolicyModel.status == PolicyStatus.ACTIVE
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_policies_by_agent(self, agent_name: str, org_id: str) -> List[AgentPolicyModel]:
        stmt = select(AgentPolicyModel).where(
            AgentPolicyModel.agent_name == agent_name,
            AgentPolicyModel.organization_id == org_id
        ).order_by(AgentPolicyModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_policy_by_id(self, policy_id: str, org_id: str) -> Optional[AgentPolicyModel]:
        stmt = select(AgentPolicyModel).where(
            AgentPolicyModel.id == policy_id,
            AgentPolicyModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def update_policy(self, policy: AgentPolicyModel) -> AgentPolicyModel:
        await self.session.flush()
        return policy

    async def create_adaptation(self, adaptation: AgentAdaptationModel) -> AgentAdaptationModel:
        self.session.add(adaptation)
        await self.session.flush()
        return adaptation

    async def list_adaptations(self, org_id: str) -> List[AgentAdaptationModel]:
        stmt = select(AgentAdaptationModel).where(
            AgentAdaptationModel.organization_id == org_id
        ).order_by(AgentAdaptationModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
