from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.agent_intelligence.models import (
    AgentIntelligenceMetricModel, AgentBenchmarkModel, AgentAnomalyModel,
    AgentWeaknessModel, AgentOptimizationRecommendationModel, RecommendationStatus,
    AgentHealthStatus, AgentTrendStatus
)
from app.agent_intelligence.schemas import (
    AgentMetricResponse, AgentBenchmarkResponse, AgentAnomalyResponse,
    AgentWeaknessResponse, AgentOptimizationRecommendationResponse,
    AgentIntelligenceOverviewResponse
)
from app.agent_intelligence.repository import AgentIntelligenceRepository
from app.agent_intelligence.engine import AgentHealthEngine
from app.agent_intelligence.benchmark import AgentBenchmarkEngine, SPECIALIST_AGENTS
from app.agent_intelligence.weakness import AgentWeaknessDetector
from app.agent_intelligence.anomaly import AgentAnomalyDetector
from app.agent_intelligence.optimizer import AgentOptimizationEngine

from app.policies.service import PolicyService
from app.policies.schemas import PolicyOptimizeRequest

from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

from app.core.events.publisher import event_publisher
from app.core.logging import logger

class AgentIntelligenceService:
    """
    Core Agent Performance Intelligence & Autonomous Optimization Service.
    Measures specialist agent performance, detects weaknesses & anomalies,
    generates bounded recommendations, and bridges to v1.6 Policy Evolution & Governance.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AgentIntelligenceRepository(session)
        self.policy_service = PolicyService(session)
        self.memory_service = MemoryService(session)

    async def analyze_agent(self, agent_name: str, org_id: str) -> AgentMetricResponse:
        """
        Calculates deterministic metrics, health score, weakness, anomaly, and optimization recommendation for an agent.
        """
        history = await self.repo.list_metric_history(agent_name, org_id)
        prev_metric = history[0] if history else None

        # Gather base telemetry or fallback to standard baseline
        exec_cnt = (prev_metric.execution_count + 1) if prev_metric else 10
        succ_cnt = (prev_metric.successful_execution_count + 1) if prev_metric else 9
        fail_cnt = (prev_metric.failed_execution_count) if prev_metric else 1
        deg_cnt = (prev_metric.degraded_execution_count) if prev_metric else 0

        succ_rate = round((succ_cnt / exec_cnt) * 100.0, 1)
        fail_rate = round((fail_cnt / exec_cnt) * 100.0, 1)

        pred_acc = prev_metric.prediction_accuracy if prev_metric else 85.0
        out_succ = prev_metric.outcome_success_rate if prev_metric else 88.0
        ev_q = prev_metric.evidence_quality_score if prev_metric else 85.0
        rel_score = prev_metric.policy_score if prev_metric else 85.0
        conf_score = prev_metric.average_confidence if prev_metric else 85.0
        tool_succ = prev_metric.tool_success_rate if prev_metric else 95.0
        llm_succ = prev_metric.llm_success_rate if prev_metric else 95.0
        lat_ms = prev_metric.average_latency_ms if prev_metric and prev_metric.average_latency_ms > 0 else 1200.0

        overall_score, health_status = AgentHealthEngine.calculate_health_score(
            outcome_success_rate=out_succ,
            prediction_accuracy=pred_acc,
            evidence_quality_score=ev_q,
            reliability_score=rel_score,
            confidence_score=conf_score,
            tool_success_rate=tool_succ,
            llm_success_rate=llm_succ,
            average_latency_ms=lat_ms
        )

        history_scores = [m.overall_agent_score for m in history] if history else [overall_score]
        trend = AgentHealthEngine.calculate_trend(history_scores)

        metric = AgentIntelligenceMetricModel(
            organization_id=org_id,
            agent_name=agent_name,
            policy_version="1.0.0",
            execution_count=exec_cnt,
            successful_execution_count=succ_cnt,
            failed_execution_count=fail_cnt,
            degraded_execution_count=deg_cnt,
            success_rate=succ_rate,
            failure_rate=fail_rate,
            average_latency_ms=lat_ms,
            p95_latency_ms=lat_ms * 1.25,
            average_confidence=conf_score,
            evidence_quality_score=ev_q,
            tool_success_rate=tool_succ,
            llm_success_rate=llm_succ,
            prediction_accuracy=pred_acc,
            outcome_success_rate=out_succ,
            policy_score=rel_score,
            average_token_usage=1450,
            estimated_cost=0.012,
            overall_agent_score=overall_score,
            health_status=health_status,
            trend=trend
        )
        metric = await self.repo.save_metric(metric)

        # Detect Weaknesses
        weaknesses = AgentWeaknessDetector.detect_weaknesses(org_id, metric)
        for w in weaknesses:
            await self.repo.save_weakness(w)
            await event_publisher.publish(
                event_type="agent.weakness.detected",
                organization_id=org_id,
                agent_name=agent_name,
                status=w.severity.value,
                metadata={"weakness_type": w.weakness_type, "metric_name": w.metric_name}
            )

        # Detect Anomalies
        anomalies = AgentAnomalyDetector.detect_anomalies(org_id, metric, prev_metric)
        for a in anomalies:
            await self.repo.save_anomaly(a)
            await event_publisher.publish(
                event_type="agent.anomaly.detected",
                organization_id=org_id,
                agent_name=agent_name,
                status=a.severity.value,
                metadata={"anomaly_type": a.anomaly_type, "deviation_percent": a.deviation_percent}
            )

        # Generate Recommendations
        recommendations = AgentOptimizationEngine.generate_recommendations(org_id, metric, weaknesses, anomalies)
        for r in recommendations:
            await self.repo.save_recommendation(r)
            await event_publisher.publish(
                event_type="agent.optimization.recommended",
                organization_id=org_id,
                agent_name=agent_name,
                metadata={"recommendation_id": r.id, "target_metric": r.target_metric}
            )

        # Memory Record
        try:
            await self.memory_service.create_memory(
                data=MemoryRecordCreate(
                    title=f"Agent Intelligence Analysis: {agent_name}",
                    content=f"Analyzed {agent_name} performance score ({overall_score}%). Health Status: {health_status.value}.",
                    memory_type=MemoryType.LEARNING,
                    outcome_status=OutcomeStatus.SUCCESS,
                    confidence=conf_score,
                    metadata={"agent_name": agent_name, "health_status": health_status.value, "overall_score": overall_score}
                ),
                org_id=org_id
            )
        except Exception as e:
            logger.warning(f"Failed to write memory log for agent analysis: {e}")

        await event_publisher.publish(
            event_type="agent.health.updated",
            organization_id=org_id,
            agent_name=agent_name,
            status=health_status.value,
            metadata={"overall_agent_score": overall_score, "trend": trend.value}
        )

        return AgentMetricResponse.model_validate(metric)

    async def get_overview(self, org_id: str) -> AgentIntelligenceOverviewResponse:
        metrics_by_agent: Dict[str, AgentIntelligenceMetricModel] = {}
        for agent_name in SPECIALIST_AGENTS:
            latest = await self.repo.get_latest_metric(agent_name, org_id)
            if not latest:
                # Trigger baseline analysis
                latest_res = await self.analyze_agent(agent_name, org_id)
                latest = await self.repo.get_latest_metric(agent_name, org_id)
            if latest:
                metrics_by_agent[agent_name] = latest

        # Benchmarks
        benchmarks = AgentBenchmarkEngine.generate_benchmarks(org_id, metrics_by_agent)
        for bm in benchmarks:
            await self.repo.save_benchmark(bm)

        metrics_list = list(metrics_by_agent.values())
        total_cnt = len(metrics_list)
        healthy_cnt = sum(1 for m in metrics_list if m.health_status in (AgentHealthStatus.EXCELLENT, AgentHealthStatus.HEALTHY))
        at_risk_cnt = sum(1 for m in metrics_list if m.health_status in (AgentHealthStatus.DEGRADED, AgentHealthStatus.AT_RISK))
        critical_cnt = sum(1 for m in metrics_list if m.health_status == AgentHealthStatus.CRITICAL)

        avg_score = sum(m.overall_agent_score for m in metrics_list) / total_cnt if total_cnt > 0 else 80.0
        avg_acc = sum(m.prediction_accuracy for m in metrics_list) / total_cnt if total_cnt > 0 else 80.0
        avg_rel = sum(m.policy_score for m in metrics_list) / total_cnt if total_cnt > 0 else 80.0

        recs = await self.repo.list_recommendations(org_id)
        weaknesses = await self.repo.list_weaknesses(org_id)
        anomalies = await self.repo.list_anomalies(org_id)

        return AgentIntelligenceOverviewResponse(
            total_agents=total_cnt,
            healthy_agents=healthy_cnt,
            at_risk_agents=at_risk_cnt,
            critical_agents=critical_cnt,
            average_agent_score=round(avg_score, 1),
            average_accuracy=round(avg_acc, 1),
            average_reliability=round(avg_rel, 1),
            optimization_recommendations_count=len(recs),
            agents=[AgentMetricResponse.model_validate(m) for m in metrics_list],
            benchmarks=[AgentBenchmarkResponse.model_validate(b) for b in benchmarks],
            recent_anomalies=[AgentAnomalyResponse.model_validate(a) for a in anomalies[:5]],
            recent_weaknesses=[AgentWeaknessResponse.model_validate(w) for w in weaknesses[:5]]
        )

    async def list_agents(self, org_id: str) -> List[AgentMetricResponse]:
        results = []
        for agent_name in SPECIALIST_AGENTS:
            latest = await self.repo.get_latest_metric(agent_name, org_id)
            if not latest:
                latest_res = await self.analyze_agent(agent_name, org_id)
                latest = await self.repo.get_latest_metric(agent_name, org_id)
            if latest:
                results.append(AgentMetricResponse.model_validate(latest))
        return results

    async def get_agent(self, agent_name: str, org_id: str) -> AgentMetricResponse:
        latest = await self.repo.get_latest_metric(agent_name, org_id)
        if not latest:
            return await self.analyze_agent(agent_name, org_id)
        return AgentMetricResponse.model_validate(latest)

    async def list_agent_history(self, agent_name: str, org_id: str) -> List[AgentMetricResponse]:
        history = await self.repo.list_metric_history(agent_name, org_id)
        return [AgentMetricResponse.model_validate(m) for m in history]

    async def list_benchmarks(self, org_id: str) -> List[AgentBenchmarkResponse]:
        bms = await self.repo.list_benchmarks(org_id)
        if not bms:
            await self.get_overview(org_id)
            bms = await self.repo.list_benchmarks(org_id)
        return [AgentBenchmarkResponse.model_validate(b) for b in bms]

    async def list_anomalies(self, org_id: str) -> List[AgentAnomalyResponse]:
        anomalies = await self.repo.list_anomalies(org_id)
        return [AgentAnomalyResponse.model_validate(a) for a in anomalies]

    async def list_weaknesses(self, org_id: str) -> List[AgentWeaknessResponse]:
        weaknesses = await self.repo.list_weaknesses(org_id)
        return [AgentWeaknessResponse.model_validate(w) for w in weaknesses]

    async def list_recommendations(self, org_id: str) -> List[AgentOptimizationRecommendationResponse]:
        recs = await self.repo.list_recommendations(org_id)
        return [AgentOptimizationRecommendationResponse.model_validate(r) for r in recs]

    async def submit_governance_recommendation(self, rec_id: str, org_id: str, user_id: str) -> AgentOptimizationRecommendationResponse:
        """
        Bridges recommendation to v1.6 Policy Evolution & Governance system.
        """
        rec = await self.repo.get_recommendation(rec_id, org_id)
        if not rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")

        # Find policy for agent
        policy_list = await self.policy_service.list_policies(org_id)
        target_policy = next((p for p in policy_list if p.agent_name == rec.agent_name), None)

        if not target_policy:
            # Create policy baseline if needed
            policy_res = await self.policy_service.create_policy(
                data=PolicyCreate(
                    agent_name=rec.agent_name,
                    policy_name=f"{rec.agent_name} Strategy Policy",
                    parameters={"confidence_threshold": 85.0},
                    change_reason="Auto-created policy baseline for optimization recommendation"
                ),
                org_id=org_id,
                created_by=user_id
            )
            policy_id = policy_res.id
        else:
            policy_id = target_policy.id

        # Trigger v1.6 Policy Optimization proposal
        opt_res = await self.policy_service.optimize_policy(
            policy_id=policy_id,
            data=PolicyOptimizeRequest(
                proposed_parameters=rec.recommended_policy_change,
                reason=rec.reason
            ),
            org_id=org_id,
            user_id=user_id
        )

        rec.status = RecommendationStatus.PENDING_GOVERNANCE
        rec.governance_approval_id = opt_res.governance_approval_id
        if opt_res.candidate_version:
            rec.candidate_policy_id = policy_id
        await self.session.commit()

        await event_publisher.publish(
            event_type="agent.optimization.governance.pending",
            organization_id=org_id,
            agent_name=rec.agent_name,
            status="PENDING_GOVERNANCE",
            metadata={"recommendation_id": rec.id, "approval_id": rec.governance_approval_id}
        )

        return AgentOptimizationRecommendationResponse.model_validate(rec)
