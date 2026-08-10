from typing import Dict, Any, Optional
from app.learning.models import AgentPerformanceModel, ToolReliabilityModel, LLMProviderPerformanceModel
from app.learning.reliability_engine import ReliabilityEngine

class PerformanceEngine:
    """
    Performance Engine tracking execution metrics and updating reliability scores.
    """

    @classmethod
    def update_agent_telemetry(
        cls,
        perf: AgentPerformanceModel,
        status: str,
        confidence: float,
        latency_ms: float,
        token_usage: int,
        prediction_accuracy: Optional[float] = None
    ) -> AgentPerformanceModel:
        perf.total_executions += 1
        if status == "SUCCESS":
            perf.successful_executions += 1
        elif status == "DEGRADED":
            perf.degraded_executions += 1
        else:
            perf.failed_executions += 1

        # Moving Averages
        n = perf.total_executions
        perf.average_confidence = round(((perf.average_confidence * (n - 1)) + confidence) / n, 1)
        perf.average_latency_ms = round(((perf.average_latency_ms * (n - 1)) + latency_ms) / n, 1)
        perf.average_token_usage = int(((perf.average_token_usage * (n - 1)) + token_usage) / n)

        if prediction_accuracy is not None:
            perf.prediction_accuracy = round(((perf.prediction_accuracy * (n - 1)) + prediction_accuracy) / n, 1)

        # Recalculate Reliability Score
        score, rel_class = ReliabilityEngine.calculate_reliability(
            total_executions=perf.total_executions,
            successful_executions=perf.successful_executions,
            prediction_accuracy=perf.prediction_accuracy,
            outcome_success_rate=perf.outcome_success_rate,
            evidence_quality_score=perf.evidence_quality_score,
            human_approval_rate=perf.human_approval_rate,
            tool_success_rate=perf.tool_success_rate,
            swarm_consensus_rate=perf.swarm_consensus_rate
        )

        perf.current_reliability_score = score
        perf.reliability_class = rel_class
        return perf
