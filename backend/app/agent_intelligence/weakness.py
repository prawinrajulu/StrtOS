from typing import List
from datetime import datetime, timezone
from app.agent_intelligence.models import (
    AgentWeaknessModel, AgentIntelligenceMetricModel, WeaknessSeverity
)

class AgentWeaknessDetector:
    """
    Agent Weakness Detector performing empirical analysis to identify operational regressions.
    """

    @classmethod
    def detect_weaknesses(
        cls,
        org_id: str,
        metric: AgentIntelligenceMetricModel
    ) -> List[AgentWeaknessModel]:
        weaknesses: List[AgentWeaknessModel] = []
        agent = metric.agent_name

        pred_acc = metric.prediction_accuracy if metric.prediction_accuracy is not None else 85.0
        ev_q = metric.evidence_quality_score if metric.evidence_quality_score is not None else 85.0
        fail_rate = metric.failure_rate if metric.failure_rate is not None else 0.0
        lat_ms = metric.average_latency_ms if metric.average_latency_ms is not None else 1200.0
        tool_succ = metric.tool_success_rate if metric.tool_success_rate is not None else 95.0
        exec_cnt = metric.execution_count if metric.execution_count is not None else 1

        # 1. Low Accuracy Check
        if pred_acc < 75.0:
            sev = WeaknessSeverity.HIGH if pred_acc < 60.0 else WeaknessSeverity.MEDIUM
            weaknesses.append(AgentWeaknessModel(
                organization_id=org_id,
                agent_name=agent,
                weakness_type="LOW_ACCURACY",
                severity=sev,
                metric_name="prediction_accuracy",
                current_value=pred_acc,
                baseline_value=85.0,
                deviation=round(85.0 - pred_acc, 2),
                sample_count=exec_cnt,
                explanation=f"Agent '{agent}' prediction accuracy ({pred_acc:.1f}%) is below baseline threshold (85.0%)."
            ))

        # 2. Low Evidence Quality Check
        if ev_q < 75.0:
            sev = WeaknessSeverity.HIGH if ev_q < 60.0 else WeaknessSeverity.MEDIUM
            weaknesses.append(AgentWeaknessModel(
                organization_id=org_id,
                agent_name=agent,
                weakness_type="LOW_EVIDENCE_QUALITY",
                severity=sev,
                metric_name="evidence_quality_score",
                current_value=ev_q,
                baseline_value=85.0,
                deviation=round(85.0 - ev_q, 2),
                sample_count=exec_cnt,
                explanation=f"Agent '{agent}' evidence quality ({ev_q:.1f}%) indicates unverified input data."
            ))

        # 3. High Failure Rate
        if fail_rate > 15.0:
            sev = WeaknessSeverity.CRITICAL if fail_rate > 30.0 else WeaknessSeverity.HIGH
            weaknesses.append(AgentWeaknessModel(
                organization_id=org_id,
                agent_name=agent,
                weakness_type="HIGH_FAILURE_RATE",
                severity=sev,
                metric_name="failure_rate",
                current_value=fail_rate,
                baseline_value=5.0,
                deviation=round(fail_rate - 5.0, 2),
                sample_count=exec_cnt,
                explanation=f"Agent '{agent}' failure rate ({fail_rate:.1f}%) exceeds maximum acceptable threshold (15.0%)."
            ))

        # 4. High Latency
        if lat_ms > 2500.0:
            sev = WeaknessSeverity.MEDIUM
            weaknesses.append(AgentWeaknessModel(
                organization_id=org_id,
                agent_name=agent,
                weakness_type="HIGH_LATENCY",
                severity=sev,
                metric_name="average_latency_ms",
                current_value=lat_ms,
                baseline_value=1200.0,
                deviation=round(lat_ms - 1200.0, 2),
                sample_count=exec_cnt,
                explanation=f"Agent '{agent}' latency ({lat_ms:.0f}ms) is higher than normal baseline (1200ms)."
            ))

        # 5. Tool Success Rate Drop
        if tool_succ < 85.0:
            sev = WeaknessSeverity.HIGH
            weaknesses.append(AgentWeaknessModel(
                organization_id=org_id,
                agent_name=agent,
                weakness_type="REPEATED_TOOL_FAILURES",
                severity=sev,
                metric_name="tool_success_rate",
                current_value=tool_succ,
                baseline_value=95.0,
                deviation=round(95.0 - tool_succ, 2),
                sample_count=exec_cnt,
                explanation=f"Agent '{agent}' tool integration success rate ({tool_succ:.1f}%) is degraded."
            ))

        return weaknesses
