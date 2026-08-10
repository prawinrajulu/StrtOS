from typing import Dict, Any, Optional

def evaluate_prediction_accuracy(
    predicted_value: float,
    actual_value: float,
    metric_name: str = "ROAS",
    unit: str = "x"
) -> Dict[str, Any]:
    """
    Evaluates prediction accuracy deterministically comparing predicted vs actual values.
    """
    abs_err = round(abs(actual_value - predicted_value), 2)
    
    if abs(predicted_value) > 1e-6:
        pct_err = round((abs_err / abs(predicted_value)) * 100.0, 1)
    else:
        pct_err = 0.0

    acc_score = round(max(0.0, min(100.0, 100.0 - pct_err)), 1)

    if pct_err <= 10.0:
        status = "HIGH_ACCURACY"
        lesson = f"Prediction model for {metric_name} demonstrated high calibration accuracy ({acc_score}% accuracy, {pct_err}% error)."
    elif pct_err <= 25.0:
        status = "MODERATE_ACCURACY"
        lesson = f"Prediction model for {metric_name} achieved moderate accuracy ({acc_score}% accuracy, {pct_err}% error)."
    else:
        status = "CALIBRATION_REQUIRED"
        lesson = f"Prediction model for {metric_name} required variance calibration ({pct_err}% error)."

    return {
        "absolute_error": abs_err,
        "percentage_error": pct_err,
        "accuracy_score": acc_score,
        "accuracy_status": status,
        "lesson_summary": lesson
    }
