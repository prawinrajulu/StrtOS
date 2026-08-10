from typing import List, Dict, Any, Optional
from app.governance.models import RiskLevel, DecisionType

def calculate_decision_risk(
    ai_confidence_score: float = 95.0,
    evidence_count: int = 0,
    decision_type: DecisionType = DecisionType.WORKFLOW_EXECUTION,
    requested_budget: float = 0.0,
    is_reversible: bool = True,
    has_unavailable_evidence: bool = False,
    ai_status: str = "COMPLETED"
) -> Dict[str, Any]:
    """
    Calculates deterministic decision risk score (0-100) and RiskLevel classification.
    """
    score = 40.0
    reasons: List[str] = []

    # 1. AI Confidence Factor
    if ai_confidence_score >= 90.0:
        score -= 15.0
        reasons.append(f"High AI Confidence ({ai_confidence_score:.1f}%) reduces risk")
    elif ai_confidence_score < 70.0:
        score += 20.0
        reasons.append(f"Low AI Confidence ({ai_confidence_score:.1f}%) increases risk")
    if ai_confidence_score < 50.0:
        score += 15.0
        reasons.append("Unverified AI confidence score")

    # 2. Evidence Volume Factor
    if evidence_count >= 5:
        score -= 10.0
        reasons.append(f"Strong evidence verification ({evidence_count} items) lowers risk")
    elif evidence_count == 0:
        score += 15.0
        reasons.append("Zero verified evidence items attached")

    # 3. Action Reversibility
    if not is_reversible:
        score += 20.0
        reasons.append("Irreversible external decision action")
    else:
        reasons.append("Reversible workflow action")

    # 4. AI Execution Health Status
    if ai_status == "DEGRADED":
        score += 15.0
        reasons.append("Degraded AI agent execution state")
    elif ai_status == "UNAVAILABLE":
        score += 30.0
        reasons.append("Unavailable AI agent execution state")

    if has_unavailable_evidence:
        score += 10.0
        reasons.append("Partial tool execution failures detected")

    # 5. Decision Type & Financial Impact
    if decision_type == DecisionType.BUDGET_CHANGE:
        score += 15.0
        reasons.append("Financial budget reallocation request")
        if requested_budget > 10000.0:
            score += 15.0
            reasons.append(f"High financial budget threshold (${requested_budget:,.2f})")
    elif decision_type == DecisionType.CAMPAIGN_LAUNCH:
        score += 15.0
        reasons.append("Live multi-channel media campaign launch")
    elif decision_type == DecisionType.STRATEGY_CHANGE:
        score += 15.0
        reasons.append("Strategic positioning change request")

    # Final Score & Level Mapping
    final_score = max(0.0, min(100.0, round(score, 1)))

    if final_score <= 25.0:
        level = RiskLevel.LOW
    elif final_score <= 50.0:
        level = RiskLevel.MEDIUM
    elif final_score <= 75.0:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL

    return {
        "risk_level": level,
        "risk_score": final_score,
        "reasons": reasons
    }
