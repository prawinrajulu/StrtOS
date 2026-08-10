from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.evidence.models import EvidenceItem

SOURCE_TYPE_WEIGHTS = {
    "database": 1.0,
    "api": 0.95,
    "website": 0.85,
    "search": 0.70,
    "llm": 0.50,
    "assumption": 0.30,
    "unavailable": 0.0,
}

def calculate_confidence(
    evidence_items: List[EvidenceItem],
    llm_status: str = "SUCCESS",
    has_unavailable_tools: bool = False
) -> float:
    """
    Calculates a deterministic confidence score (0.0 to 100.0) based on collected evidence items.
    
    Priority:
    database / api > website > search > llm > assumption > unavailable
    """
    if not evidence_items:
        if llm_status == "SUCCESS":
            return 40.0
        return 0.0

    total_weight = 0.0
    weighted_score_sum = 0.0
    distinct_sources = set()
    unavailable_count = 0
    now_utc = datetime.now(timezone.utc)

    for item in evidence_items:
        stype = item.source_type if item.source_type in SOURCE_TYPE_WEIGHTS else "llm"
        weight = SOURCE_TYPE_WEIGHTS[stype]
        
        if stype == "unavailable":
            unavailable_count += 1
            continue

        distinct_sources.add(item.source)
        
        # Individual evidence item confidence (0-100)
        item_conf = max(0.0, min(100.0, item.confidence))
        
        # Freshness penalty if timestamp > 30 days old
        freshness_factor = 1.0
        if item.timestamp:
            try:
                dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
                days_old = (now_utc - dt).days
                if days_old > 30:
                    freshness_factor = 0.9
            except Exception:
                pass

        weighted_score_sum += item_conf * weight * freshness_factor
        total_weight += weight

    if total_weight == 0.0:
        base_score = 0.0 if unavailable_count > 0 else 30.0
    else:
        base_score = weighted_score_sum / total_weight

    # Corroboration boost for multiple independent valid sources
    corroboration_boost = 0.0
    if len(distinct_sources) >= 3:
        corroboration_boost = 10.0
    elif len(distinct_sources) == 2:
        corroboration_boost = 5.0

    # Unavailable tools penalty
    penalty = 0.0
    if has_unavailable_tools or unavailable_count > 0:
        penalty += (10.0 * max(1, unavailable_count))

    if llm_status != "SUCCESS":
        penalty += 20.0

    final_score = base_score + corroboration_boost - penalty
    final_score = max(0.0, min(100.0, round(final_score, 1)))

    return final_score
