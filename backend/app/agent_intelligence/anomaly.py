from typing import List, Optional
from app.agent_intelligence.models import (
    AgentAnomalyModel, AgentIntelligenceMetricModel, WeaknessSeverity
)

class AgentAnomalyDetector:
    """
    Deterministic Anomaly Detector comparing current execution window metrics
    against historical baselines.
    """

    @classmethod
    def detect_anomalies(
        cls,
        org_id: str,
        current_metric: AgentIntelligenceMetricModel,
        historical_baseline: Optional[AgentIntelligenceMetricModel] = None
    ) -> List[AgentAnomalyModel]:
        anomalies: List[AgentAnomalyModel] = []
        agent = current_metric.agent_name

        curr_fail = current_metric.failure_rate if current_metric.failure_rate is not None else 0.0
        curr_lat = current_metric.average_latency_ms if current_metric.average_latency_ms is not None else 1200.0
        curr_conf = current_metric.average_confidence if current_metric.average_confidence is not None else 85.0
        curr_acc = current_metric.prediction_accuracy if current_metric.prediction_accuracy is not None else 85.0

        if not historical_baseline:
            base_fail = 5.0
            base_lat = 1200.0
            base_conf = 85.0
            base_acc = 85.0
        else:
            base_fail = historical_baseline.failure_rate if historical_baseline.failure_rate is not None else 5.0
            base_lat = historical_baseline.average_latency_ms if historical_baseline.average_latency_ms is not None else 1200.0
            base_conf = historical_baseline.average_confidence if historical_baseline.average_confidence is not None else 85.0
            base_acc = historical_baseline.prediction_accuracy if historical_baseline.prediction_accuracy is not None else 85.0

        # 1. Failure Rate Spike Anomaly
        if curr_fail > base_fail + 15.0:
            dev = round(((curr_fail - base_fail) / max(1.0, base_fail)) * 100.0, 2)
            sev = WeaknessSeverity.CRITICAL if curr_fail > 30.0 else WeaknessSeverity.HIGH
            anomalies.append(AgentAnomalyModel(
                organization_id=org_id,
                agent_name=agent,
                anomaly_type="FAILURE_RATE_SPIKE",
                severity=sev,
                baseline_value=base_fail,
                observed_value=curr_fail,
                deviation_percent=dev,
                explanation=f"Sudden failure rate spike for '{agent}': Observed {curr_fail:.1f}% vs baseline {base_fail:.1f}% (+{dev}% deviation)."
            ))

        # 2. Latency Spike Anomaly
        if curr_lat > base_lat * 2.0 and curr_lat > 2000.0:
            dev = round(((curr_lat - base_lat) / max(1.0, base_lat)) * 100.0, 2)
            anomalies.append(AgentAnomalyModel(
                organization_id=org_id,
                agent_name=agent,
                anomaly_type="LATENCY_SPIKE",
                severity=WeaknessSeverity.MEDIUM,
                baseline_value=base_lat,
                observed_value=curr_lat,
                deviation_percent=dev,
                explanation=f"Sudden latency spike for '{agent}': Observed {curr_lat:.0f}ms vs baseline {base_lat:.0f}ms (+{dev}% deviation)."
            ))

        # 3. Confidence Drop Anomaly
        if curr_conf < base_conf - 20.0:
            dev = round(((base_conf - curr_conf) / max(1.0, base_conf)) * 100.0, 2)
            anomalies.append(AgentAnomalyModel(
                organization_id=org_id,
                agent_name=agent,
                anomaly_type="CONFIDENCE_DROP",
                severity=WeaknessSeverity.HIGH,
                baseline_value=base_conf,
                observed_value=curr_conf,
                deviation_percent=dev,
                explanation=f"Abnormal confidence drop for '{agent}': Observed {curr_conf:.1f}% vs baseline {base_conf:.1f}% (-{dev}% deviation)."
            ))

        # 4. Accuracy Regression Anomaly
        if curr_acc < base_acc - 15.0:
            dev = round(((base_acc - curr_acc) / max(1.0, base_acc)) * 100.0, 2)
            anomalies.append(AgentAnomalyModel(
                organization_id=org_id,
                agent_name=agent,
                anomaly_type="ACCURACY_REGRESSION",
                severity=WeaknessSeverity.HIGH,
                baseline_value=base_acc,
                observed_value=curr_acc,
                deviation_percent=dev,
                explanation=f"Prediction accuracy regression for '{agent}': Observed {curr_acc:.1f}% vs baseline {base_acc:.1f}% (-{dev}% deviation)."
            ))

        return anomalies
