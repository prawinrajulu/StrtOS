from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.agent_intelligence.models import (
    AgentIntelligenceMetricModel, AgentBenchmarkModel, AgentAnomalyModel,
    AgentWeaknessModel, AgentOptimizationRecommendationModel, AgentHealthStatus
)

class AgentIntelligenceRepository:
    """
    Data Access Repository for Agent Intelligence domain with strict organization_id tenant isolation.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_metric(self, metric: AgentIntelligenceMetricModel) -> AgentIntelligenceMetricModel:
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric

    async def get_latest_metric(self, agent_name: str, org_id: str) -> Optional[AgentIntelligenceMetricModel]:
        stmt = select(AgentIntelligenceMetricModel).where(
            AgentIntelligenceMetricModel.agent_name == agent_name,
            AgentIntelligenceMetricModel.organization_id == org_id
        ).order_by(AgentIntelligenceMetricModel.recorded_at.desc())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_metrics(self, org_id: str) -> List[AgentIntelligenceMetricModel]:
        stmt = select(AgentIntelligenceMetricModel).where(
            AgentIntelligenceMetricModel.organization_id == org_id
        ).order_by(AgentIntelligenceMetricModel.recorded_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_metric_history(self, agent_name: str, org_id: str) -> List[AgentIntelligenceMetricModel]:
        stmt = select(AgentIntelligenceMetricModel).where(
            AgentIntelligenceMetricModel.agent_name == agent_name,
            AgentIntelligenceMetricModel.organization_id == org_id
        ).order_by(AgentIntelligenceMetricModel.recorded_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def save_benchmark(self, benchmark: AgentBenchmarkModel) -> AgentBenchmarkModel:
        self.session.add(benchmark)
        await self.session.commit()
        await self.session.refresh(benchmark)
        return benchmark

    async def list_benchmarks(self, org_id: str) -> List[AgentBenchmarkModel]:
        stmt = select(AgentBenchmarkModel).where(
            AgentBenchmarkModel.organization_id == org_id
        ).order_by(AgentBenchmarkModel.rank.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def save_anomaly(self, anomaly: AgentAnomalyModel) -> AgentAnomalyModel:
        self.session.add(anomaly)
        await self.session.commit()
        await self.session.refresh(anomaly)
        return anomaly

    async def list_anomalies(self, org_id: str) -> List[AgentAnomalyModel]:
        stmt = select(AgentAnomalyModel).where(
            AgentAnomalyModel.organization_id == org_id
        ).order_by(AgentAnomalyModel.detected_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def save_weakness(self, weakness: AgentWeaknessModel) -> AgentWeaknessModel:
        self.session.add(weakness)
        await self.session.commit()
        await self.session.refresh(weakness)
        return weakness

    async def list_weaknesses(self, org_id: str) -> List[AgentWeaknessModel]:
        stmt = select(AgentWeaknessModel).where(
            AgentWeaknessModel.organization_id == org_id
        ).order_by(AgentWeaknessModel.detected_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def save_recommendation(self, rec: AgentOptimizationRecommendationModel) -> AgentOptimizationRecommendationModel:
        self.session.add(rec)
        await self.session.commit()
        await self.session.refresh(rec)
        return rec

    async def get_recommendation(self, rec_id: str, org_id: str) -> Optional[AgentOptimizationRecommendationModel]:
        stmt = select(AgentOptimizationRecommendationModel).where(
            AgentOptimizationRecommendationModel.id == rec_id,
            AgentOptimizationRecommendationModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_recommendations(self, org_id: str) -> List[AgentOptimizationRecommendationModel]:
        stmt = select(AgentOptimizationRecommendationModel).where(
            AgentOptimizationRecommendationModel.organization_id == org_id
        ).order_by(AgentOptimizationRecommendationModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
