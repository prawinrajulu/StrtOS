from typing import Dict, Any, Tuple, List
from app.agent_intelligence.models import AgentHealthStatus, AgentTrendStatus

class AgentHealthEngine:
    """
    Deterministic Agent Health Engine computing overall agent health score,
    health status classification, and historical performance trends.
    DO NOT use LLM to calculate health metrics.
    """

    WEIGHT_OUTCOME_SUCCESS = 0.25
    WEIGHT_PREDICTION_ACCURACY = 0.20
    WEIGHT_EVIDENCE_QUALITY = 0.15
    WEIGHT_RELIABILITY = 0.15
    WEIGHT_CONFIDENCE = 0.10
    WEIGHT_TOOL_SUCCESS = 0.05
    WEIGHT_LLM_SUCCESS = 0.05
    WEIGHT_LATENCY = 0.05

    @classmethod
    def calculate_health_score(
        cls,
        outcome_success_rate: float = 80.0,
        prediction_accuracy: float = 80.0,
        evidence_quality_score: float = 85.0,
        reliability_score: float = 85.0,
        confidence_score: float = 85.0,
        tool_success_rate: float = 95.0,
        llm_success_rate: float = 95.0,
        average_latency_ms: float = 1200.0
    ) -> Tuple[float, AgentHealthStatus]:
        """
        Calculates deterministic overall_agent_score and maps to AgentHealthStatus.
        """
        # Latency score calculation (0-100 scale, <2000ms is ideal)
        if average_latency_ms <= 1000.0:
            latency_score = 100.0
        elif average_latency_ms <= 3000.0:
            latency_score = max(0.0, 100.0 - (average_latency_ms - 1000.0) / 40.0)
        else:
            latency_score = max(0.0, 50.0 - (average_latency_ms - 3000.0) / 100.0)

        overall_agent_score = round(
            outcome_success_rate * cls.WEIGHT_OUTCOME_SUCCESS +
            prediction_accuracy * cls.WEIGHT_PREDICTION_ACCURACY +
            evidence_quality_score * cls.WEIGHT_EVIDENCE_QUALITY +
            reliability_score * cls.WEIGHT_RELIABILITY +
            confidence_score * cls.WEIGHT_CONFIDENCE +
            tool_success_rate * cls.WEIGHT_TOOL_SUCCESS +
            llm_success_rate * cls.WEIGHT_LLM_SUCCESS +
            latency_score * cls.WEIGHT_LATENCY,
            2
        )

        if overall_agent_score >= 90.0:
            status = AgentHealthStatus.EXCELLENT
        elif overall_agent_score >= 78.0:
            status = AgentHealthStatus.HEALTHY
        elif overall_agent_score >= 65.0:
            status = AgentHealthStatus.DEGRADED
        elif overall_agent_score >= 50.0:
            status = AgentHealthStatus.AT_RISK
        else:
            status = AgentHealthStatus.CRITICAL

        return overall_agent_score, status

    @classmethod
    def calculate_trend(
        cls,
        history_scores: List[float],
        min_sample_threshold: int = 3
    ) -> AgentTrendStatus:
        """
        Calculates historical trend based on empirical scores window.
        """
        if len(history_scores) < min_sample_threshold:
            return AgentTrendStatus.INSUFFICIENT_DATA

        latest = history_scores[0]
        previous_avg = sum(history_scores[1:]) / len(history_scores[1:])

        delta = latest - previous_avg
        if delta >= 2.0:
            return AgentTrendStatus.IMPROVING
        elif delta <= -2.0:
            return AgentTrendStatus.DECLINING
        else:
            return AgentTrendStatus.STABLE
