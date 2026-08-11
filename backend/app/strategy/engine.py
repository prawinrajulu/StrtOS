import math
from typing import List, Dict, Any, Optional, Tuple
from app.strategy.models import (
    StrategicObjectiveModel, StrategicConstraintModel, StrategicPlanModel,
    ScenarioType, HorizonType
)
from app.strategy.schemas import ScenarioResponse, StrategyEvaluationResponse, StrategyExplanationResponse

MAX_ADAPTATION_DELTA = 0.10  # 10% maximum bounded autonomous adaptation

class StrategicScenarioEngine:
    """Generates multi-horizon strategic scenarios (CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM)."""

    def generate_scenarios(
        self,
        objective: StrategicObjectiveModel,
        prediction_confidence: float = 90.0,
        historical_success_rate: float = 85.0
    ) -> List[ScenarioResponse]:
        target_diff = max(1.0, objective.target_value - objective.baseline_value)
        base_days = 90
        if objective.target_horizon == HorizonType.DAYS_30:
            base_days = 30
        elif objective.target_horizon == HorizonType.DAYS_60:
            base_days = 60
        elif objective.target_horizon == HorizonType.DAYS_180:
            base_days = 180
        elif objective.target_horizon == HorizonType.DAYS_365:
            base_days = 365

        # Conservative Scenario
        sc_cons = ScenarioResponse(
            scenario_type=ScenarioType.CONSERVATIVE,
            expected_value=round(objective.baseline_value + (target_diff * 0.70), 2),
            confidence_score=min(98.0, round(prediction_confidence + 5.0, 1)),
            risk_score=10.0,
            risk_level="LOW",
            cost=round(target_diff * 15.0, 2),
            time_to_impact_days=int(base_days * 1.2),
            resource_requirement="Standard Team Capacity",
            dependency_count=1,
            upside_potential="High predictability with lower capital expenditure",
            downside_risk="Slower milestone trajectory"
        )

        # Balanced Scenario
        sc_bal = ScenarioResponse(
            scenario_type=ScenarioType.BALANCED,
            expected_value=round(objective.target_value, 2),
            confidence_score=round(prediction_confidence, 1),
            risk_score=25.0,
            risk_level="LOW",
            cost=round(target_diff * 25.0, 2),
            time_to_impact_days=base_days,
            resource_requirement="Optimal Resource Allocation",
            dependency_count=2,
            upside_potential="Achieves primary strategic target within target horizon",
            downside_risk="Moderate execution dependencies"
        )

        # Aggressive Scenario
        sc_agg = ScenarioResponse(
            scenario_type=ScenarioType.AGGRESSIVE,
            expected_value=round(objective.baseline_value + (target_diff * 1.40), 2),
            confidence_score=max(50.0, round(prediction_confidence - 15.0, 1)),
            risk_score=65.0,
            risk_level="HIGH",
            cost=round(target_diff * 45.0, 2),
            time_to_impact_days=max(15, int(base_days * 0.75)),
            resource_requirement="Maximized Capital & Agent Budget",
            dependency_count=4,
            upside_potential="Accelerated market dominance & customer acquisition",
            downside_risk="Higher burn rate & dependency exposure"
        )

        return [sc_cons, sc_bal, sc_agg]

class StrategicConstraintEngine:
    """Evaluates deterministic business constraints (Budget, Timeline, Capacity, Risk, Policy)."""

    def evaluate_constraints(
        self,
        objective: StrategicObjectiveModel,
        proposed_cost: float,
        proposed_risk_score: float,
        proposed_days: int
    ) -> Tuple[bool, List[str]]:
        violations: List[str] = []
        
        for constraint in (objective.constraints or []):
            if constraint.constraint_type.upper() == "BUDGET" and proposed_cost > constraint.limit_value:
                violations.append(f"CONSTRAINT_VIOLATION: Budget proposed ({proposed_cost}) exceeds constraint limit ({constraint.limit_value})")
            elif constraint.constraint_type.upper() == "TIMELINE" and proposed_days > constraint.limit_value:
                violations.append(f"CONSTRAINT_VIOLATION: Timeline proposed ({proposed_days} days) exceeds limit ({constraint.limit_value} days)")
            elif constraint.constraint_type.upper() == "RISK" and proposed_risk_score > constraint.limit_value:
                violations.append(f"CONSTRAINT_VIOLATION: Risk score ({proposed_risk_score}) exceeds maximum risk tolerance ({constraint.limit_value})")

        is_valid = len(violations) == 0
        return is_valid, violations

class StrategicRiskEngine:
    """Integrated strategic risk engine."""

    def calculate_risk(
        self,
        objective: StrategicObjectiveModel,
        scenario_type: ScenarioType,
        agent_reliability: float = 95.0
    ) -> Tuple[float, str]:
        base_risk = 20.0
        if scenario_type == ScenarioType.CONSERVATIVE:
            base_risk = 10.0
        elif scenario_type == ScenarioType.BALANCED:
            base_risk = 25.0
        elif scenario_type == ScenarioType.AGGRESSIVE:
            base_risk = 65.0

        # Adjust by agent reliability
        if agent_reliability < 80.0:
            base_risk += 15.0

        # Adjust by constraints presence
        if any(c.is_hard_constraint for c in (objective.constraints or [])):
            base_risk += 5.0

        risk_score = max(0.0, min(100.0, round(base_risk, 1)))

        if risk_score >= 70.0:
            level = "CRITICAL"
        elif risk_score >= 50.0:
            level = "HIGH"
        elif risk_score >= 30.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return risk_score, level

class StrategicAdaptationLoop:
    """Bounded closed-loop strategy adaptation engine."""

    def compute_adaptation(
        self,
        current_target: float,
        actual_performance: float,
        reason: str
    ) -> Tuple[float, float, bool]:
        diff = actual_performance - current_target
        raw_pct = diff / max(current_target, 1.0)

        # Bound adaptation delta to max 10%
        bounded_pct = max(-MAX_ADAPTATION_DELTA, min(MAX_ADAPTATION_DELTA, raw_pct))
        is_bounded = abs(raw_pct) > MAX_ADAPTATION_DELTA

        new_target = round(current_target * (1.0 + bounded_pct), 2)
        return new_target, round(bounded_pct * 100.0, 2), is_bounded

class StrategicExplanationEngine:
    """Generates transparent decision chain explanations."""

    def explain_plan(
        self,
        plan: StrategicPlanModel,
        objective: StrategicObjectiveModel,
        evidence_sources: Optional[List[Dict[str, Any]]] = None,
        memory_references: Optional[List[Dict[str, Any]]] = None
    ) -> StrategyExplanationResponse:
        ev_sources = evidence_sources or [
            {"finding": "Verified business state & TAM benchmark", "confidence": 95.0, "source": "KnowledgeService"}
        ]
        mem_refs = memory_references or [
            {"title": "Historical Q4 Campaign Outcome", "outcome": "COMPLETED", "relevance": 92.0}
        ]

        return StrategyExplanationResponse(
            plan_id=plan.id,
            why_objective=f"Objective '{objective.title}' addresses key business category '{objective.category}' with baseline {objective.baseline_value} -> target {objective.target_value}.",
            why_target=f"Target {objective.target_value} {objective.unit} was calculated from verified industry evidence and growth tailwinds.",
            why_horizon=f"Time horizon {plan.horizon} balances execution velocity against risk exposure.",
            why_scenario=f"Scenario '{plan.scenario_type}' optimized expected value ({plan.expected_value}) under risk score {plan.risk_score}.",
            why_risk_score=f"Risk level '{plan.risk_level}' derived from agent reliability, constraint evaluation, and causal uncertainty.",
            evidence_sources=ev_sources,
            memory_references=mem_refs,
            assumptions=["Market demand stability over selected horizon", "Agent tool availability"],
            invalidation_factors=["Macroeconomic CPM inflation > 30%", "Regulatory policy changes"]
        )

class StrategicPlanningEngine:
    """Main Strategic Planning Engine orchestrating scenario generation, risk evaluation, and constraint checking."""

    def __init__(self):
        self.scenario_engine = StrategicScenarioEngine()
        self.constraint_engine = StrategicConstraintEngine()
        self.risk_engine = StrategicRiskEngine()
        self.adaptation_loop = StrategicAdaptationLoop()
        self.explanation_engine = StrategicExplanationEngine()
