from typing import List, Dict, Any, Optional, Tuple
from app.business_state.models import MetricDirection, AlertSeverity, AlertStatus
from app.business_state.schemas import (
    OpportunityResponse, ThreatResponse, BusinessHealthResponse, BusinessExplanationResponse
)

class BusinessBaselineEngine:
    """Calculates deterministic absolute and percentage deltas against historical averages."""

    def compare_metrics(
        self,
        previous_value: float,
        current_value: float
    ) -> Tuple[float, float, MetricDirection]:
        delta = round(current_value - previous_value, 2)
        if previous_value == 0.0:
            percentage_change = 0.0 if current_value == 0.0 else 100.0
        else:
            percentage_change = round((delta / abs(previous_value)) * 100.0, 2)

        if delta > 0.01:
            direction = MetricDirection.INCREASE
        elif delta < -0.01:
            direction = MetricDirection.DECREASE
        else:
            direction = MetricDirection.STABLE

        return delta, percentage_change, direction

class ChangeDetectionEngine:
    """Evaluates metric change thresholds to classify severity."""

    def evaluate_change_severity(
        self,
        metric_name: str,
        percentage_change: float,
        direction: MetricDirection
    ) -> AlertSeverity:
        abs_change = abs(percentage_change)
        
        # Revenue or Conversion drop sensitivity
        is_negative_critical_metric = ("revenue" in metric_name.lower() or "conversion" in metric_name.lower() or "lead" in metric_name.lower()) and direction == MetricDirection.DECREASE

        if is_negative_critical_metric:
            if abs_change >= 20.0:
                return AlertSeverity.CRITICAL
            elif abs_change >= 10.0:
                return AlertSeverity.HIGH
            elif abs_change >= 5.0:
                return AlertSeverity.MEDIUM
            return AlertSeverity.LOW

        if abs_change >= 35.0:
            return AlertSeverity.HIGH
        elif abs_change >= 15.0:
            return AlertSeverity.MEDIUM
        elif abs_change >= 5.0:
            return AlertSeverity.LOW

        return AlertSeverity.INFO

class OpportunityDetectionEngine:
    """Identifies evidence-backed growth channels and SEO tailwinds."""

    def detect_opportunities(
        self,
        metrics: Dict[str, float]
    ) -> List[OpportunityResponse]:
        opportunities: List[OpportunityResponse] = []

        seo_score = metrics.get("SEO Score", 85.0)
        if seo_score >= 88.0:
            opportunities.append(
                OpportunityResponse(
                    title="High SEO Authority Growth Catalyst",
                    category="SEO Tailwinds",
                    expected_value=15.0,
                    confidence_score=94.0,
                    evidence=f"Verified technical SEO score {seo_score} provides organic ranking tailwind.",
                    recommended_action="Scale high-intent landing page creation to capture organic traffic."
                )
            )

        conversion_rate = metrics.get("Conversion Rate", 3.5)
        if conversion_rate >= 4.0:
            opportunities.append(
                OpportunityResponse(
                    title="Conversion Rate Optimization Advantage",
                    category="Funnel Optimization",
                    expected_value=25.0,
                    confidence_score=92.0,
                    evidence=f"Conversion rate reached {conversion_rate}% benchmark.",
                    recommended_action="Increase paid acquisition budget to capitalize on higher funnel yield."
                )
            )

        return opportunities

class ThreatDetectionEngine:
    """Detects revenue deterioration, conversion drops, campaign degradation, and prediction drift."""

    def detect_threats(
        self,
        metrics: Dict[str, float],
        changes: List[Any]
    ) -> List[ThreatResponse]:
        threats: List[ThreatResponse] = []

        conv = metrics.get("Conversion Rate", 3.0)

        if conv <= 2.5 or any(c.percentage_change <= -10.0 for c in changes):
            threats.append(
                ThreatResponse(
                    title="Funnel Conversion Deterioration",
                    severity=AlertSeverity.HIGH,
                    confidence_score=95.0,
                    evidence=f"Conversion rate dropped to {conv}%, violating target threshold.",
                    potential_impact="Direct reduction in new customer acquisition velocity.",
                    recommended_action="Execute landing page audit and pause underperforming ad sets."
                )
            )

        agent_rel = metrics.get("Agent Reliability", 95.0)
        if agent_rel < 80.0:
            threats.append(
                ThreatResponse(
                    title="Agent Reliability Degradation",
                    severity=AlertSeverity.CRITICAL,
                    confidence_score=98.0,
                    evidence=f"Agent reliability index fell to {agent_rel}%.",
                    potential_impact="Execution failures in background automation workflows.",
                    recommended_action="Trigger governance pause on autonomous agent tasks."
                )
            )

        return threats

class BusinessHealthEngine:
    """Calculates deterministic 0-100 business health score."""

    def calculate_health(
        self,
        metrics: Dict[str, float]
    ) -> BusinessHealthResponse:
        scores = {
            "Revenue": min(100.0, (metrics.get("Revenue", 10000.0) / 10000.0) * 100.0),
            "Conversion": min(100.0, (metrics.get("Conversion Rate", 3.0) / 3.0) * 100.0),
            "SEO": min(100.0, metrics.get("SEO Score", 85.0)),
            "AgentReliability": metrics.get("Agent Reliability", 95.0)
        }

        overall = round(sum(scores.values()) / len(scores), 1)

        if overall >= 90.0:
            status = "EXCELLENT"
        elif overall >= 75.0:
            status = "HEALTHY"
        elif overall >= 60.0:
            status = "WATCH"
        elif overall >= 45.0:
            status = "AT_RISK"
        else:
            status = "CRITICAL"

        return BusinessHealthResponse(
            health_score=overall,
            health_status=status,
            component_scores=scores,
            recommendation=f"Business state is {status}. Maintain active strategy execution." if overall >= 75.0 else f"Business health degraded ({status}). Review strategic early-warning alerts."
        )

class StrategicEarlyWarningEngine:
    """Generates proactive strategic early-warning alerts."""

    def __init__(self):
        self.baseline_engine = BusinessBaselineEngine()
        self.change_engine = ChangeDetectionEngine()
        self.opportunity_engine = OpportunityDetectionEngine()
        self.threat_engine = ThreatDetectionEngine()
        self.health_engine = BusinessHealthEngine()
