from typing import List, Dict, Any
from app.agent_intelligence.models import AgentBenchmarkModel, AgentIntelligenceMetricModel, AgentTrendStatus

SPECIALIST_AGENTS = [
    "Business Analysis",
    "SEO Audit",
    "Competitor Research",
    "Marketing Strategy",
    "Campaign Planner"
]

class AgentBenchmarkEngine:
    """
    Agent Benchmark Engine generating normalized rankings across all 5 specialist agents.
    """

    MIN_BENCHMARK_SAMPLES = 1

    @classmethod
    def generate_benchmarks(
        cls,
        org_id: str,
        metrics_by_agent: Dict[str, AgentIntelligenceMetricModel]
    ) -> List[AgentBenchmarkModel]:
        """
        Generates comparative rankings for specialist agents.
        """
        items: List[Dict[str, Any]] = []

        for agent_name in SPECIALIST_AGENTS:
            metric = metrics_by_agent.get(agent_name)
            if metric:
                score = metric.overall_agent_score if metric.overall_agent_score is not None else 80.0
                rel = metric.policy_score if metric.policy_score is not None else 85.0
                acc = metric.prediction_accuracy if metric.prediction_accuracy is not None else 80.0
                ev_q = metric.evidence_quality_score if metric.evidence_quality_score is not None else 85.0
                speed = metric.average_latency_ms if metric.average_latency_ms and metric.average_latency_ms > 0 else 1200.0
                out_s = metric.outcome_success_rate if metric.outcome_success_rate is not None else 85.0
                conf = metric.average_confidence if metric.average_confidence is not None else 85.0
                samples = metric.execution_count if metric.execution_count and metric.execution_count > 0 else 1
                trend = metric.trend or AgentTrendStatus.STABLE
            else:
                score = 80.0
                rel = 85.0
                acc = 80.0
                ev_q = 85.0
                speed = 1200.0
                out_s = 80.0
                conf = 85.0
                samples = 1
                trend = AgentTrendStatus.STABLE

            items.append({
                "agent_name": agent_name,
                "overall_score": score,
                "reliability_score": rel,
                "accuracy_score": acc,
                "evidence_quality": ev_q,
                "execution_speed_ms": speed,
                "outcome_success": out_s,
                "confidence": conf,
                "sample_count": samples,
                "trend": trend
            })

        # Sort by overall_score descending to assign rank
        items.sort(key=lambda x: x["overall_score"], reverse=True)

        benchmarks = []
        for idx, item in enumerate(items, start=1):
            bm = AgentBenchmarkModel(
                organization_id=org_id,
                agent_name=item["agent_name"],
                rank=idx,
                overall_score=item["overall_score"],
                reliability_score=item["reliability_score"],
                accuracy_score=item["accuracy_score"],
                evidence_quality=item["evidence_quality"],
                execution_speed_ms=item["execution_speed_ms"],
                outcome_success=item["outcome_success"],
                confidence=item["confidence"],
                sample_count=item["sample_count"],
                trend=item["trend"]
            )
            benchmarks.append(bm)

        return benchmarks
