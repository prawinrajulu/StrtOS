"""
Portfolio Engine — pure computation layer.

All engines are stateless, deterministic, and side-effect free.
No DB access. No randomness. No external calls.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.portfolio.models import (
    StrategicPortfolioModel, PortfolioMissionModel,
    PortfolioHealth, PortfolioCheckpointDecision, ConstraintStatus
)
from app.portfolio.schemas import (
    PortfolioEvaluationResponse, PortfolioConstraintResponse
)


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO CONSTRAINT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioConstraintEngine:
    """
    Evaluates all portfolio constraints deterministically.
    Returns VALID / WARNING / VIOLATION per constraint.
    Never silently exceeds limits.
    """

    WARNING_THRESHOLD = 0.80   # 80% utilization → WARNING
    CRITICAL_THRESHOLD = 0.90  # 90% utilization → HIGH
    VIOLATION_THRESHOLD = 1.00 # 100% utilization → VIOLATION

    def evaluate_constraint(
        self, limit_value: float, current_usage: float, is_hard: bool
    ) -> Tuple[ConstraintStatus, str]:
        if limit_value <= 0:
            return ConstraintStatus.VALID, "No limit defined."

        utilization = current_usage / limit_value

        if utilization >= self.VIOLATION_THRESHOLD:
            if is_hard:
                return ConstraintStatus.VIOLATION, f"HARD constraint exceeded: {utilization*100:.1f}% utilization."
            return ConstraintStatus.WARNING, f"SOFT constraint exceeded: {utilization*100:.1f}% utilization."
        elif utilization >= self.CRITICAL_THRESHOLD:
            return ConstraintStatus.WARNING, f"HIGH utilization: {utilization*100:.1f}% — approaching constraint limit."
        elif utilization >= self.WARNING_THRESHOLD:
            return ConstraintStatus.WARNING, f"Utilization at {utilization*100:.1f}% — monitor closely."

        return ConstraintStatus.VALID, f"Utilization: {utilization*100:.1f}% — within limits."

    def evaluate_budget_constraint(self, total_budget: float, allocated_budget: float) -> Tuple[ConstraintStatus, str]:
        return self.evaluate_constraint(total_budget, allocated_budget, is_hard=True)

    def has_violations(self, portfolio: StrategicPortfolioModel) -> bool:
        for c in portfolio.constraints:
            status, _ = self.evaluate_constraint(c.limit_value, c.current_usage, c.is_hard_constraint)
            if status == ConstraintStatus.VIOLATION:
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO PRIORITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioPriorityEngine:
    """
    Ranks missions using deterministic weighted scoring.
    No random scoring. All inputs must be concrete values.

    Weights (sum = 1.0):
      strategic_importance: 0.20
      business_impact:      0.20
      expected_value:       0.15   (normalized 0-100)
      success_probability:  0.15
      urgency:              0.10
      risk_inv:             0.10   (inverse: low risk = higher score)
      resource_efficiency:  0.10   (expected_value / resource_requirement)
    """

    WEIGHTS = {
        "strategic_importance": 0.20,
        "business_impact": 0.20,
        "expected_value_norm": 0.15,
        "success_probability": 0.15,
        "urgency": 0.10,
        "risk_inv": 0.10,
        "resource_efficiency": 0.10,
    }

    def compute_priority_score(
        self,
        strategic_importance: float,    # 0-100
        business_impact: float,         # 0-100
        expected_value: float,          # raw currency/metric, normalized below
        success_probability: float,     # 0-100
        urgency: float,                 # 0-100 (higher = more urgent)
        risk_score: float,              # 0-100 (higher = riskier)
        resource_requirement: float,    # raw units
        max_expected_value: float = 1.0 # normalization anchor
    ) -> float:
        ev_norm = min(100.0, (expected_value / max(1.0, max_expected_value)) * 100.0)
        risk_inv = max(0.0, 100.0 - risk_score)
        resource_eff = min(100.0, (expected_value / max(1.0, resource_requirement)) * 10.0)

        score = (
            self.WEIGHTS["strategic_importance"] * strategic_importance +
            self.WEIGHTS["business_impact"] * business_impact +
            self.WEIGHTS["expected_value_norm"] * ev_norm +
            self.WEIGHTS["success_probability"] * success_probability +
            self.WEIGHTS["urgency"] * urgency +
            self.WEIGHTS["risk_inv"] * risk_inv +
            self.WEIGHTS["resource_efficiency"] * resource_eff
        )
        return round(min(100.0, max(0.0, score)), 2)

    def classify_priority(self, score: float) -> str:
        if score >= 80.0:
            return "CRITICAL"
        elif score >= 60.0:
            return "HIGH"
        elif score >= 40.0:
            return "MEDIUM"
        return "LOW"


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO EVALUATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioEvaluationEngine:
    """
    Compares expected vs actual portfolio performance.
    Calculates: ROI, mission success rate, resource efficiency, health.
    """

    def evaluate(
        self,
        portfolio_id: str,
        expected_value: float,
        actual_value: float,
        total_missions: int,
        completed_missions: int,
        total_budget: float,
        allocated_budget: float,
        risk_score: float,
        confidence_score: float
    ) -> PortfolioEvaluationResponse:
        # Portfolio ROI
        if expected_value > 0:
            roi = round(((actual_value - expected_value) / expected_value) * 100.0, 2)
        else:
            roi = 0.0

        # Mission success rate
        success_rate = round((completed_missions / max(1, total_missions)) * 100.0, 1)

        # Resource efficiency
        if allocated_budget > 0:
            resource_eff = round((actual_value / max(1.0, allocated_budget)) * 100.0, 1)
        else:
            resource_eff = 0.0

        # Health score (composite)
        health_score = round(
            0.30 * success_rate +
            0.25 * (100.0 - risk_score) +
            0.25 * confidence_score +
            0.20 * min(100.0, resource_eff)
        , 1)
        health_score = min(100.0, max(0.0, health_score))

        # Health label
        if health_score >= 90.0:
            health = PortfolioHealth.EXCELLENT
        elif health_score >= 75.0:
            health = PortfolioHealth.HEALTHY
        elif health_score >= 60.0:
            health = PortfolioHealth.WATCH
        elif health_score >= 40.0:
            health = PortfolioHealth.AT_RISK
        else:
            health = PortfolioHealth.CRITICAL

        summary = (
            f"Portfolio health: {health.value} (score {health_score}). "
            f"ROI: {roi:+.1f}%. Mission success rate: {success_rate}%. "
            f"Resource efficiency: {resource_eff:.1f}%."
        )

        return PortfolioEvaluationResponse(
            portfolio_id=portfolio_id,
            health=health,
            health_score=health_score,
            expected_value=expected_value,
            actual_value=actual_value,
            portfolio_roi=roi,
            mission_success_rate=success_rate,
            resource_efficiency=resource_eff,
            risk_score=risk_score,
            confidence_score=confidence_score,
            summary=summary
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO REBALANCING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioRebalancingEngine:
    """
    Detects rebalancing triggers and computes new version metadata.
    Bounded and deterministic — no side effects.
    """

    REBALANCE_TRIGGERS = {
        "mission_failed": True,
        "mission_completed": True,
        "forecast_material_change": True,  # >15% forecast delta
        "resource_availability_change": True,
        "risk_threshold_breached": True,   # risk > 70
        "objective_priority_shift": True,
    }

    def detect_triggers(
        self,
        current_risk: float,
        previous_risk: float,
        forecast_delta_pct: float,
        mission_failed: bool = False,
        mission_completed: bool = False,
        resource_changed: bool = False,
        objective_shifted: bool = False
    ) -> List[str]:
        triggers = []
        if mission_failed:
            triggers.append("mission_failed")
        if mission_completed:
            triggers.append("mission_completed")
        if abs(forecast_delta_pct) >= 15.0:
            triggers.append(f"forecast_material_change ({forecast_delta_pct:+.1f}%)")
        if resource_changed:
            triggers.append("resource_availability_change")
        if current_risk >= 70.0 and previous_risk < 70.0:
            triggers.append(f"risk_threshold_breached ({current_risk:.1f})")
        if objective_shifted:
            triggers.append("objective_priority_shift")
        return triggers

    def compute_new_version(self, current_version: str) -> str:
        parts = current_version.replace("v", "").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return f"v{major}.{minor + 1}.0"

    def requires_governance(self, risk_score: float, budget_utilization_pct: float) -> bool:
        return risk_score >= 70.0 or budget_utilization_pct >= 90.0


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO CHECKPOINT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioCheckpointEngine:
    """Evaluates portfolio checkpoint decisions deterministically."""

    def evaluate(
        self,
        health: PortfolioHealth,
        risk_score: float,
        progress_pct: float,
        has_violations: bool
    ) -> Tuple[PortfolioCheckpointDecision, str]:
        if progress_pct >= 100.0:
            return PortfolioCheckpointDecision.COMPLETE, "Portfolio objectives achieved."

        if has_violations:
            return PortfolioCheckpointDecision.ESCALATE, "Constraint violations detected — escalate to governance."

        if health == PortfolioHealth.CRITICAL or risk_score >= 85.0:
            return PortfolioCheckpointDecision.ESCALATE, "Critical health/risk — immediate escalation required."

        if health == PortfolioHealth.AT_RISK or risk_score >= 70.0:
            return PortfolioCheckpointDecision.REBALANCE, "Portfolio at risk — rebalancing recommended."

        if health == PortfolioHealth.WATCH and progress_pct < 30.0:
            return PortfolioCheckpointDecision.PAUSE, "Early-stage progress slow under watch status — pause for review."

        return PortfolioCheckpointDecision.CONTINUE, "Portfolio progressing within acceptable bounds."
