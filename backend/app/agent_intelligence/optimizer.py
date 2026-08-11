from typing import List, Dict, Any, Optional
from app.agent_intelligence.models import (
    AgentOptimizationRecommendationModel, AgentIntelligenceMetricModel,
    AgentWeaknessModel, AgentAnomalyModel, RecommendationStatus
)

class AgentOptimizationEngine:
    """
    Agent Optimization Engine translating detected weaknesses and performance metrics
    into grounded optimization recommendations.
    Connects to v1.6 Policy Evolution without bypassing policy bounds or governance.
    """

    @classmethod
    def generate_recommendations(
        cls,
        org_id: str,
        metric: AgentIntelligenceMetricModel,
        weaknesses: List[AgentWeaknessModel],
        anomalies: List[AgentAnomalyModel]
    ) -> List[AgentOptimizationRecommendationModel]:
        recommendations: List[AgentOptimizationRecommendationModel] = []
        agent = metric.agent_name

        # If weaknesses exist, generate focused recommendation
        for w in weaknesses:
            if w.weakness_type == "LOW_ACCURACY":
                recommendations.append(AgentOptimizationRecommendationModel(
                    organization_id=org_id,
                    agent_name=agent,
                    target_metric="prediction_accuracy",
                    current_value=metric.prediction_accuracy,
                    target_value=88.0,
                    expected_improvement=8.0,
                    risk_score=20.0,
                    risk_level="LOW",
                    recommended_policy_change={"evidence_weight": 0.45, "confidence_threshold": 85.0},
                    reason=f"Optimize evidence weighting and confidence threshold to restore prediction accuracy for {agent}.",
                    evidence_summary={"weakness_id": w.id, "deviation": w.deviation},
                    status=RecommendationStatus.DRAFT
                ))

            elif w.weakness_type == "LOW_EVIDENCE_QUALITY":
                recommendations.append(AgentOptimizationRecommendationModel(
                    organization_id=org_id,
                    agent_name=agent,
                    target_metric="evidence_quality_score",
                    current_value=metric.evidence_quality_score,
                    target_value=85.0,
                    expected_improvement=10.0,
                    risk_score=25.0,
                    risk_level="LOW",
                    recommended_policy_change={"min_evidence_items": 3, "require_tool_verification": True},
                    reason=f"Enforce mandatory tool verification and minimum evidence count for {agent}.",
                    evidence_summary={"weakness_id": w.id, "deviation": w.deviation},
                    status=RecommendationStatus.DRAFT
                ))

            elif w.weakness_type == "HIGH_FAILURE_RATE":
                recommendations.append(AgentOptimizationRecommendationModel(
                    organization_id=org_id,
                    agent_name=agent,
                    target_metric="failure_rate",
                    current_value=metric.failure_rate,
                    target_value=5.0,
                    expected_improvement=12.0,
                    risk_score=45.0,
                    risk_level="MEDIUM",
                    recommended_policy_change={"max_retries": 3, "fallback_provider": "gemini"},
                    reason=f"Add automatic fallback provider routing and retry bounds to reduce failure rate for {agent}.",
                    evidence_summary={"weakness_id": w.id, "deviation": w.deviation},
                    status=RecommendationStatus.DRAFT
                ))

        # Default proactive optimization if no weaknesses exist
        if not recommendations:
            recommendations.append(AgentOptimizationRecommendationModel(
                organization_id=org_id,
                agent_name=agent,
                target_metric="overall_agent_score",
                current_value=metric.overall_agent_score,
                target_value=min(100.0, metric.overall_agent_score + 5.0),
                expected_improvement=5.0,
                risk_score=15.0,
                risk_level="LOW",
                recommended_policy_change={"bounded_adaptation_delta": 5.0},
                reason=f"Proactive bounded auto-tuning proposal (+5% score optimization) for {agent}.",
                evidence_summary={"current_score": metric.overall_agent_score},
                status=RecommendationStatus.DRAFT
            ))

        return recommendations
