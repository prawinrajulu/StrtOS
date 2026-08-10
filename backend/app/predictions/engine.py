from typing import Dict, Any, List, Optional, Tuple
from app.governance.models import RiskLevel
from app.predictions.models import ScenarioType, PredictionStatus

def calculate_prediction_confidence(
    evidence_confidence: float = 90.0,
    evidence_count: int = 0,
    memory_count: int = 0,
    historical_success_rate: float = 0.8
) -> float:
    """
    Calculates overall Prediction Confidence Score (0-100).
    Differs from Evidence Confidence by factoring in memory depth and historical outcome consistency.
    """
    base_conf = evidence_confidence * 0.5
    
    # Evidence Volume Contribution (max +20 pts)
    evidence_contrib = min(20.0, evidence_count * 4.0)
    
    # Historical Memory Depth (max +15 pts)
    memory_contrib = min(15.0, memory_count * 3.0)
    
    # Historical Consistency Factor (max +15 pts)
    consistency_contrib = historical_success_rate * 15.0

    total = round(base_conf + evidence_contrib + memory_contrib + consistency_contrib, 1)
    return max(10.0, min(100.0, total))

def calculate_prediction_risk(
    scenario_type: ScenarioType,
    predicted_value: float,
    confidence_score: float,
    budget: float = 10000.0,
    is_reversible: bool = True
) -> Tuple[float, RiskLevel]:
    """
    Calculates Prediction Risk Score (0-100) and maps to RiskLevel.
    """
    score = 40.0

    # Scenario Type Baseline
    if scenario_type == ScenarioType.CONSERVATIVE:
        score -= 15.0
    elif scenario_type == ScenarioType.AGGRESSIVE:
        score += 20.0
    elif scenario_type == ScenarioType.CUSTOM:
        score += 10.0

    # Confidence Adjustment
    if confidence_score >= 85.0:
        score -= 10.0
    elif confidence_score < 65.0:
        score += 20.0

    # Budget Exposure Adjustment
    if budget > 25000.0:
        score += 15.0
    elif budget > 10000.0:
        score += 10.0

    if not is_reversible:
        score += 15.0

    final_score = max(0.0, min(100.0, round(score, 1)))

    if final_score <= 25.0:
        level = RiskLevel.LOW
    elif final_score <= 50.0:
        level = RiskLevel.MEDIUM
    elif final_score <= 75.0:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL

    return final_score, level

def calculate_prediction_range(
    predicted_value: float,
    uncertainty_pct: float = 15.0
) -> Tuple[float, float, float]:
    """
    Calculates deterministic upper and lower bounds for predictions.
    """
    pred = round(predicted_value, 2)
    margin = round(pred * (uncertainty_pct / 100.0), 2)
    lower = round(max(0.0, pred - margin), 2)
    upper = round(pred + margin, 2)
    return pred, lower, upper
