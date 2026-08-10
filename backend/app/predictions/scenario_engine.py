from typing import List, Dict, Any, Optional
from app.predictions.models import ScenarioType, PredictionStatus
from app.predictions.engine import (
    calculate_prediction_confidence, calculate_prediction_risk, calculate_prediction_range
)
from app.governance.models import RiskLevel

class ScenarioEngine:
    """
    Deterministic Scenario Engine generating Conservative, Balanced, and Aggressive
    decision simulations derived from evidence, historical memory, and budget inputs.
    """

    @staticmethod
    def generate_default_scenarios(
        metric_name: str = "ROAS",
        monthly_budget: float = 10000.0,
        timeline_days: int = 90,
        evidence_items: Optional[List[Dict[str, Any]]] = None,
        historical_memories: Optional[List[Dict[str, Any]]] = None,
        objective: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        evidence_list = evidence_items or []
        memory_list = historical_memories or []

        # Determine baseline ROAS from historical memory if available
        baseline_roas = 3.5
        past_actuals = []
        for mem in memory_list:
            struct = mem.get("structured_data", {})
            if "actual_value" in struct and isinstance(struct["actual_value"], (int, float)):
                past_actuals.append(float(struct["actual_value"]))

        if past_actuals:
            baseline_roas = round(sum(past_actuals) / len(past_actuals), 2)

        evidence_count = len(evidence_list)
        memory_count = len(memory_list)
        evidence_conf = 90.0 if evidence_count >= 3 else 75.0

        conf_score = calculate_prediction_confidence(
            evidence_confidence=evidence_conf,
            evidence_count=evidence_count,
            memory_count=memory_count,
            historical_success_rate=0.85
        )

        scenarios = []

        # 1. CONSERVATIVE SCENARIO
        cons_budget = monthly_budget * 0.75
        cons_pred = round(baseline_roas * 0.88, 2)
        _, cons_low, cons_high = calculate_prediction_range(cons_pred, uncertainty_pct=10.0)
        cons_risk_score, cons_risk_lvl = calculate_prediction_risk(
            ScenarioType.CONSERVATIVE, cons_pred, conf_score, budget=cons_budget
        )

        scenarios.append({
            "scenario_type": ScenarioType.CONSERVATIVE,
            "scenario_name": "Conservative Efficiency Scenario",
            "objective": objective or "Maximize cost efficiency & lower budget risk",
            "metric_name": metric_name,
            "predicted_value": cons_pred,
            "lower_bound": cons_low,
            "upper_bound": cons_high,
            "unit": "x",
            "currency": "USD",
            "confidence_score": min(98.0, conf_score + 5.0),
            "risk_score": cons_risk_score,
            "risk_level": cons_risk_lvl,
            "evidence_count": evidence_count,
            "memory_count": memory_count,
            "assumptions": [
                f"Reduced monthly budget exposure (${cons_budget:,.0f}/mo)",
                "Focus on proven high-intent search acquisition channels",
                "Conservative performance floor to protect ROI margin"
            ],
            "evidence_references": evidence_list,
            "memory_references": memory_list,
            "prediction_status": PredictionStatus.GENERATED
        })

        # 2. BALANCED SCENARIO
        bal_budget = monthly_budget * 1.0
        bal_pred = round(baseline_roas * 1.0, 2)
        _, bal_low, bal_high = calculate_prediction_range(bal_pred, uncertainty_pct=15.0)
        bal_risk_score, bal_risk_lvl = calculate_prediction_risk(
            ScenarioType.BALANCED, bal_pred, conf_score, budget=bal_budget
        )

        scenarios.append({
            "scenario_type": ScenarioType.BALANCED,
            "scenario_name": "Balanced Growth Scenario",
            "objective": objective or "Optimize acquisition scale & predictable ROI",
            "metric_name": metric_name,
            "predicted_value": bal_pred,
            "lower_bound": bal_low,
            "upper_bound": bal_high,
            "unit": "x",
            "currency": "USD",
            "confidence_score": conf_score,
            "risk_score": bal_risk_score,
            "risk_level": bal_risk_lvl,
            "evidence_count": evidence_count,
            "memory_count": memory_count,
            "assumptions": [
                f"Standard monthly budget allocation (${bal_budget:,.0f}/mo)",
                "Omnichannel distribution across search, social, and SEO",
                "Balanced risk-reward profile calibrated to historical trends"
            ],
            "evidence_references": evidence_list,
            "memory_references": memory_list,
            "prediction_status": PredictionStatus.GENERATED
        })

        # 3. AGGRESSIVE SCENARIO
        agg_budget = monthly_budget * 1.4
        agg_pred = round(baseline_roas * 1.22, 2)
        _, agg_low, agg_high = calculate_prediction_range(agg_pred, uncertainty_pct=25.0)
        agg_risk_score, agg_risk_lvl = calculate_prediction_risk(
            ScenarioType.AGGRESSIVE, agg_pred, conf_score - 10.0, budget=agg_budget
        )

        scenarios.append({
            "scenario_type": ScenarioType.AGGRESSIVE,
            "scenario_name": "Aggressive Market Scaling Scenario",
            "objective": objective or "Maximize market share & aggressive customer capture",
            "metric_name": metric_name,
            "predicted_value": agg_pred,
            "lower_bound": agg_low,
            "upper_bound": agg_high,
            "unit": "x",
            "currency": "USD",
            "confidence_score": max(50.0, conf_score - 10.0),
            "risk_score": agg_risk_score,
            "risk_level": agg_risk_lvl,
            "evidence_count": evidence_count,
            "memory_count": memory_count,
            "assumptions": [
                f"Expanded monthly budget allocation (${agg_budget:,.0f}/mo)",
                "Multi-channel scaling into higher-funnel paid media flighting",
                "Higher upside variance with increased ad frequency"
            ],
            "evidence_references": evidence_list,
            "memory_references": memory_list,
            "prediction_status": PredictionStatus.GENERATED
        })

        return scenarios
