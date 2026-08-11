"""
Portfolio Optimization Engine.

Goal: MAXIMIZE EXPECTED BUSINESS VALUE subject to budget, capacity, timeline,
      risk, policy, and governance constraints.

Algorithm: Deterministic greedy knapsack sorted by value/cost ratio.
All calculations reproducible — no randomness.
"""
from typing import List, Dict, Any, Tuple
from app.portfolio.schemas import (
    MissionOptimizationResult, OptimizationResponse, ScenarioResult, SimulationResponse
)


SCENARIO_CAPACITY_FACTORS = {
    "CONSERVATIVE": 0.60,
    "BALANCED": 0.80,
    "AGGRESSIVE": 1.00,
    "CUSTOM": 1.00,
}

SCENARIO_RISK_MULTIPLIERS = {
    "CONSERVATIVE": 0.70,
    "BALANCED": 1.00,
    "AGGRESSIVE": 1.40,
    "CUSTOM": 1.00,
}


class PortfolioOptimizationEngine:
    """
    Greedy knapsack portfolio optimizer.

    Input:
      - missions: list of dicts with keys:
          mission_id, title, priority_score, expected_value,
          success_probability, resource_requirement, risk_score, status
      - total_budget: float
      - total_capacity: float (agent/execution capacity units)
      - scenario_type: CONSERVATIVE | BALANCED | AGGRESSIVE | CUSTOM
      - budget_delta_pct: float (what-if % change to budget)
      - capacity_delta_pct: float (what-if % change to capacity)

    Output:
      OptimizationResponse with selected/deferred/paused lists + explanation
    """

    def optimize(
        self,
        portfolio_id: str,
        missions: List[Dict[str, Any]],
        total_budget: float,
        total_capacity: float = 100.0,
        scenario_type: str = "BALANCED",
        budget_delta_pct: float = 0.0,
        capacity_delta_pct: float = 0.0
    ) -> OptimizationResponse:
        cap_factor = SCENARIO_CAPACITY_FACTORS.get(scenario_type, 0.80)
        risk_mult = SCENARIO_RISK_MULTIPLIERS.get(scenario_type, 1.00)

        # Apply what-if adjustments
        effective_budget = total_budget * (1.0 + budget_delta_pct / 100.0) * cap_factor
        effective_capacity = total_capacity * (1.0 + capacity_delta_pct / 100.0) * cap_factor

        # Sort by value/cost ratio (deterministic — no random tiebreaking)
        def sort_key(m: Dict) -> float:
            cost = max(1.0, m.get("resource_requirement", 1.0))
            ev = m.get("expected_value", 0.0)
            sp = m.get("success_probability", 80.0) / 100.0
            return round((ev * sp) / cost, 4)

        sorted_missions = sorted(missions, key=sort_key, reverse=True)

        selected: List[MissionOptimizationResult] = []
        deferred: List[MissionOptimizationResult] = []
        paused: List[MissionOptimizationResult] = []

        used_budget = 0.0
        used_capacity = 0.0
        total_value = 0.0
        total_risk = 0.0

        for m in sorted_missions:
            cost = m.get("resource_requirement", 0.0)
            ev = m.get("expected_value", 0.0)
            sp = m.get("success_probability", 80.0)
            risk = m.get("risk_score", 20.0) * risk_mult
            vcr = round((ev * sp / 100.0) / max(1.0, cost), 4)

            current_status = m.get("status", "ACTIVE")

            # Paused missions are passed through as paused
            if current_status in ("PAUSED", "FAILED", "CANCELLED"):
                paused.append(MissionOptimizationResult(
                    mission_id=m["mission_id"],
                    title=m.get("title", "Unknown Mission"),
                    priority_score=m.get("priority_score", 50.0),
                    expected_value=ev,
                    success_probability=sp,
                    resource_requirement=cost,
                    value_cost_ratio=vcr,
                    status="PAUSED",
                    reason=f"Mission currently {current_status} — excluded from optimization."
                ))
                continue

            # Budget and capacity check
            budget_ok = (used_budget + cost) <= effective_budget or effective_budget <= 0
            capacity_ok = (used_capacity + 1.0) <= effective_capacity or effective_capacity <= 0

            if budget_ok and capacity_ok:
                used_budget += cost
                used_capacity += 1.0
                total_value += ev * (sp / 100.0)
                total_risk += risk
                selected.append(MissionOptimizationResult(
                    mission_id=m["mission_id"],
                    title=m.get("title", "Unknown Mission"),
                    priority_score=m.get("priority_score", 50.0),
                    expected_value=ev,
                    success_probability=sp,
                    resource_requirement=cost,
                    value_cost_ratio=vcr,
                    status="SELECTED",
                    reason=(
                        f"Selected: value/cost ratio {vcr:.2f}, "
                        f"expected value {ev:,.0f} at {sp:.0f}% probability. "
                        f"Budget used: {used_budget:,.0f}/{effective_budget:,.0f}."
                    )
                ))
            else:
                reason_parts = []
                if not budget_ok:
                    reason_parts.append(
                        f"budget insufficient ({used_budget:,.0f} used + {cost:,.0f} required > {effective_budget:,.0f} available)"
                    )
                if not capacity_ok:
                    reason_parts.append(
                        f"capacity exhausted ({used_capacity:.0f} active missions at limit {effective_capacity:.0f})"
                    )
                deferred.append(MissionOptimizationResult(
                    mission_id=m["mission_id"],
                    title=m.get("title", "Unknown Mission"),
                    priority_score=m.get("priority_score", 50.0),
                    expected_value=ev,
                    success_probability=sp,
                    resource_requirement=cost,
                    value_cost_ratio=vcr,
                    status="DEFERRED",
                    reason=f"Deferred: {'; '.join(reason_parts)}."
                ))

        # Aggregate portfolio risk
        n = len(selected)
        portfolio_risk = round(total_risk / max(1, n), 1)
        portfolio_risk = min(100.0, portfolio_risk)

        # Confidence: higher when more missions selected and risk is low
        confidence = round(
            min(95.0, 70.0 + (n * 3.0) - (portfolio_risk * 0.3)),
            1
        )

        budget_util = round((used_budget / max(1.0, effective_budget)) * 100.0, 1)
        capacity_util = round((used_capacity / max(1.0, effective_capacity)) * 100.0, 1)

        explanation = (
            f"Scenario: {scenario_type} (capacity factor {cap_factor*100:.0f}%). "
            f"Selected {len(selected)} missions with expected portfolio value "
            f"{total_value:,.0f}. Deferred {len(deferred)} missions due to resource constraints. "
            f"Budget utilization: {budget_util}%, capacity: {capacity_util}%."
        )

        return OptimizationResponse(
            portfolio_id=portfolio_id,
            scenario_type=scenario_type,
            selected_missions=selected,
            deferred_missions=deferred,
            paused_missions=paused,
            expected_portfolio_value=round(total_value, 2),
            portfolio_risk_score=portfolio_risk,
            confidence=confidence,
            budget_utilization_pct=budget_util,
            capacity_utilization_pct=capacity_util,
            explanation=explanation
        )

    def simulate_all_scenarios(
        self,
        portfolio_id: str,
        missions: List[Dict[str, Any]],
        total_budget: float,
        total_capacity: float = 100.0,
        budget_delta_pct: float = 0.0,
        capacity_delta_pct: float = 0.0
    ) -> SimulationResponse:
        results: List[ScenarioResult] = []

        for scenario in ["CONSERVATIVE", "BALANCED", "AGGRESSIVE"]:
            opt = self.optimize(
                portfolio_id=portfolio_id,
                missions=missions,
                total_budget=total_budget,
                total_capacity=total_capacity,
                scenario_type=scenario,
                budget_delta_pct=budget_delta_pct,
                capacity_delta_pct=capacity_delta_pct
            )
            results.append(ScenarioResult(
                scenario_type=scenario,
                expected_value=opt.expected_portfolio_value,
                risk_score=opt.portfolio_risk_score,
                budget_utilization_pct=opt.budget_utilization_pct,
                capacity_utilization_pct=opt.capacity_utilization_pct,
                selected_mission_count=len(opt.selected_missions),
                deferred_mission_count=len(opt.deferred_missions),
                confidence=opt.confidence
            ))

        # Recommend balanced unless risk is low enough for aggressive
        balanced = next(r for r in results if r.scenario_type == "BALANCED")
        aggressive = next(r for r in results if r.scenario_type == "AGGRESSIVE")

        if aggressive.risk_score < 50.0 and aggressive.expected_value > balanced.expected_value * 1.2:
            recommendation = "AGGRESSIVE scenario recommended — risk is acceptable and value uplift is significant."
        elif balanced.risk_score <= 60.0:
            recommendation = "BALANCED scenario recommended — optimal value-risk trade-off."
        else:
            recommendation = "CONSERVATIVE scenario recommended — risk levels are elevated."

        return SimulationResponse(
            portfolio_id=portfolio_id,
            scenarios=results,
            recommendation=recommendation
        )
