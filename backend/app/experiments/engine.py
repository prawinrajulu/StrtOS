import math
from typing import Dict, Any, List, Optional
from app.experiments.models import ExperimentResult, VariantType

class ExperimentDesignEngine:
    """
    Determines experiment parameters, sample size requirements, and risk level deterministically.
    """
    @staticmethod
    def calculate_required_sample_size(baseline_value: float, min_detectable_effect: float, confidence_threshold: float = 95.0) -> int:
        """
        Calculates minimum required sample size per variant using standard sample size estimation rules.
        """
        p = max(0.01, min(0.99, baseline_value / 100.0 if baseline_value > 1.0 else baseline_value))
        delta = max(0.01, min_detectable_effect / 100.0 if min_detectable_effect > 1.0 else min_detectable_effect)
        
        # Z-scores for 95% confidence (1.96) and 80% power (0.84)
        z_alpha = 1.96 if confidence_threshold >= 95.0 else 1.645
        z_beta = 0.84
        
        variance = 2 * p * (1 - p)
        sample_size = math.ceil((variance * ((z_alpha + z_beta) ** 2)) / (delta ** 2))
        return max(20, min(sample_size, 1000))

    @staticmethod
    def design_experiment(
        baseline_policy_config: Dict[str, Any],
        variant_policy_config: Dict[str, Any],
        baseline_kpi: float,
        target_kpi: float,
        min_detectable_effect: float = 5.0,
        available_sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Designs experiment control vs variant, assesses risk bounds, and determines feasibility.
        """
        required_sample = ExperimentDesignEngine.calculate_required_sample_size(baseline_kpi, min_detectable_effect)
        
        # Calculate policy delta
        delta_max = 0.0
        for k in variant_policy_config:
            if k in baseline_policy_config and isinstance(baseline_policy_config[k], (int, float)) and isinstance(variant_policy_config[k], (int, float)):
                base = float(baseline_policy_config[k])
                var = float(variant_policy_config[k])
                if base > 0:
                    diff = abs(var - base) / base * 100.0
                    if diff > delta_max:
                        delta_max = diff
        
        # Risk assessment: Maximum policy change <= 10%
        requires_governance = delta_max > 10.0 or target_kpi > baseline_kpi * 1.2
        is_feasible = available_sample_size >= (required_sample * 2)

        return {
            "required_sample_size_per_variant": required_sample,
            "total_sample_size_needed": required_sample * 2,
            "available_sample_size": available_sample_size,
            "is_feasible": is_feasible,
            "max_policy_delta_percent": round(delta_max, 2),
            "requires_governance": requires_governance,
            "risk_level": "HIGH" if requires_governance else "LOW",
            "expected_impact_percent": round(max(0.0, ((target_kpi - baseline_kpi) / baseline_kpi * 100.0) if baseline_kpi > 0 else 5.0), 2)
        }


class ExperimentEvaluator:
    """
    Evaluates experiment control vs variant performance and determines statistical significance.
    """
    @staticmethod
    def evaluate(
        control_measurements: List[float],
        variant_measurements: List[float],
        min_detectable_effect: float = 5.0,
        confidence_threshold: float = 95.0,
        min_sample_size: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluates control vs variant measurements deterministically.
        Returns INSUFFICIENT_DATA if minimum sample size is not met.
        """
        n_c = len(control_measurements)
        n_v = len(variant_measurements)

        if n_c < min_sample_size or n_v < min_sample_size:
            return {
                "result": ExperimentResult.INCONCLUSIVE,
                "winner": None,
                "confidence": 0.0,
                "statistically_significant": False,
                "control_sample_size": n_c,
                "variant_sample_size": n_v,
                "control_mean": sum(control_measurements) / n_c if n_c > 0 else 0.0,
                "variant_mean": sum(variant_measurements) / n_v if n_v > 0 else 0.0,
                "absolute_difference": 0.0,
                "percentage_improvement": 0.0,
                "reason": f"Insufficient sample size (Control: {n_c}/{min_sample_size}, Variant: {n_v}/{min_sample_size})"
            }

        mean_c = sum(control_measurements) / n_c
        mean_v = sum(variant_measurements) / n_v

        var_c = sum((x - mean_c) ** 2 for x in control_measurements) / max(1, n_c - 1)
        var_v = sum((x - mean_v) ** 2 for x in variant_measurements) / max(1, n_v - 1)

        abs_diff = mean_v - mean_c
        pct_imp = (abs_diff / mean_c * 100.0) if mean_c != 0 else 0.0

        # Welch's t-statistic calculation
        se = math.sqrt((var_c / n_c) + (var_v / n_v)) if (var_c + var_v) > 0 else 0.0001
        t_stat = abs_diff / se if se > 0 else 0.0

        # Deterministic confidence mapping based on t-stat
        if t_stat >= 1.96:
            calc_conf = 95.0 + min(4.9, (t_stat - 1.96) * 2.0)
        elif t_stat >= 1.645:
            calc_conf = 90.0 + (t_stat - 1.645) * 15.0
        else:
            calc_conf = min(89.9, t_stat * 50.0)

        is_significant = calc_conf >= confidence_threshold and abs(pct_imp) >= min_detectable_effect

        if is_significant and pct_imp > 0:
            res = ExperimentResult.WIN
            winner = VariantType.VARIANT_A
        elif is_significant and pct_imp < 0:
            res = ExperimentResult.LOSS
            winner = VariantType.CONTROL
        elif not is_significant and (n_c + n_v) >= (min_sample_size * 2):
            res = ExperimentResult.NEUTRAL
            winner = None
        else:
            res = ExperimentResult.INCONCLUSIVE
            winner = None

        return {
            "result": res,
            "winner": winner,
            "confidence": round(calc_conf, 2),
            "statistically_significant": is_significant,
            "control_sample_size": n_c,
            "variant_sample_size": n_v,
            "control_mean": round(mean_c, 2),
            "variant_mean": round(mean_v, 2),
            "absolute_difference": round(abs_diff, 2),
            "percentage_improvement": round(pct_imp, 2),
            "reason": f"Evaluated {n_c} control and {n_v} variant measurements with {calc_conf:.1f}% confidence."
        }
