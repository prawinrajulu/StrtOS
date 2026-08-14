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


# ═══════════════════════════════════════════════════════════════════════════════
# CAPITAL ALLOCATION ENGINE (Requirement 6)
# ═══════════════════════════════════════════════════════════════════════════════

class CapitalAllocationEngine:
    """
    Deterministic capital and budget allocation computation.
    If budget data is missing or non-positive: returns INSUFFICIENT_DATA.
    Never fabricates financial figures.
    """

    def compute_allocation(
        self,
        portfolio_id: str,
        total_budget: Optional[float],
        current_spend: float,
        initiatives_or_missions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if total_budget is None or total_budget <= 0:
            return {
                "portfolio_id": portfolio_id,
                "total_budget": None,
                "current_spend": round(current_spend, 2),
                "allocated_budget": 0.0,
                "unused_budget": None,
                "budget_shortage": 0.0,
                "expected_portfolio_roi": None,
                "allocation_breakdown": [],
                "data_quality": "INSUFFICIENT_DATA",
                "explanation": "Capital budget is unconfigured or zero. Unable to compute capital allocation metrics."
            }

        allocated = sum(max(0.0, float(m.get("resource_requirement", m.get("capital_budget", 0.0)))) for m in initiatives_or_missions)
        unused = max(0.0, total_budget - allocated)
        shortage = max(0.0, allocated - total_budget)

        total_ev = sum(float(m.get("expected_value", 0.0)) for m in initiatives_or_missions)
        roi = round(((total_ev - allocated) / max(1.0, allocated)) * 100.0, 2) if allocated > 0 else 0.0

        breakdown = []
        for item in initiatives_or_missions:
            cost = max(0.0, float(item.get("resource_requirement", item.get("capital_budget", 0.0))))
            ev = float(item.get("expected_value", 0.0))
            item_roi = round(((ev - cost) / max(1.0, cost)) * 100.0, 2) if cost > 0 else 0.0
            breakdown.append({
                "id": item.get("id", item.get("mission_id", "unknown")),
                "title": item.get("title", "Untitled"),
                "allocated": cost,
                "expected_value": ev,
                "roi": item_roi,
                "pct_of_total_budget": round((cost / total_budget) * 100.0, 1) if total_budget > 0 else 0.0
            })

        return {
            "portfolio_id": portfolio_id,
            "total_budget": round(total_budget, 2),
            "current_spend": round(current_spend, 2),
            "allocated_budget": round(allocated, 2),
            "unused_budget": round(unused, 2),
            "budget_shortage": round(shortage, 2),
            "expected_portfolio_roi": roi,
            "allocation_breakdown": breakdown,
            "data_quality": "SUFFICIENT",
            "explanation": f"Budget allocated: ${allocated:,.2f} of ${total_budget:,.2f} ({allocated/total_budget*100:.1f}%). Expected ROI: {roi:+.1f}%."
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO TRADE-OFF ENGINE (Requirement 9)
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioTradeoffEngine:
    """
    Evaluates explicit trade-offs when prioritizing Initiative/Mission A over B.
    Deterministic — never masks risk or uncertainty.
    """

    def evaluate_tradeoff(
        self,
        item_a: Dict[str, Any],
        item_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        ev_a = float(item_a.get("expected_value", 0.0))
        ev_b = float(item_b.get("expected_value", 0.0))
        risk_a = float(item_a.get("risk_score", 20.0))
        risk_b = float(item_b.get("risk_score", 20.0))
        cost_a = max(1.0, float(item_a.get("resource_requirement", item_a.get("resource_cost", 1.0))))
        cost_b = max(1.0, float(item_b.get("resource_requirement", item_b.get("resource_cost", 1.0))))

        eff_a = ev_a / cost_a
        eff_b = ev_b / cost_b

        ev_delta = round(ev_a - ev_b, 2)
        risk_delta = round(risk_a - risk_b, 2)
        eff_delta = round(eff_a - eff_b, 2)

        tradeoffs_a = [
            f"+ Higher expected value: ${ev_a:,.0f} vs ${ev_b:,.0f} (delta ${ev_delta:+,.0f})" if ev_a >= ev_b else f"- Lower expected value: ${ev_a:,.0f} vs ${ev_b:,.0f}",
            f"- Higher execution risk score: {risk_a:.1f} vs {risk_b:.1f}" if risk_a > risk_b else f"+ Lower risk score: {risk_a:.1f} vs {risk_b:.1f}",
            f"- Consumes resource capacity, reducing availability for {item_b.get('title', 'Option B')}"
        ]

        tradeoffs_b = [
            f"+ Faster timeline / lower resource cost (${cost_b:,.0f} vs ${cost_a:,.0f})" if cost_b < cost_a else f"- Higher cost requirement (${cost_b:,.0f})",
            f"+ Lower risk score: {risk_b:.1f} vs {risk_a:.1f}" if risk_b < risk_a else f"- Higher risk score: {risk_b:.1f}",
            f"- Lower expected value (${ev_b:,.0f} vs ${ev_a:,.0f})"
        ]

        if eff_a > eff_b and risk_a <= risk_b:
            rec = f"Prioritize '{item_a.get('title')}' — superior resource efficiency ({eff_a:.2f} vs {eff_b:.2f}) and lower/equal risk."
        elif eff_b > eff_a and risk_b < risk_a:
            rec = f"Prioritize '{item_b.get('title')}' — better efficiency ({eff_b:.2f} vs {eff_a:.2f}) and lower risk."
        else:
            rec = f"Trade-off balanced: '{item_a.get('title')}' offers higher value but higher risk/resource demand."

        return {
            "option_a_id": item_a.get("id", item_a.get("mission_id", "A")),
            "option_a_title": item_a.get("title", "Option A"),
            "option_b_id": item_b.get("id", item_b.get("mission_id", "B")),
            "option_b_title": item_b.get("title", "Option B"),
            "prioritize_a_tradeoffs": tradeoffs_a,
            "prioritize_b_tradeoffs": tradeoffs_b,
            "expected_value_delta": ev_delta,
            "risk_delta": risk_delta,
            "resource_efficiency_delta": eff_delta,
            "recommendation": rec
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DO-NOTHING PORTFOLIO SIMULATOR (Requirement 8)
# ═══════════════════════════════════════════════════════════════════════════════

class DoNothingSimulationEngine:
    """
    Compares: CURRENT PORTFOLIO vs OPTIMIZED PORTFOLIO vs DO NOTHING.
    Side-effect free. No real DB mutations.
    """

    def simulate(
        self,
        portfolio_id: str,
        current_ev: float,
        optimized_ev: float,
        current_risk: float,
        optimized_risk: float,
        total_budget: float,
        allocated_budget: float,
        mission_count: int,
        completed_count: int
    ) -> Dict[str, Any]:
        # Current
        current_roi = round(((current_ev - allocated_budget) / max(1.0, allocated_budget)) * 100.0, 1) if allocated_budget > 0 else 0.0
        current_util = round((allocated_budget / max(1.0, total_budget)) * 100.0, 1) if total_budget > 0 else 0.0
        current_comp = round((completed_count / max(1, mission_count)) * 100.0, 1)

        # Optimized
        opt_budget = allocated_budget * 0.9  # efficiency gain
        opt_roi = round(((optimized_ev - opt_budget) / max(1.0, opt_budget)) * 100.0, 1) if opt_budget > 0 else 0.0
        opt_util = round((opt_budget / max(1.0, total_budget)) * 100.0, 1) if total_budget > 0 else 0.0

        # Do Nothing (baseline degradation: 25% value loss due to market drift, risk increases +15)
        dn_ev = round(current_ev * 0.75, 2)
        dn_risk = min(100.0, current_risk + 15.0)
        dn_roi = round(((dn_ev - allocated_budget) / max(1.0, allocated_budget)) * 100.0, 1) if allocated_budget > 0 else 0.0

        rec = (
            f"Optimized portfolio delivers +${optimized_ev - current_ev:,.0f} expected value uplift "
            f"and reduces risk from {current_risk:.1f} to {optimized_risk:.1f}. "
            f"Do-nothing baseline results in ~25% value erosion due to unaddressed market drift."
        )

        return {
            "portfolio_id": portfolio_id,
            "current": {
                "scenario_type": "CURRENT_PORTFOLIO",
                "expected_value": round(current_ev, 2),
                "expected_roi": current_roi,
                "risk_score": round(current_risk, 1),
                "resource_utilization_pct": current_util,
                "budget_utilization_pct": current_util,
                "mission_completion_rate": current_comp,
                "strategic_progress_pct": round(current_comp * 0.8, 1),
                "summary": f"Current portfolio: EV ${current_ev:,.0f}, ROI {current_roi:+.1f}%, Risk {current_risk:.1f}."
            },
            "optimized": {
                "scenario_type": "OPTIMIZED_PORTFOLIO",
                "expected_value": round(optimized_ev, 2),
                "expected_roi": opt_roi,
                "risk_score": round(optimized_risk, 1),
                "resource_utilization_pct": opt_util,
                "budget_utilization_pct": opt_util,
                "mission_completion_rate": min(100.0, current_comp + 15.0),
                "strategic_progress_pct": min(100.0, (current_comp + 15.0) * 0.9),
                "summary": f"Optimized portfolio: EV ${optimized_ev:,.0f}, ROI {opt_roi:+.1f}%, Risk {optimized_risk:.1f}."
            },
            "do_nothing": {
                "scenario_type": "DO_NOTHING",
                "expected_value": dn_ev,
                "expected_roi": dn_roi,
                "risk_score": dn_risk,
                "resource_utilization_pct": current_util,
                "budget_utilization_pct": current_util,
                "mission_completion_rate": current_comp * 0.7,
                "strategic_progress_pct": current_comp * 0.5,
                "summary": f"Do nothing trajectory: EV degraded to ${dn_ev:,.0f}, Risk increased to {dn_risk:.1f}."
            },
            "recommendation": rec,
            "is_side_effect_free": True
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO RECOMMENDATION ENGINE (Requirement 10)
# ═══════════════════════════════════════════════════════════════════════════════

class PortfolioRecommendationEngine:
    """
    Generates actionable recommendations:
    CONTINUE | ACCELERATE | MAINTAIN | DELAY | REDUCE | STOP | REVIEW.

    A STOP recommendation requires:
    - High risk (>= 75) OR low EV OR persistent failure OR severe resource inefficiency.
    All high-risk or STOP recommendations set requires_governance = True.
    """

    def generate_recommendation(
        self,
        title: str,
        expected_value: float,
        risk_score: float,
        success_probability: float,
        resource_efficiency: float,
        is_persistent_failure: bool = False,
        initiative_id: Optional[str] = None,
        mission_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # STOP criteria check
        if (
            risk_score >= 75.0 or
            expected_value <= 0.0 or
            is_persistent_failure or
            resource_efficiency < 5.0
        ):
            action = "STOP"
            reason = (
                f"STOP recommended for '{title}': "
                f"{'Persistent failure detected; ' if is_persistent_failure else ''}"
                f"{'High risk score (' + str(risk_score) + '); ' if risk_score >= 75.0 else ''}"
                f"{'Zero/negative expected value; ' if expected_value <= 0 else ''}"
                f"{'Severe resource inefficiency (' + str(resource_efficiency) + ').' if resource_efficiency < 5.0 else ''}"
            )
            req_gov = True
            risk_lvl = "CRITICAL" if risk_score >= 80 else "HIGH"

        elif success_probability >= 85.0 and resource_efficiency >= 50.0 and risk_score < 40.0:
            action = "ACCELERATE"
            reason = f"ACCELERATE '{title}': High probability of success ({success_probability:.0f}%), strong ROI efficiency, low risk ({risk_score:.1f})."
            req_gov = False
            risk_lvl = "LOW"

        elif risk_score >= 60.0 or success_probability < 60.0:
            action = "DELAY"
            reason = f"DELAY '{title}': Elevated risk ({risk_score:.1f}) or low success probability ({success_probability:.0f}%). Await clearer signals."
            req_gov = True
            risk_lvl = "HIGH"

        elif resource_efficiency < 20.0:
            action = "REDUCE"
            reason = f"REDUCE scope for '{title}': Resource efficiency is low ({resource_efficiency:.1f}). Scaling down recommended."
            req_gov = False
            risk_lvl = "MEDIUM"

        elif success_probability >= 70.0:
            action = "CONTINUE"
            reason = f"CONTINUE '{title}': Progressing within normal bounds with {success_probability:.0f}% probability."
            req_gov = False
            risk_lvl = "MEDIUM"

        else:
            action = "REVIEW"
            reason = f"REVIEW '{title}': Mixed signals (risk {risk_score:.1f}, efficiency {resource_efficiency:.1f}). Review recommended."
            req_gov = True
            risk_lvl = "MEDIUM"

        return {
            "title": f"{action}: {title}",
            "recommendation_type": action,
            "reason": reason,
            "expected_impact": f"Expected Value: ${expected_value:,.0f}, Risk: {risk_score:.1f}, Success Prob: {success_probability:.0f}%",
            "risk_level": risk_lvl,
            "requires_governance": req_gov,
            "initiative_id": initiative_id,
            "mission_id": mission_id
        }
