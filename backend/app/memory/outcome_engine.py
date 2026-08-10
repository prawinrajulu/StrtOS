from typing import Dict, Any, Tuple
from app.memory.models import OutcomeStatus

def evaluate_outcome_variance(
    predicted_value: float,
    actual_value: float,
    metric_name: str = "ROAS",
    unit: str = "x"
) -> Dict[str, Any]:
    """
    Evaluates variance between PREDICTED vs ACTUAL performance metrics deterministically.
    
    Thresholds:
    - Within ±10%: SUCCESS
    - 10% – 30%: PARTIAL
    - > 30%: FAILED
    """
    abs_var = round(abs(actual_value - predicted_value), 2)
    
    if abs(predicted_value) > 1e-6:
        pct_var = round((abs_var / abs(predicted_value)) * 100.0, 1)
    else:
        pct_var = 0.0

    if pct_var <= 10.0:
        status = OutcomeStatus.SUCCESS
        summary = f"{metric_name} achieved prediction within optimal range ({actual_value}{unit} actual vs {predicted_value}{unit} predicted, {pct_var}% variance)."
    elif pct_var <= 30.0:
        status = OutcomeStatus.PARTIAL
        summary = f"{metric_name} experienced moderate performance variance ({actual_value}{unit} actual vs {predicted_value}{unit} predicted, {pct_var}% variance)."
    else:
        status = OutcomeStatus.FAILED
        summary = f"{metric_name} significantly deviated from historical prediction ({actual_value}{unit} actual vs {predicted_value}{unit} predicted, {pct_var}% variance)."

    return {
        "outcome_status": status,
        "absolute_variance": abs_var,
        "percentage_variance": pct_var,
        "lesson_summary": summary
    }

def extract_deterministic_lesson(
    metric_name: str,
    predicted_value: float,
    actual_value: float,
    unit: str,
    outcome_status: OutcomeStatus,
    pct_var: float
) -> str:
    """
    Extracts a non-fabricated, evidence-grounded lesson based on deterministic stored outcomes.
    """
    if outcome_status == OutcomeStatus.SUCCESS:
        return f"Historical strategy model for {metric_name} demonstrated high calibration accuracy ({pct_var}% variance)."
    elif outcome_status == OutcomeStatus.PARTIAL:
        direction = "exceeded" if actual_value > predicted_value else "trailed"
        return f"Previous {metric_name} forecast {direction} actual performance by {pct_var}%. Recommendation parameters require moderate adjustment."
    else:
        direction = "exceeded" if actual_value > predicted_value else "overestimated"
        return f"Previous {metric_name} forecast {direction} actual results by {pct_var}%. Calibration penalty applied to future strategy scoring."
